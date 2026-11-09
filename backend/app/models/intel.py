from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base

class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String(100), unique=True, index=True, nullable=False)
    type = Column(String(50), nullable=False)  # IP, DOMAIN, HASH, USER, URL
    value = Column(String(255), unique=True, index=True, nullable=False)
    threat_score = Column(Float, default=75.0)  # 0 to 100
    category = Column(String(100), default="MALICIOUS_INFRASTRUCTURE")
    description = Column(Text, nullable=True)
    source = Column(String(100), default="GAS_LOCAL_INTEL")
    tags = Column(JSON, default=list)
    confidence = Column(Float, default=0.9)
    created_at = Column(DateTime, default=datetime.utcnow)
