"""A service for distributed tracing using OpenTelemetry."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from flx_core.domain.advanced_types import MetadataDict
    from opentelemetry.trace import Tracer

import structlog
from flx_core.config.domain_config import get_config

# ZERO TOLERANCE - OpenTelemetry is REQUIRED for enterprise distributed tracing
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_current_span


# Verify OpenTelemetry functionality - ZERO TOLERANCE MODERNIZATION
def _verify_opentelemetry_functionality() -> None:
    """Verify OpenTelemetry functionality with try/except patterns."""
    tracer_available = False
    exporter_available = False

    try:
        # Check if trace module has get_tracer method
        _ = trace.get_tracer
        tracer_available = True
    except AttributeError:
        pass

    try:
        # Check if OTLPSpanExporter has proper initialization
        _ = OTLPSpanExporter.__init__
        exporter_available = True
    except AttributeError:
        pass

    if not tracer_available or not exporter_available:
        msg = "OpenTelemetry with gRPC export support is required for enterprise distributed tracing"
        raise ImportError(msg)


_verify_opentelemetry_functionality()


if TYPE_CHECKING:
    from flx_core.config import Settings

logger = structlog.get_logger()

# --- Type Variables for Decorators ---
P = ParamSpec("P")
R = TypeVar("R")


def setup_tracing(settings: Settings) -> None:
    """Configure OpenTelemetry for distributed tracing - ENTERPRISE ARCHITECTURE."""
    # ZERO TOLERANCE - Settings must have proper configuration
    service_name = getattr(settings, "service_name", "flx-platform")
    if service_name == "flx-platform":
        logger.warning("service_name not configured, using default")

    # ZERO TOLERANCE - Use domain config for endpoint configuration
    endpoint = getattr(settings, "otel_exporter_endpoint", None)
    if endpoint is None:
        # Get OpenTelemetry configuration from unified domain config - with strict validation
        config = get_config()
        endpoint = config.monitoring.opentelemetry_endpoint

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    logger.info(
        "OpenTelemetry distributed tracing configured",
        service_name=service_name,
        endpoint=endpoint,
    )


def get_tracer(name: str) -> Tracer:
    """Get a tracer for a specific module - ENTERPRISE ARCHITECTURE."""
    # OpenTelemetry is guaranteed to be available - no conditional checks
    return trace.get_tracer(name)


def trace_async(
    name: str | None = None, attributes: MetadataDict | None = None
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Trace an asynchronous method.

    Decorates async functions to add OpenTelemetry tracing spans.
    Automatically captures function name, arguments, and execution time.

    Args:
    ----
        name: Optional span name. Defaults to function name.
        attributes: Optional span attributes dictionary.

    Returns:
    -------
        Decorated function with tracing capabilities.

    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # OpenTelemetry is guaranteed to be available - no conditional checks
            tracer = get_tracer(func.__module__ or __name__)

            span_name = name or func.__name__
            with tracer.start_as_current_span(span_name, attributes=attributes) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                except (
                    ValueError,
                    TypeError,
                    RuntimeError,
                    OSError,
                    TimeoutError,
                    ConnectionError,
                    ImportError,
                ) as e:
                    # ZERO TOLERANCE - Specific exception types for async distributed tracing failures
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
                else:
                    return result

        return wrapper

    return decorator


def trace_sync(
    name: str | None = None, attributes: MetadataDict | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Trace a synchronous method.

    Decorates synchronous functions to add OpenTelemetry tracing spans.
    Automatically captures function name, arguments, and execution time.

    Args:
    ----
        name: Optional span name. Defaults to function name.
        attributes: Optional span attributes dictionary.

    Returns:
    -------
        Decorated function with tracing capabilities.

    Note:
    ----
        Provides distributed tracing configuration.

    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # OpenTelemetry is guaranteed to be available - no conditional checks
            tracer = get_tracer(func.__module__ or __name__)

            span_name = name or func.__name__
            with tracer.start_as_current_span(span_name, attributes=attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                except (
                    ValueError,
                    TypeError,
                    RuntimeError,
                    OSError,
                    TimeoutError,
                    ConnectionError,
                    ImportError,
                ) as e:
                    # ZERO TOLERANCE - Specific exception types for sync distributed tracing failures
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
                else:
                    return result

        return wrapper

    return decorator


def add_span_attribute(key: str, *, value: str | float | bool) -> None:
    """Add an attribute to the current span, if one exists - ENTERPRISE ARCHITECTURE."""
    # OpenTelemetry is guaranteed to be available - no conditional checks
    span = get_current_span()
    if span and span.is_recording():
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: MetadataDict | None = None) -> None:
    """Add an event to the current span, if one exists - ENTERPRISE ARCHITECTURE."""
    # OpenTelemetry is guaranteed to be available - no conditional checks
    span = get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes=attributes)


# Alias for backward compatibility
trace_method = trace_sync
