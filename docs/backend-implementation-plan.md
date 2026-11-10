# Backend architecture and implementation plan

This document is the stable requirements and architecture baseline for FlameGuard AI Backend.
It applies across the complete development roadmap and is not an implementation status report.

Update this document only when the user explicitly requests or approves a change to product
requirements, architecture, schema requirements, API contracts or roadmap scope. Completing
work, adding a migration, running tests or moving to another phase does not require an edit.
Implementation details, approvals, verification results and progress belong in separate
`docs/phase-*.md` records. Consult those records and the source code for delivery status.

## Product scope and design references

FlameGuard AI is a research platform for exploring NASA microgravity combustion experiments,
comparing experimental evidence, identifying scenario evidence gaps and producing traceable
scientific explanations. Its results must distinguish source-backed findings, inference,
uncertainty, simulated/demo content and unsupported conclusions. It does not provide
operational spacecraft fire-safety certification.

The workspace contains sibling backend and frontend repositories. Backend work belongs in
`flameguard-ai-backend/`; the Next.js frontend in `FlameInFreewall_Tourbillion/` is a separate
integration client and must not be changed by backend-only tasks without authorization.

The original [architecture and ERD diagrams](index.html) define logical entities and
relationships. Frontend interfaces and page consumers define UI compatibility requirements;
they do not establish scientific validity or silently override the ERD. Approved physical
mappings and contract decisions must be recorded explicitly. Preserve the original diagrams
unless the user requests a design change.

| Design reference | Requirement area |
| --- | --- |
| D01-D02 | Overall system and modular-monolith component architecture |
| D03-D05 | Must/Should/Could database entities and their relationships |
| D06-D07 | User navigation and feature/database ownership |
| D08-D10 | Dashboard, exploration/comparison and scenario evidence workflows |
| D11 | Evidence-grounded assistant, retrieval and original-source citations |
| D12-D13 | Scientific ingestion, curation and many-to-many claim provenance |
| D14-D15 | Guarded predictive execution and implementation dependencies |

## Architecture and responsibility boundaries

Use Python, FastAPI, Poetry, PostgreSQL, SQLAlchemy 2.x asynchronous sessions, asyncpg,
Alembic, Pydantic v2/pydantic-settings, pytest, HTTPX and Ruff. Supported runtime and
compatible dependency versions are declared in `pyproject.toml` and pinned by `poetry.lock`.

The backend is a modular monolith with these responsibility boundaries:

| Area | Responsibility |
| --- | --- |
| API | Versioned routes, request validation, response contracts and HTTP errors |
| Schemas | Typed input/output data; explicit nullability and serialization rules |
| Services | Business decisions, workflows and transaction boundaries |
| Repositories | Async database queries and explicit relationship loading |
| Models/database | Approved schema, referential integrity, engine/session lifecycle |
| Integrations | NASA/source systems, object storage and provider adapters |
| Ingestion | Parsing, unit normalization, provenance and curator review |
| Migrations | Reviewed, versioned changes to the persistent schema |

Create modules when they have real functionality. Avoid generic CRUD layers without a
concrete use case, redundant abstractions, microservices, Kubernetes and unnecessary brokers.
A worker, retrieval framework or external service requires an actual approved need.

Keep application settings environment driven. Initialize/dispose database resources through
application lifespan, use request-scoped sessions, and keep commits explicit at service/caller
boundaries. Relationships must not trigger accidental synchronous or implicit async I/O.
Apply schema changes through Alembic, not application-startup table creation.

Liveness must not depend on database availability. Readiness checks the configured database
with a bounded deadline. Return sanitized failures, keep credentials out of responses/logs,
reject unrestricted production CORS and disable production debug. Deployment security,
authentication and monitoring must follow explicitly agreed operational requirements.

## Feature and navigation requirements

