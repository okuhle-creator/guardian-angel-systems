import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.event import SecurityEvent
from app.models.detection import Detection
from app.models.investigation import Investigation
from app.models.agent import AgentExecution
from app.services.audit_service import AuditService

# Comprehensive local MITRE ATT&CK knowledge base mapping
MITRE_TECHNIQUE_RULES = [
    {
        "id": "T1566.002",
        "name": "Phishing: Spearphishing Link",
        "tactic": "Initial Access",
        "check": lambda e: e.event_type == "EMAIL" or (e.raw_payload and "phish" in e.raw_payload.lower())
    },
    {
        "id": "T1110",
        "name": "Brute Force",
        "tactic": "Credential Access",
        "check": lambda e: e.event_type == "AUTHENTICATION" and e.authentication_result == "FAILURE"
    },
    {
        "id": "T1078",
        "name": "Valid Accounts",
        "tactic": "Defense Evasion / Persistence",
        "check": lambda e: e.event_type == "AUTHENTICATION" and e.authentication_result == "SUCCESS" and e.severity in ["HIGH", "CRITICAL"]
    },
    {
        "id": "T1059.001",
        "name": "Command and Scripting Interpreter: PowerShell",
        "tactic": "Execution",
        "check": lambda e: e.process and "powershell" in e.process.lower()
    },
    {
        "id": "T1059.003",
        "name": "Command and Scripting Interpreter: Windows Command Shell",
        "tactic": "Execution",
        "check": lambda e: e.process and "cmd.exe" in e.process.lower()
    },
    {
        "id": "T1021.002",
        "name": "Remote Services: SMB/Windows Admin Shares",
        "tactic": "Lateral Movement",
        "check": lambda e: (e.process and "psexec" in e.process.lower()) or (e.destination_ip and e.host_id and "internal" in str(e.raw_payload).lower())
    },
    {
        "id": "T1071.001",
        "name": "Application Layer Protocol: Web Protocols",
        "tactic": "Command and Control",
        "check": lambda e: e.event_type == "NETWORK_FLOW" and (e.destination_ip or (e.raw_payload and "c2" in str(e.raw_payload).lower()))
    },
    {
        "id": "T1068",
        "name": "Exploitation for Privilege Escalation",
        "tactic": "Privilege Escalation",
        "check": lambda e: e.event_type == "PRIVILEGE_ESCALATION" or (e.process and "whoami" in e.process.lower() and "/priv" in str(e.process).lower())
    },
    {
        "id": "T1562.001",
        "name": "Impair Defenses: Disable or Modify Tools",
        "tactic": "Defense Evasion",
        "check": lambda e: e.is_malformed or (e.anomaly_flags and len(e.anomaly_flags) > 0)
    }
]

