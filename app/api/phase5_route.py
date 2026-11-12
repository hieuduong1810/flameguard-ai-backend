import json
import logging

from asyncpg import PostgresError
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import TimeoutError as SQLTimeoutError
from starlette.requests import ClientDisconnect

from app.schemas.api.scenarios import EvaluationError, EvaluationErrorDetail, EvaluationRequest
from app.services.errors import Phase4Error, unknown_context
from app.services.scenario_traversal import ScenarioVersionConflict

MAX_REQUEST_BYTES = 32_768
logger = logging.getLogger(__name__)

ERRORS = {
    "INVALID_REQUEST": (422, "Invalid scenario evaluation request"),
    "VERSION_CONFLICT": (409, "Scenario evaluation bindings changed or are missing"),
    "DATA_UNAVAILABLE": (503, "Scenario evidence data is unavailable"),
    "COLLECTION_SCOPE_INVALID": (503, "Scenario evidence collection is unavailable"),
    "INTERNAL_ERROR": (500, "Internal server error"),
}


def _unique_keys(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError
    return result


def _invalid_constant(_):
    raise ValueError


class InvalidEvaluationRequest(Exception):
    pass


def _limited_request(request: Request) -> Request:
    received = 0

    async def receive():
        nonlocal received
        message = await request.receive()
        received += len(message.get("body", b""))
        if received > MAX_REQUEST_BYTES:
            raise InvalidEvaluationRequest
        return message

    return Request(request.scope, receive=receive)


async def _validated_request(request: Request) -> Request:
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if request.query_params or media_type != "application/json":
        raise InvalidEvaluationRequest
    bounded = _limited_request(request)
    try:
        data = json.loads(
            (await bounded.body()).decode("utf-8"),
            object_pairs_hook=_unique_keys,
            parse_constant=_invalid_constant,
        )
        EvaluationRequest.model_validate(data)
    except (ValidationError, ValueError, RecursionError, ClientDisconnect):
        raise InvalidEvaluationRequest from None
    return bounded


class Phase5Route(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            try:
                return await original(await _validated_request(request))
            except (RequestValidationError, InvalidEvaluationRequest):
                code = "INVALID_REQUEST"
            except ScenarioVersionConflict:
                code = "VERSION_CONFLICT"
            except Phase4Error as exc:
                code = (
                    "DATA_UNAVAILABLE"
                    if exc.code == "DATA_UNAVAILABLE"
                    else "COLLECTION_SCOPE_INVALID"
                )
            except (DBAPIError, SQLTimeoutError, OSError, TimeoutError, PostgresError):
                code = "DATA_UNAVAILABLE"
            except Exception:
                logger.error("Phase 5 evaluation failed")
                code = "INTERNAL_ERROR"
            status, message = ERRORS[code]
            error = EvaluationError(
                error=EvaluationErrorDetail(code=code, message=message),
                context=unknown_context(),
            )
            return JSONResponse(
                status_code=status, content=error.model_dump(mode="json", by_alias=True)
            )

        return handler
