from app.models import EvidenceClaim, Investigation
from app.repositories.evidence import EvidenceReadRepository
from app.services.catalog import CatalogService, scalar_fields


class EvidenceService(CatalogService):
    async def association_pages(self, ids, offset=0, limit=20):
        rows, totals = await EvidenceReadRepository(self.session).associations(ids, offset, limit)
        grouped = {i: [] for i in ids}
        for link, source, run, _ in rows:
            grouped[link.claim_id].append(
                {
                    "id": link.id,
                    "claimId": link.claim_id,
                    "source": self.source(source),
                    "testRunId": link.test_run_id,
                    "runInvestigationId": run.investigation_id if run else None,
                    "sourceLocator": link.source_locator,
                    "sourceExcerpt": link.source_excerpt,
                    "contextMismatch": run is not None
                    and run.investigation_id != source.investigation_id,
                    "context": self.context,
                }
            )
        return {
            i: self.page(grouped[i], totals.get(i, 0), offset, limit, f"/claims/{i}/sources")
            for i in ids
        }

    async def claims(self, identity, query):
        await self.require(Investigation, identity)
        rows, total = await self.repo.page(
            EvidenceReadRepository(self.session).claims(identity), query.offset, query.limit
        )
        sources = await self.association_pages([r.id for r in rows])
        return self.page(
            [{**scalar_fields(r), "sources": sources[r.id], "context": self.context} for r in rows],
            total,
            query.offset,
            query.limit,
            f"/investigations/{identity}/claims",
        )

    async def associations(self, identity, query):
        await self.require(EvidenceClaim, identity)
        return (await self.association_pages([identity], query.offset, query.limit))[identity]
