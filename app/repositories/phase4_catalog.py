from sqlalchemy import and_, exists, func, or_, select

from app.models import (
    ClaimSource,
    EvidenceClaim,
    Investigation,
    InvestigationTag,
    Measurement,
    SourceDocument,
    Tag,
    TestCondition,
    TestRun,
)


def literal_contains(column, value):
    value = value.strip().lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return func.lower(column).like(f"%{value}%", escape="\\")


def equal(column, value):
    return func.lower(func.trim(column)) == value.strip().lower()


def investigation_selection(query):
    predicates = []
    if query.q and query.q.strip():
        q = query.q
        predicates.append(
            or_(
                *(
                    literal_contains(col, q)
                    for col in [
                        Investigation.psi_id,
                        Investigation.title,
                        Investigation.research_purpose,
                        Investigation.platform,
                    ]
                ),
                exists(
                    select(TestRun.id).where(
                        TestRun.investigation_id == Investigation.id,
                        literal_contains(TestRun.material_type, q),
                    )
                ),
                exists(
                    select(Tag.id)
                    .join(InvestigationTag)
                    .where(
                        InvestigationTag.investigation_id == Investigation.id,
                        or_(literal_contains(Tag.label, q), literal_contains(Tag.slug, q)),
                    )
                ),
            )
        )
    if query.platform:
        predicates.append(equal(Investigation.platform, query.platform))
    if query.purpose:
        predicates.append(literal_contains(Investigation.research_purpose, query.purpose))
    run_predicates = []
    for value, col in [
        (query.material, TestRun.material_type),
        (query.gravity_raw, TestRun.gravity),
    ]:
        if value:
            run_predicates.append(equal(col, value))
    if run_predicates:
        predicates.append(
            exists(
                select(TestRun.id).where(
                    TestRun.investigation_id == Investigation.id, *run_predicates
                )
            )
        )
    if query.tag:
        predicates.append(
            exists(
                select(Tag.id)
                .join(InvestigationTag)
                .where(
                    InvestigationTag.investigation_id == Investigation.id,
                    equal(Tag.slug, query.tag),
                )
            )
        )
    if query.source_type:
        predicates.append(
            exists(
                select(SourceDocument.id).where(
                    SourceDocument.investigation_id == Investigation.id,
                    equal(SourceDocument.document_type, query.source_type),
                )
            )
        )
    claim_predicates = []
    for value, col in [
        (query.evidence_status, EvidenceClaim.evidence_status),
        (query.review_status, EvidenceClaim.review_status),
    ]:
        if value:
            claim_predicates.append(equal(col, value))
    if claim_predicates:
        predicates.append(
            exists(
                select(ClaimSource.id)
                .join(SourceDocument)
                .join(EvidenceClaim)
                .where(SourceDocument.investigation_id == Investigation.id, *claim_predicates)
            )
        )
    return (
        select(Investigation.id).where(and_(*predicates))
        if predicates
        else select(Investigation.id)
    )


class CatalogReadRepository:
    def __init__(self, session):
        self.session = session

    async def page(self, statement, offset=0, limit=20):
        total = await self.session.scalar(
            select(func.count()).select_from(statement.order_by(None).subquery())
        )
        rows = (await self.session.scalars(statement.offset(offset).limit(limit))).all()
        return list(rows), total

    async def investigations(self, query):
        statement = select(Investigation).where(
            Investigation.id.in_(investigation_selection(query))
        )
        if query.sort == "runs-desc":
            counts = (
                select(TestRun.investigation_id, func.count().label("n"))
                .group_by(TestRun.investigation_id)
                .subquery()
            )
            statement = statement.outerjoin(counts, Investigation.id == counts.c.investigation_id)
            statement = statement.order_by(func.coalesce(counts.c.n, 0).desc(), Investigation.id)
        else:
            statement = statement.order_by(Investigation.title.collate("C"), Investigation.id)
        return await self.page(statement, query.offset, query.limit)

    async def get(self, model, identity):
        return await self.session.get(model, identity)

    async def by_psi(self, psi):
        return await self.session.scalar(select(Investigation).where(Investigation.psi_id == psi))

    async def bulk_investigations(self, ids):
        return (
            await self.session.scalars(select(Investigation).where(Investigation.id.in_(ids)))
        ).all()

    async def detail_counts(self, identity):
        from app.repositories.phase4_evidence import claim_ids

        result = {}
        for label, model, predicate in [
            ("runs", TestRun, TestRun.investigation_id == identity),
            ("sources", SourceDocument, SourceDocument.investigation_id == identity),
            ("claims", EvidenceClaim, EvidenceClaim.id.in_(claim_ids([identity]))),
        ]:
            result[label] = await self.session.scalar(
                select(func.count()).select_from(model).where(predicate)
            )
        return result

    async def children(self, model, field, identity, page):
        return await self.page(
            select(model).where(field == identity).order_by(model.id), page.offset, page.limit
        )

    async def tags(self, identity, page):
        return await self.page(
            select(Tag)
            .join(InvestigationTag)
            .where(InvestigationTag.investigation_id == identity)
            .distinct()
            .order_by(Tag.id),
            page.offset,
            page.limit,
        )

    async def tag_previews(self, ids):
        base = (
            select(InvestigationTag.investigation_id.label("parent"), Tag.id)
            .join(Tag)
            .where(InvestigationTag.investigation_id.in_(ids))
            .distinct()
            .subquery()
        )
        window = select(
            base.c.parent,
            base.c.id,
            func.row_number().over(partition_by=base.c.parent, order_by=base.c.id).label("rn"),
            func.count().over(partition_by=base.c.parent).label("total"),
        ).subquery()
        rows = (
            await self.session.execute(
                select(window.c.parent, Tag, window.c.total)
                .join(Tag, Tag.id == window.c.id)
                .where(window.c.rn <= 20)
                .order_by(window.c.parent, Tag.id)
            )
        ).all()
        result = {i: ([], 0) for i in ids}
        for parent, tag, total in rows:
            result[parent][0].append(tag)
            result[parent] = (result[parent][0], total)
        return result

    async def observations(self, identity, page):
        statement = (
            select(Measurement)
            .join(TestRun)
            .where(TestRun.investigation_id == identity)
            .order_by(Measurement.id)
        )
        rows, total = await self.page(statement, page.offset, page.limit)
        run_ids = {r.test_run_id for r in rows}
        runs = (await self.session.scalars(select(TestRun).where(TestRun.id.in_(run_ids)))).all()
        return rows, total, {r.id: r for r in runs}

    async def run_children_counts(self, ids):
        result = {i: {"conditions": 0, "measurements": 0} for i in ids}
        for model, label in [(TestCondition, "conditions"), (Measurement, "measurements")]:
            rows = (
                await self.session.execute(
                    select(model.test_run_id, func.count())
                    .where(model.test_run_id.in_(ids))
                    .group_by(model.test_run_id)
                )
            ).all()
            for identity, count in rows:
                result[identity][label] = count
        return result
