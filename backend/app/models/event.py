from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(100), nullable=False)  # SIEM, ENDPOINT, FIREWALL, AUTH_SERVICE, THREAT_FEED
    event_type = Column(String(100), nullable=False)  # AUTHENTICATION, PROCESS_CREATION, NETWORK_FLOW, PRIVILEGE_ESCALATION, EMAIL
    user_id = Column(String(100), nullable=True, index=True)
    host_id = Column(String(100), nullable=True, index=True)
    source_ip = Column(String(50), nullable=True, index=True)
    destination_ip = Column(String(50), nullable=True, index=True)
    process = Column(String(255), nullable=True)
    authentication_result = Column(String(50), nullable=True)  # SUCCESS, FAILURE, CHALLENGE
    severity = Column(String(50), default="INFO")  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    raw_reference = Column(String(255), nullable=True)
    raw_payload = Column(Text, nullable=True)
    is_malformed = Column(Boolean, default=False)
    anomaly_flags = Column(JSON, default=list)  # ["MISSING_TIMESTAMP", "CONTRADICTORY_AUTH", "UNTRUSTED_SOURCE"]
    created_at = Column(DateTime, default=datetime.utcnow)
