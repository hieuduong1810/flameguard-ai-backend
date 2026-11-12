# Phase 5 verification

## Initial workspace

Branch feat/phase5-scenario-matching. Explicit Spec Kit feature directory specs/phase5-backend. Initial Git status showed the existing untracked feature and .specify/workflows/runs/ directories. No tracked changes. Protected files are recorded below.

## Reconciliation and Spec Kit Analyze

The installed read-only Analyze workflow resolved the absolute Phase 5 directory with RequireSpec, RequireTasks and IncludeTasks. No extension hooks are registered. Implementation prerequisites resolved the same directory. The requirements checklist had 16 checked and zero unchecked items.

| ID | Category | Severity | Finding and disposition |
| --- | --- | --- | --- |
| I1 | Inconsistency | Resolved | Generated F-01/D-02–D-05 blanket gates conflicted with owner-authorized mock engineering. The reconciled spec, plan and tasks consistently select the additive POST and leave external evidence on T056–T061. |
| I2 | Ownership | Resolved | Backend owns run orchestration, fixture policy, structural validation and storage. Data owns scientific methods, rankings and classifications. |
| U1 | Underspecification | Resolved | Flat UUID association pages and independent replay descriptors define how claims and sources are traversed. |
| I3 | Inconsistency | Resolved | FR-018/T055 define compatible internal storage and the public stateless read path. Runtime writer/lifecycle and unmappable schema are T062. |

Coverage check found tasks for all 18 FRs and seven SCs. Setup and delivery tasks map to Constitution VII, IX, XI and XII. No unresolved critical issue, duplicate requirement or blocking engineering ambiguity. External prerequisites are explicitly scoped. Next action is the authorized Implement run. Analyze made no edits.

## Protected baseline SHA-256

