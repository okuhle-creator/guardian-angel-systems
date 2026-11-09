from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DetectionResponse(BaseModel):
    id: int
    detection_id: str
    rule_id: str
    rule_name: str
    event_ids: List[str]
    severity: str
    confidence: float
    timestamp: datetime
    explanation: str
    evidence: Dict[str, Any]
    detection_category: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
