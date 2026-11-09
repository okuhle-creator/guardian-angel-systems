from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.audit import AuditRecord
from app.schemas.audit import AuditRecordResponse, AuditVerificationResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit & Cryptographic Ledger"])

@router.get("/records", response_model=List[AuditRecordResponse])
def list_audit_records(
    limit: int = 100,
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AuditRecord)
    if actor_id:
        query = query.filter(AuditRecord.actor_id == actor_id)
    if action:
        query = query.filter(AuditRecord.action == action)
    if target_type:
        query = query.filter(AuditRecord.target_type == target_type)
    return query.order_by(AuditRecord.id.desc()).limit(limit).all()

@router.get("/verify", response_model=AuditVerificationResponse)
def verify_audit_ledger_integrity(db: Session = Depends(get_db)):
    is_valid, count, tampered, root_hash, latest_hash = AuditService.verify_chain(db)
    msg = (
        f"Cryptographic hash chain verified. All {count} records intact with uninterrupted SHA-256 hash continuity."
        if is_valid
        else f"Integrity alert: Detected {len(tampered)} tampered or discontinuous records!"
    )
    return {
        "total_records": count,
        "is_valid": is_valid,
        "verified_records_count": count - len(tampered),
        "tampered_records": tampered,
        "root_hash": root_hash,
        "latest_hash": latest_hash,
        "message": msg
    }
