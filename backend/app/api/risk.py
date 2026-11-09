from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.risk import RiskAssessment
from app.schemas.risk import RiskAssessmentResponse

router = APIRouter(prefix="/risk", tags=["Risk & Uncertainty Assessment"])

@router.get("/incident/{incident_id}", response_model=RiskAssessmentResponse)
def get_risk_assessment(incident_id: str, db: Session = Depends(get_db)):
    risk = db.query(RiskAssessment).filter(RiskAssessment.incident_id == incident_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail=f"No risk assessment found for incident '{incident_id}'")
    return risk
