import asyncio
import json
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.integrations.scenario_evidence.classifications import (
    FixedClassification,
    validate_classification,
)
from app.integrations.scenario_evidence.config import ScenarioProviders
from app.integrations.scenario_evidence.execution import MAX_BYTES, ProviderFailure, execute
from app.integrations.scenario_evidence.rankings import FixedRanking, validate_ranking
from app.integrations.scenario_evidence.run_policy import (
    ExactFixturePolicy,
    exact_decisions,
    validate_decisions,
)
from app.schemas.api.scenarios import DIMS, EvidenceContext
from app.services.scenario_pillars import project
from tests.fixtures.phase5 import (
    CONDITIONS,
    IDENTITIES,
    OTHER_RUN,
    RUN,
    SCENARIO,
    original_associations,
    provider_request,
    run_evidence,
)


def test_detached_records_are_immutable_and_mock_origins_are_gated():
    request = provider_request()
    with pytest.raises(FrozenInstanceError):
        request.scenario = None
    with pytest.raises(ValidationError):
        request.scenario.name = "different"
    with pytest.raises(ValidationError):
        run_evidence().conditions[0].unit = "wrong"
    providers = ScenarioProviders(run_policy=ExactFixturePolicy())
    for origin, review in [
        ("real", "unreviewed"),
        ("unknown", "unknown"),
        ("synthetic", "unknown"),
    ]:
        context = EvidenceContext(
            collection_id="fixture",
            origin=origin,
            review_state=review,
            caveats=(),
        )
        assert providers.for_context(context) == ScenarioProviders()


async def test_six_dimensions_and_same_run_invariant():
    request = provider_request()
    complete = run_evidence()
    first = run_evidence(UUID(int=103), CONDITIONS[:3])
    second = run_evidence(OTHER_RUN, CONDITIONS[3:])
    runs = (complete, first, second)
    decisions = await ExactFixturePolicy().evaluate(request, runs)
    assert validate_decisions(request, runs, decisions) == decisions
    assert tuple(item.dimension for item in decisions[0]) == DIMS
    assert all(item.run_id == RUN for item in decisions[0])
    assert decisions[0][-1].status == "support"
    assert decisions[0][-1].condition_ids == tuple(x.condition_id for x in complete.conditions)
    assert all(item[-1].status == "partial" for item in decisions[1:])
    for invalid in (
        (decisions[0][:-1],),
        (decisions[0][:-1] + (decisions[0][0],),),
        (decisions[0] + (decisions[0][0],),),
        (decisions[0][:-1] + (decisions[0][-1].model_copy(update={"run_id": OTHER_RUN}),),),
        (
            decisions[0][:-1]
            + (decisions[0][-1].model_copy(update={"condition_ids": (UUID(int=1000),)}),),
        ),
    ):
        with pytest.raises(ProviderFailure, match="INVALID_PROVIDER_DELIVERY"):
            validate_decisions(request, (complete,), invalid)


@pytest.mark.parametrize(
    ("modify", "reason"),
    [
        ({"unit": "m/s"}, "CONDITION_UNIT_UNSUPPORTED"),
        ({"data_status": "SYNTHETIC_UNREVIEWED"}, "CONDITION_STATUS_UNSUPPORTED"),
        ({"data_status": "FLAGGED"}, "CONDITION_STATUS_UNSUPPORTED"),
        ({"value_numeric": None}, "CONDITION_VALUE_MISSING"),
        ({"value_text": "also supplied"}, "CONDITION_VALUE_UNSUPPORTED"),
    ],
)
def test_unusable_original_conditions_cannot_support_combination(modify, reason):
    run = run_evidence()
    rows = (*run.conditions[:-1], run.conditions[-1].model_copy(update=modify))
    result = exact_decisions(replace(run, conditions=rows), provider_request().scenario)
    assert result[4].reason_codes == (reason,)
    assert result[4].status == "unknown"
    assert result[-1].status == "partial"


