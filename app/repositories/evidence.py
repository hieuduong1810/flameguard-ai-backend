from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ClaimSource, EvidenceClaim


class EvidenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_sources_for_claim(self, claim_id: UUID) -> list[ClaimSource]:
        """Return associations, preserving locator, excerpt and optional run context."""
        result = await self.session.scalars(
            select(ClaimSource)
            .where(ClaimSource.claim_id == claim_id)
            .options(selectinload(ClaimSource.source_document), selectinload(ClaimSource.test_run))
            .order_by(ClaimSource.id)
        )
        return list(result)

    async def list_claims_for_source(self, source_document_id: UUID) -> list[EvidenceClaim]:
        # Multiple source associations may reference different runs for the same claim/document.
        result = await self.session.scalars(
            select(EvidenceClaim)
            .join(ClaimSource)
            .where(ClaimSource.source_document_id == source_document_id)
            .distinct()
            .options(
                selectinload(EvidenceClaim.source_links).selectinload(ClaimSource.source_document)
            )
            .order_by(EvidenceClaim.id)
        )
        return list(result)
