# Guardian Angel Systems (GAS) — Architecture Specification
## TECHgium 2026 | L&T Technology Services (LTTS)

---

## 1. System Philosophy & Purpose
Guardian Angel Systems (GAS) is an evidence-grounded, multi-agent cybersecurity co-pilot designed to augment Security Operations Centre (SOC) workflows through:
1. **Threat Detection** across fragmented telemetry sources.
2. **Alert Correlation & Deduplication** using entity graph linkages and temporal proximity.
3. **Deep Investigation** strictly grounded in MITRE ATT&CK techniques with verified citations.
4. **Explainable Risk & Uncertainty Scoring** separating probability from confidence and handling anomalous telemetry.
5. **Deterministic Policy-Gated Governance** requiring human analyst sign-off before consequential containment execution.
6. **Immutable Cryptographic Audit Trail** with SHA-256 hash chaining.

---

## 2. End-to-End Pipeline
```
TELEMETRY INGESTION (JSON, CSV, EDR, SIEM, Auth)
        │
        ▼
NORMALISATION ENGINE (Field validation, missing attribute detection, anomaly flags)
        │
        ▼
AGENT 1: DETECTION AGENT (Brute-force aggregation, process signatures, threat IoC matching)
        │
        ▼
AGENT 2: ALERT CORRELATION AGENT (Entity graph clustering, temporal deduplication)
        │
        ▼
AGENT 3: THREAT ANALYSIS AGENT (Kill-chain stage reconstruction, strict MITRE ATT&CK mapping)
        │
        ▼
AGENT 4: EVIDENCE & EXPLANATION AGENT (Evidence synthesis, alternative hypotheses, gap discovery)
        │
        ▼
AGENT 5: RISK ASSESSMENT AGENT (Multifactor risk scoring, confidence vs uncertainty calculation)
        │
        ▼
DETERMINISTIC GOVERNANCE GATE (Automated destructive action blocked by policy)
        │
        ▼
ANALYST REVIEW & HUMAN-IN-THE-LOOP AUTHORIZATION
        │
        ▼
CONTROLLED SIMULATED RESPONSE (Verified host quarantine, account lockout, IP blocking)
        │
        ▼
CRYPTOGRAPHIC AUDIT LEDGER (SHA-256 Merkle/Hash-chained tamper-evident ledger)
```

---

## 3. The Six Specialized Agents
| Agent | Role | Execution Mode | Key Output Contract |
|---|---|---|---|
| **Agent 1: Detection Agent** | Signature & Anomaly Detector | Deterministic Rules + Anomaly Scoring | Detections with `detection_id`, `rule_id`, confidence, and evidence map |
| **Agent 2: Alert Correlation Agent** | Deduplication & Entity Clustering | Temporal-Entity Graph Cluster | Unified Incidents with primary users, hosts, and IPs |
| **Agent 3: Threat Analysis Agent** | MITRE ATT&CK Mapper | Progression Analyzer | Structured Investigation with confirmed facts vs hypotheses |
| **Agent 4: Evidence & Explanation Agent** | Grounded Narrative Synthesizer | Evidence Citations | Grounded explanation narrative citing raw event IDs |
| **Agent 5: Risk Assessment Agent** | Multifactor Risk & Uncertainty Scorer | Risk / Uncertainty Dual Gauge | Risk score (0-100), Confidence (0-1), "UNCERTAIN" escalation flag |
| **Agent 6: Governance & Audit Agent** | Human Approval Gatekeeper | Deterministic Policy Gate | Recommended actions requiring human authorization |

---

## 4. Uncertainty & Telemetry Tampering Handling
GAS explicitly implements the critical operational state:
> `"UNCERTAIN — ESCALATE TO HUMAN REVIEW"`

When telemetry lacks required timestamps, displays contradictory authentication codes (e.g. failure logged as success), or originates from unverified forwarders, the Normalisation Engine raises anomaly flags. Agent 5 penalizes confidence, increases uncertainty above 50%, and automatically transitions the incident into human escalation, preventing dangerous autonomous decisions.
