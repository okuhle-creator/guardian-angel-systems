from pydantic import BaseModel
from typing import List, Dict, Any

class MetricCard(BaseModel):
    label: str
    value: str
    change: str
    trend: str  # positive, negative, neutral

class AnalyticsSummaryResponse(BaseModel):
    total_events: int
    total_detections: int
    total_incidents: int
    alert_reduction_percent: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    mttd_seconds: float
    mtti_seconds: float
    agent_health_percent: float
    baseline_comparison: Dict[str, Any]
    timeline_stats: List[Dict[str, Any]]
    severity_breakdown: Dict[str, int]
    mitre_tactic_distribution: Dict[str, int]

class ScenarioRunRequest(BaseModel):
    scenario_type: str  # SCENARIO_A_PHISHING, SCENARIO_B_LATERAL, SCENARIO_C_FALSE_POSITIVE, SCENARIO_D_MALFORMED, SCENARIO_E_CONTROLLED_RESPONSE
    reset_first: bool = False

class ScenarioRunResponse(BaseModel):
    scenario_name: str
    scenario_code: str
    status: str
    events_generated: int
    detections_triggered: int
    incidents_created: int
    actions_recommended: int
    uncertainty_flagged: bool
    summary: str
    key_observations: List[str]
