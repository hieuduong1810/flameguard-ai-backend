# Synthetic Phase 4 dataset

This collection is TEST_ONLY, not NASA data, scientific evidence, verified findings or operational safety guidance. No frontend mock findings, DOI or real experiment identifiers are copied into it.

`phase4-v1.json` has 28 rows across 9 of the approved 21 tables:

| Table | Rows |
| --- | ---: |
| investigation | 4 |
| test_run | 4 |
| test_condition | 4 |
| measurement | 4 |
| source_document | 3 |
| evidence_claim | 2 |
| claim_source | 4 |
| tag | 1 |
| investigation_tag | 2 |

The other 12 approved tables are empty. One claim is deliberately orphaned and therefore excluded from investigation membership/dashboard claim counts. Another is shared between investigations and has repeated document links, optional run/excerpt, and a deliberately mismatched document/run context. These cases are labeled synthetic and do not validate science.

UUIDs use a fixed namespace; PSI strings begin SYNTHETIC-, tag/public slugs begin synthetic-, statuses are TEST_ONLY/SYNTHETIC_UNREVIEWED, source links use example.invalid and DOI is null. Exact zero/null, unknown uncertainty, simultaneous numeric/text conditions, differing units, tied titles, repeated external run keys across studies and an investigation without children support negative cases.

Expected full-collection dashboard: investigations=4, runs=4, sources=3, linked distinct claims=1, source-linked investigations=2, document coverage=0.5, verifiedRunCount=null. No distribution or verified outcome is invented. `slugs-v1.json` maps public slugs to synthetic PSI identities, separately from UUID.

`collection.example.json` is a template, not local target authorization. Replace its target identity only for an independently approved disposable DB and read-only role. Real machine-specific configuration and authorization belong under ignored .tools/ or another private local directory, never Git.

`tests/fixtures/phase4.py` creates deterministic larger TEST_ONLY variants with 105 investigations, 105 source associations and 25 tags for page traversal. The independently empty collection variant is test-local. These variants are not scientific generators or production import formats.

Use the explicit seed CLI only under [the demo runbook](../../docs/runbooks/phase-4-demo-validation.md). Identical reruns insert zero; unexpected content/keys/privileges cause refusal and preserve existing rows. No startup or HTTP request loads fixtures, and no cleanup/reset mode exists.
