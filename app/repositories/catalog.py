from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Investigation, TestRun
from app.repositories.phase4_catalog import CatalogReadRepository
from app.schemas.catalog import InvestigationCreate, InvestigationUpdate

__all__ = ["CatalogRepository", "CatalogReadRepository"]


class CatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_investigation(self, data: InvestigationCreate) -> Investigation:
        investigation = Investigation(**data.model_dump())
        self.session.add(investigation)
        await self.session.flush()
        return investigation

    async def get_investigation(self, investigation_id: UUID) -> Investigation | None:
        result = await self.session.scalars(
            select(Investigation)
            .where(Investigation.id == investigation_id)
            .options(selectinload(Investigation.test_runs), selectinload(Investigation.tags))
        )
        return result.one_or_none()

    async def update_investigation(
        self, investigation_id: UUID, data: InvestigationUpdate
    ) -> Investigation | None:
        investigation = await self.session.get(Investigation, investigation_id)
        if investigation is not None:
            for name, value in data.model_dump(exclude_unset=True).items():
                setattr(investigation, name, value)
            await self.session.flush()
        return investigation

    async def list_test_runs(self, investigation_id: UUID) -> list[TestRun]:
        result = await self.session.scalars(
            select(TestRun)
            .where(TestRun.investigation_id == investigation_id)
            .options(selectinload(TestRun.conditions), selectinload(TestRun.measurements))
            .order_by(TestRun.id)
        )
        return list(result)
