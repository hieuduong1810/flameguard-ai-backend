# Current project status — FlameGuard AI Backend

Updated **2026-11-14** from the current API source, task ledgers and recorded
phase verification. Test counts below refer to their original execution dates.
Frontend archive observations date from **2026-11-10**. Current Frontend and
official-dataset acceptance require their owners' evidence.

## Delivery status

| Phase | Scope | Status and evidence | Owner / next step |
| --- | --- | --- | --- |
| 1 | FastAPI/Poetry/Postgres/Alembic foundation | **Reported complete** in `phase-1-verification.md` | Backend; preserve |
| 2 | 21 ERD entities, typed schemas, repositories, 3 Alembic migrations | **Reported complete** in `phase-2-database-implementation.md` (228 tests passed with isolated PostgreSQL) | Backend; preserve |
| 3A | NASA acquisition, scientific curation and import | **Data Team ownership, backend integration acceptance pending** | Data team + Backend handoff |
| 3B | Data contracts, compatibility checks and acceptance | **Compatibility audit and dependency register available**. Official dataset, publication and mapping acceptance pending | Backend + Data. See [integration dependencies](roadmap/data-integration-pending.md) |
| 4 | Dashboard, Explorer, Detail, Comparison APIs | **Executable convergence fixes through T084 verified 2026-11-12**; 441 tests passed, including 185 PostgreSQL integration tests; see `phase-4-api-verification.md` | T078 Frontend acceptance blocked; Data curated/scientific gates pending; fresh Converge review required |
| 5 | Run-level scenario matching, rankings and pillar evidence | **Backend engineering verified 2026-11-12** for P5-01–P5-06. 551 tests passed, including 197 isolated PostgreSQL integration tests. See `phase-5-scenario-evidence-verification.md`. | T056–T060 Data/Frontend acceptance pending. T061/P5-07 deferred. T062 scenario-history writer pending, chat foundation accepted in Phase 6. |
| 6 | Persistent demo chat and structured Advisor | **Backend/mock engineering and audit follow-up verified 2026-11-13**. Full suite 572 passed, PostgreSQL integration 210 passed, zero skips. See [Phase 6 verification](phase-6-chat-advisor-verification.md). | Real AI/Data evaluation and Frontend acceptance pending. Chat-only T062 boundary accepted in ADR-0004. |
| 7 | Stateless Predictive Lab backend | **Backend engineering converged 2026-11-13** for P7-01–P7-06. Full suite 650 passed, isolated PostgreSQL 223 passed, zero skips. See [Phase 7 verification](phase-7-prediction-verification.md). | T013 AI/Data and T014 Frontend acceptance pending. Public scientific readiness remains not_ready. |
| 8 | Deployment and FE integration | **Pending implementation and acceptance** | Backend + Frontend |

The Phase 3 ownership split is recorded in `docs/decisions/ADR-0001-phase3-ownership.md`.
Do not mark Phase 3 complete solely because ORM tables exist. Do not mark a later
phase complete based on mock UI screenshots or unexecuted tests.

## Current backend implementation

- Backend: FastAPI modular monolith using Poetry/Python, SQLAlchemy async and Alembic.
- ORM: 21 models across Must/Should/Could groups; migration revisions
  `0001_must_have`, `0002_should_have`, `0003_could_have`.
- APIs include health/readiness, catalog/filter/search, investigation details,
  runs/conditions/measurements, source documents and claims, dashboard and basic
  comparison. Phase 5 adds POST `/api/v1/mission/scenarios/evaluate`.
- Phase 6 adds persistent demo chat sessions/messages and
  POST `/api/v1/advisor/assessments`, bounded session history and citation checks.
- Phase 7 adds GET `/api/v1/prediction/readiness` and POST `/api/v1/predictions`.
  Execution uses the approved stateless scope. Current scientific gates return
  `not_ready` for unreviewed data and unvalidated/unavailable providers.
- Scientific collection admission supports exact v1 snapshots and the approved
  v2 chat boundary. The separate runtime role has INSERT access to the three chat
  tables. See [ADR-0004](decisions/ADR-0004-runtime-chat-boundary.md).
- Provider boundaries support unavailable and explicitly synthetic mock engines.
  Real ranking, RAG and prediction activation depend on external acceptance.
