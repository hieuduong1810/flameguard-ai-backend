# Phase 2 database implementation

Status: all 21 models, schemas, repositories and three migrations implemented.
The user explicitly approved the physical schema proposal before implementation.

## Baseline inspection

- Existing Phase 1 repository is clean at `2d05849`.
- Poetry check and Ruff passed. Existing suite: 34 passed, 1 opt-in integration test skipped.
- SQLAlchemy Base and Alembic metadata are intentionally empty; no source migration revisions.
- Async engine/session dependency and Alembic environment are ready to reuse.
- A separate execution of the existing read-only PostgreSQL test passed (1 passed,
  34 deselected). The currently selected local development target is `127.0.0.1:5432/flameguard`.
  Read-only inspection found only `public.alembic_version` with no recorded revisions.
- D03/D04/D05 in `docs/diagram/index.html` provide all 21 entities, column names, logical types,
  keys and relationships. Repeated context entities in D04/D05 are not new tables.
- Frontend TypeScript interfaces have been reviewed read-only; see the existing
  [architecture audit](backend-implementation-plan.md) for the column inventory and API mappings.

The original HTML and frontend remain unchanged. No scientific data will be seeded.
The original HTML SHA-256 remains
`26D01D5FBF540DCDE406A2E0DC3289E7ECD4C4D4F22FAEE3E94FE133BB907994`.

## User-approved physical schema mapping

The ERD does not specify most attribute nullability, decimal precision/scale, string lengths,
timezone handling, identifier defaults, physical table case, indexes or deletion policies.
The following mapping was explicitly approved by the user; these details are not claimed
to appear in the original diagram, which remains unchanged.

1. Use lowercase snake_case physical table names (`INVESTIGATION` -> `investigation`) and
   the exact existing snake_case column names. Do not add or remove columns.
2. Use native PostgreSQL UUIDs mapped to Python UUID, with Python `uuid4` defaults for IDs.
   External NASA `psi_id` remains a separate string, never a UUID or public URL slug.
3. Map Mermaid string to unbounded Text, decimal to unconstrained Numeric/Python Decimal,
   int to Integer, and datetime to timezone-aware DateTime. Do not add unapproved length or
   scientific precision restrictions. Use UTC; default only record `created_at` timestamps
   to creation time. Actual training/job event timestamps are explicitly supplied.
4. Primary keys and mandatory foreign keys are NOT NULL. Keep the two explicitly optional
   foreign keys nullable: claim_source.test_run_id and chat_session.investigation_id.
5. Other attributes are NOT NULL except the explicit approved nullable list below. This
   supports missing source metadata and incomplete workflow states without fabricated values.
6. Implement only the explicitly marked unique values: investigation.psi_id and tag.slug,
   both NOT NULL. Do not silently add composite uniqueness, enum restrictions, range checks,
   or mutually exclusive numeric/text checks absent from the ERD.
7. Add nonunique indexes on foreign keys for join performance. PK and unique constraints
   provide their own indexes. Use predictable constraint/index names.
8. Use PostgreSQL's default NO ACTION for foreign-key deletes/updates, with no ORM delete
   cascades. Relationships use lazy='raise'; repository queries explicitly eager-load what
   they return. Association objects retain all CLAIM_SOURCE and INVESTIGATION_TAG fields.
9. Keep gravity and ventilation as strings as approved. No numeric gravity/airflow columns,
   direct claim-investigation FK, measurement-source FK or slug column will be invented.

### Approved nullable attributes

All columns not listed below are NOT NULL under the approved mapping. A nullable attribute defaults to None in
Create schemas; Update schemas distinguish omitted fields from explicit null. A nullable
numeric observation is unknown, never a default zero.

