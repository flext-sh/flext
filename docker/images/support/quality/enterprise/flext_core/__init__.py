"""Mock flext_core for enterprise quality validation."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence


class FlextTypes:
    """Mock types for the FLEXT ecosystem."""

    Primitives = str | int | float | bool
    Scalar = Primitives
    object = Scalar | Sequence["object"] | Mapping[str, "object"] | None
    RegisterableService = object | logging.Logger


t = FlextTypes


class Result[T]:
    """Railway result pattern mock."""

    def __init__(
        self,
        success: bool,  # noqa: FBT001
        value: T | None = None,
        error: str | None = None,
    ) -> None:
        """Initialize result.

        Using boolean positional argument here is a mock implementation detail
        preserving internal success/failure state representation.
        """
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
        return cls(True, value=value)

    @classmethod
    def fail(cls, error: str) -> Result[T]:
        """Return failed result."""
        return cls(False, error=error)


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
