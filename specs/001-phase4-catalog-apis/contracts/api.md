# Proposed Phase 4 HTTP Contract

Status: review draft, not deployed routes or Frontend acceptance. Formal schemas/parameters: [openapi.json](openapi.json). Base path /api/v1; existing health/ready contracts remain unchanged.

## Canonical conventions

- Public names use camelCase. Add new Pydantic v2 DTOs under app/schemas/api/, with explicit aliases and extra='forbid'; retain existing snake_case persistence schemas.
- UUIDs are canonical API IDs. psiId is external identity, slug is a separately resolved public route identity. Run externalRunKey remains separate. Never pass a slug as a UUID.
- Lists are {items,total,offset,limit,next,context}. Default offset 0/limit 20, max 100; next is null at completion. Counts precede pagination. Follow next until null to retrieve all associations; no silent truncation.
- Each envelope AND detachable entity contains context {collectionId,origin,reviewState,caveats}. Origin is synthetic|real|unknown; reviewState is separately unreviewed|curated|unknown. Caller input cannot override origin. Context errors use unknown if admission fails.
- Null means unknown/absent, [] means no related records in this scope, and 0 is a known numeric count/value. Unsupported fields are named in unavailableFields with explicit reason codes; no invented code/year/confidence appears to satisfy UI types.
- Numeric originals and uncertainty serialize as finite Decimal strings using exact non-exponent formatting, never float. Examples: measuredValue='0', uncertainty=null, valueNumeric='0.10000000000000000001'. Display conversion/rounding is separate and not enabled here.
- condition.dataStatus, claim.evidenceStatus/reviewStatus and source.ingestionStatus are stored raw text. None implies run verification. Run.verification='unknown'; dashboard.verifiedRunCount=null with VERIFICATION_NOT_ESTABLISHED.

## Endpoints

| Method/path (under /api/v1) | Canonical request | Success model / semantics |
| --- | --- | --- |
| GET /catalog/capabilities | No query | Capabilities; supported/unsupported filters/sorts/display fields |
| GET /investigations | q,platform,material,gravityRaw,tag,purpose,sourceType,evidenceStatus,reviewStatus,sort,offset,limit | InvestigationPage |
| GET /investigations/by-slug/{slug} | Canonical lowercase manifest slug | InvestigationDetail, same UUID as direct detail |
| GET /investigations/{investigationId} | UUID | Detail with child links/counts, not full graphs |
| GET /investigations/{investigationId}/tags | UUID + page | TagPage, exact stored tags |
| GET /investigations/{investigationId}/runs | UUID + page | RunPage; conditions/measurements are separately paged |
| GET /runs/{runId}/conditions | UUID + page | ConditionPage; preserve numeric/text/unit/status |
| GET /runs/{runId}/measurements | UUID + page | MeasurementPage |
| GET /investigations/{investigationId}/measurements | UUID + page | ObservationPage, each measurement paired with its run and condition links |
| GET /investigations/{investigationId}/sources | UUID + page | SourcePage |
| GET /investigations/{investigationId}/claims | UUID + page | ClaimPage with first bounded source-association pages |
| GET /claims/{claimId}/sources | UUID + page | ClaimSourcePage; every association in the active collection, including cross-study context |
| GET /dashboard/summary | Same selection filters as catalog, no sort/page | Dashboard; all records belonging to selected investigations, not only the current catalog page |
| POST /compare | CompareRequest | Comparison; read-only, requested study order retained |

Tag and association first pages use limit 20, with total/next links. Use bulk partitioned queries for first pages rather than one query per item. All parent checks distinguish unknown parent (404) from known parent/no children (200 empty page).

## Search, filters, sorting and capabilities

q: literal trimmed case-insensitive substring across present psiId/title/purpose/platform, run material and linked tag label/slug. Escape %, _ and escape characters in LIKE; they are literal input, not wildcard syntax. Blank q is no constraint.

Equality filters are trimmed/case-insensitive over their existing raw values. tag means stored tag slug. purpose is substring. Distinct dimensions combine with AND; material/gravityRaw share one run predicate and evidenceStatus/reviewStatus share one claim predicate. sourceType does not turn a document type into a scientific validation status.

Supported sort values: title-asc (default) and runs-desc, with UUID ties. Unsupported frontend fuel/facility/numeric gravity categories and newest/code/confidence sorts return 422 UNSUPPORTED_CAPABILITY. Additional unrecognized keys return 422 INVALID_REQUEST. Do not map facility to platform or fuel to material silently. Capabilities and errors advertise allowed values; the Frontend team chooses UI disabling/messaging.

