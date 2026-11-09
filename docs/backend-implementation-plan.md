# Backend implementation audit and plan

Audit date: 2026-11-09. Phase 1 scope: foundation only. This document proposes future contracts;
it does not approve schema changes or verify any NASA scientific finding.

## A. Existing system and inspected sources

The workspace contains two sibling Git repositories. Before editing, backend Git status showed
only untracked `docs/`; frontend status was clean. The backend contained `docs/index.html`
and no application code. The workspace root itself is not a Git repository. No repository was
initialized, committed, or pushed. The frontend and original design files are preserved.

Primary design reference: [docs/index.html](index.html). Its HTML embeds 15 Mermaid diagrams,
each repeated in a copyable source block. The renderer imports Mermaid 11 from jsDelivr, uses
strict security and the neutral theme, and shows a fallback when the CDN cannot load or a
diagram cannot parse. There are 15 relative `.mmd` download links, but none of those files is
present in the backend docs directory. The embedded definitions are available and were used
for this audit; there are no other local linked diagram assets. No diagram was edited.

| Diagram | Design requirement |
| --- | --- |
| D01 Overall system architecture | UI -> FastAPI -> PostgreSQL; original assets retained; later vector/model storage and providers |
| D02 Detailed logical components | Modular monolith; catalog, matching, gaps, RAG, ingestion, guarded prediction responsibilities |
| D03 Must-have ERD | Nine core tables; run-level evidence and many-to-many claim provenance |
| D04 Should-have ERD | Seven additional tag, match-detail, chunk, chat and citation tables |
| D05 Could-have ERD | Five additional model/training/prediction and ingestion-operation tables |
| D06 User navigation | Landing, dashboard, explorer/detail; comparison modal; mission inline evidence/lab; global AI dock |
| D07 Feature/database ownership | Catalog, runs, evidence, scenarios, chat and models support separate feature queries |
| D08 Dashboard | Aggregate catalog and source coverage; conceptual visuals are not measured risk |
| D09 Explorer/comparison | Search/filter/detail, select 2+ studies, compare and CSV; verified runs required for numerical outcomes |
| D10 Mission/gaps | Shared scenario form; topical relevance and six gap dimensions; no safe/unsafe conclusion |
| D11 Global RAG/citations | Retrieve documents/chunks and reviewed claims; validate source links; abstain when evidence absent |
| D12 PSI ingestion/curation | Normalize PSI identity; parse available runs; retain unknowns, units, original sources; human review |
| D13 Claim lifecycle | Review exact wording; reuse canonical claims; CLAIM_SOURCE links include locator and excerpt |
| D14 Predictive readiness | Require verified training data, validated version, applicability domain and uncertainty; otherwise disabled |
| D15 Dependencies | Evidence foundation precedes tags/RAG; reviewed data and model provenance precede prediction |

Frontend sources inspected (paths relative to `../FlameInFreewall_Tourbillion/`):

- `package.json`, `next.config.ts`, `src/types/index.ts`, routing under `src/app/`.
- All four domain fixture files under `src/data/`: investigations, runs, claims and presets.
- `src/lib/`: explorer filters, comparison utilities/CSV, ranking engine, gap matrix,
  combustion math, predictive readiness, RAG knowledge engine and synthesis interfaces.
- Workspace/assistant Zustand stores; dashboard KPI/domain components; explorer/detail and
  comparison consumers; mission form/evidence/prediction panels; assistant drawer/citation UI.
- Relevant Vitest tests for dashboard, explorer/detail, comparison, mission, gap/ranking,
  assistant and combustion math; the frontend design specification and documentation inventory.

The actual frontend uses **Next.js 15 App Router, React 19, TypeScript, Zustand, Tailwind 4,
Framer Motion and Vitest**. D01/D02's React/Vite SPA labels are outdated. The frontend design
spec chooses a static offline presentation; that is not the new backend's ingestion policy.
No remote frontend page or scientific source was used to establish data authenticity.

## B. Finalized ERD inventory

The following is a transcription of D03-D05, not an implemented schema. Repeated context
entities in D04/D05 refer to D03 entities; they are not additional tables. Type names, PK/FK/UK
annotations and the two explicit nullable notes are preserved. Physical SQL types, lengths,
decimal precision/scale, most nullability, defaults, indexes, deletion policies, enum values,
and composite uniqueness are **not specified** and must be settled before Phase 2 migrations.

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

