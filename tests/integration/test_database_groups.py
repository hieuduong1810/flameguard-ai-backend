from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import selectinload

from app import models as m
from app.repositories.catalog import CatalogRepository
from app.repositories.evidence import EvidenceRepository
from app.repositories.scenarios import ScenarioRepository
from app.schemas.catalog import InvestigationCreate, InvestigationUpdate
from tests.erd_reference import approved_nullables, erd_tables
from tests.test_schemas import schema_for

pytestmark = pytest.mark.integration


async def test_catalog_repository_create_get_update_and_loaded_runs(pg_session, graph) -> None:
    rows, extras = graph
    repo = CatalogRepository(pg_session)
    created = await repo.create_investigation(
        InvestigationCreate(psi_id="TEST_ONLY_CREATED", title="Not a scientific record")
    )
    assert created.id and created.platform is None
    await repo.update_investigation(
        created.id, InvestigationUpdate(title="Updated fixture", research_purpose=None)
    )
    pg_session.expunge_all()
    fetched = await repo.get_investigation(created.id)
    assert fetched.title == "Updated fixture"
    assert fetched.research_purpose is None
    assert await repo.get_investigation(uuid4()) is None
    assert await repo.update_investigation(uuid4(), InvestigationUpdate(title="unused")) is None
    investigation = await repo.get_investigation(rows["investigation"].id)
    assert [run.id for run in investigation.test_runs] == [rows["test_run"].id]
    assert {tag.id for tag in investigation.tags} == {rows["tag"].id, extras["tag"].id}
    runs = await repo.list_test_runs(investigation.id)
    assert runs[0].conditions[0].value_numeric is None
    assert runs[0].measurements[0].measured_value == Decimal("0.12345678901234567890123456789")
    assert await repo.list_test_runs(uuid4()) == []


async def test_claim_sources_preserve_many_to_many_and_optional_context(pg_session, graph) -> None:
    rows, extras = graph
    repo = EvidenceRepository(pg_session)
    links = await repo.list_sources_for_claim(rows["evidence_claim"].id)
    assert {link.source_document.id for link in links} == {
        rows["source_document"].id,
        extras["source_document"].id,
    }
    assert {link.source_locator for link in links} == {"test-only locator 1", "test-only locator 2"}
    assert any(link.test_run is None for link in links)
    assert any(link.test_run.id == rows["test_run"].id for link in links if link.test_run)
    claims = await repo.list_claims_for_source(rows["source_document"].id)
    assert {claim.id for claim in claims} == {
        rows["evidence_claim"].id,
        extras["evidence_claim"].id,
    }
    assert all(link.source_document.source_url for claim in claims for link in claim.source_links)
    assert await repo.list_sources_for_claim(uuid4()) == []
    assert await repo.list_claims_for_source(uuid4()) == []


async def test_duplicate_provenance_associations_do_not_duplicate_claim_results(pg_session, graph):
    rows, _ = graph
    pg_session.add(
        m.ClaimSource(
            claim_id=rows["evidence_claim"].id,
            source_document_id=rows["source_document"].id,
            source_locator="another test-only locator",
        )
    )
    await pg_session.flush()
    claims = await EvidenceRepository(pg_session).list_claims_for_source(rows["source_document"].id)
    assert len(claims) == 2


async def test_many_to_many_read_views_work_in_both_directions(pg_session, graph) -> None:
    rows, extras = graph
    claim = (
        await pg_session.scalars(
            select(m.EvidenceClaim)
            .where(m.EvidenceClaim.id == rows["evidence_claim"].id)
            .options(selectinload(m.EvidenceClaim.source_documents))
        )
    ).one()
    assert len(claim.source_documents) == 2
    document = (
        await pg_session.scalars(
            select(m.SourceDocument)
            .where(m.SourceDocument.id == rows["source_document"].id)
            .options(selectinload(m.SourceDocument.claims), selectinload(m.SourceDocument.chunks))
        )
    ).one()
    assert len(document.claims) == 2
    assert document.chunks[0].embedding_ref is None
    tag = (
        await pg_session.scalars(
            select(m.Tag)
            .where(m.Tag.id == rows["tag"].id)
            .options(selectinload(m.Tag.investigations))
        )
    ).one()
    assert {inv.id for inv in tag.investigations} == {
        rows["investigation"].id,
        extras["investigation"].id,
    }


async def test_scenario_repository_retains_run_and_dimension_context(pg_session, graph) -> None:
    rows, _ = graph
    matches = await ScenarioRepository(pg_session).list_matches(rows["scenario"].id)
    assert matches[0].test_run.id == rows["test_run"].id
    assert matches[0].score is None
    assert matches[0].dimensions[0].id == rows["match_dimension"].id
    assert await ScenarioRepository(pg_session).list_matches(uuid4()) == []


async def test_chat_sessions_messages_and_original_source_citations(pg_session, graph) -> None:
    rows, _ = graph
    chat = (
        await pg_session.scalars(
            select(m.ChatSession)
            .where(m.ChatSession.id == rows["chat_session"].id)
            .options(
                selectinload(m.ChatSession.investigation),
                selectinload(m.ChatSession.messages)
                .selectinload(m.ChatMessage.citations)
                .selectinload(m.MessageCitation.source_document),
            )
        )
    ).one()
    assert chat.investigation.id == rows["investigation"].id
    citation = chat.messages[0].citations[0]
    assert citation.source_document.id == rows["source_document"].id
    assert citation.source_locator == "test-only locator"
    global_chat = m.ChatSession()
    pg_session.add(global_chat)
    await pg_session.flush()
    assert global_chat.investigation_id is None and global_chat.title is None


