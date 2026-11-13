# Phase 7 prediction handoff

The project owner approved the additive public API and stateless scope on
2026-11-13. External AI, Data and Frontend acceptance remains pending.

## HTTP contract

| Operation | Request | Response |
| --- | --- | --- |
| GET `/api/v1/prediction/readiness` | Optional `model_id` UUID query | Readiness state, reasons, model UUID/version, dataset version, collection origin, declared capabilities and limitations |
| POST `/api/v1/predictions` | `modelId`, `expectedModelVersion`, `expectedDatasetVersion`, `observable`, Phase 5 `scenario` | `state`, `readiness`, `reasons`, nullable `result` |

No selected model returns `not_ready` with `model_selection_required`. Unknown
models and incomplete metadata return explicit reasons. A missing collection or
failed admission returns 503. Public mock calls return `not_ready` and a null
result. Missing scenario dimensions are allowed at transport validation and
prevent execution through applicability checks. Invalid units and malformed
decimal strings return 422. Numeric JSON values cannot replace decimal strings.

The following request uses identifiers available only in the isolated Phase 7
test fixture. Its public response remains `not_ready` with `result` null.

```json
{
  "modelId": "70000000-0000-4000-8000-000000000001",
  "expectedModelVersion": "TEST_ONLY-v1",
  "expectedDatasetVersion": "TEST_ONLY_fixture-v1",
  "observable": "TEST_ONLY_observable",
  "scenario": {
    "material": {"key": "TEST_ONLY_material"},
    "gravity": {"value": "0", "unit": "g"},
    "oxygen": {
      "value": "0",
      "unit": "%",
      "meaning": "ambient_oxygen_fraction_percent"
    },
    "pressure": {"value": "0", "unit": "psia"},
    "airflow": {"value": "0", "unit": "cm/s"}
  }
}
```

POST returns 200 for `not_ready`, `unsupported` or a future admitted `predicted`
result. Expected model/dataset drift returns 409. Provider response rejection
returns 502, provider failure 503 and timeout 504. Responses use `Cache-Control`
`no-store`. Errors contain an `error` object with a sanitized `code`.

Readiness reasons include model selection/availability/validation/expiry,
unavailable metadata, unsupported domain units, training/evaluation or dataset
binding, unreviewed collection and unavailable provider/model binding. Exact
machine codes are defined by `PredictionService.assessment`. Applicability
reasons identify each missing, unsupported-unit or out-of-domain dimension,
unsupported material/observable and oxygen meaning mismatch.

The live `/openapi.json` is the executable field/type contract. Readiness and
outer response fields use camelCase. Provider-result and uncertainty declaration
fields currently use snake_case. Frontend adapters must preserve model UUID,
model/data/provider versions, collection fingerprint, original decimal strings,
units, uncertainty bounds and method reference, origin and limitations.
`not_ready` and `unsupported` contain no numeric result. These screens need
Frontend acceptance separately from backend contract testing.

## Registry and AI provider boundary

Use existing `model_version` and `model_training_run` through the read-only
scientific connection. This feature accepts a bounded version-1 JSON declaration
in the existing `applicability_domain` Text field. Plain text, unknown versions
and incomplete declarations remain unavailable. No existing rows are rewritten.

The authoritative declaration shape is `ModelMetadata` in
`app/schemas/api/predictions.py`. It supplies `schema_version`, `artifact_ref`,
`training_run_id`, `dataset_version`, `evaluation_ref`, `uncertainty_ref`,
timezone-aware `validation_expires_at`, `materials`, four explicit-unit domain ranges, `oxygen_meaning`, supported
`observables` mapped to units, and `limitations`. Each range supplies decimal
`minimum`, `maximum` and `unit`. Domains come from AI owners. Backend performs
inclusive bound checks and no unit conversions or extrapolation.

The selected training run must belong to the model. Its `training_dataset_ref`
must match the declaration's dataset version and `metrics_ref` its evaluation
reference. An expired validation declaration keeps readiness closed. Registry status alone grants no readiness. Artifact references and
evaluation references are opaque owner identifiers. Backend does not download
or scientifically evaluate artifacts.

Register a future trusted adapter with
`app.state.prediction_provider_factory`, a zero-argument per-application factory.
The adapter implements asynchronous `predict(PredictionCall)`, exposes `origin`
and a `ProviderRegistration` binding provider/model/data versions, model UUID,
artifact reference and availability. Transport is adapter-owned. No HTTP service
or package dependency is assumed.

The detached call contains the approved scenario/request, model declaration and
scientific snapshot fingerprint. The response must match selected identifiers,
versions, observable and unit, origin, snapshot, uncertainty method and declared
limitations. Supplied uncertainty bounds must be finite, ordered and contain
the supplied value. Backend never calculates an interval. The adapter receives
a deep copy, and the service rechecks admission and snapshot after the call.

## Configuration and current scientific gate

`PREDICTION_PROVIDER` accepts `unavailable` by default or `mock`.
`PREDICTION_TIMEOUT_SECONDS` defaults to 10 and accepts values greater than zero
through 30. Trusted factories override environment selection per app instance.
No provider credentials or network adapter are introduced.

Mocks return fixed TEST_ONLY fixture values only through internal adapter tests.
Their presence cannot make the public endpoint ready. Current collection
admission supports unreviewed/unknown scientific collections. Real reviewed
publication and real dataset version binding require future approved Data/AI
admission work. The backend preserves that gate. Real execution therefore remains
unavailable with the current admitted data and providers.

AI acceptance must provide validated versioned artifacts, reproducible evaluation,
domain and uncertainty policy, accepted expiry dates and revocation semantics and training
source traceability. Data acceptance must establish official dataset identity,
quality flags, review and lossless mappings. Richer uncertainty forms or additional
input dimensions require contract review. Unsupported forms stay unavailable.

## Stateless persistence decision

Phase 7 writes no scenarios, prediction results, model registry or chat rows.
The existing `prediction_result` table requires scenario/model foreign keys and
has scalar uncertainty. Rich provenance retention, persistence, retention policy
and any runtime writer extension require a new approved scope. Existing admission
versions, chat grants, ORM and applied migrations are preserved.

Public predictions remain research-screening outputs subject to external
scientific acceptance. Engineering tests provide no model-validation claim.
