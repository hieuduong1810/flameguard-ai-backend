# Isolated Phase 4 demo and verification

Use Poetry. This runbook never instructs seeding the normal flameguard database, shared research data, staging or production. No cleanup/drop/reset command is provided.

## Prerequisites

The operator/project owner must independently approve one new, exclusively disposable database named flameguard_demo_<suffix> or flameguard_test_<suffix> on a pinned loopback endpoint. Provision a dedicated non-superuser database/table owner and a separate SELECT-only API role. Restrict write grants to the owner. Apply only the existing migrations in that exact approved target as a separate authorized step; the seed CLI refuses schema mismatch and never migrates.

Keep owner/read credentials in local environment only. The CLI reads DEMO_DATABASE_URL, never an implicit .env or DATABASE_URL fallback. If an explicit DATABASE_URL names the same target, it is treated as a regular configured database and refused; keep regular/shared development settings separate.

Create an ignored operator-owned .tools/demo-target.json with exact values obtained independently from the approved target:

```json
{"host":"127.0.0.1","port":5433,"database":"flameguard_demo_phase4","role":"dedicated_demo_owner","databaseOid":0,"owner":"dedicated_demo_owner","environment":"test","exclusiveDisposable":true,"collectionId":"synthetic-phase4-v1"}
```

databaseOid=0 and role names above are placeholders, not authorization. Obtain the actual OID/current identity through a read-only query in the approved target. The script cannot create its own authorization or grant itself permission. Test naming/localhost/APP_ENV alone is insufficient.

## Explicit seed

With APP_ENV=test and DEMO_DATABASE_URL set privately for that exact owner/target:

```powershell
poetry run python scripts/seed_demo_data.py --allow-synthetic --confirm-database flameguard_demo_phase4 --target-authorization .tools/demo-target.json
```

Expected first run: 28 inserts and exact per-table counts from data/demo/README.md. Identical rerun: exit 0 with zero inserts. All-21-table content/schema/grant checks precede insertion. Unexpected row/key/content or contention yields safe refusal/rollback; existing data is never overwritten. Valid exact subsets may receive missing rows atomically. No --force or cleanup mode exists.

## Read API

Copy data/demo/collection.example.json to a private local file and set its fixture/slugs references to the versioned manifests and target binding to the actual endpoint/DB OID/read-only role. Set CATALOG_COLLECTION_MANIFEST to that local file and DATABASE_URL to the SELECT-only role's URL. Do not expose credentials to the frontend.

```powershell
poetry run uvicorn app.main:app --reload
```

Inspect /docs and /openapi.json. Phase 4 has no startup/request-time seed or migration. A missing/mixed/drifted collection is unavailable; health/ready retain their established behavior. Synthetic fixtures retain exact synthetic-only admission; non-curated non-synthetic reads follow the binding below. Curated publication remains blocked pending Data acceptance.

Exercise capabilities/list, UUID/slug detail, all child/association next links, dashboard counts and comparison of 2–3 UUIDs. Check exact decimal strings, zero/null, source locators/contextMismatch, synthetic origin and unavailable verification/derived outcomes. Links to example.invalid are placeholders, never real citations.

## Non-synthetic read admission

Use an owner-managed private collection manifest with the same host/port/database/databaseOid/readRole target binding and a SELECT-only role. Declare collectionId, origin=real|unknown and reviewState=unreviewed|unknown; omitted origin/review remains unknown. Do not reuse the synthetic fixture reference. Without a snapshot reference, every one of the 21 tables must be empty: the API then returns honest empty results with the declared context.

For already stored non-curated records, an optional `snapshot` path (relative to the collection file or absolute) pins the complete exact original rows across all 21 tables. Its JSON has collectionId, origin and tables with the approved scalar column names; every table key is required, including empty tables. It is a read-side allowlist, never an import command. Content/identity drift or recognized demo UUIDs, synthetic identity/status markers or example.invalid references refuse admission. Optional `slugs` uses the existing owner-managed identity manifest; omitted slugs remain null.

The snapshot and collection origins must agree. No status string establishes scientific review; curated declarations are refused. This supports inspection of owner-declared stored fields, not Data Team acquisition, ingestion, normalization, scientific validation or approved real-data publication. All read requests inspect database rows in server-side batches of at most 64 per table in the same read-only repeatable-read snapshot; no stale approval is cached.

## Tests and evidence

```powershell
poetry check
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -q
```

Without explicit test URLs, DB tests skip and that is not a PostgreSQL pass. Existing integration uses TEST_DATABASE_URL with its established test-named server/CREATEDB safeguards. New Phase 4 integration additionally uses PHASE4_ADMIN_URL for an approved test server; it creates uniquely named retained test databases and restricted owner/read roles, applies only existing migrations there, and writes private target files under ignored .tools/. Never set these URLs to a research database. Administrator capabilities are used only for those newly generated test targets, not by the seed script/API.

Windows sandbox temp-directory restrictions may require a unique permitted --basetemp or the authorized normal execution context. Report exact commands/counts/skips and distinguish real PostgreSQL from mocked HTTP tests. Do not invent passes or automatically drop retained targets/roles. See the [verification record](../phase-4-api-verification.md) and pending [Frontend](../contracts/phase-4-frontend-handoff.md)/[Data](../contracts/phase-4-data-handoff.md) gates. Converge remains a separate user-invoked step.
