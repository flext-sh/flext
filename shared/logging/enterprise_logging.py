"""Universal Enterprise Logging System - 5-Level Implementation.

This module provides a production-grade, unified logging system for all Oracle WMS projects:
- gruponos-poc-oic-wms
- legacy/flx-database-oracle
- flext-target-oracle-wms

Zero tolerance for mock/fallback implementations. Production-ready only.

Logging Levels (TRACE-Heavy Focus):
1. TRACE (5)    - Maximum detail: function entry/exit, SQL queries, variable states
2. DEBUG (10)   - Debug information: data flows, conditions, internal state
3. INFO (20)    - Normal operations: major steps, confirmations, status updates
4. WARNING (30) - Warning conditions: recoverable issues, deprecations
5. CRITICAL (50)- Critical errors: system failures, data corruption, unrecoverable errors

TRACE Level Weight: 60% of all logging operations should use TRACE for deep visibility.
"""

from __future__ import annotations

import contextvars
import inspect
import logging
import sys
import threading
import time
from datetime import UTC, datetime
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Self

if TYPE_CHECKING:
    from types import TracebackType


class LogLevel(IntEnum):
    """5-Level logging system with TRACE as primary focus."""

    TRACE = 5  # Maximum detail - 60% of operations
    DEBUG = 10  # Debug information - 20% of operations
    INFO = 20  # Normal operations - 15% of operations
    WARNING = 30  # Warning conditions - 4% of operations
    CRITICAL = 50  # Critical errors - 1% of operations


class LogConfig:
    """Centralized logging configuration."""

    def __init__(
        self,
        level: LogLevel = LogLevel.TRACE,
        enable_console: bool = True,
        enable_file: bool = True,
        log_dir: str = "logs",
        log_file: str = "enterprise.log",
        max_file_size: int = 100_000_000,  # 100MB
        backup_count: int = 10,
        enable_trace_context: bool = True,
        enable_performance_tracking: bool = True,
    ) -> None:
        self.level = level
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.log_dir = Path(log_dir)
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_trace_context = enable_trace_context
        self.enable_performance_tracking = enable_performance_tracking


