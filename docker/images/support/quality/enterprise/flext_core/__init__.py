"""Mock flext_core for enterprise quality validation."""

from __future__ import annotations

import logging
from typing import Any


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
        return (
            r.ok(self._services[name])
            if name in self._services
            else r.fail(f"Service {name} not found")
        )
