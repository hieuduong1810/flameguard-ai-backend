# Feature Specification: Phase 4 Catalog and Evidence APIs

**Feature Branch**: `main` (current branch; no branch hook is configured and no feature branch was created)

**Feature Directory**: `specs/001-phase4-catalog-apis`

**Created**: 2026-11-11

**Status**: Draft for owner review. Specification only; planning and implementation have not started.

**Input**: Phase 4 Catalog, Dashboard, Explorer, Investigation Detail, Source Evidence and Comparison APIs; include runs, conditions, measurements and clearly labeled synthetic development data. Support the existing frontend experience while preserving Phase 1–2, the finalized schema, separate identities, missing values, original units and evidence limitations. Exclude NASA scraping/ETL, Data Team production import, AI RAG, prediction, frontend edits and deployment. Create this specification only and stop before planning.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find investigations in the catalog (Priority: P1)

As a researcher, I can search and narrow the catalog, move through results and open an investigation without confusing its public slug, internal identity or external PSI identity.

**Why this priority**: Explorer is the entry point for detail, sources and comparison.

**Independent Test**: Use a declared synthetic catalog with matching and nonmatching investigations, shared tags, multiple runs, missing metadata and tied sort values. Verify exact membership, counts and stable page traversal.

**Acceptance Scenarios**:

1. **Given** supported searchable fields and a keyword with different case or outer whitespace, **When** the catalog is searched, **Then** matching records are returned without inventing code, author, institution or other absent fields.
2. **Given** supported filters, **When** filters are combined, **Then** records satisfy all filters and joins do not duplicate investigations or inflate totals. Run-based filters must match the same run.
3. **Given** an unchanged dataset with multiple pages and tied sort values, **When** all pages are traversed, **Then** each matching investigation appears once and its total is independent of page size.
4. **Given** an unsupported frontend filter or sort, **When** requested, **Then** the request is explicitly rejected as unsupported with available capabilities, rather than ignored or interpreted using unrelated fields.
5. **Given** no matches or an offset beyond the final match, **When** results are requested, **Then** the list is empty with an accurate total and pagination metadata.

### User Story 2 - Read investigation details, runs and observations (Priority: P1)

As a researcher, I can inspect individual runs, original experimental conditions, scalar observations and references to raw assets.

**Why this priority**: Experimental context and missing-data handling are prerequisites for responsible evidence use.

**Independent Test**: Inspect multiple runs with numeric/text conditions, measured zero, missing observations, uncertainty, mixed units and missing optional metadata.

**Acceptance Scenarios**:

1. **Given** a known UUID or registered public slug, **When** detail is requested, **Then** both identify the same investigation, retain its separate PSI identity and disclose unavailable display fields.
2. **Given** numeric and textual conditions, **When** viewed, **Then** original variable, values, unit and recorded condition status remain distinguishable; missing numeric values do not become zero.
3. **Given** measured zero, missing observations and unknown uncertainty, **When** viewed, **Then** zero stays zero, unknown stays unknown and uncertainty is not fabricated.
4. **Given** an asset reference without an agreed time-series contract, **When** viewed, **Then** the reference and availability limitations are preserved without generated telemetry points or channels.
5. **Given** a known investigation without runs, **When** its run collection is requested, **Then** an empty collection is returned; an unknown investigation instead produces not found.

### User Story 3 - Inspect source evidence without losing provenance (Priority: P1)

As a researcher, I can trace each claim to all its original source associations, exact locators, available excerpts and optional run context.

**Why this priority**: A readable claim must not conceal its evidence basis or limitations.

**Independent Test**: Use a synthetic claim linked to multiple documents, repeated links to one document at different locators, links with/without run context and a claim shared across investigations.

**Acceptance Scenarios**:

