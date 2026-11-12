# Phase 4 Backend ↔ Data handoff

Status: synthetic backend/API verification only. Curated data delivery, scientific status/unit vocabulary and Data acceptance are PENDING. This document does not implement ETL or authorize import into shared data.

The 21-table ERD, all model fields/FKs and migrations 0001–0003 are preserved. See [physical mapping](../phase-2-database-implementation.md) and [existing handoff draft](data-handoff.md). Internal UUID, external psi_id, public slug, run external key, document ID/DOI and claim-source association ID remain separate.

Data must supply original source/identity manifests, exact values/units/uncertainty, null/unknown meaning, raw status vocabulary, duplicate/version policy, original locators/excerpts/run contexts, asset references and QA/review evidence. A URL, DOI or review-looking text alone does not verify a run or measurement. Measurement has no approved source FK; do not invent one.

Backend acceptance will check source ownership, all many-to-many claim links, repeated associations, optional run context and mismatches; preserve originals rather than silently discard inconsistent associations. Claims have investigation membership through documents, not text inference or an invented direct FK. Real source titles/authors/year/confidence cannot be filled from frontend examples.

Current executable admission is intentionally limited to exact synthetic manifest collections and read-only database roles. Missing/unknown/real-curated manifests fail closed until a separately reviewed Data integration provides authoritative identity/origin/review semantics. This pending real-data adapter/publication gate is explicit; no NASA collection is falsely labeled synthetic or curated. Existing development data is not changed by this feature.

verifiedRunCount stays unknown/null; original observations can be inspected with context. Enabling a verified count or any derived comparison requires a reproducible scientific review rule compatible with the schema, approved unit/method/condition/uncertainty/provenance handling and reviewed consumer examples. Full time series additionally require an asset/channel/time/access contract. No matching, RAG or predictive algorithm is implemented.

Synthetic fixture/schema/API passes are technical acceptance evidence only, not acceptance of scientific findings. Data owns acquisition, cleaning, scientific normalization/curation and production import execution. Backend owns HTTP/persistence compatibility checks and safe adapters. Escalate any needed schema change before coding it; scientific/consumer sign-offs are not inferred from this handoff.
