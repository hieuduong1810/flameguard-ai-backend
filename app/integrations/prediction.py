"""Detached prediction adapter boundary. Mock values are transport fixtures only."""

import asyncio
from typing import Protocol
from uuid import UUID

from pydantic import ValidationError

from app.schemas.api.predictions import (
    Declaration,
    ModelMetadata,
    PredictionRequest,
    ProviderResult,
)


class PredictionCall(Declaration):
    request: PredictionRequest
    metadata: ModelMetadata
    collection_fingerprint: str


class ProviderRegistration(Declaration):
    provider_version: str
    model_id: UUID
    model_version: str
    dataset_version: str
    artifact_ref: str
    artifact_available: bool


class PredictionProvider(Protocol):
    origin: str
    registration: ProviderRegistration | None

    async def predict(self, call: PredictionCall) -> ProviderResult: ...


class PredictionFailure(Exception):
    def __init__(self, code, status):
        self.code, self.status = code, status


class UnavailablePredictionProvider:
    origin = "unknown"
    registration = None

    async def predict(self, call):
        raise PredictionFailure("PROVIDER_UNAVAILABLE", 503)


class MockPredictionProvider:
    origin = "synthetic"
    registration = None

    async def predict(self, call):
        request = call.request
        if not request.observable.startswith(
            "TEST_ONLY"
        ) or not call.metadata.artifact_ref.startswith("TEST_ONLY"):
            raise PredictionFailure("MOCK_FIXTURE_REQUIRED", 502)
        return ProviderResult(
            model_id=request.model_id,
            model_version=request.expected_model_version,
            dataset_version=request.expected_dataset_version,
            observable=request.observable,
            value="0",
            unit=call.metadata.observables[request.observable],
            origin="synthetic",
            provider_version="TEST_ONLY-provider-v1",
            collection_fingerprint=call.collection_fingerprint,
            uncertainty={"lower": "0", "upper": "0", "method_ref": call.metadata.uncertainty_ref},
            limitations=call.metadata.limitations
            + ("TEST_ONLY fixed transport fixture; no scientific interpretation",),
        )


def select_provider(app):
    factory = getattr(app.state, "prediction_provider_factory", None)
    if factory is None:
        factory = {"unavailable": UnavailablePredictionProvider, "mock": MockPredictionProvider}[
            app.state.settings.prediction_provider
        ]
    return factory()


async def execute_provider(provider, call: PredictionCall, seconds: float):
    try:
        origin = provider.origin
        registration = getattr(provider, "registration", None)
        async with asyncio.timeout(seconds):
            result = ProviderResult.model_validate(
                await provider.predict(call.model_copy(deep=True))
            )
        request, metadata = call.request, call.metadata
        if (
            result.model_id != request.model_id
            or result.model_version != request.expected_model_version
            or result.dataset_version != request.expected_dataset_version
            or result.observable != request.observable
            or result.unit != metadata.observables[request.observable]
            or result.origin != origin
            or provider.origin != origin
            or getattr(provider, "registration", None) != registration
            or result.collection_fingerprint != call.collection_fingerprint
            or result.uncertainty.method_ref != metadata.uncertainty_ref
            or not set(metadata.limitations).issubset(result.limitations)
        ):
            raise PredictionFailure("INVALID_PROVIDER_RESPONSE", 502)
        if origin == "real" and (
            not isinstance(registration, ProviderRegistration)
            or result.provider_version != registration.provider_version
        ):
            raise PredictionFailure("INVALID_PROVIDER_RESPONSE", 502)
        return result
    except TimeoutError:
        raise PredictionFailure("PROVIDER_TIMEOUT", 504) from None
    except (ValidationError, ValueError, KeyError):
        raise PredictionFailure("INVALID_PROVIDER_RESPONSE", 502) from None
    except PredictionFailure:
        raise
    except Exception:
        raise PredictionFailure("PROVIDER_UNAVAILABLE", 503) from None
