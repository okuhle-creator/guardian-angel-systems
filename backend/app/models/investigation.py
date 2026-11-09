from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.database.session import Base

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(String(100), unique=True, index=True, nullable=False)
    incident_id = Column(String(100), index=True, nullable=False)
    mitre_mappings = Column(JSON, default=list)  # list of {"tactic": "", "technique_id": "", "technique_name": "", "supporting_evidence": []}
    attack_progression = Column(JSON, default=list)  # list of stages: initial_access, execution, credential_access, lateral_movement, etc.
    confirmed_evidence = Column(JSON, default=list)  # list of verified facts with event references
    hypotheses = Column(JSON, default=list)  # list of plausible theories needing validation
    missing_evidence = Column(JSON, default=list)  # list of telemetry gaps detected
    contradictory_evidence = Column(JSON, default=list)  # conflicting telemetry observed
    explanation = Column(Text, nullable=True)  # synthesised narrative
    analyst_notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
