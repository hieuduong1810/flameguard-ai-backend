from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_comparison
from app.api.phase4_route import Phase4Route
from app.schemas.api import models as dto
from app.services.comparison import ComparisonService

router = APIRouter(route_class=Phase4Route, tags=["phase4"])
ERRORS = {n: {"model": dto.Error} for n in (404, 422, 503, 500)}


@router.post(
    "/compare",
    response_model=dto.Comparison,
    responses=ERRORS,
    operation_id="compareInvestigations",
)
async def compareInvestigations(
    body: dto.CompareRequest, service: Annotated[ComparisonService, Depends(get_comparison)]
):
    return await service.compare(body)