def test_conflict_cap_inverse_flame_and_e_field_remain_explicit():
    run = run_evidence()
    scenario = provider_request().scenario
    conflicting = run.conditions[-1].model_copy(
        update={"condition_id": UUID(int=222), "value_numeric": Decimal("0.01")}
    )
    result = exact_decisions(replace(run, conditions=(*run.conditions, conflicting)), scenario)
    assert result[4].reason_codes == ("CONTRADICTORY_CONDITIONS",)
    assert result[-1].status == "partial"
    capped = exact_decisions(replace(run, complete=False), scenario)
    assert all(item.status == "unknown" for item in capped)
    incompatible = run_evidence(
        conditions=(
            ("TEST_ONLY_E_FIELD", Decimal("0"), None, "V/m"),
            ("TEST_ONLY_OXIDIZER_OXYGEN", Decimal("21"), None, "%"),
        )
    )
    original = exact_decisions(incompatible, scenario)
    assert original[0].reason_codes == ("CONDITION_MISSING",)
    assert original[2].reason_codes == ("OXYGEN_MEANING_UNSUPPORTED",)
    assert original[-1].status == "unknown"


async def test_fixed_ranking_preserves_order_ties_meanings_and_nulls():
    request = provider_request()
    payload = await FixedRanking().rank(request)
    delivery, entries = validate_ranking(payload, request, IDENTITIES)
    assert delivery.complete
    assert tuple(row.investigation for row in entries) == IDENTITIES
    assert [row.rank for row in entries] == [1, 1]
    assert [row.scenario_relevance_score for row in entries] == ["70.00", "70.00"]
    assert [row.catalog_usefulness_score for row in entries] == ["3.00", None]
    assert entries[0].components[1].value is None
    assert entries[1].components[1].value == "0"
    assert all(entry.context.review_state == "unreviewed" for entry in entries)
    assert await FixedRanking().rank(provider_request(pillar="detection")) is None
    assert (
        await FixedRanking().rank(provider_request(SCENARIO | {"material": {"key": "spacesuit"}}))
        is None
    )


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("investigationId", str(UUID(int=0))),
        ("psiId", "wrong"),
        ("slug", None),
        ("externalExperimentId", "unknown"),
        ("position", 1),
        ("scenarioRelevanceScore", "100.01"),
        ("scenarioRelevanceScore", "NaN"),
        ("catalogUsefulnessScore", "5.1"),
        ("contextComponent", "1.1"),
        ("conditionComponent", None),
        ("rationale", "postgresql://secret/private/path"),
    ],
)
async def test_invalid_ranking_entry_rejects_complete_delivery(key, value):
    request = provider_request()
    delivery = json.loads(await FixedRanking().rank(request))
    delivery["entries"][1][key] = value
    with pytest.raises(ProviderFailure, match="INVALID_PROVIDER_DELIVERY"):
        validate_ranking(json.dumps(delivery).encode(), request, IDENTITIES)


@pytest.mark.parametrize(
    "field",
    [
        "scenarioDigest",
        "datasetVersion",
        "identityVersion",
        "mappingVersion",
        "collectionFingerprint",
        "pillar",
    ],
)
async def test_stale_ranking_scope_rejected(field):
    request = provider_request()
    delivery = json.loads(await FixedRanking().rank(request))
    delivery[field] = "0" * 64 if field.endswith(("Digest", "Fingerprint")) else "prevention"
    with pytest.raises(ProviderFailure, match="PROVIDER_VERSION_CONFLICT"):
        validate_ranking(json.dumps(delivery).encode(), request, IDENTITIES)


async def test_canonical_duplicate_and_incomplete_ranking_rejected():
    request = provider_request()
    original = json.loads(await FixedRanking().rank(request))
    for entries in (
        original["entries"][:1],
        [
            original["entries"][0],
            original["entries"][0]
            | {
                "position": 2,
                "investigationId": "{" + original["entries"][0]["investigationId"].upper() + "}",
            },
        ],
    ):
        with pytest.raises(ProviderFailure, match="INVALID_PROVIDER_DELIVERY"):
            validate_ranking(
                json.dumps(original | {"entries": entries}).encode(), request, IDENTITIES
            )


@pytest.mark.parametrize(
    "payload",
    [
        b"not JSON",
        b'{"version":1,"version":2}',
        b'{"data":NaN}',
        b"[" * 14 + b"0" + b"]" * 14,
        b" " * (MAX_BYTES + 1),
        b"\xff",
    ],
)
def test_untrusted_transport_limits(payload):
    with pytest.raises(ProviderFailure, match="INVALID_PROVIDER_DELIVERY"):
        validate_ranking(payload, provider_request(), IDENTITIES)


