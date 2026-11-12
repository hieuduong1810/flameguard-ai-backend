import asyncio
import json
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy import event, func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.dependencies import get_scenarios
from app.integrations.scenario_evidence.mocks import fixture_providers
from app.integrations.scenario_evidence.rankings import FixedRanking
from app.models import Scenario
from app.repositories import phase5_scenarios
from app.schemas.api.scenarios import ScenarioInput
from app.services.scenario_persistence import ScenarioStorageError, deserialize, persist_scenario
from app.services.scenarios import ScenarioService
from app.services.unit_of_work import read_unit_of_work
from tests.fixtures.phase5 import (
    INVESTIGATION,
    OTHER_INVESTIGATION,
    SCENARIO,
    original_associations,
)
from tests.integration.phase5_fixtures import (
    COMPLETE_RUN,
    OXYGEN_RUN,
    PRESSURE_RUN,
)

pytestmark = pytest.mark.integration
PATH = "/api/v1/mission/scenarios/evaluate"
BODY = {"scenario": SCENARIO, "pages": {"limit": 1}}


async def test_postgres_full_same_run_and_split_evidence_http(phase5_api):
    client, _ = phase5_api
    response = await client.post(PATH, json={"scenario": SCENARIO})
    assert response.status_code == 200, response.text
    result = response.json()
    coverage = result["coverage"]
    assert coverage["state"] == "evaluated"
    assert coverage["page"]["total"] == 4
    assert coverage["collectionTraversalComplete"]
    runs = {UUID(item["run"]["runId"]): item for item in coverage["items"]}
    assert list(runs) == sorted(runs)
    complete = runs[COMPLETE_RUN]
    combined = complete["dimensions"][-1]
    assert combined["status"] == "support"
    assert combined["runId"] == str(COMPLETE_RUN)
    assert set(combined["conditionIds"]) <= {row["conditionId"] for row in complete["conditions"]}
    assert any(row["valueNumeric"] == "0.00" for row in complete["conditions"])
    assert any(row["valueNumeric"] is None for row in complete["conditions"])
    assert all(row["uncertainty"] is None for row in complete["conditions"])
    assert runs[OXYGEN_RUN]["dimensions"][-1]["status"] == "partial"
    assert runs[PRESSURE_RUN]["dimensions"][-1]["status"] == "partial"
    assert complete["run"]["externalRunKey"] == runs[PRESSURE_RUN]["run"]["externalRunKey"]
    assert complete["run"]["investigation"] != runs[PRESSURE_RUN]["run"]["investigation"]
    assert result["rankings"]["state"] == result["pillarEvidence"]["state"] == "evaluated"


async def test_postgres_traverses_every_run_twice_and_does_not_claim_final_page_scope(phase5_api):
    client, _ = phase5_api

    async def walk():
        body = BODY
        run_ids = []
        while body:
            response = await client.post(PATH, json=body)
            assert response.status_code == 200
            coverage = response.json()["coverage"]
            assert not coverage["collectionTraversalComplete"]
            assert coverage["collectionConclusion"] is None
            run_ids.extend(item["run"]["runId"] for item in coverage["items"])
            descriptor = coverage["page"]["nextRequest"]
            body = {"scenario": SCENARIO, **descriptor} if descriptor else None
        return run_ids

    first = await walk()
    assert first == sorted(set(first))
    assert len(first) == 4
    assert first == await walk()


async def test_postgres_ranking_and_pillar_association_continuations(phase5_api):
    client, _ = phase5_api
    first = (await client.post(PATH, json=BODY)).json()
    ranking = first["rankings"]
    item = ranking["items"][0]
    assert item["investigation"]["slug"] == "synthetic-study-1"
    assert item["investigation"]["psiId"] == "SYNTHETIC-PHASE4-1"
    assert item["investigation"]["investigationId"] != item["externalExperimentId"]
    ranking_request = {"scenario": SCENARIO, **ranking["page"]["nextRequest"]}
    second = (await client.post(PATH, json=ranking_request)).json()["rankings"]
    assert second["items"][0]["rank"] == item["rank"] == 1
    assert second["items"][0]["position"] == 2

    evidence = first["pillarEvidence"]
    expected = original_associations()
    for row in expected:
        item = evidence["groups"][0]["items"][0]
        assert item["associationId"] == str(row.association_id)
        assert item["document"]["sourceDocumentId"] == str(row.source_document_id)
        assert item["document"]["sourceUrl"] == row.source_url
        assert item["sourceLocator"] == row.source_locator
        assert item["sourceExcerpt"] == row.source_excerpt
        assert item["testRunId"] == (str(row.test_run_id) if row.test_run_id else None)
        descriptor = evidence["page"]["nextRequest"]
        if descriptor:
            response = await client.post(PATH, json={"scenario": SCENARIO, **descriptor})
            assert response.status_code == 200
            evidence = response.json()["pillarEvidence"]
    assert descriptor is None


