import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError

from app.integrations.prediction import PredictionFailure, select_provider
from app.schemas.api.predictions import (
    PredictionError,
    PredictionRequest,
    PredictionResponse,
    Readiness,
)
from app.services.errors import Phase4Error
from app.services.predictions import PredictionService


def unique_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


class PredictionRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            try:
                allowed = {"model_id"} if request.method == "GET" else set()
                if set(request.query_params) - allowed or any(
                    len(request.query_params.getlist(key)) != 1 for key in request.query_params
                ):
                    raise PredictionFailure("INVALID_REQUEST", 422)
                if request.method == "POST":
                    if request.headers.get("content-type", "").split(";")[0] != "application/json":
                        raise PredictionFailure("INVALID_REQUEST", 422)
                    body = bytearray()
                    async for chunk in request.stream():
                        body.extend(chunk)
                        if len(body) > 32768:
                            raise PredictionFailure("INVALID_REQUEST", 422)
                    request._body = bytes(body)
                    json.loads(request._body.decode("utf-8"), object_pairs_hook=unique_object)
                response = await original(request)
                response.headers["Cache-Control"] = "no-store"
                return response
            except PredictionFailure as exc:
                code, status = exc.code, exc.status
            except (RequestValidationError, ValidationError, ValueError, UnicodeDecodeError):
                code, status = "INVALID_REQUEST", 422
            except Phase4Error as exc:
                code, status = exc.code, exc.status
            except Exception:
                code, status = "DATA_UNAVAILABLE", 503
            return JSONResponse(
                status_code=status,
                content={"error": {"code": code}},
                headers={"Cache-Control": "no-store"},
            )

        return handler


router = APIRouter(tags=["prediction"], route_class=PredictionRoute)


def service(request: Request):
    return PredictionService(
        request.app.state.database.session_factory,
        request.app.state.settings,
        select_provider(request.app),
    )


@router.get(
    "/prediction/readiness",
    response_model=Readiness,
    operation_id="predictionReadiness",
    responses={
        422: {"model": PredictionError, "description": "Invalid request"},
        503: {"model": PredictionError, "description": "Collection unavailable"},
    },
)
async def readiness(
    service: Annotated[PredictionService, Depends(service)],
    model_id: Annotated[UUID | None, Query()] = None,
):
    return await service.readiness(model_id)


@router.post(
    "/predictions",
    response_model=PredictionResponse,
    operation_id="executePrediction",
    responses={
        code: {"model": PredictionError, "description": label}
        for code, label in (
            (409, "Version conflict"),
            (422, "Invalid request"),
            (502, "Invalid provider response"),
            (503, "Provider or collection unavailable"),
            (504, "Provider timeout"),
        )
    },
)
async def predict(body: PredictionRequest, service: Annotated[PredictionService, Depends(service)]):
    return await service.predict(body)
