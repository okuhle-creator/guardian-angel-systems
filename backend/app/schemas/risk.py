from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class RiskAssessmentResponse(BaseModel):
    id: int
    assessment_id: str
    incident_id: str
    risk_score: float
    risk_category: str
    confidence_score: float
    uncertainty_score: float
    contributing_factors: List[Dict[str, Any]]
    missing_evidence: List[str]
    recommended_priority: str
    is_escalated: str
    evaluated_at: datetime

    class Config:
        from_attributes = True
