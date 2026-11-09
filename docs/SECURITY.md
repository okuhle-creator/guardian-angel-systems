# Guardian Angel Systems (GAS) — Security Architecture & Threat Model

---

## 1. Security Architecture Principles
1. **Zero Uncontrolled Automation**: Consequential containment operations (host network isolation, credential deactivation, firewall IP blacklisting) cannot be executed autonomously by any AI agent.
2. **Deterministic Policy Gatekeeper**: Agent 6 checks role-based authorization and explicit human approval in code before any execution dispatch can succeed.
3. **Traceable Accountability**: Every single decision, approval, rejection, and simulated execution is cryptographically committed to an immutable append-only ledger using SHA-256 hash chaining.
4. **Offline Resilience & Data Privacy**: Core operations do not rely on paid external LLM APIs. Customer telemetry remains strictly within the deployment perimeter.
5. **Robust Ingestion Sanitization**: All incoming telemetry is validated against malformed data, schema deviations, and contradictory states.

---

## 2. Cryptographic Hash-Chain Ledger
Every audit record contains:
- `record_id`: Unique identifier (e.g. `AUD-XXXX`)
- `timestamp`: UTC ISO 8601
- `actor_id` & `actor_role`: Identity rendering the action
- `action`: Specific operation
- `target_type` & `target_id`: Target of the action
- `details`: Canonical JSON payload
- `previous_hash`: SHA-256 of preceding block (or 64 zeros for Genesis block)
- `record_hash`: SHA-256(`record_id | timestamp | actor | action | target_type | target_id | details | previous_hash`)

Any retroactive alteration to database rows causes subsequent records' `previous_hash` checks to fail, alerting the `/api/v1/audit/verify` verification engine immediately.

---

## 3. Simulated Response Safety
Under no circumstances does GAS execute destructive shell commands or un-gated scripts against live infrastructure during demonstrations:
- Host isolation is routed through simulated endpoint driver calls.
- Account lockout updates simulated Active Directory / Okta state.
- Firewall blocking injects simulated perimeter ACL rules.
- Verification checks confirm state transitions safely.
