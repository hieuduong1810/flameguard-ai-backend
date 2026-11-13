import asyncio
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.integrations.chat import MockProvider, RagRequest, UnavailableProvider, bounded
from app.schemas.api.chat import Answer, Citation
from app.services.chat import validate_citations


async def test_provider_defaults_and_empty_mock():
    request = RagRequest(
        question="x", corpus_version="v1", collection_fingerprint="hash", allowed_sources=()
    )
    assert (await UnavailableProvider().answer(request)).state == "unavailable"
    result = await MockProvider().answer(request)
    assert result.state == "abstained" and result.origin == "synthetic"
    assert result.review_status == "unreviewed"


async def test_provider_bounds_and_cancellation():
    async def too_large():
        return Answer(state="abstained", text="x" * 16001)

    with pytest.raises(ValueError):
        await bounded(too_large(), 1)

    async def cancelled():
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await bounded(cancelled(), 1)


def test_exact_citation_and_synthetic_review():
    source = Citation(
        source_document_id=uuid4(),
        source_locator="page 3",
        source_excerpt="Original synthetic excerpt",
    )
    good = Answer(
        state="answered",
        text="TEST_ONLY",
        origin="synthetic",
        review_status="unreviewed",
        citations=(source, source),
    )
    validate_citations(good, (source,), True)
    for changed in (
        good.model_copy(update={"review_status": "unknown"}),
        good.model_copy(update={"origin": "real"}),
        good.model_copy(update={"state": "abstained"}),
        good.model_copy(
            update={"citations": (source.model_copy(update={"source_excerpt": "invented"}),)}
        ),
        good.model_copy(update={"citations": ()}),
    ):
        with pytest.raises(HTTPException):
            validate_citations(changed, (source,), True)


@pytest.mark.parametrize(
    "state,total,page,expected",
    [
        ("evaluated", 0, None, {"NO_EVIDENCE", "PROVIDER_ABSTAINED"}),
        (
            "evaluated",
            2,
            True,
            {"PARTIAL_OR_PAGED_EVIDENCE", "UNREVIEWED_EVIDENCE", "PROVIDER_ABSTAINED"},
        ),
        (
            "unavailable",
            None,
            None,
            {"CLASSIFICATION_UNAVAILABLE", "EVIDENCE_NOT_EXAMINED", "PROVIDER_ABSTAINED"},
        ),
    ],
)
def test_advisor_gap_semantics(state, total, page, expected):
    from types import SimpleNamespace as Item

    from app.services.advisor import evidence_gaps

    group = (
        None
        if total is None
        else Item(total=total, items=(), reason_codes=(), context=Item(review_state="unreviewed"))
    )
    section = Item(
        state=state,
        reason_codes=("CLASSIFICATION_UNAVAILABLE",) if total is None else (),
        page=Item(offset=1, next_request=None, continuation_limited=False) if page else None,
    )
    answer = Answer(state="abstained", text="")
    reasons = set(evidence_gaps(section, group, answer))
    assert expected <= reasons
    if total:
        assert "NO_EVIDENCE" not in reasons
