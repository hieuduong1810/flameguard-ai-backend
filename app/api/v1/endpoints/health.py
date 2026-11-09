import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse, "description": "Database unavailable"}},
)
async def ready(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReadinessResponse:
    try:
        async with asyncio.timeout(request.app.state.settings.db_ready_timeout_seconds):
            await session.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError, TimeoutError):
        # Exception messages may contain connection strings or server details.
        logger.warning("Database readiness check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(status="unavailable", database="unavailable")
    return ReadinessResponse(status="ready", database="ok")
