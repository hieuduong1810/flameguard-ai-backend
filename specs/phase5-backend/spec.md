# Feature Specification: Phase 5 Mission Scenario Evidence

**Feature Branch**: `feat/phase5-scenario-matching` (existing branch; no branch created)

**Created**: 2026-11-12

**Status**: Owner-authorized backend engineering scope. External acceptance pending.

**Input**: User description: "Create exactly one distinct backend feature for PROJECT PHASE 5. Set SPECIFY_FEATURE_DIRECTORY explicitly to specs/phase5-backend. Use the approved corresponding Phase 5 rows in docs/roadmap/phase5-7-backlog.md, AGENTS.md and the Constitution. Preserve Phase 4 and existing contracts. State external Data, AI and Frontend decisions as dependencies. No fabricated scientific findings or unapproved schema/API decisions."

**SPECIFY_FEATURE_DIRECTORY**: `specs/phase5-backend`

**Short name**: `mission-scenario-evidence`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect scenario evidence within individual runs (Priority: P1)

A researcher supplies a named or ad hoc mission scenario and inspects which individual runs provide relevant evidence, which requested conditions remain unsupported, and why. This is research screening, never a spacecraft safety verdict.

**Why this priority**: Same-run support prevents false coverage assembled from unrelated study ranges.

**Independent Test**: Evaluate explicitly synthetic scenarios and runs with a declared test-only mapping and rule set, without a ranking or AI provider. Inspect the interpreted scenario, per-run explanations and six coverage dimensions. This proves engineering behavior only.

**Acceptance Scenarios**:

1. **Given** a synthetic run supporting all five requested conditions under declared test-only rules, **When** evaluated, **Then** gravity, material, oxygen, pressure, airflow and combined coverage reference that same run, rule version and synthetic/unreviewed context.
2. **Given** oxygen support in one run and pressure support in another but no run supporting the full combination, **When** evaluated, **Then** combined coverage does not report a match, even if investigation-wide ranges encompass every requested value.
3. **Given** missing, contradictory, unsupported-unit, flagged or unreviewed conditions, **When** evaluated, **Then** affected dimensions explain unknown or unusable evidence; no value becomes zero, nominal atmosphere or positive support. Missing scientific rules make evaluation unavailable rather than establish a scientific gap.
4. **Given** non-finite values, ambiguous units, invalid identity or values outside agreed input limits, **When** submitted, **Then** the request receives a bounded, sanitized rejection before evaluation or persistence. Input bounds are not scientific applicability bounds.
5. **Given** identical scenario, collection and rule versions, **When** results are fully traversed twice, **Then** ordering and explanations are reproducible and page scope is explicit. **When** the final page is requested directly in a multi-page collection, **Then** that response alone cannot establish complete collection traversal or collection-wide absence.

---

### User Story 2 - Inspect trustworthy relevance rankings (Priority: P2)

A researcher requests ranked investigations for a scenario and, where supplied, a prevention, detection or suppression pillar. They can inspect Data-owned relevance rationale, components and applicability without mistaking scores for fire risk.

**Why this priority**: Rankings guide evidence navigation only when their meaning, order and provenance are explicit.

**Independent Test**: Use fixed synthetic ranking deliveries with known identities, ties, versions and score kinds; exercise accepted, malformed, stale and unavailable deliveries independently of real data.

**Acceptance Scenarios**:

1. **Given** a complete versioned synthetic ranking delivery resolving to the declared collection, **When** requested, **Then** supplied ordering and ties, component scores, rationale, applicability, dataset/algorithm versions and origin/review context are preserved.
2. **Given** catalog usefulness and scenario relevance scores, **When** presented, **Then** names, scales and meanings remain distinct; neither becomes a run-match score or fire-risk probability, and investigation rankings are not attached to arbitrary runs.
3. **Given** unknown/duplicate identities, non-finite scores, incomplete components, mismatched scenario/pillar/dataset versions or an unavailable provider, **When** checked, **Then** the delivery cannot appear as accepted ranking; the applicable reason is explicit without fabricated scores, ordering or citations.
4. **Given** a requested material/scenario outside the delivered ranking scope, **When** requested, **Then** the applicability limitation is explicit and no fallback score implies measured coverage.

