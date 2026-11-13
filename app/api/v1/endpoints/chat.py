from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from app.api.dependencies import get_scenarios
from app.integrations.chat import bounded
from app.schemas.api.chat import (
    AdvisorOutput,
    Exchange,
    MessagePage,
    Question,
    SessionInput,
    SessionOutput,
)
from app.schemas.api.scenarios import PILLARS, EvaluationRequest
from app.services.advisor import evidence_gaps, require_evaluation_scope
from app.services.chat import ChatService, validate_citations
from app.services.scenarios import ScenarioService


class ChatRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            try:
                response = await original(request)
                response.headers["Cache-Control"] = "no-store"
                return response
            except HTTPException as exc:
                exc.headers = {**(exc.headers or {}), "Cache-Control": "no-store"}
                raise
            except RequestValidationError:
                raise
            except Exception:
                raise HTTPException(
                    503, "Chat service unavailable", headers={"Cache-Control": "no-store"}
                ) from None

        return handler


router = APIRouter(
    tags=["chat", "advisor"],
    route_class=ChatRoute,
    responses={
        404: {"description": "Session or investigation unavailable"},
        409: {"description": "Scientific evidence changed"},
        502: {"description": "Invalid provider response or citation"},
        503: {"description": "Runtime storage or scientific collection unavailable"},
    },
)


def service(request: Request):
    return ChatService(request.app)


@router.post("/chat/sessions", response_model=SessionOutput, status_code=201)
async def create_session(value: SessionInput, chat: Annotated[ChatService, Depends(service)]):
    return await chat.create(value)


@router.get("/chat/sessions/{identity}", response_model=SessionOutput)
async def get_session(identity: UUID, chat: Annotated[ChatService, Depends(service)]):
    return await chat.get(identity)


@router.get("/chat/sessions/{identity}/messages", response_model=MessagePage)
async def history(
    identity: UUID,
    chat: Annotated[ChatService, Depends(service)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    return await chat.history(identity, offset, limit)


@router.post("/chat/sessions/{identity}/messages", response_model=Exchange, status_code=201)
async def send(identity: UUID, value: Question, chat: Annotated[ChatService, Depends(service)]):
    return await chat.send(identity, value.question)


@router.post("/advisor/assessments", response_model=AdvisorOutput)
async def advise(
    value: EvaluationRequest,
    chat: Annotated[ChatService, Depends(service)],
    scenarios: Annotated[ScenarioService, Depends(get_scenarios)],
):
    evaluation = await scenarios.evaluate(value)
    config, sources, _ = await chat.context()
    require_evaluation_scope(evaluation, config)
    groups = {g.pillar: g for g in evaluation.pillar_evidence.groups or ()}
    answers = {}
    gaps = {}
    for pillar in PILLARS:
        group = groups.get(pillar)
        evidence = {
            "group": group.model_dump(mode="json") if group else None,
            "pagination": evaluation.pillar_evidence.page.model_dump(mode="json")
            if evaluation.pillar_evidence.page
            else None,
            "reason_codes": evaluation.pillar_evidence.reason_codes,
            "scope": evaluation.scope.model_dump(mode="json"),
        }
        answer = await bounded(
            chat.provider.advise(evaluation.scenario.model_dump(mode="json"), evidence),
            chat.settings.chat_timeout_seconds,
        )
        allowed = tuple(
            c
            for c in sources
            if group
            and any(
                c.source_document_id == i.document.source_document_id
                and c.source_locator == i.source_locator
                and c.source_excerpt == i.source_excerpt
                and c.test_run_id == i.test_run_id
                for i in group.items
            )
        )
        validate_citations(answer, allowed, config["origin"] == "synthetic")
        answers[pillar] = answer
        gaps[pillar] = evidence_gaps(evaluation.pillar_evidence, group, answer)
    current, _, _ = await chat.context()
    require_evaluation_scope(evaluation, current)
    return AdvisorOutput(
        pillars=answers, gaps=gaps, context=evaluation.context.model_dump(mode="json")
    )
