import time
import uuid
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.risk import RiskAssessment
from app.models.response import RecommendedAction, Approval, ResponseExecution
from app.models.agent import AgentExecution
from app.services.audit_service import AuditService

class GovernanceAgent:
    NAME = "GovernanceAuditAgent"
    ROLE = "Deterministic Policy Enforcement, Human Approval Gating & Tamper-Evident Audit"

    def run(self, db: Session, incident: Incident, investigation: Investigation, risk: RiskAssessment) -> List[RecommendedAction]:
        start_time = time.time()
        actions: List[RecommendedAction] = []

        # 1. Evaluate whether containment actions are indicated
        primary_users = incident.primary_entities.get("users", [])
        primary_hosts = incident.primary_entities.get("hosts", [])
        primary_ips = incident.primary_entities.get("ips", [])

        # If compromised account or credential access identified
        for user in primary_users:
            if user and user.lower() not in ["system", "local system", "unknown"]:
                # Check if action already exists
                existing = db.query(RecommendedAction).filter(
                    RecommendedAction.incident_id == incident.incident_id,
                    RecommendedAction.action_type == "DISABLE_ACCOUNT",
                    RecommendedAction.target_entity == user
                ).first()
                if not existing:
                    action = RecommendedAction(
                        action_id=f"ACT-DIS-{uuid.uuid4().hex[:8].upper()}",
                        incident_id=incident.incident_id,
                        action_type="DISABLE_ACCOUNT",
                        target_entity=user,
                        target_type="USER",
                        rationale=f"Compromised credential indicators identified for account '{user}'. Suspend Active Directory credentials to arrest unauthorized session persistence.",
                        required_role="analyst",
                        risk_level="HIGH",
                        policy_governance_verdict="REQUIRES_HUMAN_APPROVAL",  # Strictly gated by policy
                        status="PENDING_APPROVAL",
                        created_at=datetime.utcnow()
                    )
                    actions.append(action)
                    db.add(action)

        # If malicious host compromised or lateral movement
        for host in primary_hosts:
            if host:
                existing = db.query(RecommendedAction).filter(
                    RecommendedAction.incident_id == incident.incident_id,
                    RecommendedAction.action_type == "ISOLATE_HOST",
                    RecommendedAction.target_entity == host
                ).first()
                if not existing:
                    action = RecommendedAction(
                        action_id=f"ACT-ISO-{uuid.uuid4().hex[:8].upper()}",
                        incident_id=incident.incident_id,
                        action_type="ISOLATE_HOST",
                        target_entity=host,
                        target_type="HOST",
                        rationale=f"Host '{host}' exhibiting command execution and lateral movement signals. Quarantine network adapter via EDR agent while maintaining management channel.",
                        required_role="admin",
                        risk_level="CRITICAL",
                        policy_governance_verdict="REQUIRES_HUMAN_APPROVAL",
                        status="PENDING_APPROVAL",
                        created_at=datetime.utcnow()
                    )
                    actions.append(action)
                    db.add(action)

        # If external adversary IP identified
        for ip in primary_ips:
            if ip and not ip.startswith("10.") and not ip.startswith("192.168.") and not ip.startswith("127."):
                existing = db.query(RecommendedAction).filter(
                    RecommendedAction.incident_id == incident.incident_id,
                    RecommendedAction.action_type == "BLOCK_IP",
                    RecommendedAction.target_entity == ip
                ).first()
                if not existing:
                    action = RecommendedAction(
                        action_id=f"ACT-BLK-{uuid.uuid4().hex[:8].upper()}",
                        incident_id=incident.incident_id,
                        action_type="BLOCK_IP",
                        target_entity=ip,
                        target_type="IP",
                        rationale=f"Adversary command and control / brute force traffic originating from IP '{ip}'. Blacklist on border firewalls.",
                        required_role="analyst",
                        risk_level="MEDIUM",
                        policy_governance_verdict="REQUIRES_HUMAN_APPROVAL",
                        status="PENDING_APPROVAL",
                        created_at=datetime.utcnow()
                    )
                    actions.append(action)
                    db.add(action)

        # If uncertain / low confidence, recommend human escalation
        if risk.is_escalated == "ESCALATE_HUMAN_REVIEW":
            existing = db.query(RecommendedAction).filter(
                RecommendedAction.incident_id == incident.incident_id,
                RecommendedAction.action_type == "ESCALATE_INCIDENT"
            ).first()
            if not existing:
                action = RecommendedAction(
                    action_id=f"ACT-ESC-{uuid.uuid4().hex[:8].upper()}",
                    incident_id=incident.incident_id,
                    action_type="ESCALATE_INCIDENT",
                    target_entity=incident.incident_id,
                    target_type="INCIDENT",
                    rationale="High telemetry uncertainty or contradictory signals detected. Escalating to Senior Threat Hunter for manual corroboration.",
                    required_role="analyst",
                    risk_level="MEDIUM",
                    policy_governance_verdict="REQUIRES_HUMAN_APPROVAL",
                    status="PENDING_APPROVAL",
                    created_at=datetime.utcnow()
                )
                actions.append(action)
                db.add(action)

        db.commit()
        for a in actions:
            db.refresh(a)

        duration = (time.time() - start_time) * 1000.0

        # Log Agent Execution
        execution = AgentExecution(
            execution_id=f"EXEC-GOV-{uuid.uuid4().hex[:8].upper()}",
            agent_name=self.NAME,
            status="SUCCESS",
            task_description=f"Evaluated policy gates for incident {incident.incident_id}; formulated {len(actions)} governed response actions requiring human sign-off",
            input_ref=incident.incident_id,
            output_ref=f"{len(actions)} actions",
            duration_ms=duration,
            details={"actions_proposed": len(actions)},
            executed_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        # Audit record
        if actions:
            AuditService.log_action(
                db=db,
                actor_id=self.NAME,
                actor_role="GOVERNANCE_ENGINE",
                action="RESPONSE_ACTIONS_GOVERNED",
                target_type="INCIDENT",
                target_id=incident.incident_id,
                details={"action_ids": [a.action_id for a in actions], "policy_gate": "REQUIRES_HUMAN_APPROVAL"}
            )

        return actions
