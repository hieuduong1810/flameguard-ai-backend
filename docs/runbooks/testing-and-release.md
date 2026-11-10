# Testing, verification and safe release runbook

This is the **evidence gate** for Codex. A generated test is not a passed test;
an offline unit test is not proof of a live PostgreSQL migration or validated
NASA measurement. Execute only commands suitable for the authorized scope.

## 1. Baseline local checks

```powershell
poetry check
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -q
```

Report exact commands, exit codes, pass/fail/skip counts, and why anything
could not run. With no `TEST_DATABASE_URL`, DB integration tests are expected
to skip; do not write "all tests passed" without explaining the skips.

For a documentation-only change, static link checks and relevant existing
tests are sufficient when dependencies are available. Do not launch Docker or
modify a database just to satisfy a documentation patch.

## 2. PostgreSQL integration tests — opt in only

Existing fixtures in `tests/postgres_fixtures.py` demand a separate test DB
template named `flameguard_test_<suffix>`, with permission to create a new
isolated database. They apply the three ordered migrations there and keep
the newly created DB for inspection. Do **not** point them at `flameguard`
development or production databases.

```powershell
# Example only. Supply actual dedicated TEST credentials locally.
$env:TEST_DATABASE_URL = 'postgresql+asyncpg://test_role:REDACTED@127.0.0.1:5433/flameguard_test_suite'
poetry run pytest -m integration -q
Remove-Item Env:\TEST_DATABASE_URL
```

The role must have `CREATEDB` on the chosen testing server. Verify its
identity before running. The test runner creates additional databases with a
random suffix and intentionally does **not** delete them. Cleanup requires
exact-target validation and separate authorization; never use a wildcard
`DROP DATABASE` or delete broad Docker volumes.

## 3. Data and scientific correctness tests

- Same-run condition compatibility and six-dimensional evidence coverage.
- UUID vs `psi_id` vs frontend slug identity and stable pagination.
- Source document links, optional DOI, valid source locators, claim-source
  many-to-many provenance and nullable run context.
- Unknown/null values, original units, decimal precision, valid conversions.
- Claims and dashboard aggregates filtered by **reviewed** scientific status.
- Unavailable assets, absent source review and conflicting conditions must
  not be silently replaced by synthetic values.
- AI unsupported/out-of-scope and missing-evidence cases must abstain
  correctly; predicted values require an approved model/domain.

Use synthetic fixtures labeled `TEST_ONLY` in tests. They must never be
published as measured NASA records or imported into the shared dev DB.

## 4. API contract tests (when business endpoints are implemented)

For each route, cover:

1. Exact JSON shape and OpenAPI schema.
2. 200 success with reviewed fixture data, empty collection, valid pagination.
3. 404 unknown canonical ID/slug; 422 invalid filters/ranges/units.
4. Null/missing measurements, deterministic ordering, decimal serialization.
5. Provenance URLs and no invented citation identities.
6. Database unavailable/timeout with sanitized error and no leaked credentials.
7. Frontend adapter compatibility against shared contract examples.

HTTPX with application lifespan and an isolated test database is the preferred
backend E2E boundary. UI smoke tests in the frontend are owned by its team.

## 5. Migration checks

```powershell
poetry run alembic history
poetry run alembic heads
poetry run alembic current
poetry run alembic check
```

Migration authoring requires explicit approval of all schema modifications,
forward SQL, downgrade/rollback implications, and the target environment.
`upgrade head --sql` emits SQL for offline review; it does not prove the
operation was safely executed. Never delete/squash `0001`–`0003`, stamp away
unknown revisions, or migrate a shared DB just to make tests green.

## 6. Converge checklist before reporting done

- [ ] User's accepted spec criteria mapped to files and tests.
- [ ] Spec, plan, tasks, contracts and code consistent; open risks documented.
- [ ] Every required test executed or explicitly marked blocked/skipped.
- [ ] Git diff reviewed; no unrelated frontend/DB/secret changes.
- [ ] No fabricated claims/model validation/unreviewed measurements.
- [ ] No API breaking changes or missing team handoff hidden in the result.
- [ ] `docs/project-status.md` and an appropriate phase report updated **only
      if implementation really completed**.
- [ ] Handoff names unfinished dependencies and precise next action.

Safe output template:

```text
Delivered: <bounded feature and acceptance criteria>
Files changed: <files>
Verification: <commands and actual counts/results>
Migrations/data writes: <none OR approved target/revision>
Scientific status: <verified/review pending/demo; source evidence>
Cross-team handoff: <owner, artifact, readiness>
Open items: <blocked/not done + why>
Next slice: <smallest useful next feature>
```
