export interface SecurityEvent {
  id: number;
  event_id: string;
  timestamp: string;
  source: string;
  event_type: string;
  user_id?: string;
  host_id?: string;
  source_ip?: string;
  destination_ip?: string;
  process?: string;
  authentication_result?: string;
  severity: string;
  confidence: number;
  raw_reference?: string;
  raw_payload?: string;
  is_malformed: boolean;
  anomaly_flags: string[];
  created_at: string;
}

export interface Detection {
  id: number;
  detection_id: string;
  rule_id: string;
  rule_name: string;
  event_ids: string[];
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  timestamp: string;
  explanation: string;
  evidence: Record<string, any>;
  detection_category: string;
  is_active: boolean;
  created_at: string;
}

export interface Incident {
  id: number;
  incident_id: string;
  title: string;
  description: string;
  status: 'NEW' | 'INVESTIGATING' | 'CONTAINED' | 'ESCALATED_HUMAN_REVIEW' | 'RESOLVED' | 'FALSE_POSITIVE';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  confidence_score: number;
  primary_entities: {
    users?: string[];
    hosts?: string[];
    ips?: string[];
  };
  correlated_event_ids: string[];
  detection_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface MitreMapping {
  tactic: string;
  technique_id: string;
  technique_name: string;
  confidence: number;
  supporting_evidence: string[];
}

export interface AttackStage {
  stage: string;
  timestamp: string;
  description: string;
  entities: string[];
  event_ids: string[];
}

export interface Investigation {
  id: number;
  investigation_id: string;
  incident_id: string;
  mitre_mappings: MitreMapping[];
  attack_progression: AttackStage[];
  confirmed_evidence: Array<{
    event_id: string;
    timestamp: string;
    source: string;
    fact: string;
    verified: boolean;
  }>;
  hypotheses: Array<{
    hypothesis: string;
    confidence: number;
    verification_needed: string;
  }>;
  missing_evidence: string[];
  contradictory_evidence: string[];
  explanation: string;
  analyst_notes: string;
  created_at: string;
  updated_at: string;
}

export interface RiskAssessment {
  id: number;
  assessment_id: string;
  incident_id: string;
  risk_score: number;
  risk_category: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence_score: number;
  uncertainty_score: number;
  contributing_factors: Array<{
    factor: string;
    weight: number;
    max: number;
    description: string;
  }>;
  missing_evidence: string[];
  recommended_priority: 'P1' | 'P2' | 'P3' | 'P4';
  is_escalated: 'NORMAL' | 'ESCALATE_HUMAN_REVIEW';
  evaluated_at: string;
}

export interface RecommendedAction {
  id: number;
  action_id: string;
  incident_id: string;
  action_type: 'DISABLE_ACCOUNT' | 'ISOLATE_HOST' | 'BLOCK_IP' | 'REVOKE_SESSION' | 'ESCALATE_INCIDENT';
  target_entity: string;
  target_type: 'USER' | 'HOST' | 'IP' | 'SESSION' | 'INCIDENT';
  rationale: string;
  required_role: string;
  risk_level: string;
  policy_governance_verdict: string;
  status: 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXECUTED';
  created_at: string;
}

export interface ApprovalRecord {
  id: number;
  approval_id: string;
  action_id: string;
  incident_id: string;
  approver_username: string;
  decision: 'APPROVED' | 'REJECTED';
  notes: string;
  timestamp: string;
}

export interface ResponseExecution {
  id: number;
  execution_id: string;
  action_id: string;
  incident_id: string;
  execution_type: string;
  target: string;
  status: string;
  details: Record<string, any>;
  verification_status: string;
  executed_by: string;
  executed_at: string;
}

export interface AuditRecord {
  id: number;
  record_id: string;
  timestamp: string;
  actor_id: string;
  actor_role: string;
  action: string;
  target_type: string;
  target_id: string;
  details: Record<string, any>;
  previous_hash: string;
  record_hash: string;
}

export interface AgentStatus {
  name: string;
  code: string;
  role: string;
  status: 'HEALTHY' | 'ACTIVE' | 'IDLE' | 'DEGRADED' | 'READY';
  tasks_processed: number;
  last_execution: string | null;
  avg_duration_ms: number;
  error_count: number;
  description: string;
}

export interface ThreatIndicator {
  id: number;
  indicator_id: string;
  type: string;
  value: string;
  threat_score: number;
  category: string;
  description: string;
  source: string;
  tags: string[];
  confidence: number;
  created_at: string;
}

export interface AnalyticsSummary {
  total_events: number;
  total_detections: number;
  total_incidents: number;
  alert_reduction_percent: number;
  precision: number;
  recall: number;
  f1_score: number;
  false_positive_rate: number;
  mttd_seconds: number;
  mtti_seconds: number;
  agent_health_percent: number;
  baseline_comparison: {
    traditional_siem: Record<string, any>;
    gas_platform: Record<string, any>;
  };
  timeline_stats: Array<{
    hour: string;
    events: number;
    incidents: number;
  }>;
  severity_breakdown: Record<string, number>;
  mitre_tactic_distribution: Record<string, number>;
}