async def test_provider_timeout_cancellation_and_failure_do_not_retry_or_leak():
    calls = 0
    entered = asyncio.Event()

    async def wait():
        nonlocal calls
        calls += 1
        entered.set()
        await asyncio.Event().wait()

    with pytest.raises(ProviderFailure, match="PROVIDER_TIMEOUT"):
        await execute(wait(), deadline=0.01)
    assert calls == 1
    task = asyncio.create_task(execute(wait()))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert calls == 2

    async def fail():
        raise RuntimeError("postgresql://secret/private")

    with pytest.raises(ProviderFailure, match="^PROVIDER_UNAVAILABLE$"):
        await execute(fail())


def test_foreign_duplicate_and_nonfinite_conditions_are_defensive():
    run = run_evidence()
    request = provider_request()
    foreign = run.conditions[-1].model_copy(update={"run_id": OTHER_RUN})
    duplicate = run.conditions[-1].model_copy(
        update={"condition_id": run.conditions[0].condition_id}
    )
    for row in (foreign, duplicate):
        invalid = replace(run, conditions=(*run.conditions[:-1], row))
        decisions = (exact_decisions(invalid, request.scenario),)
        with pytest.raises(ProviderFailure, match="INVALID_PROVIDER_DELIVERY"):
            validate_decisions(request, (invalid,), decisions)
    original = run.conditions[-1].model_copy(update={"value_numeric": Decimal("sNaN")})
    decisions = exact_decisions(
        replace(run, conditions=(*run.conditions[:-1], original)), request.scenario
    )
    assert decisions[4].reason_codes == ("CONDITION_VALUE_UNSUPPORTED",)
    unsupported = provider_request(SCENARIO | {"material": {"key": "spacesuit"}})
    assert exact_decisions(run, unsupported.scenario)[1].reason_codes == (
        "SCENARIO_MATERIAL_UNSUPPORTED",
    )


async def test_complete_must_be_boolean_and_ranking_entry_cap_is_checked():
    request = provider_request()
    original = json.loads(await FixedRanking().rank(request))
    for change in ({"complete": 1}, {"entries": original["entries"] * 501}):
        with pytest.raises(ProviderFailure, match="INVALID_PROVIDER_DELIVERY"):
            validate_ranking(json.dumps(original | change).encode(), request, IDENTITIES)


async def test_explicit_classification_validates_full_original_mapping():
    request = provider_request()
    rows = original_associations()
    payload = await FixedClassification().classify(request, rows)
    result = validate_classification(payload, request, rows)
    assert result == dict.fromkeys((row.association_id for row in rows), "prevention")
    for key, value in (
        ("locator", "unknown"),
        ("documentId", str(UUID(int=1))),
        ("claimId", str(UUID(int=2))),
    ):
        modified = json.loads(payload)
        modified["references"][0][key] = value
        with pytest.raises(ProviderFailure, match="SOURCE_MAPPING_UNRESOLVED"):
            validate_classification(json.dumps(modified).encode(), request, rows)
    with pytest.raises(ProviderFailure, match="SOURCE_MAPPING_UNRESOLVED"):
        validate_classification(payload, request, ())
    with pytest.raises(ProviderFailure, match="SOURCE_MAPPING_UNRESOLVED"):
        validate_classification(
            payload, request, (*rows, replace(rows[0], association_id=UUID(int=3)))
        )


def test_pillar_projection_preserves_optional_doi_and_mismatch():
    from app.schemas.api.scenarios import FixtureLabel

    row = next(
        item
        for item in original_associations()
        if item.run_investigation_id not in {None, item.investigation_id}
    )
    original = replace(row, doi="TEST_ONLY opaque original DOI field")
    item = project(
        original,
        "prevention",
        FixtureLabel(
            collection_id="TEST_ONLY",
            dataset_version="TEST_ONLY",
            provider_version="TEST_ONLY",
        ),
    )
    assert item.document.doi == original.doi
    assert item.source_locator == row.source_locator
    assert item.claim.review_status == row.review_status
    assert item.reason_codes == ("TEST_ONLY_UNREVIEWED", "SOURCE_RUN_CONTEXT_MISMATCH")
