from dataclasses import dataclass

from app.integrations.scenario_evidence.protocols import (
    ClassificationProvider,
    RankingProvider,
    RunPolicy,
)
from app.schemas.api.scenarios import EvidenceContext


@dataclass(frozen=True, slots=True)
class ScenarioProviders:
    run_policy: RunPolicy | None = None
    rankings: RankingProvider | None = None
    classifications: ClassificationProvider | None = None

    def for_context(self, context: EvidenceContext) -> "ScenarioProviders":
        if context.origin == "synthetic" and context.review_state == "unreviewed":
            return self
        return ScenarioProviders()
