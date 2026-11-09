import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.intel import ThreatIndicator
from app.schemas.intel import IndicatorCreate, IndicatorResponse
from app.services.audit_service import AuditService
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/intel", tags=["Threat Intelligence"])

@router.get("/indicators", response_model=List[IndicatorResponse])
def list_threat_indicators(
    indicator_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(ThreatIndicator)
    if indicator_type:
        query = query.filter(ThreatIndicator.type == indicator_type.upper())
    return query.order_by(ThreatIndicator.threat_score.desc()).limit(limit).all()

@router.post("/indicators", response_model=IndicatorResponse)
def create_threat_indicator(
    indicator_in: IndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(ThreatIndicator).filter(ThreatIndicator.value == indicator_in.value).first()
    if existing:
        raise HTTPException(status_code=400, detail="Indicator already exists in intelligence database")

    indicator = ThreatIndicator(
        indicator_id=f"IOC-{uuid.uuid4().hex[:8].upper()}",
        type=indicator_in.type.upper(),
        value=indicator_in.value,
        threat_score=indicator_in.threat_score,
        category=indicator_in.category,
        description=indicator_in.description,
        source=indicator_in.source,
        tags=indicator_in.tags,
        confidence=indicator_in.confidence,
        created_at=datetime.utcnow()
    )
    db.add(indicator)
    db.commit()
    db.refresh(indicator)

    AuditService.log_action(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        action="THREAT_INDICATOR_ADDED",
        target_type="IOC",
        target_id=indicator.indicator_id,
        details={"value": indicator.value, "type": indicator.type, "score": indicator.threat_score}
    )

    return indicator
