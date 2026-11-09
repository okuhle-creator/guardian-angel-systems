import {
  SecurityEvent,
  Detection,
  Incident,
  Investigation,
  RiskAssessment,
  RecommendedAction,
  ApprovalRecord,
  ResponseExecution,
  AuditRecord,
  AgentStatus,
  ThreatIndicator,
  AnalyticsSummary
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL 
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1` 
  : '/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('gas_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch {
      // ignore
    }
    throw new Error(errorDetail || `API request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Health
  getHealth: () => request<{ status: string; platform: string; mode: string }>('/health'),

  // Scenarios
  runScenario: (scenarioType: string, resetFirst: boolean = false) =>
    request<{
      scenario_name: string;
      scenario_code: string;
      status: string;
      events_generated: number;
      detections_triggered: number;
      incidents_created: number;
      actions_recommended: number;
      uncertainty_flagged: boolean;
      summary: string;
      key_observations: string[];
    }>('/scenarios/run', {
      method: 'POST',
      body: JSON.stringify({ scenario_type: scenarioType, reset_first: resetFirst }),
    }),

  resetDatabase: () => request<{ status: string; message: string }>('/scenarios/reset', { method: 'POST' }),

  // Analytics
  getAnalyticsSummary: () => request<AnalyticsSummary>('/analytics/summary'),

  // Events
  getEvents: (params: { skip?: number; limit?: number; event_type?: string; severity?: string; is_malformed?: boolean } = {}) => {
    const q = new URLSearchParams();
    if (params.skip) q.set('skip', params.skip.toString());
    if (params.limit) q.set('limit', params.limit.toString());
    if (params.event_type) q.set('event_type', params.event_type);
    if (params.severity) q.set('severity', params.severity);
    if (params.is_malformed !== undefined) q.set('is_malformed', params.is_malformed.toString());
    return request<SecurityEvent[]>(`/events/?${q.toString()}`);
  },

  ingestEvent: (eventData: Partial<SecurityEvent>) =>
    request<{ processed_count: number; detections_triggered: number; incidents_updated: number }>('/events/ingest', {
      method: 'POST',
      body: JSON.stringify(eventData),
    }),

  // Detections
  getDetections: (params: { severity?: string; rule_id?: string } = {}) => {
    const q = new URLSearchParams();
    if (params.severity) q.set('severity', params.severity);
    if (params.rule_id) q.set('rule_id', params.rule_id);
    return request<Detection[]>(`/detections/?${q.toString()}`);
  },

  // Incidents
  getIncidents: (params: { status?: string; severity?: string; limit?: number } = {}) => {
    const q = new URLSearchParams();
    if (params.status) q.set('status', params.status);
    if (params.severity) q.set('severity', params.severity);
    if (params.limit) q.set('limit', params.limit.toString());
    return request<Incident[]>(`/incidents/?${q.toString()}`);
  },

  getIncident: (incidentId: string) => request<Incident>(`/incidents/${incidentId}`),
  getIncidentEvents: (incidentId: string) => request<SecurityEvent[]>(`/incidents/${incidentId}/events`),
  updateIncident: (incidentId: string, updates: Partial<Incident>) =>
    request<Incident>(`/incidents/${incidentId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    }),

  // Investigation & Risk
  getInvestigation: (incidentId: string) => request<Investigation>(`/investigations/incident/${incidentId}`),
  updateNotes: (incidentId: string, notes: string) =>
    request<Investigation>(`/investigations/incident/${incidentId}/notes`, {
      method: 'PATCH',
      body: JSON.stringify({ notes }),
    }),
  getRiskAssessment: (incidentId: string) => request<RiskAssessment>(`/risk/incident/${incidentId}`),

  // Response & Governance
  getRecommendedActions: (params: { status?: string; incident_id?: string } = {}) => {
    const q = new URLSearchParams();
    if (params.status) q.set('status', params.status);
    if (params.incident_id) q.set('incident_id', params.incident_id);
    return request<RecommendedAction[]>(`/response/actions?${q.toString()}`);
  },

  submitApprovalDecision: (actionId: string, decision: 'APPROVED' | 'REJECTED', notes: string) =>
    request<ApprovalRecord>(`/response/actions/${actionId}/decision`, {
      method: 'POST',
      body: JSON.stringify({ decision, notes }),
    }),

  executeSimulatedAction: (actionId: string) =>
    request<ResponseExecution>(`/response/actions/${actionId}/execute`, { method: 'POST' }),

  getExecutions: () => request<ResponseExecution[]>('/response/executions'),
  getApprovals: () => request<ApprovalRecord[]>('/response/approvals'),

  // Audit
  getAuditRecords: (limit: number = 100) => request<AuditRecord[]>(`/audit/records?limit=${limit}`),
  verifyAuditLedger: () =>
    request<{
      total_records: number;
      is_valid: boolean;
      verified_records_count: number;
      tampered_records: string[];
      root_hash: string;
      latest_hash: string;
      message: string;
    }>('/audit/verify'),

  // Agents
  getAgentsStatus: () => request<AgentStatus[]>('/agents/status'),
  getAgentExecutions: () => request<any[]>('/agents/executions'),

  // Threat Intel
  getThreatIndicators: (type?: string) => {
    const q = type ? `?indicator_type=${type}` : '';
    return request<ThreatIndicator[]>(`/intel/indicators${q}`);
  },
  createThreatIndicator: (indicator: Partial<ThreatIndicator>) =>
    request<ThreatIndicator>('/intel/indicators', {
      method: 'POST',
      body: JSON.stringify(indicator),
    }),
};