---

### User Story 3 - Follow pillar evidence to original sources (Priority: P2)

A researcher inspects prevention, detection and suppression evidence and follows every supporting association to the original source and locator.

**Why this priority**: Classifications are useful only with traceable evidence; they are not advisor conclusions.

**Independent Test**: Inspect synthetic classified claims with multiple documents, repeated links to one document, optional run context and an empty pillar, without AI reasoning.

**Acceptance Scenarios**:

1. **Given** explicitly classified synthetic evidence with multiple source associations, **When** inspected, **Then** every association retains its identity, original document identity/URL, available DOI, exact locator, available excerpt, optional run context and origin/review/classification labels.
2. **Given** no accepted classification or evidence for a pillar, **When** requested, **Then** it remains empty/unknown or unavailable with a scoped reason; no prevention finding, detection method or suppression recommendation is invented.
3. **Given** source/run context mismatch or an unreviewed fact, **When** inspected, **Then** the limitation remains explicit and cannot silently count as accepted scientific support; original associations remain recoverable.

---

### User Story 4 - Understand comparison limits (Priority: P3, conditional)

A researcher comparing two or three studies can understand selected observable/context eligibility if the Data and Frontend teams approve optional P5-07 enrichment.

**Why this priority**: This optional work must preserve the delivered Phase 4 original-observation comparison.

**Independent Test**: Inspect synthetic observations with equal unit strings but different methods, geometry or quality; without approved enrichment, confirm existing comparison behavior remains intact.

**Acceptance Scenarios**:

1. **Given** no accepted scientific policy or consumer agreement, **When** existing comparison is used, **Then** original pages and `comparability=not_established` remain unchanged, with no deltas, pooled outcomes or medians.
2. **Given** separately approved explanation policy and consumer contract, **When** eligibility is inspected, **Then** compatible, missing or mismatched reasons cite original observations and the accepted policy. Equal unit strings alone never establish scientific comparability or authorize numeric comparison.

### Edge Cases

