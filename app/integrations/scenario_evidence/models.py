from dataclasses import dataclass
from uuid import UUID

from app.schemas.api.scenarios import (
    Bindings,
    EvidenceContext,
    OriginalCondition,
    RunIdentity,
    ScenarioInput,
)


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    scope: Bindings
    scenario: ScenarioInput
    context: EvidenceContext

    @property
    def test_only(self) -> bool:
        return (
            self.context.origin == "synthetic"
            and self.context.review_state == "unreviewed"
            and self.context.collection_id == self.scope.collection_id
        )


@dataclass(frozen=True, slots=True)
class RunEvidence:
    run: RunIdentity
    conditions: tuple[OriginalCondition, ...]
    complete: bool


@dataclass(frozen=True, slots=True)
class AssociationRecord:
    association_id: UUID
    claim_id: UUID
    claim_text: str
    evidence_status: str
    review_status: str
    limitation: str | None
    source_document_id: UUID
    investigation_id: UUID
    source_url: str
    doi: str | None
    document_type: str
    document_version: str | None
    ingestion_status: str
    test_run_id: UUID | None
    run_investigation_id: UUID | None
    source_locator: str
    source_excerpt: str | None
