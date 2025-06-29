# FLX Framework - Comprehensive API Overview

> **Function**: Complete FLX API reference documentation | **Audience**: Developers, architects | **Status**: Stable

[![Framework](https://img.shields.io/badge/framework-FLX_0.4.0-blue.svg)](../../index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](../../architecture/index.md)
[![DDD](https://img.shields.io/badge/pattern-DDD-orange.svg)](../../guides/patterns/index.md)

**Complete API reference for the FLX Framework's Domain-Driven Design implementation with Hexagonal Architecture**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [API Reference](../index.md) → **📄 Current**: FLX API Overview

### **📍 Learning Path Position**

```
[API Reference Hub](../index.md) → **[FLX API OVERVIEW]** → [Core API Reference](../framework/core-api-reference-validated.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [API Reference Hub](../index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [FLX Adapters Reference](../adapters/flext-adapters-comprehensive-reference.md)

---

## Overview

The `Flx` class provides a comprehensive Domain-Driven Design framework with Hexagonal Architecture, offering organized access to rich domain entities, value objects, and architectural patterns for building scalable, maintainable applications.

## Core Components

### 1. **Domain-Oriented Architecture**

The FLX framework follows Domain-Driven Design principles with clear separation of concerns:

```python
from flext import Flx

# Initialize the framework
flext = Flx()

# Rich domain entities
user = flext.Entities.BaseEntity(name="John Doe")
order = flext.Entities.AggregateRoot(name="Order #123")
service = flext.Entities.ServiceEntity(name="Payment API", service_type="REST")

# Value objects for immutable data
contact = flext.ValueObjects.ContactInfo(
    email="john@example.com",
    phone="+1-555-0123"
)

# Domain events
event = flext.ValueObjects.FlxDomainEvent(
    event_type="UserCreated",
    aggregate_id=user.id,
    aggregate_type="User",
    event_data={"name": user.name}
)
```

### 2. **Component Organization**

| Section             | Responsibility      | Main Components                                        |
| ------------------- | ------------------- | ------------------------------------------------------ |
| `flext.Entities`      | Domain entities     | `BaseEntity`, `AggregateRoot`, `BusinessEntity`        |
| `flext.ValueObjects`  | Immutable data      | `FlxDomainEvent`, `EntityId`, `Address`, `ContactInfo` |
| `flext.Protocols`     | Type interfaces     | `Configurable`, `Activatable`, `Timestamped`           |
| `flext.Mixins`        | Composable behavior | `Status`, `Config`, `Metadata`, `Management`           |
| `flext.EntityFactory` | Entity creation     | `flext_create_service()`, `flext_create_configurable()`    |

---

## API Reference

### Entities Module (`flext.Entities`)

#### BaseEntity

The foundation class for all domain entities with identity and lifecycle management.

```python
user = flext.Entities.BaseEntity(name="John Doe")
print(f"User ID: {user.id}, Name: {user.name}")
```

**Properties:**

- `id` (str): Unique identifier (auto-generated UUID)
- `name` (str): Human-readable name
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

**Methods:**

- `get_identity()` → str: Returns the entity's unique identifier
- `update_name(new_name: str)` → None: Updates the entity name

#### TimestampedEntity

Entity with automatic timestamp management.

```python
document = flext.Entities.TimestampedEntity()
print(f"Created at: {document.created_at}")
```

**Properties:**

- Inherits all BaseEntity properties
- `created_at` (datetime): Automatically set on creation
- `updated_at` (datetime): Automatically updated on changes

#### VersionedEntity

Entity with version control capabilities.

```python
contract = flext.Entities.VersionedEntity()
contract.increment_version()
print(f"Version: {contract.version}")
```

**Properties:**

- Inherits all BaseEntity properties
- `version` (int): Version number (starts at 1)

**Methods:**

- `increment_version()` → None: Increments the version number
- `get_version()` → int: Returns current version

#### BusinessEntity

Base class for entities with domain logic and event support.

```python
class OrderEntity(flext.Entities.BusinessEntity):
    def process_payment(self, amount: float):
        self.raise_domain_event("PaymentRequested", {"amount": amount})

order = OrderEntity(name="Order #12345")
order.process_payment(100.0)
events = order.get_domain_events()
```

**Methods:**

- `raise_domain_event(event_type: str, data: dict)` → None: Raises a domain event
- `get_domain_events()` → List[FlxDomainEvent]: Returns all raised events
- `clear_domain_events()` → None: Clears all domain events

#### AggregateRoot

Root entity for aggregate boundaries with domain event management.

```python
order = flext.Entities.AggregateRoot(name="Order #12345")
order.raise_domain_event("OrderCreated", {"customer_id": "123"})
```

**Methods:**

- Inherits all BusinessEntity methods
- Enhanced event management for aggregate consistency

#### ServiceEntity

Entity representing technical services and external integrations.

```python
payment_service = flext.Entities.ServiceEntity(
    name="Payment Gateway",
    service_type="REST",
    endpoint="https://api.payment.com"
)
```

**Properties:**

- Inherits all BaseEntity properties
- `service_type` (str): Type of service (REST, GraphQL, gRPC, etc.)
- `endpoint` (str, optional): Service endpoint URL

**Methods:**

- `configure_timeout(seconds: int)` → None: Sets service timeout
- `get_service_info()` → dict: Returns service information

### Value Objects Module (`flext.ValueObjects`)

#### ContactInfo

Immutable contact information value object.

```python
contact = flext.ValueObjects.ContactInfo(
    email="john@example.com",
    phone="+1-555-0123"
)
```

**Properties:**

- `email` (str): Email address (validated)
- `phone` (str): Phone number

#### Address

Immutable address value object.

```python
address = flext.ValueObjects.Address(
    street="123 Main St",
    city="Springfield",
    country="USA"
)
```

**Properties:**

- `street` (str): Street address
- `city` (str): City name
- `country` (str): Country name
- `postal_code` (str, optional): Postal/ZIP code

#### FlxDomainEvent

Domain event representation for business occurrences.

```python
event = flext.ValueObjects.FlxDomainEvent(
    event_type="CustomerRegistered",
    aggregate_id="customer-123",
    aggregate_type="Customer",
    event_data={
        "name": "John Doe",
        "email": "john@example.com"
    }
)
```

**Properties:**

- `event_type` (str): Type of domain event
- `aggregate_id` (str): ID of the aggregate that raised the event
- `aggregate_type` (str): Type of the aggregate
- `event_data` (dict): Event payload data
- `occurred_at` (datetime): When the event occurred (auto-generated)
- `event_id` (str): Unique event identifier (auto-generated)

### Protocols Module (`flext.Protocols`)

#### Configurable

Protocol for entities with configuration capabilities.

```python
def process_configurable(entity: flext.Protocols.Configurable) -> dict:
    return entity.config
```

**Required Methods:**

- `get_config(key: str)` → Any: Get configuration value
- `set_config(key: str, value: Any)` → None: Set configuration value
- `config` (property) → dict: Get all configuration

#### Activatable

Protocol for entities that can be activated/deactivated.

```python
def activate_entity(entity: flext.Protocols.Activatable) -> bool:
    entity.activate()
    return entity.active
```

**Required Methods:**

- `activate()` → None: Activate the entity
- `deactivate()` → None: Deactivate the entity
- `active` (property) → bool: Check if entity is active

#### Timestamped

Protocol for entities with timestamp tracking.

```python
def get_creation_time(entity: flext.Protocols.Timestamped) -> datetime:
    return entity.created_at
```

**Required Properties:**

- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### Mixins Module (`flext.Mixins`)

#### Status

Mixin providing activation/deactivation capabilities.

```python
class AdvancedEntity(flext.Entities.BaseEntity, flext.Mixins.Status):
    pass

entity = AdvancedEntity(name="Advanced System")
entity.activate()
print(f"Active: {entity.active}")
```

**Methods:**

- `activate()` → None: Activate the entity
- `deactivate()` → None: Deactivate the entity
- `toggle_status()` → None: Toggle activation status

**Properties:**

- `active` (bool): Current activation status

#### Config

Mixin providing configuration management.

```python
class ConfigurableEntity(flext.Entities.BaseEntity, flext.Mixins.Config):
    pass

entity = ConfigurableEntity(name="Configurable System")
entity.set_config("timeout", 30)
print(f"Timeout: {entity.get_config('timeout')}")
```

**Methods:**

- `set_config(key: str, value: Any)` → None: Set configuration value
- `get_config(key: str, default: Any = None)` → Any: Get configuration value
- `update_config(config_dict: dict)` → None: Update multiple configuration values
- `clear_config()` → None: Clear all configuration

**Properties:**

- `config` (dict): All configuration values

#### Metadata

Mixin providing flexible metadata management.

```python
class MetadataEntity(flext.Entities.BaseEntity, flext.Mixins.Metadata):
    pass

entity = MetadataEntity(name="Metadata System")
entity.add_metadata("environment", "production")
print(f"Environment: {entity.get_metadata('environment')}")
```

**Methods:**

- `add_metadata(key: str, value: Any)` → None: Add metadata
- `get_metadata(key: str, default: Any = None)` → Any: Get metadata value
- `update_metadata(metadata_dict: dict)` → None: Update multiple metadata values
- `remove_metadata(key: str)` → None: Remove metadata key
- `clear_metadata()` → None: Clear all metadata

**Properties:**

- `metadata` (dict): All metadata values

#### Management

Combines Status and Metadata mixins for comprehensive management.

```python
class ManagedEntity(flext.Entities.BaseEntity, flext.Mixins.Management):
    pass

entity = ManagedEntity(name="Managed System")
entity.activate()
entity.add_metadata("version", "2.0")
```

#### FullCapability

Combines all mixins (Status, Config, Metadata) for maximum functionality.

```python
class FullEntity(flext.Entities.BaseEntity, flext.Mixins.FullCapability):
    pass

entity = FullEntity(name="Full System")
entity.activate()
entity.set_config("timeout", 30)
entity.add_metadata("version", "2.0")
```

---

## Usage Patterns

### Pattern 1: Simple Domain Entity

```python
from flext import Flx

flext = Flx()

# Create a simple domain entity
user = flext.Entities.BaseEntity(name="John Doe")
print(f"User created: {user.id}")
```

### Pattern 2: Enhanced Entity with Capabilities

```python
# Create entity with multiple capabilities
class AdvancedUser(
    flext.Entities.BaseEntity,
    flext.Mixins.Status,
    flext.Mixins.Config,
    flext.Mixins.Metadata
):
    pass

user = AdvancedUser(name="John Doe")
user.activate()
user.set_config("theme", "dark")
user.add_metadata("last_login", "2024-01-15")
```

### Pattern 3: Business Logic with Events

```python
class OrderEntity(flext.Entities.BusinessEntity):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.items = []
        self.status = "draft"

    def add_item(self, item: dict):
        self.items.append(item)
        self.raise_domain_event("ItemAdded", {
            "order_id": self.id,
            "item": item
        })

    def confirm_order(self):
        if not self.items:
            raise ValueError("Cannot confirm empty order")

        self.status = "confirmed"
        self.raise_domain_event("OrderConfirmed", {
            "order_id": self.id,
            "items_count": len(self.items)
        })

# Usage
order = OrderEntity(name="Order #123")
order.add_item({"product": "Widget", "quantity": 2})
order.confirm_order()

events = order.get_domain_events()
print(f"Events raised: {len(events)}")
```

### Pattern 4: Service Integration

```python
# Define external service
payment_service = flext.Entities.ServiceEntity(
    name="Payment Gateway",
    service_type="REST",
    endpoint="https://api.stripe.com"
)

# Configure service
payment_service.configure_timeout(30)

# Use in business logic
class PaymentProcessor:
    def __init__(self, payment_service):
        self.payment_service = payment_service

    def process_payment(self, amount: float, order_id: str):
        # Business logic
        event = flext.ValueObjects.FlxDomainEvent(
            event_type="PaymentRequested",
            aggregate_id=order_id,
            aggregate_type="Order",
            event_data={
                "amount": amount,
                "service": self.payment_service.name,
                "endpoint": self.payment_service.endpoint
            }
        )
        return event

processor = PaymentProcessor(payment_service)
payment_event = processor.process_payment(100.0, "order-123")
```

### Pattern 5: Type-Safe Operations

```python
from typing import List

# Type-safe functions using protocols
def activate_entities(entities: List[flext.Protocols.Activatable]) -> int:
    """Activate multiple entities and return count of successful activations."""
    activated_count = 0
    for entity in entities:
        entity.activate()
        if entity.active:
            activated_count += 1
    return activated_count

def configure_entities(entities: List[flext.Protocols.Configurable], config: dict) -> None:
    """Apply configuration to multiple entities."""
    for entity in entities:
        for key, value in config.items():
            entity.set_config(key, value)

# Usage with type safety
class ServiceManager(flext.Entities.ServiceEntity, flext.Mixins.FullCapability):
    pass

services = [
    ServiceManager(name="Service A", service_type="REST"),
    ServiceManager(name="Service B", service_type="GraphQL"),
]

# Type-safe operations
activated = activate_entities(services)  # Type checker validates
configure_entities(services, {"timeout": 30, "retries": 3})
```

---

## Architecture Principles

### Hexagonal Architecture

FLX implements hexagonal architecture with clear separation:

```python
# Domain layer (center) - pure business logic
user = flext.Entities.BaseEntity(name="John")
order = flext.Entities.AggregateRoot(name="Order")

# Application layer - use cases and orchestration
class CreateOrderUseCase:
    def __init__(self, order_repo, user_repo):
        self.order_repo = order_repo  # Port (interface)
        self.user_repo = user_repo    # Port (interface)

    def execute(self, order_data: dict):
        user = self.user_repo.find_by_id(order_data["user_id"])
        order = flext.Entities.AggregateRoot(name=f"Order {order_data['id']}")
        # Business logic here...
        return order

# Infrastructure layer - adapters
class DatabaseOrderRepository:  # Adapter implementation
    def save(self, order): ...
    def find_by_id(self, order_id): ...
```

### Domain-Driven Design

Rich domain modeling with business logic encapsulation:

```python
# Entities with identity and lifecycle
customer = flext.Entities.BaseEntity(name="Customer")

# Aggregates for consistency boundaries
order = flext.Entities.AggregateRoot(name="Order")
order.raise_domain_event("OrderCreated", {"customer_id": customer.id})

# Value objects for immutable concepts
address = flext.ValueObjects.Address(street="123 Main St", city="Springfield")

# Domain events for business occurrences
event = flext.ValueObjects.FlxDomainEvent(
    event_type="CustomerMoved",
    aggregate_id=customer.id,
    event_data={"new_address": address.street}
)
```

---

## Error Handling

### Entity Validation

```python
try:
    # Entities validate input automatically
    contact = flext.ValueObjects.ContactInfo(
        email="invalid-email",  # Will raise validation error
        phone="+1-555-0123"
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

### Domain Event Validation

```python
try:
    # Domain events require valid data
    event = flext.ValueObjects.FlxDomainEvent(
        event_type="",  # Empty event type will raise error
        aggregate_id="123",
        aggregate_type="User",
        event_data={}
    )
except ValueError as e:
    print(f"Event validation error: {e}")
```

---

## Best Practices

### 1. Entity Design

```python
# Good: Focused entities with single responsibility
class User(flext.Entities.BaseEntity):
    def __init__(self, name: str, email: str):
        super().__init__(name=name)
        self.email = email
        self.profile = None

# Better: Use value objects for complex data
class User(flext.Entities.BaseEntity):
    def __init__(self, name: str, contact_info: flext.ValueObjects.ContactInfo):
        super().__init__(name=name)
        self.contact_info = contact_info
```

### 2. Event Naming

```python
# Good: Use past tense for domain events
order.raise_domain_event("OrderCreated", data)
order.raise_domain_event("PaymentProcessed", data)
order.raise_domain_event("ItemsShipped", data)

# Avoid: Present tense or unclear names
# order.raise_domain_event("CreateOrder", data)  # Avoid
# order.raise_domain_event("Process", data)      # Avoid
```

### 3. Mixin Composition

```python
# Good: Use specific mixins for specific needs
class ConfigurableService(flext.Entities.ServiceEntity, flext.Mixins.Config):
    pass

class ManagedService(flext.Entities.ServiceEntity, flext.Mixins.Management):
    pass

# Use FullCapability only when you need all features
class ComplexService(flext.Entities.ServiceEntity, flext.Mixins.FullCapability):
    pass
```

### 4. Protocol Usage

```python
# Good: Use protocols for type hints in functions
def process_configurable_entities(
    entities: List[flext.Protocols.Configurable],
    config: dict
) -> None:
    for entity in entities:
        entity.update_config(config)

# Good: Use protocols for dependency injection
class BusinessService:
    def __init__(self, notifier: flext.Protocols.Activatable):
        self.notifier = notifier
```

---

## Migration Guide

### From Simple Classes

```python
# Before: Simple classes
class User:
    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name

# After: FLX entities
class User(flext.Entities.BaseEntity):
    def __init__(self, name: str):
        super().__init__(name=name)
        # ID and timestamps are automatically managed
```

### From Basic Events

```python
# Before: Simple event handling
events = []
events.append({"type": "UserCreated", "data": {"name": "John"}})

# After: Domain events
user = flext.Entities.BusinessEntity(name="John")
user.raise_domain_event("UserCreated", {"name": "John"})
events = user.get_domain_events()
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Getting Started Guide](../../getting-started/index.md) - Setting up FLX Framework
- [Core API Reference](../framework/core-api-reference-validated.md) - Understanding core components

### **Next Steps**

- [FLX Adapters Reference](../adapters/flext-adapters-comprehensive-reference.md) - Working with adapter system
- [Domain Entity Examples](../../examples/basic-examples.md) - Practical implementation examples
- [Testing Guide](../../development/testing/index.md) - Testing FLX applications

### **Related Topics**

- [Hexagonal Architecture Guide](../../architecture/design/unified-architecture-guide.md) - Architecture principles
- [Infrastructure Services](../../infrastructure/index.md) - Infrastructure layer integration
- [Oracle Integration Examples](../../examples/oracle-integration-real-examples.md) - Real-world usage patterns

---

**📂 Hub**: [API Reference](../index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