| ERD table | Nullable attributes | Reason |
| --- | --- | --- |
| INVESTIGATION | research_purpose, platform | Permit genuinely missing source metadata |
| TEST_RUN | external_run_key, material_type, sample_geometry, gravity | Preserve unknown original run metadata |
| TEST_CONDITION | value_numeric, value_text, unit | Numeric/categorical/unknown conditions; some variables are dimensionless |
| MEASUREMENT | measured_value, raw_asset_ref, uncertainty | Original assets or scalar values may be unavailable; unknown uncertainty stays unknown |
| SOURCE_DOCUMENT | doi, version | Not all documents have a DOI or explicit version |
| EVIDENCE_CLAIM | limitation | Limitation text may not yet be provided |
| CLAIM_SOURCE | test_run_id, source_excerpt | Optional run is explicit in ERD; source locator remains required |
| SCENARIO | None | Persist explicit scenario inputs without invented defaults |
| SCENARIO_MATCH | score | An evidence gap need not have a numerical relevance score |
| TAG | category | Classification category may be unspecified |
| INVESTIGATION_TAG | None | Association requires both parents |
| MATCH_DIMENSION | gap_reason | A matching dimension may have no gap reason |
| DOCUMENT_CHUNK | embedding_ref | A source chunk may exist before vector indexing |
| CHAT_SESSION | investigation_id, title | Optional context is explicit; a new session may be untitled |
| CHAT_MESSAGE | None | Message role, body and creation time are required |
| MESSAGE_CITATION | None | Citation requires message, original source and locator |
| MODEL_VERSION | applicability_domain | An unvalidated version may not yet have an established domain |
| MODEL_TRAINING_RUN | metrics_ref | Metrics artifact may be unavailable; dataset and actual trained_at remain required |
| PREDICTION_RESULT | uncertainty | Unknown uncertainty must remain unknown; no prediction algorithm is implemented |
| INGESTION_JOB | completed_at | A running job has not completed |
| IMPORT_ISSUE | field_name | An issue can concern an entire document rather than a field |

## Implemented model and migration mapping

All entities have UUID `id` primary keys. All rows below are implemented and migrated.
The source diagrams remain authoritative for cardinality; the approved nullable mapping above
does not change any relationship. The three revisions are linked in the order shown.

| ERD table | Model | Primary key | Foreign keys | Relationships | Migration | Status |
| --- | --- | --- | --- | --- | --- | --- |
| INVESTIGATION | Investigation | UUID id | None | test runs, source documents, tag links, optional-context chat sessions | 0001_must_have | Implemented |
| TEST_RUN | TestRun | UUID id | investigation_id -> investigation.id | investigation, conditions, measurements, claim source links, scenario matches | 0001_must_have | Implemented |
| TEST_CONDITION | TestCondition | UUID id | test_run_id -> test_run.id | test run | 0001_must_have | Implemented |
| MEASUREMENT | Measurement | UUID id | test_run_id -> test_run.id | test run | 0001_must_have | Implemented |
| SOURCE_DOCUMENT | SourceDocument | UUID id | investigation_id -> investigation.id | investigation, claim links, chunks, message citations | 0001_must_have | Implemented |
| EVIDENCE_CLAIM | EvidenceClaim | UUID id | None | many source documents through claim source association objects | 0001_must_have | Implemented |
| CLAIM_SOURCE | ClaimSource | UUID id | claim_id -> evidence_claim.id; source_document_id -> source_document.id; optional test_run_id -> test_run.id | canonical claim, document, optional run | 0001_must_have | Implemented |
| SCENARIO | Scenario | UUID id | None | run-level matches, prediction results | 0001_must_have | Implemented |
| SCENARIO_MATCH | ScenarioMatch | UUID id | scenario_id -> scenario.id; test_run_id -> test_run.id | scenario, test run, match dimensions | 0001_must_have | Implemented |
| TAG | Tag | UUID id | None | many investigations through investigation tag association objects | 0002_should_have | Implemented |
| INVESTIGATION_TAG | InvestigationTag | UUID id | investigation_id -> investigation.id; tag_id -> tag.id | investigation, tag | 0002_should_have | Implemented |
| MATCH_DIMENSION | MatchDimension | UUID id | scenario_match_id -> scenario_match.id | scenario match | 0002_should_have | Implemented |
| DOCUMENT_CHUNK | DocumentChunk | UUID id | source_document_id -> source_document.id | original document | 0002_should_have | Implemented |
| CHAT_SESSION | ChatSession | UUID id | optional investigation_id -> investigation.id | optional investigation, messages | 0002_should_have | Implemented |
| CHAT_MESSAGE | ChatMessage | UUID id | chat_session_id -> chat_session.id | session, citations | 0002_should_have | Implemented |
| MESSAGE_CITATION | MessageCitation | UUID id | chat_message_id -> chat_message.id; source_document_id -> source_document.id | message, original source | 0002_should_have | Implemented |
| MODEL_VERSION | ModelVersion | UUID id | None | training runs, prediction results | 0003_could_have | Implemented |
| MODEL_TRAINING_RUN | ModelTrainingRun | UUID id | model_version_id -> model_version.id | model version | 0003_could_have | Implemented |
| PREDICTION_RESULT | PredictionResult | UUID id | scenario_id -> scenario.id; model_version_id -> model_version.id | scenario, model version | 0003_could_have | Implemented |
| INGESTION_JOB | IngestionJob | UUID id | None | import issues | 0003_could_have | Implemented |
| IMPORT_ISSUE | ImportIssue | UUID id | ingestion_job_id -> ingestion_job.id | ingestion job | 0003_could_have | Implemented |