1. **Given** several source associations, **When** a claim is returned, **Then** every eligible association retains its identity, document identity, locator, optional excerpt and optional run identity; a singular DOI cannot replace the set.
2. **Given** a claim shared by investigations A and B, **When** read in A's scope, **Then** it appears once, all associations within the selected data scope remain available, and each document/run retains its actual investigation context. The response does not imply every source belongs to A.
3. **Given** missing DOI/version or limitation text, **When** evidence is returned, **Then** absent metadata remains unknown; missing limitation text does not mean no scientific limitations exist.
4. **Given** a link whose run belongs to a different investigation than its document, **When** displayed, **Then** both contexts and a mismatch warning remain visible. The link cannot establish verification or numeric comparability.
5. **Given** a claim without source associations, **When** investigation claims are requested, **Then** text similarity or an invented relationship does not assign that claim to the investigation.

### User Story 4 - Understand the dashboard collection (Priority: P2)

As a researcher, I can understand the selected collection and distinguish unknown, unreviewed and synthetic summaries.

**Why this priority**: Summary cards must describe collection contents without implying scientific validation.

**Independent Test**: Reconcile dashboard counts with a declared fixture manifest containing shared claims, missing classifications and an empty collection.

**Acceptance Scenarios**:

1. **Given** a selected collection, **When** its dashboard is requested, **Then** distinct investigation, run, claim and source counts reconcile with the same collection; provenance links do not multiply claims.
2. **Given** no approved run-verification rule, **When** verified-run information is requested, **Then** it is unknown/unavailable; total runs cannot substitute for verified runs.
3. **Given** missing fuel/facility mappings, **When** distributions are requested, **Then** unavailable dimensions are explicit and unknown classifications are not assigned to guessed categories.
4. **Given** an empty collection, **When** summarized, **Then** known counts are zero, zero-denominator ratios are unavailable with a reason and no fallback NASA/demo totals appear.

### User Story 5 - Compare two or three investigations (Priority: P2)

As a researcher, I can compare metadata and labeled observations side by side while understanding experimental context, units and evidence readiness.

**Why this priority**: Comparison enables exploration without turning unmatched observations into scientific conclusions.

**Independent Test**: Select two and three synthetic investigations with matched/unmatched observables, incompatible units, different conditions, missing values and unknown verification.

**Acceptance Scenarios**:

1. **Given** two or three distinct existing investigation UUIDs, **When** compared, **Then** selection order, separate identities, runs, original observations and caveats are preserved.
2. **Given** observations from different runs, **When** displayed, **Then** each retains observable, unit, uncertainty, run identity and conditions; no common experimental context is implied.
3. **Given** unknown verification or compatibility, **When** numeric outcome comparison is requested, **Then** labeled original observations may appear side by side, while derived deltas, ratios, rankings, averages and superiority highlights are unavailable with reasons.
4. **Given** incompatible/unknown units, **When** compared, **Then** original values and mismatches remain explicit; values are not silently converted or pooled.
5. **Given** fewer than two, more than three, duplicate, malformed or unknown identities, **When** comparison is requested, **Then** the entire request fails clearly instead of silently reducing the selection.

### User Story 6 - Exercise capabilities with identifiable synthetic data (Priority: P1)

As a developer, I can exercise Phase 4 before curated data arrives without mistaking fixtures for NASA experiments or verified findings.

**Why this priority**: Development can proceed without fabricating scientific data or taking over Data Team responsibilities.

**Independent Test**: Inspect every response, including empty/aggregate responses and items detached from their parent response, in an explicitly selected synthetic collection.

**Acceptance Scenarios**:

1. **Given** synthetic data, **When** any response or detached item is inspected, **Then** its context identifies it as synthetic with a non-NASA caveat; it is never described as curated or verified.
2. **Given** a normal environment without imported records, **When** read, **Then** it stays empty; synthetic data is not automatic fallback behavior.
3. **Given** stable synthetic fixture identities/counts, **When** preparation is repeated in its approved isolated target, **Then** counts and identities remain deterministic without replacing unrelated data.
4. **Given** synthetic and real collections, **When** listed, summarized or compared, **Then** their scopes cannot mix; ambiguous origin cannot be promoted to curated status.

### Edge Cases