class ThreatAnalysisAgent:
    NAME = "ThreatAnalysisAgent"
    ROLE = "Deep Threat Investigation & MITRE ATT&CK Progression Mapping"

    def run(self, db: Session, incident: Incident) -> Investigation:
        start_time = time.time()

        # Load all underlying events and detections
        events = db.query(SecurityEvent).filter(SecurityEvent.event_id.in_(incident.correlated_event_ids)).order_by(SecurityEvent.timestamp.asc()).all()
        detections = db.query(Detection).filter(Detection.detection_id.in_(incident.detection_ids)).all()

        confirmed_evidence: List[Dict[str, Any]] = []
        hypotheses: List[Dict[str, Any]] = []
        mitre_mappings: List[Dict[str, Any]] = []
        attack_progression: List[Dict[str, Any]] = []
        missing_evidence: List[str] = []
        contradictory_evidence: List[str] = []

        seen_techniques = set()

        # 1. Map MITRE techniques strictly against verified evidence
        for rule in MITRE_TECHNIQUE_RULES:
            matched_events = [e for e in events if rule["check"](e)]
            if matched_events:
                tech_id = rule["id"]
                if tech_id not in seen_techniques:
                    seen_techniques.add(tech_id)
                    mitre_mappings.append({
                        "technique_id": rule["id"],
                        "technique_name": rule["name"],
                        "tactic": rule["tactic"],
                        "confidence": 0.90 if len(matched_events) >= 2 else 0.75,
                        "supporting_evidence": [
                            f"Event {e.event_id} ({e.event_type}) on host '{e.host_id or 'unknown'}' by '{e.user_id or 'unknown'}'"
                            for e in matched_events[:3]
                        ]
                    })

        # 2. Trace attack progression chronologically
        for e in events:
            # Fact check: Confirmed telemetry
            confirmed_evidence.append({
                "event_id": e.event_id,
                "timestamp": str(e.timestamp),
                "source": e.source,
                "fact": f"{e.event_type}: user='{e.user_id}', host='{e.host_id}', ip='{e.source_ip}->{e.destination_ip}', proc='{e.process}'",
                "verified": not e.is_malformed
            })

            # Check for missing telemetry context
            if not e.user_id:
                missing_evidence.append(f"Event {e.event_id} is missing user identity telemetry.")
            if not e.source_ip and e.event_type in ["AUTHENTICATION", "NETWORK_FLOW"]:
                missing_evidence.append(f"Event {e.event_id} lacks source IP address.")
            if e.anomaly_flags:
                contradictory_evidence.extend([f"{e.event_id}: {flag}" for flag in e.anomaly_flags])

        # 3. Construct attack stages
        tactic_order = ["Initial Access", "Execution", "Persistence", "Privilege Escalation", "Lateral Movement", "Command and Control", "Exfiltration"]
        for tactic in tactic_order:
            related_mitre = [m for m in mitre_mappings if m["tactic"] == tactic]
            if related_mitre:
                attack_progression.append({
                    "stage": tactic,
                    "timestamp": str(events[0].timestamp if events else datetime.utcnow()),
                    "description": f"Observed adversary behavior matching {tactic}: {', '.join([m['technique_name'] for m in related_mitre])}",
                    "entities": [f"{e.host_id} ({e.user_id})" for e in events if e.host_id or e.user_id][:3],
                    "event_ids": [e.event_id for e in events[:3]]
                })

        # 4. Formulate hypotheses vs confirmed evidence
        if any("Lateral Movement" in m["tactic"] for m in mitre_mappings):
            hypotheses.append({
                "hypothesis": "Adversary has established foothold and is conducting internal host hopping via administrative protocols.",
                "confidence": 0.82,
                "verification_needed": "Verify secondary domain controller auth logs and EDR process lineage on destination host."
            })
        if any("Credential Access" in m["tactic"] for m in mitre_mappings):
            hypotheses.append({
                "hypothesis": "Compromised credential set is being tested across internal subnets.",
                "confidence": 0.88,
                "verification_needed": "Check central active directory lockout records and MFA challenge logs."
            })

        # Synthesize investigation record
        investigation = db.query(Investigation).filter(Investigation.incident_id == incident.incident_id).first()
        if not investigation:
            investigation = Investigation(
                investigation_id=f"INV-{uuid.uuid4().hex[:8].upper()}",
                incident_id=incident.incident_id,
                mitre_mappings=mitre_mappings,
                attack_progression=attack_progression,
                confirmed_evidence=confirmed_evidence[:15],
                hypotheses=hypotheses,
                missing_evidence=list(set(missing_evidence))[:5],
                contradictory_evidence=list(set(contradictory_evidence))[:5],
                explanation="",  # populated by Agent 4
                analyst_notes="",
                created_at=datetime.utcnow()
            )
            db.add(investigation)
        else:
            investigation.mitre_mappings = mitre_mappings
            investigation.attack_progression = attack_progression
            investigation.confirmed_evidence = confirmed_evidence[:15]
            investigation.hypotheses = hypotheses
            investigation.missing_evidence = list(set(missing_evidence))[:5]
            investigation.contradictory_evidence = list(set(contradictory_evidence))[:5]

        db.commit()
        db.refresh(investigation)

        duration = (time.time() - start_time) * 1000.0

        # Log Agent Execution
        execution = AgentExecution(
            execution_id=f"EXEC-THREAT-{uuid.uuid4().hex[:8].upper()}",
            agent_name=self.NAME,
            status="SUCCESS",
            task_description=f"Investigated incident {incident.incident_id}: identified {len(mitre_mappings)} MITRE techniques across {len(attack_progression)} attack stages",
            input_ref=incident.incident_id,
            output_ref=investigation.investigation_id,
            duration_ms=duration,
            details={"mitre_count": len(mitre_mappings), "stages": len(attack_progression)},
            executed_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        return investigation