## C. Current frontend modules and behavior

| Page / surface | Current data and behavior |
| --- | --- |
| `/` | Static landing sections and conceptual flame/atmosphere illustrations |
| `/dashboard` | Fixture-based study/run/claim totals, curated studies, fuel/facility breakdown, planetary presets; hardcoded `10,000+` data points and gravity coverage text |
| `/explorer` | Local keyword search over code/title/subtitle/PI/institution/materials/tags; fuel, facility and gravity filters; newest/code/run-count/confidence sorts; grid/table display |
| `/explorer/[id]` | Slug-based study lookup; static params from fixtures; overview, runs, telemetry, claims and PSI export tabs |
| Comparison modal | 2-3 selected investigations; local averages/ranges/deltas/highlights and CSV export; not a separate route |
| `/mission?view=evidence` | Shared numeric scenario form, presets, topical ranked investigations, closest run, six-dimension gap matrix |
| `/mission?view=prediction` | Same scenario state; local deterministic readiness and spread estimate; not a validated backend model |
| Global assistant overlay | In-memory messages and optional study context; delayed local canned/keyword synthesis with citation popovers; no real model call |

Fixtures contain 20 investigations, 160 run objects and 45 claim objects. Their fields may say
`Verified`, `Measured` or `Peer-Reviewed`, but those labels are not proof. NASA PSI IDs, DOIs,
URLs, videos and numerical findings require independent source validation before ingestion.
`TestRun.dataStatus` distinguishes Verified/Preliminary/Simulated in TypeScript, while evidence
badges are Measured/Modeled/Illustrative and confidence is A/B. These are different concepts.

Local algorithms currently include:

- `rankingEngine.ts`: weighted gravity/material/O2/pressure/airflow similarity (weights
  1.0/1.5/1.0/0.8/0.8), catalog-range distances, string material matching, deterministic code
  tiebreak; closest run uses O2/pressure/flow distance, omitting gravity/material in that step.
- `gapMatrixEngine.ts`: hardcoded domain thresholds/material vocabulary and six statuses;
  partial-gravity threshold is `0.01 < g < 0.98`, narrower than displayed `0 < g < 1`.
  Matched-run count checks gravity/material/O2 only, omitting pressure/flow and validation status.
- `comparisonUtils.ts`: metrics include all fixture runs; verified-run count falls back to
  declared catalog run count when zero verified runs exist. This can overstate validation.
- `TelemetryPane.tsx`: reads embedded telemetry, otherwise constructs smooth sine-based
  temperature/radius/soot curves with default values. Such fallback curves are simulated.
- `combustionMath.ts`: hand-set material constants and deterministic shape, soot, temperature,
  spread and partial-pressure calculations; these are demo logic, not validated science.
- `predictiveLabEngine.ts`: hardcoded model label `NASA-PSI-SPM v2.4` and fixed +/-14% bounds;
  checks permit 7-16 psia while displayed domain says 8.2-14.7 psia. Validation artifacts are absent.
- `ragKnowledgeEngine.ts` / `ragSyntheses.ts`: topic routing, canned prose, keyword scores,
  investigation/claim fixture citations and propulsion scope guardrail; no document chunks,
  embeddings, citation validation against originals, provider call or durable chat storage.

Frontend tests document expected UI behavior (including 20/160/45 totals, gap warnings, ranking
stability, CSV and prediction locks). They do not establish scientific correctness. They were
inspected, not rerun or modified as part of this backend-only phase.

## D. Data flow and scientific integrity

Current flow: static TypeScript fixtures -> local filtering/aggregation/scoring -> Zustand
scenario/comparison/chat state -> React views and browser downloads. The inspected `src/`
contains no business API fetch/axios integration. Assistant latency and explorer loading are
simulated with timers.

Planned flow: PSI/source discovery -> retain originals and URLs -> normalize identifiers and
run conditions with units -> review source linkage and unknowns -> approved PostgreSQL entities
-> repository queries -> services -> versioned API DTOs -> frontend adapters. RAG later reads
source-linked chunks/reviewed claims, validates citations, and stores messages/source locators.

