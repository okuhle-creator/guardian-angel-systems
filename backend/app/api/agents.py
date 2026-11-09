from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.database.session import get_db
from app.models.agent import AgentExecution
from app.schemas.agent import AgentHealthStatus, AgentExecutionResponse

router = APIRouter(prefix="/agents", tags=["Agent Operations"])

AGENTS_METADATA = [
    {
        "name": "Detection Agent",
        "code": "DetectionAgent",
        "role": "Telemetry Analysis & Suspicious Pattern Detection",
        "description": "Performs high-throughput rule and anomaly inspection on raw telemetry, detecting brute-force, process abuse, and IoCs."
    },
    {
        "name": "Alert Correlation Agent",
        "code": "AlertCorrelationAgent",
        "role": "Deduplication & Entity-Temporal Clustering",
        "description": "Fuses isolated alerts into contextual incidents by evaluating shared identity entities, target hosts, and temporal closeness."
    },
    {
        "name": "Threat Analysis Agent",
        "code": "ThreatAnalysisAgent",
        "role": "MITRE ATT&CK Mapping & Attack Progression Reconstructor",
        "description": "Reconstructs the kill-chain trajectory, maps verified behaviours strictly to ATT&CK technique IDs, and isolates hypotheses."
    },
    {
        "name": "Evidence & Explanation Agent",
        "code": "EvidenceExplanationAgent",
        "role": "Evidence-Grounded Explanations & Counter-Hypotheses",
        "description": "Synthesises explainable investigative narratives strictly anchored in stored event records, surfacing gaps and alternative interpretations."
    },
    {
        "name": "Risk Assessment Agent",
        "code": "RiskAssessmentAgent",
        "role": "Multifactor Risk Scoring & Uncertainty Quantification",
        "description": "Calculates separate Risk and Confidence metrics, penalising confidence for missing telemetry and flagging 'UNCERTAIN — ESCALATE TO HUMAN REVIEW'."
    },
    {
        "name": "Governance & Audit Agent",
        "code": "GovernanceAuditAgent",
        "role": "Policy Enforcement & Human Approval Gatekeeper",
        "description": "Enforces deterministic boundaries preventing autonomous destructive execution, queuing actions for mandatory human analyst sign-off."
    }
]

@router.get("/status", response_model=List[AgentHealthStatus])
def get_agents_status(db: Session = Depends(get_db)):
    statuses = []
    for meta in AGENTS_METADATA:
        execs = db.query(AgentExecution).filter(AgentExecution.agent_name == meta["code"]).all()
        tasks_count = len(execs)
        errors = [e for e in execs if e.status == "FAILED"]
        last_exec = db.query(AgentExecution).filter(AgentExecution.agent_name == meta["code"]).order_by(AgentExecution.executed_at.desc()).first()
        
        avg_dur = sum(e.duration_ms for e in execs) / tasks_count if tasks_count > 0 else 0.0
        
        status_state = "HEALTHY"
        if len(errors) > 0:
            status_state = "DEGRADED"
        elif tasks_count == 0:
            status_state = "READY"

        statuses.append({
            "name": meta["name"],
            "code": meta["code"],
            "role": meta["role"],
            "status": status_state,
            "tasks_processed": tasks_count,
            "last_execution": last_exec.executed_at if last_exec else None,
            "avg_duration_ms": round(avg_dur, 2),
            "error_count": len(errors),
            "description": meta["description"]
        })
    return statuses

@router.get("/executions", response_model=List[AgentExecutionResponse])
def list_agent_executions(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(AgentExecution).order_by(AgentExecution.executed_at.desc()).limit(limit).all()
