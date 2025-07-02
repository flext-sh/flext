"""Centralized Logging Configuration for FLEXT Oracle WMS Integration.

This module provides a unified 5-level logging system with heavy TRACE emphasis
across all Oracle WMS integration modules. Zero tolerance for mock/fallback
implementations - production-ready logging only.

Logging Levels (in priority order):
1. TRACE (5)    - Maximum detail, function entry/exit, variable states
2. DEBUG (10)   - Debugging information, data flows, conditions
3. INFO (20)    - Normal operations, major steps, confirmations
4. WARNING (30) - Warnings, recoverable issues, deprecations
5. CRITICAL (50) - Critical errors, system failures, data corruption

CLI Integration: Always use with CLI for runtime log level control.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field
from rich.console import Console
from rich.logging import RichHandler


class LogLevel(IntEnum):
    """5-Level logging system with TRACE receiving maximum weight."""

    TRACE = 5  # Most verbose - function entry/exit, variable states
    DEBUG = 10  # Debug information - data flows, conditions
    INFO = 20  # Normal operations - major steps, confirmations
    WARNING = 30  # Warnings - recoverable issues, deprecations
    CRITICAL = 50  # Critical errors - system failures, data corruption


class TraceContext(BaseModel):
    """Rich context for comprehensive TRACE logging."""

    operation: str = Field(..., description="Current operation name")
    module: str = Field(..., description="Module performing operation")
    function: str | None = Field(default=None, description="Function name")
    sql_query: str | None = Field(default=None, description="SQL query being executed")
    api_endpoint: str | None = Field(default=None, description="API endpoint")
    http_method: str | None = Field(default=None, description="HTTP method")
    connection_id: str | None = Field(
        default=None, description="Database connection ID"
    )
    transaction_id: str | None = Field(default=None, description="Transaction ID")
    request_id: str | None = Field(default=None, description="Request ID")
    timing_ms: float | None = Field(
        default=None, description="Operation timing in milliseconds"
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Operation parameters"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class LoggingConfig(BaseModel):
    """Centralized logging configuration with TRACE emphasis."""

    # Core settings - TRACE is default for maximum visibility
    level: LogLevel = Field(default=LogLevel.TRACE, description="Default log level")
    enable_trace: bool = Field(default=True, description="Enable TRACE level logging")
    enable_console: bool = Field(default=True, description="Enable console output")
    enable_file: bool = Field(default=True, description="Enable file output")

    # File settings
    log_dir: str = Field(default="logs", description="Log directory")
    main_log_file: str = Field(
        default="flext_oracle_wms.log", description="Main log file"
    )
    error_log_file: str = Field(
        default="flext_oracle_wms_errors.log", description="Error log file"
    )
    trace_log_file: str = Field(
        default="flext_oracle_wms_trace.log", description="TRACE-only log file"
    )
    max_file_size: int = Field(
        default=100_000_000, description="Max file size in bytes"
    )
    backup_count: int = Field(default=15, description="Number of backup files")

    # Format settings with TRACE emphasis
    trace_format: str = Field(
        default="[{timestamp}] TRACE | {module}:{function}:{line} | {operation} | {message} | {context}",
        description="TRACE level format template",
    )
    standard_format: str = Field(
        default="[{timestamp}] {level} | {module} | {message}",
        description="Standard format template",
    )

    # Performance settings
    buffer_size: int = Field(default=16384, description="Log buffer size")
    flush_interval: float = Field(
        default=0.5, description="Auto-flush interval in seconds"
    )


class EnterpriseFormatter(logging.Formatter):
    """Custom formatter with special handling for TRACE level."""

    def __init__(self, config: LoggingConfig) -> None:
        super().__init__()
        self.config = config
        self.trace_format = config.trace_format
        self.standard_format = config.standard_format

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with level-specific formatting."""
        # Add custom fields
        record.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[
            :-3
        ]
        record.module = (
            record.name.split(".")[-1] if "." in record.name else record.name
        )
        record.function = getattr(record, "funcName", "unknown")
        record.line = getattr(record, "lineno", 0)

        # Handle TRACE level specially
        if record.levelno == LogLevel.TRACE:
            # Extract trace context if available
            trace_context = getattr(record, "trace_context", {})
            context_str = self._format_trace_context(trace_context)

            record.context = context_str
            record.level = "TRACE"
            record.operation = (
                trace_context.get("operation", "unknown")
                if isinstance(trace_context, dict)
                else getattr(trace_context, "operation", "unknown")
            )

            try:
                return self.trace_format.format(**record.__dict__)
            except (KeyError, ValueError):
                # Fallback to standard format
                return self._format_standard(record)
        else:
            return self._format_standard(record)

    def _format_trace_context(
        self, context: TraceContext | dict[str, Any] | Any
    ) -> str:
        """Format trace context for optimal readability."""
        if isinstance(context, TraceContext):
            parts = []

            if context.sql_query:
                sql = context.sql_query.strip().replace("\n", " ")
                if len(sql) > 100:
                    sql = sql[:97] + "..."
                parts.append(f"sql={sql}")

            if context.api_endpoint:
                parts.append(f"api={context.api_endpoint}")

            if context.connection_id:
                parts.append(f"conn={context.connection_id}")

            if context.transaction_id:
                parts.append(f"tx={context.transaction_id}")

            if context.timing_ms is not None:
                parts.append(f"time={context.timing_ms:.2f}ms")

            if context.params:
                param_str = " ".join(f"{k}={v}" for k, v in context.params.items())
                parts.append(f"params=[{param_str}]")

            return " | ".join(parts)

        if isinstance(context, dict):
            return " | ".join(f"{k}={v}" for k, v in context.items() if v is not None)

        return str(context) if context else ""

    def _format_standard(self, record: logging.LogRecord) -> str:
        """Format standard log levels."""
        record.level = record.levelname
        try:
            return self.standard_format.format(**record.__dict__)
        except (KeyError, ValueError):
            # Ultimate fallback
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            return f"[{timestamp}] {record.levelname} | {record.name} | {record.getMessage()}"


