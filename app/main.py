import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.database import Database

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        logging.basicConfig(
            level=settings.log_level,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        application.state.database = Database(settings)
        logger.info("Backend started (%s)", settings.app_env)
        try:
            yield
        finally:
            await application.state.database.close()
            logger.info("Backend stopped")

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Research demonstration backend. Not operational spacecraft fire safety advice."
        ),
        debug=settings.debug,
        lifespan=lifespan,
    )
    application.state.settings = settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled request failure (%s)", type(exc).__name__)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return application


app = create_app()
