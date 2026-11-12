# Implementation Plan: Phase 4 Catalog and Evidence APIs

**Branch**: actual Git branch `main`; resolver label `001-phase4-catalog-apis` is not a created branch.
**Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**Status**: Technical proposal for review. Planning authorization is not implementation, data-write, commit or cross-team acceptance authorization.

## Summary

Extend the existing backend through Router → Service → Repository → PostgreSQL. Deliver six read-only vertical slices plus an independently testable synthetic bootstrap CLI. Preserve all 21 tables, migrations 0001–0003 and Phase 1–2 behavior. Public DTOs remain separate from existing persistence schemas.

Retain the selected policies: separate slug manifest; unavailable/unsupported unmapped frontend fields; unknown verification and contextual original observations without derived scientific outcomes. No ETL, AI, full telemetry, frontend changes or deployment.

## Technical Context

**Language/Version**: Python >=3.12,<3.14, following pyproject.toml.
**Primary Dependencies**: Existing FastAPI, SQLAlchemy 2.x async, asyncpg, Alembic, Pydantic v2. Poetry remains authoritative; no new dependency currently required.
**Storage**: Existing PostgreSQL schema. Identity/fixture manifests are files; no new tables, migrations or create_all.
**Testing**: pytest/pytest-asyncio, HTTPX with lifespan, isolated PostgreSQL fixtures, Ruff and Poetry.
**Target Platform**: Existing Windows/local Python development and normal backend runtime; deployment excluded.
**Project Type**: Existing modular-monolith backend; separately owned frontend.
**Performance Goals**: Bounded pages, deterministic ordering and no per-row lazy SQL. Query count for a fixed-size page must not grow per entity. Record timings later; no approved latency/load SLO exists.
**Scale/Scope**: At least four demo investigations; larger deterministic test variants for pagination; default page 20/max 100; six journeys.
**Constraints**: Frozen schema/history, exact Decimal serialization, independent origin/review, existing engine/session lifecycle and no shared database writes.

## Constitution Check

| Gate | Before research | After design |
| --- | --- | --- |
| Scientific integrity/provenance | Pass | Original values/units, every association, unknown verification, no derived outcomes |
| Architecture/async coding | Pass | Existing app/session, service-owned transactions, repository queries, explicit bounded loading |
| Schema/history preservation | Pass | No model, column, FK or migration changes |
| Team boundaries | Pass | Backend owns adapters; Data/Frontend acceptance remains pending; no AI work |
| Contract-first | Pass for planning | Proposed formal schemas/examples provided; consumer approval gates implementation |
| Verification | Pass for docs scope | Static checks now; HTTP/PostgreSQL/OpenAPI evidence required later |
| Poetry/secrets/safe targets | Pass | No manager change; explicit seed URL and independently authorized target |
| Stable docs/honest status | Pass | Only feature artifacts; no Phase 4 completion claim or baseline rewrite |
| Git/workflow/DoD | Pass | Tasks, Analyze, authorized Implement, Test, Converge still required |
| Escalation | Pass | Scientific/consumer gaps have explicit unavailable behavior and named owners |

No exception is proposed. Design feasibility passes; implementation readiness and curated scientific validation are not declared passed.

## Project Structure

### Documentation (this feature)

```text
specs/001-phase4-catalog-apis/
  spec.md                           preserved input
  checklists/requirements.md        preserved input
  plan.md
  research.md
  data-model.md
  contracts/api.md
  contracts/openapi.json
  contracts/seed-demo.md
  contracts/team-handoffs.md
  quickstart.md
```

No tasks.md is generated.

### Source Code (proposed future files/edits only)

