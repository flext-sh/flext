# 🏛️ FLEXT Architecture Standards - Implementation Guide

> **Function**: Mandatory architectural standards and patterns for FLEXT Framework | **Audience**: Architects, Senior Developers, Technical Leads | **Status**: Stable

[![Standards](https://img.shields.io/badge/standards-mandatory-red.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-blue.svg)](../index.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT-green.svg)](../../index.md)

**Comprehensive architectural standards and mandatory patterns for FLEXT Hexagonal Architecture Multi-Protocol Client Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture Hub](../index.md) → **📂 Standards**: [Standards Hub](./index.md) → **📄 Current**: FLEXT Architecture Standards

### **📍 Learning Path Position**

```
[Architecture Hub](../index.md) → **[Architecture Standards]** → [Consistency Guide](./architectural-consistency-guide.md)
```

## 🎯 **Quick Links**

- **📂 Standards Hub**: [Standards Hub](./index.md)
- **🏛️ Architecture Root**: [Architecture Hub](../index.md)
- **🏠 Documentation Root**: [Documentation Home](../../index.md)
- **🔗 Related**: [Consistency Guide](./architectural-consistency-guide.md)

---

## 📋 **Overview**

FLEXT is a **Hexagonal Architecture Multi-Protocol Client Framework** for Python that provides enterprise-grade integration capabilities for modern systems. This document outlines the mandatory architectural standards and patterns for the FLEXT ecosystem.

## Core Philosophy

> "One import. One client. One CLI. Everything connected—without boilerplate."

## Architectural Principles

### 1. Mandatory Design Patterns

- **SOLID Principles**: Strict adherence to all five principles
- **KISS (Keep It Simple, Stupid)**: Eliminate unnecessary complexity
- **DRY (Don't Repeat Yourself)**: Abstract common patterns effectively

### 2. Python 3.13+ Advanced Features

Leverage modern Python features for code reduction:

- Pattern matching with `match/case`
- Advanced type hints and generics
- Structural pattern matching
- Performance optimizations
- Async/await patterns

### 3. Pydantic as Core Foundation

- All data validation through Pydantic models
- Configuration management via Pydantic Settings
- Type-safe protocol definitions
- Automatic serialization/deserialization

## Hexagonal Architecture Implementation

### 4. Core Domain (`flext.core`)

The domain layer contains pure business logic with zero external dependencies:

```
flext.core/
├── base.py          # Base abstractions (Entity, ValueObject, DomainService)
├── entities.py      # Domain entities and aggregate roots
├── value_objects.py # Immutable value objects
├── events.py        # Domain events (FlextDomainEvent)
├── services.py      # Domain services interfaces
├── exceptions.py    # Domain-specific exceptions
├── protocols.py     # Protocol definitions using typing.Protocol
└── types.py         # Type aliases and custom types
```

**Key Requirements:**

- Use composition over inheritance
- Leverage Python 3.13 protocols for interfaces
- Keep domain pure - no infrastructure dependencies

### 5. Infrastructure Layer (`flext.infra`)

All concrete implementations and external integrations:

```
flext.infra/
├── adapters/        # Protocol adapter implementations
├── config/          # Configuration management
├── logging/         # Structured logging with Logfire
├── messaging/       # Async messaging with Lato and Dramatiq
├── observability/   # Metrics, tracing, health checks
├── resilience/      # Circuit breakers, retries
├── security/        # Authentication, authorization
└── plugins/         # Plugin discovery and management
```

### 6. Ports Architecture (`flext.ports`)

Clean interfaces between domain and infrastructure:

```
flext.ports/
├── inbound/         # Driving ports (API, CLI, Events)
│   ├── api.py       # HTTP/gRPC API ports
│   ├── cli.py       # CLI command ports
│   └── events.py    # Event listener ports
└── outbound/        # Driven ports (repositories, clients)
    ├── database.py  # Database repository ports
    ├── http.py      # HTTP client ports
    └── messaging.py # Message queue ports
```

### 7. Adapter Pattern (`flext.adapters`)

Protocol-specific implementations as hexagonal adapters:

```
flext.adapters/
├── inbound/         # Driving adapters
│   ├── api/         # FastAPI/Flask adapters
│   ├── cli/         # Cyclopts CLI adapter
│   └── grpc/        # gRPC service adapters
└── outbound/        # Driven adapters
    ├── http/        # HTTPX/aiohttp adapters
    └── database/    # SQLAlchemy/asyncpg adapters
```

### 8. Asynchronous Communication

**Mandatory Libraries:**

- **Lato**: For Domain-Driven Design support and CQRS
- **Dramatiq**: For asynchronous task processing

All inter-adapter communication must be:

- Asynchronous by default
- Message-based using domain events
- Transparent to the domain layer

### 9. Plugin System Architecture

External adapters integration via **Pluggy**:

```python
# Plugin interface definition
class ProtocolPlugin(Protocol):
    """Protocol plugin interface."""

    @property
    def name(self) -> str: ...

    @property
    def protocols(self) -> list[str]: ...

    async def connect(self, config: Config) -> Adapter: ...
```

### 10. Default Infrastructure Stack

| Component | Implementation                  | Location                          |
| --------- | ------------------------------- | --------------------------------- |
| Logging   | Structured logging with Logfire | `flext.infra.logging.structured`  |
| Config    | YAML + Environment variables    | `flext.infra.config.hierarchical` |
| CLI       | Cyclopts with auto-discovery    | `flext.infra.cli.cyclopts`        |
| Output    | Rich console output             | `flext.infra.output.rich`         |
| Auth      | Multi-provider authentication   | `flext.infra.security.auth`       |
| Cache     | Redis with local fallback       | `flext.infra.cache.hybrid`        |

### 11. Configuration Hierarchy

Priority order (highest to lowest):

1. Environment variables (`FLX_*`)
2. CLI arguments
3. Profile-specific config (`config.{profile}.yaml`)
4. Default config (`config.yaml`)
5. Built-in defaults

**Configuration discovery:**

```bash
export FLX_CONFIG_PATH=/custom/path/config.yaml
export FLX_PROFILE=production
```

### 12. Multi-Protocol Client Pattern

The unified `ApiClient` facade:

```python
from flext import ApiClient

# One client for all protocols
client = ApiClient()

# HTTP operations
response = await client.http.get("https://api.example.com/data")

# Database operations
results = await client.database.query("SELECT * FROM users")

# Message queue operations
await client.messaging.publish(queue="tasks", message=data)

# Authentication operations
user = await client.auth.authenticate(username="user", password="pass")
```

### 13. Domain Event Architecture

Event-driven integration using domain events:

```python
from flext.core.events import FlextDomainEvent
from pydantic import Field

class InventoryUpdatedEvent(FlextDomainEvent):
    """Inventory update domain event."""

    warehouse_id: str
    sku: str
    quantity: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### 14. Testing Strategy

Comprehensive testing approach:

- **Unit Tests**: Domain logic in isolation
- **Integration Tests**: Adapter functionality
- **Contract Tests**: Port compliance
- **E2E Tests**: Complete workflows
- **Performance Tests**: Benchmarking
- **Property Tests**: Using Hypothesis

Coverage requirements:

- Domain layer: 100%
- Ports: 100%
- Adapters: 90%+
- Infrastructure: 80%+

## Implementation Guidelines

1. **Start with the domain** - Define entities, value objects, and events
2. **Design ports** - Create clean interfaces for external communication
3. **Implement adapters** - Build concrete implementations
4. **Configure infrastructure** - Setup logging, config, observability
5. **Add plugins** - Extend with protocol-specific capabilities
6. **Test thoroughly** - Unit, integration, and E2E tests

## Example: E-commerce Integration

```python
# Domain entity (flext/core/entities.py)
class ShoppingCart(AggregateRoot):
    """Shopping cart aggregate."""

    cart_id: str
    items: list[CartItem]
    customer_id: str
    created_at: datetime

    def add_item(self, product_id: str, quantity: int) -> ItemAddedEvent:
        """Add item to cart."""
        # Domain logic here
        return ItemAddedEvent(
            cart_id=self.cart_id,
            product_id=product_id,
            quantity=quantity
        )

# Port definition (flext/ports/outbound/commerce.py)
class CommercePort(Protocol):
    """E-commerce integration port."""

    async def get_cart(self, cart_id: str) -> ShoppingCart: ...
    async def update_cart(self, event: ItemAddedEvent) -> None: ...

# Adapter implementation (flext/adapters/outbound/http/commerce_adapter.py)
class HTTPCommerceAdapter(CommercePort):
    """HTTP commerce adapter."""

    def __init__(self, config: CommerceConfig):
        self.client = httpx.AsyncClient(base_url=config.api_url)

    async def get_cart(self, cart_id: str) -> ShoppingCart:
        # Implementation using REST APIs
        response = await self.client.get(f"/carts/{cart_id}")
        return ShoppingCart(**response.json())
```

This architecture ensures:

- **Protocol independence** - Business logic doesn't know about HTTP details
- **Testability** - Easy to mock ports for testing
- **Flexibility** - Can swap implementations without changing domain
- **Type safety** - Full typing with Pydantic models
- **Observability** - Built-in logging, metrics, and tracing

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Hub](../index.md) - Understanding hexagonal architecture foundations and design principles
- [Getting Started Guide](../../getting-started/index.md) - Basic FLEXT Framework concepts before implementing standards
- [Development Standards](../../development/standards/standardization-plan.md) - General development standards that complement architecture standards

### **Next Steps**

- [Architectural Consistency Guide](./architectural-consistency-guide.md) - Detailed implementation consistency patterns and guidelines
- [Modernization Roadmap](./modernization-roadmap.md) - Framework evolution strategy following these standards
- [Implementation Guides](../../guides/index.md) - Apply these standards in real-world projects

### **Related Topics**

- [SOLID Principles Implementation](../patterns/solid-principles-implementation.md) - SOLID principles applied within these architectural standards
- [Core Domain Layer](../layers/core-domain-layer.md) - Domain layer implementation following these standards
- [Ports and Adapters](../ports/index.md) - Port-adapter pattern implementation according to standards
- [Infrastructure Architecture](../infrastructure/index.md) - Infrastructure layer following these architectural standards
- [Testing Strategies](../../development/testing/index.md) - Testing approaches for standards-compliant architecture

---

## 🆘 **Troubleshooting**

### **Architecture Violations**

**Issue**: Domain code importing infrastructure dependencies
**Solution**: Refactor to use dependency injection through ports
**Prevention**: Enforce architecture rules with import analysis and linting

### **Standards Compliance**

**Issue**: Inconsistent implementation patterns across adapters
**Solution**: Apply standardized mixin patterns and follow consistency guide
**Prevention**: Use code review checklists and automated compliance checks

---

**📂 Hub**: [Standards Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
