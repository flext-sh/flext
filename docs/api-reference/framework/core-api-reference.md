# 📚 Core API Reference

> **Document Type**: API Reference | **Audience**: Developers, API implementers | **Scope**: Core framework API documentation

[![API](https://img.shields.io/badge/api-documented-green.svg)](../index.md)
[![Core](https://img.shields.io/badge/component-core-blue.svg)](../../architecture/index.md)
[![Validated](https://img.shields.io/badge/source-validated-orange.svg)](../../reference/specifications/flext-framework-technical-specification.md)

**Complete API documentation for FLEXT Core framework components, validated against actual codebase implementation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [API Reference](../index.md) → **📂 Framework**: [Index](./index.md) → **📂 Current**: Core API Reference

---

## 📋 **Overview**

The FLEXT Core API provides foundational components for building enterprise-grade domain-driven applications with hexagonal architecture. This reference documents **current, validated APIs** based on actual codebase implementation.

### **✅ Implementation Status**

All APIs documented here are **actively maintained** and verified against the actual codebase as of June 2025.

## Core Domain Layer

### Entities (`flext.core.entities`)

#### Entity

**Location**: `flext.core.entities.Entity`

Base class for domain entities with identity and lifecycle management.

```python
from flext.core.entities import Entity

class User(Entity):
    username: str
    email: str

    def change_email(self, new_email: str) -> None:
        self.email = new_email
        self.touch()  # Update timestamp
```

**Key Features:**

- Identity-based equality (entities are equal if IDs match)
- Automatic timestamp tracking (`created_at`, `updated_at`)
- Version control for optimistic locking
- Lifecycle management methods

**Methods:**

- `touch()` → None: Update the `updated_at` timestamp
- `increment_version()` → None: Increment entity version
- `get_identity()` → str: Get entity unique identifier

#### AggregateRoot

**Location**: `flext.core.entities.AggregateRoot`

Root entity for aggregates with domain event support.

```python
from flext.core.entities import AggregateRoot

class Order(AggregateRoot):
    customer_id: str
    status: str = "pending"
    total: float = 0.0

    def confirm(self) -> None:
        if self.status != "pending":
            raise ValueError("Order already confirmed")

        self.status = "confirmed"
        self.increment_version()
        self.add_event(DomainEvent(
            event_type="OrderConfirmed",
            aggregate_id=self.id,
            data={"order_id": self.id, "total": self.total}
        ))
```

**Key Features:**

- Domain event emission and collection
- Aggregate consistency boundary enforcement
- Transaction control across related entities
- Event-driven communication

**Methods:**

- `add_event(event: DomainEvent)` → None: Add a domain event to be dispatched after persistence
- `collect_events()` → List[DomainEvent]: Collect and clear pending events for publishing
- `events` → List[DomainEvent]: Property to get current pending events without clearing them

### Value Objects (`flext.core.domain.value_objects`)

#### ValueObject

**Location**: `flext.core.domain.value_objects.ValueObject`

Base class for immutable value objects.

```python
from flext.core.domain.value_objects import ValueObject

class Money(ValueObject):
    amount: float
    currency: str = "USD"

    def multiply(self, factor: float) -> "Money":
        return Money(amount=self.amount * factor, currency=self.currency)

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)
```

**Key Features:**

- Immutable by design (Pydantic frozen=True)
- Value-based equality
- Self-validating with business rules
- JSON serializable

#### Concrete Value Objects

**Email**

```python
from flext.core.domain.value_objects import Email

email = Email(value="user@example.com")
print(email.domain)  # "example.com"
print(email.local_part)  # "user"
```

**Address**

```python
from flext.core.domain.value_objects import Address

address = Address(
    street="123 Main St",
    city="Springfield",
    postal_code="12345",
    country="USA"
)
print(address.formatted())  # "123 Main St, Springfield, 12345, USA"
```

**DateRange**

```python
from flext.core.domain.value_objects import DateRange
from datetime import date

range1 = DateRange(start=date(2024, 1, 1), end=date(2024, 1, 31))
range2 = DateRange(start=date(2024, 1, 15), end=date(2024, 2, 15))

print(range1.overlaps(range2))  # True
print(range1.duration_days())   # 30
```

### Domain Events (`flext.core.events`)

#### DomainEvent

**Location**: `flext.core.events.DomainEvent`

Represents something important that happened in the domain.

```python
from flext.core.events import DomainEvent
from datetime import datetime

event = DomainEvent(
    event_type="UserRegistered",
    aggregate_id="user-123",
    aggregate_type="User",
    data={"username": "john_doe", "email": "john@example.com"},
    occurred_at=datetime.utcnow(),
    version=1
)
```

**Properties:**

- `event_type` (str): Type of the domain event
- `aggregate_id` (str): ID of the aggregate that emitted the event
- `aggregate_type` (str): Type of the aggregate
- `data` (dict): Event payload data
- `occurred_at` (datetime): When the event occurred
- `version` (int): Event version for ordering

---

## Application Layer

### Bootstrap (`flext.application.Bootstrap`)

**Location**: `flext.application.Bootstrap`

Application bootstrap and dependency injection container.

```python
from flext.application import Bootstrap, create_bootstrap

# Create and configure bootstrap
bootstrap = create_bootstrap()

# Register services
bootstrap.register_service("user_repo", UserRepository())
bootstrap.register_service("email_service", EmailService())

# Start application
await bootstrap.start()

# Get services
user_repo = bootstrap.get_service("user_repo")
```

**Methods:**

- `register_service(name: str, service: Any)` → None: Register a service
- `get_service(name: str)` → Any: Retrieve a registered service
- `start()` → None: Start all registered services
- `stop()` → None: Stop all services and cleanup

### Application Services

#### ApplicationService

**Location**: `flext.application.ApplicationService`

Base class for application services (use cases).

```python
from flext.application import ApplicationService

class CreateUserService(ApplicationService):
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service

    async def execute(self, command: CreateUserCommand) -> UserCreated:
        # Validate business rules
        if await self.user_repo.exists_by_email(command.email):
            raise UserAlreadyExistsError(command.email)

        # Create domain entity
        user = User(
            username=command.username,
            email=command.email
        )

        # Persist
        await self.user_repo.save(user)

        # Send welcome email
        await self.email_service.send_welcome(user.email)

        # Return result
        return UserCreated(user_id=user.id, username=user.username)
```

#### CommandService & QueryService

**Location**: `flext.application.CommandService`, `flext.application.QueryService`

Specialized application services for CQRS pattern.

```python
from flext.application import CommandService, QueryService

class UserCommandService(CommandService):
    async def create_user(self, command: CreateUserCommand) -> None:
        # Handle command (write operation)
        pass

class UserQueryService(QueryService):
    async def get_user_by_id(self, user_id: str) -> UserView:
        # Handle query (read operation)
        pass
```

---

## Adapter Layer

### API Client (`flext.adapters.api_client`)

**Location**: `flext.adapters.api_client.ApiClient`

HTTP client adapter for external API integration.

```python
from flext.adapters.api_client import ApiClient

client = ApiClient(base_url="https://api.example.com")

# GET request
response = await client.get("/users/123")
user_data = response.json()

# POST request with data
response = await client.post("/users", json={
    "username": "john_doe",
    "email": "john@example.com"
})
```

**Methods:**

- `get(path: str, **kwargs)` → Response: HTTP GET request
- `post(path: str, **kwargs)` → Response: HTTP POST request
- `put(path: str, **kwargs)` → Response: HTTP PUT request
- `delete(path: str, **kwargs)` → Response: HTTP DELETE request

### Logging Adapter (`flext.adapters.outbound.logging`)

**Location**: `flext.adapters.outbound.logging.StandardLoggingAdapter`

Structured logging adapter implementing the domain logging interface.

```python
from flext.adapters.outbound.logging import StandardLoggingAdapter

logger = StandardLoggingAdapter(name="my_service")

logger.info("User created", extra={
    "user_id": "123",
    "username": "john_doe",
    "correlation_id": "req-456"
})

logger.error("Database connection failed", extra={
    "database_url": "postgresql://...",
    "error_code": "CONNECTION_TIMEOUT"
})
```

---

## Testing Framework

### Declarative Testing (`flext.testing.declarative`)

#### TestEngine

**Location**: `flext.testing.declarative.DeclarativeTestEngine`

Modern testing engine for hexagonal architecture.

```python
from flext.testing.declarative import create_test_engine, TestMetrics

# Create test engine
engine = create_test_engine()

# Configure test data
await engine.setup_test_data({
    "users": [
        {"username": "test_user", "email": "test@example.com"}
    ]
})

# Run tests
results = await engine.run_test_suite()

# Validate results
assert results.passed > 0
assert results.failed == 0
```

#### TestableAdapter

**Location**: `flext.testing.declarative.TestableAdapter`

Base class for creating testable adapters.

```python
from flext.testing.declarative import TestableAdapter

class MockEmailAdapter(TestableAdapter):
    def __init__(self):
        super().__init__()
        self.sent_emails = []

    async def send_email(self, to: str, subject: str, body: str) -> None:
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body
        })
        self.record_operation("send_email", {"to": to})
```

---

## Core Interfaces

### Logging Interface (`flext.core.logging_interface`)

#### LoggerInterface

**Location**: `flext.core.logging_interface.LoggerInterface`

Domain interface for logging (hexagonal architecture port).

```python
from flext.core.logging_interface import LoggerInterface, LogLevel

class MyDomainService:
    def __init__(self, logger: LoggerInterface):
        self.logger = logger

    def process_order(self, order_id: str) -> None:
        self.logger.log(LogLevel.INFO, "Processing order", {
            "order_id": order_id,
            "operation": "process_order"
        })
```

#### LogLevel

**Location**: `flext.core.logging_interface.LogLevel`

Enumeration for log levels.

```python
from flext.core.logging_interface import LogLevel

# Available log levels
LogLevel.DEBUG
LogLevel.INFO
LogLevel.WARNING
LogLevel.ERROR
LogLevel.CRITICAL
```

---

## Utility Functions

### Factory Functions

#### create_bootstrap

**Location**: `flext.application.create_bootstrap`

Factory function for creating configured bootstrap instances.

```python
from flext.application import create_bootstrap

bootstrap = create_bootstrap(
    config_path="./config.yaml",
    enable_metrics=True,
    enable_tracing=True
)
```

#### get_logger

**Location**: `flext.get_logger`

Factory function for creating logger instances.

```python
from flext import get_logger

logger = get_logger(__name__)
logger.info("Service started")
```

---

## Migration Notes

### Obsolete APIs (DO NOT USE)

The following APIs from old documentation are **obsolete** and should not be used:

❌ `flext.Entities.BaseEntity` - Use `flext.core.entities.Entity`
❌ `flext.ValueObjects.ContactInfo` - Use `flext.core.domain.value_objects.Email` + custom value objects
❌ `flext.Protocols.*` - Use proper Python protocols or interfaces
❌ `flext.Mixins.*` - Use composition over inheritance
❌ `UnifiedAdapterManager` - Use `flext.application.Bootstrap`

### Current Best Practices

✅ Use `flext.core.entities.Entity` and `AggregateRoot` for domain entities
✅ Use `flext.core.domain.value_objects.ValueObject` for immutable domain concepts
✅ Use `flext.application.ApplicationService` for use cases
✅ Use `flext.adapters.*` for infrastructure integration
✅ Use `flext.testing.declarative.*` for testing

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Overview](../architecture/index.md) - Understanding hexagonal architecture
- [Core Domain Layer](../architecture/core-domain-layer.md) - Domain-driven design fundamentals

### **Next Steps**

- [Adapters API Reference](./flext-adapters-comprehensive-reference.md) - Infrastructure adapter APIs
- [Complete API Documentation](./flext-complete-api.md) - Full framework API coverage

### **Related Topics**

- [Development Standards](../development/standards/index.md) - API development standards
- [Testing Framework](../development/testing/index.md) - API testing strategies

---

## 🆘 **Troubleshooting**

### **Common API Issues**

- **Import Errors**: Ensure proper module path imports from `flext.core.*`
- **Type Validation**: Use Pydantic models for complex data validation
- **Entity Identity**: Always use proper entity ID management patterns
- **Value Object Immutability**: Ensure value objects remain immutable after creation

### **API Best Practices**

- Use `flext.core.entities.Entity` and `AggregateRoot` for domain entities
- Use `flext.core.domain.value_objects.ValueObject` for immutable domain concepts
- Use `flext.application.ApplicationService` for use cases
- Use `flext.adapters.*` for infrastructure integration
- Use `flext.testing.declarative.*` for comprehensive testing

---

**📂 Hub**: [API Reference Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLEXT 0.4.0+

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Framework Hub](../index.md) - API reference navigation and overview for accessing core framework documentation
- [Getting Started](../../getting-started/index.md) - Framework installation and basic concepts required for API usage
- [Architecture Hub](../../architecture/index.md) - Hexagonal architecture patterns underlying these core APIs

### **➡️ Next Steps**

- [Adapters API](../adapters/index.md) - Adapter development APIs building on core framework components
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating core API usage in practice
- [Development Hub](../../development/index.md) - Development practices for implementing with core APIs

### **🔗 Related Sections**

- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure service APIs that extend core framework functionality
- [Oracle Integration Guide](../../guides/oracle/index.md) - Oracle integration patterns utilizing these core APIs
- [Testing Guide](../../development/testing/index.md) - Testing strategies for applications using core framework APIs
- [Specifications](../../reference/specifications/flext-framework-technical-specification.md) - Technical specifications for core API components

---

**📂 API Reference**: [Framework Hub](../index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
