"""Enhanced structured logging and observability system.

This module provides comprehensive logging capabilities with structured data,
correlation IDs, performance metrics, and integration with monitoring systems.
"""

from __future__ import annotations

import sys
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from enum import StrEnum
from functools import wraps
from typing import Any

import structlog
from flx_core.config.domain_config import get_config
from pydantic import BaseModel, Field


class LogLevel(StrEnum):
    """Log level enumeration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogContext(BaseModel):
    """Structured log context for correlation and tracing."""

    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str | None = None
    span_id: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    operation: str | None = None
    component: str | None = None
    environment: str | None = None
    version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class PerformanceMetrics(BaseModel):
    """Performance metrics for operations."""

    operation_name: str
    start_time: float
    end_time: float | None = None
    duration_ms: float | None = None
    memory_usage_mb: float | None = None
    cpu_usage_percent: float | None = None

    def finish(self) -> None:
        """Mark operation as finished and calculate duration."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000


class StructuredLogger:
    """Enhanced structured logger with context and performance tracking."""

    def __init__(self, name: str, context: LogContext | None = None) -> None:
        """Initialize structured logger."""
        self.name = name
        self.context = context or LogContext()
        self._logger = structlog.get_logger(name)
        self._performance_metrics: dict[str, PerformanceMetrics] = {}

    def with_context(self, **kwargs: Any) -> StructuredLogger:
        """Create new logger with additional context."""
        new_context = self.context.model_copy()
        for key, value in kwargs.items():
            try:
                getattr(new_context, key)
                setattr(new_context, key, value)
            except AttributeError:
                pass

        return StructuredLogger(self.name, new_context)

    def _log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Internal logging method with structured data."""
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level.value,
            "logger": self.name,
            "message": message,
            **self.context.to_dict(),
            **kwargs,
        }

        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}

        getattr(self._logger, level.value)(message, **log_data)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)

    def exception(self, message: str, exc_info: Any = True, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._log(LogLevel.ERROR, message, exc_info=exc_info, **kwargs)

    @contextmanager
    def performance_context(self, operation_name: str):
        """Context manager for performance tracking."""
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
        )

        operation_id = str(uuid.uuid4())
        self._performance_metrics[operation_id] = metrics

        self.info(
            f"Starting operation: {operation_name}",
            operation_id=operation_id,
            operation_name=operation_name,
        )

        try:
            yield metrics
        except Exception as e:
            self.error(
                f"Operation failed: {operation_name}",
                operation_id=operation_id,
                operation_name=operation_name,
                error=str(e),
                exc_info=True,
            )
            raise
        finally:
            metrics.finish()

            self.info(
                f"Operation completed: {operation_name}",
                operation_id=operation_id,
                operation_name=operation_name,
                duration_ms=metrics.duration_ms,
                memory_usage_mb=metrics.memory_usage_mb,
                cpu_usage_percent=metrics.cpu_usage_percent,
            )

            # Clean up
            self._performance_metrics.pop(operation_id, None)


def performance_logged(operation_name: str | None = None):
    """Decorator for automatic performance logging."""

    def decorator(func: object):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)

            with logger.performance_context(op_name):
                try:
                    result = await func(*args, **kwargs)
                    logger.debug(
                        f"Function {op_name} completed successfully",
                        function=func.__name__,
                        args_count=len(args),
                        kwargs_count=len(kwargs),
                    )
                    return result
                except Exception as e:
                    logger.exception(
                        f"Function {op_name} failed",
                        function=func.__name__,
                        error=str(e),
                        args_count=len(args),
                        kwargs_count=len(kwargs),
                    )
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)

            with logger.performance_context(op_name):
                try:
                    result = func(*args, **kwargs)
                    logger.debug(
                        f"Function {op_name} completed successfully",
                        function=func.__name__,
                        args_count=len(args),
                        kwargs_count=len(kwargs),
                    )
                    return result
                except Exception as e:
                    logger.exception(
                        f"Function {op_name} failed",
                        function=func.__name__,
                        error=str(e),
                        args_count=len(args),
                        kwargs_count=len(kwargs),
                    )
                    raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def setup_logging() -> None:
    """Setup structured logging configuration."""
    config = get_config()

    # Get log level from config
    log_level = getattr(config, "log_level", "INFO").upper()

    # Map string levels to numeric values for structlog
    level_mapping = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    numeric_level = level_mapping.get(log_level, 20)  # Default to INFO

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.WriteLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


# Global logger cache
_logger_cache: dict[str, StructuredLogger] = {}


def get_logger(name: str, context: LogContext | None = None) -> StructuredLogger:
    """Get or create a structured logger instance."""
    cache_key = f"{name}:{id(context) if context else 'default'}"

    if cache_key not in _logger_cache:
        _logger_cache[cache_key] = StructuredLogger(name, context)

    return _logger_cache[cache_key]


def create_correlation_context(
    user_id: str | None = None,
    operation: str | None = None,
    component: str | None = None,
    **kwargs: Any,
) -> LogContext:
    """Create a new correlation context for distributed tracing."""
    config = get_config()

    return LogContext(
        user_id=user_id,
        operation=operation,
        component=component,
        environment=getattr(config, "environment", "development"),
        version=getattr(config, "version", "1.0.0"),
        **kwargs,
    )


class LoggingMiddleware:
    """Middleware for automatic request/response logging."""

    def __init__(self, component_name: str) -> None:
        """Initialize logging middleware."""
        self.component_name = component_name
        self.logger = get_logger(f"middleware.{component_name}")

    async def __call__(self, request: Any, call_next: Any) -> Any:
        """Process request with logging."""
        # Create correlation context
        context = create_correlation_context(
            operation=f"{request.method} {request.url.path}",
            component=self.component_name,
            request_id=str(uuid.uuid4()),
        )

        logger = self.logger.with_context(**context.to_dict())

        # Log request
        # Extract headers with pythonic approach
        try:
            headers_dict = dict(request.headers)
        except AttributeError:
            headers_dict = None  # Request doesn't have headers attribute

        logger.info(
            "Request received",
            method=request.method,
            path=str(request.url.path),
            query_params=str(request.url.query) if request.url.query else None,
            headers=headers_dict,
        )

        # Process request with performance tracking
        with logger.performance_context(f"request_{request.method}_{request.url.path}"):
            try:
                response = await call_next(request)

                logger.info(
                    "Request completed",
                    status_code=getattr(response, "status_code", "unknown"),
                    response_size=len(getattr(response, "body", b"")),
                )

                return response

            except Exception as e:
                logger.exception(
                    "Request failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise


class AuditLogger:
    """Specialized logger for audit trails and security events."""

    def __init__(self) -> None:
        """Initialize audit logger."""
        self.logger = get_logger("audit")

    def log_authentication(
        self,
        user_id: str,
        action: str,
        success: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Log authentication events."""
        self.logger.info(
            f"Authentication {action}",
            event_type="authentication",
            user_id=user_id,
            action=action,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            **kwargs,
        )

    def log_authorization(
        self, user_id: str, resource: str, action: str, allowed: bool, **kwargs: Any
    ) -> None:
        """Log authorization events."""
        self.logger.info(
            f"Authorization check for {resource}",
            event_type="authorization",
            user_id=user_id,
            resource=resource,
            action=action,
            allowed=allowed,
            **kwargs,
        )

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        record_count: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Log data access events."""
        self.logger.info(
            f"Data access: {action} on {resource}",
            event_type="data_access",
            user_id=user_id,
            resource=resource,
            action=action,
            record_count=record_count,
            **kwargs,
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Log security events."""
        level = LogLevel.WARNING if severity in {"medium", "high"} else LogLevel.INFO

        self.logger._log(
            level,
            f"Security event: {description}",
            event_type="security",
            security_event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            **kwargs,
        )


# Initialize logging on module import
setup_logging()

# Global audit logger instance
audit_logger = AuditLogger()
