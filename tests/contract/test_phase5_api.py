import asyncio
import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app.api.dependencies import get_scenarios
from app.integrations.scenario_evidence import execution
from app.integrations.scenario_evidence.classifications import FixedClassification
from app.integrations.scenario_evidence.config import ScenarioProviders
from app.integrations.scenario_evidence.mocks import fixture_providers
from app.integrations.scenario_evidence.rankings import FixedRanking
from app.integrations.scenario_evidence.run_policy import ExactFixturePolicy
from app.schemas.api.scenarios import DIMS, MAX_OFFSET, EvaluationRequest, EvidenceContext
from app.services.errors import Phase4Error
from app.services.scenario_traversal import check_snapshot, page_for
from app.services.scenarios import ScenarioService, Snapshot
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

PATH = "/api/v1/mission/scenarios/evaluate"
BODY = {"scenario": SCENARIO, "pages": {"limit": 1}}
ROOT = Path(__file__).resolve().parents[2]
SECRET = "postgresql://private-credential/private/path"


@pytest.fixture
def mock_snapshot(application, settings):
    service = ScenarioService(None, settings, ScenarioProviders())
    config = {
        "providers": fixture_providers(),
        "runs": (run_evidence(RUN, CONDITIONS[:3]), run_evidence(OTHER_RUN, CONDITIONS[3:])),
        "context": EvidenceContext(
            collection_id=provider_request().scope.collection_id,
            origin="synthetic",
            review_state="unreviewed",
            caveats=("TEST_ONLY engineering evidence",),
        ),
        "updates": {},
    }

    async def snapshot(request, digest):
        providers = config["providers"].for_context(config["context"])
        scope = provider_request().scope.model_copy(
            update={
                "scenario_digest": digest,
                "pillar": request.pillar,
                "rule_version": providers.run_policy.version if providers.run_policy else None,
                "mapping_version": providers.run_policy.mapping_version
                if providers.run_policy
                else None,
                "classification_version": (
                    providers.classifications.version if providers.classifications else None
                ),
                **config["updates"],
            }
        )
        check_snapshot(request, scope)
        runs = config["runs"]
        offset, limit = request.pages.run_offset, request.pages.limit
        return Snapshot(
            config["context"],
            scope,
            providers,
            len(runs),
            runs[offset : offset + limit],
            IDENTITIES,
            original_associations(),
        )

    service.snapshot = AsyncMock(side_effect=snapshot)
    application.dependency_overrides[get_scenarios] = lambda: service
    return config, service


@pytest.mark.parametrize(
    "body",
    [
        {"scenario": {}, "provider": "TEST_ONLY"},
        {"scenario": {"environment_label": "custom"}},
        {"scenario": {"gravity": {"value": 0.0, "unit": "g"}}},
        {"scenario": {"gravity": {"value": "NaN", "unit": "g"}}},
        {"scenario": {"oxygen": {"value": "12", "unit": "%"}}},
        {"scenario": {}, "pages": {"limit": 101}},
        {"scenario": {}, "pages": {"limit": True}},
        {"scenario": {}, "pages": {"runOffset": "1"}},
        {"scenario": {}, "pages": {"evidenceOffset": 1_000_001}},
        {"scenario": {}, "expectedBindings": {"collectionId": SECRET}},
    ],
)
async def test_invalid_json_fields_never_reach_snapshot(client, mock_snapshot, body):
    response = await client.post(PATH, json=body)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"
    assert SECRET not in response.text
    mock_snapshot[1].snapshot.assert_not_awaited()


async def test_malformed_duplicate_oversized_and_query_request_boundaries(client, mock_snapshot):
    for content in (
        '{"scenario":',
        '{"scenario":{},"scenario":{}}',
        '{"scenario":{"name":NaN}}',
        " " * 33_000,
    ):
        response = await client.post(
            PATH, content=content, headers={"content-type": "application/json"}
        )
        assert response.status_code == 422
    assert (await client.post(PATH + "?provider=bad", json=BODY)).status_code == 422
    assert (await client.post(PATH, content="{}")).status_code == 422
    mock_snapshot[1].snapshot.assert_not_awaited()


