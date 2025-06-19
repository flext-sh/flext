# Application Layer - Architecture

> **Function**: Application layer orchestration and use case implementation | **Audience**: Application architects, Senior developers | **Status**: Stable

[![Layer](https://img.shields.io/badge/layer-application-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-orange.svg)](../index.md)
[![Use Cases](https://img.shields.io/badge/patterns-use%20cases-green.svg)](./core-domain-layer.md)

**Complete application layer implementation guide for orchestrating use cases and coordinating domain objects in FLX Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture](../index.md) → **📂 Layers**: [Layers Hub](./index.md) → **📄 Current**: Application Layer

### **📍 Learning Path Position**

```
[Core Domain Layer](./core-domain-layer.md) → **[APPLICATION LAYER]** → [Infrastructure Layer](../infrastructure/index.md)
```

## 🎯 **Quick Links**

- **📂 Layers Hub**: [Architecture Layers](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [Domain Layer](./core-domain-layer.md), [Infrastructure](../infrastructure/index.md)

---

## 📋 **Overview**

The Application Layer orchestrates data flow between the presentation layer (adapters) and the domain layer, implementing use cases, application-specific business rules, and coordinating transactions.

## 📦 **Components**

- `bootstrap.py` - Application initialization and setup
- `container.py` - Dependency injection container
- `services.py` - Application service implementations

## 🎯 **Purpose**

The Application Layer orchestrates data flow between the presentation layer (adapters) and the domain layer. It:

- Implements use cases and application flows
- Manages transactions and consistency
- Coordinates multiple domain objects
- Handles application-specific business rules

## 🏗️ **Architecture**

This layer follows Clean Architecture pattern, depends on the domain layer, but remains independent of infrastructure concerns. Uses dependency injection to maintain low coupling.

## 🏗️ **Application Layer Implementation**

### **Service Layer Pattern**

```python
from flx.application.services import ApplicationService
from flx.core.domain import Entity, AggregateRoot

class OrderApplicationService(ApplicationService):
    """Application service orchestrating order use cases."""

    def __init__(
        self,
        order_repository: OrderRepository,
        customer_repository: CustomerRepository,
        event_publisher: EventPublisher
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.event_publisher = event_publisher

    async def create_order(self, command: CreateOrderCommand) -> OrderResult:
        """Use case: Create new order with business validation."""
        # Coordinate domain objects
        customer = await self.customer_repository.find_by_id(command.customer_id)
        if not customer.can_place_order():
            raise DomainException("Customer cannot place orders")

        # Create domain aggregate
        order = Order.create(
            customer_id=command.customer_id,
            items=command.items
        )

        # Persist and publish events
        await self.order_repository.save(order)
        await self.event_publisher.publish_domain_events(order.events)

        return OrderResult(order_id=order.id, status="created")
```

### **Transaction Management**

```python
from flx.application.transaction import TransactionManager

class OrderApplicationService(ApplicationService):
    async def process_order(self, command: ProcessOrderCommand) -> None:
        """Use case with transaction coordination."""
        async with TransactionManager() as tx:
            # Multiple operations in single transaction
            order = await self.order_repository.find_by_id(command.order_id)
            inventory = await self.inventory_repository.reserve_items(order.items)
            payment = await self.payment_service.charge(order.total)

            # All succeed or all fail
            order.mark_as_processed()
            await self.order_repository.save(order)

            # Events published after successful transaction
            await self.event_publisher.publish(order.events)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Hub](../index.md) - Understanding hexagonal architecture principles and layer separation essential for proper application service design
- [Core Domain Layer](./core-domain-layer.md) - Domain entities and business logic that application layer orchestrates, including aggregates, events, and repositories
- [Ports and Adapters](../ports/index.md) - Interface contracts that application layer implements to maintain dependency inversion and clean architecture

### **Next Steps**

- [Infrastructure Layer](../infrastructure/index.md) - Infrastructure services that support application layer including database, messaging, and external system adapters
- [Adapter Implementation](../adapters/index.md) - Adapters that connect to application services providing concrete implementations of port interfaces
- [Testing Application Layer](../../development/testing/index.md) - Testing strategies for application services including unit, integration, and acceptance testing patterns

### **Related Topics**

- [Use Case Implementation](../../guides/development/plugin-development-guide.md) - Detailed use case implementation patterns for complex business workflows and user interactions
- [Dependency Injection](../../development/architecture/index.md) - DI patterns used in application layer for managing service dependencies and configuration
- [Event-Driven Architecture](../patterns/event-sourcing-implementation.md) - Event handling in application layer for domain event publishing and subscription patterns

---

## 🆘 **Troubleshooting**

### **Common Application Layer Issues**

**Transaction Problems**:

```python
# Check transaction scope
async with TransactionManager() as tx:
    # All operations must be within transaction scope
    await repository.save(entity)
```

**Service Dependencies**:

```python
# Ensure proper dependency injection
service = OrderApplicationService(
    order_repo=container.get("order_repository"),
    event_publisher=container.get("event_publisher")
)
```

---

## 🆘 **Troubleshooting**

### **Common Application Layer Issues**

**Transaction Problems**:

```python
# Issue: Transaction scope issues with async operations
# Solution: Proper transaction boundary management
class OrderApplicationService:
    async def create_order(self, command: CreateOrderCommand) -> OrderResult:
        async with self.transaction_manager.begin() as tx:
            try:
                # All operations within transaction scope
                customer = await self.customer_repo.find_by_id(command.customer_id)
                order = Order.create(customer_id=customer.id, items=command.items)

                await self.order_repo.save(order)
                await tx.commit()

                # Events published after successful transaction
                await self.event_bus.publish_batch(order.collect_events())

                return OrderResult(order_id=order.id)
            except Exception:
                await tx.rollback()
                raise
```

**Service Dependencies**:

```python
# Issue: Circular dependency between application services
# Solution: Extract shared logic to domain services or use events
class UserApplicationService:
    def __init__(
        self,
        user_repo: UserRepository,
        event_bus: EventBus,  # Use events instead of direct service dependencies
        domain_service: UserDomainService  # Move shared logic to domain
    ):
        self.user_repo = user_repo
        self.event_bus = event_bus
        self.domain_service = domain_service
```

**Use Case Coordination Issues**:

```python
# Issue: Complex use case with multiple aggregates
# Solution: Use process managers or saga patterns
class OrderFulfillmentProcessManager:
    async def handle_order_placed(self, event: OrderPlacedEvent) -> None:
        # Coordinate multiple bounded contexts
        await self.inventory_service.reserve_items(event.order_id)
        await self.payment_service.process_payment(event.payment_info)
        await self.shipping_service.schedule_delivery(event.shipping_address)
```

**Event Publishing Failures**:

```python
# Issue: Domain events not being published
# Solution: Implement outbox pattern for reliable event publishing
class ReliableEventPublisher:
    async def publish_events(self, aggregate: AggregateRoot) -> None:
        events = aggregate.collect_events()

        # Store events in outbox table within same transaction
        async with self.transaction_manager.begin() as tx:
            await self.aggregate_repo.save(aggregate)
            await self.outbox_repo.store_events(events)
            await tx.commit()

        # Publish events asynchronously
        await self.event_publisher.publish_batch(events)
```

---

**📂 Hub**: [Architecture Layers](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
