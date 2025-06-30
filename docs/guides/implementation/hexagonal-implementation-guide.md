# 🏗️ Hexagonal Architecture Implementation Guide

> **Navigation**: [Documentation Home](../../index.md) → [Guides Hub](../index.md) → Hexagonal Implementation Guide

**Practical guide for implementing hexagonal architecture with FLEXT Framework based on production patterns and source code analysis**

## 📋 **Table of Contents**

- [🎯 Implementation Strategy](#-implementation-strategy)
- [📦 Domain Layer Implementation](#-domain-layer-implementation)
- [🔌 Ports Definition](#-ports-definition)
- [⚡ Adapters Implementation](#-adapters-implementation)
- [🏭 Infrastructure Services](#-infrastructure-services)
- [🧪 Testing Implementation](#-testing-implementation)
- [📊 Production Examples](#-production-examples)

---

## 🎯 Implementation Strategy

### **Step-by-Step Approach**

Based on FLEXT Framework source code patterns, follow this implementation sequence:

```
1. Domain Layer (Core Business Logic)
   ├── Entities with identity and lifecycle
   ├── Value objects for immutable data
   ├── Domain events for communication
   └── Business rules and invariants

2. Application Layer (Use Case Orchestration)
   ├── Application services
   ├── Command and query handlers
   ├── Bootstrap and configuration
   └── Dependency injection container

3. Port Interfaces (Contracts)
   ├── Inbound ports (API, CLI, Events)
   ├── Outbound ports (Database, Cache, HTTP)
   ├── Port validation and contracts
   └── Interface segregation

4. Infrastructure Layer (External Integrations)
   ├── Adapters implementing ports
   ├── Infrastructure services
   ├── External system clients
   └── Configuration and monitoring
```

---

## 📦 Domain Layer Implementation

### **Entity Design Patterns**

Based on `flext/core/entities.py`, implement entities with proper identity management:

```python
from flext.core.entities import Entity, AggregateRoot
from flext.core.domain.value_objects import ValueObject
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Value Objects - Immutable data containers
class Email(ValueObject):
    """Email value object with validation."""
    value: str

    def model_post_init(self, __context):
        """Validate email format."""
        if "@" not in self.value or "." not in self.value:
            raise ValueError("Invalid email format")

class Money(ValueObject):
    """Money value object with currency."""
    amount: float
    currency: str = "USD"

    def add(self, other: 'Money') -> 'Money':
        """Add money values with currency validation."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)

# Enums for domain concepts
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Entities - Objects with identity
class Customer(Entity):
    """Customer entity with business rules."""

    name: str
    email: Email
    registration_date: datetime
    is_active: bool = True

    def change_email(self, new_email: Email) -> None:
        """Change customer email with business rules."""
        if not self.is_active:
            raise ValueError("Cannot change email for inactive customer")

        old_email = self.email
        self.email = new_email
        self.touch()  # Update modification timestamp

        # Emit domain event for email change
        self.add_event({
            "event_type": "customer_email_changed",
            "customer_id": self.id,
            "old_email": old_email.value,
            "new_email": new_email.value,
            "changed_at": datetime.utcnow().isoformat()
        })

    def deactivate(self) -> None:
        """Deactivate customer account."""
        self.is_active = False
        self.touch()

        self.add_event({
            "event_type": "customer_deactivated",
            "customer_id": self.id,
            "deactivated_at": datetime.utcnow().isoformat()
        })

# Aggregate Roots - Consistency boundaries
class Order(AggregateRoot):
    """Order aggregate root managing order lifecycle."""

    customer_id: str
    status: OrderStatus = OrderStatus.PENDING
    items: List[dict] = []
    total: Money = Money(amount=0.0)
    created_at: datetime
    confirmed_at: Optional[datetime] = None

    def model_post_init(self, __context):
        """Initialize order after creation."""
        super().model_post_init(__context)
        if not hasattr(self, 'created_at'):
            self.created_at = datetime.utcnow()

    def add_item(self, product_id: str, quantity: int, unit_price: Money) -> None:
        """Add item to order with business validation."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Cannot modify confirmed order")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        item = {
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price.model_dump(),
            "line_total": Money(amount=unit_price.amount * quantity, currency=unit_price.currency).model_dump()
        }

        self.items.append(item)
        self._recalculate_total()
        self.touch()

        self.add_event({
            "event_type": "item_added_to_order",
            "order_id": self.id,
            "product_id": product_id,
            "quantity": quantity,
            "added_at": datetime.utcnow().isoformat()
        })

    def confirm(self) -> None:
        """Confirm order with business rules."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Order already processed")

        if not self.items:
            raise ValueError("Cannot confirm empty order")

        self.status = OrderStatus.CONFIRMED
        self.confirmed_at = datetime.utcnow()
        self.increment_version()  # Optimistic locking

        self.add_event({
            "event_type": "order_confirmed",
            "order_id": self.id,
            "customer_id": self.customer_id,
            "total": self.total.model_dump(),
            "item_count": len(self.items),
            "confirmed_at": self.confirmed_at.isoformat()
        })

    def _recalculate_total(self) -> None:
        """Recalculate order total from items."""
        total_amount = sum(item["line_total"]["amount"] for item in self.items)
        self.total = Money(amount=total_amount)
```

---

## 🔌 Ports Definition

### **Inbound Ports - External Actors**

Define clear contracts for external interactions:

```python
# ports/inbound/order_management.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class OrderManagementPort(ABC):
    """Port for order management operations."""

    @abstractmethod
    async def create_order(self, customer_id: str, items: List[Dict[str, Any]]) -> str:
        """Create new order and return order ID."""
        ...

    @abstractmethod
    async def confirm_order(self, order_id: str) -> bool:
        """Confirm pending order."""
        ...

    @abstractmethod
    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details by ID."""
        ...

    @abstractmethod
    async def list_customer_orders(self, customer_id: str) -> List[Dict[str, Any]]:
        """List all orders for a customer."""
        ...

class CustomerManagementPort(ABC):
    """Port for customer management operations."""

    @abstractmethod
    async def register_customer(self, name: str, email: str) -> str:
        """Register new customer and return customer ID."""
        ...

    @abstractmethod
    async def update_customer_email(self, customer_id: str, new_email: str) -> bool:
        """Update customer email address."""
        ...

    @abstractmethod
    async def deactivate_customer(self, customer_id: str) -> bool:
        """Deactivate customer account."""
        ...
```

### **Outbound Ports - External Systems**

```python
# ports/outbound/persistence.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class OrderRepositoryPort(ABC):
    """Port for order persistence operations."""

    @abstractmethod
    async def save_order(self, order: Dict[str, Any]) -> str:
        """Save order and return generated ID."""
        ...

    @abstractmethod
    async def find_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Find order by ID."""
        ...

    @abstractmethod
    async def find_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Find all orders for a customer."""
        ...

    @abstractmethod
    async def update_order(self, order_id: str, data: Dict[str, Any]) -> bool:
        """Update order data."""
        ...

class CustomerRepositoryPort(ABC):
    """Port for customer persistence operations."""

    @abstractmethod
    async def save_customer(self, customer: Dict[str, Any]) -> str:
        """Save customer and return generated ID."""
        ...

    @abstractmethod
    async def find_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Find customer by ID."""
        ...

    @abstractmethod
    async def find_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find customer by email address."""
        ...

    @abstractmethod
    async def update_customer(self, customer_id: str, data: Dict[str, Any]) -> bool:
        """Update customer data."""
        ...

class NotificationPort(ABC):
    """Port for notification operations."""

    @abstractmethod
    async def send_order_confirmation(self, customer_email: str, order_details: Dict[str, Any]) -> bool:
        """Send order confirmation notification."""
        ...

    @abstractmethod
    async def send_email_change_notification(self, old_email: str, new_email: str) -> bool:
        """Send email change notification."""
        ...
```

---

## ⚡ Adapters Implementation

### **Database Adapter**

Based on FLEXT patterns in `flext/adapters/base.py`:

```python
from flext.adapters.base import BaseAdapter
from flext.ports.outbound.persistence import OrderRepositoryPort, CustomerRepositoryPort
from pydantic import Field
from typing import Dict, Any, List, Optional
import asyncpg
import json

class PostgreSQLAdapter(BaseAdapter, OrderRepositoryPort, CustomerRepositoryPort):
    """PostgreSQL database adapter implementation."""

    # Configuration schema
    database_url: str = Field(..., description="PostgreSQL connection URL")
    pool_min_size: int = Field(default=5, description="Minimum pool size")
    pool_max_size: int = Field(default=20, description="Maximum pool size")

    def __init__(self, **data):
        super().__init__(**data)
        self._connection_pool: Optional[asyncpg.Pool] = None

    async def _connect(self) -> None:
        """Initialize PostgreSQL connection pool."""
        self._connection_pool = await asyncpg.create_pool(
            self.database_url,
            min_size=self.pool_min_size,
            max_size=self.pool_max_size,
            command_timeout=30
        )

        # Test connection
        async with self._connection_pool.acquire() as conn:
            await conn.fetchval('SELECT 1')

        self.logger.info(f"Connected to PostgreSQL with pool size {self.pool_min_size}-{self.pool_max_size}")

    async def _disconnect(self) -> None:
        """Close PostgreSQL connection pool."""
        if self._connection_pool:
            await self._connection_pool.close()
            self._connection_pool = None
            self.logger.info("Disconnected from PostgreSQL")

    async def _health_check(self) -> bool:
        """Check PostgreSQL connection health."""
        if not self._connection_pool:
            return False

        try:
            async with self._connection_pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
            return True
        except Exception as e:
            self.logger.error(f"PostgreSQL health check failed: {e}")
            return False

    # Order repository implementation
    async def save_order(self, order: Dict[str, Any]) -> str:
        """Save order to PostgreSQL."""
        async with self._connection_pool.acquire() as conn:
            order_id = await conn.fetchval(
                """
                INSERT INTO orders (id, customer_id, status, items, total, created_at, version)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                order["id"],
                order["customer_id"],
                order["status"],
                json.dumps(order["items"]),
                json.dumps(order["total"]),
                order["created_at"],
                order.get("version", 1)
            )
            return order_id

    async def find_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Find order by ID in PostgreSQL."""
        async with self._connection_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM orders WHERE id = $1",
                order_id
            )

            if row:
                return {
                    "id": row["id"],
                    "customer_id": row["customer_id"],
                    "status": row["status"],
                    "items": json.loads(row["items"]),
                    "total": json.loads(row["total"]),
                    "created_at": row["created_at"],
                    "confirmed_at": row["confirmed_at"],
                    "version": row["version"]
                }
            return None

    async def find_orders_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Find all orders for a customer."""
        async with self._connection_pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC",
                customer_id
            )

            return [
                {
                    "id": row["id"],
                    "customer_id": row["customer_id"],
                    "status": row["status"],
                    "items": json.loads(row["items"]),
                    "total": json.loads(row["total"]),
                    "created_at": row["created_at"],
                    "confirmed_at": row["confirmed_at"],
                    "version": row["version"]
                }
                for row in rows
            ]

    # Customer repository implementation
    async def save_customer(self, customer: Dict[str, Any]) -> str:
        """Save customer to PostgreSQL."""
        async with self._connection_pool.acquire() as conn:
            customer_id = await conn.fetchval(
                """
                INSERT INTO customers (id, name, email, registration_date, is_active, version)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                customer["id"],
                customer["name"],
                customer["email"]["value"],
                customer["registration_date"],
                customer["is_active"],
                customer.get("version", 1)
            )
            return customer_id

    async def find_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Find customer by ID in PostgreSQL."""
        async with self._connection_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM customers WHERE id = $1",
                customer_id
            )

            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "email": {"value": row["email"]},
                    "registration_date": row["registration_date"],
                    "is_active": row["is_active"],
                    "version": row["version"]
                }
            return None

    async def find_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find customer by email in PostgreSQL."""
        async with self._connection_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM customers WHERE email = $1",
                email
            )

            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "email": {"value": row["email"]},
                    "registration_date": row["registration_date"],
                    "is_active": row["is_active"],
                    "version": row["version"]
                }
            return None
```

### **Email Notification Adapter**

```python
from flext.adapters.base import BaseAdapter
from flext.ports.outbound.persistence import NotificationPort
from pydantic import Field
from typing import Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAdapter(BaseAdapter, NotificationPort):
    """Email notification adapter using SMTP."""

    # Configuration schema
    smtp_host: str = Field(..., description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(..., description="SMTP username")
    smtp_password: str = Field(..., description="SMTP password")
    from_email: str = Field(..., description="From email address")

    async def _connect(self) -> None:
        """Test SMTP connection."""
        try:
            await aiosmtplib.send(
                MIMEText("Test connection", "plain"),
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True,
                sender=self.from_email,
                recipients=[self.from_email]  # Send test to self
            )
            self.logger.info(f"Connected to SMTP server {self.smtp_host}:{self.smtp_port}")
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            raise

    async def _disconnect(self) -> None:
        """No persistent connection to close."""
        self.logger.info("Email adapter disconnected")

    async def _health_check(self) -> bool:
        """Check SMTP server availability."""
        try:
            # Simple connection test
            server = aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port)
            await server.connect()
            await server.quit()
            return True
        except Exception as e:
            self.logger.error(f"SMTP health check failed: {e}")
            return False

    async def send_order_confirmation(self, customer_email: str, order_details: Dict[str, Any]) -> bool:
        """Send order confirmation email."""
        try:
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = customer_email
            message["Subject"] = f"Order Confirmation - Order #{order_details['id']}"

            body = f"""
            Dear Customer,

            Your order has been confirmed!

            Order ID: {order_details['id']}
            Total: {order_details['total']['amount']} {order_details['total']['currency']}
            Items: {len(order_details['items'])} items

            Thank you for your business!

            Best regards,
            The Team
            """

            message.attach(MIMEText(body, "plain"))

            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True
            )

            self.logger.info(f"Order confirmation sent to {customer_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send order confirmation: {e}")
            return False

    async def send_email_change_notification(self, old_email: str, new_email: str) -> bool:
        """Send email change notification."""
        try:
            # Send to both old and new email addresses
            for email in [old_email, new_email]:
                message = MIMEMultipart()
                message["From"] = self.from_email
                message["To"] = email
                message["Subject"] = "Email Address Changed"

                body = f"""
                Dear Customer,

                Your email address has been changed from {old_email} to {new_email}.

                If you did not make this change, please contact support immediately.

                Best regards,
                The Team
                """

                message.attach(MIMEText(body, "plain"))

                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    start_tls=True
                )

            self.logger.info(f"Email change notification sent to {old_email} and {new_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email change notification: {e}")
            return False
```

---

## 🏭 Infrastructure Services

### **Application Service Implementation**

Based on `flext/application/services.py` patterns:

```python
from flext.application.services import ApplicationService
from flext.ports.inbound.order_management import OrderManagementPort, CustomerManagementPort
from flext.ports.outbound.persistence import OrderRepositoryPort, CustomerRepositoryPort, NotificationPort
from typing import Dict, Any, List, Optional
from datetime import datetime

class OrderService(ApplicationService, OrderManagementPort):
    """Order management application service."""

    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        customer_repository: CustomerRepositoryPort,
        notification_service: NotificationPort
    ):
        super().__init__("order_service")
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.notification_service = notification_service

    async def create_order(self, customer_id: str, items: List[Dict[str, Any]]) -> str:
        """Create new order with business validation."""
        # Validate customer exists
        customer = await self.customer_repository.find_customer_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        if not customer["is_active"]:
            raise ValueError("Cannot create order for inactive customer")

        # Create order entity
        from entities import Order, Money
        order = Order(
            customer_id=customer_id,
            created_at=datetime.utcnow()
        )

        # Add items with validation
        for item in items:
            unit_price = Money(amount=item["unit_price"], currency=item.get("currency", "USD"))
            order.add_item(
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=unit_price
            )

        # Save order
        order_data = order.model_dump()
        order_id = await self.order_repository.save_order(order_data)

        # Process domain events
        await self._process_domain_events(order.get_events())

        self.logger.info(f"Order {order_id} created for customer {customer_id}")
        return order_id

    async def confirm_order(self, order_id: str) -> bool:
        """Confirm pending order."""
        # Load order
        order_data = await self.order_repository.find_order_by_id(order_id)
        if not order_data:
            raise ValueError(f"Order {order_id} not found")

        # Recreate entity from data
        from entities import Order
        order = Order(**order_data)

        # Confirm order (business logic)
        order.confirm()

        # Save updated order
        updated_data = order.model_dump()
        await self.order_repository.update_order(order_id, updated_data)

        # Process domain events
        await self._process_domain_events(order.get_events())

        self.logger.info(f"Order {order_id} confirmed")
        return True

    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details by ID."""
        return await self.order_repository.find_order_by_id(order_id)

    async def list_customer_orders(self, customer_id: str) -> List[Dict[str, Any]]:
        """List all orders for a customer."""
        return await self.order_repository.find_orders_by_customer(customer_id)

    async def _process_domain_events(self, events: List[Dict[str, Any]]) -> None:
        """Process domain events from entities."""
        for event in events:
            if event["event_type"] == "order_confirmed":
                # Send confirmation email
                customer_id = event["customer_id"]
                customer = await self.customer_repository.find_customer_by_id(customer_id)

                if customer:
                    order_details = {
                        "id": event["order_id"],
                        "total": event["total"],
                        "items": [{"count": event["item_count"]}]
                    }

                    await self.notification_service.send_order_confirmation(
                        customer["email"]["value"],
                        order_details
                    )

class CustomerService(ApplicationService, CustomerManagementPort):
    """Customer management application service."""

    def __init__(
        self,
        customer_repository: CustomerRepositoryPort,
        notification_service: NotificationPort
    ):
        super().__init__("customer_service")
        self.customer_repository = customer_repository
        self.notification_service = notification_service

    async def register_customer(self, name: str, email: str) -> str:
        """Register new customer."""
        # Check if email already exists
        existing_customer = await self.customer_repository.find_customer_by_email(email)
        if existing_customer:
            raise ValueError(f"Customer with email {email} already exists")

        # Create customer entity
        from entities import Customer, Email
        customer = Customer(
            name=name,
            email=Email(value=email),
            registration_date=datetime.utcnow()
        )

        # Save customer
        customer_data = customer.model_dump()
        customer_id = await self.customer_repository.save_customer(customer_data)

        self.logger.info(f"Customer {customer_id} registered with email {email}")
        return customer_id

    async def update_customer_email(self, customer_id: str, new_email: str) -> bool:
        """Update customer email address."""
        # Load customer
        customer_data = await self.customer_repository.find_customer_by_id(customer_id)
        if not customer_data:
            raise ValueError(f"Customer {customer_id} not found")

        # Recreate entity
        from entities import Customer, Email
        customer = Customer(**customer_data)

        # Update email (business logic)
        old_email = customer.email.value
        customer.change_email(Email(value=new_email))

        # Save updated customer
        updated_data = customer.model_dump()
        await self.customer_repository.update_customer(customer_id, updated_data)

        # Process domain events
        await self._process_domain_events(customer.get_events())

        self.logger.info(f"Customer {customer_id} email updated from {old_email} to {new_email}")
        return True

    async def _process_domain_events(self, events: List[Dict[str, Any]]) -> None:
        """Process customer domain events."""
        for event in events:
            if event["event_type"] == "customer_email_changed":
                await self.notification_service.send_email_change_notification(
                    event["old_email"],
                    event["new_email"]
                )
```

---

## 🧪 Testing Implementation

### **Comprehensive Test Suite**

Based on `flext/testing/declarative.py`:

```python
import pytest
import asyncio
from flext.testing.declarative import create_test_engine, TestResult
from entities import Order, Customer, Money, Email
from adapters import PostgreSQLAdapter, EmailAdapter
from services import OrderService, CustomerService

class TestHexagonalImplementation:
    """Test suite for hexagonal architecture implementation."""

    @pytest.fixture
    async def test_engine(self):
        """Create test engine for adapter testing."""
        return create_test_engine()

    @pytest.fixture
    async def database_adapter(self):
        """Create PostgreSQL adapter for testing."""
        return PostgreSQLAdapter(
            database_url="postgresql://test:test@localhost/test_db",
            pool_min_size=1,
            pool_max_size=5
        )

    @pytest.fixture
    async def email_adapter(self):
        """Create email adapter for testing."""
        return EmailAdapter(
            smtp_host="localhost",
            smtp_port=1025,  # MailHog test server
            smtp_username="test",
            smtp_password="test",
            from_email="test@example.com"
        )

    async def test_entity_lifecycle(self):
        """Test entity creation and lifecycle management."""
        # Test customer entity
        customer = Customer(
            name="John Doe",
            email=Email(value="john@example.com"),
            registration_date=datetime.utcnow()
        )

        assert customer.id is not None
        assert customer.is_active is True
        assert customer.version == 1

        # Test email change
        old_email = customer.email
        new_email = Email(value="john.doe@example.com")
        customer.change_email(new_email)

        assert customer.email == new_email
        assert customer.version == 2  # Version incremented
        assert len(customer.get_events()) == 1

        # Test order entity
        order = Order(
            customer_id=customer.id,
            created_at=datetime.utcnow()
        )

        # Add items
        order.add_item(
            product_id="PROD001",
            quantity=2,
            unit_price=Money(amount=10.99)
        )

        assert len(order.items) == 1
        assert order.total.amount == 21.98

        # Confirm order
        order.confirm()
        assert order.status == OrderStatus.CONFIRMED
        assert order.confirmed_at is not None
        assert len(order.get_events()) == 2  # Item added + order confirmed

    async def test_adapter_implementation(self, test_engine, database_adapter):
        """Test database adapter implementation."""
        async with test_engine.test_adapter(database_adapter) as adapter:
            # Test customer operations
            customer_data = {
                "id": "CUST001",
                "name": "Jane Doe",
                "email": {"value": "jane@example.com"},
                "registration_date": datetime.utcnow(),
                "is_active": True,
                "version": 1
            }

            customer_id = await adapter.save_customer(customer_data)
            assert customer_id == "CUST001"

            retrieved_customer = await adapter.find_customer_by_id(customer_id)
            assert retrieved_customer["name"] == "Jane Doe"
            assert retrieved_customer["email"]["value"] == "jane@example.com"

            # Test order operations
            order_data = {
                "id": "ORD001",
                "customer_id": customer_id,
                "status": "pending",
                "items": [{"product_id": "PROD001", "quantity": 1, "unit_price": {"amount": 15.99, "currency": "USD"}}],
                "total": {"amount": 15.99, "currency": "USD"},
                "created_at": datetime.utcnow(),
                "version": 1
            }

            order_id = await adapter.save_order(order_data)
            assert order_id == "ORD001"

            retrieved_order = await adapter.find_order_by_id(order_id)
            assert retrieved_order["customer_id"] == customer_id
            assert retrieved_order["status"] == "pending"

    async def test_application_service_integration(self, database_adapter, email_adapter):
        """Test full application service integration."""
        # Initialize services
        customer_service = CustomerService(database_adapter, email_adapter)
        order_service = OrderService(database_adapter, database_adapter, email_adapter)

        # Start adapters
        await database_adapter.connect()
        await email_adapter.connect()

        try:
            # Register customer
            customer_id = await customer_service.register_customer(
                "Integration Test User",
                "integration@example.com"
            )

            assert customer_id is not None

            # Create order
            order_id = await order_service.create_order(
                customer_id,
                [
                    {
                        "product_id": "PROD001",
                        "quantity": 2,
                        "unit_price": 25.50,
                        "currency": "USD"
                    },
                    {
                        "product_id": "PROD002",
                        "quantity": 1,
                        "unit_price": 15.99,
                        "currency": "USD"
                    }
                ]
            )

            assert order_id is not None

            # Confirm order
            success = await order_service.confirm_order(order_id)
            assert success is True

            # Verify order was confirmed
            order = await order_service.get_order(order_id)
            assert order["status"] == "confirmed"
            assert order["confirmed_at"] is not None

            # List customer orders
            orders = await order_service.list_customer_orders(customer_id)
            assert len(orders) == 1
            assert orders[0]["id"] == order_id

        finally:
            await database_adapter.disconnect()
            await email_adapter.disconnect()

    async def test_performance_metrics(self, test_engine, database_adapter):
        """Test adapter performance and metrics."""
        async with test_engine.test_adapter(database_adapter) as adapter:
            # Simulate load testing
            tasks = []
            for i in range(100):
                customer_data = {
                    "id": f"PERF_CUST_{i:03d}",
                    "name": f"Performance User {i}",
                    "email": {"value": f"perf{i}@example.com"},
                    "registration_date": datetime.utcnow(),
                    "is_active": True,
                    "version": 1
                }
                tasks.append(adapter.save_customer(customer_data))

            # Execute concurrent operations
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            # Verify results
            successful_operations = sum(1 for r in results if not isinstance(r, Exception))
            assert successful_operations >= 90  # At least 90% success rate

            # Check performance
            total_time = end_time - start_time
            ops_per_second = len(tasks) / total_time
            assert ops_per_second > 10  # At least 10 ops/second

            print(f"Performance test: {ops_per_second:.2f} ops/second, {successful_operations}/{len(tasks)} successful")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 📊 Production Examples

### **Complete Application Bootstrap**

Based on `flext/application/bootstrap.py`:

```python
from flext.application.bootstrap import Bootstrap, create_bootstrap
from flext.infra.config.hierarchical import HierarchicalConfig
from adapters import PostgreSQLAdapter, EmailAdapter
from services import OrderService, CustomerService
from pydantic import Field

class ProductionConfig(HierarchicalConfig):
    """Production application configuration."""

    # Database configuration
    database_url: str = Field(..., description="PostgreSQL connection URL")
    database_pool_min: int = Field(default=5, description="Min pool size")
    database_pool_max: int = Field(default=20, description="Max pool size")

    # Email configuration
    smtp_host: str = Field(..., description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: str = Field(..., description="SMTP username")
    smtp_password: str = Field(..., description="SMTP password")
    from_email: str = Field(..., description="From email address")

    # Application configuration
    app_name: str = Field(default="E-Commerce System", description="Application name")
    log_level: str = Field(default="INFO", description="Logging level")

async def create_production_application():
    """Create production application with all dependencies."""
    # Load configuration
    config = ProductionConfig(
        _env_file=".env",
        _env_prefix="APP_",
        _config_files=["config/base.yaml", "config/production.yaml"]
    )

    # Create bootstrap
    bootstrap = create_bootstrap(config.app_name)

    # Initialize adapters
    database_adapter = PostgreSQLAdapter(
        database_url=config.database_url,
        pool_min_size=config.database_pool_min,
        pool_max_size=config.database_pool_max
    )

    email_adapter = EmailAdapter(
        smtp_host=config.smtp_host,
        smtp_port=config.smtp_port,
        smtp_username=config.smtp_username,
        smtp_password=config.smtp_password,
        from_email=config.from_email
    )

    # Register adapters with bootstrap
    bootstrap.register_adapter("database", database_adapter)
    bootstrap.register_adapter("email", email_adapter)

    # Initialize services
    customer_service = CustomerService(database_adapter, email_adapter)
    order_service = OrderService(database_adapter, database_adapter, email_adapter)

    # Register services
    bootstrap.register_service("customer_service", customer_service)
    bootstrap.register_service("order_service", order_service)

    # Start application
    await bootstrap.start()

    return bootstrap

# Usage in main application
async def main():
    """Main application entry point."""
    app = await create_production_application()

    try:
        # Application is now running with all dependencies
        print("E-Commerce system started successfully!")

        # Get services for use
        customer_service = app.get_service("customer_service")
        order_service = app.get_service("order_service")

        # Example business operations
        customer_id = await customer_service.register_customer(
            "Production User",
            "production@example.com"
        )

        order_id = await order_service.create_order(
            customer_id,
            [{"product_id": "PROD001", "quantity": 1, "unit_price": 99.99}]
        )

        await order_service.confirm_order(order_id)

        print(f"Created customer {customer_id} and order {order_id}")

        # Keep application running
        await asyncio.sleep(3600)  # Run for 1 hour

    finally:
        # Graceful shutdown
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔗 **Cross-References**

### **⬅️ Prerequisites**

- [Architecture Hub](../../architecture/index.md) - Understanding hexagonal architecture patterns and design principles
- [FLEXT Technical Reference](../../api-reference/flext-technical-reference.md) - Detailed technical documentation of framework components

### **➡️ Next Steps**

- [Testing Guide](../testing/index.md) - Comprehensive testing strategies for hexagonal architecture
- [Oracle Integration Guide](../oracle/index.md) - Enterprise Oracle integration using these patterns
- [Security Implementation](../../security/architecture/security-architecture.md) - Security patterns for hexagonal architecture

### **🔗 Related Topics**

- [Development Hub](../../development/index.md) - Development tools and practices for implementing these patterns
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure services supporting hexagonal architecture
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating these implementation patterns
- [API Reference Hub](../../api-reference/index.md) - Complete API documentation for framework components

---

## 📊 **Document Information**

- **Status**: ✅ Complete
- **Last Updated**: June 11, 2025
- **Audience**: Framework developers, system architects, backend developers
- **Complexity**: Advanced

---

**📂 Content Guide** | **🏠 Hub**: [Guides](../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