async def test_default_absent_collection_and_independent_provider_defaults(client, mock_snapshot):
    override = mock_snapshot[1]
    config = mock_snapshot[0]
    config["providers"] = ScenarioProviders()
    response = await client.post(PATH, json=BODY)
    result = response.json()
    assert response.status_code == 200
    assert result["scenario"]["original"]["gravity"] == {"value": "0.00", "unit": "g"}
    assert result["scenario"]["fieldStates"]["presetKey"] == "omitted"
    assert [x["dimension"] for x in result["coverage"]["dimensions"]] == list(DIMS)
    assert result["coverage"]["items"] is None
    assert result["rankings"]["reasonCodes"] == ["RANKING_PROVIDER_UNAVAILABLE"]
    assert result["pillarEvidence"]["reasonCodes"] == ["CLASSIFICATION_UNAVAILABLE"]
    override.snapshot.assert_awaited_once()


async def test_real_origin_retains_unreviewed_and_cannot_activate_mock_sections(
    client, mock_snapshot
):
    config = mock_snapshot[0]
    config["context"] = config["context"].model_copy(update={"origin": "real"})
    result = (await client.post(PATH, json=BODY)).json()
    assert result["context"]["origin"] == "real"
    assert result["context"]["reviewState"] == "unreviewed"
    assert result["coverage"]["reasonCodes"] == ["SCIENTIFIC_REVIEW_NOT_ACCEPTED"]
    assert result["coverage"]["items"] is None
    assert result["rankings"]["items"] is None
    assert result["pillarEvidence"]["groups"] is None


async def test_collection_not_configured_returns_sanitized_503(client):
    response = await client.post(PATH, json=BODY)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "COLLECTION_SCOPE_INVALID"


@pytest.mark.parametrize(
    ("failure", "status", "code"),
    [
        (OSError(SECRET), 503, "DATA_UNAVAILABLE"),
        (Phase4Error("COLLECTION_SCOPE_INVALID"), 503, "COLLECTION_SCOPE_INVALID"),
        (ValueError(SECRET), 500, "INTERNAL_ERROR"),
    ],
)
async def test_read_boundary_does_not_leak_exception(client, mock_snapshot, failure, status, code):
    mock_snapshot[1].snapshot.side_effect = failure
    response = await client.post(PATH, json=BODY)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert SECRET not in response.text


async def test_coverage_summary_does_not_union_split_runs_and_retains_originals(
    client, mock_snapshot
):
    response = await client.post(PATH, json={"scenario": SCENARIO})
    assert response.status_code == 200
    coverage = response.json()["coverage"]
    assert coverage["collectionTraversalComplete"]
    assert coverage["examinedRuns"] == 2
    assert coverage["dimensions"][-1]["status"] == "partial"
    assert coverage["collectionConclusion"] is None
    for run in coverage["items"]:
        assert [dim["dimension"] for dim in run["dimensions"]] == list(DIMS)
        assert run["dimensions"][-1]["status"] == "partial"
        assert run["context"]["origin"] == "synthetic"
    assert coverage["items"][0]["conditions"][0]["valueNumeric"] == "0.00"
    assert coverage["items"][0]["conditions"][0]["uncertainty"] is None
    assert coverage["items"][0]["conditions"][0]["sourceLocator"] is None


async def test_replay_is_deterministic_and_final_page_is_scoped(client, mock_snapshot):
    async def traverse():
        request = BODY
        pages = []
        while request:
            response = await client.post(PATH, json=request)
            assert response.status_code == 200
            coverage = response.json()["coverage"]
            pages.append(coverage)
            next_request = coverage["page"]["nextRequest"]
            request = {"scenario": SCENARIO, **next_request} if next_request else None
        return pages

    first = await traverse()
    assert first == await traverse()
    assert [item["items"][0]["run"]["runId"] for item in first] == [str(RUN), str(OTHER_RUN)]
    next_request = first[0]["page"]["nextRequest"]
    direct = (await client.post(PATH, json={"scenario": SCENARIO, **next_request})).json()
    assert not direct["coverage"]["collectionTraversalComplete"]
    assert direct["coverage"]["collectionConclusion"] is None
    assert direct["coverage"]["summaryScope"] == "examined_page"


@pytest.mark.parametrize(
    "field",
    [
        "scenario_digest",
        "pillar",
        "collection_fingerprint",
        "dataset_version",
        "mapping_version",
        "rule_version",
        "identity_version",
    ],
)
async def test_snapshot_drift_is_rejected(client, mock_snapshot, field):
    first = (await client.post(PATH, json=BODY)).json()
    next_request = first["coverage"]["page"]["nextRequest"]
    config = mock_snapshot[0]
    config["updates"][field] = (
        "0" * 64 if field.endswith(("digest", "fingerprint")) else "different"
    )
    response = await client.post(PATH, json={"scenario": SCENARIO, **next_request})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "VERSION_CONFLICT"


