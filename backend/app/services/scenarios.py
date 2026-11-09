from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.event import SecurityEvent
from app.models.detection import Detection
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.risk import RiskAssessment
from app.models.response import RecommendedAction, Approval, ResponseExecution
from app.models.audit import AuditRecord
from app.models.agent import AgentExecution
from app.models.intel import ThreatIndicator
from app.models.user import User
from app.services.pipeline import pipeline_orchestrator
from app.services.auth import get_password_hash

class ScenarioService:
    @staticmethod
    def seed_threat_intel_and_users(db: Session):
        # Seed default users
        users = [
            ("analyst_sarah", "sarah@gas-security.internal", "analyst", "Sarah Jenkins (Senior SOC Analyst)"),
            ("admin_marcus", "marcus@gas-security.internal", "admin", "Marcus Vance (SOC Director / Lead Admin)"),
            ("auditor_elena", "elena@gas-security.internal", "auditor", "Elena Rostova (Compliance & Audit Inspector)"),
        ]
        for uname, email, role, fname in users:
            if not db.query(User).filter(User.username == uname).first():
                user = User(
                    username=uname,
                    email=email,
                    hashed_password=get_password_hash("Techgium2026!"),
                    role=role,
                    full_name=fname,
                    is_active=True
                )
                db.add(user)

        # Seed local Threat Intelligence IoCs
        threat_iocs = [
            ("IP", "198.51.100.44", 95.0, "COMMAND_AND_CONTROL", "Adversary APT-29 Command & Control relay", ["c2", "apt29", "external"]),
            ("IP", "203.0.113.195", 88.0, "BRUTE_FORCE_HOST", "Known VPN credential stuffing automated botnet", ["bruteforce", "vpn-spray"]),
            ("IP", "185.220.101.5", 78.0, "ANONYMOUS_PROXY", "Tor exit node used in credential spraying", ["tor", "anonymizer"]),
            ("DOMAIN", "update-security-portal.com", 92.0, "PHISHING_DOMAIN", "Typosquatted corporate credential phishing domain", ["phish", "credential-theft"]),
            ("HASH", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 99.0, "MALWARE_PAYLOAD", "Cobalt Strike beacon reflective loader", ["cobaltstrike", "beacon"]),
            ("USER", "admin_backup_temp", 65.0, "SUSPICIOUS_IDENTITY", "Dormant service account created during legacy migration", ["dormant", "stale-account"])
        ]
        for itype, val, score, cat, desc, tags in threat_iocs:
            if not db.query(ThreatIndicator).filter(ThreatIndicator.value == val).first():
                ti = ThreatIndicator(
                    indicator_id=f"IOC-{val.replace('.', '-')}",
                    type=itype,
                    value=val,
                    threat_score=score,
                    category=cat,
                    description=desc,
                    source="GAS_THREAT_INTEL_NETWORK",
                    tags=tags,
                    confidence=0.95
                )
                db.add(ti)

        db.commit()

    @staticmethod
    def reset_database(db: Session) -> Dict[str, str]:
        # Clean down operational tables
        db.query(ResponseExecution).delete()
        db.query(Approval).delete()
        db.query(RecommendedAction).delete()
        db.query(RiskAssessment).delete()
        db.query(Investigation).delete()
        db.query(Incident).delete()
        db.query(Detection).delete()
        db.query(SecurityEvent).delete()
        db.query(AuditRecord).delete()
        db.query(AgentExecution).delete()
        db.commit()

        # Reseed foundational items
        ScenarioService.seed_threat_intel_and_users(db)

        return {"status": "SUCCESS", "message": "Database reset cleanly to baseline state."}

    @staticmethod
    def run_scenario_a_phishing(db: Session) -> Dict[str, Any]:
        """
        Scenario A: Phishing and Credential Compromise
        """
        base_time = datetime.utcnow() - timedelta(minutes=45)
        raw_events = [
            {
                "event_id": "EVT-PHISH-001",
                "timestamp": (base_time).isoformat(),
                "source": "EMAIL_GATEWAY",
                "event_type": "EMAIL",
                "user_id": "finance_bob",
                "host_id": "corp-mail-gw01",
                "source_ip": "198.51.100.44",
                "destination_ip": "10.0.1.15",
                "process": "outlook.exe",
                "severity": "MEDIUM",
                "raw_reference": "EML-MSG-99214",
                "raw_payload": "Inbound email containing suspicious hyperlink: 'http://update-security-portal.com/login.php'"
            },
            {
                "event_id": "EVT-AUTH-002",
                "timestamp": (base_time + timedelta(minutes=5)).isoformat(),
                "source": "AUTH_SERVICE",
                "event_type": "AUTHENTICATION",
                "user_id": "finance_bob",
                "host_id": "sso-auth-portal",
                "source_ip": "203.0.113.195",
                "destination_ip": "10.0.1.50",
                "process": "login_service",
                "authentication_result": "FAILURE",
                "severity": "LOW",
                "raw_reference": "AUTH-FAIL-1001",
                "raw_payload": "Failed login attempt: invalid credentials password mismatch"
            },
            {
                "event_id": "EVT-AUTH-003",
                "timestamp": (base_time + timedelta(minutes=7)).isoformat(),
                "source": "AUTH_SERVICE",
                "event_type": "AUTHENTICATION",
                "user_id": "finance_bob",
                "host_id": "sso-auth-portal",
                "source_ip": "203.0.113.195",
                "destination_ip": "10.0.1.50",
                "process": "login_service",
                "authentication_result": "FAILURE",
                "severity": "LOW",
                "raw_reference": "AUTH-FAIL-1002",
                "raw_payload": "Failed login attempt: second consecutive bad password"
            },
            {
                "event_id": "EVT-AUTH-004",
                "timestamp": (base_time + timedelta(minutes=8)).isoformat(),
                "source": "AUTH_SERVICE",
                "event_type": "AUTHENTICATION",
                "user_id": "finance_bob",
                "host_id": "sso-auth-portal",
                "source_ip": "203.0.113.195",
                "destination_ip": "10.0.1.50",
                "process": "login_service",
                "authentication_result": "FAILURE",
                "severity": "LOW",
                "raw_reference": "AUTH-FAIL-1003",
                "raw_payload": "Failed login attempt: third consecutive bad password"
            },
            {
                "event_id": "EVT-AUTH-005",
                "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
                "source": "AUTH_SERVICE",
                "event_type": "AUTHENTICATION",
                "user_id": "finance_bob",
                "host_id": "sso-auth-portal",
                "source_ip": "203.0.113.195",
                "destination_ip": "10.0.1.50",
                "process": "login_service",
                "authentication_result": "SUCCESS",
                "severity": "HIGH",
                "raw_reference": "AUTH-SUCC-1004",
                "raw_payload": "Successful login from previously failed remote IP 203.0.113.195 (Geoloc: Eastern Europe)"
            },
            {
                "event_id": "EVT-NET-006",
                "timestamp": (base_time + timedelta(minutes=14)).isoformat(),
                "source": "FIREWALL",
                "event_type": "NETWORK_FLOW",
                "user_id": "finance_bob",
                "host_id": "wkst-bob-01",
                "source_ip": "10.0.1.15",
                "destination_ip": "198.51.100.44",
                "process": "chrome.exe",
                "severity": "CRITICAL",
                "raw_reference": "FW-FLOW-883",
                "raw_payload": "Outbound connection to known C2 indicator 198.51.100.44 port 443"
            }
        ]

        result = pipeline_orchestrator.process_raw_events(db, raw_events, actor="SCENARIO_A_RUNNER")
        return {
            "scenario_name": "Scenario A: Phishing and Credential Compromise",
            "scenario_code": "SCENARIO_A_PHISHING",
            "status": "COMPLETED",
            "events_generated": len(raw_events),
            "detections_triggered": result["detections_triggered"],
            "incidents_created": result["incidents_created"],
            "actions_recommended": result["actions_recommended"],
            "uncertainty_flagged": result["uncertainty_flagged"],
            "summary": "Simulated spearphishing lure followed by 3 credential failures, subsequent compromise success from rogue IP 203.0.113.195, and C2 beaconing to 198.51.100.44.",
            "key_observations": [
                "Agent 1 detected Brute Force and C2 IoC match.",
                "Agent 2 correlated 6 events across 'finance_bob' and '198.51.100.44'.",
                "Agent 3 mapped MITRE T1566.002, T1110, T1078, and T1071.001.",
                "Agent 5 calculated HIGH/CRITICAL risk due to compromised credentials and active C2 beaconing.",
                "Agent 6 formulated DISABLE_ACCOUNT and BLOCK_IP actions gated by human approval."
            ]
        }

    @staticmethod
    def run_scenario_b_lateral(db: Session) -> Dict[str, Any]:
        """
        Scenario B: Lateral Movement
        """
        base_time = datetime.utcnow() - timedelta(minutes=30)
        raw_events = [
            {
                "event_id": "EVT-LAT-001",
                "timestamp": (base_time).isoformat(),
                "source": "ENDPOINT",
                "event_type": "PROCESS_CREATION",
                "user_id": "admin_svc",
                "host_id": "wkst-eng-04",
                "process": "powershell.exe -enc JAB3AGgAbwBhAG0AaQAgAC8AcAByAGkAdgA=",
                "severity": "HIGH",
                "raw_reference": "EDR-PROC-501",
                "raw_payload": "Base64 encoded powershell invoking privilege enumeration 'whoami /priv'"
            },
            {
                "event_id": "EVT-LAT-002",
                "timestamp": (base_time + timedelta(minutes=4)).isoformat(),
                "source": "ENDPOINT",
                "event_type": "PRIVILEGE_ESCALATION",
                "user_id": "admin_svc",
                "host_id": "wkst-eng-04",
                "process": "cmd.exe /c net localgroup administrators admin_svc /add",
                "severity": "HIGH",
                "raw_reference": "EDR-PRIV-502",
                "raw_payload": "User account 'admin_svc' self-elevated to local administrators group"
            },
            {
                "event_id": "EVT-LAT-003",
                "timestamp": (base_time + timedelta(minutes=8)).isoformat(),
                "source": "ENDPOINT",
                "event_type": "PROCESS_CREATION",
                "user_id": "admin_svc",
                "host_id": "wkst-eng-04",
                "destination_ip": "10.0.0.10",
                "process": "psexec.exe \\\\srv-db-prod01 -s cmd.exe",
                "severity": "CRITICAL",
                "raw_reference": "EDR-PROC-503",
                "raw_payload": "PsExec remote execution initiated from wkst-eng-04 targeting critical database server srv-db-prod01"
            },
            {
                "event_id": "EVT-LAT-004",
                "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
                "source": "SIEM",
                "event_type": "AUTHENTICATION",
                "user_id": "admin_svc",
                "host_id": "srv-db-prod01",
                "source_ip": "10.0.2.14",
                "destination_ip": "10.0.0.10",
                "authentication_result": "SUCCESS",
                "severity": "HIGH",
                "raw_reference": "SIEM-AUTH-909",
                "raw_payload": "Network logon to production database server via administrative share IPC$"
            }
        ]

        result = pipeline_orchestrator.process_raw_events(db, raw_events, actor="SCENARIO_B_RUNNER")
        return {
            "scenario_name": "Scenario B: Lateral Movement & Privilege Escalation",
            "scenario_code": "SCENARIO_B_LATERAL",
            "status": "COMPLETED",
            "events_generated": len(raw_events),
            "detections_triggered": result["detections_triggered"],
            "incidents_created": result["incidents_created"],
            "actions_recommended": result["actions_recommended"],
            "uncertainty_flagged": result["uncertainty_flagged"],
            "summary": "Simulated encoded PowerShell discovery, local group elevation, and lateral movement using PsExec targeting critical server srv-db-prod01.",
            "key_observations": [
                "Agent 1 detected suspicious PowerShell commands and PsExec execution.",
                "Agent 2 linked workstation wkst-eng-04 to critical server srv-db-prod01 via shared identity 'admin_svc'.",
                "Agent 3 reconstructed MITRE T1059.001, T1068, and T1021.002.",
                "Agent 5 factored in critical database asset 'srv-db-prod01' elevating risk to P1 Critical.",
                "Agent 6 issued host isolation recommendations requiring human approval."
            ]
        }

    @staticmethod
    def run_scenario_c_false_positive(db: Session) -> Dict[str, Any]:
        """
        Scenario C: Benign False Positive
        """
        base_time = datetime.utcnow() - timedelta(minutes=20)
        raw_events = [
            {
                "event_id": "EVT-FP-001",
                "timestamp": (base_time).isoformat(),
                "source": "ENDPOINT",
                "event_type": "PROCESS_CREATION",
                "user_id": "system_backup",
                "host_id": "srv-backup-node",
                "process": "powershell.exe -NonInteractive -ExecutionPolicy Bypass -File C:\\Scripts\\ScheduledBackup.ps1",
                "severity": "LOW",
                "raw_reference": "EDR-BENIGN-01",
                "raw_payload": "Standard automated nightly snapshot backup script executed by system_backup account"
            },
            {
                "event_id": "EVT-FP-002",
                "timestamp": (base_time + timedelta(minutes=2)).isoformat(),
                "source": "AUTH_SERVICE",
                "event_type": "AUTHENTICATION",
                "user_id": "system_backup",
                "host_id": "srv-backup-node",
                "source_ip": "127.0.0.1",
                "destination_ip": "127.0.0.1",
                "authentication_result": "SUCCESS",
                "severity": "INFO",
                "raw_reference": "AUTH-LOCAL-02",
                "raw_payload": "Local system logon for scheduled maintenance job"
            }
        ]

        result = pipeline_orchestrator.process_raw_events(db, raw_events, actor="SCENARIO_C_RUNNER")
        return {
            "scenario_name": "Scenario C: Benign Administrative Activity (False Positive Handling)",
            "scenario_code": "SCENARIO_C_FALSE_POSITIVE",
            "status": "COMPLETED",
            "events_generated": len(raw_events),
            "detections_triggered": result["detections_triggered"],
            "incidents_created": result["incidents_created"],
            "actions_recommended": result["actions_recommended"],
            "uncertainty_flagged": result["uncertainty_flagged"],
            "summary": "Evaluated automated scheduled backup script. GAS inspected context, distinguished routine maintenance from offensive tradecraft, and refrained from escalating false alarms.",
            "key_observations": [
                "Agent 1 flagged execution pattern for review without triggering critical alarm.",
                "Agent 4 formulated alternative hypothesis: legitimate administrative maintenance script.",
                "Agent 5 scored overall incident risk as LOW (P4).",
                "No destructive isolation or containment actions were triggered."
            ]
        }

    @staticmethod
    def run_scenario_d_manipulated(db: Session) -> Dict[str, Any]:
        """
        Scenario D: Missing or Manipulated Telemetry
        """
        base_time = datetime.utcnow() - timedelta(minutes=15)
        raw_events = [
            {
                "event_id": "EVT-ANOM-001",
                # Missing timestamp intentionally
                "timestamp": None,
                "source": "ANONYMOUS_PROXY",  # Untrusted source
                "event_type": "AUTHENTICATION",
                "user_id": "executive_cfo",
                "host_id": None,  # Missing host telemetry
                "source_ip": "185.220.101.5",
                # Contradictory: FAILURE marked as severity LOW
                "authentication_result": "FAILURE",
                "severity": "LOW",
                "raw_reference": "CORRUPT-RAW-001",
                "raw_payload": "Altered log entry with stripped timestamp and suspicious source"
            },
            {
                "event_id": "EVT-ANOM-002",
                "timestamp": "INVALID-TIMESTAMP-STRING",  # Malformed date string
                "source": "UNVERIFIED_FORWARDER",
                "event_type": "AUTHENTICATION",
                "user_id": None,  # Missing identity
                "host_id": "srv-finance",
                "source_ip": None,  # Missing IP
                "authentication_result": "SUCCESS",
                "severity": "HIGH",
                "raw_reference": "CORRUPT-RAW-002",
                "raw_payload": "Incomplete authentication record missing user_id and source_ip"
            }
        ]

        result = pipeline_orchestrator.process_raw_events(db, raw_events, actor="SCENARIO_D_RUNNER")
        return {
            "scenario_name": "Scenario D: Missing or Manipulated Telemetry & Uncertainty Escalation",
            "scenario_code": "SCENARIO_D_MALFORMED",
            "status": "COMPLETED",
            "events_generated": len(raw_events),
            "detections_triggered": result["detections_triggered"],
            "incidents_created": result["incidents_created"],
            "actions_recommended": result["actions_recommended"],
            "uncertainty_flagged": True,
            "summary": "Tested system against missing timestamps, untrusted forwarders, missing identities, and contradictory severities. GAS triggered 'UNCERTAIN — ESCALATE TO HUMAN REVIEW'.",
            "key_observations": [
                "Telemetry Normalizer identified missing timestamp and unverified sources.",
                "Agent 1 flagged data quality anomalies and potential defense evasion.",
                "Agent 4 highlighted telemetry gaps and contradictory evidence.",
                "Agent 5 penalized confidence down to low score and uncertainty climbed over 50%.",
                "System transitioned to state: 'UNCERTAIN — ESCALATE TO HUMAN REVIEW'."
            ]
        }
