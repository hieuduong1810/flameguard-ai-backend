import asyncio
import json
import os
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings
from app.integrations.chat import MockProvider
from app.main import create_app
from app.models import ChatMessage, ChatSession
from app.repositories.collection import RUNTIME_TABLES
from app.schemas.api.chat import Answer, Citation
from app.services.chat import ChatService
from tests.integration.phase5_fixtures import provision_phase5

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def chat_db():
    raw = os.environ.get("PHASE4_ADMIN_URL")
    if not raw:
        pytest.skip("Set isolated PHASE4_ADMIN_URL")
    db = asyncio.run(provision_phase5(raw))
    admin = make_url(raw)
    writer = "fg6_" + uuid4().hex[:12]
    password = secrets.token_hex(24)

    async def provision():
        connection = await asyncpg.connect(
            host=admin.host,
            port=admin.port,
            user=admin.username,
            password=admin.password,
            database="postgres",
        )
        try:
            await connection.execute(f"CREATE ROLE \"{writer}\" LOGIN PASSWORD '{password}'")
            await connection.execute(
                f'GRANT CONNECT ON DATABASE "{db["owner_url"].database}" TO "{writer}"'
            )
        finally:
            await connection.close()
        owner = db["owner_url"]
        connection = await asyncpg.connect(
            host=owner.host,
            port=owner.port,
            user=owner.username,
            password=owner.password,
            database=owner.database,
        )
        try:
            await connection.execute(f'GRANT USAGE ON SCHEMA public TO "{writer}"')
            await connection.execute(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{writer}"')
            for table in sorted(RUNTIME_TABLES):
                await connection.execute(f'GRANT INSERT ON "{table}" TO "{writer}"')
        finally:
            await connection.close()

    asyncio.run(provision())
    db["writer_url"] = db["owner_url"].set(username=writer, password=password)
    config = json.loads(db["collection"].read_text())
    config.update(admissionVersion=2, runtimeTables=sorted(RUNTIME_TABLES))
    db["collection"].write_text(json.dumps(config))
    return db


@pytest.fixture
async def chat_api(chat_db):
    settings = Settings(
        _env_file=None,
        debug=False,
        app_env="test",
        chat_provider="mock",
        scenario_test_providers=True,
        database_url=chat_db["reader_url"].render_as_string(hide_password=False),
        runtime_database_url=chat_db["writer_url"].render_as_string(hide_password=False),
        catalog_collection_manifest=str(chat_db["collection"]),
    )
    app = create_app(settings)
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        yield client, app


async def create_session(client):
    response = await client.post("/api/v1/chat/sessions", json={"title": "public demo"})
    assert response.status_code == 201, response.text
    assert response.headers["cache-control"] == "no-store"
    return response.json()["id"]


async def test_chat_roundtrip_and_admission(chat_api):
    client, _ = chat_api
    identity = await create_session(client)
    result = await client.post(
        f"/api/v1/chat/sessions/{identity}/messages", json={"question": "test"}
    )
    assert result.status_code == 201, result.text
    answer = result.json()["assistant"]["answer"]
    assert answer["origin"] == "synthetic"
    assert answer["citations"]
    history = await client.get(f"/api/v1/chat/sessions/{identity}/messages")
    assert history.status_code == 200
    assert [item["role"] for item in history.json()["items"]] == ["user", "assistant"]
    assert history.json()["items"][1]["answer"] == answer
    # Chat rows must coexist with unchanged scientific exact admission.
    assert (await client.get("/api/v1/chat/sessions/" + identity)).status_code == 200


async def test_concurrent_pairs(chat_api):
    client, _ = chat_api
    identity = await create_session(client)
    responses = await asyncio.gather(
        *[
            client.post(f"/api/v1/chat/sessions/{identity}/messages", json={"question": str(n)})
            for n in range(3)
        ]
    )
    assert all(r.status_code == 201 for r in responses)
    rows = (await client.get(f"/api/v1/chat/sessions/{identity}/messages")).json()["items"]
    assert [r["role"] for r in rows] == ["user", "assistant"] * 3


async def test_bad_citation_no_partial_write(chat_api, monkeypatch):
    client, app = chat_api
    identity = await create_session(client)

    async def bad(self, request):
        return Answer(
            state="answered",
            text="bad",
            origin="synthetic",
            citations=(Citation(source_document_id=uuid4(), source_locator="invented"),),
        )

    monkeypatch.setattr(MockProvider, "answer", bad)
    result = await client.post(
        f"/api/v1/chat/sessions/{identity}/messages", json={"question": "test"}
    )
    assert result.status_code == 502
    assert (await client.get(f"/api/v1/chat/sessions/{identity}/messages")).json()["items"] == []


async def test_expiry_and_invalid_input(chat_api, chat_db):
    client, _ = chat_api
    identity = await create_session(client)
    engine = create_async_engine(chat_db["owner_url"])
    try:
        async with engine.begin() as conn:
            await conn.execute(
                update(ChatSession)
                .where(ChatSession.id == identity)
                .values(created_at=datetime.now(UTC) - timedelta(days=2))
            )
    finally:
        await engine.dispose()
    assert (await client.get(f"/api/v1/chat/sessions/{identity}")).status_code == 404
    assert (
        await client.post(f"/api/v1/chat/sessions/{uuid4()}/messages", json={"question": " "})
    ).status_code == 422


async def test_timeout_and_atomic_rollback(chat_api, monkeypatch):
    client, app = chat_api
    identity = await create_session(client)
    app.state.settings.chat_timeout_seconds = 0.01

    async def slow(self, *args):
        await asyncio.sleep(1)

    monkeypatch.setattr(MockProvider, "answer", slow)
    result = await client.post(
        f"/api/v1/chat/sessions/{identity}/messages", json={"question": "test"}
    )
    assert result.status_code == 201
    assert result.json()["assistant"]["answer"]["state"] == "timeout"
    from app.repositories.chat import ChatRepository

    async def fail(self, *args):
        raise ValueError("test failure")

    monkeypatch.setattr(ChatRepository, "add_citations", fail)
    assert (
        await client.post(f"/api/v1/chat/sessions/{identity}/messages", json={"question": "test"})
    ).status_code == 503
    assert (
        len((await client.get(f"/api/v1/chat/sessions/{identity}/messages")).json()["items"]) == 2
    )


async def test_manifest_boundary_rejects_tampering(chat_api, chat_db):
    client, _ = chat_api
    original = chat_db["collection"].read_text()
    config = json.loads(original)
    try:
        config["runtimeTables"].append("source_document")
        chat_db["collection"].write_text(json.dumps(config))
        assert (await client.post("/api/v1/chat/sessions", json={})).status_code == 503
        config.pop("admissionVersion")
        config.pop("runtimeTables")
        chat_db["collection"].write_text(json.dumps(config))
        assert (await client.post("/api/v1/chat/sessions", json={})).status_code == 503
    finally:
        chat_db["collection"].write_text(original)


async def test_advisor_and_openapi(chat_api):
    from tests.fixtures.phase5 import SCENARIO

    client, _ = chat_api
    response = await client.post("/api/v1/advisor/assessments", json={"scenario": SCENARIO})
    assert response.status_code == 200, response.text
    assert set(response.json()["pillars"]) == {"prevention", "detection", "suppression"}
    assert all(
        p["state"] == "abstained" and p["origin"] == "synthetic"
        for p in response.json()["pillars"].values()
    )
    api = (await client.get("/openapi.json")).json()
    assert "post" in api["paths"]["/api/v1/advisor/assessments"]
    assert "post" in api["paths"]["/api/v1/chat/sessions/{identity}/messages"]


async def test_legacy_history_and_denied_science_writes(chat_api, chat_db):
    from uuid import UUID

    from sqlalchemy import insert, text

    client, app = chat_api
    identity = UUID(await create_session(client))
    engine = create_async_engine(chat_db["owner_url"])
    try:
        async with engine.begin() as conn:
            await conn.execute(
                insert(ChatMessage).values(
                    id=uuid4(),
                    chat_session_id=identity,
                    role="assistant",
                    body="Historical plain text",
                    created_at=datetime.now(UTC),
                )
            )
    finally:
        await engine.dispose()
    history = (await client.get(f"/api/v1/chat/sessions/{identity}/messages")).json()
    assert history["items"][0]["answer"]["origin"] == "unknown"
    async with app.state.runtime_database.session_factory() as session:
        assert not await session.scalar(
            text("SELECT has_table_privilege(current_user,'investigation','INSERT,UPDATE,DELETE')")
        )


async def test_cancellation_propagates(chat_api, monkeypatch):
    client, app = chat_api
    identity = await create_session(client)
    entered = asyncio.Event()

    async def wait(self, *args):
        entered.set()
        await asyncio.sleep(10)

    monkeypatch.setattr(MockProvider, "answer", wait)
    from uuid import UUID

    task = asyncio.create_task(ChatService(app).send(UUID(identity), "test"))
    await asyncio.wait_for(entered.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert (await client.get(f"/api/v1/chat/sessions/{identity}/messages")).json()["items"] == []


async def test_phase45_regression_and_scientific_tamper(chat_api, chat_db):
    from sqlalchemy import select

    from app.models import Investigation
    from tests.fixtures.phase5 import SCENARIO

    client, _ = chat_api
    await create_session(client)
    assert (await client.get("/api/v1/dashboard/summary")).status_code == 200
    assert (await client.get("/api/v1/investigations")).status_code == 200
    assert (
        await client.post("/api/v1/mission/scenarios/evaluate", json={"scenario": SCENARIO})
    ).status_code == 200
    engine = create_async_engine(chat_db["owner_url"])
    try:
        async with engine.connect() as conn:
            row = (await conn.execute(select(Investigation.id, Investigation.title).limit(1))).one()
            await conn.rollback()
            async with conn.begin():
                await conn.execute(
                    update(Investigation).where(Investigation.id == row.id).values(title="tampered")
                )
            try:
                assert (await client.post("/api/v1/chat/sessions", json={})).status_code == 503
            finally:
                async with conn.begin():
                    await conn.execute(
                        update(Investigation)
                        .where(Investigation.id == row.id)
                        .values(title=row.title)
                    )
    finally:
        await engine.dispose()


async def test_followup_context_is_scoped_and_provider_is_injectable(chat_api):
    from tests.fixtures.phase5 import INVESTIGATION

    client, app = chat_api
    requests = []

    class Adapter(MockProvider):
        async def answer(self, request):
            requests.append(request)
            return await super().answer(request)

    app.state.chat_provider_factory = Adapter
    response = await client.post(
        "/api/v1/chat/sessions", json={"investigation_id": str(INVESTIGATION)}
    )
    first = response.json()["id"]
    other = await create_session(client)
    for identity, question in [
        (first, "First scoped question"),
        (other, "Other session question"),
        (first, "Follow up on that"),
    ]:
        result = await client.post(
            f"/api/v1/chat/sessions/{identity}/messages", json={"question": question}
        )
        assert result.status_code == 201, result.text
    current = requests[-1]
    assert current.question == "Follow up on that"
    assert current.investigation_id == INVESTIGATION
    assert [m.role for m in current.history] == ["user", "assistant"]
    assert current.history[0].text == "First scoped question"
    assert all("Other session question" not in m.text for m in current.history)
    assert current.corpus_version and current.collection_fingerprint and current.allowed_sources
    assert not current.history_truncated


async def test_history_bounds_and_publication_gate(chat_api, chat_db):
    from uuid import UUID

    from sqlalchemy import insert

    from app.integrations.chat import HISTORY_CHARACTERS, HISTORY_MESSAGES, MESSAGE_CHARACTERS
    from app.models import ChatMessage

    client, app = chat_api
    identity = UUID(await create_session(client))
    engine = create_async_engine(chat_db["owner_url"])
    try:
        async with engine.begin() as conn:
            await conn.execute(
                insert(ChatMessage),
                [
                    dict(
                        id=uuid4(),
                        chat_session_id=identity,
                        role="user",
                        body="x" * 3000,
                        created_at=datetime.now(UTC) + timedelta(microseconds=n),
                    )
                    for n in range(16)
                ],
            )
    finally:
        await engine.dispose()
    seen = []

    class Adapter(MockProvider):
        async def answer(self, request):
            seen.append(request)
            return (await super().answer(request)).model_copy(update={"origin": "real"})

    app.state.chat_provider_factory = Adapter
    result = await client.post(
        f"/api/v1/chat/sessions/{identity}/messages", json={"question": "Continue"}
    )
    assert result.status_code == 502
    request = seen[0]
    assert request.history_truncated
    assert len(request.history) <= HISTORY_MESSAGES
    assert sum(len(m.text) for m in request.history) <= HISTORY_CHARACTERS
    assert all(len(m.text) <= MESSAGE_CHARACTERS for m in request.history)
    history = await client.get(f"/api/v1/chat/sessions/{identity}/messages")
    assert len(history.json()["items"]) == 16


async def test_advisor_paging_outcomes_and_snapshot_drift(chat_api, monkeypatch):
    from app.services.scenarios import ScenarioService
    from tests.fixtures.phase5 import SCENARIO

    client, app = chat_api
    result = await client.post(
        "/api/v1/advisor/assessments", json={"scenario": SCENARIO, "pages": {"limit": 1}}
    )
    assert result.status_code == 200, result.text
    gaps = result.json()["gaps"]
    assert any("PARTIAL_OR_PAGED_EVIDENCE" in g for g in gaps.values())
    assert any("UNREVIEWED_EVIDENCE" in g for g in gaps.values())
    assert all("PROVIDER_ABSTAINED" in g for g in gaps.values())
    app.state.settings.chat_provider = "unavailable"
    result = await client.post("/api/v1/advisor/assessments", json={"scenario": SCENARIO})
    assert all("PROVIDER_UNAVAILABLE" in g for g in result.json()["gaps"].values())
    original = ScenarioService.evaluate

    async def drift(self, request):
        evaluation = await original(self, request)
        return evaluation.model_copy(
            update={"scope": evaluation.scope.model_copy(update={"dataset_version": "drift"})}
        )

    monkeypatch.setattr(ScenarioService, "evaluate", drift)
    assert (
        await client.post("/api/v1/advisor/assessments", json={"scenario": SCENARIO})
    ).status_code == 409
