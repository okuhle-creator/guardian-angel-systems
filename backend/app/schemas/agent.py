from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentHealthStatus(BaseModel):
    name: str
    code: str
    role: str
    status: str  # HEALTHY, ACTIVE, IDLE, DEGRADED
    tasks_processed: int
    last_execution: Optional[datetime]
    avg_duration_ms: float
    error_count: int
    description: str

class AgentExecutionResponse(BaseModel):
    id: int
    execution_id: str
    agent_name: str
    status: str
    task_description: str
    input_ref: Optional[str]
    output_ref: Optional[str]
    duration_ms: float
    details: Dict[str, Any]
    error_message: Optional[str]
    executed_at: datetime

    class Config:
        from_attributes = True
