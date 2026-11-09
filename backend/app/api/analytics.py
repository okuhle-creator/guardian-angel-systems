from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Evaluation"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    return AnalyticsService.get_summary_metrics(db)
