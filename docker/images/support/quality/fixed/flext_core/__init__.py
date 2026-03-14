"""Complete Mock flext_core for FLEXT Quality - Fixed version."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class FlextTypes:
    """Mock types for the FLEXT ecosystem."""

    Primitives = str | int | float | bool
    Scalar = Primitives
    Container = Scalar | Sequence["Container"] | Mapping[str, "Container"] | None
    RegisterableService = Container | logging.Logger
    Dict = Mapping[str, Container]


t = FlextTypes


class Result[T]:
    """Railway result pattern mock."""

    def __init__(
        self,
        *,
        success: bool,
        value: T | None = None,
        error: str | None = None,
    ) -> None:
        """Initialize result."""
        self.success = success
        self.is_failure = not success
        self.value = value
        self.error_message = error

    @property
    def is_success(self) -> bool:
        """Return True if successful."""
        return self.success

    @classmethod
    def ok(cls, value: T | None = None) -> Result[T]:
        """Return successful result."""
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: str) -> Result[T]:
        """Return failed result."""
        return cls(success=False, error=error)


# Alias for compatibility
r = Result


class FlextExceptions:
    """Mock exceptions module."""

    class Error(Exception):
        """Base flext exception."""

        def __init__(self, message: str, context: t.Dict | None = None) -> None:
            """Initialize error."""
            super().__init__(message)
            self.context = context or {}

    class ValidationError(Error):
        """Validation error."""

    class ConfigurationError(Error):
        """Configuration error."""

    class FlextConnectionError(Error):
        """Connection error."""

    class ProcessingError(Error):
        """Processing error."""

    class AuthenticationError(Error):
        """Authentication error."""

    class FlextTimeoutError(Error):
        """Timeout error mock."""


def logger_factory(name: str) -> logging.Logger:
    """Return mock logger."""
    return logging.getLogger(name)


FlextLogger = logger_factory


class FlextContainer:
    """Mock dependency injection container."""

    def __init__(self) -> None:
        """Initialize container."""
        self._services: dict[str, t.RegisterableService] = {}

    def register(self, name: str, service: t.RegisterableService) -> Result[None]:
        """Register service."""
        self._services[name] = service
        return Result.ok(None)

    def get(self, name: str) -> Result[t.RegisterableService]:
        """Get service."""
        if name in self._services:
            return Result.ok(self._services[name])
        return Result.fail(f"Service {name} not found")

    def get_typed[U](self, service_type: type[U]) -> Result[U]:
        """Get service by type."""
        for service in self._services.values():
            if isinstance(service, service_type):
                return Result.ok(service)
        return Result.fail(f"Service of type {service_type} not found")

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

        def validate_domain_rules(self) -> Result[None]:
            """Validate mock rules."""
            return Result.ok(None)


class MNamespace:
    """Mock m namespace."""

    class Value(BaseModel):
        """Mock m.Value base class."""


m = MNamespace


class FlextSettings(BaseSettings):
    """Mock FlextSettings for configuration."""


class FlextConstants:
    """Mock constants class."""

    VERSION: str = "0.9.0"
    DEFAULT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3


# Type aliases for compatibility
TAnyDict = t.Dict
TConfigDict = t.Dict

# Additional helpers for mock imports
h: t.RegisterableService | None = None
x: t.RegisterableService | None = None
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
