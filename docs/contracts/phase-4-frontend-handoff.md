# Phase 4 Backend → Frontend handoff

Status: backend implementation/contract verification available for synthetic collections; Frontend consumer acceptance is PENDING. No frontend files were edited and no team messages were sent.

Wire baseline: [API behavior](../../specs/001-phase4-catalog-apis/contracts/api.md), [OpenAPI](../../specs/001-phase4-catalog-apis/contracts/openapi.json). Backend OpenAPI exposes 14 Phase 4 operations plus unchanged health/ready. Runtime HTTP/PostgreSQL evidence is in [the verification record](../phase-4-api-verification.md).

## Consumer mapping

- Keep canonical dto.id (UUID) for backend requests, dto.psiId for external identity, and dto.slug separately for existing public routes. Slug lookup uses reviewed file mappings; missing/noncanonical slugs are 404, stale mappings are unavailable. No title-derived identity.
- Context exists on envelopes and detachable entities. Preserve declared origin and independent reviewState, including empty/aggregate responses. Synthetic demo responses use synthetic/unreviewed; bound non-synthetic collections can use real/unknown origin and unreviewed/unknown review. The absence of synthetic content never proves curated data.
- Scalar originals/uncertainty are exact decimal strings or null. Preserve the original string and unit when formatting display values; never turn null into zero or silently round the source.
- Read /catalog/capabilities before offering controls. Supported stored-field filters are q/platform/material/gravityRaw/tag/purpose/sourceType/evidenceStatus/reviewStatus. Unmapped fuel/facility/numeric-gravity/newest/code/confidence controls are explicitly unsupported. Missing rich display metadata is listed in unavailableFields, not manufactured.
- Pages carry items,total,offset,limit,next,context. Traverse all next links. Detail/tag/claim previews are bounded; no unqualified flat array promises completeness.
- Runs expose separate condition/measurement pages; original gravity stays a string. Assets are references only; full telemetry remains unavailable pending a Data asset contract.
- Claim sources retain association UUID, original Source identity/URL/DOI, exact locator, optional excerpt and optional run/context. Repeated document links remain distinct. Preserve access to all sources when presenting a primary citation; contextMismatch is a warning, not a deletion.
- Comparison accepts 2–3 distinct UUIDs, retains order and original observation pages. comparability=not_established, deltas/highlights=null. No fallback verified count, inferred safe/unsafe verdict or generated ranking is provided.

## Examples and errors

Demo examples and expected counts are [documented](../../data/demo/README.md). For an admitted collection, list/detail/run/source/claim/comparison responses label every item synthetic. Unknown optional metadata remains null/unavailable. A known parent with no children is 200/empty; unknown UUID/slug is 404; invalid/unsupported request is safe 422; DB/collection/mapping failure is 503; unexpected failure is safe 500.

Before rollout, Frontend and Backend must review these examples against actual adapter behavior, unknown display states, source-page traversal, decimal precision and slug lifecycle. Backend tests do not prove a browser integration or grant Frontend sign-off. Actual frontend changes remain owned by that team.

## Remediation handoff — 2026-11-12

Public inputs accept only declared camelCase keys. JSON comparison page integers reject booleans, floating-point numbers and numeric strings; normal URL pagination remains supported. Comparison context caveats now identify page-scoped observable/unit/run-label differences, unmatched labels, missing values/run metadata and missing or unexamined conditions. Partial-page absence never asserts investigation-wide absence. Original observations and unavailable derived outcomes retain the existing response schema.

T078 remains **BLOCKED: Frontend acceptance evidence unavailable**. Required owner evidence: actual reviewer/date, reviewed contract/examples and accepted scope for identity/slug, unavailable controls/display, decimals and full provenance traversal. No feedback or sign-off was supplied by this implementation request. No team messages or Frontend changes were performed.
