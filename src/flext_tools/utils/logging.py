"""Logging utilities for FLEXT tools using flext-observability."""

import warnings
from typing import ParamSpec, Protocol

from flext_core import get_logger as flext_get_logger
from flext_observability import (
    FlextLoggingService,
    flext_create_log_entry,
)


def _deprecation_warning() -> None:
    """Warn about deprecated logging utilities."""
    warnings.warn(
        "flext_tools.utils.logging is deprecated. Use flext_observability directly. "
        "Will be removed in v2.0.0. See CLAUDE.md for migration guide.",
        DeprecationWarning,
        stacklevel=3,
    )


class DetailedLogger:
    """DEPRECATED: Use flext-observability logging instead."""

    def __init__(self, name: str) -> None:
        """Initialize logger with flext-observability integration."""
        _deprecation_warning()
        self.logger = flext_get_logger(name)
        self.logging_service = FlextLoggingService()

    def debug(
        self,
        message: str,
        *args: object,
        exc_info: bool | None = None,
        stack_info: bool = False,
        extra: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Log debug message using flext-observability."""
        # Add exc_info and stack_info to metadata if provided
        if exc_info or stack_info:
            kwargs.update({"exc_info": exc_info, "stack_info": stack_info})
        self._log_with_observability("DEBUG", message, args, extra, kwargs)

    def info(
        self,
        message: str,
        *args: object,
        exc_info: bool | None = None,
        stack_info: bool = False,
        extra: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Log info message using flext-observability."""
        # Add exc_info and stack_info to metadata if provided
        if exc_info or stack_info:
            kwargs.update({"exc_info": exc_info, "stack_info": stack_info})
        self._log_with_observability("INFO", message, args, extra, kwargs)

    def warning(
        self,
        message: str,
        *args: object,
        exc_info: bool | None = None,
        stack_info: bool = False,
        extra: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Log warning message using flext-observability."""
        # Add exc_info and stack_info to metadata if provided
        if exc_info or stack_info:
            kwargs.update({"exc_info": exc_info, "stack_info": stack_info})
        self._log_with_observability("WARNING", message, args, extra, kwargs)

    def error(
        self,
        message: str,
        *args: object,
        exc_info: bool | None = None,
        stack_info: bool = False,
        extra: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Log error message using flext-observability."""
        # Add exc_info and stack_info to metadata if provided
        if exc_info or stack_info:
            kwargs.update({"exc_info": exc_info, "stack_info": stack_info})
        self._log_with_observability("ERROR", message, args, extra, kwargs)

    def exception(
        self,
        message: str,
        *args: object,
        extra: dict[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Log exception message using flext-observability."""
        self._log_with_observability("ERROR", message, args, extra, kwargs)

    def _log_with_observability(
        self,
        level: str,
        message: str,
        args: tuple[object, ...],
        extra: dict[str, object] | None,
        kwargs: dict[str, object],
    ) -> None:
        """Log using flext-observability patterns."""
        # Format message with args
        formatted_message = message % args if args else message

        # Combine extra and kwargs
        metadata = {**(extra or {}), **kwargs}

        # Create log entry using flext-observability
        flext_create_log_entry(
            message=formatted_message,
            level=level.lower(),
            context=metadata,
        )

        # Also use flext-core logger for backward compatibility
        if level == "DEBUG":
            self.logger.debug(formatted_message, **metadata)
        elif level == "INFO":
            self.logger.info(formatted_message, **metadata)
        elif level == "WARNING":
            self.logger.warning(formatted_message, **metadata)
        elif level == "ERROR":
            self.logger.error(formatted_message, **metadata)


def get_logger(name: str) -> DetailedLogger:
    """DEPRECATED: Get a detailed logger instance using flext-observability."""
    return DetailedLogger(name)


P = ParamSpec("P")


class OperationCallable(Protocol):
    """Protocol for operation functions."""

    def __call__(self, *args: object, **kwargs: object) -> object:
        """Call with arbitrary arguments."""
        ...


def log_operation(func: OperationCallable) -> OperationCallable:
    """DEPRECATED: Use @flext_monitor_function from flext-observability instead."""
    _deprecation_warning()

    def wrapper(*args: object, **kwargs: object) -> object:
        """Wrapper function to log operation with flext-observability."""
        # Simple wrapper that calls the original function
        return func(*args, **kwargs)

    return wrapper