- Empty collections, whitespace-only search, no matches, tied ordering and pagination past the final result.
- Negative offsets, zero/excessive limits, unrecognized filters/sorts and malformed or oversized requests.
- Valid unknown UUID versus malformed UUID; slug or PSI ID supplied where UUID is required.
- Missing/duplicate slug mappings, attempted slug reuse and stale references to absent investigations.
- Identical external run keys in different investigations; external keys are not assumed globally unique.
- Zero versus null, absent uncertainty/unit where allowed, unknown categories and conditions with both numeric/text values.
- Shared claims, repeated document links, multiple locators and source/run investigation mismatches.
- Source URL present without review, unknown source accessibility or unavailable raw asset; no source fetching is implied.
- Database unavailability yields a sanitized unavailable result, not successful emptiness or synthetic fallback.
- Empty classifications/zero denominators yield no fabricated percentages or Infinity/NaN.
- Conflicting origin/verification metadata cannot establish curated/verified status; synthetic evidence cannot verify real records.

## Requirements *(mandatory)*

### Functional Requirements

#### Collection, identity and frontend compatibility

- **FR-001**: Provide read capabilities for dashboard summary, discovery/detail, runs with conditions/measurements, original sources, claims with provenance and comparison of two or three investigations. Comparison does not persist scientific outcomes.
- **FR-002**: Preserve investigation UUID, external PSI ID, public slug, run UUID/external key, document UUID/URL/DOI and claim/association identities separately. Never substitute one identity for another.
- **FR-003**: Resolve public slugs through a separate identity manifest without schema changes. Map one unique slug to one external PSI identity and resolve the current canonical UUID. Backend validates; the project owner approves entries, Data confirms real identity and Frontend confirms route compatibility. Synthetic entries are explicitly scoped to synthetic data. Reject duplicate/conflicting mappings; missing entries are unavailable/not found, never title-generated. Retiring/reassigning a published slug needs owner review and compatibility handling.
- **FR-004**: Use existing stored fields. Mark absent rich display fields unavailable with reasons, including code, hardware/facility, fuel category, dates, investigator, institution, findings, confidence and bibliographic metadata. Do not infer them from names, frontend mocks or nearby records. No display-metadata manifest is authorized.
- **FR-005**: Expose supported/unavailable filter, sort and display capabilities. Supporting the frontend means providing suitable data and unknown states, not asserting that current non-null mock types consume responses unchanged. Frontend owns its adapter and consumer sign-off.

#### Discovery and summaries

- **FR-006**: Support trimmed case-insensitive substring search over present PSI ID, title, purpose, platform, run material and linked tag labels/slugs. Blank search adds no keyword constraint. Searching absent rich fields is unavailable.
- **FR-007**: Support exact-value filtering of present platform, run material, raw run gravity string, tag, source document type and recorded claim evidence/review status, plus substring purpose filtering. Text matching is trimmed and case-insensitive; distinct dimensions combine with AND. Run-based filters match the same run. Status matching does not establish verification.
- **FR-008**: Frontend fuel/facility categories, numeric gravity categories, newest/code/confidence sorting and claim categories remain unsupported until approved mappings exist. Never silently equate platform with facility, material with fuel category or gravity strings with numeric categories. Later mappings require reviewed contract decisions.
- **FR-009**: Default order is title ascending with UUID tie-breaker; run-count descending also uses UUID ties. Defaults are offset 0/limit 20; permit nonnegative offsets and positive limits up to 100. Totals count distinct matching entities before pagination. Bound related collections independently and permit retrieval of all source associations without silent truncation. Page guarantees apply to an unchanged collection, not an invented cross-request import snapshot.
- **FR-010**: Summarize distinct investigation, run, source and associated-claim counts, document linkage coverage, classification availability and featured entries in a declared collection/filter scope. Summary filters select investigations before aggregating their records. Count each claim once if linked to a selected source. Document coverage means selected investigations with at least one document divided by selected investigations, exposing numerator/denominator; it is not source verification.
- **FR-011**: Feature up to three entries in default order as catalog entries, not scientifically endorsed studies. Unmapped fuel/facility/gravity distributions are unavailable with reasons. Grouping existing tags uses recorded labels and preserves unclassified counts without invented taxonomy.
- **FR-012**: Verification-dependent totals, counts and badges remain unknown/unavailable without an approved rule and evidence. Total runs, condition status, DOI, ingestion status or publication-looking labels do not verify a run/measurement. Known total counts can be zero while verification remains unknown.

