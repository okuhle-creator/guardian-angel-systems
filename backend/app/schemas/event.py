from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

class EventBase(BaseModel):
    event_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    source: str
    event_type: str
    user_id: Optional[str] = None
    host_id: Optional[str] = None
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    process: Optional[str] = None
    authentication_result: Optional[str] = None
    severity: Optional[str] = "INFO"
    confidence: Optional[float] = 1.0
    raw_reference: Optional[str] = None
    raw_payload: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventBatchCreate(BaseModel):
    events: List[EventCreate]

class EventResponse(EventBase):
    id: int
    event_id: str
    timestamp: datetime
    is_malformed: bool
    anomaly_flags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class EventIngestionResult(BaseModel):
    total_received: int
    processed_count: int
    malformed_count: int
    detections_triggered: int
    incidents_updated: int
    warnings: List[str]