| Surface | Required capability |
| --- | --- |
| Landing `/` | Explain the platform, scientific scope and research limitations |
| Dashboard `/dashboard` | Catalog/source coverage aggregates, featured studies and scenario entry points |
| Explorer `/explorer` | Search, filters, ordering, pagination and study selection |
| Detail `/explorer/[id]` | Source-backed overview, test runs, conditions, measurements, claims and source/export access |
| Comparison modal | Side-by-side comparison of 2-3 studies with compatible units/context and explicit caveats |
| Mission `/mission` | Shared scenario inputs, ranked research relevance and six-dimension evidence coverage |
| Assistant overlay | Optional study context, grounded answers, original-source citations and evidence-gap responses |
| Predictive Lab panel | Explicit dataset/model/domain/uncertainty readiness checks before guarded execution |

These are target capabilities, not a statement that any particular route or feature is
available. Actual API availability is discoverable through OpenAPI and delivery records.

## Approved logical ERD inventory

The following transcribes D03-D05. Repeated context entities in those diagrams refer to the
same tables, giving 21 distinct entities. Logical types, PK/FK/UK annotations and explicit
optional relationships are retained exactly. Physical type mappings, nullability, defaults,
indexes and deletion policies require an explicit approved decision record; implementations
must not infer additional columns or constraints merely from table names or frontend mocks.

### Must have (D03)
| Entity | Columns exactly as shown in ERD |
| --- | --- |
| INVESTIGATION | `uuid id PK`; `string psi_id UK`; `string title`; `string research_purpose`; `string platform` |
| TEST_RUN | `uuid id PK`; `uuid investigation_id FK`; `string external_run_key`; `string material_type`; `string sample_geometry`; `string gravity` |
| TEST_CONDITION | `uuid id PK`; `uuid test_run_id FK`; `string variable`; `decimal value_numeric`; `string value_text`; `string unit`; `string data_status` |
| MEASUREMENT | `uuid id PK`; `uuid test_run_id FK`; `string observable`; `decimal measured_value`; `string unit`; `string raw_asset_ref`; `decimal uncertainty` |
| SOURCE_DOCUMENT | `uuid id PK`; `uuid investigation_id FK`; `string source_url`; `string doi`; `string document_type`; `string version`; `string ingestion_status` |
| EVIDENCE_CLAIM | `uuid id PK`; `string claim_text`; `string evidence_status`; `string review_status`; `string limitation`; `datetime created_at` |
| CLAIM_SOURCE | `uuid id PK`; `uuid claim_id FK`; `uuid source_document_id FK`; `uuid test_run_id FK "Nullable"`; `string source_locator`; `string source_excerpt` |
| SCENARIO | `uuid id PK`; `string name`; `string environment`; `string gravity`; `decimal oxygen_pct`; `decimal pressure_psi`; `string material`; `string ventilation` |
| SCENARIO_MATCH | `uuid id PK`; `uuid scenario_id FK`; `uuid test_run_id FK`; `string match_status`; `decimal score`; `string explanation`; `string engine_version` |

### Should have (D04)

| Entity | Columns exactly as shown in ERD |
| --- | --- |
| TAG | `uuid id PK`; `string slug UK`; `string label`; `string category` |
| INVESTIGATION_TAG | `uuid id PK`; `uuid investigation_id FK`; `uuid tag_id FK` |
| MATCH_DIMENSION | `uuid id PK`; `uuid scenario_match_id FK`; `string variable`; `string match_status`; `string gap_reason` |
| DOCUMENT_CHUNK | `uuid id PK`; `uuid source_document_id FK`; `int chunk_index`; `string source_locator`; `string chunk_text`; `string embedding_ref` |
| CHAT_SESSION | `uuid id PK`; `uuid investigation_id FK "Nullable"`; `string title`; `datetime created_at` |
| CHAT_MESSAGE | `uuid id PK`; `uuid chat_session_id FK`; `string role`; `string body`; `datetime created_at` |
| MESSAGE_CITATION | `uuid id PK`; `uuid chat_message_id FK`; `uuid source_document_id FK`; `string source_locator` |

### Could have (D05)