class FlextEnterpriseLogger:
    """Enterprise-grade logger with 5-level system and TRACE emphasis."""

    _instances: ClassVar[dict[str, FlextEnterpriseLogger]] = {}
    _config: ClassVar[LoggingConfig | None] = None
    _lock: ClassVar[threading.RLock] = threading.RLock()
    _configured: ClassVar[bool] = False
    _console: ClassVar[Console] = Console(stderr=True, force_terminal=True)

    def __init__(self, name: str) -> None:
        """Initialize logger instance."""
        self.name = name
        self.logger = logging.getLogger(name)
        self._start_times: dict[str, float] = {}
        self._setup_logger()

    @classmethod
    def configure(cls, config: LoggingConfig | None = None) -> None:
        """Configure global logging settings."""
        with cls._lock:
            if cls._configured:
                return

            cls._config = config or LoggingConfig()

            # Add TRACE level to logging module
            logging.addLevelName(LogLevel.TRACE, "TRACE")

            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(cls._config.level)

            # Clear existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Setup handlers
            cls._setup_handlers(cls._config)
            cls._configured = True

    @classmethod
    def _setup_handlers(cls, config: LoggingConfig) -> None:
        """Set up logging handlers."""
        root_logger = logging.getLogger()
        formatter = EnterpriseFormatter(config)

        # Console handler with Rich support
        if config.enable_console:
            rich_handler = RichHandler(
                console=cls._console,
                show_time=True,
                show_level=True,
                show_path=True,
                rich_tracebacks=True,
                markup=True,
            )
            rich_handler.setLevel(config.level)
            root_logger.addHandler(rich_handler)

        # File handlers
        if config.enable_file:
            from logging.handlers import RotatingFileHandler

            # Ensure log directory exists
            log_path = Path(config.log_dir)
            log_path.mkdir(parents=True, exist_ok=True)

            # Main log file (all levels)
            main_file_path = log_path / config.main_log_file
            main_handler = RotatingFileHandler(
                main_file_path,
                maxBytes=config.max_file_size,
                backupCount=config.backup_count,
                encoding="utf-8",
            )
            main_handler.setLevel(config.level)
            main_handler.setFormatter(formatter)
            root_logger.addHandler(main_handler)

            # Error log file (WARNING and above)
            error_file_path = log_path / config.error_log_file
            error_handler = RotatingFileHandler(
                error_file_path,
                maxBytes=config.max_file_size // 2,
                backupCount=config.backup_count,
                encoding="utf-8",
            )
            error_handler.setLevel(LogLevel.WARNING)
            error_handler.setFormatter(formatter)
            root_logger.addHandler(error_handler)

            # TRACE-only log file for maximum detail
            if config.enable_trace:
                trace_file_path = log_path / config.trace_log_file
                trace_handler = RotatingFileHandler(
                    trace_file_path,
                    maxBytes=config.max_file_size * 2,  # Larger for TRACE
                    backupCount=config.backup_count * 2,
                    encoding="utf-8",
                )
                trace_handler.setLevel(LogLevel.TRACE)
                trace_handler.addFilter(lambda record: record.levelno == LogLevel.TRACE)
                trace_handler.setFormatter(formatter)
                root_logger.addHandler(trace_handler)

    @classmethod
    def get_logger(cls, name: str) -> FlextEnterpriseLogger:
        """Get or create logger instance."""
        if not cls._configured:
            cls.configure()

        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = cls(name)
            return cls._instances[name]

    def _setup_logger(self) -> None:
        """Set up individual logger."""
        if self._config:
            self.logger.setLevel(self._config.level)
        else:
            self.logger.setLevel(LogLevel.TRACE)

    def trace(
        self,
        message: str,
        context: TraceContext | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Log TRACE level message with rich context - MAXIMUM WEIGHT."""
        if self.logger.isEnabledFor(LogLevel.TRACE):
            # Create log record
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

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log DEBUG level message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log INFO level message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log WARNING level message."""
        self.logger.warning(message, extra=kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log CRITICAL level message."""
        self.logger.critical(message, extra=kwargs)

    def trace_sql(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
        connection_id: str | None = None,
        timing_ms: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Specialized TRACE logging for SQL operations - HEAVY EMPHASIS."""
        context = TraceContext(
            operation="sql_execute",
            module=self.name,
            sql_query=sql,
            connection_id=connection_id,
            timing_ms=timing_ms,
            params=params or {},
            metadata=kwargs,
        )
        self.trace("SQL execution", context)

    def trace_api(
        self,
        method: str,
        endpoint: str,
        status_code: int | None = None,
        timing_ms: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Specialized TRACE logging for API operations - HEAVY EMPHASIS."""
        context = TraceContext(
            operation="api_call",
            module=self.name,
            api_endpoint=endpoint,
            http_method=method,
            timing_ms=timing_ms,
            metadata={"status_code": status_code, **kwargs},
        )
        self.trace(f"API call: {method} {endpoint}", context)

    def trace_operation(self, operation_name: str) -> TraceOperationContext:
        """Context manager for tracing operations with timing - HEAVY EMPHASIS."""
        return TraceOperationContext(self, operation_name)

    def start_operation(self, operation: str) -> None:
        """Start timing an operation for performance monitoring."""
        self._start_times[operation] = time.perf_counter()
        self.trace(
            f"Operation started: {operation}",
            TraceContext(operation=operation, module=self.name),
        )

    def end_operation(self, operation: str, **kwargs: Any) -> None:
        """End timing an operation and log duration."""
        if operation in self._start_times:
            duration = time.perf_counter() - self._start_times[operation]
            del self._start_times[operation]
            duration_ms = round(duration * 1000, 2)

            self.trace(
                f"Operation completed: {operation}",
                TraceContext(
                    operation=operation,
                    module=self.name,
                    timing_ms=duration_ms,
                    metadata=kwargs,
                ),
            )
        else:
            self.warning(f"Operation {operation} was not started or already ended")


class TraceOperationContext:
    """Context manager for automatic TRACE operation timing."""

    def __init__(self, logger: FlextEnterpriseLogger, operation_name: str) -> None:
        self.logger = logger
        self.operation_name = operation_name
        self.start_time: float | None = None

    def __enter__(self) -> TraceOperationContext:
        self.start_time = time.perf_counter()
        self.logger.trace(
            f"Starting operation: {self.operation_name}",
            TraceContext(operation=self.operation_name, module=self.logger.name),
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        if self.start_time is not None:
            duration_ms = (time.perf_counter() - self.start_time) * 1000

            if exc_type is None:
                self.logger.trace(
                    f"Completed operation: {self.operation_name}",
                    TraceContext(
                        operation=self.operation_name,
                        module=self.logger.name,
                        timing_ms=duration_ms,
                        metadata={"status": "success"},
                    ),
                )
            else:
                self.logger.critical(
                    f"Failed operation: {self.operation_name}",
                    operation=self.operation_name,
                    error=str(exc_val),
                    timing_ms=duration_ms,
                    status="failed",
                )


# Global configuration and convenience functions
def configure_flext_logging(
    level: LogLevel = LogLevel.TRACE,
    *,
    enable_trace: bool = True,
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """Configure global FLEXT logging with TRACE emphasis."""
    config = LoggingConfig(
        level=level,
        enable_trace=enable_trace,
        log_dir=log_dir,
        enable_console=enable_console,
        enable_file=enable_file,
    )
    FlextEnterpriseLogger.configure(config)


def get_flext_logger(name: str) -> FlextEnterpriseLogger:
    """Get enterprise logger instance for the given name."""
    return FlextEnterpriseLogger.get_logger(name)


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

    configure_flext_logging(
        level=log_level, enable_trace=True, enable_console=True, enable_file=True
    )


# Default configuration with TRACE emphasis
configure_flext_logging()


__all__ = [
    "LogLevel",
    "TraceContext",
    "LoggingConfig",
    "FlextEnterpriseLogger",
    "TraceOperationContext",
    "configure_flext_logging",
    "get_flext_logger",
    "configure_cli_logging",
]