async def test_postgres_bounded_queries_and_incomplete_condition_sets(phase5_db, monkeypatch):
    engine = create_async_engine(phase5_db["reader_url"], hide_parameters=True)
    statements = []

    def record(_conn, _cursor, statement, *_):
        statements.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", record)
    monkeypatch.setattr(phase5_scenarios, "CONDITION_LIMIT", 2)
    try:
        async with async_sessionmaker(engine)() as session, read_unit_of_work(session):
            repo = phase5_scenarios.ScenarioEvidenceRepository(session, {})
            await session.execute(text("SELECT 1"))
            statements.clear()
            total, one = await repo.runs(1, 1)
            single_count = len(statements)
            statements.clear()
            _, many = await repo.runs(0, 4)
            assert len(statements) == single_count == 3
            assert total == len(many) == 4 and len(one) == 1
            assert len(one[0].conditions) <= 2
            run = next(row for row in many if row.run.run_id == COMPLETE_RUN)
            assert not run.complete and len(run.conditions) == 2
    finally:
        await engine.dispose()


async def test_postgres_transaction_closes_before_provider_wait_and_cancel(phase5_api, monkeypatch):
    client, app = phase5_api
    database = app.state.database
    provider_entered = asyncio.Event()
    saw_readonly_snapshot = False
    statements = []
    commits = []
    rollbacks = []
    original = phase5_scenarios.ScenarioEvidenceRepository.runs

    async def verify_snapshot(self, offset, limit):
        nonlocal saw_readonly_snapshot
        assert await self.session.scalar(text("SHOW transaction_read_only")) == "on"
        isolation = await self.session.scalar(text("SHOW transaction_isolation"))
        assert isolation == "repeatable read"
        saw_readonly_snapshot = True
        return await original(self, offset, limit)

    class SlowRanking(FixedRanking):
        async def rank(self, request):
            assert database.engine.pool.checkedout() == 0
            provider_entered.set()
            await asyncio.Event().wait()

    monkeypatch.setattr(phase5_scenarios.ScenarioEvidenceRepository, "runs", verify_snapshot)
    event.listen(
        database.engine.sync_engine,
        "before_cursor_execute",
        lambda _conn, _cursor, statement, *_: statements.append(statement),
    )
    event.listen(database.engine.sync_engine, "commit", lambda _: commits.append(True))
    event.listen(database.engine.sync_engine, "rollback", lambda _: rollbacks.append(True))
    providers = replace(fixture_providers(), rankings=SlowRanking())
    app.dependency_overrides[get_scenarios] = lambda: ScenarioService(
        database.session_factory,
        app.state.settings,
        providers,
    )
    task = asyncio.create_task(client.post(PATH, json=BODY))
    try:
        await asyncio.wait_for(provider_entered.wait(), timeout=5)
        assert saw_readonly_snapshot and rollbacks and not commits
        assert not any(
            statement.lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for statement in statements
        )
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert database.engine.pool.checkedout() == 0


async def test_postgres_scope_drift_and_mixed_origin_refused(phase5_api, phase5_db, tmp_path):
    client, app = phase5_api
    baseline = (await client.post(PATH, json=BODY)).json()
    replay = {"scenario": SCENARIO, **baseline["coverage"]["page"]["nextRequest"]}
    source = phase5_db["collection"]
    config = json.loads(source.read_text(encoding="utf-8"))
    changed = tmp_path / "collection.json"
    slugs_raw = await asyncio.to_thread(Path(config["slugs"]).read_text, encoding="utf-8")
    slugs = json.loads(slugs_raw)
    slugs["entries"][0]["slug"] = "synthetic-changed"
    new_slugs = tmp_path / "slugs.json"
    new_slugs.write_text(json.dumps(slugs), encoding="utf-8")
    config["slugs"] = str(new_slugs)
    changed.write_text(json.dumps(config), encoding="utf-8")
    app.state.settings.catalog_collection_manifest = str(changed)
    assert (await client.post(PATH, json=replay)).status_code == 409
    config["origin"] = "real"
    changed.write_text(json.dumps(config), encoding="utf-8")
    response = await client.post(PATH, json=BODY)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "COLLECTION_SCOPE_INVALID"


