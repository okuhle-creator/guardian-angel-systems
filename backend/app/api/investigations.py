from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.investigation import Investigation
from app.models.incident import Incident
from app.schemas.investigation import InvestigationResponse, NoteUpdateRequest
from app.services.auth import get_current_user
from app.models.user import User
from app.services.audit_service import AuditService

router = APIRouter(prefix="/investigations", tags=["Investigations"])

@router.get("/incident/{incident_id}", response_model=InvestigationResponse)
def get_investigation_by_incident(incident_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.incident_id == incident_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail=f"No investigation found for incident '{incident_id}'")
    return inv

@router.patch("/incident/{incident_id}/notes", response_model=InvestigationResponse)
def update_investigation_notes(
    incident_id: str,
    note_in: NoteUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.incident_id == incident_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation record not found")

    inv.analyst_notes = note_in.notes
    db.commit()
    db.refresh(inv)

    AuditService.log_action(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        action="ANALYST_NOTES_UPDATED",
        target_type="INVESTIGATION",
        target_id=inv.investigation_id,
        details={"incident_id": incident_id, "note_length": len(note_in.notes)}
    )

    return inv
