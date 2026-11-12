from sqlalchemy import func, select

from app.models import EvidenceClaim, Investigation, SourceDocument, TestRun
from app.repositories.phase4_catalog import investigation_selection
from app.repositories.phase4_evidence import claim_ids


async def summary_counts(session, query):
    ids = investigation_selection(query).cte("selected_investigations")
    selected = select(ids.c.id)
    counts = {}
    for label, model, predicate in [
        ("investigationCount", Investigation, Investigation.id.in_(selected)),
        ("runCount", TestRun, TestRun.investigation_id.in_(selected)),
        ("sourceCount", SourceDocument, SourceDocument.investigation_id.in_(selected)),
        ("claimCount", EvidenceClaim, EvidenceClaim.id.in_(claim_ids(selected))),
    ]:
        counts[label] = await session.scalar(
            select(func.count()).select_from(model).where(predicate)
        )
    counts["withSources"] = await session.scalar(
        select(func.count(func.distinct(SourceDocument.investigation_id))).where(
            SourceDocument.investigation_id.in_(selected)
        )
    )
    return counts
