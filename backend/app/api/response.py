from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.response import RecommendedAction, Approval, ResponseExecution
from app.schemas.response import (
    RecommendedActionResponse,
    ApprovalDecisionRequest,
    ApprovalRecordResponse,
    ExecutionResponse
)
from app.services.response_service import ResponseExecutionService
from app.services.auth import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/response", tags=["Response & Human Governance"])

@router.get("/actions", response_model=List[RecommendedActionResponse])
def list_recommended_actions(
    status: Optional[str] = None,
    incident_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RecommendedAction)
    if status:
        query = query.filter(RecommendedAction.status == status)
    if incident_id:
        query = query.filter(RecommendedAction.incident_id == incident_id)
    return query.order_by(RecommendedAction.created_at.desc()).all()

@router.get("/actions/{action_id}", response_model=RecommendedActionResponse)
def get_action(action_id: str, db: Session = Depends(get_db)):
    action = db.query(RecommendedAction).filter(RecommendedAction.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action

@router.post("/actions/{action_id}/decision", response_model=ApprovalRecordResponse)
def submit_approval_decision(
    action_id: str,
    decision_in: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        approval, _ = ResponseExecutionService.process_approval(
            db=db,
            action_id=action_id,
            decision=decision_in.decision.upper(),
            approver_username=current_user.username,
            notes=decision_in.notes or ""
        )
        return approval
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/actions/{action_id}/execute", response_model=ExecutionResponse)
def execute_simulated_action(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        execution = ResponseExecutionService.execute_simulated_action(
            db=db,
            action_id=action_id,
            executed_by=current_user.username
        )
        return execution
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/executions", response_model=List[ExecutionResponse])
def list_executions(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(ResponseExecution).order_by(ResponseExecution.executed_at.desc()).limit(limit).all()

@router.get("/approvals", response_model=List[ApprovalRecordResponse])
def list_approvals(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Approval).order_by(Approval.timestamp.desc()).limit(limit).all()