| Entity | Columns exactly as shown in ERD |
| --- | --- |
| MODEL_VERSION | `uuid id PK`; `string model_name`; `string version`; `string validation_status`; `string applicability_domain` |
| MODEL_TRAINING_RUN | `uuid id PK`; `uuid model_version_id FK`; `string training_dataset_ref`; `string metrics_ref`; `datetime trained_at` |
| PREDICTION_RESULT | `uuid id PK`; `uuid scenario_id FK`; `uuid model_version_id FK`; `string predicted_observable`; `decimal predicted_value`; `string unit`; `decimal uncertainty`; `string applicability_status` |
| INGESTION_JOB | `uuid id PK`; `string source_uri`; `string status`; `datetime started_at`; `datetime completed_at` |
| IMPORT_ISSUE | `uuid id PK`; `uuid ingestion_job_id FK`; `string severity`; `string field_name`; `string explanation`; `string review_status` |

Relationships specified by the diagrams:

- INVESTIGATION has zero or more TEST_RUN and SOURCE_DOCUMENT rows; each child has one parent.
- TEST_RUN has zero or more TEST_CONDITION and MEASUREMENT rows.
- EVIDENCE_CLAIM and SOURCE_DOCUMENT are **many-to-many through CLAIM_SOURCE**.
  CLAIM_SOURCE optionally references a TEST_RUN; a run can have many source associations.
- SCENARIO has many SCENARIO_MATCH rows, each compared to one TEST_RUN; runs can appear in many matches.
- INVESTIGATION and TAG are many-to-many through INVESTIGATION_TAG.
- SCENARIO_MATCH has MATCH_DIMENSION rows; SOURCE_DOCUMENT has DOCUMENT_CHUNK rows.
- CHAT_SESSION optionally references an INVESTIGATION and has CHAT_MESSAGE rows.
  CHAT_MESSAGE and SOURCE_DOCUMENT are linked by MESSAGE_CITATION with a locator.
- MODEL_VERSION has MODEL_TRAINING_RUN and PREDICTION_RESULT rows. Each prediction also
  references a SCENARIO. INGESTION_JOB has IMPORT_ISSUE rows.

There is no direct EVIDENCE_CLAIM.investigation_id, no direct claim.source_document_id, and no
approved relationship from MEASUREMENT to SOURCE_DOCUMENT. Do not add these implicitly.

## Scientific data and contract invariants

Data flow: discover sources -> retain originals/URLs -> normalize investigation/run identity
and original conditions/units -> review provenance and unknowns -> approved relational
entities -> repository queries -> services -> explicit API projections -> frontend views.

- Keep internal UUIDs, external NASA PSI identifiers and public URL slugs distinct. A
  stable public slug requires an approved mapping; do not generate permanent identity from
  mutable display titles without a collision policy.
- Preserve original measurements, conditions, units, raw asset references, uncertainty,
  source URLs, DOI when available and review/validation context. Unknown values remain
  unknown; a missing observation is not zero or a nominal atmosphere.
- Claim-document provenance is many-to-many through CLAIM_SOURCE, including locator,
  excerpt and optional run context. A flat UI object must not discard these associations.
- Investigation-tag classification remains many-to-many through INVESTIGATION_TAG.
- Keep approved string gravity/ventilation fields distinct from numeric scenario UI inputs;
  use an explicit unit-aware API mapping or seek approval for a schema change.
- MEASUREMENT stores observables and raw asset references, not a preapproved telemetry
  array structure. Time-series channels, sampling and asset manifests require an explicit
  API/asset contract that preserves original data and uncertainty.
- Chat citations identify original documents and source locators. Do not invent claim/chunk
  foreign keys or citation metadata outside the approved schema.
- Catalog counts, confidence badges and publication-looking identifiers do not establish
  verification. Aggregate only data with the declared validation status and compatible units.
- Combined scenario coverage must be supported by compatible conditions within relevant
  runs, not independently overlapping min/max ranges from unrelated studies.
- Relevance scores describe research similarity, never a fire probability or safety verdict.
  Evidence gaps must reflect the curated collection's coverage, not unverified universal
  claims about the absence of all NASA research.
- RAG must retrieve traceable sources, check citations, distinguish support from inference
  and explain missing evidence instead of inventing answers or references.
