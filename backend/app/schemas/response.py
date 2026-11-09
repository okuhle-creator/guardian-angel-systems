from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class RecommendedActionResponse(BaseModel):
    id: int
    action_id: str
    incident_id: str
    action_type: str
    target_entity: str
    target_type: str
    rationale: str
    required_role: str
    risk_level: str
    policy_governance_verdict: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApprovalDecisionRequest(BaseModel):
    decision: str  # APPROVED or REJECTED
    notes: Optional[str] = "Decision rendered via Human-in-the-Loop Governance console"

class ApprovalRecordResponse(BaseModel):
    id: int
    approval_id: str
    action_id: str
    incident_id: str
    approver_username: str
    decision: str
    notes: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ExecutionResponse(BaseModel):
    id: int
    execution_id: str
    action_id: str
    incident_id: str
    execution_type: str
    target: str
    status: str
    details: Dict[str, Any]
    verification_status: str
    executed_by: str
    executed_at: datetime

    class Config:
        from_attributes = True
