# Phase 7 Predictive Lab

Branch `feat/phase7-predictive-lab`. Prepared 2026-11-13.
Competition development authorization confirmed by the owner in this conversation.
Phase 6 baseline `61ada61` is available. Material API decisions are approved in
[approval.md](approval.md).

## User stories and acceptance

### US1 Inspect readiness (P1)

The caller requests model readiness and capabilities. Missing, unvalidated,
unavailable, incompatible or insufficiently documented models return `not_ready`
with explicit reasons. A model registry row alone cannot satisfy readiness.
Response metadata distinguishes original registry declarations and accepted
scientific validation evidence supplied by external owners.

### US2 Request guarded prediction (P1)

The caller supplies a candidate model UUID, selected observable, expected model
and dataset versions, and explicit scenario quantities. Missing conditions,
unsupported units/material/domain, missing uncertainty or incompatible versions
prevent execution. Successful future scientific execution requires all model,
data, provider and applicability gates. Provider timeout/failure and malformed
results return bounded errors. Backend performs orchestration and contract checks.

### US3 Exercise provider contract with synthetic fixtures (P2)

Internal synthetic providers return fixed TEST_ONLY results for provider tests.
Public readiness remains `not_ready` for synthetic or unvalidated models. Public
scientific execution cannot promote mock output into a validated prediction.
The server defaults to unavailable. A trusted per-application provider factory
allows later real adapters with independent transport choices.

## Functional requirements

- FR-001 / P7-01 Expose readiness states/reasons for artifact, registry version,
  training/evaluation evidence, dataset compatibility, domain, uncertainty,
  supported observables/units, provider and scientific admission eligibility.
- FR-002 / P7-02 Define PredictionProvider and detached versioned request/result
  contracts, unavailable/fixed synthetic adapters and trusted injection.
- FR-003 / P7-03 Read ModelVersion and ModelTrainingRun through repositories.
  Keep model UUID, version and training dataset identity separate. An owner
  metadata contract may reference existing domain Text and artifact refs with
  explicit schema versions. Unknown formats produce unavailable metadata.
- FR-004 / P7-04 Validate all scenario inputs against AI-declared applicability
  and uncertainty rules. Missing/unknown bounds remain unsupported. Backend
  cannot invent gravity mappings, scientific tolerances or confidence intervals.
- FR-005 / P7-05 Execute only after every accepted scientific gate passes.
  Preserve observable, finite original value/unit, model/data versions,
  applicability, supplied uncertainty and limitations. Reject output drift,
  timeout and malformed contracts. Recheck scientific snapshot/version context.
- FR-006 / P7-06 Keep the approved execution stateless. Assert no scenario,
  prediction-result or registry writes for successful mock contract tests,
  not_ready requests and provider failures. Conditional future persistence
  requires separately accepted lifecycle, provenance and write-boundary impact.
- FR-007 Preserve Phase 4–6 behavior, both admission versions, runtime writer
  grants, original models and applied migrations.
- FR-008 Provide HTTP/OpenAPI examples, provider/configuration handoff and actual
  test results with distinct engineering and scientific readiness statements.

## Success criteria

- SC-001 Every P7-01–P7-06 requirement maps to an implemented or explicitly gated
  capability and executed acceptance evidence.
- SC-002 Invalid/unvalidated/missing-domain/missing-uncertainty inputs cannot
  reach scientific execution. Synthetic outputs remain explicitly labeled.
- SC-003 Required lint/full/PostgreSQL checks pass with explicit skips/failures.
  Isolated tests prove collection integrity and absence of runtime prediction writes.

Real model availability, AI adapter/evaluation, official dataset compatibility and
Frontend acceptance remain external evidence gates. Prior phase external tasks
retain their status. Phase 8 is outside this feature.