- Model/training/prediction tables are storage structures. Prediction requires validated
  datasets, versioned artifacts, applicability checks and defensible uncertainty. Demo
  equations or hardcoded intervals do not constitute scientific validation.

## API contract baseline

The following is the preliminary integration contract. Implementation status is tracked
separately; implementing an endpoint does not require changing this baseline. Changes to
names, semantics, identity, units or response contracts require explicit agreement.

All paths below are under `/api/v1`. Proposed JSON uses camelCase to fit TypeScript interfaces;
ORM attributes remain independent. An explicit frontend adapter is required for identity,
nullability and multi-source evidence. Version and finalize DTOs before implementing endpoints.
Lists use `{items, total, offset, limit}` with proposed defaults offset 0, limit 20, max 100;
unknown filters/identifiers produce validation/404 errors rather than silent substitutions.

| Frontend surface | Proposed endpoint | Inputs | Response / UI types | ERD entities | Priority |
| --- | --- | --- | --- | --- | --- |
| Dashboard | `GET /dashboard/summary` | Optional validated catalog filters | `{investigationCount, runCount, verifiedRunCount, claimCount, sourceCoverage, fuelDistribution, facilityDistribution, featuredInvestigations, caveats}`; counts only from curated data | INVESTIGATION, TEST_RUN, TEST_CONDITION, SOURCE_DOCUMENT, EVIDENCE_CLAIM, CLAIM_SOURCE, TAG | Phase 4 |
| Explorer | `GET /investigations` | `q`, `fuel=solid|droplet|gas`, `facility=CIR|MSG|Cygnus`, `gravity=0g|1g|partial`, `sort=newest|code-asc|runs-desc|confidence`, offset/limit; additional purpose/source/evidence filters by agreement | Paginated Investigation DTOs and available facets; metadata-dependent filters require approved mappings | INVESTIGATION, TAG, INVESTIGATION_TAG, TEST_RUN, TEST_CONDITION, SOURCE_DOCUMENT | Phase 4 |
| Detail | `GET /investigations/{uuid}` | Canonical UUID | Investigation DTO, completeness/caveats; 404 if unknown | INVESTIGATION, TEST_RUN, TEST_CONDITION, SOURCE_DOCUMENT, CLAIM_SOURCE | Phase 4 |
| Public detail URLs | `GET /investigations/by-slug/{slug}` | Explicit public slug | Same DTO with distinct UUID, slug and psiId; mapping policy requires decision | INVESTIGATION plus reviewed identity mapping | Phase 4 |
| Runs tab | `GET /investigations/{uuid}/runs` | Pagination; optional validated status/material | TestRun DTOs with conditions/measurements, units, provenance and missing-data status | TEST_RUN, TEST_CONDITION, MEASUREMENT; validation linkage requires an approved provenance policy | Phase 4 |
| Telemetry tab | `GET /runs/{uuid}/telemetry` | Optional time range/channel list and bounded/downsampled point limit | `{runId, series, units, rawAssetRef, dataStatus, provenance, caveats}`; series fits TelemetryDataPoint when actual channels exist | MEASUREMENT.raw_asset_ref, TEST_RUN; time-series metadata requires an approved asset contract | Phase 4 |
| Claims tab | `GET /investigations/{uuid}/claims` | Pagination; optional category/review filter once vocabulary approved | Canonical claim DTOs with `sources[]` (document, locator, excerpt, optional run); no loss of associations | EVIDENCE_CLAIM, CLAIM_SOURCE, SOURCE_DOCUMENT, TEST_RUN | Phase 4 |
| PSI/export tab | `GET /investigations/{uuid}/sources` | Pagination | Original source URLs, DOI, document type/version/status; browser JSON/CSV export can remain local over API DTOs | SOURCE_DOCUMENT, INVESTIGATION | Phase 4 |
| Comparison modal | `POST /compare` | `{investigationIds: UUID[2..3]}` distinct; explicit measurement/status filters | `{studies, metrics, deltas, highlights, caveats}` following comparisonUtils type shapes; separate verified/unknown counts and compatible-unit/context summaries | INVESTIGATION, TEST_RUN, TEST_CONDITION, MEASUREMENT, SOURCE_DOCUMENT, CLAIM_SOURCE | Phase 4 |
| Mission form | `GET /scenario-presets` (optional) | None | Reviewed or explicitly illustrative ScenarioPreset DTOs; UI-only presets may stay local | SCENARIO if persisted; no preset table approved | Phase 5 |
| Mission evidence | `POST /scenarios/analyze` | `{scenario: ScenarioInput}`; optional reviewed ranking configuration later | `{scenarioId, rankings: RankedInvestigation[], gapMatrix: GapMatrixResult, engineVersion, provenance, caveats}`; run-level match details retained | SCENARIO, SCENARIO_MATCH, MATCH_DIMENSION, TEST_RUN, TEST_CONDITION, CLAIM_SOURCE, SOURCE_DOCUMENT | Phase 5 |
| Global assistant | `POST /ask` | `{question, sessionId?, investigationId?}` with length/context limits | `{sessionId, message: ChatMessage, suggestedQuestions, isOutOfScope?, provenance}`; citations carry source document/URL/locator plus optional claim/run context | CHAT_SESSION, CHAT_MESSAGE, MESSAGE_CITATION, DOCUMENT_CHUNK, SOURCE_DOCUMENT, CLAIM_SOURCE, EVIDENCE_CLAIM | Phase 6 |
| Lab inline panel | Readiness endpoint subject to validation design | ScenarioInput | PredictiveLabAudit plus artifact provenance; blocked when prerequisites absent; execution requires validated data, model and applicability domain | MODEL_VERSION, MODEL_TRAINING_RUN, PREDICTION_RESULT, SCENARIO | Phase 7 |

