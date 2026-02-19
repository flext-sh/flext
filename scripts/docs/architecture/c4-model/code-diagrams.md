# Code Diagrams


<!-- TOC START -->
- [Overview](#overview)
- [Key Classes and Interfaces](#key-classes-and-interfaces)
  - [Error Handling](#error-handling)
  - [Dependency Injection](#dependency-injection)
  - [Domain Models](#domain-models)
<!-- TOC END -->

## Overview

Code-level architecture showing class relationships and implementation patterns:

```plantuml
@startuml FLEXT Code Architecture
!include <C4/C4_Code>

class FlextResult {
    +value: T
    +error: E
    +is_success: bool
    +is_failure: bool
    +unwrap(): T
    +map(func): FlextResult[U]
    +flat_map(func): FlextResult[U]
}

class FlextContainer {
    -_services: Dict[str, object]
    +register(name: str, service: object)
    +resolve(name: str): object
    +get_global(): FlextContainer
}

abstract class FlextModel {
    +id: str
}

class Entity {
    +id: str
    +equals(other): bool
}

class Value {
    +equals(other): bool
}

class AggregateRoot {
    +id: str
    +version: int
    +domain_events: List[DomainEvent]
}

class FlextDispatcher {
    -_handlers: Dict[type, Callable]
    +register_handler(command_type, handler)
    +dispatch(command): FlextResult
}

class FlextBus {
    -_subscribers: Dict[type, List[Callable]]
    +subscribe(event_type, handler)
    +publish(event)
}

FlextResult --> FlextContainer : uses
FlextContainer --> FlextModel : manages
FlextModel <|-- Entity
FlextModel <|-- Value
FlextModel <|-- AggregateRoot

FlextDispatcher --> FlextBus : publishes events
FlextBus --> FlextLogger : logs events

note right of FlextResult
    Railway-oriented
    error handling
end note

note right of FlextContainer
    Dependency injection
    singleton container
end note

note right of FlextModel
    Domain-Driven Design
    base classes
end note
@enduml
```

## Key Classes and Interfaces

### Error Handling

```python
class FlextResult[T, E]:
    """Monadic result type for railway-oriented programming."""

    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def is_failure(self) -> bool:
        return self._error is not None

    def unwrap(self) -> T:
        if self.is_failure:
            raise RuntimeError(f"Cannot unwrap failure result: {self._error}")
        return self._value

    def map[U](self, func: Callable[[T], U]) -> FlextResult[U, E]:
        if self.is_success:
            return FlextResult(func(self._value))
        return FlextResult(error=self._error)

    def flat_map[U](self, func: Callable[[T], FlextResult[U, E]]) -> FlextResult[U, E]:
        if self.is_success:
            return func(self._value)
        return FlextResult(error=self._error)
```

### Dependency Injection

```python
class FlextContainer:
    """Global dependency injection container."""

    _instance: Optional['FlextContainer'] = None

    def __init__(self):
        self._services: Dict[str, object] = {}

    @classmethod
    def get_global(cls) -> 'FlextContainer':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, service: object) -> None:
        self._services[name] = service

    def resolve(self, name: str) -> object:
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        return self._services[name]
```

### Domain Models

```python
class FlextModels:
    """Domain-Driven Design base classes."""

    class Entity:
        """Base class for domain entities."""

        def __init__(self, id: str):
            self.id = id

        def equals(self, other: 'Entity') -> bool:
            return isinstance(other, Entity) and self.id == other.id

    class Value:
        """Base class for value objects."""

        def equals(self, other: 'Value') -> bool:
            return isinstance(other, type(self)) and self.__dict__ == other.__dict__

    class AggregateRoot(Entity):
        """Base class for aggregate roots."""

        def __init__(self, id: str):
            super().__init__(id)
            self._version = 0
            self._domain_events: List[DomainEvent] = []

        def add_domain_event(self, event: DomainEvent) -> None:
            self._domain_events.append(event)

        def clear_domain_events(self) -> List[DomainEvent]:
            events = self._domain_events.copy()
            self._domain_events.clear()
            return events
```

---

**Generated:** 2025-10-10 15:19:05
**Version:** 0.9.0
