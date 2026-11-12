# Phase 4 Proposed Team Handoffs

Status: design proposal; no messages were sent and no team sign-off is claimed.

## Frontend handoff

Backend provides [API](api.md), [formal schemas](openapi.json), safe synthetic examples, error/capability matrix and later exact test/OpenAPI evidence for each slice. Frontend owns the adapter, UI changes and browser verification.

- Preserve dto.id as canonical UUID for requests; use separately approved dto.slug for existing routes and carry psiId independently. Never overwrite UUID with the current UI slug ID.
- Original decimals are strings; display formatting must retain original values and unit context. No Number coercion that loses originals, null-to-zero fallback, or fabricated required metadata.
- Consume explicit unavailableFields/capabilities to disable or explain fuel/facility/numeric-gravity/newest/confidence controls until mappings are accepted. Current mock confidence, hardware, PI, dates and findings are not backend facts.
- Traverse claim source pages; a primary citation display must retain access to every association/locator/excerpt/context. Do not collapse them into the old flat EvidenceClaim DOI.
- Runs expose paged conditions/measurements rather than a hard-coded telemetry array. Assets and missing charts require honest unavailable states.
- Comparison shows original observations and scientific caveats; no fallback verifiedRunCount, arbitrary averages or best-study highlights.
- Synthetic collection/individual-item labels and non-NASA caveats remain visible, including dashboard totals. Empty real data must not trigger hidden local mock fallback.

Acceptance before dependent consumer behavior: Frontend/Backend agree on list/detail, unknown fields, invalid/empty cases, slug mapping, Decimal handling and multi-source evidence examples. Later Frontend-owned adapter/browser tests prove actual integration; backend tests alone do not prove it.

## Data Team handoff

Data owns acquisition, curation, normalization, scientific review and import execution. Backend supplies the unchanged physical schema, compatibility examples and acceptance checks; this plan is not ETL.

Required artifacts: real identity/source manifest, non-synthetic collection origin, reviewed slug entries, unit/observable dictionary, status vocabulary/meaning, exact missing-value policy, source/run relationship context, raw asset contract, dedup/version policy and QA/acceptance evidence. No personal or secret data is requested.

Backend will verify UUID/PSI/run/document identities, exact original values/units/uncertainty, nulls, every source association, review limitations and origin separation. A source URL/DOI or collection-level review flag does not validate a measurement. Because the ERD lacks a measurement-source FK or run-verification flag, propose explicit evidence rules compatible with the schema; escalate before any schema change.

Until accepted: real origin may be unknown/unreviewed, verified counts remain unavailable, numeric outcome derivations remain blocked and asset references are not time series. Synthetic acceptance never counts as curated Data acceptance.

## Dependency record

| Dependency | Owner | Output/evidence | Gate |
| --- | --- | --- | --- |
| Slug entries and lifecycle | Backend validates, project owner approves, Data/Frontend consult | Versioned mapping and collision/stale/retirement examples | Before publishing affected slug |
| Wire payload and adapter | Backend + Frontend | Agreed schemas/examples and consumer tests | Before dependent implementation/integration |
| Curated real dataset | Data + Backend acceptance | Origin/source/unit/status manifests and QA | Before claiming curated scientific collection |
| Verified run/observation rule | Data/scientific reviewer + Backend | Reproducible provenance and review evidence | Before changing unknown verification |
| Derived comparison | Data/scientific reviewer + Backend/Frontend | Accepted compatibility/unit/uncertainty method and examples | Before any numeric delta/rank/average |
| Full telemetry | Data + Backend + Frontend | Asset/time/channel/unit/access contract | Separate reviewed scope |
| Disposable database | Operator/project owner | Target authorization and restricted role evidence | Before any seed/integration writes |

AI has no Phase 4 algorithm dependency. No RAG/model work is assigned here. Escalate schema, identity, scientific and incompatible contract changes; continue independent synthetic backend slices only within their approved scope.
