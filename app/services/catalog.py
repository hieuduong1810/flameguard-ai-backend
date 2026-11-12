from decimal import Decimal
from urllib.parse import urlencode

from pydantic.alias_generators import to_camel

from app.models import (
    Investigation,
    Measurement,
    SourceDocument,
    TestCondition,
    TestRun,
)
from app.repositories.catalog import CatalogReadRepository
from app.services.errors import Phase4Error

RICH_FIELDS = [
    "code",
    "hardware",
    "facility",
    "fuelCategory",
    "yearRange",
    "primaryInvestigator",
    "institution",
    "findings",
    "confidence",
    "citationBibliography",
]


def scalar_fields(row):
    result = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        result[column.name] = format(value, "f") if isinstance(value, Decimal) else value
    return result


class CatalogService:
    def __init__(self, session, context, slugs, prefix="/api/v1"):
        self.session, self.context, self.slugs, self.prefix = session, context, slugs, prefix
        self.repo = CatalogReadRepository(session)

    def page(self, items, total, offset, limit, path, params=None):
        more = offset + limit < total
        query = {**(params or {}), "offset": offset + limit, "limit": limit}
        return {
            "items": items,
            "total": total,
            "offset": offset,
            "limit": limit,
            "next": self.prefix + path + "?" + urlencode(query) if more else None,
            "context": self.context,
        }

    def link(self, path, total):
        return {"href": self.prefix + path, "total": total}

    async def require(self, model, identity):
        row = await self.repo.get(model, identity)
        if row is None:
            raise Phase4Error("ENTITY_NOT_FOUND", 404)
        return row

    def source(self, row):
        return {**scalar_fields(row), "context": self.context}

    async def investigation_views(self, rows):
        previews = await self.repo.tag_previews([r.id for r in rows])
        result = []
        for row in rows:
            tags, total = previews[row.id]
            unavailable = {field: "UNSUPPORTED_MAPPING" for field in RICH_FIELDS}
            if row.platform is None:
                unavailable["platform"] = "MISSING_SOURCE_DATA"
            if row.research_purpose is None:
                unavailable["researchPurpose"] = "MISSING_SOURCE_DATA"
            result.append(
                {
                    **scalar_fields(row),
                    "slug": self.slugs.get(row.psi_id),
                    "tags": self.page(
                        [self.source(t) for t in tags],
                        total,
                        0,
                        20,
                        f"/investigations/{row.id}/tags",
                    ),
                    "unavailableFields": unavailable,
                    "context": self.context,
                }
            )
        return result

    async def investigations(self, query):
        rows, total = await self.repo.investigations(query)
        return self.page(
            await self.investigation_views(rows),
            total,
            query.offset,
            query.limit,
            "/investigations",
            query.model_dump(by_alias=True, exclude_none=True, exclude={"offset", "limit"}),
        )

    async def detail(self, identity):
        row = await self.require(Investigation, identity)
        result = (await self.investigation_views([row]))[0]
        for label, total in (await self.repo.detail_counts(identity)).items():
            result[label] = self.link(f"/investigations/{identity}/{label}", total)
        return result

    async def by_slug(self, slug):
        psi = next((psi for psi, value in self.slugs.items() if value == slug), None)
        if psi is None:
            raise Phase4Error("ENTITY_NOT_FOUND", 404)
        row = await self.repo.by_psi(psi)
        if row is None:
            raise Phase4Error("IDENTITY_MAPPING_UNAVAILABLE")
        return await self.detail(row.id)

    async def tags(self, identity, query):
        await self.require(Investigation, identity)
        rows, total = await self.repo.tags(identity, query)
        return self.page(
            [self.source(r) for r in rows],
            total,
            query.offset,
            query.limit,
            f"/investigations/{identity}/tags",
        )

    async def run_views(self, rows):
        counts = await self.repo.run_children_counts([r.id for r in rows])
        return [
            {
                **scalar_fields(r),
                "context": self.context,
                "verification": "unknown",
                "unavailableFields": {"verification": "VERIFICATION_NOT_ESTABLISHED"},
                **{
                    key: self.link(f"/runs/{r.id}/{key}", count)
                    for key, count in counts[r.id].items()
                },
            }
            for r in rows
        ]

    def measurement(self, row):
        unavailable = {"telemetry": "ASSET_CONTRACT_PENDING"}
        for key in ["measured_value", "uncertainty"]:
            if getattr(row, key) is None:
                unavailable[to_camel(key)] = "MISSING_SOURCE_DATA"
        return {**scalar_fields(row), "unavailableFields": unavailable, "context": self.context}

    async def children(self, kind, identity, query):
        mapping = {
            "runs": (Investigation, TestRun, TestRun.investigation_id),
            "conditions": (TestRun, TestCondition, TestCondition.test_run_id),
            "measurements": (TestRun, Measurement, Measurement.test_run_id),
            "sources": (Investigation, SourceDocument, SourceDocument.investigation_id),
        }
        parent, model, field = mapping[kind]
        await self.require(parent, identity)
        rows, total = await self.repo.children(model, field, identity, query)
        if kind == "runs":
            items = await self.run_views(rows)
        else:
            items = [
                self.measurement(r) if kind == "measurements" else self.source(r) for r in rows
            ]
        parent_path = "runs" if parent is TestRun else "investigations"
        return self.page(
            items, total, query.offset, query.limit, f"/{parent_path}/{identity}/{kind}"
        )

    async def observations(self, identity, query):
        await self.require(Investigation, identity)
        rows, total, runs = await self.repo.observations(identity, query)
        views = dict(zip(runs, await self.run_views(list(runs.values())), strict=True))
        return self.page(
            [
                {
                    "measurement": self.measurement(r),
                    "run": views[r.test_run_id],
                    "context": self.context,
                }
                for r in rows
            ],
            total,
            query.offset,
            query.limit,
            f"/investigations/{identity}/measurements",
        )

    def capabilities(self):
        return {
            "supportedFilters": [
                "q",
                "platform",
                "material",
                "gravityRaw",
                "tag",
                "purpose",
                "sourceType",
                "evidenceStatus",
                "reviewStatus",
            ],
            "supportedSorts": ["title-asc", "runs-desc"],
            "unsupportedFilters": ["fuel", "facility", "gravity", "category"],
            "unsupportedSorts": ["newest", "code-asc", "confidence"],
            "unavailableDisplayFields": RICH_FIELDS,
            "maxPageSize": 100,
            "context": self.context,
        }
