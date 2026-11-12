from fastapi import APIRouter

from app.api.v1.endpoints import catalog, comparison, dashboard, evidence, health, runs, scenarios

api_router = APIRouter()
api_router.include_router(health.router)


for phase4_router in (
    catalog.router,
    runs.router,
    evidence.router,
    dashboard.router,
    comparison.router,
):
    api_router.include_router(phase4_router)

api_router.include_router(scenarios.router)
