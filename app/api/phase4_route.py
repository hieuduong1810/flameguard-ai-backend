import json
import logging

from asyncpg import PostgresError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, TypeAdapter, ValidationError
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from app.services.errors import Phase4Error, unknown_context

logger = logging.getLogger(__name__)


class Phase4Route(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            try:
                keys = list(request.query_params.keys())
                if keys and not self.dependant.query_params:
                    raise Phase4Error("INVALID_REQUEST", 422)
                if any(len(request.query_params.getlist(k)) > 1 for k in keys):
                    raise Phase4Error("INVALID_REQUEST", 422)
                for field in self.dependant.query_params:
                    model = field.field_info.annotation
                    if isinstance(model, type) and issubclass(model, BaseModel):
                        values = dict(request.query_params)
                        if any(
                            k in values and f.alias and f.alias != k
                            for k, f in model.model_fields.items()
                        ):
                            raise Phase4Error("INVALID_REQUEST", 422)
                        model.model_validate(values)
                for field in self.dependant.path_params:
                    TypeAdapter(field.field_info.annotation).validate_python(
                        request.path_params[field.alias]
                    )
                for field in self.dependant.body_params:
                    model = field.field_info.annotation
                    if isinstance(model, type) and issubclass(model, BaseModel):
                        values = await request.json()
                        if isinstance(values, dict) and set(values) - {
                            f.alias or k for k, f in model.model_fields.items()
                        }:
                            raise Phase4Error("INVALID_REQUEST", 422)
                        # JSON strict mode accepts UUID strings but never coerces
                        # booleans, numeric strings or floats into integer fields.
                        model.model_validate_json(await request.body(), strict=True)
                return await original(request)
            except Phase4Error as exc:
                error = exc
            except (
                RequestValidationError,
                ValidationError,
                json.JSONDecodeError,
                UnicodeDecodeError,
            ):
                unsupported = set(request.query_params) & {
                    "fuel",
                    "facility",
                    "gravity",
                    "category",
                }
                if request.query_params.get("sort") not in {None, "title-asc", "runs-desc"}:
                    unsupported.add("sort")
                error = Phase4Error(
                    "UNSUPPORTED_CAPABILITY" if unsupported else "INVALID_REQUEST",
                    422,
                    fields=sorted(unsupported),
                    supported=["title-asc", "runs-desc"] if "sort" in unsupported else [],
                )
            except (DBAPIError, SQLTimeoutError, OSError, TimeoutError, PostgresError):
                error = Phase4Error("DATA_UNAVAILABLE")
            except Exception as exc:
                logger.error("Phase 4 request failed (%s)", type(exc).__name__)
                error = Phase4Error("INTERNAL_ERROR", 500)
            return JSONResponse(
                status_code=error.status,
                content={
                    "error": {
                        "code": error.code,
                        "message": error.code.replace("_", " ").capitalize(),
                        "fields": error.fields,
                        "supportedValues": error.supported,
                    },
                    "context": getattr(request.state, "phase4_context", unknown_context()),
                },
            )

        return handler
