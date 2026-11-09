import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.models.event import SecurityEvent
from app.models.detection import Detection
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.risk import RiskAssessment
from app.models.response import RecommendedAction, Approval
from app.models.audit import AuditRecord
from app.models.intel import ThreatIndicator
from app.services.normalizer import TelemetryNormalizer
from app.services.audit_service import AuditService
from app.services.response_service import ResponseExecutionService
from app.services.scenarios import ScenarioService
from app.services.pipeline import pipeline_orchestrator

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    ScenarioService.seed_threat_intel_and_users(db)
    try:
        yield db
    finally:
        db.close()

def test_telemetry_normalizer():
    # Test valid event with full telemetry
    raw_valid = {
        "event_id": "EVT-TEST-1",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "SIEM",
        "event_type": "AUTHENTICATION",
        "user_id": "test_user",
        "source_ip": "10.0.0.1",
        "authentication_result": "SUCCESS"
    }
    norm, malformed, flags = TelemetryNormalizer.normalize_record(raw_valid)
    assert not malformed
    assert len(flags) == 0
    assert norm["event_id"] == "EVT-TEST-1"
    assert norm["confidence"] == 1.0

    # Test event with missing timestamp (should flag MISSING_TIMESTAMP and penalize confidence)
    raw_missing_ts = {
        "event_id": "EVT-TEST-2",
        "source": "SIEM",
        "event_type": "AUTHENTICATION"
    }
    norm_ts, malformed_ts, flags_ts = TelemetryNormalizer.normalize_record(raw_missing_ts)
    assert "MISSING_TIMESTAMP" in flags_ts
    assert norm_ts["confidence"] == 0.8

    # Test malformed & missing timestamp & contradictory auth
    raw_anom = {
        "source": "ANONYMOUS_PROXY",
        "event_type": "AUTHENTICATION",
        "authentication_result": "FAILURE",
        "severity": "LOW"
    }
    norm2, malformed2, flags2 = TelemetryNormalizer.normalize_record(raw_anom)
    assert "MISSING_TIMESTAMP" in flags2
    assert "UNTRUSTED_TELEMETRY_SOURCE" in flags2
    assert "SUSPICIOUS_LOW_SEVERITY_ON_AUTH_FAILURE" in flags2
    assert norm2["confidence"] < 1.0

def test_audit_hash_chain_integrity(test_db):
    # Log 3 audit actions
    r1 = AuditService.log_action(test_db, "analyst_1", "analyst", "INGESTION", "EVENT", "EVT-1", {"k": 1})
    r2 = AuditService.log_action(test_db, "analyst_1", "analyst", "INCIDENT_CREATED", "INCIDENT", "INC-1", {"k": 2})
    r3 = AuditService.log_action(test_db, "admin_1", "admin", "APPROVAL_GRANTED", "ACTION", "ACT-1", {"k": 3})

    assert r2.previous_hash == r1.record_hash
    assert r3.previous_hash == r2.record_hash

    # Verify chain
    is_valid, count, tampered, root_h, latest_h = AuditService.verify_chain(test_db)
    assert is_valid is True
    assert count == 3
    assert len(tampered) == 0

    # Tamper with record r2 to verify detection
    r2.actor_id = "malicious_hacker"
    test_db.commit()

    is_valid_after, count_after, tampered_after, _, _ = AuditService.verify_chain(test_db)
    assert is_valid_after is False
    assert len(tampered_after) > 0

def test_governance_policy_gate(test_db):
    # Create action
    action = RecommendedAction(
        action_id="ACT-TEST-001",
        incident_id="INC-TEST",
        action_type="ISOLATE_HOST",
        target_entity="srv-finance",
        target_type="HOST",
        rationale="Ransomware lateral movement prevention",
        required_role="admin",
        policy_governance_verdict="REQUIRES_HUMAN_APPROVAL",
        status="PENDING_APPROVAL"
    )
    test_db.add(action)
    test_db.commit()

    # Attempting to execute unapproved action MUST raise PermissionError
    with pytest.raises(PermissionError):
        ResponseExecutionService.execute_simulated_action(test_db, "ACT-TEST-001", "auto_bot")

    # Approve action as human analyst
    approval, updated_act = ResponseExecutionService.process_approval(
        test_db, "ACT-TEST-001", "APPROVED", "analyst_sarah", "Approved host isolation"
    )
    assert updated_act.status == "APPROVED"
    assert approval.decision == "APPROVED"

    # Now simulated execution succeeds
    execution = ResponseExecutionService.execute_simulated_action(test_db, "ACT-TEST-001", "admin_marcus")
    assert execution.status == "SIMULATED_SUCCESS"
    assert execution.verification_status == "VERIFIED_CONTAINED"
    assert updated_act.status == "EXECUTED"

def test_scenario_a_phishing_pipeline(test_db):
    result = ScenarioService.run_scenario_a_phishing(test_db)
    assert result["status"] == "COMPLETED"
    assert result["events_generated"] == 6
    assert result["detections_triggered"] >= 1
    assert result["incidents_created"] >= 1

    # Check incident was created with MITRE mappings
    incident = test_db.query(Incident).first()
    assert incident is not None
    assert incident.severity in ["HIGH", "CRITICAL"]

    investigation = test_db.query(Investigation).filter(Investigation.incident_id == incident.incident_id).first()
    assert investigation is not None
    assert len(investigation.mitre_mappings) > 0

    risk = test_db.query(RiskAssessment).filter(RiskAssessment.incident_id == incident.incident_id).first()
    assert risk is not None
    assert risk.risk_score >= 60.0

def test_scenario_d_uncertainty_escalation(test_db):
    result = ScenarioService.run_scenario_d_manipulated(test_db)
    assert result["uncertainty_flagged"] is True

    # Confirm incident is marked ESCALATED_HUMAN_REVIEW
    escalated_inc = test_db.query(Incident).filter(Incident.status == "ESCALATED_HUMAN_REVIEW").first()
    assert escalated_inc is not None
