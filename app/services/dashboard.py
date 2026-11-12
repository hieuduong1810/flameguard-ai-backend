from decimal import Decimal, localcontext

from app.repositories.dashboard import summary_counts
from app.schemas.api.queries import CatalogQuery
from app.services.catalog import CatalogService


class DashboardService(CatalogService):
    async def summary(self, query):
        counts = await summary_counts(self.session, query)
        numerator, denominator = counts.pop("withSources"), counts["investigationCount"]
        with localcontext() as ctx:
            ctx.prec = 28
            ratio = format(Decimal(numerator) / denominator, "f") if denominator else None
        featured = await self.investigations(CatalogQuery(**query.model_dump(), limit=3))
        unavailable = {
            field: "UNSUPPORTED_MAPPING"
            for field in ["fuelDistribution", "facilityDistribution", "gravityDistribution"]
        }
        unavailable["verifiedRunCount"] = "VERIFICATION_NOT_ESTABLISHED"
        if not denominator:
            unavailable["sourceCoverage"] = "NO_DENOMINATOR"
        return {
            **counts,
            "selection": query.model_dump(by_alias=True, exclude_none=True),
            "verifiedRunCount": None,
            "sourceCoverage": {"numerator": numerator, "denominator": denominator, "ratio": ratio},
            "fuelDistribution": None,
            "facilityDistribution": None,
            "gravityDistribution": None,
            "featuredInvestigations": featured["items"],
            "unavailableFields": unavailable,
            "context": self.context,
        }
