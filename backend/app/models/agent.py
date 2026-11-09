from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base

class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    agent_name = Column(String(100), index=True, nullable=False)  # DetectionAgent, AlertCorrelationAgent, ThreatAnalysisAgent, EvidenceExplanationAgent, RiskAssessmentAgent, GovernanceAuditAgent
    status = Column(String(50), default="SUCCESS")  # SUCCESS, WARNING, FAILED
    task_description = Column(String(255), nullable=False)
    input_ref = Column(String(255), nullable=True)
    output_ref = Column(String(255), nullable=True)
    duration_ms = Column(Float, default=0.0)
    details = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)