Contract mapping details:

- **Investigation DTO:** preserve code/title/researchPurpose/platform and nested UI fields
  (`fuelDetails`, ranges, variables, findings, dataAvailability, sources, tags) where backed
  by reviewed data. Add canonical `id: UUID`, `slug: string`, `psiId: string`. The frontend compatibility contract uses `id` as a slug, so its adapter must provide `id = dto.slug` for existing routes
  and carry `dto.id` separately for API calls. A versioned API can make this explicit without
  rewriting database identity. Slug and rich display metadata are not columns in the original ERD; their storage requires an approved mapping or schema change.
- **Run DTO:** `id` is UUID; retain `externalRunKey` separately from UI demo identifiers.
  Map known TEST_CONDITION.variable/unit pairs into oxygenPct, pressurePsi, flowVelocityCmS,
  radiantFluxKWPerM2, ambientTempK, gravityG. Map MEASUREMENT.observable/unit pairs into
  known measurement properties only after unit/observable vocabularies are approved.
  Preserve original values and units along with converted display units. Booleans such as
  coolFlameObserved are not directly represented by a decimal-only measured_value.
- **Evidence DTO:** canonical claim `id`, claimText/evidenceStatus/reviewStatus/limitation;
  `sources[]` contains every CLAIM_SOURCE and SOURCE_DOCUMENT reference. Investigation scope
  is derived through source documents/run associations, not a claim-owned investigation FK.
  Existing EvidenceClaim's singular DOI/locator/authors/year fields cannot represent all sources;
  a UI extension or explicitly labeled primary-source projection is needed. Never discard links.
- **ScenarioInput:** name, environment (`iss|lunar|mars|earth|custom`), numeric gravity in g,
  oxygenPct (%), pressurePsi (absolute psi), material, numeric airflowVelocity (cm/s), optional
  description. Baseline form ranges: g 0-1, O2 15-40, pressure 7-16, airflow 0-50; these are UI
  limits, not validated scientific applicability limits. Reject non-finite inputs. Do not persist
  a preset slug as a UUID. Storage conversion for gravity/ventilation requires agreement first.
- **Gap/ranking DTOs:** preserve six dimension names (gravity/material/oxygen/pressure/airflow/
  combined), MATCH/RELATED/PARTIAL/GAP and explanatory strings. Persist SCENARIO_MATCH per run,
  then aggregate to ranked investigations, with engineVersion and reproducible provenance.
  Do not treat catalog-level score as a SCENARIO_MATCH without retaining the selected run basis.
