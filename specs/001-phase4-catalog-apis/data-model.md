# Phase 4 Read Model and Identity Design

Proposed projections over the frozen schema. No table/column/FK/constraint/migration is added. Physical authority remains docs/phase-2-database-implementation.md.

## Existing entities reused

| Entity | Preserved fields | Constraints/context |
| --- | --- | --- |
| Investigation | id, psi_id, title, research_purpose?, platform? | Runs, documents, tag links; no slug/rich metadata column |
| TestRun | id, investigation_id, external_run_key?, material_type?, sample_geometry?, gravity? | Original string gravity; external key not globally unique |
| TestCondition | id, test_run_id, variable, value_numeric?, value_text?, unit?, data_status | Both numeric/text may exist; no new exclusivity constraint |
| Measurement | id, test_run_id, observable, measured_value?, unit, raw_asset_ref?, uncertainty? | No source FK, origin, review flag or telemetry array |
| SourceDocument | id, investigation_id, source_url, doi?, document_type, version?, ingestion_status | No invented bibliographic title/authors/year |
| EvidenceClaim | id, claim_text, evidence_status, review_status, limitation?, created_at | Investigation association derives through documents |
| ClaimSource | id, claim_id, source_document_id, test_run_id?, source_locator, source_excerpt? | Distinct repeated links preserved; mismatch flagged, not silently erased |
| Tag / InvestigationTag | IDs, slug, label, category? / association IDs | No automatic scientific taxonomy |

Other tables remain untouched. Canonical demo fixtures leave them empty; seed admission checks all 21 tables.

## File manifests and read context

- Slug manifest: version, collectionId, entries {slug, psiId}; lowercase ASCII canonical slugs, exact lookup and uniqueness per collection. UUID resolves from psi_id. Unknown/noncanonical slug is 404; a stale entry is safe 503 identity-mapping-unavailable. Published reuse/retirement requires owner compatibility review.
- Collection manifest: collectionId/version, origin synthetic|real|unknown, reviewState unreviewed|curated|unknown, identity/fixture references and target binding. Origin and review are separate; curated collection status never verifies every run. A real curated declaration requires Data acceptance.
- Local target authorization: ignored operator-owned .tools/ file pins endpoint, DB, role, DB OID/owner, development/test environment and exclusive-disposable approval. Credentials remain outside versioned files.
- Fixture manifest: fixed UUIDs (dedicated deterministic namespace), synthetic PSI IDs/tag slugs, stable required timestamps, exact rows/values, expected counts/results and distinct source-association identities.

Synthetic admission validates target binding and every row against the manifest within each read transaction; cache parsed manifests, not stale database approval. Drift/mixed contents return safe 503 COLLECTION_SCOPE_INVALID. API uses a read-only role on the exclusive dataset. Real/unknown admission never infers curated origin from missing labels; recognized synthetic fixture records cause refusal of a real collection. Real mode publication requires Data acceptance and no synthetic mixing.

## Public projection mapping

Formal required/nullability rules: [OpenAPI](contracts/openapi.json). Behavioral semantics/examples: [API](contracts/api.md).

- ResponseContext on each envelope/detachable entity: collectionId, origin, reviewState, caveats. Errors use unknown context if admission fails.
- Availability map: reason-coded absent/unsupported fields and unknown verification; missing scalar values remain null and true zero stays zero.
- InvestigationView: canonical identity, psiId, optional slug, title/purpose/platform, tags, unavailableFields, context. Detail adds links to independently paged children.
- RunView: canonical/run/investigation identity, external key/material/geometry/string gravity, context, unavailable verification, condition/measurement links.
- ConditionView/MeasurementView: exact original fields with camelCase names, finite decimal strings/null and original units. Rounded display values are separate and not implemented here.
- SourceView: original document/investigation/URL/DOI/version/type/status and context, no fabricated citation metadata.
- ClaimView: original text/status/limitation/UTC timestamp, context and first bounded sources page with totals/next link. /claims/{id}/sources exposes later pages.
- ClaimSourceView: association/claim IDs, SourceView, optional runId/runInvestigationId, locator/excerpt, contextMismatch and context. Repeated document links remain distinct.
- ObservationView: MeasurementView plus RunView; original conditions remain reachable through paged links. Unretrieved context does not grant comparability.
- DashboardView: selected-scope counts, coverage numerator/denominator/decimal ratio, unknown verifiedRunCount with reason, unavailable unmapped distributions, up to three featured entries.
- ComparisonView: ordered identities, contextual original observation pages, unavailable derived metrics/highlights, explicit unit/context caveats; no persistence.

## Validation and lifecycle

1. UUID fields validate format; absent canonical identity is 404. Compare accepts 2–3 distinct UUIDs and rejects the whole request on missing identity.
2. Offset >=0, limit 1–100. Original Numeric values/uncertainty serialize exactly as finite decimal strings without new scientific rounding/range restrictions.
3. Unknown query/body keys are rejected. Raw stored statuses stay strings; unsupported capabilities are safe 422 with supported values.
4. Manifests proceed through proposed → owner-reviewed → consumer-accepted publication as document states, not DB columns.
5. HTTP reads, including POST comparison, never write. Only the separately authorized seed flow inserts atomically.

## Planned fixture coverage

At least four investigations A–D: A/B share a claim with repeated locator associations; A has zero/null observations and mixed units; B has different run conditions; C lacks optional metadata; D has no runs/sources. Include a labeled source/run mismatch, an unlinked claim excluded from investigation membership, tied titles and numeric/text conditions. Use deterministic larger TEST_ONLY variants for pagination. URLs use example.invalid, DOI is null, and existing free-text status fields use TEST_ONLY/SYNTHETIC_UNREVIEWED rather than verified/NASA labels. No actual fixture data is created by this plan.