async def test_empty_and_capped_pages_are_distinguishable(client, mock_snapshot):
    config = mock_snapshot[0]
    config["runs"] = ()
    coverage = (await client.post(PATH, json=BODY)).json()["coverage"]
    assert coverage["items"] == []
    assert coverage["collectionTraversalComplete"]
    assert coverage["collectionConclusion"] is None
    config["runs"] = (run_evidence(complete=False),)
    coverage = (await client.post(PATH, json=BODY)).json()["coverage"]
    assert coverage["reasonCodes"] == ["CONDITION_LIMIT_EXCEEDED"]
    assert not coverage["requiredConditionsComplete"]
    assert not coverage["collectionTraversalComplete"]


async def test_missing_replay_bindings_fail_before_snapshot(client, mock_snapshot):
    response = await client.post(PATH, json=BODY | {"pages": {"runOffset": 1}})
    assert response.status_code == 409
    mock_snapshot[1].snapshot.assert_not_awaited()


async def test_ranking_scope_and_payload_replay_binding(client, mock_snapshot):
    first = (await client.post(PATH, json=BODY)).json()
    ranking = first["rankings"]
    assert ranking["items"][0]["catalogUsefulnessScore"] == "3.00"
    next_request = ranking["page"]["nextRequest"]
    request = {"scenario": SCENARIO, **next_request}
    second = (await client.post(PATH, json=request)).json()
    assert second["rankings"]["items"][0]["rank"] == 1
    assert second["rankings"]["items"][0]["catalogUsefulnessScore"] is None

    class ChangedRanking(FixedRanking):
        async def rank(self, request):
            payload = await super().rank(request)
            if payload is None:
                return None
            delivery = json.loads(payload)
            delivery["entries"][1]["conditionComponent"] = "0.80"
            return json.dumps(delivery).encode()

    config = mock_snapshot[0]
    config["providers"] = replace(config["providers"], rankings=ChangedRanking())
    assert (await client.post(PATH, json=request)).status_code == 409
    response = await client.post(PATH, json=BODY | {"pillar": "suppression"})
    assert response.json()["rankings"]["reasonCodes"] == ["OUT_OF_SCOPE"]


async def test_pillar_traversal_preserves_every_association_and_empty_groups(client, mock_snapshot):
    collected = []
    request = BODY
    for _ in original_associations():
        evidence = (await client.post(PATH, json=request)).json()["pillarEvidence"]
        groups = evidence["groups"]
        assert [group["pillar"] for group in groups] == ["prevention", "detection", "suppression"]
        assert groups[1]["items"] == groups[2]["items"] == []
        assert groups[1]["reasonCodes"] == ["NO_CLASSIFIED_ASSOCIATIONS_IN_SCOPE"]
        collected.extend(groups[0]["items"])
        replay = evidence["page"]["nextRequest"]
        request = {"scenario": SCENARIO, **replay} if replay else None
    assert request is None
    assert [x["associationId"] for x in collected] == [
        str(row.association_id) for row in original_associations()
    ]
    assert len({item["document"]["sourceDocumentId"] for item in collected}) == 3
    assert any(item["testRunId"] is None for item in collected)
    assert any("SOURCE_RUN_CONTEXT_MISMATCH" in item["reasonCodes"] for item in collected)
    for item in collected:
        assert item["context"]["providerVersion"].startswith("TEST_ONLY")
        assert item["document"]["doi"] is None
        assert item["claim"]["context"]["reviewState"] == "unreviewed"