```text
app/api/v1/router.py                register routes, preserve health/ready
app/api/v1/endpoints/catalog.py     capabilities/list/detail/slug
app/api/v1/endpoints/runs.py        runs/conditions/measurements
app/api/v1/endpoints/evidence.py    sources/claims/association pages
app/api/v1/endpoints/dashboard.py   summary
app/api/v1/endpoints/comparison.py  read-only POST comparison
app/api/dependencies.py            new service/read-context dependencies
app/services/                     catalog/evidence/dashboard/comparison,
                                  collection and demo_seed services
app/repositories/catalog.py        extend paged read queries
app/repositories/evidence.py       extend provenance reads
app/repositories/dashboard.py      aggregate queries
app/repositories/demo_seed.py      inspection/inserts, no commit
app/schemas/api/                   public DTO/query/error models
app/core/config.py                 explicit collection/manifest settings
app/core/database.py               read-unit-of-work integration if required
data/demo/                        versioned fixture and slug manifests
scripts/seed_demo_data.py           thin operator CLI
tests/unit/                       pure mapping and seed guards
tests/contract/                   HTTPX contracts
tests/integration/                PostgreSQL queries, HTTP and seed safety
```

**Structure Decision**: Reuse app/main.py, api/v1/router.py, get_db_session, CatalogRepository and EvidenceRepository. services/, schemas/api/ and the listed new modules are planned additions, not implemented now. Preserve existing persistence schema names and old repository method behavior; add page-oriented read methods rather than breaking Phase 2 tests.

## Layers, transactions and repository queries

- Router: validate canonical query/body DTOs, invoke one service and declare success/error models. Register static by-slug routes before UUID routes. Reject unknown query keys.
- Service: collection admission, identity, availability/provenance projection, transaction scope and safe error translation. No direct ORM HTTP serialization.
- Repository: parameterized SQLAlchemy queries over an injected AsyncSession; explicit loading; no commit. Never run concurrent SQL tasks on one AsyncSession.
- Read unit of work: begin REPEATABLE READ, READ ONLY before the first query; use one snapshot for count/page/aggregates. Configure isolation before autobegin, not after SQL. Roll back/close reads. Boundary tests use independent read sessions against committed fixtures in an approved disposable database; old rollback-based repository fixtures remain intact.
- Catalog: reusable filtered investigation-ID relation; literal substring search with escaped LIKE wildcards; trimmed case-insensitive equality. Text order uses explicit PostgreSQL C collation then UUID. Tags filter by slug. Material and raw gravity predicates share one TestRun EXISTS; claim evidence/review predicates share one linked claim. Tag/source/claim EXISTS avoids multiplying rows.
- Pagination: count and page the same filtered identity relation. Group run counts in one subquery for runs-desc ordering. Detail loads no unbounded children. Child collections use independent UUID-ordered pages and counts.
- Public investigation tag projections also use bounded first pages and /investigations/{id}/tags traversal; load first tag pages in bulk, not per-row queries or unbounded tag collections.
- Claims: membership through ClaimSource → SourceDocument.investigation_id; select distinct claim IDs before paging. Fetch first bounded association pages with row_number partitioned by claim and per-claim counts; separate endpoint traverses later pages. Do not eagerly load the entire graph or collapse repeated documents.
- Dashboard: select investigations once, separately count their runs/documents/distinct linked claims. Document coverage counts investigations with a source, not verified sources. Tag buckets count distinct investigations; overlapping buckets must not imply percentages sum to 100%.
- Comparison: bulk-read 2–3 IDs, verify existence, restore request order and return paged original observations/run context. No AVG/MAX-selected outcome, automatic conversion, score, ratio or superiority calculation.

## Small vertical slices

Each slice includes DTO → query → service → HTTP/CLI → tests → reviewed handoff example. Do not implement all repositories first and defer all observable behavior to the end.

