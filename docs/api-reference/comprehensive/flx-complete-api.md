# 📚 FLEXT Framework - Complete API Reference

> **Function**: Complete FLEXT Framework API documentation | **Audience**: All developers, architects | **Status**: Production-Ready

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](http://mypy-lang.org/)
[![Source](https://img.shields.io/badge/source-validated-green.svg)](../../index.md)

**Complete API reference for FLEXT Framework 0.4.0+ generated from actual source code with type safety and production validation - verified against `/flext/src/flext/` implementation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [API Reference](../index.md) → **📂 Section**: [Comprehensive](./index.md) → **📄 Current**: Complete API Reference

### **📍 Learning Path Position**

```
[API Reference Hub](../index.md) → [Comprehensive](./index.md) → **[Complete API]** → [Implementation Examples](../../examples/index.md)
```

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue)](http://mypy-lang.org/)

## Quick Import Reference

```python
from flext import (
    # Core Domain Layer
    AggregateRoot, Entity, ValueObject,
    DomainEvent, DomainLogger, LogLevel,

    # Application Services
    ApplicationService, Bootstrap,
    CommandService, QueryService,
    create_bootstrap, run_bootstrap,

    # Testing Framework
    DeclarativeTestEngine, TestableAdapter,
    TestMetrics, TestResult,
    create_test_engine, run_full_test_suite,

    # Logging
    StandardLoggingAdapter, get_logger
)
```

---

## Core Domain Layer

### Entity & Aggregate Classes

#### `Entity(DomainObject, Identifiable, Timestamped)`

**Location**: `/flext/src/flext/core/entities.py:133`

Base class for domain entities with identity and lifecycle management.

```python
class Customer(Entity):
    name: str
    email: str
    status: str = "active"

    def deactivate(self) -> Self:
        """Deactivate customer using immutable pattern."""
        return self.model_copy(update={
            "status": "inactive",
            "updated_at": datetime.now(UTC)
        })
```

**Key Methods:**

- `touch() -> Self`: Update timestamp (immutable)
- `__eq__(other) -> bool`: Identity-based equality
- `__hash__() -> int`: Identity-based hashing

#### `AggregateRoot(Entity, Versionable)`

**Location**: `/flext/src/flext/core/entities.py:247`

Base class for aggregate roots implementing DDD consistency boundaries.

```python
class Order(AggregateRoot):
    customer_id: str
    status: str = "pending"
    items: list[OrderItem] = []

    def add_item(self, product_id: str, quantity: int, price: Money) -> None:
        # Business validation
        if self.status != "pending":
            raise ValueError("Cannot modify confirmed order")

        # Add item and emit event
        item = OrderItem(product_id=product_id, quantity=quantity, unit_price=price)
        self.items.append(item)
        self.increment_version()

        self.add_event(ItemAddedToOrderEvent(
            order_id=self.id,
            product_id=product_id,
            quantity=quantity
        ))
```

**Event Management:**

- `add_event(event: DomainEvent) -> None`: Add domain event
- `collect_events() -> list[DomainEvent]`: Collect and clear events
- `events -> list[DomainEvent]`: Read-only access to pending events

**Version Control:**

- `increment_version() -> Self`: Increment for optimistic locking
- `version: int`: Current version number

### Domain Events

#### `DomainEvent(DomainObject)`

**Location**: `/flext/src/flext/core/events.py:85`

Base class for all domain events with automatic metadata.

```python
class UserRegistered(DomainEvent):
    user_id: str
    email: str
    full_name: str

event = UserRegistered(
    aggregate_id=UUID("user-aggregate-id"),
    user_id="user_12345",
    email="john.doe@example.com",
    full_name="John Doe"
)
```

**Automatic Fields:**

- `event_id: UUID`: Unique event identifier
- `event_type: str`: Auto-generated from class name
- `occurred_at: datetime`: UTC timestamp
- `correlation_id: UUID | None`: Request tracing
- `causation_id: UUID | None`: Event causation

**Correlation Methods:**

- `with_correlation(correlation_id: UUID) -> DomainEvent`
- `with_causation(causation_id: UUID) -> DomainEvent`

#### `FlextDomainEvent(DomainEvent)`

**Location**: `/flext/src/flext/core/events.py:338`

FLEXT-specific events with multi-tenancy and routing.

```python
class TenantUserRegistered(FlextDomainEvent):
    user_id: str
    email: str

event = TenantUserRegistered(
    tenant_id="company_abc",
    user_id="new_user_123",
    email="user@company-abc.com"
)

# Automatic routing key: "flext.company_abc.tenantuserregistered"
```

**Additional Fields:**

- `tenant_id: str | None`: Multi-tenant isolation
- `user_id: str | None`: User attribution
- `source: str = "flext"`: Event source
- `version: str = "1.0"`: Schema version

**Routing:**

- `routing_key -> str`: Intelligent message routing key

---

## Application Layer

### Application Services

#### `ApplicationService`

**Location**: `/flext/src/flext/application/services.py`

Base application service for use case orchestration.

#### `Bootstrap`

**Location**: `/flext/src/flext/application/bootstrap.py`

Application bootstrap and lifecycle management.

```python
# Create and run bootstrap
bootstrap = create_bootstrap(config={
    "database_url": "postgresql://localhost/mydb",
    "redis_url": "redis://localhost:6379"
})

await run_bootstrap(bootstrap)
```

**Functions:**

- `create_bootstrap(config: dict) -> Bootstrap`
- `run_bootstrap(bootstrap: Bootstrap) -> None`

### Command and Query Services

#### `CommandService`

**Location**: `/flext/src/flext/application/services.py`

CQRS command handling service.

#### `QueryService`

**Location**: `/flext/src/flext/application/services.py`

CQRS query handling service.

---

## Port Interfaces

### Base Port Protocols

#### `BaseConnectionPort`

**Location**: `/flext/src/flext/ports/base.py:13`

Protocol for ports requiring connection management.

```python
class MyPort(BaseConnectionPort):
    async def connect(self) -> None:
        """Establish connection."""

    async def disconnect(self) -> None:
        """Close connection."""

    async def health_check(self) -> dict[str, Any]:
        """Health check."""
```

#### `BaseCrudPort`

**Location**: `/flext/src/flext/ports/base.py:95`

Protocol for CRUD operations.

```python
async def get(self, key: str) -> Any | None
async def set(self, key: str, value: Any, **options: Any) -> bool
async def delete(self, key: str) -> bool
async def exists(self, key: str) -> bool
```

### Composite Ports

#### `StandardOutboundPort`

**Location**: `/flext/src/flext/ports/base.py:344`

Combines: `BaseConnectionPort + BaseAsyncContextPort + BaseCrudPort`

#### `AdvancedOutboundPort`

**Location**: `/flext/src/flext/ports/base.py:352`

Adds: `BaseBatchOperationsPort + BaseQueryPort`

---

## Infrastructure Layer

### Core Infrastructure Services

#### Cache Service

**Location**: `/flext/src/flext/infra/cache/`

Redis-based caching with test engine support.

```python
cache_service = CacheService(
    redis_url="redis://localhost:6379",
    use_test_engine=False  # True for testing
)

await cache_service.connect()
result = await cache_service.get("key")
await cache_service.set("key", "value", ttl=3600)
await cache_service.disconnect()
```

#### Database Service

**Location**: `/flext/src/flext/infra/database/`

SQLAlchemy-based database integration.

```python
db_service = DatabaseService(
    database_url="postgresql://localhost/db",
    use_test_engine=False
)

await db_service.connect()
session = await db_service.get_session()
await db_service.disconnect()
```

#### HTTP Service

**Location**: `/flext/src/flext/infra/http/`

HTTP client service using httpx.

```python
http_service = HttpService(
    base_url="https://api.example.com",
    use_test_engine=False
)

await http_service.connect()
response = await http_service.get("/users/123")
await http_service.disconnect()
```

#### CLI Service

**Location**: `/flext/src/flext/infra/cli/`

CLI infrastructure using Cyclopts framework.

```python
cli_service = CliService(
    app_name="myapp",
    use_test_engine=False
)

await cli_service.connect()
result = await cli_service.execute_command("process", ["--input", "data.json"])
```

### Observability Services

#### Observability Service

**Location**: `/flext/src/flext/infra/observability/`

Comprehensive monitoring with Prometheus metrics.

```python
obs_service = ObservabilityService(
    prometheus_endpoint="http://localhost:9090",
    use_test_engine=False
)

await obs_service.collect_metrics()
health = await obs_service.health_check()
```

#### Analytics Service

Structured event analytics and reporting.

### Security Services

#### Security Service

**Location**: `/flext/src/flext/infra/security/`

Authentication, authorization, and encryption.

```python
security_service = SecurityService(
    jwt_secret="your-secret-key",
    use_test_engine=False
)

token = await security_service.generate_token(user_id="123")
is_valid = await security_service.validate_token(token)
```

---

## Testing Framework

### Declarative Testing

#### `DeclarativeTestEngine`

**Location**: `/flext/src/flext/testing/declarative.py`

Comprehensive testing framework for hexagonal architecture.

```python
from flext.testing import (
    DeclarativeTestEngine,
    create_test_engine,
    run_full_test_suite,
    validate_test_coverage
)

# Create test engine
engine = create_test_engine()

# Run comprehensive tests
results = run_full_test_suite(engine)

# Validate coverage
coverage_ok = validate_test_coverage(results)
```

#### Test Adapters

**`TestableAdapter`**: Base for testable adapters
**`TestMetrics`**: Test performance metrics
**`TestResult`**: Test execution results

### Test Engines by Domain

**Location**: `/flext/src/flext/testing/engines/`

- `DatabaseTestEngine`: In-memory database testing
- `CacheTestEngine`: In-memory cache testing
- `HttpTestEngine`: Mock HTTP responses
- `CliTestEngine`: Command-line interface testing
- `MetricsTestEngine`: Metrics collection testing

---

## Logging System

### Structured Logging

#### `StandardLoggingAdapter`

**Location**: `/flext/src/flext/adapters/outbound/logging.py`

Production-ready structured logging adapter.

```python
from flext import get_logger

logger = get_logger(__name__)

# Structured logging
logger.info("User action", extra={
    "user_id": "123",
    "action": "login",
    "timestamp": datetime.utcnow()
})
```

#### Domain Logger Interface

**Location**: `/flext/src/flext/core/logging_interface.py`

```python
from flext import DomainLogger, LogLevel

class OrderService:
    def __init__(self, logger: DomainLogger):
        self.logger = logger

    def process_order(self, order_id: str):
        self.logger.log(LogLevel.INFO, "Processing order", {"order_id": order_id})
```

---

## Type System

### Base Types

#### `DomainObject`

**Location**: `/flext/src/flext/core/base.py:200`

Immutable base class for all domain objects.

```python
class Money(DomainObject):
    amount: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(
            amount=self.amount + other.amount,
            currency=self.currency
        )
```

#### Mixins

**`Identifiable`**: UUID-based identity
**`Timestamped`**: Creation and update timestamps
**`Versionable`**: Optimistic locking with version control

---

## Usage Examples

### Complete Hexagonal Flow

```python
from flext import *

# 1. Domain Entity
class Order(AggregateRoot):
    customer_id: str
    total: Money
    status: str = "pending"

    def confirm(self) -> Self:
        if self.status != "pending":
            raise ValueError("Order already confirmed")

        confirmed = self.model_copy(update={
            "status": "confirmed",
            "updated_at": datetime.now(UTC),
            "version": self.version + 1
        })

        confirmed.add_event(OrderConfirmedEvent(
            order_id=self.id,
            customer_id=self.customer_id,
            total=self.total
        ))

        return confirmed

# 2. Application Service
class OrderApplicationService(ApplicationService):
    def __init__(self, order_repo: OrderRepository, event_bus: EventBus):
        self.order_repo = order_repo
        self.event_bus = event_bus

    async def confirm_order(self, order_id: UUID) -> None:
        # Load aggregate
        order = await self.order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)

        # Execute business operation
        confirmed_order = order.confirm()

        # Save with optimistic locking
        await self.order_repo.save(confirmed_order)

        # Publish domain events
        events = confirmed_order.collect_events()
        await self.event_bus.publish_batch(events)

# 3. Testing
async def test_order_confirmation():
    engine = create_test_engine()

    # Use test engines for all infrastructure
    order_repo = OrderRepository(use_test_engine=True)
    event_bus = EventBus(use_test_engine=True)

    service = OrderApplicationService(order_repo, event_bus)

    # Test business logic
    order = Order(customer_id="123", total=Money(amount=99.99, currency="USD"))
    await order_repo.save(order)

    await service.confirm_order(order.id)

    # Verify results
    saved_order = await order_repo.find_by_id(order.id)
    assert saved_order.status == "confirmed"
```

---

## Error Handling

### Domain Exceptions

All domain operations raise clear business exceptions:

- `ValidationError`: Data validation failures
- `ValueError`: Business rule violations
- `ConcurrencyError`: Optimistic locking conflicts

### Infrastructure Exceptions

Infrastructure services provide specific error types:

- `ConnectionError`: Service connection failures
- `TimeoutError`: Operation timeouts
- `ConfigurationError`: Invalid configuration

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Framework Installation**](../../getting-started/setup/installation-guide.md) - Python 3.13+ setup and FLEXT Framework installation required for API usage
- [**Core API Concepts**](../core/index.md) - Core API foundation including base classes and domain events essential for understanding complete API
- [**Architecture Understanding**](../../architecture/design/unified-architecture-guide.md) - Hexagonal architecture patterns underlying all API design decisions

### **➡️ Implementation Next Steps**

- [**Real-World Implementation Examples**](../../examples/real-world-implementations.md) - Production examples demonstrating complete API usage in real systems
- [**Oracle Integration Examples**](../../examples/oracle-integration-real-examples.md) - Oracle-specific examples using complete API for enterprise integration
- [**Testing API Implementation**](../../development/testing/hexagonal-testing-guide.md) - Testing strategies for components built with the complete API

### **🔗 Related Implementation Topics**

- [**Infrastructure Service Integration**](../../infrastructure/service-patterns.md) - Infrastructure services and patterns complementing the complete API
- [**Security API Implementation**](../../security/architecture/security-architecture.md) - Security patterns and authentication using framework APIs
- [**Performance API Optimization**](../../optimization/performance/optimization-guide.md) - Performance optimization techniques for API-based implementations
- [**Oracle WMS API Integration**](../../guides/oracle/oracle-wms-comprehensive-guide.md) - Oracle WMS integration using framework APIs
- [**Database API Patterns**](../../guides/oracle/database-complete-guide.md) - Database integration patterns using framework APIs
- [**Production Deployment APIs**](../../deployment/kubernetes-deployment.md) - Deployment configurations and APIs for production environments

---

**📂 API Reference** | **🏠 Parent**: [Comprehensive API Hub](./index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11

**API Reference Version**: 1.0.0
**Generated From**: `/flext/src/flext/` codebase
**Python Version**: 3.13+