- Zero gravity/airflow differs from missing data; accepted zero values retain their units and meaning.
- A lunar/Mars label supplies no missing gravity measurement. E-FIELD supplies no gravity proxy or voltage-to-gravity relationship.
- Inverse-flame oxidizer oxygen is not room-air oxygen; similar names or numbers do not establish compatible meaning.
- Conflicting conditions, mixed review states, flagged values, missing uncertainty and unknown units require explicit limitations under accepted policy.
- Empty accepted collections, partial traversal, missing methodology and provider outages are distinguishable; none proves NASA has never studied the scenario.
- Preset slugs, canonical UUIDs, PSI identifiers and scoped external run keys are distinct; canonical duplicates must be detected.
- Score boundaries, ties, absent components, stale versions and changed dataset identities retain accepted semantics or fail acceptance.
- Repeated documents and cross-study/run links retain separate source associations and context; missing measurement provenance cannot be invented.
- A ranking outage must not erase independently available coverage or source evidence; unavailable sections identify their own dependency.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Provide one Phase 5 mission-scenario evidence feature covering P5-01–P5-06 and conditional P5-07, preserving Phase 4 behavior and contracts. Acceptance: Stories 1–4; SC-006.
- **FR-002**: Scenario input MUST distinguish optional naming/context, environment label, material, gravity in g, oxygen percentage, absolute pressure in psia and airflow in cm/s. Supplied values and units MUST survive interpretation; absent/unmappable fields MUST be explicit without guessed conditions. The engineering contract defines requiredness, nullability, finite-value checks and bounds. Scientific mappings and consumer acceptance remain pending. Acceptance: Story 1.3–1.4; SC-001.
- **FR-003**: Accepted evaluation MUST expose interpreted scenario/units, declared collection/dataset scope, origin and independent review state, rule/engine version, caveats and unavailable fields. Environment/preset names MUST NOT implicitly supply scientific conditions. Acceptance: Story 1.1, 1.3; SC-001.
- **FR-004**: Evaluate gravity, material, oxygen, pressure and airflow within each individual run. Combined support MUST require one run supporting the full combination under accepted rules; investigation-wide extrema and other runs MUST NOT fill missing conditions. Acceptance: Story 1.1–1.2; SC-002.
- **FR-005**: Each of the six dimensions MUST identify supporting run/condition records or a scoped gap, partial, unknown or unavailable reason. Engineering statuses explain fixture-only support, mismatch, partial, unknown or unavailable. Scientific tolerances and support require D-02/D-03. Acceptance: Story 1.1–1.3; SC-002.
- **FR-006**: Missing values, incompatible units, contradictory conditions, quality flags and unapproved review state MUST NOT become accepted coverage. Unavailable methodology MUST be distinguishable from an evaluated mismatch or scoped evidence gap. Acceptance: Story 1.3 and edge cases; SC-002.
- **FR-007**: Retain distinct investigation UUID, PSI ID, available reviewed slug, run UUID and external run key. Resolve identities within the declared dataset. Traversal MUST be bounded, deterministic and explicit about completeness; a page MUST NOT establish collection-wide absence. Acceptance: Story 1.5, Story 2.3; SC-003.
- **FR-008**: Consume Data-owned rankings, validating scope, canonical identities/duplicates, finite components, completeness, versions, origin/review and applicability. Backend MUST NOT recreate or substitute the Data ranking algorithm. Acceptance: Story 2.1, 2.3–2.4; SC-004.
- **FR-009**: Preserve supplied ranking order/ties, component provenance, rationale, applicability and caveats. Invalid, stale or missing deliveries MUST expose rejected/unavailable behavior under agreed policy, without fabricated numerical fallback. Acceptance: Story 2; SC-004.
- **FR-010**: Catalog usefulness, scenario relevance and per-run match scores MUST remain distinct. The fixture declares its own scales. Real score semantics require Data acceptance. No score is a fire-risk probability or proof of measured coverage; missing scores MUST NOT become zero. Acceptance: Story 2.2; SC-004.
- **FR-011**: Group prevention/detection/suppression evidence only by explicit accepted classification and reviewed facts/source mapping. Free text, frontend examples and URLs alone MUST NOT imply scientific classification. Empty/unknown or unavailable pillars MUST state why. Acceptance: Story 3.1–3.2; SC-005.
- **FR-012**: Preserve original values/units/precision, available uncertainty, quality flags, review context, document URLs/DOIs, exact locators, available excerpts and all claim-source associations, including repeated documents and optional run context. Missing provenance MUST be explicit, never invented; raw data MUST remain independently recoverable. Acceptance: Story 3; SC-005.
- **FR-013**: Synthetic scenarios, fixtures and provider results MUST be visibly synthetic/unreviewed on detachable items and enclosing results. Real origin MUST NOT imply review. Engineering, real-data and scientific acceptance MUST remain separate claims. Acceptance: Stories 1.1, 2.1, 3.1; SC-007.
- **FR-014**: Distinguish invalid input, unresolved identity, unsupported mapping, missing review/rules, unavailable provider, version conflict and empty evaluated evidence as applicable. Public errors MUST be bounded/sanitized without secrets, private provider bodies or internal traces. The engineering contract specifies the wire forms. F-01 tracks consumer acceptance. Acceptance: Stories 1.3–1.4, 2.3–2.4, 3.2; SC-007.
- **FR-015**: Identical inputs, accepted rules, ranking delivery and dataset versions MUST yield reproducible explanations/order. Partial results MUST disclose evaluated sections and collection scope. Acceptance: Story 1.5, Story 2.1; SC-003.
- **FR-016**: Optional comparison explanations MUST depend on D-03/F-02. Until accepted, retain Phase 4 original pages and `not_established`; no medians, pooled outcomes, deltas or safety conclusions. Acceptance: Story 4; SC-006.
- **FR-017**: No unconditional safe/unsafe verdict, fabricated finding/citation/uncertainty, model training, generated advisor answer or prediction execution is permitted. AI reasoning, grounding and prediction remain later-phase external work. Acceptance: all stories; SC-007.
- **FR-018**: Use the owner-selected additive `POST /api/v1/mission/scenarios/evaluate`. The public evaluation is stateless. Provide explicit lossless scenario persistence for a compatible complete subset via a trusted writable session, preserving existing schema. Incomplete or unmappable scenarios stay transient. Preserve existing models, applied migrations, chat tables, diagrams and Phase 4 artifacts. Acceptance: scope/dependency review and PostgreSQL storage round trip; SC-006.

