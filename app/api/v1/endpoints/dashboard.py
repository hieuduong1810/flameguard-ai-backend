from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_dashboard
from app.api.phase4_route import Phase4Route
from app.schemas.api import models as dto
from app.schemas.api.queries import SelectionQuery
from app.services.dashboard import DashboardService

router = APIRouter(route_class=Phase4Route, tags=["phase4"])
ERRORS = {n: {"model": dto.Error} for n in (404, 422, 503, 500)}


@router.get(
    "/dashboard/summary",
    response_model=dto.Dashboard,
    responses=ERRORS,
    operation_id="getDashboardSummary",
)
async def getDashboardSummary(
    query: Annotated[SelectionQuery, Query()],
    service: Annotated[DashboardService, Depends(get_dashboard)],
):
    return await service.summary(query)
