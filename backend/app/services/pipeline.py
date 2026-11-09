import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.event import SecurityEvent
from app.models.detection import Detection
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.risk import RiskAssessment
from app.models.response import RecommendedAction
from app.services.normalizer import TelemetryNormalizer
from app.services.audit_service import AuditService
from app.agents.detection_agent import DetectionAgent
from app.agents.correlation_agent import CorrelationAgent
from app.agents.threat_analysis_agent import ThreatAnalysisAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.risk_agent import RiskAssessmentAgent
from app.agents.governance_agent import GovernanceAgent

class PipelineOrchestrator:
    def __init__(self):
        self.detection_agent = DetectionAgent()
        self.correlation_agent = CorrelationAgent()
        self.threat_agent = ThreatAnalysisAgent()
        self.explanation_agent = ExplanationAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.governance_agent = GovernanceAgent()

    def process_raw_events(self, db: Session, raw_records: List[Dict[str, Any]], actor: str = "API_INGEST") -> Dict[str, Any]:
        """
        Executes complete multi-agent pipeline on a batch of security records.
        """
        start_time = time.time()
        normalized_events: List[SecurityEvent] = []
        malformed_count = 0
        all_warnings: List[str] = []

        # 1. Telemetry Normalisation
        for raw in raw_records:
            try:
                norm_dict, is_malformed, flags = TelemetryNormalizer.normalize_record(raw)
                if is_malformed:
                    malformed_count += 1
                if flags:
                    all_warnings.extend(flags)

                event = SecurityEvent(**norm_dict)
                db.add(event)
                normalized_events.append(event)
            except Exception as e:
                malformed_count += 1
                all_warnings.append(f"Failed to normalize raw record: {str(e)}")

        db.commit()
        for ev in normalized_events:
            db.refresh(ev)

        AuditService.log_action(
            db=db,
            actor_id=actor,
            actor_role="DATA_INGESTION",
            action="EVENTS_INGESTED",
            target_type="EVENT_BATCH",
            target_id=f"BATCH-{len(normalized_events)}",
            details={"total": len(raw_records), "normalized": len(normalized_events), "malformed": malformed_count}
        )

        # 2. Detection Agent
        detections = self.detection_agent.run(db, normalized_events)

        # 3. Alert Correlation Agent
        incidents = self.correlation_agent.run(db, detections)

        # 4, 5, 6. Deep Investigation, Explanation, Risk, & Governance per incident
        total_actions: List[RecommendedAction] = []
        uncertainty_flagged = False

        for inc in incidents:
            try:
                # Agent 3: Threat Analysis
                inv = self.threat_agent.run(db, inc)

                # Agent 4: Evidence & Explanation
                self.explanation_agent.run(db, inc, inv)

                # Agent 5: Risk Assessment
                risk = self.risk_agent.run(db, inc, inv)
                if risk.is_escalated == "ESCALATE_HUMAN_REVIEW":
                    uncertainty_flagged = True

                # Agent 6: Governance & Policy Gates
                actions = self.governance_agent.run(db, inc, inv, risk)
                total_actions.extend(actions)

            except Exception as e:
                # Failure handling: preserve evidence and escalate to human review
                inc.status = "ESCALATED_HUMAN_REVIEW"
                db.commit()
                AuditService.log_action(
                    db=db,
                    actor_id="PIPELINE",
                    actor_role="SYSTEM",
                    action="PIPELINE_AGENT_ERROR_HANDLED",
                    target_type="INCIDENT",
                    target_id=inc.incident_id,
                    details={"error": str(e), "fallback_action": "ESCALATED_TO_HUMAN_REVIEW"}
                )

        return {
            "total_received": len(raw_records),
            "processed_count": len(normalized_events),
            "malformed_count": malformed_count,
            "detections_triggered": len(detections),
            "incidents_created": len(incidents),
            "actions_recommended": len(total_actions),
            "uncertainty_flagged": uncertainty_flagged,
            "duration_ms": round((time.time() - start_time) * 1000.0, 2),
            "warnings": list(set(all_warnings))
        }

pipeline_orchestrator = PipelineOrchestrator()
