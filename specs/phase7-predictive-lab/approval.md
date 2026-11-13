# Phase 7 scope and API approval

Competition development permission was explicitly confirmed by the project owner
on 2026-11-13. Approval below concerns the concrete feature contract and
implementation scope after that preflight condition was satisfied.

## Approved smallest architecture

Use stateless prediction orchestration with the existing scientific reader and
exact admission checks. Reuse Phase 6 per-app provider injection and bounded
provider calls. Read ModelVersion/ModelTrainingRun and accept only versioned,
owner-supplied artifact/domain/evaluation/uncertainty metadata whose identities
match registry and dataset references. Missing metadata keeps readiness closed.
Current scientific collections carry unreviewed/unknown review state, so scientific
execution remains unavailable until the Data/AI publication gates are accepted.

P7-06 is satisfied for this scope by an explicit no-persistence decision and
executed no-write checks. PredictionResult requires scenario_id/model_version_id
and stores only scalar uncertainty. Persisting richer provenance, training/data
versions or uncertainty structures needs a reviewed lossless mapping and runtime
boundary extension. Preserve existing chat writer grants and all ORM/migrations.

## Approved additive public API

| Operation | Inputs | Outcomes |
| --- | --- | --- |
| GET `/api/v1/prediction/readiness` | Optional model UUID query | 200 readiness, model/capabilities metadata and reason codes. Without a candidate, return not_ready with model-selection reason. |
| POST `/api/v1/predictions` | model UUID, expected model/dataset versions, observable and Phase 5 scenario input | 200 explicit not_ready/unsupported or future validated prediction; 409 version drift; 422 malformed request; 502 invalid provider response; 503 provider failure; 504 provider timeout |

GET is a registry/capability preflight. Scenario-specific domain validation occurs
in POST before provider execution. Numeric quantities use explicit units and
decimal strings consistent with Phase 5. Response carries state/reasons, origin,
model/data versions, observable/unit, supplied uncertainty and limitations.
Numeric results are absent for not_ready and unsupported states.

Unavailable is the default provider. Synthetic mocks exercise the internal
provider contract with fixed TEST_ONLY values and declared fixture-only domains.
Public scientific calls with mock/unvalidated providers return not_ready.
This proposal adds no public synthetic execution mode. Client displays explicit
readiness, unsupported, unavailable and failure states. Scientific publications
and frontend acceptance remain separately gated.

## Owner approval recorded

On 2026-11-13 the owner replied “duyệt rồi làm đi” to this concrete proposal.
The stateless storage decision, additive API and independent implementation and
isolated PostgreSQL verification are approved. External scientific and frontend
acceptance remain pending.

Approval covers all independent backend tasks and isolated PostgreSQL verification
using the existing fresh retained fixture conventions. Material contract changes
require a separate decision.
