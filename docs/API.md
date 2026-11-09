# Guardian Angel Systems (GAS) — REST API Documentation
## Base URL: `/api/v1`

---

## 1. Authentication (`/api/v1/auth`)
- `POST /auth/login` — Authenticate via OAuth2 form data (returns JWT Bearer token).
- `POST /auth/register` — Register analyst or auditor identity.
- `GET /auth/me` — Retrieve active session profile.

## 2. Telemetry Ingestion (`/api/v1/events`)
- `POST /events/ingest` — Ingest single raw event JSON (triggers end-to-end pipeline).
- `POST /events/ingest/batch` — Ingest array of security events.
- `POST /events/upload/csv` — Multipart CSV log upload and normalisation.
- `GET /events/` — List normalised events with query parameters (`event_type`, `source`, `severity`, `is_malformed`).
- `GET /events/{event_id}` — Retrieve detailed normalised record.

## 3. Detections (`/api/v1/detections`)
- `GET /detections/` — List all suspicious activity detections.
- `GET /detections/{detection_id}` — View detection rule, confidence, and evidence citations.

## 4. Incidents (`/api/v1/incidents`)
- `GET /incidents/` — List correlated multi-event incidents.
- `GET /incidents/{incident_id}` — Get single incident details.
- `GET /incidents/{incident_id}/events` — Correlated telemetry timeline for this incident.
- `PATCH /incidents/{incident_id}` — Update status or severity.

## 5. Investigation & Explanations (`/api/v1/investigations`)
- `GET /investigations/incident/{incident_id}` — Structured investigation: MITRE ATT&CK technique matrix, kill-chain stages, facts vs hypotheses, and grounded explanations.
- `PATCH /investigations/incident/{incident_id}/notes` — Update analyst case notes.

## 6. Risk Assessment (`/api/v1/risk`)
- `GET /risk/incident/{incident_id}` — Multifactor risk score, separate confidence score, uncertainty score, contributing factors, and escalation state.

## 7. Response & Governance (`/api/v1/response`)
- `GET /response/actions` — Queue of recommended containment actions.
- `POST /response/actions/{action_id}/decision` — Submit human approval or rejection (`APPROVED` / `REJECTED`) with analyst justification.
- `POST /response/actions/{action_id}/execute` — Trigger simulated containment execution (fails if action was not approved by a human).
- `GET /response/executions` — Response execution history and containment verification status.
- `GET /response/approvals` — Immutable record of analyst approvals.

## 8. Cryptographic Audit Ledger (`/api/v1/audit`)
- `GET /audit/records` — Retrieve append-only audit trail with `previous_hash` and `record_hash`.
- `GET /audit/verify` — Cryptographically recompute the full SHA-256 hash chain to verify zero record tampering or sequence breaks.

## 9. Agent Operations (`/api/v1/agents`)
- `GET /agents/status` — Live status, tasks processed count, average latency (ms), and error metrics across all 6 agents.
- `GET /agents/executions` — Audit log of recent agent task runs.

## 10. Threat Intelligence (`/api/v1/intel`)
- `GET /intel/indicators` — Retrieve local Indicators of Compromise (IPs, domains, hashes, suspicious users).
- `POST /intel/indicators` — Create new threat intelligence indicator.

## 11. Analytics & Evaluation (`/api/v1/analytics`)
- `GET /analytics/summary` — Empirical performance metrics: Precision, Recall, F1 score, False Positive Rate, MTTD, MTTI, Alert Reduction %, and comparative baseline vs legacy SIEM.

## 12. Demonstration Scenarios (`/api/v1/scenarios`)
- `POST /scenarios/run` — Run repeatable attack scenarios (`SCENARIO_A_PHISHING`, `SCENARIO_B_LATERAL`, `SCENARIO_C_FALSE_POSITIVE`, `SCENARIO_D_MALFORMED`).
- `POST /scenarios/reset` — Cleanly reset database back to baseline seeded state.
