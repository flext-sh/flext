# flext-core

## Table of Contents

- [flext-core](#flext-core)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Key Components](#key-components)
    - [FlextContainer (Dependency Injection)](#flextcontainer-dependency-injection)
    - [FlextDispatcher (CQRS Pattern)](#flextdispatcher-cqrs-pattern)
    - [FlextResult (Railway-Oriented Programming)](#flextresult-railway-oriented-programming)
    - [FlextBus (Domain Events)](#flextbus-domain-events)
    - [FlextLogger (Structured Logging)](#flextlogger-structured-logging)
  - [Architecture Patterns](#architecture-patterns)
    - [Clean Architecture Implementation](#clean-architecture-implementation)
    - [SOLID Principles](#solid-principles)
  - [Configuration Management](#configuration-management)
    - [FlextConfig](#flextconfig)
  - [Error Handling Strategy](#error-handling-strategy)
    - [FlextExceptions Hierarchy](#flextexceptions-hierarchy)
  - [Utilities and Helpers](#utilities-and-helpers)
    - [u](#u)
  - [Performance Features](#performance-features)
    - [FlextMetrics](#flextmetrics)
  - [Development Guidelines](#development-guidelines)
    - [Testing with flext-core](#testing-with-flext-core)
  - [Migration from Previous Versions](#migration-from-previous-versions)
    - [From v0.x to v1.0.0](#from-v0x-to-v100)
    - [Migration Guide](#migration-guide)
  - [Best Practices](#best-practices)
    - [Dependency Injection Best Practices](#dependency-injection-best-practices)
    - [Error Handling Best Practices](#error-handling-best-practices)
    - [Logging Best Practices](#logging-best-practices)
  - [Support and Documentation](#support-and-documentation)

**Core Framework** - The foundation of the FLEXT ecosystem providing essential patterns, abstractions, and utilities.

## Overview

flext-core is the foundational framework that provides the core patterns and abstractions used throughout the FLEXT ecosystem. It implements enterprise-grade patterns like Dependency Injection,

CQRS, Railway-Oriented Programming, and Domain Events.

## Installation

```bash
pip install flext-core
```

## Key Components

### FlextContainer (Dependency Injection)

Central dependency injection container for managing component lifecycles and dependencies.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

# Register services
container = FlextContainer()
container.register(IService, ServiceImplementation())
container.register(IRepository, RepositoryImplementation())

# Resolve dependencies
service = container.resolve(IService)
```

### FlextDispatcher (CQRS Pattern)

Command Query Responsibility Segregation implementation for handling commands and queries.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

# Register handlers
dispatcher = FlextDispatcher()
dispatcher.register_handler(CreateUserCommand, CreateUserHandler)
dispatcher.register_handler(GetUserQuery, GetUserHandler)

# Dispatch operations
result = dispatcher.dispatch(CreateUserCommand(user_data))
user = dispatcher.dispatch(GetUserQuery(user_id))
```

### FlextResult (Railway-Oriented Programming)

Functional error handling with happy path and sad path composition.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

def divide(a: float, b: float) -> FlextResult[float, Exception]:
    if b == 0:
        return FlextResult.failure(ValueError("Cannot divide by zero"))
    return FlextResult.success(a / b)

# Compose operations
result = (FlextResult.success(10.0)
          .bind(lambda x: divide(x, 2.0))
          .bind(lambda x: divide(x, 3.0)))

if result.is_success:
    print(f"Result: {result.unwrap()}")
else:
    print(f"Error: {result.failure()}")
```

### FlextBus (Domain Events)

Event-driven architecture support with domain event publishing and subscription.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

# Subscribe to events
bus = FlextBus()
bus.subscribe(UserCreatedEvent, UserCreatedHandler)
bus.subscribe(UserDeletedEvent, UserDeletedHandler)

# Publish events
bus.emit(UserCreatedEvent(user_id="123", email="user@example.com"))
```

### FlextLogger (Structured Logging)

Enterprise-grade logging with structured data support and multiple output formats.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

logger = FlextLogger.get_logger(__name__)

# Structured logging
logger.info("User created",
           extra={
               "user_id": "123",
               "email": "user@example.com",
               "source": "api"
           })

# Different log levels
logger.debug("Debug information")
logger.warning("Warning message", extra={"context": "validation"})
logger.error("Error occurred", exc_info=True)
```

## Architecture Patterns

### Clean Architecture Implementation

flext-core implements core clean architecture principles:

- **Dependency Inversion**: Components depend on abstractions, not concretions
- **Single Responsibility**: Each class has one reason to change
- **Interface Segregation**: Clients depend only on methods they use

### SOLID Principles

All flext-core components follow SOLID principles:

```python
# Single Responsibility: Each class has one job
class UserService:
    def create_user(self, data: UserData) -> FlextResult[User, Exception]:
        # Only handles user creation logic
        pass

# Open/Closed: Open for extension, closed for modification
class BaseHandler(ABC):
    @abstractmethod
    def handle(self, command: BaseCommand) -> FlextResult:
        pass

class UserHandler(BaseHandler):
    def handle(self, command: CreateUserCommand) -> FlextResult:
        # Implementation specific to user creation
        pass
```

## Configuration Management

### FlextConfig

Centralized configuration management with environment variable support and validation.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

class AppConfig(FlextConfig):
    database_url: str
    debug_mode: bool = False
    log_level: str = "INFO"

# Load from environment
config = AppConfig.from_env()

# Access configuration
db_url = config.database_url
```

## Error Handling Strategy

### FlextExceptions Hierarchy

Structured exception hierarchy for consistent error handling across the ecosystem.

```python
from flext_core import FlextException, FlextUtilitiesDomainException, FlextInfrastructureException

class UserNotFoundException(FlextUtilitiesDomainException):
    def __init__(self, user_id: str):
        super().__init__(f"User not found: {user_id}")
        self.user_id = user_id

class DatabaseConnectionException(FlextInfrastructureException):
    def __init__(self, message: str):
        super().__init__(f"Database error: {message}")
```

## Utilities and Helpers

### u

Common utility functions and helpers used across the ecosystem.

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

# String operations
camel_case = u.to_camel_case("snake_case_string")
kebab_case = u.to_kebab_case("camelCaseString")

# File operations
exists = u.file_exists("/path/to/file")
content = u.read_file("/path/to/file")

# Data validation
is_valid_email = u.is_valid_email("user@example.com")
```

## Performance Features

### FlextMetrics

Built-in performance monitoring and metrics collection.

```python
from flext_core import FlextMetrics

# Decorator for automatic timing
@FlextMetrics.timer("user_creation_duration")
def create_user(self, user_data: dict) -> FlextResult:
    # Implementation
    pass

# Manual metrics
FlextMetrics.increment("users_created_total")
FlextMetrics.gauge("active_users", 150)
```

## Development Guidelines

### Testing with flext-core

```python
import pytest
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

class TestUserService:
    def test_create_user_success(self):
        # Arrange
        container = FlextContainer()
        service = container.resolve(IUserService)

        # Act
        result = service.create_user(valid_user_data())

        # Assert
        assert result.is_success
        user = result.unwrap()
        assert user.id is not None

    def test_create_user_validation_error(self):
        # Arrange
        container = FlextContainer()
        service = container.resolve(IUserService)

        # Act
        result = service.create_user(invalid_user_data())

        # Assert
        assert result.is_failure
        error = result.failure()
        assert isinstance(error, ValidationException)
```

## Migration from Previous Versions

### From v0.x to v1.0.0

Key changes in flext-core v1.0.0:

1. **Python 3.13+ Requirement**: Updated to support latest Python features
2. **Pydantic v2 Integration**: Full adoption of Pydantic v2 patterns
3. **Async Support**: Native async/await support throughout
4. **Type Safety**: Enhanced type annotations and validation
5. **Performance**: Significant performance improvements

### Migration Guide

```python
# Before (v0.x)
from flext.core import Container, Result

container = Container()
result = Result.success(data)

# After (v1.0.0)
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

container = FlextContainer()
result = FlextResult.success(data)
```

## Best Practices

### Dependency Injection Best Practices

1. **Register interfaces, not implementations**
2. **Use singleton scope for stateless services**
3. **Inject dependencies through constructors**
4. **Avoid service locator anti-pattern**

### Error Handling Best Practices

1. **Use FlextResult for all operations**
2. **Create specific exception types for different error categories**
3. **Log errors with appropriate context**
4. **Handle errors at the appropriate architectural layer**

### Logging Best Practices

1. **Use structured logging with extra parameters**
2. **Include correlation IDs for request tracing**
3. **Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)**
4. **Avoid logging sensitive information**

## Support and Documentation

- 📖 [Full API Reference](../api-reference/README.md#flext-core)
- 🐛 [Issue Tracker](https://github.com/flext/flext-core/issues)
- 💬 [Discussions](https://github.com/flext/flext-core/discussions)
- 📧 Support: <dev@flext.com>

---

_Part of the FLEXT ecosystem - Built for enterprise-grade reliability and scalability._
