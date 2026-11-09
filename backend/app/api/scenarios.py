from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database.session import get_db
from app.schemas.analytics import ScenarioRunRequest, ScenarioRunResponse
from app.services.scenarios import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["Demonstration Scenarios"])

@router.post("/run", response_model=ScenarioRunResponse)
def run_scenario(request: ScenarioRunRequest, db: Session = Depends(get_db)):
    if request.reset_first:
        ScenarioService.reset_database(db)

    stype = request.scenario_type.upper()
    if stype == "SCENARIO_A_PHISHING":
        return ScenarioService.run_scenario_a_phishing(db)
    elif stype == "SCENARIO_B_LATERAL":
        return ScenarioService.run_scenario_b_lateral(db)
    elif stype == "SCENARIO_C_FALSE_POSITIVE":
        return ScenarioService.run_scenario_c_false_positive(db)
    elif stype == "SCENARIO_D_MALFORMED":
        return ScenarioService.run_scenario_d_manipulated(db)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown scenario type: {request.scenario_type}")

@router.post("/reset")
def reset_demonstration_database(db: Session = Depends(get_db)):
    return ScenarioService.reset_database(db)