- Internal UUIDs, PSI identifiers and public slugs retain distinct identities.
- Latest recorded regression is the Phase 7 run on **2026-11-13**, with **650
  passed**, including **223 PostgreSQL integration tests**, zero failures/skips.
  See [Phase 7 verification](phase-7-prediction-verification.md).

## Outstanding acceptance and next work

| Area | Pending work | Evidence / owner |
| --- | --- | --- |
| Phase 3B | Assess the official dataset on arrival, accept identities, units, quality flags, source provenance, lossless mapping and publication rules | [Compatibility audit](references/data-backend-compatibility-audit-2026-11-12.md), [dependency register](roadmap/data-integration-pending.md). Backend + Data |
| Phase 4 | T078 Frontend acceptance and recorded follow-up review disposition | [Phase 4 verification](phase-4-api-verification.md). Frontend + Backend |
| Phase 5 | T056–T059 Data/scientific/ranking acceptance, T060 Frontend acceptance, T062 scenario-history writer decision | [Phase 5 handoff](../specs/phase5-backend/handoff.md). Data + Frontend + Backend owner |
| Phase 5 optional enrichment | T061/P5-07 remains deferred | Data + Frontend |
| Phase 6 | T018 reviewed corpus/real AI provider evaluation and T019 Frontend API/privacy acceptance | [Phase 6 handoff](../specs/phase6-rag-advisor/handoff.md). AI + Data + Frontend |
| Phase 7 | T013 validated model/provider/data acceptance and T014 Frontend acceptance | [Prediction handoff](contracts/phase-7-prediction-handoff.md). AI + Data + Frontend |
| Phase 8 | Integration, deployment and end-to-end acceptance under its own approved scope | Backend + Frontend |

No official-dataset receipt or acceptance evidence has been recorded in these
phase reports. Its expected arrival date alone cannot close the Data/AI gates.

## Known risks and caveats

- Frontend demo includes scientific-looking statements, numerical intervals and
  model names. None are promoted to verified backend facts without source review.
- `docs/diagram/index.html` records the current 21-table ERD baseline.
  [ADR-0003](decisions/ADR-0003-schema-evolution-and-hackathon-prototype.md)
  governs justified schema evolution after source-data and impact review.
- Existing tests parse approved nullability from the Phase 2 Markdown report.
  Preserve its path/content structure until a separately approved contract
  refactor updates those tests.
- Runtime chat is approved for public-demo session continuity with a 24-hour
  session lifetime. Consumer privacy/retry acceptance remains with Frontend.
- Scientific publication requires accepted source review, model/domain and
  uncertainty evidence. Backend/mock engineering completion is tracked separately
  from real-data and scientific acceptance.

## Historical archive observations — 2026-11-10

The initial archive contained a health-only backend snapshot and a Next.js
frontend with static data and local ranking/gap/predictive/RAG demo engines.
The Frontend observations have not been reassessed by this status update.
The archive omitted local environment files and live database state. Subsequent
backend implementation and verification are recorded in the delivery table above.

## Historical Phase 4 milestone — 2026-11-11 through 2026-11-12

The archive snapshot above is historical context. The live backend now implements the scoped synthetic Phase 4 read APIs and explicit isolated seed CLI described in `phase-4-api-verification.md`. Source/claim provenance, exact observation values, separate IDs and unknown verification are retained. Runtime OpenAPI and real isolated PostgreSQL tests are recorded in `../specs/001-phase4-catalog-apis/verification.md`.

The initial implementation admitted synthetic-only collections. The 2026-11-12 remediation now also admits explicitly bound empty real/unknown collections and exact owner-declared non-curated stored-field snapshots, preserving unknown origin/review and raw statuses. Synthetic membership, mixed-origin refusal and SELECT-only snapshot checks remain enforced; curated publication still awaits Data acceptance.

The first user-invoked Converge found eight follow-ups. The next review added
T083–T084 for canonical duplicate UUID rejection and accurate comparison label
warnings. Executable tasks through T084 were verified with 441 passing tests.
T078 still requires Frontend reviewer/date/scope evidence, and the Phase 4 record
lists a fresh review as pending. This milestone covers the Phase 4 read API scope.
Later scenario matching, chat/Advisor and stateless prediction engineering are
recorded under Phases 5–7 above.

## Update rule

On completion of a **reviewed** feature, update only its row, acceptance state,
known blockers and relevant phase record. Do not invent completion, change the
historical test counts, or rewrite architecture history.