```
CDFC559BE01963186CFB6A97570476A1194214F81949535B00424C3063CDBB55 README.md
B8542C3BEA0B95F9AF3EFBC1D3F6D1D46F782F0A7B08E4A43E0F0786738807BA alembic/env.py
2D4BD33FD5FFE5E3917CC92D483F2C2E4BEF8C1669B22B3AEC8E8446B4CDACAE alembic/script.py.mako
01BA4719C80B6FE911B091A7C05124B64EEECE964E09C058EF8F9805DACA546B alembic/versions/.gitkeep
46A09596E7AD195F8F45E4B72BBA2A61495864D3745E920E5014E379C0488643 alembic/versions/0001_must_have.py
9FF07199D8A4EEC227BFA30B7028B064B7503B10CCFD3F8AC5182B4DAF899ABD alembic/versions/0002_should_have.py
CD5B2E9908000C8AEF96070F94E991D3B55DFC11AF1360009659F56EA4D5ED63 alembic/versions/0003_could_have.py
8FFB7118ED0C0B3DBC7C889A6A38BFAA6CB6EC8E805362389824E7C8BA9309BC app/models/__init__.py
656F1F95246DC3C3D7B6CF6355E5100967A16175EEDDF914437B0B7C53EFEC13 app/models/base.py
0A83A2333E04E1E4B7E9D9C6DB290AAC6F58B7067E70A52ECB4B00C48AB9414B app/models/catalog.py
F653F64B9F21284C119AE6AA0AE1BF826307B9CFC6B5517AAC79E7C0418AC9FA app/models/chat.py
37D1E4AE43393BB9780578C08104C0E60814D85E196BE2F2CF50DFAA64EB2FE1 app/models/evidence.py
B0B8728C6EE2CD9AD4E34175E3E9EE2CB97B817E1030E3FD7AB8F7A219C7EAF4 app/models/ingestion.py
C21D29E80E0316434F093110F1B755DFE40EFCAED473EE27E80C952B3193979D app/models/prediction.py
ACFCC37BCB7179BDD43E158B4E54438CDCE3BE6BB815A301FDAD85396E03D7E4 app/models/scenarios.py
D3C907A8D7B0E247FED653922F631A0118075E90B1C4F22653BBAAF3E4D6A921 docs/backend-implementation-plan.md
2ED717A53407ACEEF7C73B34A48BFAA027801983953F7816E213DF5EC4AFC997 docs/diagram/01-overall-system-architecture.mmd
9B8DEFC6E618A9D82C8A3FF87662D9A16B000F91D346A731BEDEEB8505C2052E docs/diagram/02-detailed-component-architecture.mmd
B961275C7487668C07B6B044D5BBE06AA774B003D098183974E221D6B163F891 docs/diagram/03-database-must-have-erd.mmd
1B2D35EB7CDA8083CBF9E95090EA5E9B3C9B2412C9DF60FFAC4B313142221DF8 docs/diagram/04-database-should-have-erd.mmd
822931EC321949A03A38AEED377DE38F9BAEDF8925DF83C4727BE44EB14BDCCF docs/diagram/05-database-could-have-erd.mmd
911C64A5C5E0F797D04241CB08252CEFB4BC85498C54E4789E3B72B0D6A011F6 docs/diagram/06-user-navigation.mmd
1882A64CCB138CE13127C9E0AA4BCC436D8CE0890E9CD4EFE37F0C3201C673B5 docs/diagram/07-feature-to-database-map.mmd
00FCBB24E4564485935F7085C9C3FA923261EE8C12D7CAF6108924ECD62AF679 docs/diagram/08-research-dashboard.mmd
3BE3BD8FC954A215CAEB28DB36A90AB49B258982D31AED3C1738843F1EF78F88 docs/diagram/09-explorer-and-comparison.mmd
FF2502A6340A75362742B5C4685AC9D846D5CAE5BCA9FD545CEFAB6C0FBD97B9 docs/diagram/10-mission-scenario-evidence.mmd
C78EF5BE2810163898A8518617915647081B95C8A4E22E9F87B6E16350CB94B5 docs/diagram/11-floating-rag-assistant.mmd
CBA7BBCEF9DE450DE3247ECBB605C64CCAA52D6A2E8EF4FDAB4461F1BE3B408F docs/diagram/12-nasa-psi-ingestion.mmd
D1DFD92936CE92A60C40BEE0456CE14615AEEF7D3AB365F6AADAAD0A09875394 docs/diagram/13-evidence-claim-provenance.mmd
242E596E0E90C76E0C702AD310693A906C32E5BCA34EC420DA9CA207B9035A60 docs/diagram/14-predictive-lab-readiness.mmd
8808C9BDD0887FEADFCD3BE21048C8B599A1C4BA5C91CBF189F12EAD14B3D0C3 docs/diagram/15-implementation-priorities.mmd
9EBA2A11D55ADA5D42016C225520DBD01BC49787BCC235F0E095141D71970EC9 docs/diagram/index.html
11949BF8BC93CCF0B1D522991C9D4B882017927CED684A0C624E49CDC7232406 docs/phase-4-api-verification.md
D6A274712BE64C3D18E8EDBDD0EC09B73228B1E3D5F8D528451C813522595D44 specs/001-phase4-catalog-apis/analysis.md
91154C04AE20B5851A1F83F680DCA71DF086723D3FA14D41F1703CEF5571D76F specs/001-phase4-catalog-apis/changed-files.md
EA58794522E4EE3D77E2D909BECDA9F7286076E53ADA2823BDD2674BA254A19A specs/001-phase4-catalog-apis/checklists/requirements.md
D42F2A694A832D549741297C79F4EC59A405AA575ECF1172FD4B13FA5F89583D specs/001-phase4-catalog-apis/contracts/api.md
83E25FBC5CAD624A20C82AEA7E3DA785D9F8A33B4A59243E380B1A2DE30B642F specs/001-phase4-catalog-apis/contracts/openapi.json
310C319CFDC225C3C55AE80B3A5BB82E2E24C2F484AD982678656410053E8F98 specs/001-phase4-catalog-apis/contracts/review-record.md
F63458B72F8FA482E515AA430F5C4AD1468214798A7A2B9C541642C3DDE313CA specs/001-phase4-catalog-apis/contracts/seed-demo.md
989E6C14753AF323715B0C38E7FA43E3F6DF68C04E6177828C312578D8B36B51 specs/001-phase4-catalog-apis/contracts/team-handoffs.md
0C6BE7BA6E637A5897D35E1841651C20256713FC60AE2574C579AE6ABC329AAF specs/001-phase4-catalog-apis/data-model.md
2D07150EC07B6CF5466866ECE5211DCE330E4A85081A8225E20332377393E5C2 specs/001-phase4-catalog-apis/plan.md
F0969E6FE6FD5690BDF94A7D872624B75261C11B40E7246D95846222CC8AD1A9 specs/001-phase4-catalog-apis/quickstart.md
4E8E644F5D03503719CC84FE945C07A6A0B18A518AFB5A0B49EA2DFA37315B98 specs/001-phase4-catalog-apis/research.md
74EE129A7EC59612CFAD372C722159D0F764419FA566690871B959AB4FFAD8A3 specs/001-phase4-catalog-apis/spec.md
930235F1772666AABC11B53209DBE89EFF7A5A17E1906208F7784445DBBA854C specs/001-phase4-catalog-apis/tasks.md
930B66A044C21EFD1FE2A9FC02329A59A9A5F361C7BF772CDC5163B69A525115 specs/001-phase4-catalog-apis/verification.md
```

