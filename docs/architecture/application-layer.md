# Application Layer - Architecture

> **Function**: Application service orchestration and use case implementation | **Audience**: Application developers, architects | **Status**: Stable

[![Architecture](https://img.shields.io/badge/layer-application-purple.svg)](./index.md)
[![Domain](https://img.shields.io/badge/depends_on-domain_layer-blue.svg)](./core-domain-layer.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT%200.4.0-orange.svg)](../index.md)

**Orchestration layer implementing application use cases and coordinating domain objects in the FLEXT Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Architecture Hub](./index.md) → **📄 Current**: Application Layer

### **📍 Learning Path Position**

```
[Core Domain Layer](./core-domain-layer.md) → **[Application Layer]** → [Infrastructure Layer](./infrastructure/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Architecture Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Related**: [Domain Services](./patterns/advanced-patterns-hub.md)

---

## 📋 **Overview**

The Application Layer orchestrates the flow between presentation (adapters) and domain layers, implementing application-specific business rules and coordinating transactions. It provides the use case implementations that drive the application's behavior.

### **Key Responsibilities**

- **Use Case Implementation**: Orchestrates domain objects to fulfill business requirements
- **Transaction Management**: Ensures data consistency across operations
- **Application Flow**: Coordinates multi-step business processes
- **Service Composition**: Combines domain services for complex operations
- **Cross-Cutting Concerns**: Handles logging, validation, and security at application level

### **Prerequisites**

- Understanding of [Core Domain Layer](./core-domain-layer.md)
- Knowledge of [Hexagonal Architecture](./hexagonal-architecture-hub.md)
- Familiarity with dependency injection patterns

---

## 📚 **Architecture**

### **Layer Dependencies**

Based on actual implementation in `/flext/src/flext/application/`:

```python
# Application layer depends ONLY on domain layer
from flext.domain.entities import Customer, Order
from flext.domain.services import PricingService
from flext.domain.repositories import CustomerRepository

# NO infrastructure imports allowed
# ❌ from flext.infra.database import DatabaseConnection
# ❌ from flext.adapters.http import HttpClient
```

### **Core Components**

#### **Application Services**

```python
from flext.application.services import ApplicationService
from flext.domain.repositories import Repository

class OrderApplicationService(ApplicationService):
    """Orchestrates order-related use cases."""

    def __init__(self,
                 order_repo: Repository[Order],
                 customer_repo: Repository[Customer],
                 pricing_service: PricingService):
        self.order_repo = order_repo
        self.customer_repo = customer_repo
        self.pricing_service = pricing_service

    async def create_order(self, customer_id: str, items: List[OrderItem]) -> str:
        """Use case: Create new order with pricing calculation."""
        # 1. Load customer
        customer = await self.customer_repo.get(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)

        # 2. Calculate pricing
        total_price = await self.pricing_service.calculate_total(
            customer.tier,
            items
        )

        # 3. Create order
        order = Order.create(
            customer_id=customer_id,
            items=items,
            total_price=total_price
        )

        # 4. Save order
        await self.order_repo.save(order)

        return order.id
```

#### **Dependency Injection Container**

```python
from flext.application.container import ApplicationContainer

class ApplicationContainer:
    """Manages application service dependencies."""

    def __init__(self):
        self._services = {}
        self._factories = {}

    def register_factory(self, service_type: Type[T], factory: Callable[[], T]):
        """Register service factory for lazy instantiation."""
        self._factories[service_type] = factory

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve service with dependencies."""
        if service_type not in self._services:
            factory = self._factories.get(service_type)
            if not factory:
                raise ServiceNotRegisteredError(service_type)
            self._services[service_type] = factory()
        return self._services[service_type]
```

#### **Bootstrap Process**

```python
from flext.application.bootstrap import ApplicationBootstrap

class ApplicationBootstrap:
    """Initializes application with all dependencies."""

    async def bootstrap(self, config: ApplicationConfig) -> ApplicationContainer:
        container = ApplicationContainer()

        # Register repositories (interfaces only)
        container.register_factory(
            CustomerRepository,
            lambda: self._create_customer_repository(config)
        )

        # Register domain services
        container.register_factory(
            PricingService,
            lambda: PricingService(
                pricing_rules=config.pricing_rules
            )
        )

        # Register application services
        container.register_factory(
            OrderApplicationService,
            lambda: OrderApplicationService(
                order_repo=container.resolve(OrderRepository),
                customer_repo=container.resolve(CustomerRepository),
                pricing_service=container.resolve(PricingService)
            )
        )

        return container
```

---

## 🔧 **Implementation Patterns**

### **Command Pattern for Use Cases**

```python
from flext.application.commands import Command, CommandHandler

class CreateOrderCommand(Command):
    """Command representing order creation request."""
    customer_id: str
    items: List[OrderItem]

class CreateOrderHandler(CommandHandler[CreateOrderCommand, str]):
    """Handles order creation commands."""

    def __init__(self, order_service: OrderApplicationService):
        self.order_service = order_service

    async def handle(self, command: CreateOrderCommand) -> str:
        return await self.order_service.create_order(
            command.customer_id,
            command.items
        )
```

### **Transaction Management**

```python
from flext.application.transactions import TransactionManager

class TransactionalApplicationService:
    """Base class for transactional services."""

    def __init__(self, transaction_manager: TransactionManager):
        self._tx_manager = transaction_manager

    async def execute_in_transaction(self, operation: Callable):
        """Execute operation within transaction boundaries."""
        async with self._tx_manager.begin() as transaction:
            try:
                result = await operation()
                await transaction.commit()
                return result
            except Exception:
                await transaction.rollback()
                raise
```

### **Query Services**

```python
from flext.application.queries import QueryService

class OrderQueryService(QueryService):
    """Read-only queries for orders."""

    def __init__(self, query_executor: QueryExecutor):
        self.query_executor = query_executor

    async def get_customer_orders(self, customer_id: str) -> List[OrderDTO]:
        """Get all orders for a customer."""
        query = """
            SELECT o.id, o.created_at, o.total_price, o.status
            FROM orders o
            WHERE o.customer_id = :customer_id
            ORDER BY o.created_at DESC
        """

        results = await self.query_executor.fetch_all(
            query,
            {"customer_id": customer_id}
        )

        return [OrderDTO.from_row(row) for row in results]
```

---

## 🧪 **Testing Application Services**

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_repositories():
    return {
        "order_repo": Mock(spec=OrderRepository),
        "customer_repo": Mock(spec=CustomerRepository)
    }

async def test_create_order_success(mock_repositories):
    # Arrange
    customer = Customer(id="123", tier="gold")
    mock_repositories["customer_repo"].get = AsyncMock(return_value=customer)
    mock_repositories["order_repo"].save = AsyncMock()

    pricing_service = Mock(spec=PricingService)
    pricing_service.calculate_total = AsyncMock(return_value=99.99)

    service = OrderApplicationService(
        order_repo=mock_repositories["order_repo"],
        customer_repo=mock_repositories["customer_repo"],
        pricing_service=pricing_service
    )

    # Act
    order_id = await service.create_order("123", [OrderItem(...)])

    # Assert
    assert order_id is not None
    mock_repositories["order_repo"].save.assert_called_once()
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Core Domain Layer](./core-domain-layer.md) - Domain entities and business rules
- [Hexagonal Architecture](./hexagonal-architecture-hub.md) - Overall architecture pattern

### **Next Steps**

- [Infrastructure Layer](./infrastructure/index.md) - Technical implementation details
- [Ports and Adapters](./ports/index.md) - Interface definitions

### **Related Topics**

- [Domain Services](./patterns/domain-services.md) - Business logic services
- [CQRS Pattern](./patterns/cqrs.md) - Command Query Responsibility Segregation
- [Event Sourcing](./patterns/event-sourcing.md) - Event-driven state management

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Circular Dependencies**

```python
# Problem: Circular dependency between services
# Solution: Use dependency injection with factories

container.register_factory(
    ServiceA,
    lambda: ServiceA(container.resolve(ServiceB))
)

container.register_factory(
    ServiceB,
    lambda: ServiceB()  # B doesn't depend on A directly
)
```

#### **Transaction Boundaries**

```python
# Problem: Transaction not covering entire use case
# Solution: Wrap entire use case in transaction

async def create_order_with_payment(self, command: CreateOrderCommand):
    async with self._tx_manager.begin():
        order_id = await self.create_order(command)
        await self.process_payment(order_id, command.payment_info)
        # Both operations in same transaction
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Core Domain Layer](./core-domain-layer.md) - Domain entities and business logic needed for application services
- [Hexagonal Architecture](./HEXAGONAL_VALIDATED_IMPLEMENTATION.md) - Architectural foundation understanding required

### **Next Steps**

- [Infrastructure Architecture](./infrastructure/infrastructure-architecture.md) - Implement infrastructure supporting application layer
- [Design Patterns](./patterns/advanced-patterns-hub.md) - Apply advanced patterns in application services

### **Related Topics**

- [Development Testing](../development/testing/index.md) - Testing strategies for application services
- [Oracle Integration](../guides/oracle/index.md) - Real-world application layer with Oracle systems
- [API Reference](../api-reference/index.md) - Technical details of application service implementations

---

**📂 Hub**: [Architecture Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