### Scope and Backlog Traceability

One feature contains these related capabilities. The owner authorized engineering execution of P5-01–P5-06 and selected the evaluation route from the backlog. Consumer and scientific acceptance are pending.

| Backlog row | Outcome | Requirements / scenarios | Boundary |
| --- | --- | --- | --- |
| P5-01 | Validated scenario and explicit interpretation | FR-002–FR-003, FR-014, FR-018; Story 1 | Engineering mapping and bounds selected; Data and consumer acceptance pending |
| P5-02 | Reproducible same-run evaluation | FR-004, FR-006–FR-007, FR-015; Story 1 | Data mapping/review rules gate scientific evaluation |
| P5-03 | Six-dimension coverage/gaps | FR-004–FR-006; Story 1 | Fixture statuses selected; scientific thresholds and consumer acceptance pending |
| P5-04 | Validated Data ranking handoff | FR-008–FR-009; Story 2 | Adapter boundary only; no Data algorithm development |
| P5-05 | Distinct versioned score meanings | FR-010, FR-015; Story 2 | Data scale/semantics/version approval pending |
| P5-06 | Pillar evidence and provenance | FR-011–FR-013; Story 3 | Data classification/fact/source review; no advisor reasoning |
| P5-07 | Optional comparison eligibility explanations | FR-016; Story 4 | Conditional only; no Phase 4 rewrite or numeric derived comparison |

Out of scope: Phase 3B import/schema remediation; NASA acquisition, ETL and scientific normalization; Data ranking algorithm development; frontend edits; AI retrieval/reasoning, model validation or prediction; chat/authentication; scientific-looking preset inventions; deployment, paid services or shared database operations. Authorized isolated verification and compatible scenario storage are in scope.

### Conceptual Inputs and Outputs

Examples describe user-visible meaning, **not** agreed field names, serialization, routes, tolerances or scientific findings.

| Example | Input | Required observable outcome |
| --- | --- | --- |
| Synthetic complete run | Ad hoc `fixture-material-A`, gravity 0 g, oxygen 21%, absolute pressure 14.7 psia, airflow 5 cm/s; declared synthetic collection/test-only rules | Interpreted scenario and six explanations referencing one supporting synthetic run, synthetic/unreviewed context; no safety claim |
| Synthetic split conditions | Same requested scenario; fixture run A supports oxygen only, run B pressure only | Separate dimension reasons; no combined support from their union |
| Missing prerequisites | Finite scenario without accepted mapping/review policy or ranking delivery | Explicit unavailable sections and prerequisites; no fabricated coverage, score, sources or research-absence claim |
| Ranking delivery | Data-supplied scenario/pillar scope, versions, ordered investigations, score components/rationale | Validated supplied order and distinct score meanings, or explicit rejected/unavailable ranking |
| Pillar evidence | Scenario and accepted classification/fact/source associations | Classified evidence with every source association retained; empty/unknown pillar explicit |

