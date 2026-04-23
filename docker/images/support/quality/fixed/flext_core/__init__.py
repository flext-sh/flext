"""Mock flext_core package for fixed quality validation."""

from __future__ import annotations

import logging
from collections.abc import (
    Callable,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from typing import Any

from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    Error,
    ProcessingError,
    TimeoutError,
    ValidationError,
)


class FlextTypes:
    """Minimal type surface used by the quality Docker images."""

    Dict = dict[str, Any]
    JsonMapping = dict[str, Any]
    Scalar = str | int | float | bool
    StrSequence = tuple[str, ...]


t = FlextTypes


class Result[T]:
    """Small railway-style result used by the mock package."""

    def __init__(
        self,
        *,
        success: bool,
        value: T | None = None,
        error: str | None = None,
    ) -> None:
        self.success = success
        self.is_failure = not success
        self.value = value
        self.error = error

    @property
    def is_success(self) -> bool:
        """Return whether the result is successful."""
        return self.success

    @classmethod
    def ok(cls, value: T | None = None) -> Result[T]:
        """Build a successful result instance."""
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: str) -> Result[T]:
        """Build a failed result instance."""
        return cls(success=False, error=error)


r = Result


class FlextContainer:
    """Minimal dependency container mock."""

    def __init__(self) -> None:
        self._services: MutableMapping[str, ServiceValue] = {}

    def register(self, name: str, service: ServiceValue) -> Result[None]:
        """Register a service object by name."""
        self._services[name] = service
        return Result.ok(None)

    def get(self, name: str) -> Result[ServiceValue]:
        """Resolve a service object by name."""
        service = self._services.get(name)
        if service is None:
            return Result.fail(f"Service {name} not found")
        return Result.ok(service)


class FlextBus:
    """Placeholder bus type."""


class FlextConstants:
    """Placeholder constants namespace."""


class FlextContext:
    """Placeholder context type."""


class FlextDecorators:
    """Placeholder decorators namespace."""


class FlextDispatcher:
    """Placeholder dispatcher type."""


class FlextHandlers:
    """Placeholder handlers namespace."""


class FlextMixins:
    """Placeholder mixins namespace."""


class FlextModels:
    """Placeholder models namespace."""


class FlextProcessors:
    """Placeholder processors namespace."""


class FlextProtocols:
    """Placeholder protocols namespace."""


class FlextRegistry:
    """Placeholder registry type."""


class FlextSettings:
    """Placeholder settings type."""


class FlextService[T]:
    """Placeholder service base."""


class FlextUtilities:
    """Placeholder utilities namespace."""

    @staticmethod
    def generate(_name: str) -> str:
        """Return a generated string payload."""
        return ""


FlextLogger = logging.Logger

type ServiceValue = (
    FlextBus
    | FlextConstants
    | FlextContext
    | FlextDecorators
    | FlextDispatcher
    | FlextHandlers
    | FlextLogger
    | FlextMixins
    | FlextModels
    | FlextProcessors
    | FlextProtocols
    | FlextRegistry
    | FlextSettings
    | FlextUtilities
    | bool
    | float
    | int
    | str
)


class FlextExceptions:
    """Exception namespace mirroring the public flext_core alias."""

    AuthenticationError = AuthenticationError
    ConfigurationError = ConfigurationError
    ConnectionError = ConnectionError
    Error = Error
    ProcessingError = ProcessingError
    TimeoutError = TimeoutError
    ValidationError = ValidationError


c = FlextConstants
d = FlextDecorators
e = FlextExceptions
h = FlextHandlers
m = FlextModels
p = FlextProtocols
s = FlextService
u = FlextUtilities
x = FlextMixins

__all__: list[str] = [
    "AuthenticationError",
    "ConfigurationError",
    "ConnectionError",
    "Error",
    "FlextBus",
    "FlextConstants",
    "FlextContainer",
    "FlextContext",
    "FlextDecorators",
    "FlextDispatcher",
    "FlextExceptions",
    "FlextHandlers",
    "FlextLogger",
    "FlextMixins",
    "FlextModels",
    "FlextProcessors",
    "FlextProtocols",
    "FlextRegistry",
    "FlextService",
    "FlextSettings",
    "FlextTypes",
    "FlextUtilities",
    "ProcessingError",
    "Result",
    "TimeoutError",
    "ValidationError",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]
