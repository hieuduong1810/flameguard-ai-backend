# Phase 7 engineering report

Delivery date 2026-11-13. Branch `feat/phase7-predictive-lab`, Phase 6 baseline
`61ada61`. Owner competition, API, stateless scope and implementation approvals
are recorded in [approval.md](approval.md).

## Implemented capability coverage

| Requirement | Backend delivery | Evidence |
| --- | --- | --- |
| P7-01 | Readiness API with model, data, metadata, provider and scientific admission gates | Unit, HTTP and PostgreSQL tests |
| P7-02 | Transport-neutral provider, unavailable/default, synthetic internal mock and trusted per-app registration | Provider contract and failure tests |
| P7-03 | Read-only registry/training adapter and versioned declaration, training/evaluation/dataset binding | Registry integration and identity tests |
| P7-04 | Explicit-unit material/gravity/oxygen/pressure/airflow applicability, required uncertainty declaration and bounded finite results | Domain and uncertainty tests |
| P7-05 | Guarded stateless POST, version conflicts, bounded provider call, output checks, scientific snapshot recheck | HTTP orchestration and admission regression tests |
| P7-06 | Approved stateless scope, no runtime permission extension | All-21-table before/after snapshots and reader-grant tests |

The API operations are GET `/api/v1/prediction/readiness` and POST
`/api/v1/predictions`. See the
[consumer/provider handoff](../../docs/contracts/phase-7-prediction-handoff.md)
for field names, error states, configuration and external acceptance requirements.

## Files

- Application changes include `app/core/config.py`, `app/api/v1/router.py`,
  `app/api/v1/endpoints/predictions.py`, `app/schemas/api/predictions.py`,
  `app/repositories/prediction_registry.py`, `app/services/predictions.py` and
  `app/integrations/prediction.py`.
- Tests include `tests/fixtures/phase7.py`, `tests/unit/test_phase7.py`,
  `tests/contract/test_phase7_contract.py`,
  `tests/contract/test_phase7_orchestration.py` and
  `tests/integration/test_phase7.py`.
- Feature evidence resides in this directory. The documentation map, project
  status, AI/frontend contract pointers and Phase 7 handoff link the current
  engineering delivery.

## Completion boundaries

Executable backend work is checked against the approved specification through
focused convergence and executed verification. T013 remains external AI/Data
acceptance and T014 remains Frontend acceptance. Phase 4 T078 and Phase 5/6
external tasks retain their existing states.

Public readiness remains closed with existing unreviewed scientific admission.
AI validation, a real provider, accepted scientific publication and official
dataset compatibility are pending. Rich uncertainty, quality-flag input mapping,
accepted artifact expiry/revocation declarations and real training-source acceptance need external
contract evidence. No artificial scientific result was added to any shared
collection. Synthetic registry rows exist only in retained isolated test DBs.

The manual workflow used the existing feature selector and preserved Phase 6.
The local prerequisite checker initially encountered the Windows script execution
policy. Its checked repository script was then executed with a process-local
PowerShell policy override and confirmed the Phase 7 feature. No machine policy
was changed. The legacy YAML workflow was not executed.

Verification counts and convergence disposition are recorded in
[verification.md](verification.md). Backend Engineering Readiness and External
Integration Readiness are reported separately there.
