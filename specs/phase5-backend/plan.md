# Phase 5 implementation plan

Owner authorization received 2026-11-12. Implement P5-01–P5-06 within the existing FastAPI modular monolith. See [spec.md](spec.md), [HTTP contract](contracts/http.md) and [decision record](contracts/review-record.md). Preserve Phase 4 and defer P5-07.

## Layers and transactions

- Add one POST operation at /api/v1/mission/scenarios/evaluate. Use strict camelCase input DTOs, exact decimal strings and a dedicated sanitized error boundary. The request carries optional context and explicit condition quantities, independent page offsets and equality-only continuation bindings.
- Compose versioned providers on the server. Default to unavailable. Explicit test-only composition operates only against admitted synthetic/unreviewed snapshots. Backend owns deterministic fixture-only exact comparisons and structural validation. Data owns scientific rules, ranking computation and classifications.
- Admit the exact collection in the existing PostgreSQL read-only REPEATABLE READ unit of work. Fetch detached UUID-ordered run pages with bounded per-run condition windows. Capture a content fingerprint over admitted fixture/snapshot and slug content. End the read transaction before provider work.
- Validate a complete bounded ranking payload before projecting pages by delivered position. Keep supplied ties, components, score scales, provenance and applicability. Filter classifications by explicit claim mappings. Validate original association ID/document/locator before projecting sources. Page flattened associations by UUID inside the selected pillar scope so every repeated association is reachable without nested cursors.
- Preserve optional values, exact units/precision, raw statuses and independent origin/review. For unavailable methodology return six unavailable summary dimensions and null run results. For evaluated runs require all five compatible records from the same run before returning fixture-only combined support. Compute summaries from examined runs. A multi-page final response does not establish collection traversal.
- Use trusted scenario storage through the existing scenario table and service-owned transaction. Require all stored fields, fixed unit/meaning semantics for Numeric columns, and versioned canonical JSON strings for gravity and ventilation. Verify exact round trip. The public route has no writer and maintains exact collection admission. Runtime history/writer binding and persistence of fields without a lossless mapping are separately gated.

## Limits and verification

Use 20/100 default/max page size, 1,000 conditions per run and 1,000 complete provider entries. Reject whole invalid deliveries, propagate cancellation, apply a five-second deadline and bound JSON bytes, depth and text. No outbound provider, schema or dependency changes. See [provider contract](contracts/providers.md).

Prove strict parsing, same-run references, deterministic replay, original provenance, independent failure, PostgreSQL isolation/round trip and preservation of existing OpenAPI and comparison. Run Poetry, Ruff, full pytest and marked integration against the authorized local targets. Record commands, counts and criterion evidence. Converge on engineering behavior while tracking external acceptance separately. Remove the additive route and provider composition to roll back API code. Runtime storage activation requires a compatible trusted writer and lifecycle decision.
