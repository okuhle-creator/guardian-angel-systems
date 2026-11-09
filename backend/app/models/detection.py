from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(String(100), unique=True, index=True, nullable=False)
    rule_id = Column(String(100), index=True, nullable=False)
    rule_name = Column(String(200), nullable=False)
    event_ids = Column(JSON, nullable=False)  # list of event_id strings
    severity = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    explanation = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=False)  # Key-value dictionary of supporting facts
    detection_category = Column(String(100), default="SUSPICIOUS_BEHAVIOR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