## Verification and data protection

- Registered all 21 typed models; tests compare column/type/key/cardinality inventory
  to the embedded Mermaid definitions in automated tests.
- Created three ordered, self-contained Alembic revisions. Reviewed SQL, metadata consistency,
  constraints and indexes without calling Base.metadata.create_all().
- Used separate PostgreSQL test databases and transactional test rollback. Never truncate,
  drop or reset the development database. Do not blindly stamp migration state.
- Tested inserts, queries, updates, constraints and relationship navigation across all groups.
  Test values are clearly synthetic fixtures and never presented as NASA scientific records.
- Confirmed the selected development target and existing schema before applying additive
  migrations. Inspected the resulting schema and checked metadata drift.
- Do not implement API CRUD, NASA ingestion, scenario scoring, RAG or prediction algorithms.
- Do not automatically commit or push Phase 2.

## Frontend compatibility considerations

- Frontend slug IDs remain distinct from database UUIDs and psi_id. Storage for permanent
  public slugs and many rich display fields is not in the approved ERD.
- Numeric gravity/airflow in ScenarioState require a future explicit API mapping to the
  approved string gravity/ventilation fields. No new persistence fields are proposed here.
- Flat EvidenceClaim objects must be adapted to many-to-many sources with exact locators,
  excerpts and optional run context. Do not flatten or discard provenance associations.
- MEASUREMENT represents observables and raw asset references, not an embedded telemetry
  array. Unknowns/units/uncertainty must survive the future API projection.
- Chat citations refer to original documents, not invented claim/chunk foreign keys.
- Model versions/training artifacts/prediction records are structures only. Their existence
  does not validate a scientific model or constitute operational fire-safety guidance.

The database foundation is ready for Phase 3 scientific ingestion and source-validation work.
No ingestion, scoring, RAG or prediction algorithm has been implemented in this phase.

## Model, schema and repository files

Models and matching scalar Create/Update/Read schemas are grouped by domain:

| Domain | Model module | Pydantic module |
| --- | --- | --- |
| Catalog, runs, conditions, measurements, tags | `app/models/catalog.py` | `app/schemas/catalog.py` |
| Original sources, claims, provenance links, chunks | `app/models/evidence.py` | `app/schemas/evidence.py` |
| Scenarios, run-level matches, dimensions | `app/models/scenarios.py` | `app/schemas/scenarios.py` |
| Sessions, messages, original-source citations | `app/models/chat.py` | `app/schemas/chat.py` |
| Model versions, training records, prediction records | `app/models/prediction.py` | `app/schemas/prediction.py` |
| Ingestion jobs and import issues | `app/models/ingestion.py` | `app/schemas/ingestion.py` |

`app/models/base.py` supplies shared naming conventions, UUID IDs and a UTC creation-time
helper. `app/models/__init__.py` registers all entities for Alembic. UUIDs and record
`created_at` defaults are Python/ORM defaults, not database server defaults: direct SQL
inserts must explicitly supply those fields. No extra audit timestamps were added.

`app/schemas/base.py` provides `from_attributes`, extra-field rejection, finite decimals,
timezone validation/UTC normalization and partial-update semantics. Create schemas omit
generated IDs/creation times; Read schemas include them. Update schemas reject explicit null
for NOT NULL columns while leaving omitted fields unchanged. Decimal values serialize to
JSON strings to preserve precision. These are scalar persistence contracts, not finalized
public/frontend DTOs; no business routes expose internal artifact/embedding references.

`app/repositories/catalog.py` implements create/get/update investigation and load related
runs with conditions/measurements. `app/repositories/evidence.py` retrieves all source links
for a claim (including locator/excerpt/run), or deduplicated claims for a source, without
discarding provenance. `app/repositories/scenarios.py` retrieves run-level matches with
dimensions. Repositories flush but never commit; callers own transaction boundaries.

For example, a future service can explicitly commit a validated catalog record:

```python
from app.repositories.catalog import CatalogRepository
from app.schemas.catalog import InvestigationCreate

async with database.session_factory() as session:
    repository = CatalogRepository(session)
    investigation = await repository.create_investigation(validated_create_schema)
    await session.commit()
```

`validated_create_schema` must come from source-reviewed input; this example does not seed
any research record. Writable association objects own CLAIM_SOURCE/INVESTIGATION_TAG
changes. Direct many-to-many convenience relationships are read-only views. No composite
uniqueness constraints were added beyond the two explicitly approved unique values.

