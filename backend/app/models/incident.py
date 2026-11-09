from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="NEW", index=True)  # NEW, INVESTIGATING, CONTAINED, ESCALATED_HUMAN_REVIEW, RESOLVED, FALSE_POSITIVE
    severity = Column(String(50), default="MEDIUM", index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float, default=0.0)  # 0 to 100
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    primary_entities = Column(JSON, default=dict)  # {"users": [], "hosts": [], "ips": []}
    correlated_event_ids = Column(JSON, default=list)  # list of event_ids
    detection_ids = Column(JSON, default=list)  # list of detection_ids
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
