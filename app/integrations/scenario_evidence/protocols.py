from typing import Protocol
from uuid import UUID

from app.integrations.scenario_evidence.models import (
    AssociationRecord,
    ProviderRequest,
    RunEvidence,
)
from app.schemas.api.scenarios import Dimension


class RunPolicy(Protocol):
    version: str
    mapping_version: str

    async def evaluate(
        self, request: ProviderRequest, runs: tuple[RunEvidence, ...]
    ) -> tuple[tuple[Dimension, ...], ...]: ...


class RankingProvider(Protocol):
    version: str

    async def rank(self, request: ProviderRequest) -> bytes | None: ...


class ClassificationProvider(Protocol):
    version: str
    claim_ids: tuple[UUID, ...]

    async def classify(
        self, request: ProviderRequest, associations: tuple[AssociationRecord, ...]
    ) -> bytes: ...
