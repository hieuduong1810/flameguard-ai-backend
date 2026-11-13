from fastapi import HTTPException

from app.services.collection import collection_context


def require_evaluation_scope(evaluation, config):
    if (
        evaluation.scope.collection_fingerprint != config["phase6CollectionFingerprint"]
        or evaluation.scope.dataset_version != config["phase5DatasetVersion"]
        or evaluation.scope.identity_version != config["phase5IdentityVersion"]
        or evaluation.context.model_dump(mode="json", by_alias=True) != collection_context(config)
    ):
        raise HTTPException(409, "Evidence changed during assessment")


def evidence_gaps(section, group, answer):
    reasons = list(section.reason_codes)
    if group is None:
        reasons.append("EVIDENCE_NOT_EXAMINED")
    else:
        reasons.extend(group.reason_codes)
        if section.state == "evaluated" and group.total == 0:
            reasons.append("NO_EVIDENCE")
        if group.total > len(group.items):
            reasons.append("PARTIAL_OR_PAGED_EVIDENCE")
        if group.total and group.context.review_state == "unreviewed":
            reasons.append("UNREVIEWED_EVIDENCE")
    page = section.page
    if page and (page.offset > 0 or page.next_request or page.continuation_limited):
        reasons.append("PARTIAL_OR_PAGED_EVIDENCE")
    provider_reason = {
        "unavailable": "PROVIDER_UNAVAILABLE",
        "abstained": "PROVIDER_ABSTAINED",
        "timeout": "PROVIDER_TIMEOUT",
    }.get(answer.state)
    if provider_reason:
        reasons.append(provider_reason)
    return tuple(dict.fromkeys(reasons))
