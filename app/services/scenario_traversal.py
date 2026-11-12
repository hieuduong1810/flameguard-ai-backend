from app.schemas.api.scenarios import (
    DIMS,
    MAX_OFFSET,
    Bindings,
    Dimension,
    EvaluationRequest,
    NextRequest,
    Page,
    RunEvaluation,
)

SECTIONS = ("run_offset", "ranking_offset", "evidence_offset")
DELIVERY_BINDINGS = {
    "ranking_offset": "ranking_fingerprint",
    "evidence_offset": "classification_fingerprint",
}


class ScenarioVersionConflict(Exception):
    pass


def require_replay(request: EvaluationRequest) -> None:
    if request.expected_bindings is None and any(
        getattr(request.pages, field) for field in SECTIONS
    ):
        raise ScenarioVersionConflict


def check_snapshot(request: EvaluationRequest, current: Bindings) -> None:
    expected = request.expected_bindings
    if expected is None:
        return
    independent = set(DELIVERY_BINDINGS.values())
    is_replay = any(getattr(request.pages, field) for field in SECTIONS)
    if is_replay and not request.pages.run_offset:
        independent.update(("mapping_version", "rule_version"))
    if is_replay and not request.pages.evidence_offset:
        independent.add("classification_version")
    if expected.model_dump(exclude=independent) != current.model_dump(exclude=independent):
        raise ScenarioVersionConflict


def check_deliveries(request: EvaluationRequest, current: Bindings) -> None:
    expected = request.expected_bindings
    for offset, binding in DELIVERY_BINDINGS.items():
        expected_hash = getattr(expected, binding, None)
        if (getattr(request.pages, offset) or expected_hash) and (
            expected_hash is None or expected_hash != getattr(current, binding)
        ):
            raise ScenarioVersionConflict


def page_for(request: EvaluationRequest, bindings: Bindings, field: str, total: int) -> Page:
    offset = getattr(request.pages, field)
    limit = request.pages.limit
    next_offset = offset + limit
    next_request = None
    if next_offset < total and next_offset <= MAX_OFFSET:
        next_request = NextRequest(
            pages=request.pages.model_copy(
                update=dict.fromkeys(SECTIONS, 0) | {field: next_offset}
            ),
            expected_bindings=bindings.model_copy(
                update={
                    binding: None
                    for offset, binding in DELIVERY_BINDINGS.items()
                    if offset != field
                }
            ),
        )
    return Page(
        offset=offset,
        limit=limit,
        total=total,
        next_request=next_request,
        continuation_limited=next_offset < total and next_offset > MAX_OFFSET,
    )


def summarize(runs: tuple[RunEvaluation, ...]) -> tuple[Dimension, ...]:
    result = []
    for index, name in enumerate(DIMS):
        decisions = tuple(run.dimensions[index] for run in runs)
        positive = next(
            (
                item
                for status in ("support", "partial")
                for item in decisions
                if item.status == status
            ),
            None,
        )
        if positive is not None:
            result.append(positive)
        elif not decisions:
            result.append(
                Dimension(
                    dimension=name,
                    status="unknown",
                    reason_codes=("NO_RUNS_IN_EXAMINED_PAGE",),
                )
            )
        elif all(item.status == "mismatch" for item in decisions):
            result.append(
                Dimension(
                    dimension=name,
                    status="mismatch",
                    reason_codes=("TEST_ONLY_NO_MATCH_IN_EXAMINED_PAGE",),
                )
            )
        else:
            result.append(
                Dimension(
                    dimension=name,
                    status="unknown",
                    reason_codes=("NO_SUPPORT_ESTABLISHED_IN_EXAMINED_PAGE",),
                )
            )
    return tuple(result)
