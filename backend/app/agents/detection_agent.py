import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.event import SecurityEvent
from app.models.detection import Detection
from app.models.agent import AgentExecution
from app.models.intel import ThreatIndicator
from app.services.audit_service import AuditService

class DetectionAgent:
    NAME = "DetectionAgent"
    ROLE = "Threat Detection & Suspicious Activity Identification"

    def __init__(self):
        # Known suspicious process signatures
        self.suspicious_process_patterns = [
            ("powershell", ["-enc", "-encodedcommand", "downloadstring", "bypass", "invoke-expression", "iex"]),
            ("certutil", ["-urlcache", "-split", "-f"]),
            ("vssadmin", ["delete", "shadows"]),
            ("mimikatz", ["sekurlsa", "logonpasswords"]),
            ("cmd", ["whoami", "net user", "net localgroup administrators"]),
            ("psexec", ["-s", "-accepteula"]),
            ("rundll32", ["shell32.dll", "advpack.dll"]),
        ]

        # Suspicious destination ports
        self.suspicious_ports = ["4444", "8888", "1337", "6667", "5555"]

    def run(self, db: Session, events: List[SecurityEvent]) -> List[Detection]:
        start_time = time.time()
        detections: List[Detection] = []
        
        # Query known threat indicators for fast cross-referencing
        threat_ips = {ind.value: ind for ind in db.query(ThreatIndicator).filter(ThreatIndicator.type == "IP").all()}
        threat_users = {ind.value: ind for ind in db.query(ThreatIndicator).filter(ThreatIndicator.type == "USER").all()}

        # 1. Check Brute-Force & Credential Stuffing Patterns per user & source_ip
        auth_events = [e for e in events if e.event_type == "AUTHENTICATION"]
        auth_groups: Dict[str, List[SecurityEvent]] = {}
        for ae in auth_events:
            key = f"{ae.user_id or 'anon'}@{ae.source_ip or 'unknown'}"
            auth_groups.setdefault(key, []).append(ae)

        for key, group in auth_groups.items():
            failures = [e for e in group if e.authentication_result == "FAILURE"]
            successes = [e for e in group if e.authentication_result == "SUCCESS"]

            if len(failures) >= 3:
                conf = 0.92 if successes else 0.85
                sev = "HIGH" if successes else "MEDIUM"
                sample = failures[0]
                det = Detection(
                    detection_id=f"DET-BF-{uuid.uuid4().hex[:8].upper()}",
                    rule_id="RULE-AUTH-001",
                    rule_name="Brute-Force Authentication Attempt Detected",
                    event_ids=[e.event_id for e in group],
                    severity=sev,
                    confidence=conf,
                    timestamp=datetime.utcnow(),
                    explanation=(
                        f"Detected {len(failures)} failed authentication attempts for target account "
                        f"'{sample.user_id}' originating from source IP '{sample.source_ip}'."
                        + (" Followed by a successful login indicating potential credential compromise." if successes else "")
                    ),
                    evidence={
                        "user_id": sample.user_id,
                        "source_ip": sample.source_ip,
                        "failed_attempts": len(failures),
                        "compromise_success": len(successes) > 0,
                        "timestamp_first": str(failures[0].timestamp),
                        "timestamp_last": str(failures[-1].timestamp)
                    },
                    detection_category="CREDENTIAL_ACCESS",
                    is_active=True
                )
                detections.append(det)

        # 2. Check Suspicious Process Execution
        for ev in events:
            if ev.process:
                proc_lower = ev.process.lower()
                for base_cmd, keywords in self.suspicious_process_patterns:
                    if base_cmd in proc_lower:
                        matched = [kw for kw in keywords if kw in proc_lower]
                        if matched:
                            det = Detection(
                                detection_id=f"DET-PROC-{uuid.uuid4().hex[:8].upper()}",
                                rule_id="RULE-PROC-002",
                                rule_name=f"Suspicious Process Invocation: {base_cmd}",
                                event_ids=[ev.event_id],
                                severity="HIGH",
                                confidence=0.88,
                                timestamp=datetime.utcnow(),
                                explanation=(
                                    f"Process '{ev.process}' was executed on host '{ev.host_id or 'unknown'}' "
                                    f"by user '{ev.user_id or 'unknown'}'. Contains suspicious flags: {', '.join(matched)}."
                                ),
                                evidence={
                                    "process": ev.process,
                                    "matched_keywords": matched,
                                    "host_id": ev.host_id,
                                    "user_id": ev.user_id,
                                    "event_id": ev.event_id
                                },
                                detection_category="EXECUTION",
                                is_active=True
                            )
                            detections.append(det)

        # 3. Check Threat Intel IoC Matching
        for ev in events:
            matched_ioc = None
            if ev.source_ip and ev.source_ip in threat_ips:
                matched_ioc = threat_ips[ev.source_ip]
            elif ev.destination_ip and ev.destination_ip in threat_ips:
                matched_ioc = threat_ips[ev.destination_ip]

            if matched_ioc:
                det = Detection(
                    detection_id=f"DET-IOC-{uuid.uuid4().hex[:8].upper()}",
                    rule_id="RULE-TI-003",
                    rule_name=f"Threat Intelligence IoC Match: {matched_ioc.category}",
                    event_ids=[ev.event_id],
                    severity="CRITICAL" if matched_ioc.threat_score >= 80 else "HIGH",
                    confidence=matched_ioc.confidence,
                    timestamp=datetime.utcnow(),
                    explanation=(
                        f"Network or authentication event matched known threat indicator {matched_ioc.value} "
                        f"({matched_ioc.description or 'Known malicious adversary node'}). Source: {matched_ioc.source}."
                    ),
                    evidence={
                        "indicator_value": matched_ioc.value,
                        "threat_score": matched_ioc.threat_score,
                        "category": matched_ioc.category,
                        "event_source_ip": ev.source_ip,
                        "event_dest_ip": ev.destination_ip
                    },
                    detection_category="COMMAND_AND_CONTROL",
                    is_active=True
                )
                detections.append(det)

        # 4. Check Privilege Escalation & Lateral Movement
        for ev in events:
            if ev.event_type in ["PRIVILEGE_ESCALATION", "ACCOUNT_MANAGEMENT"]:
                det = Detection(
                    detection_id=f"DET-PRV-{uuid.uuid4().hex[:8].upper()}",
                    rule_id="RULE-PRIV-004",
                    rule_name="Privilege Escalation Activity Flagged",
                    event_ids=[ev.event_id],
                    severity="HIGH",
                    confidence=0.85,
                    timestamp=datetime.utcnow(),
                    explanation=f"Privilege escalation event detected on host '{ev.host_id}' for user '{ev.user_id}'.",
                    evidence={
                        "user_id": ev.user_id,
                        "host_id": ev.host_id,
                        "process": ev.process,
                        "raw_ref": ev.raw_reference
                    },
                    detection_category="PRIVILEGE_ESCALATION",
                    is_active=True
                )
                detections.append(det)

        # 5. Check Telemetry Manipulation / Anomaly Warnings
        for ev in events:
            if ev.anomaly_flags:
                det = Detection(
                    detection_id=f"DET-ANO-{uuid.uuid4().hex[:8].upper()}",
                    rule_id="RULE-QUAL-005",
                    rule_name="Telemetry Integrity Warning: Potential Log Tampering or Incompleteness",
                    event_ids=[ev.event_id],
                    severity="MEDIUM",
                    confidence=0.60,  # Lower confidence due to anomalous telemetry
                    timestamp=datetime.utcnow(),
                    explanation=(
                        f"Telemetry record {ev.event_id} exhibited data quality anomalies: "
                        f"{', '.join(ev.anomaly_flags)}. Signals potential log evasion, missing context, or malformed ingestion."
                    ),
                    evidence={
                        "anomaly_flags": ev.anomaly_flags,
                        "event_id": ev.event_id,
                        "source": ev.source
                    },
                    detection_category="DEFENSE_EVASION",
                    is_active=True
                )
                detections.append(det)

        # Persist detections in DB
        for d in detections:
            db.add(d)
        db.commit()

        duration = (time.time() - start_time) * 1000.0

        # Record Agent Execution
        execution = AgentExecution(
            execution_id=f"EXEC-DET-{uuid.uuid4().hex[:8].upper()}",
            agent_name=self.NAME,
            status="SUCCESS",
            task_description=f"Evaluated {len(events)} security events; identified {len(detections)} suspicious detections",
            input_ref=f"{len(events)} events",
            output_ref=f"{len(detections)} detections",
            duration_ms=duration,
            details={"events_analyzed": len(events), "detections_count": len(detections)},
            executed_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        # Audit record
        if detections:
            AuditService.log_action(
                db=db,
                actor_id=self.NAME,
                actor_role="AI_AGENT",
                action="DETECTIONS_GENERATED",
                target_type="DETECTION_SET",
                target_id=f"COUNT-{len(detections)}",
                details={"detections": [d.detection_id for d in detections]}
            )

        return detections
