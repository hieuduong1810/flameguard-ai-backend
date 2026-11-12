from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Scenario, ScenarioMatch


class ScenarioRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_scenario(self, scenario: Scenario) -> None:
        self.session.add(scenario)
        await self.session.flush()

    async def list_matches(self, scenario_id: UUID) -> list[ScenarioMatch]:
        result = await self.session.scalars(
            select(ScenarioMatch)
            .where(ScenarioMatch.scenario_id == scenario_id)
            .options(selectinload(ScenarioMatch.test_run), selectinload(ScenarioMatch.dimensions))
            .order_by(ScenarioMatch.id)
        )
        return list(result)
