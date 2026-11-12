import asyncio
import json
from collections.abc import Awaitable

from pydantic import ValidationError

MAX_BYTES = 1_048_576
MAX_DEPTH = 12
MAX_ENTRIES = 1_000
PROVIDER_DEADLINE = 5.0


class ProviderFailure(Exception):
    def __init__(self, code: str, *, rejected: bool = False):
        super().__init__(code)
        self.code = code
        self.rejected = rejected


async def execute[T](call: Awaitable[T], *, deadline: float | None = None) -> T:
    try:
        async with asyncio.timeout(PROVIDER_DEADLINE if deadline is None else deadline):
            return await call
    except TimeoutError:
        raise ProviderFailure("PROVIDER_TIMEOUT") from None
    except Exception:
        raise ProviderFailure("PROVIDER_UNAVAILABLE") from None


def reject():
    return ProviderFailure("INVALID_PROVIDER_DELIVERY", rejected=True)


def _unique_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError
    return result


def _reject_constant(_):
    raise ValueError


def _check_depth(value, depth=0):
    if isinstance(value, (list, dict)):
        if depth == MAX_DEPTH:
            raise ValueError
        for child in value.values() if isinstance(value, dict) else value:
            _check_depth(child, depth + 1)


def decode[T](payload: bytes, model: type[T]) -> T:
    if not isinstance(payload, bytes) or len(payload) > MAX_BYTES:
        raise reject()
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
        _check_depth(value)
        return model.model_validate(value)
    except (ValueError, RecursionError, ValidationError):
        raise reject() from None