#### Details, observations and provenance

- **FR-013**: Detail exposes available identity, title, purpose, platform, tags, origin and discoverable runs/sources/claims with completeness/caveats. Known parents with no children return empty collections; unknown parents return not found.
- **FR-014**: Runs retain investigation identity, UUID, external key, material, geometry and original string gravity. Conditions retain variable, numeric/text values, original unit and recorded status. No forced mapping to fixed numeric frontend fields precedes an approved unit/vocabulary contract.
- **FR-015**: Measurements retain measurement/run identity, observable, original value/unit, optional uncertainty and asset reference. Zero remains zero; missing remains unknown. Original-value representation preserves scientific decimal precision; later rounded displays are separate and labeled. Do not infer unsupported boolean observations from decimals.
- **FR-016**: Asset references are not embedded telemetry. This scope covers scalar observations and asset-reference availability, not asset fetching/parsing, fabricated time-series or downsampling. Full baseline telemetry delivery remains dependent on a separate Data/Frontend asset contract.
- **FR-017**: Sources retain document/investigation identity, original URL, optional DOI/version, type and ingestion status. Do not invent title/authors/year, successful retrieval or review from identifiers. Return references as data; do not fetch arbitrary caller-supplied URLs.
- **FR-018**: Claims retain identity/text, recorded evidence/review statuses, limitation and all association identities, original documents, exact locators, optional excerpts and optional run contexts. Repeated links remain distinct. Never flatten to a singular citation or invent direct claim-investigation/measurement-source relationships.
- **FR-019**: Investigation claim membership derives from links to its documents. Optional run context cannot reassign document ownership. A shared claim appears once and retains all associations within the selected data scope, including explicitly identified cross-investigation associations. Flag source/run mismatches and exclude them from verification/comparability assertions without deleting original provenance.
- **FR-020**: Unlinked claims cannot be assigned to investigations. Research limitations, unknown review and missing-source caveats survive every projection/summary/comparison. Linkage must never be described as scientific validation.

#### Comparison and synthetic data

- **FR-021**: Accept only two or three distinct canonical investigation UUIDs. Preserve requested order, reject malformed/duplicate identities as invalid, and fail the whole comparison if any valid identity is missing. Do not mix origins or omit selected studies silently.
- **FR-022**: Compare stored metadata and original observations side by side with run conditions, unit, uncertainty, origin and limitations. Unmatched observables/contexts remain unmatched, not zero. Do not pool incompatible contexts/units or select a favorable run as an investigation-wide outcome.
- **FR-023**: Pending approved verification and scientific comparison rules, derived outcome deltas, ratios, averages, ranks, superiority highlights and verified numeric conclusions are unavailable with reasons. Original observations, including synthetic ones, may be inspected with explicit labels. No risk probability or safety conclusion is produced.
- **FR-024**: The future deterministic synthetic collection must contain at least four investigations, multiple runs, conditions, observations, documents, shared claims/locators and tags. Cover every acceptance/edge case, including unknown metadata, zero/null values, mixed units and provenance mismatches. Document expected counts/identities and intentionally invalid or unverified cases.
- **FR-025**: Use unmistakably synthetic names/identifiers, non-resolving example source references and no invented real NASA/DOI attribution. Every response, including empty/aggregate responses and detached items, carries sufficient origin/caveat context. Origin is separate from recorded review/status text; no new persistence field is implied.
- **FR-026**: Synthetic preparation is explicit, repeatable and restricted to an approved isolated development/test target, with stable fixture identities and no startup/request-time loading. Refuse shared/curated targets or mixed-origin collections; preserve unrelated rows and obtain separate cleanup/reset approval. Actual fixture preparation/import is outside this specification task.
- **FR-027**: Absence of a synthetic label does not establish curated origin. Real-data delivery, origin acceptance and provenance/status dictionaries remain Data-owned. Empty real-data environments stay empty; missing dependencies never trigger fabricated NASA data.

