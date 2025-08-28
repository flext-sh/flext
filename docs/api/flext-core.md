# FLEXT Core API Reference

**Complete reference for FLEXT Core foundation patterns**

This document provides accurate API documentation for FLEXT Core v0.9.0, based on the actual implementation in `src/flext_core/__init__.py`.

## 🎯 Essential Imports

### Core Patterns (Most Common)

```python
from flext_core import (
    # Railway-oriented programming
    FlextResult,          # Type-safe error handling

    # Dependency injection
    FlextContainer,       # Enterprise DI container
    get_flext_container, # Global container access

    # Domain modeling
    FlextEntity,         # Rich domain entities
    FlextValue,    # Immutable value objects
    FlextAggregates,  # DDD aggregates

    # Configuration
    FlextConfig,   # Environment-aware config
)
```

### Additional Patterns

```python
from flext_core import (
    # Commands and handlers (CQRS)
    FlextCommands,
    FlextHandlers,

    # Validation
    FlextValidation,
    FlextValidators,
    FlextPredicates,

    # Utilities
    FlextUtilities,
    FlextGenerators,

    # Logging
    FlextLogger,
    get_logger,
)
```

## 🚂 FlextResult[T] - Railway-Oriented Programming

Type-safe error handling without exceptions.

### Basic Usage

```python
from flext_core import FlextResult

def divide(a: int, b: int) -> FlextResult[float]:
    if b == 0:
        return FlextResult[None].fail("Division by zero")
    return FlextResult[None].ok(a / b)

# Chain operations safely
result = (
    divide(10, 2)
    .map(lambda x: x * 2)        # Transform success value
    .flat_map(lambda x: divide(x, 3))  # Chain another operation
)

if result.success:
    print(f"Result: {result.data}")
else:
    print(f"Error: {result.error}")
```

### Key Methods

- `FlextResult[None].ok(value)` - Create success result
- `FlextResult[None].fail(error)` - Create failure result
- `.map(func)` - Transform success value
- `.flat_map(func)` - Chain operations returning FlextResult
- `.success` - Boolean indicating success
- `.data` - Success value (when success=True)
- `.error` - Error message (when success=False)

## 📦 FlextContainer - Dependency Injection

Enterprise dependency injection with type safety.

### Basic Usage

```python
from flext_core import FlextContainer, get_flext_container

# Use global container
container = FlextContainer.get_global()

# Register services
result = container.register("user_service", UserService())
assert result.success

# Retrieve services
service_result = container.get("user_service")
if service_result.success:
    user_service = service_result.data
```

### Key Methods

- `container.register(name, instance)` - Register service instance
- `container.get(name)` - Retrieve service (returns FlextResult)
- `container.contains(name)` - Check if service exists
- `FlextContainer.get_global()` - Get global container instance

## 🏛️ Domain Modeling

### FlextEntity - Rich Domain Entities

```python
from flext_core import FlextEntity

class User(FlextEntity):
    name: str
    email: str
    is_active: bool = False

    def activate(self) -> FlextResult[None]:
        if self.is_active:
            return FlextResult[None].fail("User already active")

        self.is_active = True
        # Domain events can be added here
        return FlextResult[None].ok(None)
```

### FlextValue - Immutable Values

```python
from flext_core import FlextValue

class Email(FlextValue):
    address: str

    def __post_init__(self):
        if "@" not in self.address:
            raise ValueError("Invalid email format")
```

### FlextAggregates - DDD Aggregates

```python
from flext_core import FlextAggregates

class Order(FlextAggregates):
    customer_id: str
    items: list
    total: float

    def add_item(self, item) -> FlextResult[None]:
        self.items.append(item)
        self.total += item.price
        # Domain event would be added here
        return FlextResult[None].ok(None)
```

## ⚙️ Configuration Management

### FlextConfig - Environment-Aware Config

```python
from flext_core import FlextConfig

class AppSettings(FlextConfig):
    database_url: str = "postgresql://localhost/app"
    log_level: str = "INFO"
    debug: bool = False

    class Config:
        env_prefix = "APP_"

# Usage
settings = AppSettings()  # Reads from environment variables
print(settings.database_url)  # Uses APP_DATABASE_URL if set
```

## 📝 Structured Logging

### FlextLogger Usage

```python
from flext_core import get_logger

logger = get_logger(__name__)

# Structured logging with context
logger.info("Processing request",
    user_id="123",
    operation="user_update",
    duration_ms=45)

# Error logging with FlextResult
result = some_operation()
if result.is_failure:
    logger.error("Operation failed",
        error=result.error,
        operation="some_operation")
```

## 🧪 Testing Patterns

### Using FlextResult in Tests

```python
import pytest
from flext_core import FlextResult

def test_user_activation():
    user = User(name="John", email="john@test.com")

    result = user.activate()

    assert result.success
    assert user.is_active

def test_user_double_activation():
    user = User(name="John", email="john@test.com", is_active=True)

    result = user.activate()

    assert result.is_failure
    assert "already active" in result.error
```

### Container Testing

```python
def test_service_registration():
    container = FlextContainer()
    service = UserService()

    result = container.register("user_service", service)

    assert result.success

    retrieved = container.get("user_service")
    assert retrieved.success
    assert retrieved.data is service
```

---

This API reference is based on actual implementation analysis and provides working examples for all documented patterns.
