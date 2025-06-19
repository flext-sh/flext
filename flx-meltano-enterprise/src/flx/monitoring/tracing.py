"""
OpenTelemetry tracing setup for FLX platform.

Provides distributed tracing capabilities for monitoring request flows
across the platform components.
"""

from functools import wraps
from typing import Any, Callable, Optional

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aioredis import AioRedisInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.grpc import GrpcAioInstrumentorServer
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies



# Lazy import to avoid circular dependencies
Settings = lazy_import("flx.config", "Settings")

logger = structlog.get_logger()


def setup_tracing(config: Settings) -> Optional[trace.Tracer]:
    """
    Configure OpenTelemetry tracing.

    Args:
        config: Application settings

    Returns:
        Tracer instance if tracing is enabled, None otherwise
    """
    if not config.tracing_enabled:
        logger.info("Tracing disabled")
        return None

    logger.info("Setting up tracing", endpoint=config.tracing_endpoint)

    try:
        # Create resource
        resource = Resource.create(
            {
                "service.name": config.tracing_service_name,
                "service.version": "2.0.0",
                "deployment.environment": config.environment,
            }
        )

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Configure exporter
        if config.tracing_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=config.tracing_endpoint,
                insecure=True,  # Use insecure for local development
            )

            # Add batch processor
            span_processor = BatchSpanProcessor(
                otlp_exporter,
                max_queue_size=2048,
                max_export_batch_size=512,
                max_export_interval_millis=5000,
            )
            provider.add_span_processor(span_processor)

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        # Instrument libraries
        GrpcAioInstrumentorServer().instrument()
        AsyncPGInstrumentor().instrument()
        AioRedisInstrumentor().instrument()
        RequestsInstrumentor().instrument()

        logger.info("Tracing setup complete")

        # Return tracer
        return trace.get_tracer(__name__)

    except Exception as e:
        logger.error("Failed to setup tracing", error=str(e))
        return None


def trace_method(
    name: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to trace async methods.

    Args:
        name: Custom span name (defaults to function name)
        attributes: Additional span attributes

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Get tracer
            tracer = trace.get_tracer(__name__)

            # Determine span name
            span_name = name or f"{func.__module__}.{func.__name__}"

            # Start span
            with tracer.start_as_current_span(span_name) as span:
                # Add attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add args/kwargs as attributes (be careful with sensitive data)
                if args and hasattr(args[0], "__class__"):
                    span.set_attribute("class.name", args[0].__class__.__name__)

                try:
                    # Execute function
                    result = await func(*args, **kwargs)

                    # Mark span as successful
                    span.set_status(trace.Status(trace.StatusCode.OK))

                    return result

                except Exception as e:
                    # Record exception
                    span.record_exception(e)
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            str(e),
                        )
                    )
                    raise

        return wrapper

    return decorator


def trace_sync_method(
    name: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to trace synchronous methods.

    Args:
        name: Custom span name (defaults to function name)
        attributes: Additional span attributes

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get tracer
            tracer = trace.get_tracer(__name__)

            # Determine span name
            span_name = name or f"{func.__module__}.{func.__name__}"

            # Start span
            with tracer.start_as_current_span(span_name) as span:
                # Add attributes
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    # Execute function
                    result = func(*args, **kwargs)

                    # Mark span as successful
                    span.set_status(trace.Status(trace.StatusCode.OK))

                    return result

                except Exception as e:
                    # Record exception
                    span.record_exception(e)
                    span.set_status(
                        trace.Status(
                            trace.StatusCode.ERROR,
                            str(e),
                        )
                    )
                    raise

        return wrapper

    return decorator


def get_current_span() -> Optional[trace.Span]:
    """Get the current active span."""
    return trace.get_current_span()


def add_span_attribute(key: str, value: Any) -> None:
    """Add attribute to current span if one exists."""
    span = get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict[str, Any]] = None) -> None:
    """Add event to current span if one exists."""
    span = get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})


def record_exception(exception: Exception) -> None:
    """Record exception in current span if one exists."""
    span = get_current_span()
    if span:
        span.record_exception(exception)
