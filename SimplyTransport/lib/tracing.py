"""OpenTelemetry helpers: CLI span naming and method decorators."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from typing import Any, ParamSpec, TypeVar, overload

from opentelemetry import trace

from . import settings

P = ParamSpec("P")
R = TypeVar("R")


def get_app_tracer() -> trace.Tracer:
    return trace.get_tracer(settings.app.NAME, settings.app.VERSION)


def cli_span_name(func: Callable[..., object]) -> str:
    return f"cli.{func.__name__}"


@contextmanager
def cli_command_span(name: str) -> Generator[None, None, None]:
    with get_app_tracer().start_as_current_span(name):
        yield


class CreateSpan:
    """
    Span over a sync or async callable. Default name is ``fn.__qualname__`` (e.g. ``MapService.foo``).
    Pass an explicit name for ``@staticmethod`` or awkward nested callables.
    """

    def __init__(self, name: str | None = None) -> None:
        self._name = name

    @overload
    def __call__(self, fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]: ...

    @overload
    def __call__(self, fn: Callable[P, R]) -> Callable[P, R]: ...

    def __call__(self, fn: Callable[P, Any]) -> Callable[P, Any]:
        span_name_override = self._name
        tracer = get_app_tracer()

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                span_name = span_name_override or fn.__qualname__
                with tracer.start_as_current_span(span_name):
                    return await fn(*args, **kwargs)

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            span_name = span_name_override or fn.__qualname__
            with tracer.start_as_current_span(span_name):
                return fn(*args, **kwargs)

        return sync_wrapper
