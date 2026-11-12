# Phase 5 HTTP engineering contract

Owner-authorized backend operation on 2026-11-12. Consumer acceptance F-01 is pending. The existing Phase 4 surface remains in service.

## POST /api/v1/mission/scenarios/evaluate

```json
{
  "scenario": {
    "name": "TEST_ONLY zero gravity",
    "environmentLabel": "fixture",
    "material": {"key": "TEST_MATERIAL_A"},
    "gravity": {"value": "0.00", "unit": "g"},
    "oxygen": {"value": "21", "unit": "%", "meaning": "ambient_oxygen_fraction_percent"},
    "pressure": {"value": "14.7", "unit": "psia"},
    "airflow": {"value": "0", "unit": "cm/s"}
  },
  "pillar": null,
  "pages": {"runOffset": 0, "rankingOffset": 0, "evidenceOffset": 0, "limit": 20}
}
```

Only scenario is required. Optional context includes name, description, environmentLabel and presetKey. Explicit null and omitted fields are retained by interpreted field-state metadata. Original lexical decimals survive unchanged. Quantities require unsigned finite decimal strings with up to 32 fractional digits and 64 total characters. Oxygen is bounded at 100 and requires explicit ambient or oxidizer fraction meaning. Accepted units are g, %, psia and cm/s for the respective fields. Engineering validation adds no environmental defaults, unit conversions or scientific tolerance. Material and preset keys are bounded tokens. Unknown fields, duplicate keys, extra query parameters, wrong JSON types, JSON bodies over 32 KiB and out-of-range pagination receive a sanitized 422 before service work.

Results contain scenario interpretation, context, scope bindings and independent coverage, rankings and pillarEvidence. States are evaluated, unavailable or rejected. Affected lists are null when unavailable or rejected, and empty for evaluated empty pages. Test-only records are labeled synthetic/unreviewed with TEST_ONLY versions. Unreviewed real or unknown collections retain their origin and get unavailable scientific sections.

Coverage contains six explanations at page and run level. Only the same run can supply all five inputs for combined support. Per-run decisions carry original condition references, units and raw status. The condition table carries no per-condition uncertainty or locator, which are explicitly null. Measurements and their original uncertainty remain accessible through the Phase 4 observation APIs. Unknown, mismatch and partial statuses describe fixture evidence. Summary scope is the examined page. A final page in a multi-page collection cannot prove collection-wide traversal or absence.

Ranking preserves complete validated provider delivery order and ties. Scenario relevance, catalog usefulness and component scores retain distinct meanings and fixture scales. Pillar evidence carries original claim and association records in UUID order. Repeated documents remain separate associations. Empty evaluated groups and groups with entries outside the current page have distinct reasons. Source/run disagreement remains explicit. See [provider contract](providers.md).

Replay the same scenario and pillar with the section's nextRequest pages and expectedBindings. Offsets are strict integers 0–1,000,000 and limit is 1–100 with default 20. Each nextRequest advances its section and restarts the others at offset zero. Missing or changed bindings give 409. Common bindings cover exact admitted database and manifest originals, slug mapping, identity and scenario interpretation. Coverage additionally binds rule and run mapping versions. Ranking and pillar pages each bind their validated delivery content. When the public offset ceiling prevents another page, continuationLimited is true.

The evaluation API has no stored identity or write operation. Trusted compatible scenario storage is described in [data-model.md](../data-model.md).

| Status | Code or result |
| --- | --- |
| 200 | Independent sections, with reason codes for unavailable, rejected or empty evidence |
| 409 | VERSION_CONFLICT |
| 422 | INVALID_REQUEST |
| 503 | DATA_UNAVAILABLE or COLLECTION_SCOPE_INVALID |
| 500 | INTERNAL_ERROR |

Errors use the existing outer error shape with Phase 5 codes, fixed messages, empty fields/supportedValues and unknown context. A valid provider reference absent from its declared scope causes section rejection. The request accepts no entity selector or provider/database selection.
