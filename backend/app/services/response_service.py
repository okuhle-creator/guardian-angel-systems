import uuid
from datetime import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.response import RecommendedAction, Approval, ResponseExecution
from app.models.incident import Incident
from app.services.audit_service import AuditService

class ResponseExecutionService:
    @staticmethod
    def process_approval(
        db: Session,
        action_id: str,
        decision: str,  # APPROVED or REJECTED
        approver_username: str,
        notes: str = ""
    ) -> Tuple[Approval, RecommendedAction]:
        action = db.query(RecommendedAction).filter(RecommendedAction.action_id == action_id).first()
        if not action:
            raise ValueError(f"Action '{action_id}' not found.")

        if action.status not in ["PENDING_APPROVAL", "REJECTED"]:
            raise ValueError(f"Action '{action_id}' has already been processed (Current status: {action.status}).")

        # Record approval decision
        approval = Approval(
            approval_id=f"APP-{uuid.uuid4().hex[:8].upper()}",
            action_id=action.action_id,
            incident_id=action.incident_id,
            approver_username=approver_username,
            decision=decision,
            notes=notes,
            timestamp=datetime.utcnow()
        )
        db.add(approval)

        action.status = "APPROVED" if decision == "APPROVED" else "REJECTED"
        db.commit()
        db.refresh(action)
        db.refresh(approval)

        # Audit record
        AuditService.log_action(
            db=db,
            actor_id=approver_username,
            actor_role="SOC_ANALYST",
            action=f"ACTION_{decision}",
            target_type="RECOMMENDED_ACTION",
            target_id=action.action_id,
            details={
                "incident_id": action.incident_id,
                "action_type": action.action_type,
                "target_entity": action.target_entity,
                "decision": decision,
                "notes": notes
            }
        )

        return approval, action

    @staticmethod
    def execute_simulated_action(
        db: Session,
        action_id: str,
        executed_by: str
    ) -> ResponseExecution:
        action = db.query(RecommendedAction).filter(RecommendedAction.action_id == action_id).first()
        if not action:
            raise ValueError(f"Action '{action_id}' not found.")

        # Deterministic Policy Check: Must be APPROVED by a human
        if action.status != "APPROVED":
            raise PermissionError(f"Deterministic Policy Violation: Action '{action_id}' cannot execute. Current status is '{action.status}' (Must be 'APPROVED').")

        # Simulated response dispatch based on action_type
        simulated_details = {}
        verif_status = "VERIFIED_CONTAINED"

        if action.action_type == "DISABLE_ACCOUNT":
            simulated_details = {
                "target_account": action.target_entity,
                "directory_service": "Simulated Active Directory / Azure AD",
                "attributes_modified": {"accountEnabled": False, "pwdLastSet": 0, "sessionTokens": "REVOKED"},
                "message": f"Successfully deactivated account '{action.target_entity}' across all simulated identity domains."
            }
        elif action.action_type == "ISOLATE_HOST":
            simulated_details = {
                "target_host": action.target_entity,
                "edr_agent": "Simulated Endpoint Quarantine Driver",
                "network_state": "VLAN 999 (Blackhole Isolation)",
                "whitelisted_traffic": ["10.0.0.5:443 (Management Controller)"],
                "message": f"Host '{action.target_entity}' isolated from production network fabric."
            }
        elif action.action_type == "BLOCK_IP":
            simulated_details = {
                "target_ip": action.target_entity,
                "perimeter_firewall": "Simulated Next-Gen Firewall (Palo Alto / Fortinet)",
                "rule_added": f"DENY ANY -> {action.target_entity} (DROP_AND_LOG)",
                "message": f"Adversary IP '{action.target_entity}' blacklisted on all external gateways."
            }
        elif action.action_type == "REVOKE_SESSION":
            simulated_details = {
                "target_session": action.target_entity,
                "sso_provider": "Simulated Okta / Entra ID",
                "message": f"Active bearer tokens revoked for session '{action.target_entity}'."
            }
        else:
            simulated_details = {
                "target": action.target_entity,
                "message": f"Executed controlled containment for {action.action_type}."
            }

        execution = ResponseExecution(
            execution_id=f"EXEC-{uuid.uuid4().hex[:8].upper()}",
            action_id=action.action_id,
            incident_id=action.incident_id,
            execution_type=f"SIMULATED_{action.action_type}",
            target=action.target_entity,
            status="SIMULATED_SUCCESS",
            details=simulated_details,
            verification_status=verif_status,
            executed_by=executed_by,
            executed_at=datetime.utcnow()
        )
        db.add(execution)

        action.status = "EXECUTED"
        
        # Update incident status if contained
        incident = db.query(Incident).filter(Incident.incident_id == action.incident_id).first()
        if incident and incident.status in ["NEW", "INVESTIGATING"]:
            incident.status = "CONTAINED"

        db.commit()
        db.refresh(execution)
        db.refresh(action)

        # Audit record
        AuditService.log_action(
            db=db,
            actor_id=executed_by,
            actor_role="SOC_ENGINEER",
            action="RESPONSE_EXECUTED_SIMULATED",
            target_type="EXECUTION",
            target_id=execution.execution_id,
            details={
                "action_id": action.action_id,
                "target": action.target_entity,
                "execution_type": execution.execution_type,
                "verification_status": verif_status
            }
        )

        return execution