## Executed engineering evidence

The test references below are in the following modules.

- [Scenario unit tests](../../tests/unit/test_phase5_scenario.py)
- [Provider unit tests](../../tests/unit/test_phase5_providers.py)
- [HTTP and OpenAPI tests](../../tests/contract/test_phase5_api.py)
- [Isolated PostgreSQL tests](../../tests/integration/test_phase5.py)
- [Phase 4 OpenAPI](../../tests/contract/test_phase4_openapi.py) and [comparison](../../tests/integration/test_comparison_queries.py) regressions

| Criterion | Executed test evidence | Observed result |
| --- | --- | --- |
| FR-001, SC-006, US4.1 | test_runtime_openapi_is_additive_and_matches_snapshot, test_all_runtime_contract_paths_and_output_schemas, test_phase4_comparison_keeps_original_observations_and_context | One additive operation, existing API contract verified. Original observations, run geometry and null derived outputs remain on comparison. |
| FR-002, FR-003, SC-001, US1.4 | test_strict_decimal_originals, test_reject_ambiguous_units_scope_and_extras, test_interpret_retains_omission_null_and_exact_lexical_digits, test_invalid_json_fields_never_reach_snapshot | Strict parsing rejects invalid inputs before snapshot work. Scenario echo preserves units, exact lexical values, omissions and nulls. |
| FR-004, FR-005, SC-002, US1.1, US1.2 | test_six_dimensions_and_same_run_invariant, test_coverage_summary_does_not_union_split_runs_and_retains_originals, test_postgres_full_same_run_and_split_evidence_http | One fixture run supplies all five inputs with five same-run condition references. Two split runs remain partial. Each run and summary has six distinct explanations. |
| FR-006, SC-002, US1.3 | test_unusable_original_conditions_cannot_support_combination, test_conflict_cap_inverse_flame_and_e_field_remain_explicit, test_foreign_duplicate_and_nonfinite_conditions_are_defensive, test_postgres_bounded_queries_and_incomplete_condition_sets | Unknown, flagged, incompatible, capped and conflicting records cannot supply positive combined support. Queries stay at three statements for one and four selected runs. |
| FR-007, FR-015, SC-003, US1.5 | test_replay_is_deterministic_and_final_page_is_scoped, test_snapshot_drift_is_rejected, test_postgres_traverses_every_run_twice_and_does_not_claim_final_page_scope, test_postgres_scope_drift_and_mixed_origin_refused, test_postgres_replay_binds_manifest_precision_as_well_as_stored_values, test_offset_ceiling_discloses_remaining_rows | Four UUID-ordered runs traverse identically twice. Scope, identity, version and exact original precision drift reject replay. Reaching the last page alone establishes only examined scope. |
| FR-008, SC-004, US2.3 | test_invalid_ranking_entry_rejects_complete_delivery, test_stale_ranking_scope_rejected, test_canonical_duplicate_and_incomplete_ranking_rejected, test_complete_must_be_boolean_and_ranking_entry_cap_is_checked | Rejects complete delivery on malformed components, unknown or duplicate identities, scope drift, wrong positions, incomplete or oversized content and invalid declared completeness. |
| FR-009, SC-004, US2.1, US2.4 | test_fixed_ranking_preserves_order_ties_meanings_and_nulls, test_ranking_scope_and_payload_replay_binding, test_section_replay_checks_only_its_provider_and_classification_content, test_postgres_ranking_and_pillar_association_continuations | Preserves positions 1 and 2 tied at rank 1, rejects content drift and reports unsupported material/pillar scope. |
| FR-010, SC-004, US2.2 | test_fixed_ranking_preserves_order_ties_meanings_and_nulls, test_postgres_ranking_and_pillar_association_continuations | Separate fixture scales and original precision. Missing usefulness/component stays null. Explicit zero stays zero. |
| FR-011, SC-005, US3.1, US3.2 | test_explicit_classification_validates_full_original_mapping, test_pillar_traversal_preserves_every_association_and_empty_groups, test_section_replay_checks_only_its_provider_and_classification_content | Explicit mapping covers every admitted association in the classified claim. Empty groups and unavailable classification have distinct reasons. |
| FR-012, SC-005, US3.1, US3.3 | test_pillar_projection_preserves_optional_doi_and_mismatch, test_postgres_ranking_and_pillar_association_continuations, test_phase4_comparison_keeps_original_observations_and_context | Four association IDs across three documents, including repeated document, nullable run, exact locator/excerpt and mismatch. Projection retains supplied DOI when present. Original observation units, precision and missing uncertainty survive through Phase 4. |
| FR-013, SC-007, US1.1, US2.1, US3.3 | test_detached_records_are_immutable_and_mock_origins_are_gated, test_real_origin_retains_unreviewed_and_cannot_activate_mock_sections, test_postgres_default_providers_return_independent_unavailable_sections | Mock fixtures and detachable records label synthetic/unreviewed. Real origin is independent from review. Default providers report absence on an admitted collection. |
| FR-014, SC-007 | test_malformed_duplicate_oversized_and_query_request_boundaries, test_read_boundary_does_not_leak_exception, test_ranking_failure_does_not_erase_other_sections, test_independent_rule_and_classification_failures, test_provider_timeout_cancellation_and_failure_do_not_retry_or_leak | Fixed 422/409/503/500 behavior and section isolation. Malformed, private, timed-out and oversized payloads are safely unavailable or rejected. |
| FR-016, SC-006, US4.1 | test_phase4_comparison_keeps_original_observations_and_context, test_comparison_partial_pages_are_not_collection_absence | Original observations and caveats remain. US4.2 optional policy-backed explanation is deferred as T061. |
| FR-017, SC-007 | test_ranking_failure_does_not_erase_other_sections, test_untrusted_transport_limits, test_postgres_full_same_run_and_split_evidence_http | Fixture-only rule and ranking labels, scoped explanations, null collection conclusion. Provider errors and payloads cannot fabricate outward evidence. |
| FR-018, SC-006 | test_storage_is_explicit_and_round_trips_the_representable_subset, test_storage_rejects_unmappable_inputs, test_postgres_lossless_approved_fields_and_refusal_of_unmappable_storage, test_postgres_transaction_closes_before_provider_wait_and_cancel, test_postgres_cancellation_during_read_releases_pool_and_allows_retry | Read-only repeatable snapshots roll back and release connections on success and cancellation. The trusted storage transaction round-trips existing Numeric/Text columns exactly, with fixture rollback at teardown. |

