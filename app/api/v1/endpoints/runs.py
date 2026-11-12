from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_catalog
from app.api.phase4_route import Phase4Route
from app.schemas.api import models as dto
from app.schemas.api.queries import PageQuery
from app.services.catalog import CatalogService

router = APIRouter(route_class=Phase4Route, tags=["phase4"])
ERRORS = {n: {"model": dto.Error} for n in (404, 422, 503, 500)}


@router.get(
    "/investigations/{investigationId}/runs",
    response_model=dto.RunPage,
    responses=ERRORS,
    operation_id="listInvestigationRuns",
)
async def listInvestigationRuns(
    investigationId: UUID,
    query: Annotated[PageQuery, Query()],
    service: Annotated[CatalogService, Depends(get_catalog)],
):
    return await service.children("runs", investigationId, query)


@router.get(
    "/runs/{runId}/conditions",
    response_model=dto.ConditionPage,
    responses=ERRORS,
    operation_id="listRunConditions",
)
async def listRunConditions(
    runId: UUID,
    query: Annotated[PageQuery, Query()],
    service: Annotated[CatalogService, Depends(get_catalog)],
):
    return await service.children("conditions", runId, query)


@router.get(
    "/runs/{runId}/measurements",
    response_model=dto.MeasurementPage,
    responses=ERRORS,
    operation_id="listRunMeasurements",
)
async def listRunMeasurements(
    runId: UUID,
    query: Annotated[PageQuery, Query()],
    service: Annotated[CatalogService, Depends(get_catalog)],
):
    return await service.children("measurements", runId, query)


@router.get(
    "/investigations/{investigationId}/measurements",
    response_model=dto.ObservationPage,
    responses=ERRORS,
    operation_id="listInvestigationObservations",
)
async def listInvestigationObservations(
    investigationId: UUID,
    query: Annotated[PageQuery, Query()],
    service: Annotated[CatalogService, Depends(get_catalog)],
):
    return await service.observations(investigationId, query)
