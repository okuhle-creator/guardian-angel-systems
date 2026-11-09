# GUARDIAN ANGEL SYSTEMS (GAS)
## Enterprise-Grade AI-Supported Cyber-Resilience Platform
### TECHgium 2026 | L&T Technology Services (LTTS) | Set 2

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS v4](https://img.shields.io/badge/TailwindCSS-v4.0-38B2AC.svg)](https://tailwindcss.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

---

## 1. PRODUCT IDENTITY & POSITIONING
- **Product Name**: Guardian Angel Systems
- **Abbreviation**: GAS
- **Competition**: TECHgium 2026
- **Organisation**: L&T Technology Services (LTTS)
- **Category**: Cybersecurity / AI-Supported Security Operations

### Core Philosophy:
> **DETECT. CORRELATE. INVESTIGATE. EXPLAIN. GOVERN. PROTECT.**

Guardian Angel Systems (GAS) is an evidence-grounded, multi-agent cybersecurity co-pilot designed to improve modern Security Operations Centres (SOCs) through:
- Real-time suspicious activity detection across fragmented telemetry.
- Alert deduplication and incident relationship graph correlation.
- Deep kill-chain progression mapping strictly to MITRE ATT&CK techniques.
- Traceable evidence-grounded explanations with alternative hypothesis formulation.
- Separate risk and confidence scoring with explicit uncertainty handling (`"UNCERTAIN — ESCALATE TO HUMAN REVIEW"`).
- Deterministic policy-gated human oversight before any consequential containment action.
- Tamper-evident, append-only cryptographic audit records with SHA-256 hash chaining.
- **100% Offline Capability**: Works without paid external LLM APIs.

---

## 2. THE SIX SPECIALIZED AGENTS

```
  ┌────────────────────────────────────────────────────────┐
  │              TELEMETRY NORMALISATION                   │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ AGENT 1: DETECTION AGENT                               │
  │ • Signature inspection & brute-force aggregation       │
  │ • Process execution flags & threat IoC cross-referencing│
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ AGENT 2: ALERT CORRELATION AGENT                       │
  │ • Entity graph clustering (Users, Hosts, IPs)          │
  │ • Temporal proximity window fusion                     │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ AGENT 3: THREAT ANALYSIS AGENT                         │
  │ • MITRE ATT&CK technique mapping with citations        │
  │ • Attack kill-chain stage trajectory reconstruction    │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ AGENT 4: EVIDENCE & EXPLANATION AGENT                  │
  │ • Grounded narrative synthesis tied to raw event IDs   │
  │ • Counter-hypotheses & telemetry gap discovery         │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ AGENT 5: RISK ASSESSMENT AGENT                         │
  │ • Multifactor risk (0-100) & separate confidence score │
  │ • Flags: "UNCERTAIN — ESCALATE TO HUMAN REVIEW"        │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ AGENT 6: GOVERNANCE & AUDIT AGENT                      │
  │ • Deterministic policy gate (Automated action blocked) │
  │ • Mandatory human analyst sign-off                     │
  │ • Simulated safe containment execution                 │
  │ • SHA-256 Merkle/Hash-chained tamper-evident ledger    │
  └────────────────────────────────────────────────────────┘
```

---

## 3. THE NINE APPLICATION MODULES

1. **Command Centre**: Operational SOC overview displaying live active incidents, critical alerts, events processed, alert reduction percentage, agent health, and pending approvals.
2. **Threat Detection**: Multi-source log ingestion (manual form, synthetic generator, CSV upload), normalized telemetry inspector vs original payload, anomaly flags, and detections feed.
3. **Incident Management**: Incident listing with status and severity filters, correlated entity graph (Users, Hosts, IPs), and chronological event timeline.
4. **Investigation Workspace**: Deep incident workspace with verified evidence citations, kill-chain attack progression stages, strict MITRE ATT&CK matrix technique mapping, grounded narrative explanations, and case notes editor.
5. **Threat Intelligence**: Local Indicators of Compromise (IPs, domains, hashes, suspicious identities) with threat scoring, categories, tags, and new indicator creation.
6. **Agent Operations**: Live operational dashboard displaying all 6 agents with responsibilities, tasks processed, average execution latency (ms), error counts, and recent execution audit traces.
7. **Response Centre**: Queue of recommended containment measures, policy governance gates (`REQUIRES_HUMAN_APPROVAL`), Human Approval and Rejection actions with analyst justification input, and simulated safe execution with verification checks.
8. **Audit Centre**: Immutable append-only audit trail with previous hash and record hash, plus live "Verify Cryptographic Chain" action that validates uninterrupted SHA-256 hash continuity.
9. **Analytics and Evaluation**: Detection precision, recall, F1 score, false-positive rate, alert fatigue reduction %, MTTD, MTTI, Recharts trend charts, and comparative baseline table vs conventional SIEM.

---

## 4. REPEATABLE DEMONSTRATION SCENARIOS

All scenarios can be triggered with 1-click from the top navigation bar or via REST API:

- **Scenario A: Phishing and Credential Compromise**:
  Simulates inbound spearphishing email, 3 failed authentication attempts followed by compromise login from rogue IP `203.0.113.195`, and C2 beaconing to `198.51.100.44`. Maps MITRE T1566.002, T1110, T1078, T1071.001.
- **Scenario B: Lateral Movement & Privilege Escalation**:
  Simulates encoded PowerShell discovery, local administrator elevation, and PsExec network traversal targeting critical server `srv-db-prod01`. Maps MITRE T1059.001, T1068, T1021.002.
- **Scenario C: Benign Activity (False Positive Handling)**:
  Simulates scheduled maintenance backup script. GAS inspects context, identifies routine administrative task, and refrains from escalating false alarms.
- **Scenario D: Missing or Manipulated Telemetry & Uncertainty Escalation**:
  Simulates stripped timestamps, untrusted forwarders, and contradictory severities. GAS penalizes confidence, increases uncertainty above 50%, and transitions into system state: `"UNCERTAIN — ESCALATE TO HUMAN REVIEW"`.
- **Scenario E: Controlled Response**:
  Inspect proposed host isolation and account suspension, review rationale, authorize approval as human analyst, execute simulated containment, and verify state transition.
- **Reset Database**:
  Cleans operational tables back to baseline seeded state.

---

## 5. LOCAL DEVELOPMENT (WINDOWS 10 POWERSHELL)

### Prerequisites:
- Python 3.11+
- Node.js v20+ & npm

### Option A: One-Click Startup Script (Recommended)
```powershell
.\scripts\start-dev.ps1
```

### Option B: Manual Startup

#### 1. Backend Service
```powershell
cd backend
$env:PYTHONPATH = "."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive Swagger API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

#### 2. Frontend Application
```powershell
cd frontend
npm install
npm run dev
```
- Frontend UI: `http://localhost:5173`

---

## 6. RUNNING AUTOMATED TESTS

Execute the comprehensive automated test suite:
```powershell
# Using the test script
.\scripts\run-tests.ps1

# Or running pytest directly:
cd backend
python -m pytest -v
```

All 9 test suites pass:
- `test_telemetry_normalizer`: Verifies schema normalisation, missing timestamp detection, and confidence penalty.
- `test_audit_hash_chain_integrity`: Verifies SHA-256 hash chaining and detects retroactive row tampering.
- `test_governance_policy_gate`: Enforces `PermissionError` on unapproved actions and verifies human approval workflow.
- `test_scenario_a_phishing_pipeline`: End-to-end spearphishing and credential compromise verification.
- `test_scenario_d_uncertainty_escalation`: Verifies `"UNCERTAIN — ESCALATE TO HUMAN REVIEW"` state.
- `test_health_check` & `test_auth_login`: Verifies API availability and JWT tokens.
- `test_scenario_run_and_analytics`: Verifies end-to-end scenario runner and analytics calculations.

---

## 7. PRODUCTION DEPLOYMENT ARCHITECTURE

- **Frontend**: React + TypeScript + Vite deployed on **Vercel**.
- **Backend**: Python + FastAPI deployed on **Render** (assigns dynamic `$PORT`).
- **Database**: PostgreSQL hosted on **Neon** (`DATABASE_URL`).

Refer to [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the 10-step step-by-step production deployment checklist.

---

## 8. DEMONSTRATION CREDENTIALS (SYNTHETIC)

| Role | Username | Password | Full Name |
|---|---|---|---|
| **Senior SOC Analyst** | `analyst_sarah` | `Techgium2026!` | Sarah Jenkins |
| **SOC Director / Admin** | `admin_marcus` | `Techgium2026!` | Marcus Vance |
| **Compliance Inspector** | `auditor_elena` | `Techgium2026!` | Elena Rostova |

---

## 9. ACCEPTANCE CRITERIA STATUS

- [x] Frontend runs locally on port 5173.
- [x] Backend runs locally on port 8000 with interactive docs at `/docs`.
- [x] Database persists data (SQLite locally, Neon PostgreSQL in production).
- [x] Authentication works (PBKDF2-HMAC-SHA256 password hashing + JWT access tokens).
- [x] Security events ingested via JSON, CSV, API, and synthetic generator.
- [x] Detection engine produces real explainable detections.
- [x] Alerts correlated into incidents using entity graph and temporal proximity.
- [x] Incident investigations work with kill-chain progression stages.
- [x] Strict MITRE ATT&CK technique mapping with citations.
- [x] Explanations strictly reference real stored evidence.
- [x] Risk and confidence calculated separately.
- [x] Missing or manipulated telemetry handled with confidence penalty.
- [x] System state `"UNCERTAIN — ESCALATE TO HUMAN REVIEW"` supported.
- [x] Human approval enforced via deterministic policy gatekeeper.
- [x] Simulated responses execute safely with verification status.
- [x] Audit records persisted with SHA-256 cryptographic hash chaining.
- [x] All 6 agents have working responsibilities and backend execution records.
- [x] Demonstration scenarios (A, B, C, D, E) repeatable and resettable.
- [x] Evaluation metrics calculated from actual operational data.
- [x] Critical automated tests pass (100% pass rate).
- [x] Zero critical frontend or backend runtime errors.
- [x] GitHub repository clean and deployable.
- [x] Vercel deployment configuration prepared (`frontend/vercel.json`).
- [x] Render deployment configuration prepared (`render.yaml`).
- [x] Neon PostgreSQL configuration supported (`DATABASE_URL`).
- [x] Complete architecture, API, security, testing, and deployment documentation provided.
