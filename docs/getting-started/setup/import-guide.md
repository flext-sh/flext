# Import Guide - Getting Started

> **Function**: Module import and configuration patterns | **Audience**: Developers, integration engineers | **Status**: Stable

[![Imports](https://img.shields.io/badge/imports-validated-green.svg)](#core-imports-from-flext)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](./installation-guide.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-orange.svg)](../../architecture/index.md)

**Complete import guide for FLX 0.4.0 framework - validated against current source code implementation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Getting Started](../index.md) → **📂 Section**: [Setup](./index.md) → **📄 Current**: Import Guide

### **📍 Learning Path Position**

```
[Installation Guide](./installation-guide.md) → **[IMPORT GUIDE]** → [Quickstart](../basics/quickstart.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Setup Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Next Step**: [Quickstart Guide](../basics/quickstart.md)

---

## 📋 **Overview**

This guide provides the correct import paths for the FLX 0.4.0 framework based on the current modern codebase structure with hexagonal architecture patterns.

## Core Imports (from `flext`)

```python
# Core domain entities
from flext import (
    Entity,
    AggregateRoot,
    ValueObject,
    DomainEvent,
)

# Application services
from flext import (
    ApplicationService,
    CommandService,
    QueryService,
    Bootstrap,
)

# Logging
from flext import (
    StandardLoggingAdapter,
    DomainLogger,
    LoggerInterface,
    LogLevel,
    get_logger,
)

# API Client
from flext import ApiClient
```

## Modern Adapter Imports (Unified Architecture)

All adapters now use the unified architecture pattern with significant code reduction through `AdvancedAdapterMixin`.

### Inbound Adapters (Driving Side)

```python
# API/HTTP Interface Adapter
from flext.adapters.inbound.api import ApiAdapter

# CLI Interface Adapter
from flext.adapters.inbound.cli import CliAdapter
```

### Outbound Adapters (Driven Side)

```python
# Database operations (SQLite/PostgreSQL)
from flext.adapters.outbound.database import DatabaseAdapter

# Cache operations (Redis/Memory)
from flext.adapters.outbound.cache import CacheAdapter
from flext.adapters.outbound.memory_cache import MemoryCacheAdapter

# HTTP client operations
from flext.adapters.outbound.http import HttpClientAdapter

# Event publishing (Dramatiq integration)
from flext.adapters.outbound.events import EventPublisherAdapter

# Analytics and metrics
from flext.adapters.outbound.analytics import AnalyticsAdapter

# Structured logging
from flext.adapters.outbound.logging import StandardLoggingAdapter
```

## Application Layer

```python
# Application services
from flext.application import (
    ApplicationService,
    CommandHandler,
    CommandService,
    QueryHandler,
    QueryService,
    ServiceRegistry,
)

# Dependency injection
from flext.application import (
    DIContainer,
    ServiceContainer,
)

# Bootstrap
from flext.application import (
    Bootstrap,
    create_bootstrap,
    run_bootstrap,
)
```

## Core Domain Layer

```python
# Entities and value objects
from flext.core.entities import Entity, AggregateRoot
from flext.core.domain.value_objects import ValueObject

# Events
from flext.core.events import DomainEvent

# Exceptions
from flext.core.exceptions import (
    DomainError,
    ValidationError,
    BusinessRuleViolation,
    NotFoundError,
    ConflictError,
    AuthorizationError,
)

# Base classes
from flext.core.base import DomainObject

# Modern mixins
from flext.core.mixins import TimestampMixin, VersionedMixin
from flext.adapters.mixins.advanced import AdvancedAdapterMixin
```

## Infrastructure Services

```python
# Cache service
from flext.infra.cache.cache_service import CacheService

# Database engine
from flext.infra.database.engine import DatabaseEngine

# CLI service
from flext.infra.cli.cli_service import CliService

# HTTP client service
from flext.infra.http.client_service import HttpClientService

# Analytics service
from flext.infra.analytics.analytics_service import AnalyticsService

# Event service
from flext.infra.events.event_service import EventService
```

## Adapter Factory System

```python
# Centralized adapter creation
from flext.adapters.factory import AdapterFactory

# Create adapters dynamically
factory = AdapterFactory()
database_adapter = await factory.create_adapter("database", config)
```

## Modern Mixin System

```python
# Unified adapter mixins
from flext.adapters.mixins.error_handling import (
    UnifiedErrorHandlingMixin,
    AdapterErrorHandlingMixin
)

from flext.adapters.mixins.configuration import (
    UnifiedAdapterConfigurationMixin,
    ConfigurationValidationMixin
)

from flext.adapters.mixins.observability import (
    UnifiedObservabilityMixin,
    ComprehensiveMetricsMixin
)
```

## Usage Examples

### Modern Database Adapter Usage

```python
from flext.adapters.outbound.database import DatabaseAdapter

async def main():
    # Modern pattern with unified configuration
    db = DatabaseAdapter(
        connection_url="postgresql://localhost/app",
        enable_wal_mode=True,
        use_test_engine=True  # For testing
    )

    # Auto-connect and disconnect with context manager
    async with db:
        # Save aggregate
        user = UserEntity(username="john", email="john@example.com")
        await db.save(user)

        # Query with criteria
        users = await db.query(
            criteria=QueryCriteria(filters={"active": True})
        )
```

### Modern HTTP Client Usage

```python
from flext.adapters.outbound.http import HttpClientAdapter

async def main():
    # Modern pattern with comprehensive configuration
    http = HttpClientAdapter(
        base_url="https://api.example.com",
        bearer_token="your-token",
        connection_timeout=30,
        use_test_engine=False
    )

    async with http:
        # GET request with automatic observability
        response = await http.get("/users/123")

        # POST with data
        result = await http.post("/users", data={"name": "John"})

        # File operations
        await http.download("/files/report.pdf", Path("./report.pdf"))
```

### CLI Adapter Pattern

```python
from flext.adapters.inbound.cli import CliAdapter
from flext.application import CommandService

class MyCliAdapter(CliAdapter):
    def __init__(self, command_service: CommandService):
        super().__init__(
            app_name="myapp",
            app_version="1.0.0",
            colors_enabled=True
        )
        self.command_service = command_service

    async def setup_commands(self):
        @self.register_command("create-user")
        async def create_user(username: str, email: str):
            """Create a new user account."""
            result = await self.command_service.execute(
                CreateUserCommand(username=username, email=email)
            )
            return f"✅ User created: {result.id}"
```

### Application Service Pattern

```python
from flext import ApplicationService, Entity
from flext.adapters.outbound.database import DatabaseAdapter
from flext.adapters.outbound.cache import CacheAdapter

class UserEntity(Entity):
    username: str
    email: str

class UserService(ApplicationService):
    def __init__(self):
        self.db = DatabaseAdapter(
            connection_url="postgresql://localhost/app"
        )
        self.cache = CacheAdapter(
            redis_url="redis://localhost:6379/0"
        )

    async def create_user(self, username: str, email: str) -> UserEntity:
        """Create user with caching."""
        user = UserEntity(username=username, email=email)

        # Save to database
        await self.db.save(user)

        # Cache user data
        await self.cache.set(f"user:{user.id}", user.to_dict(), ttl=3600)

        return user

    async def get_user(self, user_id: str) -> Optional[UserEntity]:
        """Get user with cache-first strategy."""
        # Try cache first
        cached_data = await self.cache.get(f"user:{user_id}")
        if cached_data:
            return UserEntity.from_dict(cached_data)

        # Fallback to database
        user = await self.db.get(user_id)
        if user:
            # Cache for future requests
            await self.cache.set(f"user:{user_id}", user.to_dict(), ttl=3600)

        return user
```

## Testing with Test Engines

```python
from flext.adapters.outbound.database import DatabaseAdapter
from flext.adapters.outbound.http import HttpClientAdapter

async def test_user_service():
    # All adapters support test engines for isolation
    db = DatabaseAdapter(
        connection_url="postgresql://test_db",
        use_test_engine=True  # No actual database needed
    )

    http = HttpClientAdapter(
        base_url="https://api.example.com",
        use_test_engine=True  # Mock HTTP responses
    )

    async with db, http:
        # Test with mocked dependencies
        service = UserService(db=db, http=http)
        user = await service.create_user("test", "test@example.com")
        assert user.username == "test"
```

## Migration Notes from Legacy Versions

1. **No More "Modern" Suffixes**: All adapters now use the modern pattern by default
2. **Unified Configuration**: All adapters use consistent configuration hierarchies
3. **85-90% Code Reduction**: Through `AdvancedAdapterMixin` pattern
4. **Context Manager Support**: All adapters support `async with` for resource management
5. **Built-in Observability**: Automatic logging, metrics, and tracing
6. **Test Engine Integration**: Set `use_test_engine=True` for testing without external dependencies
7. **Error Handling**: Rich error context with correlation IDs automatically

## Framework Architecture

```
flext/src/flext/
├── __init__.py              # Top-level exports
├── adapters/                # Infrastructure adapters (hexagonal architecture)
│   ├── inbound/             # Driving side (CLI, API)
│   ├── outbound/            # Driven side (Database, HTTP, Cache, etc.)
│   ├── mixins/              # Cross-cutting concerns
│   ├── templates/           # Reference implementations
│   └── factory.py           # Centralized adapter creation
├── application/             # Application services layer
├── core/                    # Domain layer (entities, events, exceptions)
├── infra/                   # Infrastructure services
├── ports/                   # Port interfaces
└── testing/                 # Testing infrastructure
```

## Configuration Examples

### Database Configuration

```python
from flext.adapters.outbound.database import DatabaseAdapter

# SQLite configuration
db = DatabaseAdapter(
    connection_url="sqlite:///app.db",
    enable_wal_mode=True,
    connection_pool_size=5
)

# PostgreSQL configuration
db = DatabaseAdapter(
    connection_url="postgresql://user:pass@localhost:5432/db",
    connection_pool_size=20,
    query_timeout=30
)
```

### Cache Configuration

```python
from flext.adapters.outbound.cache import CacheAdapter

# Redis configuration
cache = CacheAdapter(
    redis_url="redis://localhost:6379/0",
    key_prefix="myapp:",
    default_ttl=3600,
    max_connections=10
)
```

### HTTP Client Configuration

```python
from flext.adapters.outbound.http import HttpClientAdapter

# Comprehensive HTTP configuration
http = HttpClientAdapter(
    base_url="https://api.example.com",
    bearer_token="your-token",
    connection_timeout=30,
    read_timeout=60,
    max_retries=3,
    retry_delay=1.0,
    ssl_verify=True
)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Installation Guide](./installation-guide.md) - Essential framework installation before importing modules
- [Python 3.13+ Environment](https://python.org) - Required runtime environment for FLX imports
- [Architecture Overview](../../architecture/index.md) - Understanding hexagonal architecture patterns for proper imports

### **Next Steps**

- [Quickstart Guide](../basics/quickstart.md) - Build your first FLX application using these imports
- [Framework Concepts](../concepts/flext-framework-overview.md) - Deep dive into architecture concepts behind imports
- [Basic Examples](../../examples/basic/index.md) - Working code examples demonstrating import patterns

### **Related Topics**

- [API Reference Hub](../../api-reference/index.md) - Complete API documentation for all importable modules
- [Development Standards](../../development/standards/index.md) - Code organization and import conventions
- [Testing Framework](../../development/testing/index.md) - Testing patterns using framework imports
- [Oracle Integration](../../guides/oracle/index.md) - Oracle-specific import patterns and adapters
- [Infrastructure Services](../../infrastructure/index.md) - Production infrastructure import patterns

---

## 🆘 **Troubleshooting**

### **Import Errors**

- **ModuleNotFoundError**: Ensure FLX Framework is properly installed via [Installation Guide](./installation-guide.md)
- **Version Conflicts**: Verify Python 3.13+ and framework version compatibility
- **Path Issues**: Use absolute imports as shown in examples above

### **Common Issues**

- **Legacy Import Paths**: Update from pre-0.4.0 import patterns using examples in this guide
- **Circular Imports**: Follow hexagonal architecture separation shown in [Architecture Guide](../../architecture/index.md)
- **Test Engine Setup**: Use `use_test_engine=True` for testing without external dependencies

---

**📂 Hub**: [Setup Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
