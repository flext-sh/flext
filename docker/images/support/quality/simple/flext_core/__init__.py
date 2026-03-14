"""Mock flext_core for simple quality validation."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence


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


class FlextModels:
    """Mock models container."""

    class Entity:
        """Mock FlextModels.Entity base class."""

        def __init__(self, id_val: str = "mock_id") -> None:
            """Initialize entity."""
            self.id = id_val

        def validate_domain_rules(self) -> Result[None]:
            """Validate mock rules."""
            return Result.ok(None)


TAnyDict = t.Dict


# Placeholder for other imports used in validation
class MockAttr:
    """Generic mock attribute."""


FlextBus = MockAttr
FlextSettings = MockAttr
FlextConstants = MockAttr
FlextContext = MockAttr
FlextDecorators = MockAttr
FlextDispatcher = MockAttr
FlextExceptions = MockAttr
h: t.RegisterableService | None = None
x = MockAttr
FlextProcessors = MockAttr
p: t.RegisterableService | None = None
FlextRegistry = MockAttr
FlextRuntime = MockAttr
FlextService = MockAttr
u = MockAttr

__all__ = [
    "FlextBus",
    "FlextConstants",
    "FlextContainer",
    "FlextContext",
    "FlextDecorators",
    "FlextDispatcher",
    "FlextExceptions",
    "FlextLogger",
    "FlextModels",
    "FlextProcessors",
    "FlextRegistry",
    "FlextRuntime",
    "FlextService",
    "FlextSettings",
    "TAnyDict",
    "h",
    "p",
    "r",
    "u",
    "x",
]
