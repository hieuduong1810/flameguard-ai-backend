# Phase 6 HTTP and provider handoff

Implementation follows the owner-approved [decision record](approval.md).
The generated OpenAPI exposes these operations under `/api/v1`.

| Method and path | Request | Success |
| --- | --- | --- |
| POST `/chat/sessions` | Optional `investigation_id` UUID and title | 201 session with expiry and privacy caveat |
| GET `/chat/sessions/{identity}` | Session UUID | 200 session or 404 unknown/expired |
| GET `/chat/sessions/{identity}/messages` | offset ≥ 0, limit 1–100 | 200 stable history |
| POST `/chat/sessions/{identity}/messages` | `{"question":"Public research question"}` | 201 atomic user/assistant exchange |
| POST `/advisor/assessments` | Phase 5 `EvaluationRequest` | 200 pillar responses, gaps and original collection context |

Assistant answers expose state, text, origin, review_status, provider_version,
model_version, corpus_version and original citations. Unknown metadata stays null.
New messages preserve this envelope in the existing Text body. Historical plain
text messages remain readable with unknown provenance metadata. Citations keep
original document IDs, exact locators and optional original excerpt/run context.

Question length is 1–4000 characters with non-whitespace content. Title length
is at most 200. Invalid input returns 422. Invalid provider/citation payloads
return 502. Changed evidence returns 409. Missing storage/admission returns 503.
Provider timeout produces an explicit timeout outcome. A valid abstention,
unavailable or timeout exchange is committed atomically. Malformed responses
leave no exchange rows. POST sends are non-idempotent and have no automatic retry.

The server defaults to the unavailable provider. `CHAT_PROVIDER=mock` enables
fixed TEST_ONLY synthetic/unreviewed responses. A real engine needs an adapter
implementing RagProvider/AdvisorProvider and accepted AI/Data corpus evaluation.
Current scientific admission accepts unreviewed/unknown collections, so real
scientific answer publication remains unavailable.

## Internal provider follow-up

RagProvider now accepts a detached RagRequest containing the current question,
optional investigation UUID, corpus/dataset versions, collection fingerprint,
allowed original sources and persisted history from the current session only.
History is chronological and bounded to the latest 12 messages, at most 2,000
characters per message and 12,000 total. `history_truncated` discloses omitted
or shortened history. Origin/review labels accompany historical text. History
is untrusted conversational input. Citations must still match the current
allowed source references. Concurrent sends observe committed history at the
start of their provider calls and retain the existing atomic commit semantics.

Trusted startup code may set `app.state.chat_provider_factory` to a zero-argument
factory returning a provider with answer/advise methods. ChatService also accepts
an explicit provider for internal injection. Unavailable/mock configuration stays
supported. Registration alone does not grant scientific publication eligibility.

Advisor keeps the approved HTTP response shape. Its existing `gaps` strings now
include `NO_EVIDENCE`, `PARTIAL_OR_PAGED_EVIDENCE`, `UNREVIEWED_EVIDENCE`,
`EVIDENCE_NOT_EXAMINED`, `PROVIDER_UNAVAILABLE`, `PROVIDER_ABSTAINED` and
`PROVIDER_TIMEOUT` where applicable, together with original Phase 5 reason codes.
Empty current pages with a nonzero pillar total report partial/paged evidence.
Classification unavailability reports its original reason and unexamined scope.
Provider evidence includes the pillar group, pagination, reason codes and Phase 5
scope versions. Scientific fingerprint, dataset/identity versions and collection
context must match Phase 5 evaluation before calls and again before returning.

## Privacy and operations

An opaque UUID gives 24-hour demo continuity and access to anyone holding it.
Use public research content only. Stored rows remain until explicitly authorized
operator cleanup. Disable HTTP access logs that include session paths, for
example `poetry run uvicorn app.main:app --no-access-log`. Configure proxies with
equivalent path/body redaction. Successful responses and HTTP service errors use
`Cache-Control: no-store`. Frontend should keep the identifier out of analytics.

Providers receive bounded detached source context with at most 50 associations.
Advisor consumes the Phase 5 paged pillar evidence. Missing page evidence remains
an explicit gap. Real retrieval quality and pagination-wide scientific coverage
require external evaluation.
