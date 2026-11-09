from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    description: str
    status: str
    severity: str
    risk_score: float
    confidence_score: float
    primary_entities: Dict[str, Any]
    correlated_event_ids: List[str]
    detection_ids: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
