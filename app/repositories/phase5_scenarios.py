from collections import defaultdict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.scenario_evidence.execution import MAX_ENTRIES
from app.integrations.scenario_evidence.models import AssociationRecord, RunEvidence
from app.models import (
    ClaimSource,
    EvidenceClaim,
    Investigation,
    SourceDocument,
    TestCondition,
    TestRun,
)
from app.schemas.api.scenarios import InvestigationIdentity, OriginalCondition, RunIdentity

CONDITION_LIMIT = 1_000


class ScenarioEvidenceRepository:
    """Reads only after exact collection admission in the caller's snapshot."""

    def __init__(self, session: AsyncSession, slugs: dict[str, str]) -> None:
        self.session = session
        self.slugs = slugs

    def investigation(self, row: Investigation) -> InvestigationIdentity:
        return InvestigationIdentity(
            investigation_id=row.id, psi_id=row.psi_id, slug=self.slugs.get(row.psi_id)
        )

    async def runs(self, offset: int, limit: int) -> tuple[int, tuple[RunEvidence, ...]]:
        total = await self.session.scalar(select(func.count()).select_from(TestRun))
        rows = (
            await self.session.execute(
                select(TestRun, Investigation)
                .join(Investigation, Investigation.id == TestRun.investigation_id)
                .order_by(TestRun.id)
                .offset(offset)
                .limit(limit)
            )
        ).all()
        conditions = await self.conditions(tuple(run.id for run, _ in rows))
        return total, tuple(
            RunEvidence(
                run=RunIdentity(
                    run_id=run.id,
                    external_run_key=run.external_run_key,
                    investigation=self.investigation(investigation),
                    material_type=run.material_type,
                    sample_geometry=run.sample_geometry,
                    gravity=run.gravity,
                ),
                conditions=tuple(conditions[run.id][:CONDITION_LIMIT]),
                complete=len(conditions[run.id]) <= CONDITION_LIMIT,
            )
            for run, investigation in rows
        )

    async def conditions(self, run_ids: tuple[UUID, ...]):
        result = defaultdict(list)
        if not run_ids:
            return result
        window = (
            select(
                TestCondition.id,
                func.row_number()
                .over(
                    partition_by=TestCondition.test_run_id,
                    order_by=TestCondition.id,
                )
                .label("position"),
            )
            .where(TestCondition.test_run_id.in_(run_ids))
            .subquery()
        )
        rows = await self.session.scalars(
            select(TestCondition)
            .join(window, window.c.id == TestCondition.id)
            .where(window.c.position <= CONDITION_LIMIT + 1)
            .order_by(TestCondition.test_run_id, TestCondition.id)
        )
        for row in rows:
            result[row.test_run_id].append(
                OriginalCondition(
                    condition_id=row.id,
                    run_id=row.test_run_id,
                    variable=row.variable,
                    value_numeric=row.value_numeric,
                    value_text=row.value_text,
                    unit=row.unit,
                    data_status=row.data_status,
                )
            )
        return result

    async def ranking_identities(self) -> tuple[InvestigationIdentity, ...] | None:
        rows = list(
            await self.session.scalars(
                select(Investigation).order_by(Investigation.id).limit(MAX_ENTRIES + 1)
            )
        )
        if len(rows) > MAX_ENTRIES:
            return None
        return tuple(self.investigation(row) for row in rows)

    async def associations(
        self, claim_ids: tuple[UUID, ...]
    ) -> tuple[AssociationRecord, ...] | None:
        if not claim_ids:
            return ()
        if len(claim_ids) > MAX_ENTRIES or len(set(claim_ids)) != len(claim_ids):
            return None
        rows = (
            await self.session.execute(
                select(ClaimSource, EvidenceClaim, SourceDocument, TestRun.investigation_id)
                .join(EvidenceClaim, EvidenceClaim.id == ClaimSource.claim_id)
                .join(SourceDocument, SourceDocument.id == ClaimSource.source_document_id)
                .outerjoin(TestRun, TestRun.id == ClaimSource.test_run_id)
                .where(ClaimSource.claim_id.in_(claim_ids))
                .order_by(ClaimSource.id)
                .limit(MAX_ENTRIES + 1)
            )
        ).all()
        if len(rows) > MAX_ENTRIES:
            return None
        return tuple(
            AssociationRecord(
                association_id=link.id,
                claim_id=claim.id,
                claim_text=claim.claim_text,
                evidence_status=claim.evidence_status,
                review_status=claim.review_status,
                limitation=claim.limitation,
                source_document_id=document.id,
                investigation_id=document.investigation_id,
                source_url=document.source_url,
                doi=document.doi,
                document_type=document.document_type,
                document_version=document.version,
                ingestion_status=document.ingestion_status,
                test_run_id=link.test_run_id,
                run_investigation_id=run_investigation,
                source_locator=link.source_locator,
                source_excerpt=link.source_excerpt,
            )
            for link, claim, document, run_investigation in rows
        )
