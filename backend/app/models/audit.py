from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base
import hashlib
import json

class AuditRecord(Base):
    __tablename__ = "audit_records"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    actor_id = Column(String(100), nullable=False)
    actor_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)  # INGESTION, DETECTION_TRIGGERED, INCIDENT_CREATED, APPROVAL_GRANTED, APPROVAL_REJECTED, RESPONSE_SIMULATED, POLICY_ENFORCED
    target_type = Column(String(100), nullable=False)  # EVENT, DETECTION, INCIDENT, ACTION, POLICY
    target_id = Column(String(100), nullable=False, index=True)
    details = Column(JSON, default=dict)
    previous_hash = Column(String(64), nullable=False)
    record_hash = Column(String(64), nullable=False, index=True)

    @staticmethod
    def calculate_hash(record_id: str, timestamp_str: str, actor_id: str, action: str, target_type: str, target_id: str, details_dict: dict, previous_hash: str) -> str:
        payload = f"{record_id}|{timestamp_str}|{actor_id}|{action}|{target_type}|{target_id}|{json.dumps(details_dict, sort_keys=True)}|{previous_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
