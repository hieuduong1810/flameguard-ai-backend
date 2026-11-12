# Pre-implementation consistency assessment — 2026-11-11

The Implement request explicitly approves the existing spec/plan/tasks and authorizes all executable backend work, including isolated PostgreSQL verification. requirements.md is a read-only gate: 16 checked, 0 unchecked. No extension hook file is installed.

Schema, ownership, separate identities, exact scalar values and original provenance agree across artifacts. Scientific comparison is original-observation display only; derived outcomes remain unavailable. No model/migration/diagram change is required.

Interpretation: Group 7 real-HTTP tests complete evidence not available from earlier mock HTTP/repository checks. Tests written before fixture helpers may initially fail import/collection; this is expected red evidence, not a circular implementation dependency. Plan statements saying tasks are not yet generated are historical design-stage statements, not implementation prohibitions after the new instruction.

The owner approves backend wire contracts for this execution. Frontend consumer acceptance and Data scientific acceptance remain external gates; record them as pending rather than contact teams or invent sign-off. T074 automatic Converge conflicts with the current explicit instruction not to start convergence, so T074 is BLOCKED by user scope. Independent implementation continues.

Database safety: current local role lacks CREATEDB; existing Docker PostgreSQL at loopback port 5433 will host newly generated test-named databases. Existing research/development databases are not migration or seed targets. No cleanup/drop is authorized.

Contract reconciliation: the spec/read-model explicitly gives noncanonical slug lookup 404; the initial OpenAPI pattern would imply validation 422. Preserve specified lookup semantics and document canonical spelling rather than impose that pattern on request input. Optional URL-query null branches in generated Pydantic schemas represent omission, not a JSON-null query value; compare their supplied-value schemas without weakening response/body null checks.

## Remediation consistency disposition — 2026-11-12

The new user request authorizes all executable convergence follow-ups T075-T077 and T079-T082. They fit the approved read model, existing response caveat surface and frozen ERD; no new architecture or scientific decision is needed. Read-only owner-declared snapshots pin already stored non-curated content without performing Data ETL. Curated publication remains disabled. Strict HTTP validation is separate from internal Python population, preserving DTO compatibility. T078 requires actual external acceptance and remains blocked; it does not block independent remediation. The previous user-invoked Converge satisfies T074's assessment action and produced the appended work; no fresh Converge is automatically authorized by this Implement command.