async def test_postgres_replay_binds_manifest_precision_as_well_as_stored_values(
    phase5_api,
    phase5_db,
    tmp_path,
):
    client, app = phase5_api
    baseline = (await client.post(PATH, json=BODY)).json()
    replay = {"scenario": SCENARIO, **baseline["coverage"]["page"]["nextRequest"]}
    config = json.loads(phase5_db["collection"].read_text(encoding="utf-8"))
    original = await asyncio.to_thread(Path(config["fixture"]).read_text, encoding="utf-8")
    data = json.loads(original)
    condition = next(
        row for row in data["tables"]["test_condition"] if row["id"] == str(UUID(int=1))
    )
    assert condition["value_numeric"] == "0.00"
    condition["value_numeric"] = "0.0000"
    changed_fixture = tmp_path / "fixture.json"
    changed_fixture.write_text(json.dumps(data), encoding="utf-8")
    config["fixture"] = str(changed_fixture)
    changed_collection = tmp_path / "collection.json"
    changed_collection.write_text(json.dumps(config), encoding="utf-8")
    app.state.settings.catalog_collection_manifest = str(changed_collection)
    assert (await client.post(PATH, json=replay)).status_code == 409

    response = await client.post(PATH, json={"scenario": SCENARIO})
    assert response.status_code == 200
    conditions = [row for run in response.json()["coverage"]["items"] for row in run["conditions"]]
    assert (
        next(row for row in conditions if row["conditionId"] == str(UUID(int=1)))["valueNumeric"]
        == "0.00"
    )


async def test_postgres_cancellation_during_read_releases_pool_and_allows_retry(
    phase5_api, monkeypatch
):
    client, app = phase5_api
    database = app.state.database
    entered = asyncio.Event()
    block = True
    original = phase5_scenarios.ScenarioEvidenceRepository.runs

    async def slow_read(self, offset, limit):
        if block:
            await self.session.execute(text("SELECT pg_sleep(30)"))
        return await original(self, offset, limit)

    def on_query(_conn, _cursor, statement, *_):
        if "pg_sleep" in statement:
            entered.set()

    monkeypatch.setattr(phase5_scenarios.ScenarioEvidenceRepository, "runs", slow_read)
    event.listen(database.engine.sync_engine, "before_cursor_execute", on_query)
    task = asyncio.create_task(client.post(PATH, json=BODY))
    try:
        await asyncio.wait_for(entered.wait(), timeout=5)
        assert database.engine.pool.checkedout() == 1
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert database.engine.pool.checkedout() == 0
    block = False
    response = await client.post(PATH, json=BODY)
    assert response.status_code == 200


async def test_postgres_default_providers_return_independent_unavailable_sections(phase5_api):
    client, app = phase5_api
    app.state.settings.scenario_test_providers = False
    response = await client.post(PATH, json=BODY)
    assert response.status_code == 200
    result = response.json()
    assert result["context"]["origin"] == "synthetic"
    assert result["scope"]["ruleVersion"] is None
    assert result["coverage"]["items"] is None
    assert result["rankings"]["reasonCodes"] == ["RANKING_PROVIDER_UNAVAILABLE"]
    assert result["pillarEvidence"]["reasonCodes"] == ["CLASSIFICATION_UNAVAILABLE"]


async def test_postgres_lossless_approved_fields_and_refusal_of_unmappable_storage(pg_session):
    original = SCENARIO | {
        "pressure": {"value": "14.70000000000000000000000000000000", "unit": "psia"},
        "oxygen": {"value": "0.000", "unit": "%", "meaning": "ambient_oxygen_fraction_percent"},
    }
    scenario = ScenarioInput.model_validate(original)
    identity = await persist_scenario(pg_session, scenario)
    row = await pg_session.get(Scenario, identity)
    assert deserialize(row).model_dump(by_alias=True, exclude_unset=True) == original
    await pg_session.rollback()
    with pytest.raises(ScenarioStorageError):
        await persist_scenario(
            pg_session, ScenarioInput.model_validate(original | {"presetKey": "x"})
        )
    assert await pg_session.scalar(select(func.count()).select_from(Scenario)) == 1


async def test_phase4_comparison_keeps_original_observations_and_context(phase5_api, phase5_db):
    client, _ = phase5_api
    body = {"investigationIds": [str(INVESTIGATION), str(OTHER_INVESTIGATION)]}
    result = await client.post("/api/v1/compare", json=body)
    assert result.status_code == 200
    result = result.json()
    assert result["comparability"] == "not_established"
    assert result["deltas"] is result["highlights"] is None
    assert "CONDITIONS_NOT_EXAMINED" in " ".join(result["context"]["caveats"])
    originals = {str(row["id"]): row for row in phase5_db["manifest"]["tables"]["measurement"]}
    observed = [item for study in result["studies"] for item in study["observations"]["items"]]
    assert len(observed) == 3
    assert any(item["run"]["sampleGeometry"] == "TEST_ONLY inverse flame" for item in observed)
    for item in observed:
        measurement = item["measurement"]
        original = originals[measurement["id"]]
        assert measurement["unit"] == original["unit"]
        for public, stored in (("measuredValue", "measured_value"), ("uncertainty", "uncertainty")):
            value = original[stored]
            assert measurement[public] == (format(value, "f") if value is not None else None)
    partial = await client.post("/api/v1/compare", json=body | {"observationLimit": 1})
    assert partial.status_code == 200
    assert "PARTIAL_OBSERVATION_PAGE" in " ".join(partial.json()["context"]["caveats"])
