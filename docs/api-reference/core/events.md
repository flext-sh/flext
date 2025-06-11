# 🎯 Domain Events API Reference

> **Function**: Event-driven architecture patterns and domain events | **Audience**: Domain developers, event architects | **Status**: Production-Ready

[![Events](https://img.shields.io/badge/events-domain-purple.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-event_driven-green.svg)](../../architecture/patterns/event-sourcing-implementation.md)
[![DDD](https://img.shields.io/badge/DDD-events-blue.svg)](../../architecture/patterns/domain-driven-design-patterns.md)

**Event-driven architecture foundation for FLX hexagonal framework implementing Domain Events pattern for business occurrences and loose coupling between bounded contexts - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [API Reference](../index.md) → **📂 Section**: [Core](./index.md) → **📄 Current**: Domain Events API

### **📍 Learning Path Position**

```
[Core APIs](./index.md) → [Base Classes](./base-classes.md) → **[Domain Events]** → [Complete API](../comprehensive/flx-complete-api.md)
```

## Overview

The Domain Events module provides the foundation for event-driven architecture in the FLX hexagonal framework. It implements the Domain Events pattern to capture important business occurrences and enable loose coupling between bounded contexts.

## Classes

### DomainEvent

Base class for all domain events in the FLX hexagonal architecture.

```python
from flx.core.events import DomainEvent

class UserRegistered(DomainEvent):
    user_id: str
    email: str
    registration_date: datetime
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `event_id` | `UUID` | Unique identifier for the event, automatically generated |
| `event_type` | `str` | Event type name, derived from class name if not specified |
| `occurred_at` | `datetime` | Timestamp when the event occurred (UTC) |
| `aggregate_id` | `UUID \| None` | ID of the aggregate that generated this event |
| `correlation_id` | `UUID \| None` | ID for tracing related events across requests |
| `causation_id` | `UUID \| None` | ID of the event that caused this event |
| `metadata` | `dict[str, object]` | Additional contextual information |

#### Methods

##### `__init__(**data: object) -> None`

Initialize domain event with automatic event type generation and validation.

**Parameters:**

- `**data`: Event data including both standard fields and event-specific fields

**Example:**

```python
event = UserRegistered(
    aggregate_id=uuid4(),
    user_id="user_12345",
    email="john.doe@example.com"
)
```

##### `with_correlation(correlation_id: UUID) -> DomainEvent`

Create a new event instance with correlation ID for distributed tracing.

**Parameters:**

- `correlation_id`: UUID that identifies the broader request or operation context

**Returns:**

- New event instance with the correlation ID set

**Example:**

```python
correlation_id = uuid4()
correlated_event = event.with_correlation(correlation_id)
```

##### `with_causation(causation_id: UUID) -> DomainEvent`

Create a new event instance with causation ID for event chain tracking.

**Parameters:**

- `causation_id`: UUID of the event that directly caused this event

**Returns:**

- New event instance with the causation ID set

**Example:**

```python
caused_event = follow_up_event.with_causation(original_event.event_id)
```

### FlxDomainEvent

FLX framework-specific domain event with enhanced multi-tenancy and routing.

```python
from flx.core.events import FlxDomainEvent

class TenantUserRegistered(FlxDomainEvent):
    user_id: str
    email: str
    plan_type: str
```

#### Additional Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tenant_id` | `str \| None` | Tenant identifier for multi-tenant isolation |
| `user_id` | `str \| None` | User who initiated the action that caused this event |
| `source` | `str` | Source system identifier (default: "flx") |
| `version` | `str` | Event schema version (default: "1.0") |

#### Properties

##### `routing_key -> str`

Generate intelligent message routing key for event-driven architectures.

**Returns:**

- Hierarchical routing key for message broker routing

**Format:**

- With tenant: `"flx.{tenant_id}.{event_type_normalized}"`
- Without tenant: `"flx.{event_type_normalized}"`

**Example:**

```python
# Single-tenant event
event = FlxDomainEvent()
event.event_type = "UserRegistered"
assert event.routing_key == "flx.userregistered"

# Multi-tenant event
tenant_event = FlxDomainEvent(tenant_id="acme_corp")
tenant_event.event_type = "OrderPlaced"
assert tenant_event.routing_key == "flx.acme_corp.orderplaced"
```

## Usage Patterns

### Basic Event Creation

```python
from flx.core.events import DomainEvent
from datetime import datetime
from uuid import uuid4

class OrderCreated(DomainEvent):
    order_id: str
    customer_id: str
    total_amount: float

# Create event
event = OrderCreated(
    aggregate_id=uuid4(),
    order_id="ORD-123",
    customer_id="CUST-456",
    total_amount=99.99,
    metadata={"channel": "web", "promotion": "SAVE10"}
)
```

### Event Correlation and Causation

```python
# Create correlated events for request tracing
correlation_id = uuid4()

order_event = OrderCreated(...).with_correlation(correlation_id)
payment_event = PaymentProcessed(...).with_correlation(correlation_id)
shipping_event = ShippingScheduled(...).with_causation(order_event.event_id)
```

### Multi-Tenant Events

```python
from flx.core.events import FlxDomainEvent

class TenantOrderPlaced(FlxDomainEvent):
    order_id: str
    customer_id: str
    items: list[dict]

# Create tenant-specific event
event = TenantOrderPlaced(
    tenant_id="company_abc",
    user_id="sales_rep_123",
    order_id="ORD-456",
    customer_id="CUST-789",
    items=[{"product": "Widget", "qty": 2}],
    version="2.0"
)

# Automatic routing key for message brokers
routing_key = event.routing_key  # "flx.company_abc.tenantorderplaced"
```

## Architecture Integration

### Event Sourcing

```python
# Store events as the source of truth
event_store.append_events(stream_id="order-123", events=[
    OrderCreated(...),
    PaymentProcessed(...),
    OrderShipped(...)
])

# Replay events to rebuild state
events = event_store.get_events(stream_id="order-123")
order = Order.from_events(events)
```

### CQRS Integration

```python
# Command side generates events
class PlaceOrderHandler:
    async def handle(self, command: PlaceOrderCommand) -> None:
        order = Order.create(command.customer_id, command.items)

        # Generate domain event
        event = OrderCreated(
            aggregate_id=order.id,
            order_id=order.order_id,
            customer_id=order.customer_id,
            total_amount=order.total
        )

        # Publish event for read model updates
        await self.event_publisher.publish(event)
```

### Message Broker Integration

```python
# RabbitMQ routing patterns
await publisher.publish(
    routing_key=event.routing_key,  # "flx.tenant123.orderplaced"
    message=event.model_dump()
)

# Subscribe to tenant-specific events
await subscriber.subscribe(
    pattern="flx.tenant123.*",
    handler=handle_tenant_events
)

# Subscribe to specific event types across tenants
await subscriber.subscribe(
    pattern="flx.*.orderplaced",
    handler=handle_order_events
)
```

## Best Practices

### Event Design

1. **Use Past Tense**: Events represent things that have already happened

   ```python
   # Good
   class OrderPlaced(DomainEvent): pass
   class PaymentProcessed(DomainEvent): pass

   # Avoid
   class PlaceOrder(DomainEvent): pass
   class ProcessPayment(DomainEvent): pass
   ```

2. **Self-Contained**: Include all necessary information

   ```python
   class OrderShipped(DomainEvent):
       order_id: str
       customer_id: str
       tracking_number: str
       carrier: str
       estimated_delivery: datetime
   ```

3. **Immutable**: Never modify events after creation

   ```python
   # Good - create new event with updates
   updated_event = event.with_correlation(correlation_id)

   # Avoid - modifying existing event
   event.correlation_id = correlation_id  # Don't do this
   ```

### Security Considerations

1. **Sensitive Data**: Avoid storing sensitive information in events

   ```python
   class UserRegistered(DomainEvent):
       user_id: str
       email: str
       # Don't include: password, ssn, credit_card
   ```

2. **Tenant Isolation**: Use tenant_id for proper isolation

   ```python
   event = FlxDomainEvent(
       tenant_id="tenant123",  # Ensures proper routing
       # ... other fields
   )
   ```

3. **Audit Trails**: Use correlation and causation for security auditing

   ```python
   # Track security-related event chains
   login_event = UserLoggedIn(...).with_correlation(session_id)
   permission_event = PermissionGranted(...).with_causation(login_event.event_id)
   ```

## Error Handling

Events are immutable and validated through Pydantic. Common errors include:

- **Validation Error**: Invalid field types or missing required fields
- **Serialization Error**: Non-serializable objects in metadata
- **Routing Error**: Invalid tenant_id or event_type formats

```python
try:
    event = OrderCreated(
        order_id="ORD-123",
        # Missing required customer_id
    )
except ValidationError as e:
    logger.error(f"Event validation failed: {e}")
```

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Base Classes Foundation**](./base-classes.md) - Domain object patterns essential for understanding event generation and handling
- [**Event Sourcing Patterns**](../../architecture/patterns/event-sourcing-implementation.md) - Event sourcing architectural patterns required for event-driven design
- [**Domain-Driven Design Concepts**](../../architecture/patterns/domain-driven-design-patterns.md) - DDD patterns including aggregate roots and domain events

### **➡️ Implementation Next Steps**

- [**Messaging Infrastructure**](../../infrastructure/messaging-infrastructure.md) - Message bus and event handling infrastructure for event distribution
- [**Event-Driven Examples**](../../examples/real-world-implementations.md) - Production examples demonstrating domain events in real systems
- [**Testing Event-Driven Systems**](../../development/testing/hexagonal-testing-guide.md) - Testing strategies for event-driven components

### **🔗 Related Implementation Topics**

- [**Infrastructure Service Patterns**](../../infrastructure/service-patterns.md) - Infrastructure services for event handling, storage, and distribution
- [**Oracle Integration Events**](../../examples/oracle-integration-real-examples.md) - Oracle integration examples using domain events for workflow coordination
- [**Complete Framework API**](../comprehensive/flx-complete-api.md) - Full API documentation including event handling and infrastructure integration
- [**Security Event Patterns**](../../security/architecture/security-architecture.md) - Security-related events and audit trail patterns
- [**Performance Event Optimization**](../../optimization/performance/optimization-guide.md) - Performance considerations for event processing and distribution
- [**Production Event Monitoring**](../../infrastructure/operational-excellence.md) - Event monitoring, tracing, and observability in production systems

---

**📂 API Reference** | **🏠 Parent**: [Core APIs Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
