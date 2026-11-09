import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.risk import RiskAssessment
from app.models.agent import AgentExecution
from app.services.audit_service import AuditService

class RiskAssessmentAgent:
    NAME = "RiskAssessmentAgent"
    ROLE = "Explainable Quantitative Risk & Separate Confidence/Uncertainty Evaluation"

    def run(self, db: Session, incident: Incident, investigation: Investigation) -> RiskAssessment:
        start_time = time.time()

        contributing_factors: List[Dict[str, Any]] = []

        # 1. Base Severity Score (0 - 40 pts)
        sev_weights = {"CRITICAL": 40.0, "HIGH": 30.0, "MEDIUM": 20.0, "LOW": 10.0, "INFO": 5.0}
        base_sev_score = sev_weights.get(incident.severity, 15.0)
        contributing_factors.append({
            "factor": "Alert Severity",
            "weight": base_sev_score,
            "max": 40.0,
            "description": f"Incident maximum severity evaluated as {incident.severity}."
        })

        # 2. Attack Progression Stage (0 - 30 pts)
        stages_count = len(investigation.attack_progression)
        has_lateral = any("Lateral Movement" in s.get("stage", "") for s in investigation.attack_progression)
        has_c2 = any("Command and Control" in s.get("stage", "") for s in investigation.attack_progression)
        has_priv = any("Privilege Escalation" in s.get("stage", "") for s in investigation.attack_progression)

        progression_score = min(30.0, stages_count * 8.0 + (10.0 if (has_lateral or has_c2) else 0.0))
        contributing_factors.append({
            "factor": "Attack Kill-Chain Depth",
            "weight": progression_score,
            "max": 30.0,
            "description": f"Observed {stages_count} kill-chain stages (Lateral Movement: {has_lateral}, C2: {has_c2})."
        })

        # 3. Asset Criticality (0 - 20 pts)
        critical_assets = ["dc01", "srv-db", "prod-api", "srv-vault", "domain-controller", "admin"]
        hosts = [h.lower() for h in incident.primary_entities.get("hosts", [])]
        users = [u.lower() for u in incident.primary_entities.get("users", [])]

        is_critical_asset = any(any(ca in h for ca in critical_assets) for h in hosts) or any("admin" in u or "root" in u for u in users)
        asset_score = 20.0 if is_critical_asset else 10.0
        contributing_factors.append({
            "factor": "Target Asset Criticality",
            "weight": asset_score,
            "max": 20.0,
            "description": "High-value domain/server asset or privileged credential involved." if is_critical_asset else "Standard workstation/user asset."
        })

        # 4. Scope & Entity Breadth (0 - 10 pts)
        entities_count = len(hosts) + len(users) + len(incident.primary_entities.get("ips", []))
        scope_score = min(10.0, entities_count * 2.5)
        contributing_factors.append({
            "factor": "Entity Blast Radius",
            "weight": scope_score,
            "max": 10.0,
            "description": f"Encompasses {entities_count} total correlated identity and network endpoints."
        })

        total_risk_score = round(min(100.0, base_sev_score + progression_score + asset_score + scope_score), 1)

        # Separate Confidence & Uncertainty Calculation
        # Base confidence begins from detection confidence
        raw_conf = incident.confidence_score if incident.confidence_score > 0 else 0.85
        
        # Penalise confidence if there are missing telemetry elements or contradictions
        gaps_penalty = len(investigation.missing_evidence) * 0.12
        contradiction_penalty = len(investigation.contradictory_evidence) * 0.18
        final_confidence = round(max(0.15, min(0.99, raw_conf - gaps_penalty - contradiction_penalty)), 2)
        uncertainty_score = round(1.0 - final_confidence, 2)

        # Risk category
        if total_risk_score >= 80:
            category = "CRITICAL"
            priority = "P1"
        elif total_risk_score >= 60:
            category = "HIGH"
            priority = "P2"
        elif total_risk_score >= 40:
            category = "MEDIUM"
            priority = "P3"
        else:
            category = "LOW"
            priority = "P4"

        # Explicit support for UNCERTAIN — ESCALATE TO HUMAN REVIEW
        is_escalated = "NORMAL"
        if final_confidence < 0.50 or uncertainty_score >= 0.50 or len(investigation.contradictory_evidence) > 0:
            is_escalated = "ESCALATE_HUMAN_REVIEW"
            incident.status = "ESCALATED_HUMAN_REVIEW"

        # Update incident risk & confidence
        incident.risk_score = total_risk_score
        incident.confidence_score = final_confidence
        db.commit()

        # Save or update RiskAssessment record
        assessment = db.query(RiskAssessment).filter(RiskAssessment.incident_id == incident.incident_id).first()
        if not assessment:
            assessment = RiskAssessment(
                assessment_id=f"RISK-{uuid.uuid4().hex[:8].upper()}",
                incident_id=incident.incident_id,
                risk_score=total_risk_score,
                risk_category=category,
                confidence_score=final_confidence,
                uncertainty_score=uncertainty_score,
                contributing_factors=contributing_factors,
                missing_evidence=investigation.missing_evidence,
                recommended_priority=priority,
                is_escalated=is_escalated,
                evaluated_at=datetime.utcnow()
            )
            db.add(assessment)
        else:
            assessment.risk_score = total_risk_score
            assessment.risk_category = category
            assessment.confidence_score = final_confidence
            assessment.uncertainty_score = uncertainty_score
            assessment.contributing_factors = contributing_factors
            assessment.missing_evidence = investigation.missing_evidence
            assessment.recommended_priority = priority
            assessment.is_escalated = is_escalated
            assessment.evaluated_at = datetime.utcnow()

        db.commit()
        db.refresh(assessment)

        duration = (time.time() - start_time) * 1000.0

        # Log Agent Execution
        execution = AgentExecution(
            execution_id=f"EXEC-RISK-{uuid.uuid4().hex[:8].upper()}",
            agent_name=self.NAME,
            status="SUCCESS",
            task_description=f"Calculated risk: {total_risk_score}/100 ({category}), confidence: {final_confidence}, uncertainty: {uncertainty_score}",
            input_ref=incident.incident_id,
            output_ref=assessment.assessment_id,
            duration_ms=duration,
            details={"risk": total_risk_score, "confidence": final_confidence, "uncertainty": uncertainty_score, "escalated": is_escalated},
            executed_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        # Audit record
        AuditService.log_action(
            db=db,
            actor_id=self.NAME,
            actor_role="AI_AGENT",
            action="RISK_EVALUATED",
            target_type="INCIDENT",
            target_id=incident.incident_id,
            details={
                "risk_score": total_risk_score,
                "confidence_score": final_confidence,
                "uncertainty_score": uncertainty_score,
                "is_escalated": is_escalated
            }
        )

        return assessment
