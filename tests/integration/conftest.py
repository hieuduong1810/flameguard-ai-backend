from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app import models as m


@pytest.fixture
async def graph(pg_session):
    """Clearly synthetic records, rolled back per test; never NASA research records."""
    now = datetime(2020, 1, 1, tzinfo=UTC)
    inv = m.Investigation(psi_id="TEST_ONLY_INV_1", title="Synthetic fixture, not research")
    inv2 = m.Investigation(psi_id="TEST_ONLY_INV_2", title="Second synthetic fixture")
    run = m.TestRun(investigation=inv, external_run_key="TEST_ONLY_RUN")
    condition = m.TestCondition(test_run=run, variable="fixture-variable", data_status="synthetic")
    measurement = m.Measurement(
        test_run=run,
        observable="TEST_ONLY_OBSERVABLE",
        unit="fixture-unit",
        measured_value=Decimal("0.12345678901234567890123456789"),
        raw_asset_ref="fixture://not-real",
        uncertainty=None,
    )
    doc = m.SourceDocument(
        investigation=inv,
        source_url="https://example.invalid/test-only/1",
        document_type="synthetic",
        ingestion_status="test-only",
    )
    doc2 = m.SourceDocument(
        investigation=inv,
        source_url="https://example.invalid/test-only/2",
        document_type="synthetic",
        ingestion_status="test-only",
    )
    claim = m.EvidenceClaim(
        claim_text="TEST ONLY; no scientific finding",
        evidence_status="synthetic",
        review_status="test-only",
    )
    claim2 = m.EvidenceClaim(
        claim_text="SECOND TEST ONLY; no scientific finding",
        evidence_status="synthetic",
        review_status="test-only",
    )
    link = m.ClaimSource(
        claim=claim,
        source_document=doc,
        test_run=run,
        source_locator="test-only locator 1",
        source_excerpt="Not scientific evidence",
    )
    extra_links = [
        m.ClaimSource(claim=claim, source_document=doc2, source_locator="test-only locator 2"),
        m.ClaimSource(claim=claim2, source_document=doc, source_locator="test-only locator 3"),
    ]
    scenario = m.Scenario(
        name="TEST_ONLY_SCENARIO",
        environment="test-only",
        gravity="unknown-test-value",
        oxygen_pct=Decimal("0.123"),
        pressure_psi=Decimal("0.456"),
        material="TEST_ONLY_MATERIAL",
        ventilation="unknown-test-value",
    )
    match = m.ScenarioMatch(
        scenario=scenario,
        test_run=run,
        match_status="test-only-gap",
        score=None,
        explanation="Fixture only; no matching algorithm",
        engine_version="test-only",
    )
    tag = m.Tag(slug="test-only-tag-1", label="Synthetic tag")
    tag2 = m.Tag(slug="test-only-tag-2", label="Another synthetic tag")
    tag_link = m.InvestigationTag(investigation=inv, tag=tag)
    extra_tag_links = [
        m.InvestigationTag(investigation=inv, tag=tag2),
        m.InvestigationTag(investigation=inv2, tag=tag),
    ]
    dimension = m.MatchDimension(scenario_match=match, variable="fixture", match_status="test-only")
    chunk = m.DocumentChunk(
        source_document=doc,
        chunk_index=0,
        source_locator="test-only locator",
        chunk_text="Synthetic text; not a scientific source",
    )
    chat = m.ChatSession(investigation=inv, title="TEST_ONLY_CHAT")
    message = m.ChatMessage(session=chat, role="assistant", body="TEST ONLY; no RAG performed")
    citation = m.MessageCitation(
        message=message, source_document=doc, source_locator="test-only locator"
    )
    version = m.ModelVersion(
        model_name="TEST_ONLY_MODEL", version="fixture", validation_status="unvalidated"
    )
    training = m.ModelTrainingRun(
        model_version=version, training_dataset_ref="fixture://no-real-dataset", trained_at=now
    )
    prediction = m.PredictionResult(
        scenario=scenario,
        model_version=version,
        predicted_observable="TEST_ONLY_OBSERVABLE",
        predicted_value=Decimal("0.12345678901234567890123456789"),
        unit="fixture-unit",
        applicability_status="synthetic-not-applicable",
    )
    job = m.IngestionJob(
        source_uri="fixture://no-real-import", status="test-running", started_at=now
    )
    issue = m.ImportIssue(
        ingestion_job=job,
        severity="test-only",
        explanation="Synthetic document-level issue",
        review_status="test-only",
    )
    rows = {
        "investigation": inv,
        "test_run": run,
        "test_condition": condition,
        "measurement": measurement,
        "source_document": doc,
        "evidence_claim": claim,
        "claim_source": link,
        "scenario": scenario,
        "scenario_match": match,
        "tag": tag,
        "investigation_tag": tag_link,
        "match_dimension": dimension,
        "document_chunk": chunk,
        "chat_session": chat,
        "chat_message": message,
        "message_citation": citation,
        "model_version": version,
        "model_training_run": training,
        "prediction_result": prediction,
        "ingestion_job": job,
        "import_issue": issue,
    }
    extras = {"investigation": inv2, "source_document": doc2, "evidence_claim": claim2, "tag": tag2}
    pg_session.add_all([*rows.values(), *extras.values(), *extra_links, *extra_tag_links])
    await pg_session.flush()
    pg_session.expunge_all()
    return rows, extras