async def test_model_training_predictions_and_scenario_relationships(pg_session, graph) -> None:
    rows, _ = graph
    version = (
        await pg_session.scalars(
            select(m.ModelVersion)
            .where(m.ModelVersion.id == rows["model_version"].id)
            .options(
                selectinload(m.ModelVersion.training_runs),
                selectinload(m.ModelVersion.predictions).selectinload(m.PredictionResult.scenario),
            )
        )
    ).one()
    assert version.training_runs[0].training_dataset_ref == "fixture://no-real-dataset"
    assert version.training_runs[0].trained_at.tzinfo is not None
    assert version.predictions[0].scenario.id == rows["scenario"].id
    assert version.predictions[0].uncertainty is None
    scenario = (
        await pg_session.scalars(
            select(m.Scenario)
            .where(m.Scenario.id == rows["scenario"].id)
            .options(selectinload(m.Scenario.predictions))
        )
    ).one()
    assert scenario.predictions[0].model_version_id == version.id


async def test_ingestion_job_and_document_level_issue(pg_session, graph) -> None:
    rows, _ = graph
    job = (
        await pg_session.scalars(
            select(m.IngestionJob)
            .where(m.IngestionJob.id == rows["ingestion_job"].id)
            .options(selectinload(m.IngestionJob.issues))
        )
    ).one()
    assert job.completed_at is None
    assert job.issues[0].field_name is None
    assert job.issues[0].ingestion_job_id == job.id


async def test_unloaded_relationship_raises_instead_of_implicit_io(pg_session, graph) -> None:
    rows, _ = graph
    investigation = await pg_session.get(m.Investigation, rows["investigation"].id)
    with pytest.raises(InvalidRequestError, match="lazy='raise'"):
        _ = investigation.test_runs


@pytest.mark.parametrize("table_name", erd_tables())
async def test_every_entity_roundtrips_to_its_read_schema(pg_session, graph, table_name):
    rows, _ = graph
    row = rows[table_name]
    fetched = await pg_session.get(type(row), row.id)
    response = schema_for(table_name, "Read").model_validate(fetched)
    assert response.id == row.id


@pytest.mark.parametrize("table_name", erd_tables())
async def test_primary_keys_and_required_columns_are_enforced(pg_session, graph, table_name):
    rows, _ = graph
    table = m.Base.metadata.tables[table_name]
    row = rows[table_name]
    values = {col.name: getattr(row, col.name) for col in table.columns}
    async with pg_session.begin_nested():
        with pytest.raises(IntegrityError):
            async with pg_session.begin_nested():
                await pg_session.execute(insert(table).values(**values))
    for column in table.columns:
        if column.nullable:
            continue
        with pytest.raises(IntegrityError):
            async with pg_session.begin_nested():
                await pg_session.execute(
                    update(table).where(table.c.id == row.id).values(**{column.name: None})
                )


FOREIGN_KEYS = [
    (table.name, fk.parent.name)
    for table in m.Base.metadata.tables.values()
    for fk in table.foreign_keys
]


@pytest.mark.parametrize("table_name, column_name", FOREIGN_KEYS)
async def test_each_foreign_key_rejects_a_missing_parent(
    pg_session, graph, table_name, column_name
):
    rows, _ = graph
    table = m.Base.metadata.tables[table_name]
    with pytest.raises(IntegrityError):
        async with pg_session.begin_nested():
            await pg_session.execute(
                update(table)
                .where(table.c.id == rows[table_name].id)
                .values(**{column_name: uuid4()})
            )


@pytest.mark.parametrize(
    "table_name, unique_column", [("investigation", "psi_id"), ("tag", "slug")]
)
async def test_approved_unique_values_reject_duplicates(
    pg_session, graph, table_name, unique_column
):
    rows, _ = graph
    table = m.Base.metadata.tables[table_name]
    values = {col.name: getattr(rows[table_name], col.name) for col in table.columns}
    values["id"] = uuid4()
    assert values[unique_column]
    with pytest.raises(IntegrityError):
        async with pg_session.begin_nested():
            await pg_session.execute(insert(table).values(**values))


@pytest.mark.parametrize("table_name", erd_tables())
async def test_all_approved_nullable_columns_accept_unknowns(pg_session, graph, table_name):
    rows, _ = graph
    nullable = approved_nullables()[table_name]
    if nullable:
        table = m.Base.metadata.tables[table_name]
        await pg_session.execute(
            update(table)
            .where(table.c.id == rows[table_name].id)
            .values(**{column: None for column in nullable})
        )
        await pg_session.flush()


async def test_parent_delete_cannot_silently_remove_evidence(pg_session, graph) -> None:
    rows, _ = graph
    from sqlalchemy import delete

    with pytest.raises(IntegrityError):
        async with pg_session.begin_nested():
            await pg_session.execute(
                delete(m.SourceDocument).where(m.SourceDocument.id == rows["source_document"].id)
            )
    assert await pg_session.get(m.SourceDocument, rows["source_document"].id) is not None


async def test_repository_commits_stay_inside_test_transaction(pg_session) -> None:
    repo = CatalogRepository(pg_session)
    row = await repo.create_investigation(
        InvestigationCreate(psi_id="TEST_ONLY_COMMIT", title="Must not persist beyond this test")
    )
    await pg_session.commit()
    assert await repo.get_investigation(row.id) is not None
