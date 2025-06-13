"""Exceptions for API client.

This module defines exception classes for various error conditions that can
occur when using the API client.
"""

from typing import Any


class ApiError(Exception):
    """Base exception for all API client errors."""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize API error.

        Args:
            message: Error message
            code: Error code (optional)
            details: Additional error details (optional)
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.code:
            return f"{self.code}: {self.message}"
        return self.message


class ConfigurationError(ApiError):
    """Exception raised when there is an issue with the client configuration."""


class ConnectionError(ApiError):
    """Exception raised when there is an issue connecting to the API."""


class AuthenticationError(ApiError):
    """Exception raised when authentication fails."""


class RequestError(ApiError):
    """Exception raised when there is an issue with the request."""


class ResponseError(ApiError):
    """Exception raised when there is an issue with the API response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize response error.

        Args:
            message: Error message
            status_code: HTTP status code (optional)
            response_body: Response body (optional)
            code: Error code (optional)
            details: Additional error details (optional)
        """
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message, code, details)

    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = super().__str__()
        if self.status_code:
            return f"{base_str} (Status: {self.status_code})"
        return base_str


class ValidationError(ApiError):
    """Exception raised when data validation fails."""

    def __init__(
        self,
        message: str,
        field_errors: dict[str, str] | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field_errors: Mapping of field names to error messages (optional)
            code: Error code (optional)
            details: Additional error details (optional)
        """
        self.field_errors = field_errors or {}
        super().__init__(message, code, details)

    def __str__(self) -> str:
        """Return string representation of the error."""
        base_str = super().__str__()
        if self.field_errors:
            field_errors_str = ", ".join(
                f"{field}: {error}" for field, error in self.field_errors.items()
            )
            return f"{base_str} (Fields: {field_errors_str})"
        return base_str