- **Chat DTO:** map CHAT_MESSAGE.body -> content and created_at -> UTC epoch milliseconds
  (`timestamp`), UUID -> id, role user/assistant. Enrich MESSAGE_CITATION through its document
  and investigation to fit AiCitation; claimId cannot be persisted as a citation FK under the
  current ERD. Retain all original source links and locators, with an evidenceGapWarning when
  applicable. Streaming and session-history endpoints require explicit contracts; a UI streaming indicator alone does not define those requirements.
- **Nullability:** required TypeScript display fields must not force unavailable source data into the database. Extend
  the frontend adapter/types to support unknowns when integrating; do not manufacture PI names,
  ranges, geometry, findings, confidence tiers or source titles. Decimal-to-JSON conversion needs
  an explicit precision policy; UI numeric values must not silently round scientific originals.

## Compatibility decisions and change control

The original ERD does not define storage for every frontend display field, a permanent public
slug, boolean observation encoding or complete measurement/source validation linkage.
Maintain explicit mappings for these gaps. A frontend-required field is not authorization
to invent scientific values or add a database column. Record decisions about physical types,
nullability, units, provenance, enums and constraints before applying the affected migrations.

Source models and API projection models have different responsibilities. Preserve all source
associations and original values in persistence while presenting a deliberate, versioned
contract to the frontend. Any changes to approved columns, cardinality or citation identity
must be reviewed as requirement/schema changes, rather than hidden inside implementation work.

## Delivery roadmap and dependencies

The phase numbering below defines scope and dependency order. It is not a progress checklist;
completion status and executed results belong in phase-specific records.

| Phase | Scope | Delivery requirement |
| --- | --- | --- |
| 1 | Backend foundation | Configuration, FastAPI lifecycle, health/readiness, CORS, async database access, Alembic, Poetry and tests |
| 2 | Approved ERD and migrations | All 21 entities, approved physical mapping, typed schemas, meaningful repositories and migration/relationship tests |
| 3 | Scientific ingestion and source validation | Retain originals, deduplicate PSI identities, normalize units, validate provenance and preserve unknowns |
| 4 | Catalog and comparison APIs | Dashboard, explorer/detail/run/source/telemetry contracts and scientifically compatible comparisons |
| 5 | Scenario matching and gaps | Validated inputs, reproducible run-level matching, versioned relevance and same-run coverage explanations |
| 6 | Evidence-grounded assistant | Source/chunk retrieval, reviewed claims, citation validation, abstention and chat persistence |
| 7 | Predictive Lab | Validated datasets/models, training provenance, applicability and uncertainty before execution |
| 8 | Deployment and integration | HTTPS, environment-specific configuration, secret management, migrations, monitoring and frontend integration |

Ingestion and source validation precede scientific aggregates and evidence matching.
Reviewed source provenance precedes grounded answers. Validated data and model artifacts
precede prediction. Deployment needs may be addressed alongside these stages when requested,
without changing their scientific validation requirements.

## Verification and documentation requirements

Verify each delivery with checks appropriate to its behavior: model/key/cardinality tests,
clean-database migration checks, schema drift inspection, async repository operations,
request/response validation, source traceability and integration behavior. Use separate
PostgreSQL test databases; never reset, truncate or overwrite development data during tests.
Do not report checks as passed unless they were executed.

The documentation responsibilities remain stable:

- `README.md`: project purpose, technology, setup, configuration and common development workflow.
- `docs/backend-implementation-plan.md`: requirements, architecture, ERD/API mapping and roadmap.
- `docs/index.html`: original approved architecture and logical ERD reference.
- `docs/phase-*.md`: scoped implementation details, decisions/approvals, changed files,
  migration revisions, test results, limitations and handoff notes for each delivery.

Do not append completion notes, test totals, local machine incidents, temporary blockers,
commit hashes or implementation snapshots to README or this plan. Update these two baseline
files only for an explicit user-requested or user-approved requirement/contract change.
Do not modify unrelated projects, alter original diagrams, commit or push without the
applicable user authorization.
