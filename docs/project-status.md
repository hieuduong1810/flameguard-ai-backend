# Current project status — FlameGuard AI Backend

Snapshot date: **2026-11-10**. Evidence source: user-supplied backend/frontend
archive and existing phase reports. This file is a **handoff status index**,
not a substitute for a Git diff, live API check or independent database audit.

## Delivery status

| Phase | Scope | Status and evidence | Owner / next step |
| --- | --- | --- | --- |
| 1 | FastAPI/Poetry/Postgres/Alembic foundation | **Reported complete** in `phase-1-verification.md` | Backend; preserve |
| 2 | 21 ERD entities, typed schemas, repositories, 3 Alembic migrations | **Reported complete** in `phase-2-database-implementation.md` (228 tests passed with isolated PostgreSQL) | Backend; preserve |
| 3A | NASA acquisition, scientific curation and import | **External handoff pending**, not implemented in the submitted backend | Data team |
| 3B | Data contracts, compatibility checks and acceptance | **Needs agreement**, may be developed alongside API contract tests | Backend + Data |
| 4 | Dashboard, Explorer, Detail, Comparison APIs | **Not implemented**; current API only exposes `/api/v1/health` and `/api/v1/ready` | Backend, coordinate Frontend |
| 5 | Run-level scenario matching and evidence gaps | **Not implemented** in backend | Backend + Data |
| 6 | Grounded assistant/RAG | **Not implemented** in backend; frontend has offline demo text generation | AI + Backend + Frontend |
| 7 | Predictive Lab | **Not implemented** in backend; frontend demo logic is not model certification | AI + Backend + Data |
| 8 | Deployment and FE integration | **Not implemented** for backend in the provided snapshot | Backend + Frontend |

The Phase 3 ownership split is recorded in `docs/decisions/ADR-0001-phase3-ownership.md`.
Do not mark Phase 3 complete solely because ORM tables exist. Do not mark a later
phase complete based on mock UI screenshots or unexecuted tests.

## Current technical snapshot (archive inspection)

- Backend: FastAPI modular monolith using Poetry/Python, SQLAlchemy async and Alembic.
- ORM: 21 models across Must/Should/Could groups; migration revisions
  `0001_must_have`, `0002_should_have`, `0003_could_have`.
- Current HTTP endpoints: liveness and database readiness only.
- Frontend (sibling repo): Next.js app uses static `src/data/*.ts`, local TypeScript
  ranking/gap/predictive/RAG demo engines and an in-memory Zustand chat store.
  No active network API adapter was found in the inspected frontend snapshot.
- The frontend's study route IDs are slugs, not database UUIDs or `psi_id`.
- Existing backend reports record a working Windows native development DB and
  isolated Docker test DB. The archive **does not include live database state**.

## Gates before the next business implementation

1. Agree on the Data team handoff fields and source-review meaning in
   `docs/contracts/data-handoff.md`.
2. Agree on the public API identity/slug and missing-data mapping in
   `docs/contracts/frontend-backend-api.md`.
3. Specify the next **small Phase 4 vertical slice** (catalog list/detail first
   is a reasonable candidate) using Spec Kit, with HTTPX contract tests and
   synthetic fixture rows only.
4. Give the Frontend team the same approved DTO contract; do not modify its
   repository as part of backend-only work.
5. Obtain AI team contracts and verified model/data prerequisites before
   exposing RAG or predictive results as validated scientific outputs.

## Known risks and caveats

- Frontend demo includes scientific-looking statements, numerical intervals and
  model names. None are promoted to verified backend facts without source review.
- `docs/diagram/index.html` is the approved ERD; a similarly named frontend HTML file
  has different content/hash and is **not** the backend schema authority.
- Existing tests parse approved nullability from the Phase 2 Markdown report.
  Preserve its path/content structure until a separately approved contract
  refactor updates those tests.
- The exported ZIP intentionally omitted `.env*`, including `.env.example`.
  Confirm its existence and sanitized values in the live repo when needed.
- Reported test results from Phase 1–2 were **not rerun** on the user's live
  Windows/Postgres environment by this handoff work.

## Update rule

On completion of a **reviewed** feature, update only its row, acceptance state,
known blockers and relevant phase record. Do not invent completion, change the
historical test counts, or rewrite architecture history.
