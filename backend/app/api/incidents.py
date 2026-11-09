from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.incident import Incident
from app.models.event import SecurityEvent
from app.schemas.incident import IncidentResponse, IncidentUpdate
from app.schemas.event import EventResponse
from app.services.audit_service import AuditService
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity.upper())
    return query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.get("/{incident_id}/events", response_model=List[EventResponse])
def get_incident_correlated_events(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    events = db.query(SecurityEvent).filter(SecurityEvent.event_id.in_(inc.correlated_event_ids)).order_by(SecurityEvent.timestamp.asc()).all()
    return events

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    update_in: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inc = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    if update_in.status:
        inc.status = update_in.status
    if update_in.severity:
        inc.severity = update_in.severity
    if update_in.title:
        inc.title = update_in.title
    if update_in.description:
        inc.description = update_in.description

    db.commit()
    db.refresh(inc)

    AuditService.log_action(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        action="INCIDENT_UPDATED",
        target_type="INCIDENT",
        target_id=inc.incident_id,
        details=update_in.model_dump(exclude_unset=True)
    )

    return inc
