import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import Base, engine, SessionLocal
from app.services.scenarios import ScenarioService

@pytest.fixture(scope="module")
def client():
    # Setup test DB tables and seed
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    ScenarioService.seed_threat_intel_and_users(db)
    db.close()

    with TestClient(app) as test_client:
        yield test_client

def test_health_check(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

def test_auth_login(client):
    res = client.post("/api/v1/auth/login", data={"username": "analyst_sarah", "password": "Techgium2026!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "analyst"

def test_scenario_run_and_analytics(client):
    # Run Scenario B Lateral Movement
    res = client.post("/api/v1/scenarios/run", json={"scenario_type": "SCENARIO_B_LATERAL", "reset_first": True})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["events_generated"] == 4

    # Check incidents
    inc_res = client.get("/api/v1/incidents/")
    assert inc_res.status_code == 200
    incidents = inc_res.json()
    assert len(incidents) >= 1
    inc_id = incidents[0]["incident_id"]

    # Check investigation
    inv_res = client.get(f"/api/v1/investigations/incident/{inc_id}")
    assert inv_res.status_code == 200
    assert len(inv_res.json()["mitre_mappings"]) > 0

    # Check risk
    risk_res = client.get(f"/api/v1/risk/incident/{inc_id}")
    assert risk_res.status_code == 200
    assert risk_res.json()["risk_score"] > 0

    # Check agents status
    agents_res = client.get("/api/v1/agents/status")
    assert agents_res.status_code == 200
    assert len(agents_res.json()) == 6

    # Check audit ledger verification
    audit_res = client.get("/api/v1/audit/verify")
    assert audit_res.status_code == 200
    assert audit_res.json()["is_valid"] is True

    # Check analytics summary
    analytics_res = client.get("/api/v1/analytics/summary")
    assert analytics_res.status_code == 200
    assert analytics_res.json()["total_events"] >= 4

def test_human_approval_workflow(client):
    # Fetch pending actions
    actions_res = client.get("/api/v1/response/actions?status=PENDING_APPROVAL")
    assert actions_res.status_code == 200
    actions = actions_res.json()
    if len(actions) > 0:
        act = actions[0]
        # Approve action
        appr_res = client.post(
            f"/api/v1/response/actions/{act['action_id']}/decision",
            json={"decision": "APPROVED", "notes": "Authorized by Senior Analyst for live quarantine"}
        )
        assert appr_res.status_code == 200
        assert appr_res.json()["decision"] == "APPROVED"

        # Execute simulated response
        exec_res = client.post(f"/api/v1/response/actions/{act['action_id']}/execute")
        assert exec_res.status_code == 200
        assert exec_res.json()["status"] == "SIMULATED_SUCCESS"
        assert exec_res.json()["verification_status"] == "VERIFIED_CONTAINED"
