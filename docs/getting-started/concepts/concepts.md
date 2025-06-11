# 💡 Core Concepts - Getting Started

> **Function**: Fundamental hexagonal architecture | **Audience**: All users | **Status**: ✅ Active

[![Core Concepts](https://img.shields.io/badge/concepts-fundamental-blue.svg)](./concepts.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-orange.svg)](../architecture/index.md)
[![Getting Started](https://img.shields.io/badge/getting--started-active-green.svg)](./index.md)

**Understanding the foundational concepts of FLX Framework's hexagonal architecture and domain-driven design**

---

## 🧭 **Navigation Context**

**🏠 Hub**: [Getting Started Index](./index.md) → **📄 Current**: Core Concepts

### **📍 Location in Learning Path**

```
[Quickstart](./quickstart.md) → **[CONCEPTS]** → [Troubleshooting](./troubleshooting.md)
```

## 🎯 **Quick Links**

- **🎯 Main Hub**: [Getting Started](./index.md)
- **📚 Documentation Root**: [Root Index](../index.md)  
- **🔗 Architecture Deep**: [Architecture Hub](../architecture/index.md)

---

## 🏛️ **Hexagonal Architecture Fundamentals**

### **🎯 What is Hexagonal Architecture?**

Hexagonal Architecture (also known as "Ports and Adapters") is an architectural pattern that isolates the core business logic from external concerns like databases, web frameworks, and user interfaces.

```
         ┌─────────────────────────────────────┐
         │          External World             │
         │                                     │
    ┌────▼─────┐                   ┌─────▼────┐
    │  Web UI  │                   │ Database │
    └────┬─────┘                   └─────┬────┘
         │                               │
    ┌────▼─────┐    ┌─────────────┐ ┌────▼─────┐
    │  Port    │◄───┤ Application ├─►│   Port   │
    │(Inbound) │    │    Core     │ │(Outbound)│
    └──────────┘    └─────────────┘ └──────────┘
                           │
                    ┌─────▼─────┐
                    │  Domain   │
                    │   Layer   │
                    └───────────┘
```

### **🎯 Key Benefits**

1. **Testability**: Core logic can be tested without external dependencies
2. **Flexibility**: Easy to swap implementations (different databases, APIs)
3. **Maintainability**: Clear separation of concerns
4. **Independence**: Business logic doesn't depend on frameworks

---

## 🔌 **Ports and Adapters**

### **📥 Inbound Ports (Driving Side)**

Inbound ports define how the outside world interacts with your application:

```python
from abc import ABC, abstractmethod
from typing import Protocol

class OrderUseCasePort(Protocol):
    """Inbound port for order management operations."""
    
    def create_order(self, order_data: OrderCreateData) -> OrderResult:
        """Create a new order in the system."""
        ...
    
    def get_order(self, order_id: str) -> OrderResult:
        """Retrieve order by ID."""
        ...
```

**Examples**: CLI interfaces, REST APIs, GraphQL endpoints, Message handlers

### **📤 Outbound Ports (Driven Side)**

Outbound ports define how your application interacts with external systems:

```python
class OrderRepositoryPort(Protocol):
    """Outbound port for order persistence."""
    
    def save(self, order: Order) -> None:
        """Save order to storage."""
        ...
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """Find order by ID."""
        ...

class NotificationPort(Protocol):
    """Outbound port for notifications."""
    
    def send_order_confirmation(self, order: Order) -> None:
        """Send order confirmation notification."""
        ...
```

**Examples**: Database repositories, HTTP clients, Message queues, File systems

---

## 🎯 **Domain-Driven Design (DDD)**

### **🏗️ Domain Entities**

Entities represent core business objects with identity:

```python
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Order:
    """Order domain entity with business logic."""
    
    id: UUID
    customer_id: UUID
    items: list[OrderItem]
    status: OrderStatus
    created_at: datetime
    total_amount: Decimal
    
    @classmethod
    def create_new(cls, customer_id: UUID, items: list[OrderItem]) -> 'Order':
        """Factory method to create new order with validation."""
        if not items:
            raise ValueError("Order must have at least one item")
        
        total = sum(item.total_price for item in items)
        
        return cls(
            id=uuid4(),
            customer_id=customer_id,
            items=items,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            total_amount=total
        )
    
    def mark_as_confirmed(self) -> None:
        """Business logic for order confirmation."""
        if self.status != OrderStatus.PENDING:
            raise OrderError(f"Cannot confirm order in {self.status} status")
        
        self.status = OrderStatus.CONFIRMED
```

### **💎 Value Objects**

Value objects represent concepts without identity:

```python
@dataclass(frozen=True)
class Money:
    """Value object for monetary amounts."""
    
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code")
    
    def add(self, other: 'Money') -> 'Money':
        """Add two monetary amounts."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        
        return Money(self.amount + other.amount, self.currency)
```

### **📢 Domain Events**

Events represent important business occurrences:

```python
@dataclass(frozen=True)
class OrderConfirmedEvent:
    """Domain event fired when order is confirmed."""
    
    order_id: UUID
    customer_id: UUID
    total_amount: Decimal
    confirmed_at: datetime
    
    @classmethod
    def from_order(cls, order: Order) -> 'OrderConfirmedEvent':
        """Create event from order entity."""
        return cls(
            order_id=order.id,
            customer_id=order.customer_id,
            total_amount=order.total_amount,
            confirmed_at=datetime.utcnow()
        )
```

---

## ⚙️ **FLX Framework Implementation**

### **🎯 Application Services**

Application services orchestrate domain logic and coordinate with infrastructure:

```python
class OrderApplicationService:
    """Application service for order operations."""
    
    def __init__(
        self,
        order_repo: OrderRepositoryPort,
        notification_service: NotificationPort,
        event_publisher: EventPublisherPort
    ):
        self._order_repo = order_repo
        self._notification_service = notification_service
        self._event_publisher = event_publisher
    
    def confirm_order(self, order_id: UUID) -> OrderResult:
        """Confirm order use case implementation."""
        # Load domain entity
        order = self._order_repo.find_by_id(str(order_id))
        if not order:
            raise OrderNotFoundError(order_id)
        
        # Execute business logic
        order.mark_as_confirmed()
        
        # Persist changes
        self._order_repo.save(order)
        
        # Publish domain event
        event = OrderConfirmedEvent.from_order(order)
        self._event_publisher.publish(event)
        
        # Send notification
        self._notification_service.send_order_confirmation(order)
        
        return OrderResult.from_entity(order)
```

### **🔧 Adapters**

Adapters implement ports to connect with external systems:

```python
class SqlAlchemyOrderRepository:
    """SQL database adapter for order repository."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, order: Order) -> None:
        """Save order to SQL database."""
        db_order = OrderModel.from_entity(order)
        self._session.merge(db_order)
        self._session.commit()
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """Find order by ID from SQL database."""
        db_order = self._session.query(OrderModel).filter_by(id=order_id).first()
        return db_order.to_entity() if db_order else None

class EmailNotificationAdapter:
    """Email adapter for notification service."""
    
    def __init__(self, email_client: EmailClient):
        self._email_client = email_client
    
    def send_order_confirmation(self, order: Order) -> None:
        """Send order confirmation via email."""
        message = self._build_confirmation_message(order)
        self._email_client.send(message)
```

---

## 🏗️ **Dependency Injection**

FLX uses dependency injection to wire components together:

```python
from flx.core.container import Container

def configure_container() -> Container:
    """Configure dependency injection container."""
    container = Container()
    
    # Infrastructure
    container.register(Session, SQLAlchemySession)
    container.register(EmailClient, SMTPEmailClient)
    
    # Repositories (Outbound adapters)
    container.register(OrderRepositoryPort, SqlAlchemyOrderRepository)
    container.register(NotificationPort, EmailNotificationAdapter)
    
    # Application services
    container.register(OrderApplicationService, OrderApplicationService)
    
    return container
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Quickstart Guide](./quickstart.md) - Basic framework usage
- [Installation](./installation.md) - Environment setup

### **Next Steps**

- [Architecture Guide](../architecture/index.md) - Detailed architectural patterns
- [API Reference](../api-reference/core/index.md) - Core framework APIs
- [Oracle Integration](../guides/oracle-wms-comprehensive-guide.md) - Real-world implementation

### **Related Topics**

- [Ports Implementation](../architecture/hexagonal/ports.md) - Port design patterns
- [Adapters Guide](../architecture/hexagonal/adapters.md) - Adapter implementation
- [Domain Layer](../architecture/hexagonal/domain.md) - Domain modeling patterns

---

**📍 Location**: [Getting Started Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
