# Complete Mock flext_core for FLEXT Quality - ALL IMPORTS
from typing import Dict, Optional, Union, List, Any
import logging
import typing as t

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class r:
    """Mock r for enterprise compatibility."""

    def __init__(self, success: bool, data: Any = None, error: Optional[str] = None):
        self.success = success
        self.is_failure = not success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data: Any = None):
        return cls(True, data=data)

    @classmethod
    def fail(cls, error: str):
        return cls(False, error=error)


class FlextExceptions:
    """Mock exceptions module."""

    class Error(Exception):
        """Base flext exception."""

        def __init__(self, message: str, context: Optional[dict[str, Any]] = None):
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


def FlextLogger(name: str):
    """Mock logger factory."""
    return logging.getLogger(name)


class FlextContainer:
    """Mock dependency injection container."""

    def __init__(self):
        self._services = {}

    def register(self, name: str, service: Any):
        self._services[name] = service
        return r.ok(None)

    def get(self, name: str):
        if name in self._services:
            return r.ok(self._services[name])
        return r.fail(f"Service {name} not found")

    def get_typed(self, service_type: type):
        """Get service by type."""
        for service in self._services.values():
            if isinstance(service, service_type):
                return r.ok(service)
        return r.fail(f"Service of type {service_type} not found")

    @staticmethod
    def get_global():
        """Get global container instance."""
        return _global_container


# Mock global container instance
_global_container = FlextContainer()


def get_flext_container():
    """Get global container instance."""
    return _global_container


class FlextModels:
    class Entity(BaseModel):
        """Mock FlextModels.Entity base class."""

        id: str = "mock_id"

        def validate_domain_rules(self):
            return r.ok(None)


class m:
    class Value(BaseModel):
        """Mock m.Value base class."""

        pass


class FlextSettings(BaseSettings):
    """Mock FlextSettings for configuration."""

    pass


class FlextConstants:
    """Mock constants class to fix import errors."""

    VERSION = "0.9.0"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3


# Type aliases for compatibility
TAnyDict = Dict[str, Any]
TConfigDict = Dict[str, Any]

# Additional helpers for imports
h = t  # Just a mock
x = t  # Just a mock

# Export all required symbols
__all__ = [
    "r",
    "FlextLogger",
    "FlextContainer",
    "get_flext_container",
    "FlextModels",
    "m",
    "FlextSettings",
    "FlextConstants",
    "TAnyDict",
    "TConfigDict",
    "FlextExceptions",
    "h",
    "x",
]
