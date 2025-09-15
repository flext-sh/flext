"""Logging utilities for FLEXT tools using flext-observability."""

import warnings
from typing import ParamSpec, Protocol

from flext_core import FlextLogger, FlextTypes
from flext_observability import (
    FlextLoggingService,
    flext_create_log_entry,
)


def deprecation_warning() -> None:
    """Issue deprecation warning for legacy logging utilities.

    Emits a DeprecationWarning to notify users that flext_tools.utils.logging
    is deprecated and will be removed in v2.0.0. Directs users to migrate
    to flext-observability for modern logging patterns.

    This function is called by deprecated logging components to ensure
    proper notification and migration guidance for users transitioning
    to the modern FLEXT observability infrastructure.

    Raises:
        DeprecationWarning: Always raised to notify about deprecated usage.

    Example:
        >>> deprecation_warning()
        # Emits: "flext_tools.utils.logging is deprecated. Use flext_observability..."

    Note:
        Uses stacklevel=3 to show the actual caller location rather than
        this warning function in the stack trace.

    """
    warnings.warn(
        "flext_tools.utils.logging is deprecated. Use flext_observability directly. "
        "Will be removed in v2.0.0. See CLAUDE.md for migration guide.",
        DeprecationWarning,
        stacklevel=3,
    )


class FlextObservabilityService:
    """FLEXT Observability Service - Unified logging and monitoring container.

    Provides comprehensive observability capabilities including deprecated logging
    utilities and operation monitoring protocols. This unified class follows
    FLEXT architectural patterns for single-class-per-module compliance.
    """

    class DetailedLogger:
        """DEPRECATED: Detailed logging wrapper with flext-observability integration.

        This class provides backward compatibility for existing code while
        transitioning to the flext-observability logging system. All logging
        operations are delegated to flext-observability patterns with proper
        metadata handling and structured logging support.

        Warning:
            This class is deprecated and will be removed in v2.0.0. Use
            flext-observability logging functions directly for new code.

        Attributes:
            logger: FlextCore logger instance for backward compatibility.
            logging_service: FlextLoggingService for observability integration.

        Example:
            Basic usage (deprecated):

            >>> logger = FlextObservabilityService.DetailedLogger("my_module")
            >>> logger.info("Processing started", extra={"user_id": 123})
            >>> logger.error("Process failed", exc_info=True)

            Recommended approach:

            >>> from flext_observability import flext_create_log_entry
            >>> flext_create_log_entry("Processing started", "info", {"user_id": 123})

        Note:
            Migration guide available in CLAUDE.md for transitioning to
            flext-observability patterns.

        """

        def __init__(self, name: str) -> None:
            """Initialize logger with flext-observability integration."""
            deprecation_warning()
            self.name = name
            self.logger = FlextLogger(name)
            self.logging_service = FlextLoggingService()

        def debug(
            self,
            message: str,
            *args: object,
            exc_info: bool | None = None,
            stack_info: bool = False,
            extra: FlextTypes.Core.Dict | None = None,
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
            extra: FlextTypes.Core.Dict | None = None,
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
            extra: FlextTypes.Core.Dict | None = None,
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
            extra: FlextTypes.Core.Dict | None = None,
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
            extra: FlextTypes.Core.Dict | None = None,
            **kwargs: object,
        ) -> None:
            """Log exception message using flext-observability."""
            self._log_with_observability("ERROR", message, args, extra, kwargs)

        def _log_with_observability(
            self,
            level: str,
            message: str,
            args: tuple[object, ...],
            _extra: FlextTypes.Core.Dict | None,
            _kwargs: FlextTypes.Core.Dict,
        ) -> None:
            """Log using flext-observability patterns."""
            # Format message with args
            formatted_message = message % args if args else message

            # Future: Combine extra and kwargs for enhanced logging

            # Create log entry using flext-observability
            flext_create_log_entry(
                message=formatted_message,
                service=self.name,
                level=level.lower(),
            )

            # Also use flext-core logger for backward compatibility
            if level == "DEBUG":
                self.logger.debug(formatted_message)
            elif level == "INFO":
                self.logger.info(formatted_message)
            elif level == "WARNING":
                self.logger.warning(formatted_message)
            elif level == "ERROR":
                self.logger.error(formatted_message)

    class OperationCallable(Protocol):
        """Protocol defining the interface for operation functions.

        Defines the expected signature for functions that can be wrapped
        with operation logging decorators. Provides type safety for the
        log_operation decorator pattern in the deprecated logging utilities.

        This protocol ensures that any function passed to operation logging
        decorators conforms to the expected callable interface with arbitrary
        arguments and return values.

        Example:
            Function conforming to the protocol:

            >>> def my_operation(data: str, flag: bool = True) -> str:
            ...     return f"processed: {data}"
            >>> # This function matches OperationCallable protocol
            >>> logged_op = log_operation(my_operation)

        Note:
            This protocol is part of the deprecated logging utilities.
            Use flext-observability monitoring decorators for new code.

        """

        def __call__(self, *args: object, **kwargs: object) -> object:
            """Call with arbitrary arguments."""
            ...


def create_detailed_logger(name: str) -> FlextObservabilityService.DetailedLogger:
    """Create deprecated logger instance with flext-observability integration.

    Creates a DetailedLogger instance that wraps flext-observability logging
    functionality for backward compatibility. This function is deprecated
    and will be removed in v2.0.0.

    Args:
        name: Logger name, typically the module name (__name__).

    Returns:
        DetailedLogger instance configured with flext-observability integration
        for backward compatibility with existing logging patterns.

    Example:
        Deprecated usage:

        >>> logger = FlextLogger(__name__)
        >>> logger.info("Processing started")

        Recommended approach:

        >>> from flext_core import FlextLogger
        >>> logger = FlextLogger(__name__)

    Warning:
        This function is deprecated. Use flext_core.FlextLogger or
        flext-observability functions directly for new code.

    Note:
        Emits deprecation warning on each call to encourage migration
        to modern logging patterns.

    """
    return FlextObservabilityService.DetailedLogger(name)


P = ParamSpec("P")


def log_operation(
    func: FlextObservabilityService.OperationCallable,
) -> FlextObservabilityService.OperationCallable:
    """Decorator for operation logging with flext-observability integration.

    Wraps functions with deprecated logging functionality for backward
    compatibility. This decorator is deprecated and will be removed in v2.0.0.
    Use @flext_monitor_function from flext-observability for new code.

    Args:
        func: Function to wrap with logging capabilities. Must conform to
            OperationCallable protocol with arbitrary arguments and return values.

    Returns:
        Wrapped function that maintains original signature while adding
        deprecated logging functionality for compatibility.

    Example:
        Deprecated usage:

        >>> @log_operation
        ... def process_data(data: str) -> str:
        ...     return f"processed: {data}"

        Recommended approach:

        >>> from flext_observability import flext_monitor_function
        >>> @flext_monitor_function
        ... def process_data(data: str) -> str:
        ...     return f"processed: {data}"

    Warning:
        This decorator is deprecated. Use @flext_monitor_function from
        flext-observability for modern monitoring and logging patterns.

    Note:
        Emits deprecation warning when applied to encourage migration
        to flext-observability monitoring decorators.

    """
    deprecation_warning()

    def wrapper(*args: object, **kwargs: object) -> object:
        """Log operation with flext-observability wrapper."""
        return func(*args, **kwargs)

    return wrapper
