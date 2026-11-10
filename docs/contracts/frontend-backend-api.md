# Frontend ↔ Backend API contract — integration working draft

**Status: PROPOSED, not yet approved or implemented.** This document
translates the stable target endpoints from
`../backend-implementation-plan.md` into handoff questions for the Frontend
team. Finalize per feature via Spec Kit and contract tests. Do not claim an
endpoint exists until it appears in the running OpenAPI and tests pass.

## Current reality (archive, 2026-11-10)

- Backend only exposes `/api/v1/health` and `/api/v1/ready`.
- Next.js currently renders from `src/data/*.ts`; components calculate local
  rankings, gaps, comparisons and AI demos. No frontend API client was found.
- Current frontend study IDs are strings such as `bass`/`sofie-gel`; backend
  investigation `id` is a UUID, `psi_id` is the external NASA identifier.
- Frontend `AiAssistantStore` holds messages in memory, with no persisted
  session token or history API.

## Conventions for proposed public endpoints

- Base path: `/api/v1`; JSON names use `camelCase`. No secrets in URLs or JSON.
- List envelope: `{ "items": [], "total": 0, "offset": 0, "limit": 20 }`;
  proposed `limit` max 100. Always use deterministic ordering with ties.
- Use 200 for success; 404 for unknown canonical IDs, 422 for invalid request
  fields, 503 for unavailable reviewed scientific dependencies. HTTP errors
  should be sanitized, consistent JSON; settle final error codes per spec.
- Null/unknown is **not zero** or an empty scientific assertion. Preserve
  original numeric precision/units and explicitly document public rounding.
- Source links/citations carry original source-document identities, DOI where
  present, source locator, and evidence status. Never flatten a many-to-many
  claim-source relationship into a single unqualified DOI.
- Pagination, filters and data completeness are server-defined; frontend may
  show local demo examples only when visibly identified as demo.

## Planned surface → API matrix

| Client surface | Proposed method and path | Relevant implementation dependencies |
| --- | --- | --- |
| Dashboard | `GET /api/v1/dashboard/summary` | Reviewed counts/aggregates and provenance |
| Explorer | `GET /api/v1/investigations` | Search/filter/sort/pagination, slug mapping |
| Detail | `GET /api/v1/investigations/{uuid}` | Canonical UUID, 404, null-safe DTO |
| Public slug lookup | `GET /api/v1/investigations/by-slug/{slug}` | **Requires approved slug identity policy** |
| Run list | `GET /api/v1/investigations/{uuid}/runs` | Conditions, measurements, units and status |
| Raw telemetry | `GET /api/v1/runs/{uuid}/telemetry` | **Requires asset/time-series contract** |
| Claims + provenance | `GET /api/v1/investigations/{uuid}/claims` | Derived investigation association via original documents/runs |
| Original sources | `GET /api/v1/investigations/{uuid}/sources` | URL, optional DOI, status, version, pagination |
| Comparison | `POST /api/v1/compare` | 2–3 distinct UUIDs, same-unit/context comparison |
| Scenario analysis | `POST /api/v1/scenarios/analyze` | Reviewed run-level matching algorithm, optional persistence |
| Grounded assistant | `POST /api/v1/ask` | **AI team contract**, DB chat persistence and source citations |
| Predictive readiness | TBD | **AI team model and data validation** |

These are **target** endpoints, not a request to implement them all at once.
The Phase 4 vertical slice order is catalog → detail/runs/sources/claims →
dashboard → comparison/telemetry, subject to user approval and Data readiness.

## Data identity: decision required before Phase 4

| Identity | Example | Origin / use |
| --- | --- | --- |
| `id` | UUID | Database investigation primary key; joins and canonical API |
| `psiId` | NASA PSI code, string | External system identity; unique approved DB field |
| `slug` | `bass` | Current Next.js route `/explorer/[id]`; **no column in ERD** |

**Open question:** define a stable, non-colliding, reviewed slug mapping
without inventing a new database column. Options need explicit agreement
(curated manifest keyed by `psiId`, or a schema migration). Do not derive
permanent slugs from changeable titles without an approved collision policy.

## Proposed investigation envelope (illustrative shape only)

```json
{
  "id": "00000000-0000-4000-8000-000000000001",
  "psiId": "EXAMPLE-ONLY",
  "slug": "example-only",
  "title": "Illustrative study",
  "researchPurpose": null,
  "platform": null,
  "dataStatus": "unverified",
  "sources": [],
  "caveats": ["Synthetic response shape; not a NASA record"]
}
```

This is **not** a final DTO or seed. For frontend's rich `Investigation`
type (`hardware`, ranges, findings, confidence, sources, etc.), define a
versioned adapter that tolerates unavailable fields instead of fabricating
values. `Investigation.id = slug` in today's frontend must not be confused
with the returned canonical UUID.

## Scenario input and evidence matching

The TypeScript form uses numeric `gravity` (g) and `airflowVelocity` (cm/s),
while the frozen SCENARIO table uses string `gravity` and `ventilation`.
Agree on serialization with units before persisting. Oxygen is percentage;
pressure is absolute psi (psia), not gauge pressure. Reject non-finite values.

Six dimensions: gravity, material, oxygen, pressure, airflow, combined.
The combined result must come from scientifically compatible conditions
**in one relevant test run**, not an intersection of separate study ranges.
`RELATED`/`PARTIAL`/`GAP` describe evidence coverage, not safe/unsafe status.

## Chat demo contract to agree with the AI and Frontend teams

- No login or guest credentials at this stage; keep `chat_session`,
  `chat_message`, `message_citation` unchanged.
- Browser may save an opaque, backend-created session ID in `sessionStorage`
  and send it with later requests. The current frontend does **not** do this.
- Need explicit decisions for session creation (separate endpoint or first ask),
  message-history pagination, clearing/deleting, expiration, and error handling.
- A session ID is **not authenticated ownership**: anybody who obtains it may
  be able to retrieve its messages without extra controls. Store no private
  user data, avoid URL/log exposure, bound requests, and label demo limitations.
- `MESSAGE_CITATION` persists `chat_message_id`, `source_document_id`,
  `source_locator` only. Any claim detail in public responses must be derived
  from retrieved/validated evidence, not stored in a fictional claim FK.

## Contract acceptance checklist (per feature)

- [ ] Frontend and Backend agree on request/response sample and identity map.
- [ ] Nullability, units, pagination and errors documented.
- [ ] Backend HTTPX tests cover happy path, empty state, invalid input, 404,
      source links and non-fabricated missing-data behavior.
- [ ] API appears in generated OpenAPI.
- [ ] Frontend owner implements/validates adapter against a running backend.
- [ ] Demo mocks and real scientific data have distinct presentation labels.