#### Errors, ownership and delivery

- **FR-028**: Distinguish invalid input, unsupported capability, missing entity, empty result and unavailable dependency. Use consistent sanitized errors with no secrets, connection strings, stack traces or private paths. Existing proposed error conventions are the starting point; review final wire examples before implementation.
- **FR-029**: Preserve the 21-table schema, migration history, Phase 1–2 behavior, original diagrams and Poetry. No new authentication, persistence field, scientific algorithm, scenario analysis, RAG, prediction, frontend change, deployment or production import is included.
- **FR-030**: Before behavior implementation, review request/response examples covering identities, pagination, errors, unsupported fields, origin labels, exact values and full provenance. Contract/acceptance verification covers all six journeys and listed edge cases with synthetic inputs. Backend verification is distinct from Frontend rollout and Data scientific acceptance.

### Key Entities *(include if feature involves data)*

- **Investigation**: Available catalog identity/title/purpose/platform, linked runs, tags and documents; separate public slug and PSI identity.
- **Public identity manifest**: Owner-approved slug-to-PSI mapping resolved to canonical identity and scoped by origin; not a new database entity.
- **Test run**: Experimental context with separate internal/external identity and related conditions/measurements.
- **Condition**: Original variable, numeric/text values, unit and status; not evidence of run-wide verification.
- **Measurement**: Original scalar observable/value/unit and optional uncertainty/asset reference; not a telemetry array or direct document link.
- **Source document**: Original identity, investigation, URL, DOI/version where present and recorded ingestion status.
- **Claim and source association**: Claim/status/limitations and many-to-many documents, locators, excerpts and optional runs.
- **Tag association**: Recorded classifications, not an automatically approved fuel/facility taxonomy.
- **Origin and availability**: Response context distinguishing synthetic, curated, unreviewed and unknown origin and missing/unsupported reasons; no schema addition.
- **Comparison result**: Ordered studies with contextual observations and explicit caveats; not persisted or validated model output.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six journeys pass their acceptance scenarios against a documented synthetic collection and an independently exercised empty collection. This proves backend capability, not NASA validation or Frontend deployment.
- **SC-002**: Discovery membership and summary counts match 100% of declared expected fixture results; stable page traversal returns every matching identity exactly once.
- **SC-003**: Returned claims preserve 100% of eligible source associations with exact locators/context, without inflating entity totals.
- **SC-004**: Every synthetic response and detachable fixture item is identifiable as synthetic; none is presented as NASA/curated/verified and no mixed-origin aggregate is accepted.
- **SC-005**: Every zero, missing-value, original-unit and uncertainty example survives read/comparison journeys without silent replacement, conversion or fabrication.
- **SC-006**: All valid two-/three-study comparisons retain identity/order/context; invalid selections fail as specified and blocked derived numeric conclusions carry explicit unavailable reasons.
- **SC-007**: Every affected journey represents unsupported metadata and unknown verification explicitly, with zero fallback verified counts, invented confidence tiers or implied validated safety conclusions.
- **SC-008**: Each supported frontend surface has a reviewed consumer example identifying supported values, unavailable fields and adapter obligations before implementation begins. This draft does not assert Frontend sign-off.

## Assumptions

### Scope and approved clarification decisions