FR-001–FR-018, SC-001–SC-007 and all 14 story scenarios were assessed. US4.2 is conditional. The acceptance rows above cover engineering behavior and fixture provenance. Official corpus, scientific policy and consumer acceptance are tracked under T056–T062.

## Spec Kit Converge

| Pass | Finding | Disposition |
| --- | --- | --- |
| 1 | Foreign/duplicate run records, classification content drift, independent ranking replay and live comparison proof were partial | Appended and implemented T063–T066. Focused unit/HTTP and PostgreSQL checks passed. |
| 2 | Replay needed manifest-original precision binding; live cancellation and default-unavailable evidence were partial | Appended and implemented T067–T068. The final full and marked integration checks include the new cases. |
| 3 | Reviewed the 18 FRs, seven SCs, 14 story scenarios and the constitution against the implementation | No additional engineering tasks identified. The external/deferred gates remain open. |

## Commands and exact outcomes

| Check | Exit and result |
| --- | --- |
| `poetry check` | 0, All set |
| `poetry run ruff check .` | 0, all checks passed |
| `poetry run ruff format --check .` | 0, 211 files already formatted |
| `poetry run pytest -q` | 0, 551 passed, 0 failed, 0 skipped in 81.53 seconds |
| `poetry run pytest -m integration -q` | 0, 197 passed, 0 failed, 0 skipped, 354 deselected in 76.20 seconds |
| Focused offline after first convergence, `poetry run pytest -q tests/unit/test_phase5_scenario.py tests/unit/test_phase5_providers.py tests/contract/test_phase5_api.py tests/contract/test_phase4_openapi.py tests/contract/test_comparison.py --tb=short` | 0, 112 passed, 0 failed, 0 skipped in 4.06 seconds. Fixture opt-ins cleared for the command. |
| Focused PostgreSQL after first convergence, `poetry run pytest -m integration -q tests/integration/test_phase5.py --tb=short -rs` | 0, 8 passed, 0 failed, 0 skipped in 9.98 seconds. The final full and integration runs include all 11 Phase 5 PostgreSQL cases. |