Proposed request bounds: q/purpose <=256 characters, each equality filter <=256, one value per query key, no repeated parameter ambiguity. These are HTTP input bounds, not new storage/scientific constraints. Invalid query/body input is rejected without echoing sensitive submitted values.

## Evidence projection

Claim sources are association objects, not a deduplicated document list. Each includes id,claimId,source (with investigationId),testRunId,runInvestigationId,sourceLocator,sourceExcerpt,contextMismatch,context. A null run means source-level context only. A mismatch retains both identities and warning; it cannot establish verification or comparability.

Claim membership in an investigation is through that investigation's documents. Shared claims appear once per claim page; their source pages preserve all eligible associations in the active collection, explicitly including other investigations. Orphan claims are not assigned by text similarity. No measurement-source or direct claim-investigation FK is added.

Sources preserve original URLs/DOI/version/status as stored. This read API performs no arbitrary URL fetching. Missing authors/title/year/limitation cannot be filled from demos, IDs or guessed defaults. Raw assets remain references with ASSET_CONTRACT_PENDING where appropriate.

## Dashboard definitions

Selection filters first select investigation IDs; counts then include their records. Claims are distinct IDs linked through selected source documents. sourceCoverage={numerator: investigations with >=1 source, denominator: selected investigations, ratio: decimal string|null}; zero denominator yields null and NO_DENOMINATOR. Coverage measures linkage, not review. Featured entries are first three in default order with no endorsement claim. Fuel/facility/gravity distributions stay null with UNSUPPORTED_MAPPING. No verified-run fallback or fixed mock KPI is allowed.

## Comparison and scientific gate

Example request (synthetic IDs only):

```json
{"investigationIds":["e1a75331-3f1f-57b8-9042-405ff61dff51","afa58280-0d0c-58a3-926a-1499a1e20a96"],"observationOffset":0,"observationLimit":20}
```

Every study contains Investigation and its independently paged original observations; next links use that investigation's measurement collection endpoint. Run conditions remain reachable through paged links and are not claimed complete until traversed. The body disallows extra fields, requires 2–3 distinct UUIDs, and bounds observation pages 1–100. This is a read operation despite POST.

comparability='not_established', deltas=null and highlights=null with SCIENTIFIC_COMPARISON_NOT_APPROVED. Different unit strings, missing units/context and mismatched provenance remain explicit caveats. Even equal unit strings or equal observed condition values do not establish the same scientific method. Show original values with unit/run/origin/unknown-verification labels; never silently convert, pool, rank, average, choose favorable extrema or compute risk/safety conclusions.

Enabling a future derived outcome requires Data/scientific review of observable meaning, original unit dictionary, conversion/precision, material/geometry/gravity/condition compatibility, measurement method, uncertainty and valid source/run provenance; review comparison examples with Frontend and amend the approved contract first. This plan implements no such algorithm or approval shortcut.

## Error contract

All new endpoints declare 404/422/503 and sanitized 500 in OpenAPI. Use a Phase 4 route-local error boundary so existing health/ready and global behavior remain compatible.

```json
{"error":{"code":"UNSUPPORTED_CAPABILITY","message":"Unsupported capability","fields":["sort"],"supportedValues":["title-asc","runs-desc"]},"context":{"collectionId":"unknown","origin":"unknown","reviewState":"unknown","caveats":[]}}
```

404: ENTITY_NOT_FOUND for valid absent UUID/unknown canonical slug. A known stale manifest entry is 503 IDENTITY_MAPPING_UNAVAILABLE, not a fabricated match. 422: INVALID_REQUEST or UNSUPPORTED_CAPABILITY; comparison duplicate/size/format and unknown query keys are rejected. 503: DATA_UNAVAILABLE, COLLECTION_SCOPE_INVALID or IDENTITY_MAPPING_UNAVAILABLE. Unexpected errors are 500 INTERNAL_ERROR, with only safe class-level logging. Reject mixed-origin comparison/scope as 503 rather than returning partial results. Never echo credentials, DSNs, request bodies, stack traces or local paths.

## Acceptance and OpenAPI verification

These files are the proposed wire baseline, not generated runtime proof. After implementation, verify real app.openapi() includes each proposed operation plus unchanged health/ready; validate required fields, camelCase aliases, UUID/date formats, nullability, Decimal strings, limits and error declarations. HTTPX must exercise each documented example/error, multi-page association traversal and exact original values. Verify runtime responses and Pydantic JSON-mode serialization, not merely identical snapshots.
