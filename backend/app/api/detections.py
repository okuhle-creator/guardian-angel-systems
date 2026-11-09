from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.detection import Detection
from app.schemas.detection import DetectionResponse

router = APIRouter(prefix="/detections", tags=["Detections"])

@router.get("/", response_model=List[DetectionResponse])
def list_detections(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    rule_id: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Detection)
    if severity:
        query = query.filter(Detection.severity == severity.upper())
    if rule_id:
        query = query.filter(Detection.rule_id == rule_id)
    if category:
        query = query.filter(Detection.detection_category == category)
    return query.order_by(Detection.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/{detection_id}", response_model=DetectionResponse)
def get_detection(detection_id: str, db: Session = Depends(get_db)):
    det = db.query(Detection).filter(Detection.detection_id == detection_id).first()
    if not det:
        raise HTTPException(status_code=404, detail="Detection not found")
    return det