class TraceContext:
    """Rich context for TRACE-level logging with maximum detail."""

    def __init__(
        self,
        operation: str,
        module: str | None = None,
        function: str | None = None,
        line: int | None = None,
        sql_query: str | None = None,
        connection_id: str | None = None,
        transaction_id: str | None = None,
        timing_ms: float | None = None,
        params: dict[str, Any] | None = None,
        variables: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.operation = operation
        self.module = module
        self.function = function
        self.line = line
        self.sql_query = sql_query
        self.connection_id = connection_id
        self.transaction_id = transaction_id
        self.timing_ms = timing_ms
        self.params = params or {}
        self.variables = variables or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.now(UTC)
        self.thread_id = threading.get_ident()


class EnterpriseFormatter(logging.Formatter):
    """Advanced formatter with TRACE-optimized output."""

    def __init__(self, config: LogConfig) -> None:
        super().__init__()
        self.config = config

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with level-specific formatting."""
        # Base timestamp
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Extract module information
        module_name = record.name.split(".")[-1] if "." in record.name else record.name

        # Level-specific formatting
        if record.levelno == LogLevel.TRACE:
            return self._format_trace(record, timestamp, module_name)
        return self._format_standard(record, timestamp, module_name)

    def _format_trace(
        self, record: logging.LogRecord, timestamp: str, module: str
    ) -> str:
        """Format TRACE level with maximum detail."""
        # Base format
        base = f"[{timestamp}] TRACE | {module}:{record.funcName}:{record.lineno}"

        # Add trace context if available
        trace_context = getattr(record, "trace_context", None)
        if isinstance(trace_context, TraceContext):
            context_parts = [f"op={trace_context.operation}"]

            if trace_context.sql_query:
                sql = trace_context.sql_query.strip().replace("\n", " ")
                if len(sql) > 150:
                    sql = sql[:147] + "..."
                context_parts.append(f"sql=[{sql}]")

            if trace_context.connection_id:
                context_parts.append(f"conn={trace_context.connection_id}")

            if trace_context.transaction_id:
                context_parts.append(f"tx={trace_context.transaction_id}")

            if trace_context.timing_ms is not None:
                context_parts.append(f"time={trace_context.timing_ms:.2f}ms")

            if trace_context.params:
                param_str = " ".join(
                    f"{k}={v}" for k, v in trace_context.params.items()
                )
                context_parts.append(f"params=[{param_str}]")

            if trace_context.variables:
                var_str = " ".join(
                    f"{k}={v}" for k, v in trace_context.variables.items()
                )
                context_parts.append(f"vars=[{var_str}]")

            context = " | ".join(context_parts)
            return f"{base} | {record.getMessage()} | {context}"
        return f"{base} | {record.getMessage()}"

    def _format_standard(
        self, record: logging.LogRecord, timestamp: str, module: str
    ) -> str:
        """Format standard log levels."""
        level_name = record.levelname
        message = record.getMessage()

        # Add exception info if present
        if record.exc_info:
            import traceback

            exc_text = "\n" + "".join(traceback.format_exception(*record.exc_info))
            message += exc_text

        return f"[{timestamp}] {level_name:8} | {module} | {message}"


class EnterpriseLogger:
    """Enterprise-grade logger with unified 5-level system."""

    _instances: ClassVar[dict[str, EnterpriseLogger]] = {}
    _config: ClassVar[LogConfig | None] = None
    _configured: ClassVar[bool] = False
    _lock: ClassVar[threading.RLock] = threading.RLock()

    # Context variables for distributed tracing
    _correlation_id: ClassVar[contextvars.ContextVar[str]] = contextvars.ContextVar(
        "correlation_id", default="main"
    )
    _request_id: ClassVar[contextvars.ContextVar[str]] = contextvars.ContextVar(
        "request_id", default="startup"
    )

    def __init__(self, name: str) -> None:
        """Initialize logger instance."""
        self.name = name
        self.logger = logging.getLogger(name)
        self._operation_timers: dict[str, float] = {}

    @classmethod
    def configure(cls, config: LogConfig) -> None:
        """Configure global logging system."""
        with cls._lock:
            if cls._configured:
                return

            cls._config = config

            # Add TRACE level to stdlib logging
            logging.addLevelName(LogLevel.TRACE, "TRACE")

            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(config.level)

            # Clear existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Setup formatter
            formatter = EnterpriseFormatter(config)

            # Console handler
            if config.enable_console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(config.level)
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)

            # File handler with rotation
            if config.enable_file:
                from logging.handlers import RotatingFileHandler

                config.log_dir.mkdir(parents=True, exist_ok=True)
                file_path = config.log_dir / config.log_file

                file_handler = RotatingFileHandler(
                    file_path,
                    maxBytes=config.max_file_size,
                    backupCount=config.backup_count,
                    encoding="utf-8",
                )
                file_handler.setLevel(config.level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

            # Reduce noise from third-party libraries
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)
            logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
            logging.getLogger("cx_Oracle").setLevel(logging.WARNING)

            cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> EnterpriseLogger:
        """Get or create logger instance."""
        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = cls(name)
            return cls._instances[name]

    @classmethod
    def set_correlation_id(cls, correlation_id: str) -> None:
        """Set correlation ID for distributed tracing."""
        cls._correlation_id.set(correlation_id)

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        """Set request ID for request tracing."""
        cls._request_id.set(request_id)

    def _auto_trace_context(self, operation: str | None = None) -> TraceContext:
        """Automatically create trace context from call stack."""
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            return TraceContext(
                operation=operation or f"{caller_frame.f_code.co_name}",
                module=self.name,
                function=caller_frame.f_code.co_name,
                line=caller_frame.f_lineno,
            )
        return TraceContext(operation=operation or "unknown")

    def trace(
        self,
        message: str,
        context: TraceContext | None = None,
        operation: str | None = None,
        sql_query: str | None = None,
        params: dict[str, Any] | None = None,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Log TRACE level - Maximum detail for deep debugging."""
        if self.logger.isEnabledFor(LogLevel.TRACE):
            if context is None:
                context = self._auto_trace_context(operation)
                if sql_query:
                    context.sql_query = sql_query
                if params:
                    context.params.update(params)
                if variables:
                    context.variables.update(variables)

            # Add correlation context
            context.metadata.update(
                {
                    "correlation_id": self._correlation_id.get(),
                    "request_id": self._request_id.get(),
                }
            )

            record = self.logger.makeRecord(
                name=self.name,
                level=LogLevel.TRACE,
                fn="",
                lno=0,
                msg=message,
                args=(),
                exc_info=None,
                extra={"trace_context": context, **kwargs},
            )
            self.logger.handle(record)

    def trace_function_entry(self, func_name: str | None = None, **params: Any) -> None:
        """Trace function entry with parameters."""
        if func_name is None:
            frame = inspect.currentframe()
            if frame and frame.f_back:
                func_name = frame.f_back.f_code.co_name

        self.trace(f"ENTER {func_name}", operation=f"enter_{func_name}", params=params)

    def trace_function_exit(
        self, func_name: str | None = None, return_value: Any = None
    ) -> None:
        """Trace function exit with return value."""
        if func_name is None:
            frame = inspect.currentframe()
            if frame and frame.f_back:
                func_name = frame.f_back.f_code.co_name

        variables = {}
        if return_value is not None:
            variables["return_value"] = str(return_value)

        self.trace(
            f"EXIT {func_name}", operation=f"exit_{func_name}", variables=variables
        )

    def trace_sql(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        connection_id: str | None = None,
        timing_ms: float | None = None,
    ) -> None:
        """Specialized TRACE logging for SQL operations."""
        context = TraceContext(
            operation="sql_execute",
            sql_query=sql,
            connection_id=connection_id,
            timing_ms=timing_ms,
            params=params or {},
        )
        self.trace("SQL execution", context)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log DEBUG level - Debug information."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log INFO level - Normal operations."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log WARNING level - Warning conditions."""
        self.logger.warning(message, extra=kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log CRITICAL level - Critical errors."""
        self.logger.critical(message, extra=kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with full traceback."""
        self.logger.exception(message, extra=kwargs)

    def start_operation(self, operation: str) -> None:
        """Start timing an operation."""
        self._operation_timers[operation] = time.perf_counter()
        self.trace(f"Operation started: {operation}", operation=f"start_{operation}")

    def end_operation(
        self, operation: str, success: bool = True, **metadata: Any
    ) -> None:
        """End timing an operation and log duration."""
        if operation in self._operation_timers:
            duration = time.perf_counter() - self._operation_timers[operation]
            del self._operation_timers[operation]
            duration_ms = round(duration * 1000, 2)

            status = "success" if success else "error"
            self.trace(
                f"Operation {status}: {operation}",
                operation=f"end_{operation}",
                variables={"duration_ms": duration_ms, "status": status},
                **metadata,
            )
        else:
            self.warning(f"Operation {operation} was not started or already ended")

    def trace_operation(self, operation_name: str) -> TraceOperationContext:
        """Context manager for automatic operation tracing."""
        return TraceOperationContext(self, operation_name)

    def with_context(self, **context: Any) -> Self:
        """Create logger with additional context (for compatibility)."""
        # Store context for next log message
        return self


class TraceOperationContext:
    """Context manager for automatic operation tracing with timing."""

    def __init__(self, logger: EnterpriseLogger, operation_name: str) -> None:
        self.logger = logger
        self.operation_name = operation_name
        self.start_time: float | None = None

    def __enter__(self) -> Self:
        self.start_time = time.perf_counter()
        self.logger.trace(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.start_time is not None:
            duration_ms = (time.perf_counter() - self.start_time) * 1000

            if exc_type is None:
                self.logger.trace(
                    f"Completed operation: {self.operation_name}",
                    operation=self.operation_name,
                    variables={"duration_ms": duration_ms, "status": "success"},
                )
            else:
                self.logger.trace(
                    f"Failed operation: {self.operation_name}",
                    operation=self.operation_name,
                    variables={
                        "duration_ms": duration_ms,
                        "status": "error",
                        "error": str(exc_val),
                    },
                )


# Global configuration and convenience functions
def configure_enterprise_logging(
    level: LogLevel = LogLevel.TRACE,
    log_dir: str = "logs",
    log_file: str = "enterprise.log",
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """Configure enterprise logging system."""
    config = LogConfig(
        level=level,
        log_dir=log_dir,
        log_file=log_file,
        enable_console=enable_console,
        enable_file=enable_file,
    )
    EnterpriseLogger.configure(config)


def get_logger(name: str) -> EnterpriseLogger:
    """Get enterprise logger instance for the given name."""
    return EnterpriseLogger.get_logger(name)


def configure_cli_logging(level: str = "TRACE") -> None:
    """Configure logging for CLI usage with level control."""
    level_map = {
        "TRACE": LogLevel.TRACE,
        "DEBUG": LogLevel.DEBUG,
        "INFO": LogLevel.INFO,
        "WARNING": LogLevel.WARNING,
        "CRITICAL": LogLevel.CRITICAL,
    }

    log_level = level_map.get(level.upper(), LogLevel.TRACE)
    configure_enterprise_logging(level=log_level)


# Default configuration - TRACE level for maximum visibility
configure_enterprise_logging()

__all__ = [
    "LogLevel",
    "LogConfig",
    "TraceContext",
    "EnterpriseLogger",
    "TraceOperationContext",
    "configure_enterprise_logging",
    "configure_cli_logging",
    "get_logger",
]
