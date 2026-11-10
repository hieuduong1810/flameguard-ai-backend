# NASA Data team → Backend ingestion handoff

**Status: CONTRACT DRAFT; awaiting Data team delivery and field-level review.**
The user assigned scientific acquisition, cleaning, curation and import to
the Data team. Backend/Codex owns storage compatibility, validation and API
readiness, not a second independent ingest pipeline.

## Required delivery artifacts

| Artifact | Owner | Acceptance evidence |
| --- | --- | --- |
| Source manifest | Data | Original NASA PSI/source URL, DOI if applicable, retrieval time, license/access constraints, original file/asset reference |
| Normalized export or importer | Data | Repeatable process/output in agreed schema, deterministic source IDs and version |
| Field/unit dictionary | Data | `variable`/`observable` names, original units, approved unit conversions and rounding |
| Identity/deduplication rule | Data + Backend review | Unique `psi_id` investigation mapping, external run-key scope, duplicate policy |
| Scientific review record | Data | Reviewed vs preliminary vs unknown status, curator method and unresolved issues |
| Claim↔document traceability | Data | Every claim association preserves document ID, locator, excerpt if available and optional run |
| QA results | Data | Field completeness, invalid rows, rejects, duplicate counts, missing sources and representative examples |
| Import operations record | Data | Safe test run, rollback/retry/idempotency method, ownership of operational failures |

## Approved database groups available for the handoff

- Catalog: `investigation`, `test_run`, `test_condition`, `measurement`.
- Provenance: `source_document`, `evidence_claim`, `claim_source`.
- Optional classifications: `tag`, `investigation_tag`, `document_chunk`.
- Import operations: `ingestion_job`, `import_issue`.

All 21 ERD tables already exist as approved models/migrations; table existence
does not mean scientific rows have been imported or verified. The original
column and nullability rules remain in `../phase-2-database-implementation.md`.

## Field rules to enforce together

1. **Identity:** preserve external `psi_id` separately from UUID and public
   route slug. Confirm whether `external_run_key` is unique within its
   investigation; the ERD does not impose a uniqueness constraint on it.
2. **Original data:** retain raw asset URI, original measurement value/unit,
   original condition string/value and reported uncertainty. A conversion must
   be reproducible and unit-labeled; do not overwrite originals silently.
3. **Unknowns:** null/unavailable differs from zero, measured false and
   "NASA has no such experiment". Do not invent missing dates or DOI.
4. **Provenance:** `evidence_claim` links to multiple `source_document` records
   through `claim_source`. Each link has `source_locator`, optional excerpt,
   and optional `test_run_id`. Validate that any linked run has a scientifically
   compatible investigation context; the FK alone does not check this.
5. **Review:** agree on the allowed `ingestion_status`, `data_status`,
   `evidence_status`, `review_status`, severity and issue-resolution vocabulary.
   These are open text fields under the frozen ERD, not a license to mix meanings.
6. **Repeated imports:** agree on idempotency, atomicity, dedup, record versioning
   and partial failure handling **before** touching shared/development data.
7. **Separation:** synthetic tests and frontend demos must never be imported
   under the same verified statuses as curator-reviewed scientific records.

## Safe acceptance sequence — Backend responsibility

1. Validate a small sanitized mapping sample **outside production**.
2. Parse it into existing Pydantic schemas/ORM; log normalized mismatches
   without printing credentials or private provider data.
3. Run tests against a distinct disposable PostgreSQL testing target;
   never reset/overwrite development or production tables.
4. Check relational integrity and claim/document/run provenance.
5. Verify units, null semantics, input encoding, duplicates and status filtering.
6. Demonstrate representative read-only repository queries and canonical DTOs.
7. Produce an acceptance report: accepted, rejected, unresolved, reproducibility
   evidence, and which team owns each correction.
8. **Separately approve** any write/import run against a shared environment.

## Outstanding decisions to send the Data team

- Export format and delivery location? (CSV/JSON/Parquet or importer; not fixed.)
- Approved unit dictionary and status vocabulary?
- Source-document content/large telemetry assets: where stored and how linked?
- Who signs off a claim as reviewed and how is that review audited?
- Stable public slug mapping: who curates it and how is identity collision handled?
- Import retry/rollback strategy and the target environment?

Phase 4 service code may proceed using clearly labeled synthetic fixtures,
but verified scientific responses remain blocked until the necessary curated
data and acceptance checks exist.
