# Mock flext_core.exceptions module
"""Mock exceptions module for enterprise compatibility."""


class Error(Exception):
    """Base flext exception."""

    def __init__(self, message: str, context: dict[str, object] = None):
        super().__init__(message)
        self.context = context or {}


class ValidationError(Error):
    """Validation error."""

    pass


class ConfigurationError(Error):
    """Configuration error."""

    pass


class ConnectionError(Error):
    """Connection error."""

    pass


class ProcessingError(Error):
    """Processing error."""

    pass


class AuthenticationError(Error):
    """Authentication error."""

    pass


class TimeoutError(Error):
    """Timeout error."""

    pass


__all__ = [
    "Error",
    "ValidationError",
    "ConfigurationError",
    "ConnectionError",
    "ProcessingError",
    "AuthenticationError",
    "TimeoutError",
]