Schema foreign keys guarantee that referenced rows exist; they do not prove a scientific
source is valid. In particular, the ERD does not enforce that an optional CLAIM_SOURCE run
belongs to the same investigation as its document. Phase 3 curation must validate that
context or seek approval for additional constraints; none was silently invented here.

## Reproducing verification safely

Run from the backend root:

```powershell
poetry check
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
poetry run alembic history
poetry run alembic current
poetry run alembic check
```

Without TEST_DATABASE_URL, PostgreSQL tests are skipped; model/schema/offline SQL and API
tests still execute. Database tests require an explicitly selected testing server/role
with CREATEDB and a test-name template distinct from the development database:

```powershell
# Example template; replace the password with the testing role's actual password.
$env:TEST_DATABASE_URL = 'postgresql+asyncpg://flameguard:YOUR_TEST_PASSWORD@127.0.0.1:5433/flameguard_test_phase2'
poetry run pytest
Remove-Item Env:\TEST_DATABASE_URL
```

The fixture connects to the testing server's `postgres` administrative database to create
`flameguard_test_phase2_<random-suffix>`. It then migrates that new, initially empty database
through 9/16/21 tables, retaining the per-step table inventory and revision. It does not need
or grant CREATEDB to the native development role. Tests enforce a test-name prefix and
reject a template matching the development database name. No development tables are used
for inserts, updates, deletes or migration tests.

Each test session binds ORM sessions to a rollback-only outer transaction and savepoints;
even explicit session commits stay inside that outer transaction. Session teardown verifies
all 21 tables contain zero rows. Synthetic fixture values use TEST_ONLY labels and reserved
`.invalid` URLs, never purported NASA records. Test databases and schema remain available
for inspection: the suite does not drop databases, truncate tables, reset the development
schema or stamp revisions. The last test target, migration steps and row counts are stored
in ignored `.tools/phase2-test-state.json` without credentials. Repeated runs create new test
databases; cleanup of retained databases is a separate explicit action.

The migration files include standard downgrade implementations, but no database downgrade
was executed. Only reviewed additive upgrades were applied to development.

## Development schema verification

The selected development target was confirmed as `127.0.0.1:5432/flameguard` before changes.
It contained only an empty Alembic version table, and the role had permission to create
tables in `public`. Applied `poetry run alembic upgrade head` successfully without resetting,
dropping, stamping or overwriting existing data.

- Current revision: `0003_could_have` (single head).
- Domain tables: **21**, excluding `alembic_version`.
- Foreign keys: **21**; approved nonunique foreign-key indexes: **21**.
- Unique constraints: **2**, on investigation.psi_id and tag.slug; primary keys: **21**.
- Live schema versus model metadata: **no differences** (`alembic check` also passed).
- All 21 development tables contain **zero rows**. No scientific/demo seed records were inserted.
- Original ERD HTML hash and frontend Git status are unchanged.

Development used native PostgreSQL on 5432. Isolated tests used the Docker server on 5433.
Migrating a separate Docker development database later requires selecting its DATABASE_URL
and running `poetry run alembic upgrade head`; migrations do not copy data between servers.

## Executed Phase 2 results

| Check | Actual result |
| --- | --- |
| `poetry check` | Passed: All set! |
| `poetry run ruff check .` | Passed: All checks passed! |
| `poetry run ruff format --check .` | Passed: 55 files already formatted |
| `poetry run pytest -q --tb=short` with TEST_DATABASE_URL configured | **228 passed in 15.70s** |
| Same test command without TEST_DATABASE_URL | **128 passed, 100 skipped in 1.21s**; PostgreSQL-dependent tests skipped |
| Clean test database migrations | Passed: 9 -> 16 -> 21 domain tables and all three expected revisions |
| Test fixture teardown | Passed: zero persisted rows in all 21 test tables, including after explicit session commit |
| Native development `alembic upgrade head` | Passed: all three revisions applied additively |
| `alembic history` / `alembic current` | Linear three-revision history; `0003_could_have (head)` |
| `alembic check` | Passed: No new upgrade operations detected |
| Development inspection | 21 domain tables, 21 PKs, 21 FKs, 2 unique constraints, 21 nonunique FK indexes, zero rows |
| Frontend / original HTML | Unchanged; original SHA-256 preserved |

The final full test run used fresh Docker database `flameguard_test_phase2_6447e4b3` on
127.0.0.1:5433. It was retained with its schema and no data. The earlier successful full
run used another isolated database; no database was dropped. Verification was completed
before the user's commit/push step; publication state is tracked in Git.
