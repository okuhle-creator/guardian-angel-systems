from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base

class RecommendedAction(Base):
    __tablename__ = "recommended_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(100), unique=True, index=True, nullable=False)
    incident_id = Column(String(100), index=True, nullable=False)
    action_type = Column(String(100), nullable=False)  # DISABLE_ACCOUNT, ISOLATE_HOST, BLOCK_IP, REVOKE_SESSION, ESCALATE_INCIDENT, MARK_INVESTIGATION
    target_entity = Column(String(255), nullable=False)
    target_type = Column(String(50), nullable=False)  # USER, HOST, IP, SESSION, INCIDENT
    rationale = Column(Text, nullable=False)
    required_role = Column(String(50), default="analyst")  # analyst, admin
    risk_level = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    policy_governance_verdict = Column(String(50), default="REQUIRES_HUMAN_APPROVAL")  # REQUIRES_HUMAN_APPROVAL, BLOCKED_BY_POLICY, ALLOWED_AUTOMATED
    status = Column(String(50), default="PENDING_APPROVAL", index=True)  # PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(String(100), unique=True, index=True, nullable=False)
    action_id = Column(String(100), index=True, nullable=False)
    incident_id = Column(String(100), index=True, nullable=False)
    approver_username = Column(String(100), nullable=False)
    decision = Column(String(50), nullable=False)  # APPROVED, REJECTED
    notes = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

class ResponseExecution(Base):
    __tablename__ = "response_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    action_id = Column(String(100), index=True, nullable=False)
    incident_id = Column(String(100), index=True, nullable=False)
    execution_type = Column(String(100), nullable=False)  # SIMULATED_DISABLE_ACCOUNT, SIMULATED_ISOLATE_HOST, etc.
    target = Column(String(255), nullable=False)
    status = Column(String(50), default="SIMULATED_SUCCESS")  # SIMULATED_SUCCESS, SUCCESS, FAILED
    details = Column(JSON, default=dict)
    verification_status = Column(String(50), default="VERIFIED_CONTAINED")  # VERIFIED_CONTAINED, PENDING_VERIFICATION, FAILED_VERIFICATION
    executed_by = Column(String(100), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