Claims must retain all source associations, exact source locator/excerpt, experimental context,
DOI when available, uncertainty and limitations. An evidence-backed finding in one run does
not establish safety in another mission scenario. Future APIs must distinguish source-backed
verified data, preliminary findings, simulated/demo content and unsupported conclusions.
Do not infer these states from an A/B tier or a publication-looking DOI. Missing measurements
and conditions remain null/unknown, rather than defaulting to zero or a nominal atmosphere.
Combined coverage requires compatible conditions within the same relevant run, not separate
catalog min/max ranges taken across unrelated runs. Research matching scores are relevance,
never probabilities of fire or operational risk ratings.

## E. Preliminary API contract proposal (not implemented)

All paths below are under `/api/v1`. Proposed JSON uses camelCase to fit TypeScript interfaces;
ORM attributes remain independent. An explicit frontend adapter is still required for identity,
nullability and multi-source evidence. Version and finalize DTOs before implementing endpoints.
Lists use `{items, total, offset, limit}` with proposed defaults offset 0, limit 20, max 100;
unknown filters/identifiers produce validation/404 errors rather than silent substitutions.

| Frontend surface | Proposed endpoint | Inputs | Response / UI types | ERD entities | Priority |
| --- | --- | --- | --- | --- | --- |
| Dashboard | `GET /dashboard/summary` | Optional validated catalog filters | `{investigationCount, runCount, verifiedRunCount, claimCount, sourceCoverage, fuelDistribution, facilityDistribution, featuredInvestigations, caveats}`; counts only from curated data | INVESTIGATION, TEST_RUN, TEST_CONDITION, SOURCE_DOCUMENT, EVIDENCE_CLAIM, CLAIM_SOURCE, TAG | Phase 4 |
| Explorer | `GET /investigations` | `q`, `fuel=solid|droplet|gas`, `facility=CIR|MSG|Cygnus`, `gravity=0g|1g|partial`, `sort=newest|code-asc|runs-desc|confidence`, offset/limit; future purpose/source/evidence filters | Paginated Investigation DTOs and available facets; metadata-dependent filters pending resolution | INVESTIGATION, TAG, INVESTIGATION_TAG, TEST_RUN, TEST_CONDITION, SOURCE_DOCUMENT | Phase 4 |
| Detail | `GET /investigations/{uuid}` | Canonical UUID | Investigation DTO, completeness/caveats; 404 if unknown | INVESTIGATION, TEST_RUN, TEST_CONDITION, SOURCE_DOCUMENT, CLAIM_SOURCE | Phase 4 |
| Existing public detail URLs | `GET /investigations/by-slug/{slug}` | Explicit public slug | Same DTO with distinct UUID, slug and psiId; mapping policy requires decision | INVESTIGATION plus reviewed identity mapping | Phase 4 |
| Runs tab | `GET /investigations/{uuid}/runs` | Pagination; optional validated status/material | TestRun DTOs with conditions/measurements, units, provenance and missing-data status | TEST_RUN, TEST_CONDITION, MEASUREMENT; validation linkage unresolved | Phase 4 |
| Telemetry tab | `GET /runs/{uuid}/telemetry` | Optional time range/channel list and bounded/downsampled point limit | `{runId, series, units, rawAssetRef, dataStatus, provenance, caveats}`; series fits TelemetryDataPoint when actual channels exist | MEASUREMENT.raw_asset_ref, TEST_RUN; time-series metadata unresolved | Phase 4 |
| Claims tab | `GET /investigations/{uuid}/claims` | Pagination; optional category/review filter once vocabulary approved | Canonical claim DTOs with `sources[]` (document, locator, excerpt, optional run); no loss of associations | EVIDENCE_CLAIM, CLAIM_SOURCE, SOURCE_DOCUMENT, TEST_RUN | Phase 4 |
| PSI/export tab | `GET /investigations/{uuid}/sources` | Pagination | Original source URLs, DOI, document type/version/status; browser JSON/CSV export can remain local over API DTOs | SOURCE_DOCUMENT, INVESTIGATION | Phase 4 |
| Comparison modal | `POST /compare` | `{investigationIds: UUID[2..3]}` distinct; explicit measurement/status filters | `{studies, metrics, deltas, highlights, caveats}` following comparisonUtils type shapes; separate verified/unknown counts and compatible-unit/context summaries | INVESTIGATION, TEST_RUN, TEST_CONDITION, MEASUREMENT, SOURCE_DOCUMENT, CLAIM_SOURCE | Phase 4 |
| Mission form | `GET /scenario-presets` (optional) | None | Reviewed or explicitly illustrative ScenarioPreset DTOs; UI-only presets may stay local | SCENARIO if persisted; no preset table approved | Phase 5 |
| Mission evidence | `POST /scenarios/analyze` | `{scenario: ScenarioInput}`; optional reviewed ranking configuration later | `{scenarioId, rankings: RankedInvestigation[], gapMatrix: GapMatrixResult, engineVersion, provenance, caveats}`; run-level match details retained | SCENARIO, SCENARIO_MATCH, MATCH_DIMENSION, TEST_RUN, TEST_CONDITION, CLAIM_SOURCE, SOURCE_DOCUMENT | Phase 5 |
| Global assistant | `POST /ask` | `{question, sessionId?, investigationId?}` with length/context limits | `{sessionId, message: ChatMessage, suggestedQuestions, isOutOfScope?, provenance}`; citations carry source document/URL/locator plus optional claim/run context | CHAT_SESSION, CHAT_MESSAGE, MESSAGE_CITATION, DOCUMENT_CHUNK, SOURCE_DOCUMENT, CLAIM_SOURCE, EVIDENCE_CLAIM | Phase 6 |
| Lab inline panel | Future readiness endpoint only after validation design | ScenarioInput | PredictiveLabAudit plus artifact provenance; blocked when prerequisites absent; no prediction route in Phase 1 | MODEL_VERSION, MODEL_TRAINING_RUN, PREDICTION_RESULT, SCENARIO | Phase 7 |

