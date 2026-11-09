from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class AuditRecordResponse(BaseModel):
    id: int
    record_id: str
    timestamp: datetime
    actor_id: str
    actor_role: str
    action: str
    target_type: str
    target_id: str
    details: Dict[str, Any]
    previous_hash: str
    record_hash: str

    class Config:
        from_attributes = True

class AuditVerificationResponse(BaseModel):
    total_records: int
    is_valid: bool
    verified_records_count: int
    tampered_records: List[str]
    root_hash: Optional[str]
    latest_hash: Optional[str]
    message: str
