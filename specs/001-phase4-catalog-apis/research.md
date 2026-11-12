# Planning Research and Decisions

Date: 2026-11-11. Repository-based research; no new library/version or scientific claim is proposed.

| Topic | Decision and rationale | Alternatives rejected |
| --- | --- | --- |
| Existing architecture | Reuse app/main.py, api/v1/router.py, core/database.py and repositories. Existing schemas explicitly describe scalar persistence, so add separate public DTOs/services. | Reinitializing FastAPI, replacing Poetry or introducing a generic repository framework adds unrequested risk. |
| Public reads | Add bounded read methods. Current get_investigation/list_test_runs eagerly load unbounded children. Preserve old methods for Phase 2 compatibility. | Exposing ORM graphs causes unbounded data and lazy-loading/serialization failures. |
| Identity | File manifest slug → psi_id → current UUID, with owner-reviewed collision/lifecycle policy, as selected by user. | New schema fields and title-derived permanent slugs contradict the approved choice. |
| Rich mock metadata | Explicit unavailable fields and unsupported filters/sorts. Frontend uses hardware, fuelType, code, yearRange and confidence without stored equivalents. | Guessing classifications or copying frontend mocks invents data. |
| Decimals/provenance | Original numeric values/uncertainty are decimal strings; preserve association UUID/document/locator/excerpt/run context. | Float-only numbers, singular DOI and fictional measurement-source FK lose data. |
| Queries/snapshots | EXISTS, same-run predicates, distinct IDs before paging, bounded loading and REPEATABLE READ READ ONLY service scope. | Joined pagination inflates totals; separate default snapshots can disagree during imports; per-row queries create N+1. |
| Scientific comparison | Original observation display; unknown verified counts and disabled derived metrics. Equal unit strings do not establish scientific compatibility. | Frontend fallback counts, arbitrary run pooling and invented unit/verification algorithms violate user choices and D09. |
| Origin | Collection manifest and exact fixture membership/content checks, separate from recorded review strings. No is_synthetic/status column is invented. | Prefixes/status labels alone cannot establish collection integrity; no marker table allowed. |
| Seed admission | Dedicated URL, explicit opt-in, independent ignored target authorization, role/ownership/OID/schema checks and all-table content checks. | Settings defaults to development and reads .env, so environment/name/localhost alone cannot authorize a safe target. |
| Atomic seed | Fixed manifest identities, bounded write-conflicting locks and insert-only transaction. Identical rerun is no-op; drift/foreign rows abort. | Broad UPSERT, silent conflict skip, auto-reset or advisory locking alone cannot protect existing scientific data. |
| Evidence | Separate unit/HTTPX, real PostgreSQL, CLI and generated OpenAPI checks; static checks only during planning. | Mock success is not database/scientific proof; generated tests are not executed verification. |

Read-only seed research additionally reviewed Settings, approved catalog/evidence models and tests/postgres_fixtures.py. The latter creates suffixed isolated test DBs, applies existing migrations and retains them; that provisioning behavior must not be embedded in seed_demo_data.py.

All necessary technical design choices have explicit defaults. External Frontend examples, Data vocabulary/curated manifests, verification rules and telemetry contracts remain acceptance dependencies with specified unavailable behavior. The Plan invocation authorizes design despite the historical Specify stop statement, but grants no implementation permission.
