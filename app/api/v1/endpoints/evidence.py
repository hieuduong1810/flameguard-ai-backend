from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_evidence
from app.api.phase4_route import Phase4Route
from app.schemas.api import models as dto
from app.schemas.api.queries import PageQuery
from app.services.evidence import EvidenceService

router = APIRouter(route_class=Phase4Route, tags=["phase4"])
ERRORS = {n: {"model": dto.Error} for n in (404, 422, 503, 500)}


@router.get(
    "/investigations/{investigationId}/sources",
    response_model=dto.SourcePage,
    responses=ERRORS,
    operation_id="listInvestigationSources",
)
async def listInvestigationSources(
    investigationId: UUID,
    query: Annotated[PageQuery, Query()],
    service: Annotated[EvidenceService, Depends(get_evidence)],
):
    return await service.children("sources", investigationId, query)


@router.get(
    "/investigations/{investigationId}/claims",
    response_model=dto.ClaimPage,
    responses=ERRORS,
    operation_id="listInvestigationClaims",
)
async def listInvestigationClaims(
    investigationId: UUID,
    query: Annotated[PageQuery, Query()],
    service: Annotated[EvidenceService, Depends(get_evidence)],
):
    return await service.claims(investigationId, query)


@router.get(
    "/claims/{claimId}/sources",
    response_model=dto.ClaimSourcePage,
    responses=ERRORS,
    operation_id="listClaimSourceAssociations",
)
async def listClaimSourceAssociations(
    claimId: UUID,
    query: Annotated[PageQuery, Query()],
    service: Annotated[EvidenceService, Depends(get_evidence)],
):
    return await service.associations(claimId, query)
