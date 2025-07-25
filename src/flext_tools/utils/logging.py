"""Logging utilities for FLEXT tools."""

import logging
from collections.abc import Callable
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log levels for FLEXT tools."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class DetailedLogger:
    """Detailed logger for FLEXT operations."""

    def __init__(self, name: str) -> None:
        """Initialize logger."""
        self.logger = logging.getLogger(name)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def exception(self, message: str) -> None:
        """Log exception message."""
        self.logger.exception(message)


def get_logger(name: str) -> DetailedLogger:
    """Get a detailed logger instance."""
    return DetailedLogger(name)


def log_operation(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log operations."""

    def wrapper(*args: Any, **kwargs: object) -> Any:
        logger = get_logger(func.__name__)
        logger.info(f"Starting operation: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completed operation: {func.__name__}")
            return result
        except Exception as e:
            logger.exception(f"Failed operation: {func.__name__} - {e}")
            raise

    return wrapper