| Slice | Entry | Deliverables | Verification | Exit / trace |
| --- | --- | --- | --- | --- |
| S0 Synthetic bootstrap | Reviewed plan/fixtures; target separately authorized | Fixture/slug manifest, guard and insert-only service/repository, scripts/seed_demo_data.py | Pure guard tests; PostgreSQL first-run/no-op/drift/rollback/concurrency | Safe reusable CLI; FR-003,024–027 |
| S1 Discovery | Examples accepted; synthetic test context | Capabilities, query DTO, count/page, list service/router | HTTPX invalid/empty/filter/page; PostgreSQL same-run/dedup/order | Explorer with explicit unsupported states; FR-004–009,028 |
| S2 Detail/identity | S1 common contracts; slug examples reviewed | UUID detail, slug resolution, child links/null-aware DTO | UUID/PSI/slug, collision/stale/missing mapping/children | Honest canonical detail; FR-002–005,013 |
| S3 Runs/observations | S2; original value/unit contract accepted | Paged runs, conditions, measurements, contextual observation pages | Exact decimals, zero/null, uncertainty, string gravity/assets; real SQL/HTTP | Inspection without fabricated telemetry; FR-014–016 |
| S4 Source evidence | S2; provenance examples accepted | Source/claim pages and all association traversal | Shared claims, repeated locators, mismatches, orphan claims, multiple pages | Full provenance retrievable; FR-017–020 |
| S5 Dashboard | S1/S4 reusable selection/counts | Summary, coverage, featured entries, unknown verification/distributions | PostgreSQL reconciliation, empty/zero denominator, HTTPX | Counts describe selected collection; FR-010–012 |
| S6 Comparison | S2–S4; observational contract accepted | Ordered 2–3 studies, paged observations, unavailable derivations | Invalid/mixed selection, units/context mismatch, null/zero and scientific gates | No verified numeric conclusion; FR-021–023 |

Every slice also verifies origin labels, sanitized failures and unchanged health/ready. Full completion requires S0–S6, criterion-to-evidence mapping for SC-001–008 and OpenAPI checks; Frontend rollout and Data scientific acceptance remain separate milestones.

## Verification strategy

1. Pure tests: manifests/collisions, aliasing, decimal strings, unavailable rules and safe errors.
2. HTTPX contracts: application lifespan/dependency overrides, exact shape/status, empty and invalid requests, detached origin labels. This does not prove PostgreSQL.
3. Real PostgreSQL queries: reuse existing guards/rollback fixtures, exercise actual UUID/Numeric, EXISTS, dedup, association paging and ordering.
4. Real PostgreSQL HTTP/CLI: separately authorized generated test targets with committed synthetic fixtures and independent read sessions; subprocess seed guard/idempotency/drift/atomicity/concurrency tests. Existing migrations only; no seeder migration. Retain generated DBs; cleanup remains separately authorized.
5. OpenAPI: static contract refs/examples now; later compare generated app.openapi() paths/parameters/required fields/aliases/nullability/decimal strings/errors to contracts/openapi.json. Exercise actual HTTP responses; do not rely only on snapshot equality.
6. Poetry check, Ruff lint/format, relevant pytest then applicable regressions. Record exact commands/counts/skips; missing database permission is blocked evidence, not a pass.
7. Diff review: no models/migrations/frontend/secrets. Update delivery/status records only for genuinely implemented and verified scope.

## Review, rollback and change control

Future settings add CATALOG_COLLECTION_MANIFEST as an explicit file reference for Phase 4, validated against the configured read database identity and allowed read role. Missing/invalid collection configuration makes Phase 4 unavailable; health/ready retain existing behavior. No credential or machine-specific target authorization is versioned.

Review [API](contracts/api.md), [seed safety](contracts/seed-demo.md) and [handoffs](contracts/team-handoffs.md). After review: Tasks → Analyze consistency → explicitly authorized implementation. Use a feature branch for future implementation; this plan does not switch branches, commit, push or merge.

Rollback future code through scoped reverts/route removal; no DB downgrade is needed. The seeder has no reset/delete mode. Disposal of databases or fixture rows requires separate exact-target approval. Preserve published slug mappings or review compatibility before retirement.

## Complexity Tracking

No Constitution violation or new framework is requested. Collection manifests and the read unit of work address origin/snapshot correctness; they do not form a generic data platform or replacement ETL.
