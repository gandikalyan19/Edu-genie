"""Tracks which model produced a response so the API can persist model_used.

The feature modules fall back to deterministic local output whenever a provider
is unavailable, so the caller cannot infer the model from configuration alone.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar


FALLBACK_MODEL = "local-fallback"


class ModelUsage:
    def __init__(self, default: str) -> None:
        self.default = default
        self.recorded: str | None = None

    @property
    def model_used(self) -> str:
        return self.recorded or self.default


_current_usage: ContextVar[ModelUsage | None] = ContextVar("edugenie_model_usage", default=None)


def record_model(model_name: str) -> None:
    usage = _current_usage.get()
    if usage is not None:
        usage.recorded = model_name


@contextmanager
def capture_model(default: str = FALLBACK_MODEL) -> Iterator[ModelUsage]:
    usage = ModelUsage(default)
    token = _current_usage.set(usage)
    try:
        yield usage
    finally:
        _current_usage.reset(token)