async def test_section_replay_checks_only_its_provider_and_classification_content(
    client,
    mock_snapshot,
):
    result = (await client.post(PATH, json=BODY)).json()
    ranking = {"scenario": SCENARIO, **result["rankings"]["page"]["nextRequest"]}
    evidence = {"scenario": SCENARIO, **result["pillarEvidence"]["page"]["nextRequest"]}
    coverage = {"scenario": SCENARIO, **result["coverage"]["page"]["nextRequest"]}

    config = mock_snapshot[0]
    providers = config["providers"]
    config["providers"] = replace(providers, run_policy=None, classifications=None)
    independent_ranking = await client.post(PATH, json=ranking)
    assert independent_ranking.status_code == 200
    assert independent_ranking.json()["rankings"]["items"][0]["position"] == 2

    class ChangedClassification(FixedClassification):
        async def classify(self, request, associations):
            data = json.loads(await super().classify(request, associations))
            for reference in data["references"]:
                reference["pillar"] = "detection"
            return json.dumps(data).encode()

    config["providers"] = replace(providers, classifications=ChangedClassification(), rankings=None)
    assert (await client.post(PATH, json=evidence)).status_code == 409
    independent_coverage = await client.post(PATH, json=coverage)
    assert independent_coverage.status_code == 200
    assert independent_coverage.json()["coverage"]["items"][0]["run"]["runId"] == str(OTHER_RUN)


def test_offset_ceiling_discloses_remaining_rows():
    request = EvaluationRequest.model_validate(
        {"scenario": SCENARIO, "pages": {"runOffset": MAX_OFFSET}}
    )
    page = page_for(request, provider_request().scope, "run_offset", MAX_OFFSET + 21)
    assert page.continuation_limited
    assert page.next_request is None


@pytest.mark.parametrize("mode", ["timeout", "exception", "malformed", "oversize", "private"])
async def test_ranking_failure_does_not_erase_other_sections(
    client, mock_snapshot, monkeypatch, mode
):
    monkeypatch.setattr(execution, "PROVIDER_DEADLINE", 0.02)

    class BrokenRanking(FixedRanking):
        async def rank(self, request):
            if mode == "timeout":
                await asyncio.Event().wait()
            if mode == "exception":
                raise RuntimeError(SECRET)
            if mode == "oversize":
                return b" " * (execution.MAX_BYTES + 1)
            if mode == "private":
                payload = json.loads(await super().rank(request))
                payload["entries"][1]["rationale"] = SECRET
                return json.dumps(payload).encode()
            return b"{bad JSON"

    config = mock_snapshot[0]
    config["providers"] = replace(config["providers"], rankings=BrokenRanking())
    response = await client.post(PATH, json=BODY)
    result = response.json()
    assert response.status_code == 200
    assert result["coverage"]["state"] == result["pillarEvidence"]["state"] == "evaluated"
    assert result["rankings"]["state"] == (
        "unavailable" if mode in {"exception", "timeout"} else "rejected"
    )
    assert result["rankings"]["items"] is None
    assert SECRET not in response.text


async def test_independent_rule_and_classification_failures(client, mock_snapshot):
    class BrokenRule(ExactFixturePolicy):
        async def evaluate(self, request, runs):
            return ()

    class BrokenClassification(FixedClassification):
        async def classify(self, request, associations):
            raise RuntimeError(SECRET)

    config = mock_snapshot[0]
    config["providers"] = replace(
        config["providers"],
        run_policy=BrokenRule(),
        classifications=BrokenClassification(),
    )
    response = await client.post(PATH, json=BODY)
    result = response.json()
    assert response.status_code == 200
    assert result["coverage"]["state"] == "rejected"
    assert result["pillarEvidence"]["state"] == "unavailable"
    assert result["rankings"]["state"] == "evaluated"
    assert all(dim["status"] == "unavailable" for dim in result["coverage"]["dimensions"])
    assert SECRET not in response.text


def test_runtime_openapi_is_additive_and_matches_snapshot(application):
    actual = application.openapi()
    snapshot = json.loads((ROOT / "specs/phase5-backend/contracts/openapi.json").read_text())
    assert actual["paths"][PATH] == snapshot["paths"][PATH]
    assert set(actual["paths"][PATH]) == {"post"}
    operation = actual["paths"][PATH]["post"]
    assert operation["operationId"] == "evaluateMissionScenario"
    assert set(operation["responses"]) == {"200", "409", "422", "500", "503"}
    assert all("scenario" not in path for path in actual["paths"] if path != PATH)
    schemas = actual["components"]["schemas"]
    for name, schema in snapshot["components"]["schemas"].items():
        assert schemas[name] == schema
    assert schemas["EvaluationRequest"]["required"] == ["scenario"]
    assert schemas["RunEvaluation"]["properties"]["dimensions"]["minItems"] == 6
    assert schemas["EvaluationRequest"]["examples"][0]["scenario"]["name"].startswith("TEST_ONLY")
