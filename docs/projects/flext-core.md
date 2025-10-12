# flext-core

**Core Framework** - The foundation of the FLEXT ecosystem providing essential patterns, abstractions, and utilities.

## Overview

flext-core is the foundational framework that provides the core patterns and abstractions used throughout the FLEXT ecosystem. It implements enterprise-grade patterns like Dependency Injection, CQRS, Railway-Oriented Programming, and Domain Events.

## Installation

```bash
pip install flext-core
```

## Key Components

### FlextCore.Container (Dependency Injection)

Central dependency injection container for managing component lifecycles and dependencies.

```python
from flext_core import FlextCore

# Register services
container = FlextCore.Container()
container.register(IService, ServiceImplementation())
container.register(IRepository, RepositoryImplementation())

# Resolve dependencies
service = container.resolve(IService)
```

### FlextCore.Dispatcher (CQRS Pattern)

Command Query Responsibility Segregation implementation for handling commands and queries.

```python
from flext_core import FlextCore

# Register handlers
dispatcher = FlextCore.Dispatcher()
dispatcher.register_handler(CreateUserCommand, CreateUserHandler)
dispatcher.register_handler(GetUserQuery, GetUserHandler)

# Dispatch operations
result = dispatcher.dispatch(CreateUserCommand(user_data))
user = dispatcher.dispatch(GetUserQuery(user_id))
```

### FlextCore.Result (Railway-Oriented Programming)

Functional error handling with happy path and sad path composition.

```python
from flext_core import FlextCore

def divide(a: float, b: float) -> FlextCore.Result[float, Exception]:
    if b == 0:
        return FlextCore.Result.failure(ValueError("Cannot divide by zero"))
    return FlextCore.Result.success(a / b)

# Compose operations
result = (FlextCore.Result.success(10.0)
          .bind(lambda x: divide(x, 2.0))
          .bind(lambda x: divide(x, 3.0)))

if result.is_success:
    print(f"Result: {result.unwrap()}")
else:
    print(f"Error: {result.failure()}")
```

### FlextCore.Bus (Domain Events)

Event-driven architecture support with domain event publishing and subscription.

```python
from flext_core import FlextCore

# Subscribe to events
bus = FlextCore.Bus()
bus.subscribe(UserCreatedEvent, UserCreatedHandler)
bus.subscribe(UserDeletedEvent, UserDeletedHandler)

# Publish events
bus.emit(UserCreatedEvent(user_id="123", email="user@example.com"))
```

### FlextCore.Logger (Structured Logging)

Enterprise-grade logging with structured data support and multiple output formats.

```python
from flext_core import FlextCore

logger = FlextCore.Logger.get_logger(__name__)

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
    def create_user(self, data: UserData) -> FlextCore.Result[User, Exception]:
        # Only handles user creation logic
        pass

# Open/Closed: Open for extension, closed for modification
class BaseHandler(ABC):
    @abstractmethod
    def handle(self, command: BaseCommand) -> FlextCore.Result:
        pass

class UserHandler(BaseHandler):
    def handle(self, command: CreateUserCommand) -> FlextCore.Result:
        # Implementation specific to user creation
        pass
```

## Configuration Management

### FlextCore.Config

Centralized configuration management with environment variable support and validation.

```python
from flext_core import FlextCore

class AppConfig(FlextCore.Config):
    database_url: str
    debug_mode: bool = False
    log_level: str = "INFO"

# Load from environment
config = AppConfig.from_env()

# Access configuration
db_url = config.database_url
```

## Error Handling Strategy

### FlextCore.Exceptions Hierarchy

Structured exception hierarchy for consistent error handling across the ecosystem.

```python
from flext_core import FlextException, FlextDomainException, FlextInfrastructureException

class UserNotFoundException(FlextDomainException):
    def __init__(self, user_id: str):
        super().__init__(f"User not found: {user_id}")
        self.user_id = user_id

class DatabaseConnectionException(FlextInfrastructureException):
    def __init__(self, message: str):
        super().__init__(f"Database error: {message}")
```

## Utilities and Helpers

### FlextCore.Utilities

Common utility functions and helpers used across the ecosystem.

```python
from flext_core import FlextCore

# String operations
camel_case = FlextCore.Utilities.to_camel_case("snake_case_string")
kebab_case = FlextCore.Utilities.to_kebab_case("camelCaseString")

# File operations
exists = FlextCore.Utilities.file_exists("/path/to/file")
content = FlextCore.Utilities.read_file("/path/to/file")

# Data validation
is_valid_email = FlextCore.Utilities.is_valid_email("user@example.com")
```

## Performance Features

### FlextMetrics

Built-in performance monitoring and metrics collection.

```python
from flext_core import FlextMetrics

# Decorator for automatic timing
@FlextMetrics.timer("user_creation_duration")
def create_user(self, user_data: dict) -> FlextCore.Result:
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
from flext_core import FlextCore

class TestUserService:
    def test_create_user_success(self):
        # Arrange
        container = FlextCore.Container()
        service = container.resolve(IUserService)

        # Act
        result = service.create_user(valid_user_data())

        # Assert
        assert result.is_success
        user = result.unwrap()
        assert user.id is not None

    def test_create_user_validation_error(self):
        # Arrange
        container = FlextCore.Container()
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
from flext_core import FlextCore

container = FlextCore.Container()
result = FlextCore.Result.success(data)
```

## Best Practices

### Dependency Injection Best Practices

1. **Register interfaces, not implementations**
2. **Use singleton scope for stateless services**
3. **Inject dependencies through constructors**
4. **Avoid service locator anti-pattern**

### Error Handling Best Practices

1. **Use FlextCore.Result for all operations**
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
