# 🏗️ Core Base Classes API Reference

> **Function**: Foundational domain object abstractions and base classes | **Audience**: Framework developers, domain modelers | **Status**: Production-Ready

[![Core](https://img.shields.io/badge/core-base_classes-blue.svg)](./index.md)
[![DDD](https://img.shields.io/badge/DDD-patterns-green.svg)](../../architecture/patterns/domain-driven-design-patterns.md)
[![Python](https://img.shields.io/badge/python-3.13+-orange.svg)](../../getting-started/setup/installation-guide.md)

**Foundational abstractions for building domain objects in FLX hexagonal architecture implementing Domain-Driven Design patterns with Python 3.13+ features and Pydantic validation - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [API Reference](../index.md) → **📂 Section**: [Core](./index.md) → **📄 Current**: Base Classes API

### **📍 Learning Path Position**

```
[API Reference Hub](../index.md) → [Core APIs](./index.md) → **[Base Classes]** → [Events API](./events.md)
```

## Overview

The Core Base module provides foundational abstractions for building domain objects in the FLX hexagonal architecture framework. It implements Domain-Driven Design (DDD) patterns using Python 3.13+ features and Pydantic for robust domain modeling with validation, immutability, and type safety.

## Classes

### DomainObject

Abstract base class for all domain objects in the FLX hexagonal architecture.

```python
from flx.core.base import DomainObject
from pydantic import Field

class Product(DomainObject):
    name: str = Field(min_length=1)
    price: Money
    category: str

    def apply_discount(self, percentage: float) -> Self:
        new_price = self.price.multiply(1 - percentage / 100)
        return self.model_copy(update={'price': new_price})
```

#### Configuration

| Property                  | Value  | Description                              |
| ------------------------- | ------ | ---------------------------------------- |
| `validate_assignment`     | `True` | All field assignments trigger validation |
| `arbitrary_types_allowed` | `True` | Supports complex domain types            |
| `frozen`                  | `True` | Enforces immutability for data integrity |
| `str_strip_whitespace`    | `True` | Automatic string normalization           |
| `use_enum_values`         | `True` | Consistent enum serialization            |

#### Key Features

- **Immutability by Default**: All domain objects are frozen to prevent accidental mutation
- **Automatic Field Validation**: Leverages Pydantic's runtime validation
- **Type Safety**: Full Python 3.13+ type system integration
- **Serialization Support**: Built-in JSON serialization/deserialization
- **Self-Documenting**: Rich type hints and field descriptions

### Identifiable

Mixin providing unique identity semantics for domain entities.

```python
from flx.core.base import DomainObject, Identifiable, Timestamped
from uuid import UUID
from pydantic import Field

class Customer(DomainObject, Identifiable, Timestamped):
    name: str = Field(min_length=1)
    email: str = Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')

    def update_contact_info(self, name: str = None, email: str = None) -> Self:
        updates = {'updated_at': datetime.now(UTC)}
        if name is not None:
            updates['name'] = name
        if email is not None:
            updates['email'] = email
        return self.model_copy(update=updates)
```

#### Attributes

| Attribute | Type   | Description                                       |
| --------- | ------ | ------------------------------------------------- |
| `id`      | `UUID` | Unique entity identifier, automatically generated |

#### Methods

##### `__eq__(other: object) -> bool`

Compare entities by identity rather than attributes.

**Parameters:**

- `other`: Object to compare with

**Returns:**

- `True` if both objects are Identifiable and have the same ID

**Example:**

```python
customer1 = Customer(id=customer_id, name="John Doe", email="john@example.com")
customer2 = Customer(id=customer_id, name="John Smith", email="john.smith@example.com")

assert customer1 == customer2  # Same identity = same entity
```

##### `__hash__() -> int`

Generate hash based on entity identity.

**Returns:**

- Hash value based on the entity's UUID for use in sets and dictionaries

**Example:**

```python
customers = {customer1, customer2}  # Same ID, so set contains only one
assert len(customers) == 1
```

#### Entity Identity Principles

- **Identity Over Attributes**: Two entities with the same ID are the same entity
- **Lifecycle Continuity**: Entity identity remains constant while attributes change
- **Reference Stability**: Provides stable references across aggregate boundaries
- **Equality Semantics**: Overrides default Pydantic equality with identity-based comparison

### Timestamped

Mixin providing comprehensive temporal tracking for domain entities.

```python
from flx.core.base import DomainObject, Identifiable, Timestamped
from datetime import datetime, UTC

class Order(DomainObject, Identifiable, Timestamped):
    customer_id: UUID
    total_amount: Money
    status: OrderStatus = OrderStatus.DRAFT

    def confirm_order(self) -> Self:
        return self.model_copy(update={
            'status': OrderStatus.CONFIRMED,
            'updated_at': datetime.now(UTC)
        })
```

#### Attributes

| Attribute    | Type               | Description                                                  |
| ------------ | ------------------ | ------------------------------------------------------------ |
| `created_at` | `datetime`         | Automatically set to current UTC time when object is created |
| `updated_at` | `datetime \| None` | Set to None initially, updated via domain operations         |

#### Methods

##### `touch() -> Self`

Update the updated_at timestamp to current UTC time.

**Returns:**

- New instance with updated timestamp

**Example:**

```python
updated_entity = entity.touch()
assert updated_entity.updated_at > entity.updated_at
```

#### Temporal Features

- **Automatic Creation Tracking**: Creation timestamp set during instantiation
- **Modification Tracking**: Optional updated_at timestamp tracks modifications
- **UTC Consistency**: All timestamps use UTC timezone for global consistency
- **Immutable History**: Timestamps cannot be arbitrarily changed
- **Precision**: Microsecond precision timestamps

### Versionable

Mixin providing optimistic concurrency control for domain entities.

```python
from flx.core.base import DomainObject, Identifiable, Versionable
from decimal import Decimal

class BankAccount(DomainObject, Identifiable, Timestamped, Versionable):
    account_number: str
    balance: Money

    def withdraw(self, amount: Money) -> Self:
        if self.balance.amount < amount.amount:
            raise ValueError("Insufficient funds")

        new_balance = Money(
            amount=self.balance.amount - amount.amount,
            currency=self.balance.currency
        )

        return self.model_copy(update={
            'balance': new_balance,
            'updated_at': datetime.now(UTC),
            'version': self.version + 1
        })
```

#### Attributes

| Attribute | Type  | Description                                                    |
| --------- | ----- | -------------------------------------------------------------- |
| `version` | `int` | Positive integer version starting at 1, incremented on updates |

#### Methods

##### `increment_version() -> Self`

Increment version number for optimistic locking.

**Returns:**

- New instance with incremented version number

**Example:**

```python
new_version = entity.increment_version()
assert new_version.version == entity.version + 1
```

#### Concurrency Control Features

- **Optimistic Locking**: Assumes conflicts are rare, checks at commit time
- **Version Tracking**: Monotonically increasing version number
- **Automatic Increment**: Version increments with each state change
- **Conflict Detection**: Enables repositories to detect concurrent modifications
- **Performance Optimized**: No locking overhead during operations

## Usage Patterns

### Value Objects

Value objects inherit from DomainObject only:

```python
from decimal import Decimal
from enum import Enum

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class Money(DomainObject):
    amount: Decimal = Field(ge=0)
    currency: Currency

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: Decimal) -> "Money":
        return Money(amount=self.amount * factor, currency=self.currency)

    def is_zero(self) -> bool:
        return self.amount == 0
```

### Domain Entities

Entities combine DomainObject with mixins:

```python
from uuid import UUID
from datetime import datetime, UTC

class Customer(DomainObject, Identifiable, Timestamped):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: str | None = None
    is_active: bool = True

    def change_email(self, new_email: str) -> Self:
        return self.model_copy(update={
            'email': new_email,
            'updated_at': datetime.now(UTC)
        })

    def deactivate(self) -> Self:
        return self.model_copy(update={
            'is_active': False,
            'updated_at': datetime.now(UTC)
        })
```

### Aggregate Roots

Aggregates use all mixins for full functionality:

```python
from enum import Enum
from typing import List

class OrderStatus(Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class OrderItem(DomainObject):
    product_id: UUID
    quantity: int = Field(gt=0)
    unit_price: Money

    @property
    def line_total(self) -> Money:
        return self.unit_price.multiply(Decimal(str(self.quantity)))

class Order(DomainObject, Identifiable, Timestamped, Versionable):
    customer_id: UUID
    items: list[OrderItem] = Field(default_factory=list)
    status: OrderStatus = OrderStatus.DRAFT

    @property
    def total_amount(self) -> Money:
        if not self.items:
            return Money(amount=Decimal('0'), currency=Currency.USD)

        total = Money(amount=Decimal('0'), currency=self.items[0].unit_price.currency)
        for item in self.items:
            total = total.add(item.line_total)
        return total

    def add_item(self, product_id: UUID, quantity: int, unit_price: Money) -> Self:
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Cannot modify confirmed order")

        new_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )

        return self.model_copy(update={
            'items': self.items + [new_item],
            'updated_at': datetime.now(UTC),
            'version': self.version + 1
        })

    def confirm(self) -> Self:
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Can only confirm draft orders")

        if not self.items:
            raise ValueError("Cannot confirm empty order")

        return self.model_copy(update={
            'status': OrderStatus.CONFIRMED,
            'updated_at': datetime.now(UTC),
            'version': self.version + 1
        })
```

## Repository Integration

### Basic Repository Pattern

```python
from abc import ABC, abstractmethod

class CustomerRepository(ABC):
    @abstractmethod
    async def find_by_id(self, customer_id: UUID) -> Customer | None:
        pass

    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        pass

class SqlCustomerRepository(CustomerRepository):
    async def save(self, customer: Customer) -> Customer:
        # Implementation with optimistic locking for Versionable entities
        if isinstance(customer, Versionable):
            current = await self.find_by_id(customer.id)
            if current and current.version != customer.version - 1:
                raise ConcurrencyError("Entity was modified by another process")

        # Proceed with save...
        return customer
```

### Domain Services

```python
class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    async def update_customer_email(self, customer_id: UUID, new_email: str) -> Customer:
        customer = await self.repository.find_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)

        updated_customer = customer.change_email(new_email)
        return await self.repository.save(updated_customer)
```

## Best Practices

### Domain Modeling

1. **Rich Domain Models**: Implement business logic as methods on domain objects
2. **Ubiquitous Language**: Use terminology directly from business conversations
3. **Invariant Protection**: Use validation and business rules to protect domain invariants
4. **Immutable Updates**: Always use model_copy() for state changes
5. **Self-Contained Objects**: Include all necessary business logic within the domain object

### Validation

```python
from pydantic import field_validator

class Product(DomainObject):
    name: str
    price: Money

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Product name cannot be empty")
        return v.title()  # Normalize to title case

    @field_validator('price')
    @classmethod
    def validate_positive_price(cls, v: Money) -> Money:
        if v.amount <= 0:
            raise ValueError("Product price must be positive")
        return v
```

### Concurrency Handling

```python
class TransferService:
    async def transfer_money(
        self,
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Money
    ) -> tuple[BankAccount, BankAccount]:
        max_retries = 3

        for attempt in range(max_retries):
            try:
                from_account = await self.repository.find_by_id(from_account_id)
                to_account = await self.repository.find_by_id(to_account_id)

                updated_from = from_account.withdraw(amount)
                updated_to = to_account.deposit(amount)

                saved_from = await self.repository.save(updated_from)
                saved_to = await self.repository.save(updated_to)

                return saved_from, saved_to

            except ConcurrencyError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.1 * (2 ** attempt))
```

## Error Handling

Common exceptions and handling patterns:

```python
from pydantic import ValidationError

try:
    customer = Customer(
        name="",  # Invalid: empty name
        email="invalid-email"  # Invalid: malformed email
    )
except ValidationError as e:
    # Handle validation errors
    for error in e.errors():
        print(f"Field {error['loc']}: {error['msg']}")

try:
    order = Order()
    confirmed_order = order.confirm()  # Business rule violation
except ValueError as e:
    # Handle business rule violations
    print(f"Business rule error: {e}")
```

## Testing

### Unit Testing with Fixed Data

```python
import pytest
from unittest.mock import patch
from datetime import datetime, UTC

def test_customer_creation():
    customer = Customer(
        name="John Doe",
        email="john@example.com"
    )

    assert customer.name == "John Doe"
    assert customer.email == "john@example.com"
    assert customer.is_active is True

def test_timestamped_behavior():
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        customer = Customer(name="Test", email="test@example.com")
        assert customer.created_at == fixed_time

        updated_customer = customer.touch()
        assert updated_customer.updated_at == fixed_time

def test_identity_based_equality():
    customer_id = UUID('550e8400-e29b-41d4-a716-446655440000')
    customer1 = Customer(id=customer_id, name="John", email="john@example.com")
    customer2 = Customer(id=customer_id, name="Jane", email="jane@example.com")

    assert customer1 == customer2  # Same ID
    assert hash(customer1) == hash(customer2)  # Same hash

    customers = {customer1, customer2}
    assert len(customers) == 1  # Only one unique customer by identity
```

### Concurrency Testing

```python
async def test_optimistic_locking():
    account = BankAccount(
        account_number="123456",
        balance=Money(amount=Decimal('1000'), currency=Currency.USD)
    )

    # Simulate concurrent withdrawals
    withdrawal1 = account.withdraw(Money(amount=Decimal('100'), currency=Currency.USD))
    withdrawal2 = account.withdraw(Money(amount=Decimal('200'), currency=Currency.USD))

    # First save succeeds
    await repository.save(withdrawal1)

    # Second save should fail due to version conflict
    with pytest.raises(ConcurrencyError):
        await repository.save(withdrawal2)
```

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Architecture Foundation**](../../architecture/design/unified-architecture-guide.md) - Hexagonal architecture patterns essential for understanding domain object placement
- [**Core API Hub**](./index.md) - Core API overview and fundamental concepts required for base class usage
- [**Framework Installation**](../../getting-started/setup/installation-guide.md) - Python 3.13+ setup required for advanced type features

### **➡️ Implementation Next Steps**

- [**Domain Events API**](./events.md) - Event-driven patterns building on base domain objects for cross-aggregate communication
- [**Complete API Reference**](../comprehensive/flx-complete-api.md) - Full framework API documentation extending base class concepts
- [**Real-World Implementation Examples**](../../examples/real-world-implementations.md) - Production examples demonstrating base class usage patterns

### **🔗 Related Implementation Topics**

- [**Domain-Driven Design Patterns**](../../architecture/patterns/domain-driven-design-patterns.md) - Advanced DDD patterns building on these base class foundations
- [**Testing Domain Objects**](../../development/testing/hexagonal-testing-guide.md) - Testing strategies for domain objects and base class validation
- [**Infrastructure Integration**](../../infrastructure/service-patterns.md) - Infrastructure services working with domain objects and persistence patterns
- [**Oracle Integration Examples**](../../examples/oracle-integration-real-examples.md) - Real Oracle integration examples using base classes for entity modeling
- [**Performance Optimization**](../../optimization/performance/optimization-guide.md) - Performance considerations for domain object usage and optimization strategies
- [**Security Patterns**](../../security/architecture/security-architecture.md) - Security implementation patterns for domain objects and data protection

---

**📂 API Reference** | **🏠 Parent**: [Core APIs Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11

```

```
