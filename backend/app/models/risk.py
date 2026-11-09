from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.database.session import Base

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(100), unique=True, index=True, nullable=False)
    incident_id = Column(String(100), index=True, nullable=False)
    risk_score = Column(Float, nullable=False)  # 0 to 100
    risk_category = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    uncertainty_score = Column(Float, nullable=False)  # 0.0 to 1.0 (1.0 - confidence adjusted by telemetry gaps)
    contributing_factors = Column(JSON, default=list)  # breakdown of factors: asset criticality, progression, severity, etc.
    missing_evidence = Column(JSON, default=list)
    recommended_priority = Column(String(50), default="P3")  # P1 (Immediate), P2 (High), P3 (Standard), P4 (Low)
    is_escalated = Column(String(50), default="NORMAL")  # NORMAL, ESCALATE_HUMAN_REVIEW
    evaluated_at = Column(DateTime, default=datetime.utcnow)
