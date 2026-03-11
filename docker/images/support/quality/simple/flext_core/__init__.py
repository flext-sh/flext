from typing import Dict, Any, Optional
import logging
import typing as t

from pydantic import BaseModel


class r:
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


def FlextLogger(name: str):
    return logging.getLogger(name)


class FlextContainer:
    def __init__(self):
        self._services = {}

    def register(self, name: str, service: Any):
        self._services[name] = service
        return r.ok(None)

    def get(self, name: str):
        if name in self._services:
            return r.ok(self._services[name])
        return r.fail(f"Service {name} not found")


class FlextModels:
    class Entity(BaseModel):
        id: str = "mock_id"

        def validate_domain_rules(self):
            return r.ok(None)


TAnyDict = Dict[str, Any]


# Placeholder for other imports used in validation
class MockAttr:
    pass


FlextBus = MockAttr
FlextSettings = MockAttr
FlextConstants = MockAttr
FlextContext = MockAttr
FlextDecorators = MockAttr
FlextDispatcher = MockAttr
FlextExceptions = MockAttr
h = t
x = MockAttr
FlextProcessors = MockAttr
p = t
FlextRegistry = MockAttr
FlextRuntime = MockAttr
FlextService = MockAttr
u = MockAttr

__all__ = [
    "r",
    "FlextLogger",
    "FlextContainer",
    "FlextModels",
    "TAnyDict",
    "FlextBus",
    "FlextSettings",
    "FlextConstants",
    "FlextContext",
    "FlextDecorators",
    "FlextDispatcher",
    "FlextExceptions",
    "h",
    "x",
    "FlextProcessors",
    "p",
    "FlextRegistry",
    "FlextRuntime",
    "FlextService",
    "t",
    "u",
]
