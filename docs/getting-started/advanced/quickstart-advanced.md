# Quick Start Guide

Get up and running with FLEXT in minutes! This guide will walk you through creating your first domain entities and understanding the core concepts.

## Your First FLEXT Application

### 1. Basic Setup

```python
from flext import Flx

# Initialize the FLEXT framework
flext = Flx()

# Access organized domain components
entities = flext.Entities              # Rich entity classes
protocols = flext.Protocols            # Type protocols for interfaces
mixins = flext.Mixins                  # Composable functionality
value_objects = flext.ValueObjects     # Immutable data structures
```

### 2. Create Your First Entity

```python
# Create a simple domain entity
user = flext.Entities.BaseEntity(name="John Doe")

print(f"Created user: {user.name}")
print(f"Entity ID: {user.id}")
print(f"Created at: {user.created_at}")
print(f"Is active: {user.active}")
```

**Output:**

```
Created user: John Doe
Entity ID: ent_abc123def456
Created at: 2024-01-15T10:30:00Z
Is active: True
```

### 3. Working with Rich Domain Entities

```python
# Create different types of entities
customer = flext.Entities.BusinessEntity(
    name="Acme Corporation",
    business_type="Enterprise"
)

order = flext.Entities.AggregateRoot(
    name="Order #12345"
)

service = flext.Entities.ServiceEntity(
    name="Payment Gateway",
    service_type="REST",
    endpoint="https://api.payments.com"
)

print(f"Customer: {customer.name} (Type: {customer.business_type})")
print(f"Order: {order.name}")
print(f"Service: {service.name} at {service.endpoint}")
```

### 4. Using Composable Mixins

```python
# Create entities with specific capabilities
class AdvancedCustomer(
    flext.Entities.BaseEntity,    # Identity and lifecycle
    flext.Mixins.Status,          # Activation/deactivation
    flext.Mixins.Config,          # Configuration management
    flext.Mixins.Metadata         # Flexible metadata storage
):
    pass

# Create and configure the entity
customer = AdvancedCustomer(name="Tech Startup Inc")

# Use mixin capabilities
customer.set_config("payment_terms", "NET30")
customer.set_config("credit_limit", 50000)
customer.add_metadata("industry", "technology")
customer.add_metadata("region", "north_america")
customer.activate()  # From Status mixin

print(f"Customer: {customer.name}")
print(f"Payment Terms: {customer.get_config('payment_terms')}")
print(f"Credit Limit: ${customer.get_config('credit_limit'):,}")
print(f"Industry: {customer.get_metadata('industry')}")
print(f"Active: {customer.active}")
```

### 5. Value Objects for Immutable Data

```python
# Create value objects for structured data
contact_info = flext.ValueObjects.ContactInfo(
    email="john.doe@acme.com",
    phone="+1-555-0123",
    address="123 Business St, Tech City, TC 12345"
)

# Value objects are immutable
print(f"Email: {contact_info.email}")
print(f"Phone: {contact_info.phone}")

# Create business events
event = flext.ValueObjects.FlextDomainEvent(
    event_type="CustomerRegistered",
    aggregate_id=customer.id,
    aggregate_type="Customer",
    event_data={
        "customer_name": customer.name,
        "registration_date": "2024-01-15",
        "initial_credit_limit": 50000
    }
)

print(f"Event: {event.event_type}")
print(f"Aggregate: {event.aggregate_type}")
print(f"Event ID: {event.event_id}")
```

### 6. Domain Events with Aggregate Roots

```python
# Aggregate roots can raise domain events
order = flext.Entities.AggregateRoot(name="Order #12345")

# Raise business events
order.raise_domain_event("OrderCreated", {
    "order_id": "12345",
    "customer_id": customer.id,
    "total_amount": 1250.00,
    "created_by": "john.doe@acme.com"
})

order.raise_domain_event("OrderItemAdded", {
    "item_sku": "LAPTOP-001",
    "quantity": 2,
    "unit_price": 625.00
})

# Check raised events
events = order.get_domain_events()
print(f"Order has {len(events)} domain events:")

for event in events:
    print(f"  - {event.event_type} at {event.occurred_at}")
    print(f"    Data: {event.event_data}")

# Clear events (typically done after publishing)
order.clear_domain_events()
print(f"Events after clearing: {len(order.get_domain_events())}")
```

## Core Concepts

### 1. Hexagonal Architecture

FLEXT implements hexagonal architecture with clear layer separation:

```python
# Domain Layer - Pure business logic
user = flext.Entities.BaseEntity(name="User")     # No external dependencies

# Ports Layer - Define contracts
from flext.ports.secondary.events import FlextEventPublisher
from flext.ports.secondary.external import FlextHttpService

# Adapters Layer - Implement contracts
# (Covered in advanced tutorials)

# Infrastructure Layer - External system integration
# (Covered in infrastructure guides)
```

### 2. Entity Hierarchy

```python
# Base entity - fundamental identity and lifecycle
base = flext.Entities.BaseEntity(name="Base Entity")

# Business entity - domain-specific entities
business = flext.Entities.BusinessEntity(
    name="Business Entity",
    business_type="Service"
)

# Aggregate root - manages domain events
aggregate = flext.Entities.AggregateRoot(name="Aggregate Root")

# Service entity - represents external services
service = flext.Entities.ServiceEntity(
    name="External API",
    service_type="REST"
)

# Timestamped entity - automatic timestamp management
timestamped = flext.Entities.TimestampedEntity(name="Time Tracked")
```

### 3. Type Safety and Validation

