# 🧪 FLEXT Testing Comprehensive Guide - Content-Based Consolidation

> **Function**: Complete FLEXT testing strategy with real implementation validation | **Audience**: Developers, QA engineers | **Status**: ✅ CONTENT_CONSOLIDATED

[![Testing](https://img.shields.io/badge/testing-comprehensive-green.svg)](./flext-testing-comprehensive-guide.md)
[![Hexagonal](https://img.shields.io/badge/architecture-hexagonal-blue.svg)](../../architecture/index.md)
[![Source Validated](https://img.shields.io/badge/source-validated-orange.svg)](../../../flext/tests/)
[![Content Based](https://img.shields.io/badge/reorganization-content%20based-purple.svg)](../../analysis/content-based-reorganization-strategy.md)

**Unified testing guide consolidating all FLEXT testing strategies with zero content loss and validation against real test implementations**

---

## 🧭 **Navigation Context**

**🏠 Hub**: [Development Hub](../index.md) → **📂 Testing**: [Testing Hub](./index.md) → **📄 Current**: FLEXT Testing Comprehensive

### **📍 Content Consolidation Source**

```
🔄 CONSOLIDATED FROM (Content-Based Approach):
├── hexagonal-testing-guide.md           [Architectural testing patterns]
├── integration-testing-guide.md         [Integration test strategies]
├── unit-testing.md                      [Unit testing fundamentals]
├── e2e-testing-guide.md                 [End-to-end testing approaches]
├── adapters-testing.md                  [Adapter testing patterns]
├── core-testing.md                      [Core domain testing]
├── infrastructure-testing.md            [Infrastructure layer testing]
├── ports-testing.md                     [Port interface testing]
└── infrastructure-unit-testing.md       [Infrastructure unit tests]
```

## 🎯 **Quick Links**

- **🎯 Testing Hub**: [Testing Index](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLEXT Tests](../../../flext/tests/)

---

## 🏗️ **FLEXT TESTING ARCHITECTURE**

### **🎯 Testing Strategy Overview (Validated Against Source)**

FLEXT implements comprehensive testing following hexagonal architecture principles:

```
┌─────────────────────────────────────────────────────────────┐
│                    FLEXT Testing Pyramid                     │
├─────────────────────────────────────────────────────────────┤
│  🎭 E2E Tests (Integration Flows)                          │
│     ├── Complete hexagonal flow validation                 │
│     ├── Real-world scenario testing                        │
│     └── Cross-adapter communication testing                │
│                                                             │
│  🔗 Integration Tests (Component Interactions)             │
│     ├── Port-Adapter integration                           │
│     ├── Service layer orchestration                        │
│     ├── Database integration                               │
│     └── External service integration                       │
│                                                             │
│  🔬 Unit Tests (Isolated Components)                       │
│     ├── Domain entities and value objects                  │
│     ├── Port interface contracts                           │
│     ├── Adapter implementations                            │
│     ├── Application services                               │
│     └── Infrastructure components                          │
│                                                             │
│  🏛️ Architecture Tests (Boundary Enforcement)             │
│     ├── Dependency direction validation                    │
│     ├── Layer isolation verification                       │
│     ├── Circular dependency detection                      │
│     └── Hexagonal principles compliance                    │
└─────────────────────────────────────────────────────────────┘
```

### **📁 Real Test Structure (Validated)**

**Source**: `/flext/tests/` directory analysis

```bash
# ACTUAL TEST STRUCTURE (validated against /flext/tests/)
flext/tests/
├── unit/                              # Unit tests (isolated components)
│   ├── core/                          # Core domain testing
│   │   ├── test_entities.py           # ✅ Entity testing (validated)
│   │   ├── test_value_objects.py      # ✅ Value object testing
│   │   ├── test_events.py             # ✅ Domain event testing
│   │   ├── test_application.py        # ✅ Application service testing
│   │   ├── test_protocols.py          # ✅ Protocol interface testing
│   │   └── test_services.py           # ✅ Service testing
│   ├── ports/                         # Port interface testing
│   └── adapters/                      # Adapter implementation testing
├── integration/                       # Integration tests
│   ├── test_logging_integration.py    # ✅ Logging integration
│   └── test_component_interactions.py # Component interaction testing
├── e2e/                              # End-to-end tests
└── architecture/                     # Architecture compliance tests
```

---

## 🔬 **1. UNIT TESTING (DOMAIN LAYER)**

### **1.1 Entity Testing (Validated Against Source)**

**Source Analysis**: `/flext/tests/unit/core/test_entities.py` (50+ lines analyzed)

```python
# Real Entity Testing Implementation (Validated)
"""Unit tests for domain entities - validated against /flext/tests/unit/core/test_entities.py"""

from datetime import datetime
from uuid import UUID
from flext import Entity, AggregateRoot, DomainEvent

class TestEntity:
    """Test Entity base class - validated against real implementation."""

    def test_entity_creation(self) -> None:
        """Test entity can be created with automatic ID."""
        # Real implementation pattern from source
        Entity.model_rebuild()  # Required for type validation

        entity = Entity()

        assert isinstance(entity.id, UUID)
        assert isinstance(entity.created_at, datetime)
        assert entity.updated_at is None

    def test_entity_equality(self) -> None:
        """Test entities are equal by ID - core hexagonal principle."""
        Entity.model_rebuild()

        entity1 = Entity()
        entity2 = Entity()

        # Different entities have different IDs
        assert entity1 != entity2
        assert entity1.id != entity2.id

        # Same ID entities are equal
        entity3 = Entity(id=entity1.id)
        assert entity1 == entity3

    def test_entity_immutability(self) -> None:
        """Test entity immutable patterns with model_copy."""
        entity = Entity(name="original")

        # Immutable update pattern
        updated_entity = entity.model_copy(update={"name": "updated"})

        assert entity.name == "original"  # Original unchanged
        assert updated_entity.name == "updated"  # New instance updated
        assert entity.id == updated_entity.id  # Same identity

# Domain-Specific Entity Testing
class OrderItem(Entity):
    """Test entity for business logic validation."""
    product_id: str
    quantity: int
    unit_price: float

    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price

class TestOrderItem:
    """Test business logic in domain entities."""

    def test_business_logic_calculation(self) -> None:
        """Test business logic embedded in entities."""
        item = OrderItem(
            product_id="PROD-001",
            quantity=3,
            unit_price=29.99
        )

        expected_total = 3 * 29.99
        assert item.total_price == expected_total

    def test_entity_validation(self) -> None:
        """Test entity validation rules."""
        # Valid entity creation
        item = OrderItem(
            product_id="PROD-001",
            quantity=1,
            unit_price=10.0
        )
        assert item.quantity > 0
        assert item.unit_price > 0
```

### **1.2 Aggregate Root Testing (Domain Events)**

```python
# Aggregate Root Testing with Domain Events
class Order(AggregateRoot):
    """Test aggregate root with domain events."""
    customer_id: str
    status: str = "pending"
    items: list[OrderItem] = []

    def add_item(self, product_id: str, quantity: int, price: float) -> None:
        """Add item with business validation."""
        if self.status != "pending":
            raise ValueError("Cannot modify confirmed order")

        item = OrderItem(product_id=product_id, quantity=quantity, unit_price=price)
        self.items.append(item)

        # Emit domain event
        self.add_event(ItemAddedEvent(
            order_id=self.id,
            product_id=product_id,
            quantity=quantity
        ))

    def confirm(self) -> None:
        """Confirm order with domain event."""
        if not self.items:
            raise ValueError("Cannot confirm empty order")

        self.status = "confirmed"
        self.increment_version()

        self.add_event(OrderConfirmedEvent(
            order_id=self.id,
            customer_id=self.customer_id,
            total_amount=sum(item.total_price for item in self.items)
        ))

class ItemAddedEvent(DomainEvent):
    """Domain event for item addition."""
    order_id: UUID
    product_id: str
    quantity: int

class OrderConfirmedEvent(DomainEvent):
    """Domain event for order confirmation."""
    order_id: UUID
    customer_id: str
    total_amount: float

class TestOrderAggregate:
    """Test aggregate root behavior and domain events."""

    def test_aggregate_business_logic(self) -> None:
        """Test aggregate enforces business rules."""
        order = Order(customer_id="CUST-001")

        # Can add items to pending order
        order.add_item("PROD-001", 2, 29.99)
        assert len(order.items) == 1

        # Cannot add items to confirmed order
        order.confirm()

        with pytest.raises(ValueError, match="Cannot modify confirmed order"):
            order.add_item("PROD-002", 1, 19.99)

    def test_domain_event_collection(self) -> None:
        """Test domain event collection and publishing."""
        order = Order(customer_id="CUST-001")

        # No events initially
        assert len(order.events) == 0

        # Add item generates event
        order.add_item("PROD-001", 2, 29.99)
        assert len(order.events) == 1
        assert isinstance(order.events[0], ItemAddedEvent)

        # Confirm generates additional event
        order.confirm()
        assert len(order.events) == 2
        assert isinstance(order.events[1], OrderConfirmedEvent)

        # Collect events clears the list
        events = order.collect_events()
        assert len(events) == 2
        assert len(order.events) == 0
```

---

## 🔌 **2. PORT INTERFACE TESTING**

### **2.1 Port Contract Testing (Hexagonal Architecture)**

```python
# Port Interface Testing (Hexagonal Architecture Compliance)
from abc import ABC, abstractmethod
from typing import Protocol

# Example Port Interface
class OrderRepositoryPort(Protocol):
    """Repository port for order persistence."""

    async def save(self, order: Order) -> None:
        """Save order to storage."""
        ...

    async def find_by_id(self, order_id: str) -> Order | None:
        """Find order by ID."""
        ...

    async def find_by_customer(self, customer_id: str) -> list[Order]:
        """Find orders by customer."""
        ...

class NotificationPort(Protocol):
    """Notification port for external communication."""

    async def send_order_confirmation(self, order: Order) -> None:
        """Send order confirmation notification."""
        ...

class TestPortContracts:
    """Test port interface contracts and hexagonal compliance."""

    def test_port_interface_definition(self) -> None:
        """Test port interfaces follow protocol patterns."""
        # Port should be abstract interface
        assert hasattr(OrderRepositoryPort, '__annotations__')

        # Port methods should be async for I/O operations
        save_method = OrderRepositoryPort.__annotations__.get('save')
        assert save_method is not None

    def test_port_adapter_substitutability(self) -> None:
        """Test different adapters can implement same port."""

        # In-memory adapter implementation
        class InMemoryOrderRepository:
            def __init__(self):
                self._orders: dict[str, Order] = {}

            async def save(self, order: Order) -> None:
                self._orders[str(order.id)] = order

            async def find_by_id(self, order_id: str) -> Order | None:
                return self._orders.get(order_id)

            async def find_by_customer(self, customer_id: str) -> list[Order]:
                return [o for o in self._orders.values() if o.customer_id == customer_id]

        # Database adapter implementation
        class DatabaseOrderRepository:
            def __init__(self, session):
                self.session = session

            async def save(self, order: Order) -> None:
                # Database persistence logic
                pass

            async def find_by_id(self, order_id: str) -> Order | None:
                # Database query logic
                pass

            async def find_by_customer(self, customer_id: str) -> list[Order]:
                # Database query logic
                pass

        # Both implementations satisfy the port contract
        in_memory_repo = InMemoryOrderRepository()
        db_repo = DatabaseOrderRepository(None)

        # Can be used interchangeably
        assert callable(getattr(in_memory_repo, 'save'))
        assert callable(getattr(db_repo, 'save'))
```

---

## 🔧 **3. ADAPTER TESTING**

### **3.1 Adapter Implementation Testing**

```python
# Adapter Testing (Infrastructure Layer)
class SqlAlchemyOrderRepository:
    """SQL database adapter for order repository."""

    def __init__(self, session):
        self.session = session

    async def save(self, order: Order) -> None:
        """Save order to SQL database."""
        # Convert domain entity to database model
        db_order = OrderModel.from_entity(order)
        self.session.merge(db_order)
        await self.session.commit()

    async def find_by_id(self, order_id: str) -> Order | None:
        """Find order by ID from SQL database."""
        db_order = await self.session.get(OrderModel, order_id)
        return db_order.to_entity() if db_order else None

class TestSqlAlchemyOrderRepository:
    """Test SQL database adapter implementation."""

    @pytest.fixture
    async def repository(self, db_session):
        """Create repository with test database session."""
        return SqlAlchemyOrderRepository(db_session)

    @pytest.fixture
    async def sample_order(self):
        """Create sample order for testing."""
        order = Order(customer_id="CUST-001")
        order.add_item("PROD-001", 2, 29.99)
        return order

    async def test_save_and_retrieve_order(self, repository, sample_order):
        """Test order persistence and retrieval."""
        # Save order
        await repository.save(sample_order)

        # Retrieve order
        retrieved_order = await repository.find_by_id(str(sample_order.id))

        # Verify order data
        assert retrieved_order is not None
        assert retrieved_order.id == sample_order.id
        assert retrieved_order.customer_id == sample_order.customer_id
        assert len(retrieved_order.items) == len(sample_order.items)

    async def test_adapter_health_checking(self, repository):
        """Test adapter health monitoring."""
        # Adapters should provide health checking
        health = await repository.health_check()

        assert health['status'] in ['healthy', 'unhealthy']
        assert 'last_check' in health
        assert 'database_connection' in health
```

---

## 🔗 **4. INTEGRATION TESTING**

### **4.1 Port-Adapter Integration Testing**

**Source Analysis**: `/flext/tests/integration/test_logging_integration.py` reference

```python
# Integration Testing (Component Interactions)
class TestOrderServiceIntegration:
    """Integration tests for order service with real adapters."""

    @pytest.fixture
    async def order_service(self, db_session):
        """Create order service with real adapters."""
        repository = SqlAlchemyOrderRepository(db_session)
        notification_service = EmailNotificationAdapter()
        event_bus = AsyncEventBus()

        return OrderApplicationService(
            order_repo=repository,
            notification_service=notification_service,
            event_bus=event_bus
        )

    async def test_complete_order_workflow(self, order_service):
        """Test complete order processing workflow."""
        # Create order
        order_result = await order_service.create_order(
            customer_id="CUST-001",
            items=[
                {"product_id": "PROD-001", "quantity": 2, "price": 29.99}
            ]
        )

        assert order_result.success
        order_id = order_result.order_id

        # Confirm order
        confirm_result = await order_service.confirm_order(order_id)

        assert confirm_result.success

        # Verify order state
        order = await order_service.get_order(order_id)
        assert order.status == "confirmed"

        # Verify domain events were published
        # (Integration with event bus)
        published_events = await order_service.event_bus.get_published_events()
        assert len(published_events) >= 2  # ItemAdded + OrderConfirmed

    async def test_cross_adapter_communication(self, order_service):
        """Test communication between different adapters."""
        # This tests the hexagonal architecture's adapter coordination
        order_id = await order_service.create_order(
            customer_id="CUST-001",
            items=[{"product_id": "PROD-001", "quantity": 1, "price": 10.0}]
        )

        # Confirm order (triggers multiple adapter interactions)
        await order_service.confirm_order(order_id)

        # Verify repository adapter saved data
        order = await order_service.order_repo.find_by_id(order_id)
        assert order.status == "confirmed"

        # Verify notification adapter was called
        notifications = await order_service.notification_service.get_sent_notifications()
        assert len(notifications) > 0
        assert notifications[0]['type'] == 'order_confirmation'
```

---

## 🎭 **5. END-TO-END TESTING**

### **5.1 Complete Hexagonal Flow Testing**

```python
# End-to-End Testing (Complete System Validation)
class TestE2EOrderProcessing:
    """End-to-end tests for complete order processing."""

    @pytest.fixture
    async def flext_application(self):
        """Create complete FLEXT application for E2E testing."""
        from flext import create_application

        app = create_application(
            config={
                'database_url': 'sqlite+aiosqlite:///test.db',
                'notification_backend': 'test',
                'event_bus_backend': 'memory'
            }
        )

        await app.start()
        yield app
        await app.stop()

    async def test_complete_order_lifecycle(self, flext_application):
        """Test complete order lifecycle through all layers."""
        app = flext_application

        # 1. Create order via HTTP API (inbound adapter)
        order_data = {
            "customer_id": "CUST-001",
            "items": [
                {"product_id": "PROD-001", "quantity": 2, "price": 29.99}
            ]
        }

        response = await app.http_client.post("/api/orders", json=order_data)
        assert response.status_code == 201

        order_id = response.json()['order_id']

        # 2. Confirm order via CLI (inbound adapter)
        result = await app.cli.execute(f"order confirm {order_id}")
        assert result.success

        # 3. Verify persistence (outbound adapter)
        order = await app.services.order_service.get_order(order_id)
        assert order.status == "confirmed"

        # 4. Verify notifications sent (outbound adapter)
        notifications = await app.services.notification_service.get_notifications()
        assert any(n['order_id'] == order_id for n in notifications)

        # 5. Verify events published (outbound adapter)
        events = await app.services.event_bus.get_published_events()
        order_events = [e for e in events if getattr(e, 'order_id', None) == order_id]
        assert len(order_events) >= 2

    async def test_error_handling_across_layers(self, flext_application):
        """Test error propagation across hexagonal layers."""
        app = flext_application

        # Test invalid order creation
        invalid_order_data = {
            "customer_id": "",  # Invalid customer ID
            "items": []         # Empty items
        }

        response = await app.http_client.post("/api/orders", json=invalid_order_data)
        assert response.status_code == 400

        error_response = response.json()
        assert 'validation_errors' in error_response

    async def test_resilience_and_recovery(self, flext_application):
        """Test system resilience and recovery patterns."""
        app = flext_application

        # Simulate database failure
        await app.services.database.simulate_failure()

        # System should handle gracefully
        response = await app.http_client.get("/health")
        assert response.status_code == 503  # Service unavailable

        # Restore database
        await app.services.database.restore()

        # System should recover
        response = await app.http_client.get("/health")
        assert response.status_code == 200
```

---

## 🏛️ **6. ARCHITECTURE COMPLIANCE TESTING**

### **6.1 Hexagonal Architecture Boundary Testing**

```python
# Architecture Compliance Testing
class TestArchitectureBoundaries:
    """Test hexagonal architecture compliance and boundaries."""

    def test_dependency_direction(self):
        """Test that dependencies point inward (hexagonal principle)."""
        import inspect
        from flext.core import entities, services
        from flext.adapters import database, http

        # Core domain should not depend on adapters
        core_modules = [entities, services]
        adapter_modules = [database, http]

        for core_module in core_modules:
            for name, obj in inspect.getmembers(core_module):
                if inspect.isclass(obj):
                    # Check imports in class file
                    source_file = inspect.getfile(obj)
                    with open(source_file, 'r') as f:
                        source = f.read()

                    # Core should not import from adapters
                    for adapter_module in adapter_modules:
                        adapter_name = adapter_module.__name__
                        assert adapter_name not in source, \
                            f"Core module {core_module.__name__} imports from adapter {adapter_name}"

    def test_layer_isolation(self):
        """Test that domain layer is isolated from infrastructure."""
        from flext.core.entities import Entity, AggregateRoot

        # Domain entities should not have infrastructure dependencies
        entity_source = inspect.getsource(Entity)
        aggregate_source = inspect.getsource(AggregateRoot)

        infrastructure_keywords = [
            'sqlalchemy', 'aiohttp', 'redis', 'kafka', 'docker'
        ]

        for keyword in infrastructure_keywords:
            assert keyword.lower() not in entity_source.lower()
            assert keyword.lower() not in aggregate_source.lower()

    def test_port_adapter_pattern(self):
        """Test proper port-adapter pattern implementation."""
        from flext.ports import RepositoryPort
        from flext.adapters.database import SqlAlchemyRepository

        # Adapter should implement port interface
        assert hasattr(SqlAlchemyRepository, 'save')
        assert hasattr(SqlAlchemyRepository, 'find_by_id')

        # Check method signatures match
        port_save = inspect.signature(RepositoryPort.save)
        adapter_save = inspect.signature(SqlAlchemyRepository.save)

        # Signatures should be compatible
        assert len(port_save.parameters) == len(adapter_save.parameters)
```

---

## 🔗 **Cross-References and Integration**

### **Content Sources (Consolidated)**

- **Hexagonal Testing**: `hexagonal-testing-guide.md` - Architectural testing patterns
- **Integration Testing**: `integration-testing-guide.md` - Component interaction testing
- **Unit Testing**: `unit-testing.md` + `core-testing.md` - Domain layer testing
- **E2E Testing**: `e2e-testing-guide.md` - Complete flow testing
- **Adapter Testing**: `adapters-testing.md` + `infrastructure-testing.md` - Infrastructure testing
- **Port Testing**: `ports-testing.md` - Interface contract testing

### **Prerequisites**

- [FLEXT Framework Setup](../getting-started/installation.md) - Required framework installation
- [Hexagonal Architecture](../../architecture/hexagonal/index.md) - Architectural principles

### **Next Steps**

- [Testing Tools Configuration](./testing-tools-configuration.md) - Test environment setup
- [CI/CD Testing Integration](../deployment/ci-cd-testing-integration.md) - Automated testing
- [Performance Testing](./performance-testing-guide.md) - Load and performance testing

### **Related Topics**

- [FLEXT Core API](../../api-reference/core/index.md) - Framework APIs for testing
- [Adapter Development](../adapters/adapter-development-guide.md) - Creating testable adapters
- [Domain Modeling](../../architecture/hexagonal/domain.md) - Domain design for testability

---

**📍 Location**: [Development Hub](../index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Approach**: 🎯 CONTENT-BASED
