# Phase 5 engineering decision and external acceptance record

The backend owner authorized implementation on 2026-11-12 and selected POST /api/v1/mission/scenarios/evaluate. F-01 records pending Frontend consumer acceptance. Backend owns public engineering DTOs, error vocabulary, pagination and provider orchestration. Data owns ranking, scientific mappings and reviewed source classifications. Data and scientific reviewers own scientific acceptance. AI has no Phase 5 engine deliverable.

- Scope includes independent engineering mock sections and explicit unavailability. Default providers are unavailable. TEST_ONLY runs use declared fixture labels and exact equality without scientific tolerances. Fixed ranking rows do not execute Data's rank.py.
- The evaluation API is stateless. A trusted persistence service round-trips the compatible complete subset in existing columns. Public write activation requires a lifecycle and writer target compatible with exact collection admission. See [data model](../data-model.md).
- A flattened UUID-ordered association page spans selected pillar groups. It carries all association identities with original claim and source context. Independent offsets and equality preconditions drive replay.
- V-01 is satisfied for authorized fixture provisioning at 127.0.0.1:5433 using TEST_DATABASE_URL and PHASE4_ADMIN_URL. Use fresh retained test resources only. Privileges and executed evidence are tracked in [verification](../verification.md).

| Task | Owner | Remaining evidence |
| --- | --- | --- |
| T056 / D-01 | Data and Backend | Official dataset/raw manifest, versioned identity mapping and source inventory |
| T057 / D-02/D-03 | Data and scientific reviewers | Accepted unit/quality/review dictionary and same-run scientific policy |
| T058 / D-04 | Data | Versioned ranking export/service, scope, algorithm and score semantics |
| T059 / D-05 | Data | Reviewed classification/fact/source mapping and acceptance corpus |
| T060 / F-01 | Frontend | Named consumer reviewer, date, scope and actual client acceptance results |
| T061 / F-02 | Data and Frontend | Optional comparison eligibility and additive consumer contract |
| T062 / B-01 | Backend owner | Compatible runtime writer/lifecycle and impact acceptance for unsupported fields |

Existing Phase 4 T078 still requires independent consumer acceptance. Phase 4 comparison remains on original observations with comparability unestablished.
