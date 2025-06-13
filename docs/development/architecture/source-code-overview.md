# FLX Source Code Overview

## Overview

This document provides a comprehensive overview of the FLX framework source code structure, implementing hexagonal architecture patterns for enterprise-grade Python applications.

## Related Documentation

- [Architecture Overview](../architecture/) - Core architectural principles
- [Development Guidelines](./development-guidelines.md) - Code development standards
- [API Reference](../api-reference/) - Complete API documentation
- [Testing Strategy](./testing-strategy.md) - Testing approaches and patterns

## Source Code Structure

The FLX framework follows a clean architecture approach with clear separation of concerns:

### Core Components

#### Domain Layer (`flx/core/`)

- **Pure domain logic** - Business rules and entities
- **Domain events** - Event-driven architecture patterns
- **Value objects** - Immutable domain representations
- **Domain services** - Complex business operations

#### Ports Layer (`flx/ports/`)

- **Inbound ports** - External system interfaces (CLI, API, events)
- **Outbound ports** - Infrastructure interfaces (database, HTTP, cache)
- **Protocol definitions** - Type-safe interface contracts
- **Port abstractions** - Clean interface boundaries

#### Adapters Layer (`flx/adapters/`)

- **Inbound adapters** - External system implementations
- **Outbound adapters** - Infrastructure implementations
- **Base adapters** - Common adapter functionality
- **Adapter patterns** - Reusable adapter components

#### Infrastructure Layer (`flx/infra/`)

- **Configuration management** - Environment and settings
- **Logging system** - Structured logging infrastructure
- **Database connections** - Data persistence layer
- **Messaging system** - Event and message handling
- **Security components** - Authentication and authorization
- **Observability tools** - Monitoring and metrics

#### Application Layer (`flx/application/`)

- **Application services** - Use case orchestration
- **Service containers** - Dependency injection
- **Application bootstrap** - Application lifecycle management
- **Service registry** - Service discovery and management

#### CLI Layer (`flx/cli/`)

- **Command-line interface** - CLI application framework
- **Command handlers** - CLI command implementations
- **Output formatters** - Result presentation
- **CLI configuration** - Command-line setup

#### Testing Framework (`flx/testing/`)

- **Test utilities** - Testing helper functions
- **Mock engines** - Test double implementations
- **Test adapters** - Testing-specific adapters
- **Test fixtures** - Reusable test components

### Architecture Principles

#### 1. Hexagonal Architecture

```
External Systems → Adapters → Ports → Domain Logic
Domain Logic → Ports → Adapters → External Systems
```

#### 2. Dependency Inversion

- **High-level modules** don't depend on low-level modules
- **Both depend on abstractions** (ports/interfaces)
- **Abstractions don't depend on details**
- **Details depend on abstractions**

#### 3. Single Responsibility

- **Each module** has one reason to change
- **Clear boundaries** between components
- **Focused interfaces** with minimal surface area
- **Cohesive functionality** within modules

#### 4. Open/Closed Principle

- **Open for extension** through plugins and adapters
- **Closed for modification** of core framework
- **Plugin architecture** for extensibility
- **Adapter patterns** for integration

## Key Design Patterns

### 1. Port and Adapter Pattern

```python
# Port definition (interface)
class DatabasePort(Protocol):
    async def save(self, entity: Entity) -> None: ...
    async def find_by_id(self, entity_id: str) -> Entity | None: ...

# Adapter implementation
class PostgreSQLAdapter(DatabasePort):
    async def save(self, entity: Entity) -> None:
        # PostgreSQL-specific implementation
        pass
    
    async def find_by_id(self, entity_id: str) -> Entity | None:
        # PostgreSQL-specific implementation
        pass
```

### 2. Dependency Injection

```python
# Service container
container = ServiceContainer()
container.bind(DatabasePort, PostgreSQLAdapter)
container.bind(HttpPort, HttpClientAdapter)

# Service resolution
service = container.get(UserService)  # Auto-wired dependencies
```

### 3. Plugin Architecture

```python
# Plugin definition
@plugin("user-management")
class UserManagementPlugin(Plugin):
    async def initialize(self, container: ServiceContainer) -> None:
        container.bind(UserService, EnhancedUserService)
    
    async def get_commands(self) -> List[Command]:
        return [CreateUserCommand, UpdateUserCommand]
```

### 4. Event-Driven Architecture

```python
# Domain event
class UserCreatedEvent(DomainEvent):
    user_id: str
    username: str
    email: str

# Event handler
class EmailNotificationHandler(EventHandler[UserCreatedEvent]):
    async def handle(self, event: UserCreatedEvent) -> None:
        await self.email_service.send_welcome_email(event.email)
```

## Package Organization

### Directory Structure

