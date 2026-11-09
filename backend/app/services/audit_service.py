import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.audit import AuditRecord

GENESIS_HASH = "0" * 64

class AuditService:
    @staticmethod
    def get_latest_hash(db: Session) -> str:
        latest = db.query(AuditRecord).order_by(AuditRecord.id.desc()).first()
        if latest:
            return latest.record_hash
        return GENESIS_HASH

    @staticmethod
    def log_action(
        db: Session,
        actor_id: str,
        actor_role: str,
        action: str,
        target_type: str,
        target_id: str,
        details: Dict[str, Any]
    ) -> AuditRecord:
        record_id = f"AUD-{uuid.uuid4().hex[:12].upper()}"
        ts = datetime.utcnow()
        ts_str = ts.isoformat()
        prev_hash = AuditService.get_latest_hash(db)
        
        record_hash = AuditRecord.calculate_hash(
            record_id=record_id,
            timestamp_str=ts_str,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details_dict=details,
            previous_hash=prev_hash
        )

        record = AuditRecord(
            record_id=record_id,
            timestamp=ts,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            previous_hash=prev_hash,
            record_hash=record_hash
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def verify_chain(db: Session) -> Tuple[bool, int, List[str], str, str]:
        records = db.query(AuditRecord).order_by(AuditRecord.id.asc()).all()
        if not records:
            return True, 0, [], GENESIS_HASH, GENESIS_HASH

        expected_prev = GENESIS_HASH
        tampered = []

        for r in records:
            # Check previous hash continuity
            if r.previous_hash != expected_prev:
                tampered.append(f"Record {r.record_id} has invalid previous_hash '{r.previous_hash}', expected '{expected_prev}'")
            
            # Recompute expected hash
            recomputed = AuditRecord.calculate_hash(
                record_id=r.record_id,
                timestamp_str=r.timestamp.isoformat(),
                actor_id=r.actor_id,
                action=r.action,
                target_type=r.target_type,
                target_id=r.target_id,
                details_dict=r.details or {},
                previous_hash=r.previous_hash
            )
            if recomputed != r.record_hash:
                tampered.append(f"Record {r.record_id} hash mismatch. Computed '{recomputed}', stored '{r.record_hash}'")

            expected_prev = r.record_hash

        is_valid = len(tampered) == 0
        root_hash = records[0].record_hash if records else GENESIS_HASH
        latest_hash = records[-1].record_hash if records else GENESIS_HASH
        return is_valid, len(records), tampered, root_hash, latest_hash