Contract mapping details:

- **Investigation DTO:** preserve code/title/researchPurpose/platform and nested UI fields
  (`fuelDetails`, ranges, variables, findings, dataAvailability, sources, tags) where backed
  by reviewed data. Add canonical `id: UUID`, `slug: string`, `psiId: string`. The current
  frontend uses `id` as a slug, so its adapter must provide `id = dto.slug` for existing routes
  and carry `dto.id` separately for API calls. A versioned API can make this explicit without
  rewriting database identity. Slug and most display metadata have no approved storage yet.
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
  description. Current form ranges: g 0-1, O2 15-40, pressure 7-16, airflow 0-50; these are UI
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
  applicable. Streaming/session history endpoints are separate future decisions, not required
  by the currently simulated streaming indicator.
- **Nullability:** current required TypeScript fields exceed available schema and data. Extend
  the frontend adapter/types to support unknowns when integrating; do not manufacture PI names,
  ranges, geometry, findings, confidence tiers or source titles. Decimal-to-JSON conversion needs
  an explicit precision policy; UI numeric values must not silently round scientific originals.

## F. Inconsistencies and decisions needed before later phases

| Issue | Evidence / impact | Proposed resolution requiring agreement where schema changes are involved |
| --- | --- | --- |
| Framework labels | D01/D02 say Vite; package/config/routes use Next.js | Treat actual code as UI behavior reference; update diagrams only if requested |
| Missing linked diagram files | All 15 `.mmd` download targets are absent | Embedded Mermaid is available; restore download assets separately only if requested |
| Physical schema unspecified | ERD has generic string/decimal/datetime; few nullability/constraint details | Agree types, precision, timezone, nullable fields, uniqueness, FK deletion rules and indexes before migrations |
| Slug vs UUID vs PSI ID | Frontend `bass`, DB id UUID, psi_id unique; no slug column | Reviewed explicit mapping/registry or approved slug column; never derive persistent slugs from mutable titles without a collision policy |
| Rich catalog metadata | No ERD PI/institution/hardware/year/fuel category/findings/citation title/authors columns | Derive only supportable aggregates/tags; agree source metadata storage or schema extension; support unknown fields |
| Numeric scenario fields | SCENARIO.gravity/ventilation and TEST_RUN.gravity are strings | Agree a reversible canonical text/unit encoding or request numeric/unit schema changes; no ad-hoc coercion implemented |
| Flat claims vs N:N provenance | UI claim has one investigation, optional run and singular DOI/locator | Query through CLAIM_SOURCE; preserve sources[] and review scope; no relationship flattening |
| Claim categories/context/publication metadata | UI scientificContext/category/authors/year absent from claim/document ERD | Review explicit metadata strategy; don't equate publication type with curation status |
| Telemetry storage | MEASUREMENT holds scalar value/unit/raw_asset_ref/uncertainty; no timestamp/channel-series schema | Retain originals as assets, parse bounded validated series for API; agree asset manifest/time metadata and boolean observation encoding |
| Validation/provenance coverage | data_status exists on TEST_CONDITION, not TEST_RUN/MEASUREMENT; no measurement-source FK | Define auditable validation/provenance policy or seek approved additions before asserting run/measurement verification |
| Match aggregation | DB matches runs, frontend ranks investigations and shows richer dimension values | Persist per-run matches; deterministic aggregation; compute display values without adding unapproved columns |
| Citation richness | MESSAGE_CITATION references documents, not chunks/claims; UI citations show claims | Preserve document+locator traceability; approve richer linkage if durable claim/chunk identity is required |
| Demo verified counts | Comparison fallback counts catalog runs as verified; outcome means include all runs | Count actual validated runs; filter compatible observations; return null for unavailable outcomes |
| Hardcoded scientific claims | Fixtures/spec label sources/model as verified; artifacts not validated | No seeding as verified research. Curator validation with original records and artifacts in Phases 3/7 |
| Gap threshold/count mismatch | Display 0<g<1 vs implemented 0.01<g<0.98; count omits pressure/flow/status | Define evidence-backed matching tolerances and same-run combined coverage; never claim a universal NASA data absence from local catalog coverage |
| Predictive mismatch | Fixed model/version/interval; domain text differs from code | Keep backend prediction absent; require real model training, validation metrics and domain checks in Phase 7 |
| Dashboard filter handoff | DomainBreakdown updates workspace filter, Explorer uses separate local filter state | Agree a future shared state/query adapter; frontend unchanged here |
| UI navigation vs diagram tabs | D09 lists Overview/Conditions/Evidence, actual detail has five tabs | API supports actual consumers; no forced route/tab redesign |

