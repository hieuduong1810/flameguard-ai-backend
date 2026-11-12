# Phase 4 Future Validation Guide

Status: implemented synthetic backend validation guide. The original planning run executed no database commands; implementation has now verified these endpoints/seed behavior on isolated PostgreSQL. See [execution evidence](verification.md) for exact current results and [the operator runbook](../../docs/runbooks/phase-4-demo-validation.md) for safe target setup. Frontend/Data scientific acceptance remains pending.

## Prerequisites and target approval

Use the existing Poetry environment and Python range. Review [API](contracts/api.md), [seed](contracts/seed-demo.md) and [handoffs](contracts/team-handoffs.md). Obtain separate approval for an exact disposable target and restricted roles. Seed URL, read-only API URL and local authorization stay outside Git. Never point these examples at the normal flameguard development DB, a shared DB or production.

Schema provisioning is a separately approved operation using only existing migrations. The seed script must refuse an unmigrated target, not migrate it. No Docker startup or database creation is part of this plan.

## Baseline checks (when implementation is authorized)

```powershell
poetry check
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -q
```

With no TEST_DATABASE_URL, PostgreSQL cases skip. Report exact counts/skips; do not claim a real DB pass. Windows pytest temporary paths may need a unique writable --basetemp; never reuse/delete an unverified computed directory.

## Explicit synthetic setup (after implementation)

Set APP_ENV=test and DEMO_DATABASE_URL locally to the separately authorized target; provide .tools/demo-target.json as defined in the seed contract. The script has no DATABASE_URL fallback.

```powershell
poetry run python scripts/seed_demo_data.py --allow-synthetic --confirm-database flameguard_demo_phase4 --target-authorization .tools/demo-target.json
```

Expected: exit 0, exact manifest counts and non-NASA labels. Repeat unchanged: exit 0, zero inserted. In approved isolated tests, alter fixture content or add an unrelated sentinel: the command must refuse without overwriting/deleting any data. Do not perform that mutation in a shared or real collection.

Set the future CATALOG_COLLECTION_MANIFEST locally to the reviewed collection file, bind it to the same admitted database identity and allowed read role, and use that dedicated read-only role for DATABASE_URL. Then start the existing app:

```powershell
poetry run uvicorn app.main:app --reload
```

No endpoint starts seeding or migrating.

## Researcher journeys to verify through HTTP

1. GET /api/v1/catalog/capabilities and /api/v1/investigations?limit=2; traverse next links and reconcile total/membership. Unsupported sort=confidence returns safe 422.
2. Read known UUID and manifest slug; UUID/PSI/slug remain distinct. Missing identity is 404, stale manifest is safe 503, known empty children are 200/empty.
3. Traverse run/condition/measurement pages: original decimal strings, zero/null, units, uncertainty and raw references survive. No generated telemetry.
4. Traverse source/claim pages and every association next link: repeated document/locator associations and cross-study/mismatch context remain explicit. Shared claims are counted once.
5. Read dashboard using matching selection filters; counts/coverage agree with fixture expectations. verifiedRunCount is null; empty-denominator ratio is null, not NaN or fabricated zero.
6. POST /api/v1/compare with 2 and 3 known UUIDs: ordered studies, original observations/context and unavailable derivations. Duplicate/invalid/unknown selection fails whole request.
7. Inspect every detached entity, empty result and summary for synthetic origin. Collection drift must yield safe refusal rather than mixed data. No URL/DOI or status creates scientific verification.

## Real PostgreSQL integration (separate authorization)

Set TEST_DATABASE_URL locally for the approved test-named server/role under the existing runbook, then:

```powershell
poetry run pytest -m integration -q
```

Existing fixtures create suffixed test DBs with existing migrations and retain them. New HTTP snapshot tests need committed fixtures plus independent read-only sessions, not interference with existing outer rollback fixtures. CLI safety tests use target-specific approvals produced by the authorized test fixture/operator, never seed self-authorization. Cleanup needs separate exact-target approval.

## OpenAPI and completion evidence

After implementation inspect /openapi.json or app.openapi() from a controlled test application. Verify proposed paths/schemas in contracts/openapi.json and unchanged health/ready. Cover aliases, required/null fields, Decimal strings, pagination/query limits, invalid input and every declared error with real HTTPX responses. Formal contract parse alone is not runtime verification.

For each slice record commands, result counts, skips, query/transaction behavior and criterion coverage; deliver Frontend/Data examples with pending sign-offs clearly marked. Only then run Converge against SC-001–008. No commit, deployment, scientific acceptance or project completion follows automatically from this guide.