- The user's 2026-11-11 answers authorize: (1) a separate, owned, collision-checked slug manifest without schema changes; (2) existing stored fields with explicit unavailable/unsupported behavior for unmapped frontend metadata, pending Frontend review; (3) unknown/unavailable verification with metadata and labeled original observations side by side, without verified numeric outcomes pending Data sign-off.
- These answers resolve this draft's three material questions, but do not approve the full specification, scientific status vocabulary or cross-team contract acceptance.
- This is one feature specification with independently testable journeys. Slice decomposition belongs to later planning. No plan, tasks, fixture dataset or endpoint is created now.
- Existing endpoint proposals remain the starting surface; baseline presence is not implementation evidence or final payload approval. Default title ordering, raw-field filters and unavailable capabilities are explicit proposals for this review.
- Measurements and raw references are in scope. Full time-series delivery remains a prerequisite-dependent baseline capability pending an approved asset contract; no baseline document is rewritten here.
- Anonymous research reads retain the existing demo security boundary; no credential/account flow is introduced.

### Team dependencies and acceptance gates

| Dependency | Owner | Required artifact / acceptance | Current status |
| --- | --- | --- | --- |
| Public identity | Backend validation; owner approval; Data/Frontend consult | Collision-safe manifest examples and missing/stale/retired mapping behavior | Approach selected; entries and consumer contract pending |
| Frontend compatibility | Backend + Frontend | Agreed examples, unknown/unsupported states, identity adapter and full-provenance display | Existing frontend read-only inspection; consumer agreement pending |
| Scientific data/status | Data; Backend acceptance | Curated delivery, origin/identity manifest, unit/status vocabulary and QA | Pending; synthetic development permitted |
| Run/measurement verification | Data review + Backend acceptance | Reproducible provenance/verification rules compatible with frozen schema | Pending; unknown behavior selected |
| Numeric outcome comparison | Data/scientific reviewer + Backend/Frontend | Compatibility, units, aggregation and uncertainty rules | Pending; original observation display only |
| Full telemetry | Data + Backend + Frontend | Asset/channel/time/unit/uncertainty and access contract | Pending; no fabricated series |

Unknown verification and unavailable display fields are specified states, not blockers to this specification. Required consumer/scientific decisions block only dependent implementation or validated-data claims. No team has been contacted or represented as approving a contract.

### Context and source alignment

Source precedence follows the documentation map. Reviewed context includes:

- [Instructions](../../AGENTS.md), [README](../../README.md), [Constitution](../../.specify/memory/constitution.md), [status](../../docs/project-status.md) and [documentation map](../../docs/documentation-map.md).
- [Architecture/roadmap](../../docs/backend-implementation-plan.md), especially scientific invariants and the preliminary Phase 4 contract; [Phase 2 mapping/evidence](../../docs/phase-2-database-implementation.md) and existing catalog/evidence models.
- Approved diagrams [D03](../../docs/diagram/03-database-must-have-erd.mmd), [D08](../../docs/diagram/08-research-dashboard.mmd) and [D09](../../docs/diagram/09-explorer-and-comparison.mmd). D09's numeric-outcome restriction remains: inspecting labeled original values does not authorize derived verified outcomes.
- [Ownership](../../docs/team-ownership.md), [ADR-0001](../../docs/decisions/ADR-0001-phase3-ownership.md), [Frontend draft](../../docs/contracts/frontend-backend-api.md) and [Data handoff draft](../../docs/contracts/data-handoff.md). Drafts remain drafts.
- Read-only sibling frontend: `src/types/index.ts`, `src/lib/explorerFilters.ts`, `src/lib/comparisonUtils.ts`, Dashboard KPI/distribution components and investigation detail client. Mock code/year/confidence, fallback verified counts and fixed telemetry types are consumer context, not scientific truth.

### Entry, deliverable, verification and exit for Specify

- **Entry**: User Phase 4 scope, Phase 1–2 constraints, installed template resolved, clean starting Git state and relevant backend/frontend context inspected.
- **Deliverable**: This draft and its requirements-quality checklist; an ignored local feature pointer identifies the directory for later commands.
- **Verification**: Check requirements against source precedence, user clarification answers, journeys, edge cases, outcomes, ownership and schema preservation; validate links/artifact scope. Application tests and database writes are unnecessary for this specification-only edit.
- **Exit**: Hand off for owner review and stop. Planning requires a subsequent instruction after review; implementation/completion cannot be inferred from this draft or a checked quality checklist.
