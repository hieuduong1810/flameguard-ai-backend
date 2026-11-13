# Phase 6 technical plan

Status approved through the owner’s [material decisions](approval.md).
Implementation and verification completed for the backend/mock scope.

## Existing architecture

Current admission iterates `Base.metadata.sorted_tables` and checks every row
against a manifest. `database_identity` rejects a reader with effective public
table write privilege. Chat models already have session/investigation and
citation/source foreign keys. One current Database engine supplies catalog reads.
See [Phase 5 handoff](../phase5-backend/handoff.md).

## Implementation slices

1. Add explicit admission-v2 table scope in collection repositories/services.
   Keep legacy default unchanged. Reuse canonical row checks and Phase 5 replay
   fingerprints. Test scientific tampering and runtime inserts independently.
2. Add optional runtime engine/settings and validate same-target identity and
   least privilege at runtime enablement. Operator-owned grants have a dedicated
   runbook. Preserve the three ORM chat entities and applied Alembic revisions.
3. Define Pydantic chat/provider DTOs and unavailable/mock providers. Providers
   receive detached bounded context. Validate exact original source associations.
4. Implement ChatService/ChatRepository with explicit service-owned transactions,
   atomic exchange writes, session commit serialization and expiry rechecks.
5. Add session/message routes, scoped error mapping and runtime OpenAPI examples.
6. Add AdvisorService/AdvisorProvider reusing Phase 5 pillar orchestration with
   independent unavailable/abstention behavior. Keep response-only assessment.
7. Execute lint/HTTP/PostgreSQL/Phase 4–5 regressions and focused convergence.

## Verification

Use existing retained PostgreSQL fixture conventions on fresh test-named targets.
Verify effective grants, same DB identity, exact v1/v2 admission, forged manifest
exclusions, FK failures, rollback, concurrent message pairs, source drift, unknown
and expired sessions, bad citations and cancellation. Run Poetry/Ruff/full pytest
and integration pytest with both test URLs. Record actual pass/fail/skip counts.

## Entry and exit

Implementation enters after owner approval recorded in approval.md. Each slice
exits with focused executed tests. Final engineering completion requires accepted
FR/SC evidence, regression checks, diff review and an explicit external handoff.
Scientific integration requires AI/Data acceptance independently.
