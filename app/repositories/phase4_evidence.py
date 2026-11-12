from sqlalchemy import func, select

from app.models import ClaimSource, EvidenceClaim, SourceDocument, TestRun


def claim_ids(investigation_ids):
    return (
        select(ClaimSource.claim_id)
        .join(SourceDocument)
        .where(SourceDocument.investigation_id.in_(investigation_ids))
        .distinct()
    )


class EvidenceReadRepository:
    def __init__(self, session):
        self.session = session

    async def associations(self, claim_ids_, offset=0, limit=20):
        window = (
            select(
                ClaimSource.id,
                ClaimSource.claim_id,
                func.row_number()
                .over(partition_by=ClaimSource.claim_id, order_by=ClaimSource.id)
                .label("rn"),
                func.count().over(partition_by=ClaimSource.claim_id).label("total"),
            )
            .where(ClaimSource.claim_id.in_(claim_ids_))
            .subquery()
        )
        rows = (
            await self.session.execute(
                select(ClaimSource, SourceDocument, TestRun, window.c.total)
                .join(window, window.c.id == ClaimSource.id)
                .join(SourceDocument, SourceDocument.id == ClaimSource.source_document_id)
                .outerjoin(TestRun, TestRun.id == ClaimSource.test_run_id)
                .where(window.c.rn > offset, window.c.rn <= offset + limit)
                .order_by(ClaimSource.claim_id, ClaimSource.id)
            )
        ).all()
        totals = dict(
            (
                await self.session.execute(
                    select(ClaimSource.claim_id, func.count())
                    .where(ClaimSource.claim_id.in_(claim_ids_))
                    .group_by(ClaimSource.claim_id)
                )
            ).all()
        )
        return rows, totals

    def claims(self, identity):
        return (
            select(EvidenceClaim)
            .where(EvidenceClaim.id.in_(claim_ids([identity])))
            .order_by(EvidenceClaim.id)
        )
