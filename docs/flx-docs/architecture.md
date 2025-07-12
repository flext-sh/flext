# 🏛️ FLX Architecture Guide

> **Function**: Comprehensive architecture documentation for FLX framework | **Audience**: Architects, Senior Engineers | **Status**: Reference

[![Architecture](https://img.shields.io/badge/pattern-hexagonal-orange.svg)](https://alistair.cockburn.us/hexagonal-architecture/)
[![DDD](https://img.shields.io/badge/approach-DDD-blue.svg)](https://www.domainlanguage.com/ddd/)
[![SOLID](https://img.shields.io/badge/principles-SOLID-green.svg)](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
[![Clean](https://img.shields.io/badge/style-clean-purple.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

Complete architectural guide for FLX's hexagonal architecture implementation with DDD patterns and enterprise best practices.

---

## 🧭 **Navigation**

**🏠 Root**: [PyAuto](../../README.md) → **📂 Framework**: [FLX](../README.md) → **📄 Current**: Architecture Guide

---

## 📋 **Architecture Overview**

### **Hexagonal Architecture (Ports & Adapters)**

FLX implements hexagonal architecture to achieve:

- **Testability**: Business logic testable in isolation
- **Flexibility**: Easy to swap infrastructure components
- **Maintainability**: Clear separation of concerns
- **Evolvability**: Domain model can evolve independently

### **Core Principles**

1. **Domain-Centric**: Business logic at the center
2. **Dependency Inversion**: Infrastructure depends on domain
3. **Port Abstraction**: Clear interface boundaries
4. **Adapter Pattern**: Pluggable infrastructure
5. **Layered Architecture**: Strict layer dependencies

---

## 🏗️ **Architectural Layers**

```
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                         │
│  (Users, APIs, Databases, Message Queues, File Systems)    │
└─────────────────────┬─────────────────┬────────────────────┘
                      │                 │
┌─────────────────────▼─────────────────▼────────────────────┐
│                    Adapters Layer                           │
│  ┌─────────────────────┐   ┌──────────────────────────┐    │
│  │   Inbound Adapters  │   │   Outbound Adapters     │    │
│  │  • REST Controllers │   │  • Database Repos      │    │
│  │  • CLI Commands     │   │  • HTTP Clients        │    │
│  │  • GraphQL          │   │  • Message Publishers  │    │
│  │  • WebSocket        │   │  • File Systems        │    │
│  └─────────────────────┘   └──────────────────────────┘    │
└────────────────────┬──────────────────┬────────────────────┘
                     │                  │
┌────────────────────▼──────────────────▼────────────────────┐
│                     Ports Layer                             │
│  ┌─────────────────────┐   ┌──────────────────────────┐    │
│  │   Inbound Ports     │   │    Outbound Ports      │    │
│  │  • Use Case APIs    │   │  • Repository APIs     │    │
│  │  • Query APIs       │   │  • Service APIs        │    │
│  │  • Command APIs     │   │  • Event Publisher APIs │    │
│  └─────────────────────┘   └──────────────────────────┘    │
└────────────────────┬──────────────────┬────────────────────┘
                     │                  │
┌────────────────────▼──────────────────▼────────────────────┐
│                 Application Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Application Services                        │  │
│  │  • Use Case Orchestration                           │  │
│  │  • Transaction Management                           │  │
│  │  • Cross-Aggregate Coordination                     │  │
│  │  • Application Events                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Domain Layer                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Core Business Logic                     │  │
│  │  • Entities & Value Objects                          │  │
│  │  • Aggregates & Domain Events                        │  │
│  │  • Domain Services                                   │  │
│  │  • Business Rules & Invariants                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Layer Responsibilities**

### **1. Domain Layer** (Innermost)

**Purpose**: Pure business logic with zero dependencies

**Components**:

- **Entities**: Business objects with identity
- **Value Objects**: Immutable domain values
- **Aggregates**: Consistency boundaries
- **Domain Events**: Business state changes
- **Domain Services**: Cross-aggregate logic

**Rules**:

- No external dependencies
- No infrastructure concerns
- Pure business logic only
- Highly testable

**Example**:

```python
from flx.core import Entity, ValueObject, DomainEvent

class ProductId(ValueObject):
    value: str

class Product(Entity):
    product_id: ProductId
    name: str
    price: Money
    stock: int

    def purchase(self, quantity: int) -> None:
        if self.stock < quantity:
            raise InsufficientStock()

        self.stock -= quantity
        self.add_domain_event(ProductPurchased(
            product_id=self.product_id,
            quantity=quantity
        ))
```

### **2. Application Layer**

**Purpose**: Use case orchestration and workflow

**Components**:

- **Application Services**: Use case implementation
- **Command Handlers**: Write operations (CQRS)
- **Query Handlers**: Read operations (CQRS)
- **DTOs**: Data transfer objects
- **Mappers**: Domain ↔ DTO conversion

**Responsibilities**:

- Transaction management
- Cross-aggregate coordination
- Security enforcement
- Use case flow control

**Example**:

```python
from flx.application import ApplicationService

class OrderService(ApplicationService):
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        payment_service: PaymentService
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.payment_service = payment_service

    async def place_order(self, command: PlaceOrderCommand) -> OrderId:
        # Load aggregates
        products = await self.product_repo.find_by_ids(command.product_ids)

        # Create order (domain logic)
        order = Order.create(command.customer_id, products)

        # Process payment (external service)
        payment = await self.payment_service.charge(order.total)
        order.confirm_payment(payment)

        # Persist
        await self.order_repo.save(order)

        # Publish events
        await self.publish_events(order.get_uncommitted_events())

        return order.id
```

### **3. Ports Layer**

**Purpose**: Interface definitions (contracts)

**Components**:

- **Inbound Ports**: APIs exposed by application
- **Outbound Ports**: APIs required by application
- **Port DTOs**: Data structures for port communication

**Types**:

- **Repository Ports**: Data persistence
- **Service Ports**: External services
- **Event Publisher Ports**: Event distribution
- **Query Ports**: Read models

**Example**:

```python
from abc import ABC, abstractmethod
from typing import Optional, List

# Outbound port (required by application)
class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        pass

# Inbound port (exposed by application)
class OrderUseCase(ABC):
    @abstractmethod
    async def place_order(self, command: PlaceOrderCommand) -> OrderId:
        pass

    @abstractmethod
    async def cancel_order(self, order_id: OrderId) -> None:
        pass
```

### **4. Adapters Layer** (Outermost)

**Purpose**: Infrastructure implementations

**Components**:

- **Inbound Adapters**: Entry points (REST, CLI, GraphQL)
- **Outbound Adapters**: Infrastructure (DB, HTTP, Files)
- **Adapter Configuration**: Infrastructure settings
- **Adapter Mappings**: External ↔ Domain conversion

**Examples**:

**Inbound Adapter (REST)**:

```python
from fastapi import APIRouter, Depends
from flx.adapters.inbound import RESTAdapter

class OrderController(RESTAdapter):
    def __init__(self, order_use_case: OrderUseCase):
        self.use_case = order_use_case
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/orders")
        async def create_order(request: CreateOrderRequest):
            command = self._map_to_command(request)
            order_id = await self.use_case.place_order(command)
            return {"order_id": str(order_id)}
```

**Outbound Adapter (Database)**:

```python
from flx_database_oracle import OracleAdapter
from domain.ports import OrderRepository

class OracleOrderRepository(OrderRepository):
    def __init__(self, db: OracleAdapter):
        self.db = db

    async def save(self, order: Order) -> None:
        db_order = self._map_to_db_model(order)
        async with self.db.session() as session:
            session.add(db_order)
            await session.commit()

    async def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        async with self.db.session() as session:
            db_order = await session.get(DbOrder, str(order_id))
            return self._map_to_domain(db_order) if db_order else None
```

---

## 🔄 **Data Flow**

### **Inbound Request Flow**

```
External Request
    ↓
Inbound Adapter (e.g., REST Controller)
    ↓ [validates & transforms]
Application Service
    ↓ [orchestrates]
Domain Layer
    ↓ [business logic]
Outbound Port
    ↓ [interface]
Outbound Adapter (e.g., Database)
    ↓ [implementation]
External System
```

### **Event Flow**

```
Domain Event (e.g., OrderPlaced)
    ↓
Application Layer [collects events]
    ↓
Event Publisher Port
    ↓
Event Publisher Adapter
    ↓
Message Queue / Event Store
    ↓
Event Subscribers
```

---

## 🎭 **Design Patterns**

### **1. Repository Pattern**

Abstracts data persistence:

```python
class CustomerRepository(ABC):
    """Domain repository interface."""

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[Customer]:
        pass

    @abstractmethod
    async def save(self, customer: Customer) -> None:
        pass

class InMemoryCustomerRepository(CustomerRepository):
    """Test implementation."""

    def __init__(self):
        self.customers: Dict[str, Customer] = {}

    async def find_by_email(self, email: Email) -> Optional[Customer]:
        return next(
            (c for c in self.customers.values() if c.email == email),
            None
        )
```

### **2. Factory Pattern**

Complex object creation:

```python
class OrderFactory:
    """Creates valid order aggregates."""

    @staticmethod
    def create_from_cart(
        cart: ShoppingCart,
        customer: Customer,
        shipping: ShippingMethod
    ) -> Order:
        # Complex creation logic
        order = Order(
            order_id=OrderId.generate(),
            customer_id=customer.id,
            created_at=datetime.utcnow()
        )

        for item in cart.items:
            order.add_line_item(item.product, item.quantity)

        order.set_shipping(shipping)
        order.calculate_total()

        return order
```

### **3. Strategy Pattern**

Pluggable algorithms:

```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, order: Order) -> Money:
        pass

class StandardPricing(PricingStrategy):
    def calculate_price(self, order: Order) -> Money:
        return order.subtotal

class VIPPricing(PricingStrategy):
    def calculate_price(self, order: Order) -> Money:
        discount = order.subtotal.multiply(Decimal("0.1"))
        return order.subtotal.subtract(discount)

class PricingService:
    def __init__(self, strategy: PricingStrategy):
        self.strategy = strategy

    def price_order(self, order: Order) -> Money:
        return self.strategy.calculate_price(order)
```

### **4. Chain of Responsibility**

Processing pipeline:

```python
class ValidationHandler(ABC):
    def __init__(self, next_handler: Optional['ValidationHandler'] = None):
        self.next = next_handler

    def handle(self, order: Order) -> ValidationResult:
        result = self.validate(order)
        if result.is_valid and self.next:
            return self.next.handle(order)
        return result

    @abstractmethod
    def validate(self, order: Order) -> ValidationResult:
        pass

class StockValidator(ValidationHandler):
    def validate(self, order: Order) -> ValidationResult:
        # Check stock availability
        pass

class CreditValidator(ValidationHandler):
    def validate(self, order: Order) -> ValidationResult:
        # Check customer credit
        pass

# Usage
validator = StockValidator(CreditValidator())
result = validator.handle(order)
```

---

## 🔧 **Configuration Architecture**

### **Layered Configuration**

```python
# Domain layer - no configuration needed
class Product(Entity):
    # Pure business logic
    pass

# Application layer - application config
class ApplicationConfig:
    transaction_timeout: int = 30
    max_retry_attempts: int = 3

# Adapter layer - infrastructure config
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    pool_size: int = 20

# Bootstrap configuration
class Bootstrap:
    def __init__(self):
        self.db_config = DatabaseConfig.from_env()
        self.app_config = ApplicationConfig.from_env()

    def create_application(self) -> Application:
        # Wire everything together
        db_adapter = OracleAdapter(self.db_config)
        order_repo = OracleOrderRepository(db_adapter)
        order_service = OrderService(order_repo)

        return Application(order_service)
```

---

## 🧪 **Testing Architecture**

### **Test Pyramid**

```
         ╱╲
        ╱  ╲       E2E Tests (Few)
       ╱    ╲      - Full system tests
      ╱──────╲     - Real infrastructure
     ╱        ╲
    ╱          ╲   Integration Tests (Some)
   ╱            ╲  - Cross-layer tests
  ╱              ╲ - Test with real adapters
 ╱────────────────╲
╱                  ╲ Unit Tests (Many)
────────────────────  - Domain logic tests
                      - Pure, fast, isolated
```

### **Testing Strategies by Layer**

**Domain Layer Testing**:

```python
def test_order_total_calculation():
    # Pure unit test - no mocks needed
    order = Order(order_id=OrderId("123"))
    order.add_item(Product("Widget", Money(10, "USD")), quantity=2)

    assert order.total == Money(20, "USD")
```

**Application Layer Testing**:

```python
async def test_place_order_use_case():
    # Test with in-memory adapters
    order_repo = InMemoryOrderRepository()
    payment_service = MockPaymentService()

    use_case = OrderService(order_repo, payment_service)
    order_id = await use_case.place_order(command)

    assert await order_repo.find_by_id(order_id) is not None
```

**Adapter Testing**:

```python
@pytest.mark.integration
async def test_oracle_repository():
    # Test with real database
    async with TestDatabase() as db:
        repo = OracleOrderRepository(db)
        order = create_test_order()

        await repo.save(order)
        retrieved = await repo.find_by_id(order.id)

        assert retrieved == order
```

---

## 📊 **Architecture Metrics**

### **Layer Independence**

```
Domain Layer Dependencies:     0 external
Application Layer Dependencies: Domain only
Port Layer Dependencies:        Domain only
Adapter Layer Dependencies:     All layers + external
```

### **Testability Metrics**

- **Domain Logic**: 100% unit testable
- **Application Logic**: 95% unit testable (5% integration)
- **Adapters**: 20% unit, 80% integration
- **Overall Coverage Target**: 90%+

### **Complexity Metrics**

```
Layer               Cyclomatic Complexity    Max Method Lines
Domain              Low (1-5)                20
Application         Medium (5-10)            50
Ports               Low (1-2)                10 (interfaces)
Adapters            Medium (5-15)            100
```

---

## 🚀 **Best Practices**

### **1. Dependency Direction**

```
External Systems
    ↓ depends on
Adapters
    ↓ depends on
Ports (interfaces)
    ↓ depends on
Application
    ↓ depends on
Domain
    ↓ depends on
Nothing (pure)
```

### **2. Interface Segregation**

```python
# ❌ WRONG - Fat interface
class UserService:
    def create_user(self, data: dict) -> User
    def update_user(self, id: str, data: dict) -> User
    def delete_user(self, id: str) -> None
    def find_user(self, id: str) -> User
    def list_users(self) -> List[User]
    def authenticate(self, credentials: dict) -> Token
    def reset_password(self, email: str) -> None
    # ... 20 more methods

# ✅ CORRECT - Segregated interfaces
class UserCommandService:
    def create_user(self, command: CreateUserCommand) -> UserId
    def update_user(self, command: UpdateUserCommand) -> None
    def delete_user(self, user_id: UserId) -> None

class UserQueryService:
    def find_user(self, user_id: UserId) -> UserDTO
    def list_users(self, criteria: SearchCriteria) -> List[UserDTO]

class AuthenticationService:
    def authenticate(self, credentials: Credentials) -> Token
    def reset_password(self, email: Email) -> None
```

### **3. Domain Isolation**

```python
# ❌ WRONG - Domain depends on infrastructure
from sqlalchemy import Column, String

class User(Entity, SQLAlchemyBase):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)

# ✅ CORRECT - Pure domain model
class User(Entity):
    user_id: UserId
    name: str
    email: Email

    def change_email(self, new_email: Email) -> None:
        # Business logic only
        self.email = new_email
        self.add_domain_event(EmailChanged(self.user_id, new_email))
```

---

## 🔗 **Cross-References**

### **Architecture Patterns**

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) - Original article
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/) - DDD resources
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - Uncle Bob's Clean Architecture

### **Implementation Examples**

- [FLX Core Domain](../src/flx/core/README.md) - Domain layer implementation
- [FLX Application](../src/flx/application/README.md) - Application layer
- [FLX Ports](../src/flx/ports/README.md) - Port definitions
- [FLX Adapters](../src/flx/adapters/README.md) - Adapter implementations

---

**📂 Documentation**: Architecture Guide | **🏠 Framework**: [FLX](../README.md) | **🏠 Root**: [PyAuto](../../README.md) | **Updated**: 2025-01-19