The initial focused check found a test adapter that attempted to parse an intentionally unavailable ranking payload. The test adapter was corrected and the scope rejection passed on rerun. The initial fixture preflight tried the test-name prefix as a database. The existing fixtures connect to the maintenance database for provisioning, so preflight was corrected to use the actual connection path. No fixture writes occurred during preflight.

Both URLs resolved to the authorized loopback port 5433 and test-named prefixes. The two role checks verified CREATEDB capability and the Phase 4 maintenance role's ability to create roles and assign database ownership. DEBUG=false. No credentials were printed. Generic, Phase 4 and Phase 5 fixture paths ran against fresh generated databases. Provisioned databases and roles were retained. Existing Alembic revisions were exercised only through fixture provisioning. The public evaluation's read-only lifecycle, live cancellation and successful retry were verified.

The runtime OpenAPI snapshot was extracted from the app and verified against its reachable schemas. The HTTP quickstart used app lifespan and independent coverage, ranking and pillar replay. Existing Phase 4 contract tests and the PostgreSQL comparison regression exercised the same application router.

Completed T001–T055 and T063–T068. T056–T060 and T062 are blocked and T061 is deferred. External evidence and acceptance owners are listed in the [handoff](handoff.md).


## Final scope review

Git diff whitespace check exited 0. The final static audit verified 48 protected file hashes, 39 local documentation links, reachable OpenAPI schema references and 68 sequential task IDs with 61 completed and seven open. The tracked diff is limited to Phase 5 wiring, collection replay support, the existing scenario repository, the test fixture index and project status. Existing workflow-run artifacts were retained. Models, applied revisions, diagrams, stable baselines and Phase 4 artifacts matched the starting hashes. The sibling repository was used as a read-only integration reference.
