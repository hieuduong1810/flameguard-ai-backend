# AI team ↔ Backend RAG and predictive interface

**Status: CONTRACT DRAFT.** No validated RAG provider/model or predictive
artifact is present in the submitted backend. This is a collaboration boundary,
not authorization to implement AI algorithms as mock science.

## Ownership

| Capability | AI team | Backend/Codex |
| --- | --- | --- |
| Retrieval and answer formulation | Owns implementation and evaluation | Adapter, timeout/error mapping and HTTP route |
| Evidence grounding and refusal thresholds | Owns rules and scientific testing | Requires/verifies citation payload before persistence |
| Scientific document chunks/embeddings | Defines indexing strategy with Data team | Stores approved `document_chunk`, `embedding_ref` references |
| Prompt/model/ranking version | Publishes meaningful version and evaluation | Persists/returns agreed provenance fields |
| Predictive algorithms, training and domain | Owns artifacts, validation, uncertainty | Models/version persistence, readiness gates, API |
| Guest chat session ownership | No user auth required | `chat_session`, `chat_message`, `message_citation` persistence |

## Proposed assistant request/response — conceptual, not final

Input:

```json
{
  "question": "What evidence exists for fabric combustion at 0.16g?",
  "sessionId": null,
  "investigationId": null
}
```

Output must include an answer or explicit abstention/evidence gap, a backend
session ID, provenance/model version and an array of original-source citations.
Every citation needs an actual known `source_document_id` plus source locator;
URLs/DOIs come from that stored document. Citation IDs cannot be invented.

Define before implementation:

- Maximum input length, context window, sanitized error model, provider timeout,
  retry/rate-limit policy and data-retention/PII constraints.
- Synchronous vs streaming response contract (the existing frontend typing
  indicator is **not** proof streaming is implemented).
- How the AI signals `unsupported`, `not in curated corpus`, `source pending
  review`, `out of scope`, and provider unavailable separately.
- Evidence/citation validation: no source IDs/locators not present in the
  retrieved approved corpus; distinguish direct quotes, paraphrases and
  interpretation. At least one supporting reference for supported claims.
- How an investigation context uses UUID/slug/`psi_id` without confusion.
- Monitoring/evaluation: groundedness, citation accuracy, abstention quality,
  offline/failed-provider behavior, and regression prompts.

## Session persistence is a backend responsibility

The current ERD contains:

1. `chat_session(id, investigation_id?, title?, created_at)`
2. `chat_message(id, chat_session_id, role, body, created_at)`
3. `message_citation(id, chat_message_id, source_document_id, source_locator)`

No login/guest credentials are authorized now. Browser-held session IDs are
demo continuity only; unauthorized access remains possible if an ID leaks.
The frontend must add actual `sessionStorage`/API integration separately.
History/list/create/delete details must be approved as public API contracts;
do not add `user_id` or `guest_credential` columns on assumption.

## Prediction readiness and safety gate

Before returning numeric prediction results, require:

- Verified, versioned model artifact owned by AI team.
- Training dataset reference and reproducible evaluation metrics.
- Scientific applicability domain for scenario material/gravity/O2/pressure.
- Defensible uncertainty interval and no extrapolation beyond domain without
  explicit caveat/rejection.
- Run-level traceability and a clear statement that outputs are research
  screening, not safety certification.

The current frontend `predictiveLabEngine.ts` contains model names and hard-coded
uncertainty assertions. These are **unverified demonstration inputs** for this
backend contract; they must not be treated as a real validated model or be
persisted as `validation_status = validated` without AI/Data sign-off.

If prerequisites are missing, the backend should report **unavailable/not
validated** with missing requirements and provenance, not fabricate a numerical
prediction or issue a fire-safety verdict.

## Test obligations

- Stub AI adapter tests can verify timeout, structured error, abstention and
  citation validation, but do **not** prove model correctness.
- Real AI integration tests must include expert-reviewed prompts/sources,
  original document/locator checks and missing-evidence adversarial cases.
- Prediction tests verify readiness locks, domain and unit mismatches; a
  synthetic scenario test is not empirical validation.