```python
# All entities use Pydantic for validation
try:
    # This will validate automatically
    user = flext.Entities.BaseEntity(
        name="Valid User",
        active=True  # Boolean validation
    )
    print("✅ Valid entity created")

except ValueError as e:
    print(f"❌ Validation error: {e}")

# Type hints provide IDE support
def process_entity(entity: flext.Entities.BaseEntity) -> str:
    """Process an entity and return its description."""
    return f"Processing {entity.name} (ID: {entity.id})"

result = process_entity(user)
print(result)
```

### 4. Entity Factory Pattern

```python
# Use factory for complex entity creation
factory = flext.EntityFactory()

# Factory can create entities with predefined configurations
customer_entity = factory.create_entity(
    entity_type="business",
    name="Enterprise Customer",
    configuration={
        "business_type": "Enterprise",
        "credit_limit": 100000,
        "payment_terms": "NET15"
    }
)

print(f"Factory created: {customer_entity.name}")
print(f"Type: {type(customer_entity).__name__}")
```

## Complete Example: Order Management System

Let's build a simple order management system combining all concepts:

```python
from flext import Flx
from datetime import datetime

# Initialize FLEXT
flext = Flx()

# Create a customer with advanced capabilities
class Customer(
    flext.Entities.BusinessEntity,
    flext.Mixins.Status,
    flext.Mixins.Config,
    flext.Mixins.Metadata
):
    pass

# Create customer
customer = Customer(
    name="Acme Electronics",
    business_type="Retailer"
)
customer.set_config("credit_limit", 75000)
customer.set_config("payment_terms", "NET30")
customer.add_metadata("industry", "electronics")
customer.activate()

# Create contact information
contact = flext.ValueObjects.ContactInfo(
    email="orders@acme-electronics.com",
    phone="+1-555-ACME",
    address="456 Commerce Blvd, Business City, BC 67890"
)

# Create an order (aggregate root for events)
order = flext.Entities.AggregateRoot(name="Order #ORD-2024-001")

# Raise domain events for the order
order.raise_domain_event("OrderStarted", {
    "customer_id": customer.id,
    "customer_name": customer.name,
    "order_date": datetime.now().isoformat(),
    "credit_limit": customer.get_config("credit_limit"),
    "payment_terms": customer.get_config("payment_terms")
})

# Add order items
items = [
    {"sku": "LAPTOP-PRO-15", "quantity": 10, "unit_price": 1299.99},
    {"sku": "MOUSE-WIRELESS", "quantity": 15, "unit_price": 79.99},
    {"sku": "KEYBOARD-MECH", "quantity": 12, "unit_price": 149.99}
]

total_amount = 0
for item in items:
    item_total = item["quantity"] * item["unit_price"]
    total_amount += item_total

    order.raise_domain_event("OrderItemAdded", {
        "sku": item["sku"],
        "quantity": item["quantity"],
        "unit_price": item["unit_price"],
        "line_total": item_total
    })

# Finalize the order
order.raise_domain_event("OrderCompleted", {
    "total_amount": total_amount,
    "items_count": len(items),
    "completed_at": datetime.now().isoformat()
})

# Display results
print("=== Order Management System Demo ===")
print(f"Customer: {customer.name} ({customer.business_type})")
print(f"Contact: {contact.email}")
print(f"Order: {order.name}")
print(f"Credit Limit: ${customer.get_config('credit_limit'):,}")
print(f"Payment Terms: {customer.get_config('payment_terms')}")
print(f"Order Total: ${total_amount:,.2f}")
print(f"Active: {customer.active}")

print("\n=== Domain Events ===")
events = order.get_domain_events()
for i, event in enumerate(events, 1):
    print(f"{i}. {event.event_type}")
    print(f"   ID: {event.event_id}")
    print(f"   Time: {event.occurred_at}")
    if "total_amount" in event.event_data:
        print(f"   Amount: ${event.event_data['total_amount']:,.2f}")
```

**Expected Output:**

```
=== Order Management System Demo ===
Customer: Acme Electronics (Retailer)
Contact: orders@acme-electronics.com
Order: Order #ORD-2024-001
Credit Limit: $75,000
Payment Terms: NET30
Order Total: $16,299.73
Active: True

=== Domain Events ===
1. OrderStarted
   ID: evt_abc123def456
   Time: 2024-01-15T10:30:00Z

2. OrderItemAdded
   ID: evt_def456ghi789
   Time: 2024-01-15T10:30:01Z

3. OrderItemAdded
   ID: evt_ghi789jkl012
   Time: 2024-01-15T10:30:02Z

4. OrderItemAdded
   ID: evt_jkl012mno345
   Time: 2024-01-15T10:30:03Z

5. OrderCompleted
   ID: evt_mno345pqr678
   Time: 2024-01-15T10:30:04Z
   Amount: $16,299.73
```

## Next Steps

Now that you understand the basics:

1. **[First Pipeline Tutorial](first-pipeline.md)** - Build a complete application with ports and adapters
2. **[Architecture Guide](../INFRASTRUCTURE_ARCHITECTURE.md)** - Understand the hexagonal architecture implementation
3. **[API Reference](../api-reference/)** - Explore all available components and methods
4. **[Testing Guide](../guides/testing.md)** - Learn how to test your FLEXT applications
5. **[Examples](../examples/)** - See more complex real-world scenarios

## Helpful Resources

- **Type Safety**: All FLEXT components are fully typed for excellent IDE support
- **Validation**: Pydantic models provide automatic data validation
- **Events**: Use domain events to capture business occurrences
- **Mixins**: Compose functionality with mixins for flexible entity design
- **Architecture**: Follow hexagonal architecture principles for maintainable code

---

**🎉 Congratulations! You've created your first FLEXT entities and learned the core concepts. Ready to build enterprise applications!**
