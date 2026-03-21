"""Mock flext_core for enterprise quality validation."""

from __future__ import annotations

import logging
from collections.abc import Container as BeartypeContainer

from dependency_injector.containers import Container as DIContainersContainer
from dependency_injector.providers import Container as DIProvidersContainer
from docker.models.containers import Container as DockerContainerModel
from matplotlib.container import Container as MatplotlibContainer
from python_on_whales import Container as WhalesContainer
from python_on_whales.components.container.cli_wrapper import (
    Container as WhalesCliContainer,
)
from tomlkit.container import Container as TomlkitContainer


class FlextTypes:
    """Mock types for the FLEXT ecosystem."""

    Primitives = str | int | float | bool
    Scalar = Primitives
    Container = Scalar | None
    RegisterableService = Container | logging.Logger


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

_CONTAINER_TYPES = (
    BeartypeContainer,
    DIContainersContainer,
    DIProvidersContainer,
    DockerContainerModel,
    MatplotlibContainer,
    WhalesContainer,
    WhalesCliContainer,
    TomlkitContainer,
)


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