### Key Entities *(include if feature involves data)*

- **Mission scenario**: Requested conditions and units, optional name/environment context; preset identity is distinct from any later approved persisted identity.
- **Evidence collection/version**: Declared investigation/run membership, dataset identity, origin, review and examined scope.
- **Run evaluation**: One scenario against one run, five dimension explanations, combined coverage, rule version and supporting records/limitations.
- **Ranking delivery**: Data-owned scenario/pillar-scoped ordered investigations, distinct scores/components, rationale, versions and applicability; not a run evaluation.
- **Pillar evidence association**: Explicit classification connecting a fact/claim with every source association and optional run context, review and limitations.
- **Comparison explanation**: Conditional policy-backed eligibility reasons with original observations; no derived numerical outcome.

These are conceptual entities, not approved new tables or columns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In the agreed scenario acceptance corpus, 100% of accepted requests expose interpreted values/units without invented conditions; 100% of non-finite, ambiguous-unit and out-of-bound cases are rejected under agreed policy.
- **SC-002**: Each evaluated run and each evaluated page summary independently report exactly six distinct dimension explanations: gravity, material, oxygen, pressure, airflow and combined. When coverage cannot be evaluated, explain why the six dimensions are unavailable without fabricating evaluated run results. Across complete, split-run, partial, missing, contradictory, flagged, inverse-flame and unsupported-unit cases, zero combined-support results rely on multiple runs or unknown/unapproved conditions.
- **SC-003**: Fully traversing each fixed-version acceptance case twice yields identical ordered records/explanations, zero missing or duplicate result identities, and explicit completeness.
- **SC-004**: All accepted ranking cases preserve supplied order/ties, versions, components and distinct score meanings. Every invalid, stale, unavailable or out-of-scope case exposes its limitation and yields zero fabricated scores or accepted mismatched identities.
- **SC-005**: Reviewers can trace 100% of accepted pillar associations to original documents/locators, retaining repeated associations and optional run context; every empty/unknown pillar is explicit.
- **SC-006**: All existing Phase 4 acceptance cases retain contracted behavior. Without optional-enrichment approval, comparison remains `not_established` in 100% of cases. Zero unapproved schema or public-contract changes are introduced.
- **SC-007**: In every acceptance case reviewers can distinguish synthetic/real origin, reviewed/unknown status and unavailable dependencies/evaluated gaps. Zero fabricated scientific claims, unconditional safety verdicts, secret disclosures or mock results labeled verified occur.

These are acceptance targets, not achieved results. Synthetic acceptance proves engineering behavior only; real-data publication, scientific acceptance and Frontend integration need their own evidence.

## Assumptions

- The existing backend and Phase 4 remain the foundation. This feature delivers the scoped backend engineering work.
- Public evaluation uses no new authentication or retention. Missing input stays explicit and scientific values receive no guessed defaults.
- Frontend form ranges (g 0–1, oxygen 15–40%, absolute pressure 7–16 psia, airflow 0–50 cm/s) are consumer constraints only, not approved backend bounds or scientific applicability.
- Synthetic mappings and rules support engineering acceptance. Scientific publication requires external acceptance.
- The November 14, 2026 official dataset must be evaluated on arrival. Prototype data/counts do not establish official compatibility or scientific acceptance.

### Dependencies and material decisions

The [decision record](contracts/review-record.md) maps each pending external owner, input and acceptance requirement to the task ledger. Real-provider publication, scientific methodology, consumer integration and P5-07 remain independently gated. The [HTTP contract](contracts/http.md) defines the owner-authorized engineering surface. The evaluation route is stateless. The trusted scenario persistence service admits only losslessly represented fields.

### Preservation and verification boundary

Use only authorized isolated PostgreSQL fixtures for data-writing verification. Preserve all three revisions and existing read contracts. Engineering evidence includes executed unit, HTTP/OpenAPI and PostgreSQL checks. Scientific and consumer evidence require the corresponding external reviews.
