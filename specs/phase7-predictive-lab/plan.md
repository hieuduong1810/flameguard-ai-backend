# Phase 7 technical plan

Status approved by the owner on 2026-11-13. See [scope/API approval](approval.md).

## Reuse and implementation order

1. Add Pydantic prediction request/result/readiness and versioned owner metadata
   contracts. Reuse Phase 5 ScenarioInput, decimal/unit conventions and immutable
   context. Every scientific domain/uncertainty field comes from AI declarations.
2. Add a read-only prediction registry repository over existing ModelVersion and
   ModelTrainingRun, scoped to the admitted collection. Parse supported metadata
   versions explicitly. Never infer approval from free-text status alone.
3. Add PredictionProvider request/result DTOs, unavailable/synthetic providers and
   per-app injection. Keep transport neutral. Mocks use fixed labeled fixtures.
4. Add readiness and applicability service rules. Check registry/artifact/training,
   evaluation, corpus review, supported observable/unit, domain, uncertainty and
   provider metadata identity before calling predict. Real readiness fails closed
   with current unreviewed admission. Missing AI/Data evidence remains explicit.
5. Add API router and stateless execution service. Provider calls use detached
   context outside read transactions. Validate finite output, exact selected
   versions/units, uncertainty presence and fresh scientific fingerprint.
6. Add focused unit/HTTP/OpenAPI/PostgreSQL tests and handoff. Run one focused
   consistency review, then fix only genuine implementation gaps at convergence.

## Persistence impact

PredictionResult FK constraints require existing scenario/model rows. Its scalar
uncertainty and absence of full data-version provenance require a separate storage
decision for future publication. This phase's approved stateless mode writes no
tables and requires no extension to the runtime writer/admission boundary.

## Verification and completion

Test no model, unvalidated/unknown metadata, version mismatch, missing input,
out-of-domain values/materials, uncertainty gaps, synthetic mock contracts,
malformed/nonfinite provider results, timeout/cancellation/failure, no-write
invariants and Phase 4–6 regression behavior. Run Poetry check, Ruff lint/format,
full pytest and isolated PostgreSQL tests. Report pass/fail/skip counts.

Implementation starts after owner scope/API approval. Each slice exits with
focused tests. Engineering completion requires all executable criteria tested,
consistent artifacts/OpenAPI and diff review. Scientific readiness requires AI
and Data acceptance independently of backend mock completion.
