from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["flameguard-ai-backend"] = "flameguard-ai-backend"


class ReadinessResponse(BaseModel):
    status: Literal["ready", "unavailable"]
    service: Literal["flameguard-ai-backend"] = "flameguard-ai-backend"
    database: Literal["ok", "unavailable"]
