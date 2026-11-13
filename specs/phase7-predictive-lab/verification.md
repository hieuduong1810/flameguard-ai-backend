# Phase 7 verification

Executed 2026-11-13 on `feat/phase7-predictive-lab` after owner approval.

## Final checks

| Command | Exit | Passed | Failed | Skipped | Other |
| --- | --- | --- | --- | --- | --- |
| `poetry check` | 0 | Configuration valid | 0 | 0 | All set |
| `poetry run ruff check .` | 0 | Lint clean | 0 | 0 | All checks passed |
| `poetry run ruff format --check .` | 0 | 253 files formatted | 0 | 0 | No formatting gaps |
| `poetry run pytest -q --tb=short` | 0 | 650 | 0 | 0 | 78.16 seconds |
| `poetry run pytest -m integration -q --tb=short` | 0 | 223 | 0 | 0 | 427 deselected, 84.59 seconds |
| `poetry run pytest tests/integration/test_phase7.py -q --tb=short` | 0 | 13 | 0 | 0 | 5.23 seconds |
| `git diff --check` | 0 | Whitespace check clean | 0 | 0 | No staged changes |

The 223 integration tests are included in the 650 full-suite tests. They are
also executed separately for an explicit PostgreSQL gate. Phase 7 contributes
78 tests across fixtures, unit/domain/provider, HTTP/OpenAPI/orchestration and
PostgreSQL paths. Deselected tests belong to the separate integration-only run.

## Database execution boundary

Tests used Docker PostgreSQL on loopback port 5433. Process-local
`PHASE4_ADMIN_URL` and `TEST_DATABASE_URL` selected the approved test-named
`flameguard_test_phase7` namespace. Credentials were resolved locally and were
excluded from output and reports. Existing fixture validation rejects ordinary
development targets.

Fixtures created fresh randomly named retained databases and roles, applied
existing migrations only to those fresh targets, and inserted TEST_ONLY registry
and scenario-evidence fixtures. No shared database reset or destructive migration
was executed. Read APIs used a separate scientific reader without write grants.

Phase 7 compared every row of all 21 tables before and after not_ready requests,
version conflicts, rejected admission and internal successful/malformed/failing/
timed-out synthetic provider calls. All snapshots matched. Both admission versions
were exercised. Attempts to claim reviewed collection status or mismatch the
scientific manifest were rejected. Existing Phase 6 chat writer regression tests
executed with the full integration suite.

## Verification limits and resolved failures

The initial sandbox test attempt could not access the Windows pytest temporary
directory. The authorized tests were rerun with the required host access.
The initial PostgreSQL fixture used an unsupported synthetic status. It was
corrected to the existing `TEST_ONLY` vocabulary, preserving admission policy.
All resulting failures were rerun successfully. Lint/format findings were fixed
before the final full checks.

The internal HTTP/DB orchestration harness overrides readiness only inside tests
to exercise guarded downstream transport outcomes with synthetic results. Public
tests separately prove unreviewed/mock calls stay not_ready. No test establishes
scientific model validity or accepted real-data/provider integration.

The local Spec Kit prerequisite script returned the absolute Phase 7 feature
directory with `tasks.md` available. The ignored selector points to
`specs/phase7-predictive-lab`. Phase 6 artifacts, ORM, Alembic revisions and runtime
permission code have no changes in this delivery.

## Readiness and convergence

Backend Engineering Readiness is ready for the approved stateless/mock-tested
scope. T001–T012 are complete. Focused convergence found no remaining executable
backend gaps. See [convergence.md](convergence.md).

External Integration Readiness remains pending through T013 and T014. Real model
validation, AI provider registration and acceptance, reviewed data publication,
official dataset/version compatibility and Frontend integration require owner/team
evidence. The current scientific gate retains not_ready. Prior phase external
acceptance tasks retain their status.
