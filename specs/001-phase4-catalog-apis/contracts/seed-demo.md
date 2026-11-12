# Proposed scripts/seed_demo_data.py Contract

Status: future CLI design only. No script, credentials, target authorization or database rows are created in this planning step.

## Operator interface

Proposed command after implementation and separate disposable-target authorization:

```powershell
poetry run python scripts/seed_demo_data.py --allow-synthetic --confirm-database flameguard_demo_phase4 --target-authorization .tools/demo-target.json
```

Require explicitly set APP_ENV=development|test and DEMO_DATABASE_URL using postgresql+asyncpg. Do not load an implicit .env credential or fall back to DATABASE_URL/Settings' development defaults. Missing environment/URL/flag/confirmation/authorization is refusal. No --force, --reset, --truncate, --drop, cleanup or auto-migrate option.

## Target admission before any data write

1. Validate the versioned fixture/slug manifest offline: unique UUIDs, PSI IDs/tag slugs, all references, fixed timestamps, valid locators, TEST_ONLY statuses and example.invalid references. No real DOI/NASA finding.
2. Read an independently operator-approved, ignored target authorization file. It pins normalized host/port/database/role, server identity under that approved endpoint, database OID/owner, dataset version and exclusive-disposable declaration. The seed script cannot generate authorization for itself. Do not version credentials or actual local approvals.
3. Permit only allowlisted loopback/local disposable endpoints and names flameguard_demo_<suffix> or flameguard_test_<suffix>. Reject production/staging/shared/unknown contexts, default development DB, wrong confirmations, URL query connection overrides/multiple hosts and mismatched endpoints. Pin the resolved endpoint; do not trust a DNS alias or a name alone. Target DB role must be dedicated, non-superuser and limited to the approved disposable DB; seed needs no CREATEDB.
4. Verify current_database/current_user, DB OID/owner and effective grants match authorization. Reject PUBLIC or unrelated-role write grants to the 21 tables and nonexclusive use. A default name/APP_ENV/localhost alone never proves the target is disposable. Provisioning/role restrictions and authorization are external prerequisites, not script side effects.
5. Require exact existing migration head 0003_could_have and expected approved table shape. No create/alter/stamp/upgrade/drop, extensions or synthetic marker table/column.

## Atomic insert-only behavior

- Begin one transaction; acquire a dataset-scoped transaction advisory lock and bounded write-conflicting table locks across all 21 tables in deterministic order. Advisory lock alone coordinates only cooperating seeders; table locks prevent a concurrent writer changing the preflight set. Short lock/statement timeouts fail safely.
- Recheck target identity/schema and inspect all 21 tables, excluding only alembic_version metadata. Target must be empty or contain exact manifest records. Unexpected IDs, unrelated/scientific rows, noncanonical status/content, unique-key collisions and incomplete foreign graphs cause refusal/rollback.
- Identical complete dataset is successful no-op. An exact, referentially valid subset may receive only its missing manifest rows after full graph validation; inconsistent partial state is refused. Never update existing rows, silently skip a conflict or use ON CONFLICT DO UPDATE. Plain insert after locked checks is preferred; a collision aborts rather than overwrites.
- Insert in FK order, verify all expected IDs/content/counts and commit once at the service/CLI orchestration boundary. Repositories flush/execute only. A forced error rolls back every new row; no half-seeded state.
- Use stable synthetic IDs, PSI strings, tag slugs and fixed created_at values. Repeated runs do not change timestamps or scientific fields. Never write unused chat/scenario/prediction/import tables.
- A second concurrent seed either observes the identical committed dataset and exits as no-op or receives a safe contention failure; it never duplicates rows. No automatic cleanup of failed or old data.

## Origin and status rules

Use TEST_ONLY/SYNTHETIC_UNREVIEWED in existing condition/source/claim status fields. Runs/measurements have no approved status/origin column: project synthetic labels from admitted collection/fixture manifest membership. Every detached entity, empty page and aggregate receives origin context. Do not create a column or misuse scientific review labels. Synthetic PSI IDs are visibly synthetic values in psi_id, not real external NASA identities.

Fixture membership/content validation also occurs when serving a synthetic collection. Missing origin remains unknown; synthetic records cannot be served as a curated collection or mixed with future Data delivery.

## Output and exit contract

Success exit 0: dataset ID/version, sanitized target identity and per-table inserted/already-present counts; identical rerun inserts zero. Failure exits nonzero with code TARGET_NOT_AUTHORIZED, SCHEMA_MISMATCH, DATASET_CONFLICT, LOCK_TIMEOUT or SEED_FAILED and a sanitized message. No password, full DSN, private path, scientific content or raw SQL exception output. Target authorization file contents are not printed.

## Required tests before calling the CLI safe

- Missing opt-in/env/URL/confirmation/file; production/staging/shared/default-dev and misleading local/test-name targets; role/OID/endpoint/grant mismatch; connection-option bypass attempts.
- Manifest duplicate IDs/unique PSI or tag keys, invalid refs and invented verified statuses rejected before writes.
- Existing-head/shape mismatch fails without migration.
- First run, identical no-op, valid subset completion, altered fixture, unique collision, scientific/unrelated row in any of 21 tables, and malformed partial graph.
- Concurrent runs, bounded lock contention and injected mid-insert failure; full rollback and unchanged scientific sentinel data.
- Synthetic origin/Decimal/provenance visible through real HTTP reads; no startup/request-time seed path.
- Integration tests use independently approved generated targets and preserve old fixture safeguards; no automatic DB disposal.
