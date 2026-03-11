"""Mock flext_core.exceptions module."""

from __future__ import annotations

from typing import Any


class Error(Exception):
    """Base flext exception."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize error."""
        super().__init__(message)
        self.context = context or {}


class ValidationError(Error):
    """Validation error."""


class ConfigurationError(Error):
    """Configuration error."""


class ConnectionError(Error):
    """Connection error."""


class ProcessingError(Error):
    """Processing error."""


class AuthenticationError(Error):
    """Authentication error."""


class TimeoutError(Error):
    """Timeout error mock."""


__all__ = [
    "AuthenticationError",
    "ConfigurationError",
    "ConnectionError",
    "Error",
    "ProcessingError",
    "TimeoutError",
    "ValidationError",
]
