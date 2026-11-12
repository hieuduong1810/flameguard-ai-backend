from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.catalog import CatalogService
from app.services.collection import admit_collection, collection_context
from app.services.comparison import ComparisonService
from app.services.dashboard import DashboardService
from app.services.errors import Phase4Error
from app.services.evidence import EvidenceService
from app.services.unit_of_work import read_unit_of_work


async def get_read_context(
    request: Request, session: Annotated[AsyncSession, Depends(get_db_session)]
):
    if not request.app.state.settings.catalog_collection_manifest:
        raise Phase4Error("COLLECTION_SCOPE_INVALID")
    async with read_unit_of_work(session):
        config, slugs = await admit_collection(session, request.app.state.settings)
        context = collection_context(config)
        request.state.phase4_context = context
        yield session, context, slugs, request.app.state.settings.api_v1_prefix


def get_catalog(value: Annotated[tuple, Depends(get_read_context)]):
    return CatalogService(*value)


def get_evidence(value: Annotated[tuple, Depends(get_read_context)]):
    return EvidenceService(*value)


def get_dashboard(value: Annotated[tuple, Depends(get_read_context)]):
    return DashboardService(*value)


def get_comparison(value: Annotated[tuple, Depends(get_read_context)]):
    return ComparisonService(*value)
