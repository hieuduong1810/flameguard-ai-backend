from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_scenarios
from app.api.phase5_route import Phase5Route
from app.schemas.api.scenarios import Evaluation, EvaluationError, EvaluationRequest
from app.services.scenarios import ScenarioService

router = APIRouter(prefix="/mission/scenarios", tags=["mission"], route_class=Phase5Route)


@router.post(
    "/evaluate",
    response_model=Evaluation,
    operation_id="evaluateMissionScenario",
    responses={
        409: {"model": EvaluationError, "description": "Continuation bindings changed"},
        422: {"model": EvaluationError, "description": "Invalid scenario evaluation request"},
        503: {"model": EvaluationError, "description": "Evidence collection unavailable"},
        500: {"model": EvaluationError, "description": "Internal server error"},
    },
)
async def evaluate_mission_scenario(
    request: EvaluationRequest,
    service: Annotated[ScenarioService, Depends(get_scenarios)],
) -> Evaluation:
    """Inspect scoped evidence for a mission scenario using available providers."""
    return await service.evaluate(request)
