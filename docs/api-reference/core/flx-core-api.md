# FLX Core API Reference

**Status**: 🚧 CRITICAL DOCUMENTATION GAP - Implementation Complete, Documentation Needed  
**Implementation**: `/flx/src/flx/core/`  
**Last Updated**: 2025-01-06

## Overview

The FLX Core module implements the domain layer of the hexagonal architecture, containing pure business logic with no external dependencies. This is the heart of the FLX framework, providing domain-driven design (DDD) patterns and clean architecture compliance.

## TODO IMPLEMENTATION ALIGNMENT
- [ ] Document all 40+ exported components from `/flx/src/flx/core/__init__.py`
- [ ] Add code examples for each domain component
- [ ] Cross-reference with actual implementation patterns
- [ ] Link to architecture documentation
- [ ] Add usage patterns from real codebase

## Architecture Compliance

✅ **Pure Domain Layer**: No infrastructure dependencies  
✅ **DDD Patterns**: Entities, Value Objects, Aggregates, Domain Events  
✅ **Clean Interfaces**: Protocol-based abstractions  
✅ **Event-Driven**: Domain events for business logic  

## Core Components

### Domain Objects

#### AggregateRoot
```python
from flx.core import AggregateRoot

# TODO: Add real usage example from implementation
class OrderAggregate(AggregateRoot):
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document AggregateRoot usage patterns
- [ ] Add business logic examples
- [ ] Link to DDD patterns guide
- [ ] Show event publication patterns

#### Entity
```python
from flx.core import Entity

# TODO: Add real usage example from implementation
class OrderItem(Entity):
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document Entity patterns
- [ ] Show identity management
- [ ] Add validation examples

#### ValueObject
```python
from flx.core import ValueObject

# TODO: Add real usage example from implementation
class Money(ValueObject):
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document ValueObject immutability
- [ ] Show comparison patterns
- [ ] Add validation examples

### Domain Events

#### DomainEvent
```python
from flx.core import DomainEvent

# TODO: Add real usage example from implementation
class OrderCreated(DomainEvent):
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document event patterns
- [ ] Show event publishing
- [ ] Link to event sourcing guide

### Domain Services

#### DomainService
```python
from flx.core import DomainService

# TODO: Add real usage example from implementation
class OrderPricingService(DomainService):
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document service patterns
- [ ] Show business logic orchestration
- [ ] Add service composition examples

### Protocols and Interfaces

#### Adapter Protocol
```python
from flx.core import Adapter

# TODO: Add real usage example from implementation
class DatabaseAdapter(Adapter):
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document adapter contracts
- [ ] Show port-adapter binding
- [ ] Link to ports documentation

#### LoggerInterface
```python
from flx.core import LoggerInterface, DomainLogger

# TODO: Add real usage example from implementation
def create_domain_logger() -> DomainLogger:
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document logging patterns
- [ ] Show structured logging
- [ ] Link to infrastructure logging

### Models and Enums

#### FlxAdapterModel
```python
from flx.core import FlxAdapterModel

# TODO: Add real usage example from implementation
model = FlxAdapterModel(...)
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document all model classes
- [ ] Show model validation
- [ ] Add configuration examples

#### Status Enums
```python
from flx.core import (
    FlxAdapterStatus,
    FlxConnectionStatus,
    FlxOperationStatus,
    FlxTransactionStatus
)

# TODO: Add real usage examples from implementation
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document all enum types
- [ ] Show status transitions
- [ ] Add state management patterns

### Mixins System

#### ConfigurationMixin
```python
from flx.core import ConfigurationMixin

# TODO: Add real usage example from implementation
class ConfigurableService(ConfigurationMixin):
    pass
```

#### ErrorHandlingMixin
```python
from flx.core import ErrorHandlingMixin

# TODO: Add real usage example from implementation
class RobustService(ErrorHandlingMixin):
    pass
```

#### HealthCheckMixin
```python
from flx.core import HealthCheckMixin

# TODO: Add real usage example from implementation
class MonitorableService(HealthCheckMixin):
    pass
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document all 8+ mixin classes
- [ ] Show mixin composition patterns
- [ ] Add cross-cutting concerns examples
- [ ] Link to mixin development guide

### Exceptions

#### DomainError
```python
from flx.core import DomainError

# TODO: Add real usage example from implementation
raise DomainError("Business rule violation")
```

#### ValidationError
```python
from flx.core import ValidationError

# TODO: Add real usage example from implementation
raise ValidationError("Invalid entity state")
```

#### BusinessRuleViolationError
```python
from flx.core import BusinessRuleViolationError

# TODO: Add real usage example from implementation
raise BusinessRuleViolationError("Order cannot be modified after shipping")
```

**TODO DOCUMENTATION GAPS:**
- [ ] Document exception hierarchy
- [ ] Show error handling patterns
- [ ] Add validation examples

## Usage Patterns

### TODO: Complete Usage Documentation
- [ ] **Domain Modeling**: How to model business domains using FLX core
- [ ] **Event Sourcing**: Implementing event-driven business logic
- [ ] **Aggregate Design**: Designing aggregates for complex business logic
- [ ] **Service Composition**: Composing domain services
- [ ] **Validation Patterns**: Implementing business rule validation
- [ ] **Testing Patterns**: Testing domain logic in isolation

## Cross-References

### TODO: Add Cross-Reference Links
- [ ] **Architecture Guide**: `/docs/architecture/core-domain-layer.md`
- [ ] **DDD Patterns**: `/docs/architecture/patterns/domain-driven-design-patterns.md`
- [ ] **Event Sourcing**: `/docs/architecture/patterns/event-sourcing-implementation.md`
- [ ] **Development Guide**: `/docs/guides/development/domain-modeling.md`
- [ ] **Examples**: `/docs/examples/core/`
- [ ] **Testing**: `/docs/development/testing/core-testing.md`

## Next Steps

1. **🔴 CRITICAL**: Add real code examples from `/flx/src/flx/core/`
2. **🔴 CRITICAL**: Document all exported components
3. **🟡 HIGH**: Create domain modeling guide
4. **🟡 HIGH**: Add comprehensive usage patterns
5. **🟢 MEDIUM**: Link to architecture documentation

---

**Implementation Reference**: `/flx/src/flx/core/__init__.py`  
**Related Documentation**: [Architecture Guide](../architecture/core-domain-layer.md) | [DDD Patterns](../architecture/patterns/domain-driven-design-patterns.md)