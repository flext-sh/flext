"""Complete Mock flext_core for FLEXT Quality - Fixed version."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class r:  # noqa: N801
    """Railway result pattern mock."""

    def __class_getitem__(cls, _item: Any) -> Any:
        """Support r[T] syntax."""
        return cls

    def __init__(
        self,
        success: bool,  # noqa: FBT001
        data: Any | None = None,
        error: str | None = None,
    ) -> None:
        """Initialize result."""
        self.success = success
        self.is_failure = not success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data: Any | None = None) -> r:
        """Return successful result."""
        return cls(True, data=data)

    @classmethod
    def fail(cls, error: str) -> r:
        """Return failed result."""
        return cls(False, error=error)


class FlextExceptions:
    """Mock exceptions module."""

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

    class ConnectionError(Error):  # noqa: A001
        """Connection error."""

    class ProcessingError(Error):
        """Processing error."""

    class AuthenticationError(Error):
        """Authentication error."""

    class TimeoutError(Error):  # noqa: A001
        """Timeout error mock."""


def FlextLogger(  # noqa: N802
    name: str,
) -> logging.Logger:
    """Return mock logger."""
    return logging.getLogger(name)


class FlextContainer:
    """Mock dependency injection container."""

    def __init__(self) -> None:
        """Initialize container."""
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> r:
        """Register service."""
        self._services[name] = service
        return r.ok(None)

    def get(self, name: str) -> r:
        """Get service."""
        if name in self._services:
            return r.ok(self._services[name])
        return r.fail(f"Service {name} not found")

    def get_typed(self, service_type: type[Any]) -> r:
        """Get service by type."""
        for service in self._services.values():
            if isinstance(service, service_type):
                return r.ok(service)
        return r.fail(f"Service of type {service_type} not found")

    @staticmethod
    def get_global() -> FlextContainer:
        """Get global container instance."""
        return _global_container


# Mock global container instance
_global_container = FlextContainer()


def get_flext_container() -> FlextContainer:
    """Get global container instance."""
    return _global_container


class FlextModels:
    """Mock models container."""

    class Entity(BaseModel):
        """Mock FlextModels.Entity base class."""

        id: str = "mock_id"

        def validate_domain_rules(self) -> r:
            """Validate mock rules."""
            return r.ok(None)


class m:  # noqa: N801
    """Mock m namespace."""

    class Value(BaseModel):
        """Mock m.Value base class."""


class FlextSettings(BaseSettings):
    """Mock FlextSettings for configuration."""


class FlextConstants:
    """Mock constants class."""

    VERSION: str = "0.9.0"
    DEFAULT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3


# Type aliases for compatibility
TAnyDict = dict[str, Any]
TConfigDict = dict[str, Any]

# Additional helpers for mock imports
h: Any = None
x: Any = None
e = FlextExceptions

# Export all required symbols
__all__ = [
    "FlextConstants",
    "FlextContainer",
    "FlextExceptions",
    "FlextLogger",
    "FlextModels",
    "FlextSettings",
    "TAnyDict",
    "TConfigDict",
    "e",
    "get_flext_container",
    "h",
    "m",
    "r",
    "x",
]
