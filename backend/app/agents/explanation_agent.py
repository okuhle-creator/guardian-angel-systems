import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.event import SecurityEvent
from app.models.agent import AgentExecution

class ExplanationAgent:
    NAME = "EvidenceExplanationAgent"
    ROLE = "Evidence-Grounded Incident Explanation & Alternative Hypothesis Generation"

    def run(self, db: Session, incident: Incident, investigation: Investigation) -> str:
        start_time = time.time()

        events = db.query(SecurityEvent).filter(SecurityEvent.event_id.in_(incident.correlated_event_ids)).order_by(SecurityEvent.timestamp.asc()).all()

        users = incident.primary_entities.get("users", [])
        hosts = incident.primary_entities.get("hosts", [])
        ips = incident.primary_entities.get("ips", [])

        # Formulate deterministic, evidence-grounded explanation
        users_str = ", ".join(users) if users else "unspecified accounts"
        hosts_str = ", ".join(hosts) if hosts else "unspecified hosts"
        ips_str = ", ".join(ips) if ips else "internal subnets"

        narrative_parts = []
        narrative_parts.append(
            f"**Incident Overview**: Security Incident `{incident.incident_id}` was flagged due to correlated suspicious behaviors "
            f"involving user account(s) `{users_str}` on host(s) `{hosts_str}`, referencing network infrastructure `{ips_str}`."
        )

        mapped_tech_summaries = [f"{m.get('technique_id', '')} ({m.get('technique_name', '')})" for m in investigation.mitre_mappings]
        narrative_parts.append(
            f"**Evidence Chain**: Total of {len(events)} telemetry events contributed to this investigation. "
            f"Chronologically, the activity began at {events[0].timestamp if events else 'N/A'} "
            f"and culminated in {len(investigation.mitre_mappings)} distinct ATT&CK-mapped techniques: "
            f"{', '.join(mapped_tech_summaries)}."
        )

        if investigation.missing_evidence:
            narrative_parts.append(
                f"**Telemetry Limitations & Data Gaps**: Antigravity has identified {len(investigation.missing_evidence)} specific gaps in telemetry: "
                + " ".join([f"- {g}" for g in investigation.missing_evidence[:3]])
            )

        if investigation.contradictory_evidence:
            narrative_parts.append(
                f"**Contradictory / Anomalous Observations**: System detected inconsistent signals: "
                + " ".join([f"- {c}" for c in investigation.contradictory_evidence[:3]])
                + " Consequently, confidence has been penalised to prevent unverified conclusions."
            )

        # Alternative interpretations (benign vs malicious)
        alt_hypotheses = []
        if any("Execution" in s.get("stage", "") for s in investigation.attack_progression):
            alt_hypotheses.append("Scheduled administrative maintenance script or automated inventory scanner execution.")
        if any("Credential Access" in s.get("stage", "") for s in investigation.attack_progression):
            alt_hypotheses.append("Legitimate user forgetting credentials or misconfigured service account with expired token.")
        
        if alt_hypotheses:
            narrative_parts.append(
                f"**Alternative Interpretations**: Before concluding hostile intent, analysts should consider: "
                + " ".join([f"1) {h}" for h in alt_hypotheses])
            )

        final_explanation = "\n\n".join(narrative_parts)

        # Update investigation record
        investigation.explanation = final_explanation
        db.commit()

        duration = (time.time() - start_time) * 1000.0

        # Log Agent Execution
        execution = AgentExecution(
            execution_id=f"EXEC-EXPL-{uuid.uuid4().hex[:8].upper()}",
            agent_name=self.NAME,
            status="SUCCESS",
            task_description=f"Generated grounded explanation for incident {incident.incident_id} referencing {len(events)} events",
            input_ref=incident.incident_id,
            output_ref=investigation.investigation_id,
            duration_ms=duration,
            details={"events_referenced": len(events), "alternatives_considered": len(alt_hypotheses)},
            executed_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        return final_explanation
