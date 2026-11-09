from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class IndicatorBase(BaseModel):
    type: str  # IP, DOMAIN, HASH, USER
    value: str
    threat_score: float = 75.0
    category: str = "MALICIOUS_INFRASTRUCTURE"
    description: Optional[str] = None
    source: str = "GAS_LOCAL_INTEL"
    tags: List[str] = []
    confidence: float = 0.9

class IndicatorCreate(IndicatorBase):
    pass

class IndicatorResponse(IndicatorBase):
    id: int
    indicator_id: str
    created_at: datetime

    class Config:
        from_attributes = True