```
flx/src/flx/
├── core/                   # Domain layer
│   ├── entities.py         # Domain entities
│   ├── value_objects.py    # Value objects
│   ├── events.py           # Domain events
│   ├── services.py         # Domain services
│   └── exceptions.py       # Domain exceptions
├── ports/                  # Interface layer
│   ├── inbound/            # External → Domain
│   │   ├── api.py          # HTTP API ports
│   │   ├── cli.py          # CLI ports
│   │   └── events.py       # Event ports
│   └── outbound/           # Domain → External
│       ├── database.py     # Database ports
│       ├── http.py         # HTTP client ports
│       └── cache.py        # Cache ports
├── adapters/               # Implementation layer
│   ├── inbound/            # External system adapters
│   │   ├── api.py          # API adapters
│   │   └── cli.py          # CLI adapters
│   └── outbound/           # Infrastructure adapters
│       ├── database.py     # Database adapters
│       ├── http.py         # HTTP adapters
│       └── cache.py        # Cache adapters
├── infra/                  # Infrastructure layer
│   ├── config/             # Configuration management
│   ├── logging/            # Logging infrastructure
│   ├── database/           # Database infrastructure
│   ├── messaging/          # Messaging infrastructure
│   └── security/           # Security infrastructure
├── application/            # Application layer
│   ├── services.py         # Application services
│   ├── container.py        # Service container
│   └── bootstrap.py        # Application bootstrap
├── cli/                    # CLI layer
│   ├── main.py             # CLI entry point
│   ├── commands.py         # CLI commands
│   └── formatters.py       # Output formatters
└── testing/                # Testing framework
    ├── engines/            # Test engines
    ├── adapters/           # Test adapters
    └── fixtures/           # Test fixtures
```

### Import Organization

```python
# Core imports (domain layer)
from flx.core.entities import User, Order, Product
from flx.core.domain.value_objects import Email, Money, SKU
from flx.core.events import UserCreatedEvent, OrderProcessedEvent

# Port imports (interface layer)
from flx.ports.inbound.api import ApiPort
from flx.ports.outbound.database import DatabasePort

# Adapter imports (implementation layer)
from flx.adapters.inbound.api import FastApiAdapter
from flx.adapters.outbound.database import PostgreSQLAdapter

# Infrastructure imports
from flx.infra.config import FlxConfig
from flx.infra.logging import FlxLogger

# Application imports
from flx.application.services import UserService
from flx.application.container import ServiceContainer
```

## Code Quality Standards

### 1. Type Safety

```python
# Full type annotations
from typing import List, Optional, Dict, Any

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository
    
    async def create_user(self, username: str, email: str) -> User:
        # Implementation with proper typing
        pass
```

### 2. Error Handling

```python
# Comprehensive error handling
class UserService:
    async def create_user(self, username: str, email: str) -> User:
        try:
            # Validate input
            if not username or not email:
                raise ValidationError("Username and email are required")
            
            # Business logic
            user = User(username=username, email=Email(email))
            await self.repository.save(user)
            
            return user
            
        except ValidationError:
            # Re-raise validation errors
            raise
        except RepositoryError as e:
            # Handle repository errors
            logger.error("Failed to save user: %s", str(e))
            raise UserCreationError(f"User creation failed: {str(e)}") from e
        except Exception as e:
            # Handle unexpected errors
            logger.exception("Unexpected error in user creation")
            raise UserCreationError("Unexpected error occurred") from e
```

### 3. Logging Integration

```python
# Structured logging throughout
from flx.infra.logging import FlxLogger

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository
        self.logger = FlxLogger("user.service")
    
    async def create_user(self, username: str, email: str) -> User:
        self.logger.info("Creating user - Username: %s", username)
        
        try:
            user = User(username=username, email=Email(email))
            await self.repository.save(user)
            
            self.logger.info("User created successfully - ID: %s", user.id)
            return user
            
        except Exception as e:
            self.logger.error("User creation failed - Error: %s", str(e))
            raise
```

### 4. Testing Integration

```python
# Comprehensive testing support
import pytest
from flx.testing.fixtures import user_repository_mock, event_publisher_mock

class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user_success(
        self, 
        user_repository_mock: UserRepository,
        event_publisher_mock: EventPublisher
    ):
        # Arrange
        service = UserService(
            repository=user_repository_mock,
            event_publisher=event_publisher_mock
        )
        
        # Act
        user = await service.create_user("john", "john@example.com")
        
        # Assert
        assert user.username == "john"
        assert user.email.value == "john@example.com"
        user_repository_mock.save.assert_called_once_with(user)
```

## Development Workflow

### 1. Adding New Features

1. **Define domain requirements** in core layer
2. **Create port interfaces** for external interactions
3. **Implement adapters** for specific technologies
4. **Add infrastructure support** as needed
5. **Create application services** for use case orchestration
6. **Add CLI commands** for user interaction
7. **Write comprehensive tests** for all layers

### 2. Extension Points

- **Plugin system** for adding new functionality
- **Adapter interfaces** for new integrations
- **Event system** for decoupled communication
- **Service container** for dependency management

### 3. Configuration Management

```python
# Environment-based configuration
from flx.infra.config import FlxConfig

config = FlxConfig()
database_url = config.get_required("DATABASE_URL")
api_key = config.get_required("API_KEY")
debug_mode = config.get_bool("DEBUG_MODE", False)
```

## Performance Considerations

### 1. Async-First Design

- **All I/O operations** use async/await
- **Non-blocking adapters** for external systems
- **Concurrent processing** where appropriate
- **Resource pooling** for database connections

### 2. Memory Management

- **Lazy loading** of heavy components
- **Connection pooling** for external resources
- **Event streaming** for large datasets
- **Garbage collection** optimization

### 3. Caching Strategies

- **Result caching** at service layer
- **Query caching** for expensive operations
- **Configuration caching** for static data
- **Connection caching** for external systems

## See Also

- [Development Environment Setup](./environment-setup.md) - Development environment configuration
- [Coding Standards](./coding-standards.md) - Code style and quality guidelines
- [Testing Guidelines](./testing-guidelines.md) - Testing strategies and patterns
- [Performance Optimization](../optimization/performance-optimization.md) - Performance tuning guide

---

**Last Updated**: January 2025  
**Status**: Production Ready  
**Architecture**: Hexagonal Architecture  
**Language**: Python 3.13+
