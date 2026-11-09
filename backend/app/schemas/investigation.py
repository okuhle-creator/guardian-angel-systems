from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class MitreMappingItem(BaseModel):
    tactic: str
    technique_id: str
    technique_name: str
    confidence: float
    supporting_evidence: List[str]

class AttackProgressionStage(BaseModel):
    stage: str
    timestamp: str
    description: str
    entities: List[str]
    event_ids: List[str]

class InvestigationResponse(BaseModel):
    id: int
    investigation_id: str
    incident_id: str
    mitre_mappings: List[Dict[str, Any]]
    attack_progression: List[Dict[str, Any]]
    confirmed_evidence: List[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    missing_evidence: List[str]
    contradictory_evidence: List[str]
    explanation: Optional[str]
    analyst_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NoteUpdateRequest(BaseModel):
    notes: str
