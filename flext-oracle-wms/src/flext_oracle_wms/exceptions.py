"""Oracle WMS exception classes using flext-core standards.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Enterprise-grade exception hierarchy for Oracle WMS operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Import flext-core exception base
from flext_core.domain.core import DomainError as FlextError

if TYPE_CHECKING:
    from flext_core.domain.types import WMSEntityName


class OracleWMSError(FlextError):
    """Base exception for Oracle WMS operations using flext-core standards."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        entity_name: WMSEntityName | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize Oracle WMS error with enhanced metadata.

        Args:
            message: Human-readable error message
            error_code: Oracle WMS specific error code
            entity_name: WMS entity associated with error
            details: Additional error context

        """
        super().__init__(message)
        self.error_code = error_code
        self.entity_name = entity_name
        self.details = details or {}


class AuthenticationError(OracleWMSError):
    """Oracle WMS authentication and authorization errors."""

    def __init__(
        self,
        message: str = "Oracle WMS authentication failed",
        auth_method: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize authentication error.

        Args:
            message: Authentication error message
            auth_method: Authentication method that failed
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="AUTH_FAILED", **kwargs)
        self.auth_method = auth_method


class APIError(OracleWMSError):
    """Oracle WMS API request and response errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize API error.

        Args:
            message: API error message
            status_code: HTTP status code
            response_body: Raw response body
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="API_ERROR", **kwargs)
        self.status_code = status_code
        self.response_body = response_body


class OracleWMSConnectionError(OracleWMSError):
    """Oracle WMS connection and network errors."""

    def __init__(
        self,
        message: str = "Oracle WMS connection failed",
        retry_count: int = 0,
        **kwargs: Any,
    ) -> None:
        """Initialize connection error.

        Args:
            message: Connection error message
            retry_count: Number of retry attempts made
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="CONNECTION_ERROR", **kwargs)
        self.retry_count = retry_count


class DataValidationError(OracleWMSError):
    """Oracle WMS data validation and schema errors."""

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        invalid_value: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize data validation error.

        Args:
            message: Validation error message
            field_name: Field that failed validation
            invalid_value: Value that failed validation
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field_name = field_name
        self.invalid_value = invalid_value


class ConfigurationError(OracleWMSError):
    """Oracle WMS configuration and setup errors."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Configuration error message
            config_key: Configuration key that caused error
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.config_key = config_key


class EntityNotFoundError(OracleWMSError):
    """Oracle WMS entity not found errors."""

    def __init__(
        self,
        entity_name: WMSEntityName,
        message: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize entity not found error.

        Args:
            entity_name: WMS entity that was not found
            message: Custom error message
            **kwargs: Additional error context

        """
        message = message or f"Oracle WMS entity '{entity_name}' not found"
        super().__init__(
            message,
            error_code="ENTITY_NOT_FOUND",
            entity_name=entity_name,
            **kwargs,
        )


class RateLimitError(OracleWMSError):
    """Oracle WMS rate limiting errors."""

    def __init__(
        self,
        message: str = "Oracle WMS API rate limit exceeded",
        retry_after_seconds: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Rate limit error message
            retry_after_seconds: Seconds to wait before retry
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED", **kwargs)
        self.retry_after_seconds = retry_after_seconds


class SchemaFlatteningError(OracleWMSError):
    """Oracle WMS schema flattening/deflattening errors."""

    def __init__(
        self,
        message: str,
        schema_operation: str,
        depth_level: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize schema flattening error.

        Args:
            message: Schema operation error message
            schema_operation: Operation that failed (flatten/deflatten)
            depth_level: Schema depth where error occurred
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="SCHEMA_PROCESSING_ERROR", **kwargs)
        self.schema_operation = schema_operation
        self.depth_level = depth_level


class FilterError(OracleWMSError):
    """Oracle WMS filtering and query errors."""

    def __init__(
        self,
        message: str,
        filter_type: str | None = None,
        filter_value: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize filter error.

        Args:
            message: Filter error message
            filter_type: Type of filter that failed
            filter_value: Filter value that caused error
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="FILTER_ERROR", **kwargs)
        self.filter_type = filter_type
        self.filter_value = filter_value


class SchemaError(OracleWMSError):
    """Oracle WMS schema definition and validation errors."""

    def __init__(
        self,
        message: str,
        schema_name: str | None = None,
        validation_details: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize schema error.

        Args:
            message: Schema error message
            schema_name: Schema name that caused error
            validation_details: Schema validation details
            **kwargs: Additional error context

        """
        super().__init__(message, error_code="SCHEMA_ERROR", **kwargs)
        self.schema_name = schema_name
        self.validation_details = validation_details or {}


# Create aliases for backward compatibility
OracleWMSFlatteningError = SchemaFlatteningError
OracleWMSFilterError = FilterError
OracleWMSSchemaError = SchemaError
