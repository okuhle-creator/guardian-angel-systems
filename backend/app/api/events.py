import csv
import io
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.event import SecurityEvent
from app.schemas.event import EventCreate, EventBatchCreate, EventResponse, EventIngestionResult
from app.services.pipeline import pipeline_orchestrator
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events & Telemetry Ingestion"])

@router.post("/ingest", response_model=EventIngestionResult)
def ingest_single_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_dict = event_in.model_dump()
    result = pipeline_orchestrator.process_raw_events(db, [raw_dict], actor=current_user.username)
    return result

@router.post("/ingest/batch", response_model=EventIngestionResult)
def ingest_batch_events(
    batch_in: EventBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_records = [e.model_dump() for e in batch_in.events]
    result = pipeline_orchestrator.process_raw_events(db, raw_records, actor=current_user.username)
    return result

@router.post("/upload/csv", response_model=EventIngestionResult)
async def upload_csv_telemetry(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    raw_records = []
    for row in reader:
        raw_records.append(dict(row))
    
    result = pipeline_orchestrator.process_raw_events(db, raw_records, actor=f"CSV_UPLOAD:{current_user.username}")
    return result

@router.get("/", response_model=List[EventResponse])
def list_events(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    is_malformed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SecurityEvent)
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type.upper())
    if source:
        query = query.filter(SecurityEvent.source == source.upper())
    if severity:
        query = query.filter(SecurityEvent.severity == severity.upper())
    if is_malformed is not None:
        query = query.filter(SecurityEvent.is_malformed == is_malformed)
    
    return query.order_by(SecurityEvent.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    ev = db.query(SecurityEvent).filter(SecurityEvent.event_id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail=f"Security event '{event_id}' not found")
    return ev