No ambiguity above blocks a model-free Phase 1. They must not be resolved by silently changing
the approved ERD or by duplicating static frontend fixtures in PostgreSQL.

## G. Backend phases and responsibilities

1. **Foundation (implemented here):** Poetry, configuration, FastAPI lifespan, health/readiness,
   explicit CORS, async engine/session dependency, declarative base, Alembic, Compose and tests.
2. **Approved ERD and migrations:** settle physical schema and identity/unit/provenance questions,
   implement the 21-table design by agreed priority, review migrations and relationship tests.
3. **Scientific ingestion/source validation:** retain originals, deduplicate PSI records, normalize
   units without losing originals, curate source associations, preserve unknowns and validation state.
4. **Catalog APIs:** dashboard, explorer, detail/run/source/telemetry and comparison read contracts;
   response adapter/nullability agreement and scientifically compatible aggregation.
5. **Scenario evidence:** validated inputs, reproducible run-level matching, versioned relevance,
   same-run condition coverage and transparent evidence gaps; no operational safety decisions.
6. **Grounded assistant:** document/chunk retrieval, reviewed claim provenance, citation checking,
   abstention, context/session/message persistence and source-supported/inference/gap labels.
7. **Predictive Lab:** only after datasets, artifacts, model versions, validation, applicability and
   uncertainty are demonstrably available. Demo equations are not training/validation evidence.
8. **Deployment/monitoring/integration:** HTTPS backend, secret management, environment-specific
   origins, authentication/rate limits as needed, deployment migrations, monitoring and frontend URL.

Routes will delegate business decisions to services and persistence queries to repositories.
Integration adapters will own NASA/provider access; ingestion will own parsing and curation.
Those packages should be added with real functionality, not unused Phase 1 placeholders.
No message broker, Celery, microservice, RAG framework or prediction code is needed now.

## Phase 1 architecture decisions

The app factory accepts settings for dependency-isolated testing. Lifespan initializes a lazy
engine and disposes it on shutdown; a database outage does not block liveness/docs. Readiness
uses a bounded SELECT 1. Async sessions close through a request dependency with no implicit
commit. SQL echo is disabled, parameters are hidden, and readiness/general error responses
are sanitized. Production debug is rejected. CORS permits explicit origins only.

SQLAlchemy metadata is empty and Alembic has no revisions. The local database runs alone in
Docker with persistent storage and conservative resources. Poetry owns `.venv/`, runtime and
dev groups, with a generated lockfile. No science data or business endpoints were implemented.
See [verification results](phase-1-verification.md) for actual checks and environment blockers.
