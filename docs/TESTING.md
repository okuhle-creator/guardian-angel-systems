# Guardian Angel Systems (GAS) — Automated Testing Suite

---

## 1. Test Architecture
GAS includes comprehensive automated tests covering backend core engine algorithms, multi-agent pipeline orchestration, deterministic governance, cryptographic ledger verification, and end-to-end scenario reproduction.

## 2. Test Execution Commands

### Run all backend tests:
```powershell
cd backend
python -m pytest -v
```

### Run specific test suites:
```powershell
# Core multi-agent engine tests
python -m pytest tests/test_core_engine.py -v

# REST API integration tests
python -m pytest tests/test_api_endpoints.py -v
```

### Test coverage breakdown:
1. `test_telemetry_normalizer`:
   - Valid event schema ingestion.
   - Missing timestamp detection (`MISSING_TIMESTAMP` flag).
   - Contradictory authentication result detection.
   - Untrusted source tracking.
   - Dynamic confidence penalty evaluation.
2. `test_audit_hash_chain_integrity`:
   - Sequential SHA-256 hash chaining.
   - Tamper detection when a record's contents are maliciously altered.
3. `test_governance_policy_gate`:
   - Enforcing `PermissionError` when an unapproved action attempts execution.
   - Human approval workflow transition.
   - Verified simulated containment execution.
4. `test_scenario_a_phishing_pipeline`:
   - End-to-end spearphishing, brute-force login attempts, credential compromise, and C2 beaconing.
   - MITRE ATT&CK technique mapping verification.
5. `test_scenario_d_uncertainty_escalation`:
   - Missing/manipulated telemetry causing transition into `"UNCERTAIN — ESCALATE TO HUMAN REVIEW"`.
6. `test_health_check` & `test_auth_login`:
   - API liveness and JWT authentication issuance.
