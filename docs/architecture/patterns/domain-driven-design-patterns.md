# 🏢 Domain-Driven Design Patterns

> **Document Type**: Implementation Guide | **Audience**: Senior developers, domain architects | **Scope**: Advanced DDD patterns in FLX Framework

[![DDD](https://img.shields.io/badge/patterns-DDD-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](../index.md)
[![Advanced](https://img.shields.io/badge/complexity-advanced-orange.svg)](../../development/index.md)

**Complete implementation guide for Domain-Driven Design patterns within FLX Framework hexagonal architecture**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture](../index.md) → **📂 Patterns**: [Index](./index.md) → **📂 Current**: Domain-Driven Design Patterns  

---

## 🎯 Overview

Domain-Driven Design (DDD) patterns in FLX enable sophisticated enterprise applications with complex business domains. This guide focuses on practical implementation of DDD concepts within the hexagonal architecture.

### **Key DDD Concepts**

- **🎯 Bounded Contexts**: Clear domain boundaries
- **🏛️ Aggregate Roots**: Consistency boundaries
- **💎 Value Objects**: Immutable domain concepts
- **📝 Domain Events**: Business occurrence capture
- **🔧 Domain Services**: Cross-aggregate business logic

---

## 🏛️ Bounded Contexts

### **Context Definition**

```python
# flx/domain/customers/context.py
from flx.core.base import DomainContext
from flx.core.domain import AggregateRoot, ValueObject, DomainEvent

class CustomerContext(DomainContext):
    """Customer management bounded context."""
    
    def __init__(self):
        super().__init__(name="customers")
        self.register_aggregates([Customer, CustomerAccount])
        self.register_value_objects([CustomerAddress, ContactInfo])
        self.register_domain_events([
            CustomerRegistered, CustomerUpdated, CustomerDeactivated
        ])
```

### **Aggregate Root Implementation**

```python
class Customer(AggregateRoot):
    """Customer aggregate with rich domain behavior."""
    
    def __init__(self, customer_id: CustomerId, personal_info: PersonalInfo):
        super().__init__(entity_id=customer_id)
        self.personal_info = personal_info
        self.addresses: list[CustomerAddress] = []
        self.contact_info: ContactInfo | None = None
        self.status = CustomerStatus.PENDING
        self.registration_date = datetime.utcnow()
    
    def register(self, contact_info: ContactInfo) -> None:
        """Register customer with contact information."""
        if self.status != CustomerStatus.PENDING:
            raise DomainError("Customer already registered")
        
        self.contact_info = contact_info
        self.status = CustomerStatus.ACTIVE
        
        # Raise domain event
        self.raise_event(CustomerRegistered(
            customer_id=self.id,
            email=contact_info.email,
            registration_date=self.registration_date
        ))
    
    def add_address(self, address: CustomerAddress) -> None:
        """Add address with business rules."""
        if len(self.addresses) >= 5:
            raise DomainError("Customer cannot have more than 5 addresses")
        
        # Ensure only one primary address
        if address.is_primary:
            for addr in self.addresses:
                addr.is_primary = False
        
        self.addresses.append(address)
        self.mark_modified()
    
    def change_email(self, new_email: str) -> None:
        """Change email with validation."""
        if not self.contact_info:
            raise DomainError("Customer must have contact info to change email")
        
        old_email = self.contact_info.email
        self.contact_info = self.contact_info.with_email(new_email)
        
        self.raise_event(CustomerEmailChanged(
            customer_id=self.id,
            old_email=old_email,
            new_email=new_email
        ))
        self.mark_modified()
```

---

## 💎 Value Objects

### **Immutable Domain Concepts**

```python
class CustomerAddress(ValueObject):
    """Customer address value object."""
    
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: bool = False
    address_type: AddressType = AddressType.SHIPPING
    
    def __post_init__(self):
        self.validate_postal_code()
    
    def validate_postal_code(self) -> None:
        """Validate postal code format."""
        if self.country == "US":
            if not re.match(r'^\d{5}(-\d{4})?$', self.postal_code):
                raise ValueError("Invalid US postal code format")
    
    def with_primary(self, is_primary: bool) -> 'CustomerAddress':
        """Return new address with updated primary status."""
        return CustomerAddress(
            street=self.street,
            city=self.city,
            state=self.state,
            postal_code=self.postal_code,
            country=self.country,
            is_primary=is_primary,
            address_type=self.address_type
        )

class ContactInfo(ValueObject):
    """Contact information value object."""
    
    email: str
    phone: str | None = None
    preferred_contact: ContactMethod = ContactMethod.EMAIL
    
    def __post_init__(self):
        self.validate_email()
    
    def validate_email(self) -> None:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.email):
            raise ValueError("Invalid email format")
    
    def with_email(self, email: str) -> 'ContactInfo':
        """Return new contact info with updated email."""
        return ContactInfo(
            email=email,
            phone=self.phone,
            preferred_contact=self.preferred_contact
        )
```

---

## 📝 Domain Events

### **Business Occurrence Capture**

```python
class CustomerRegistered(DomainEvent):
    """Customer registration domain event."""
    
    customer_id: CustomerId
    email: str
    registration_date: datetime

class CustomerEmailChanged(DomainEvent):
    """Customer email change domain event."""
    
    customer_id: CustomerId
    old_email: str
    new_email: str

class CustomerDeactivated(DomainEvent):
    """Customer deactivation domain event."""
    
    customer_id: CustomerId
    reason: str
    deactivation_date: datetime
```

---

## 🔧 Domain Services

### **Cross-Aggregate Business Logic**

```python
class CustomerDuplicationService(DomainService):
    """Service to check for customer duplication."""
    
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository
    
    async def is_duplicate(self, email: str, phone: str = None) -> bool:
        """Check if customer with same contact info exists."""
        # Check email duplication
        existing_by_email = await self.customer_repository.find_by_email(email)
        if existing_by_email:
            return True
        
        # Check phone duplication if provided
        if phone:
            existing_by_phone = await self.customer_repository.find_by_phone(phone)
            if existing_by_phone:
                return True
        
        return False
    
    async def find_similar_customers(self, customer: Customer) -> list[Customer]:
        """Find customers with similar information."""
        similar = []
        
        # Find by partial name match
        if customer.personal_info.last_name:
            name_matches = await self.customer_repository.find_by_last_name(
                customer.personal_info.last_name
            )
            similar.extend(name_matches)
        
        # Find by address similarity
        for address in customer.addresses:
            address_matches = await self.customer_repository.find_by_address_similarity(
                address.postal_code, address.street
            )
            similar.extend(address_matches)
        
        # Remove duplicates and self
        unique_similar = []
        seen_ids = {customer.id}
        for similar_customer in similar:
            if similar_customer.id not in seen_ids:
                unique_similar.append(similar_customer)
                seen_ids.add(similar_customer.id)
        
        return unique_similar

class CustomerLifecycleService(DomainService):
    """Service managing customer lifecycle."""
    
    def __init__(self, customer_repository: CustomerRepository,
                 account_repository: CustomerAccountRepository):
        self.customer_repository = customer_repository
        self.account_repository = account_repository
    
    async def complete_registration(self, customer: Customer,
                                  initial_account_settings: dict) -> None:
        """Complete customer registration process."""
        if customer.status != CustomerStatus.ACTIVE:
            raise DomainError("Customer must be active to complete registration")
        
        # Create customer account
        account = CustomerAccount(
            customer_id=customer.id,
            settings=AccountSettings(**initial_account_settings)
        )
        
        # Set up welcome workflow
        await self._setup_welcome_workflow(customer, account)
        
        # Save entities
        await self.customer_repository.save(customer)
        await self.account_repository.save(account)
    
    async def _setup_welcome_workflow(self, customer: Customer,
                                    account: CustomerAccount) -> None:
        """Setup welcome workflow for new customer."""
        # Create welcome tasks
        welcome_tasks = [
            WelcomeTask.VERIFY_EMAIL,
            WelcomeTask.COMPLETE_PROFILE,
            WelcomeTask.SETUP_PREFERENCES
        ]
        
        for task in welcome_tasks:
            account.add_onboarding_task(task)
```

---

## 🔗 Integration with Hexagonal Architecture

### **Repository Patterns**

```python
# Domain layer repository interface
class CustomerRepository(ABC):
    """Repository interface for customer aggregate."""
    
    @abstractmethod
    async def get(self, customer_id: CustomerId) -> Customer | None:
        """Get customer by ID."""
        pass
    
    @abstractmethod
    async def save(self, customer: Customer) -> None:
        """Save customer aggregate."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Customer | None:
        """Find customer by email."""
        pass

# Infrastructure layer implementation
class DatabaseCustomerRepository(CustomerRepository):
    """Database implementation of customer repository."""
    
    def __init__(self, database: DatabaseAdapter):
        self.database = database
    
    async def get(self, customer_id: CustomerId) -> Customer | None:
        """Get customer by ID from database."""
        query = "SELECT * FROM customers WHERE customer_id = ?"
        row = await self.database.fetch_one(query, [str(customer_id)])
        
        if not row:
            return None
        
        return Customer.from_dict(row)
    
    async def save(self, customer: Customer) -> None:
        """Save customer to database."""
        data = customer.to_dict()
        
        if customer.is_new():
            await self._insert_customer(data)
        else:
            await self._update_customer(data)
        
        # Publish domain events
        for event in customer.get_uncommitted_events():
            await self.event_bus.publish(event)
        
        customer.mark_events_as_committed()
```

---

## 🚀 Best Practices

### **DDD Implementation Guidelines**

1. **Keep Aggregates Small**: Focus on consistency boundaries
2. **Use Value Objects**: Immutable concepts with validation
3. **Domain Events**: Capture business occurrences
4. **Repository per Aggregate**: One repository per aggregate root
5. **Domain Services**: For cross-aggregate logic

### **Testing Strategies**

```python
class TestCustomerAggregate:
    """Test customer aggregate behavior."""
    
    def test_customer_registration(self):
        """Test customer registration process."""
        # Arrange
        customer_id = CustomerId.generate()
        personal_info = PersonalInfo(first_name="John", last_name="Doe")
        contact_info = ContactInfo(email="john@example.com")
        
        # Act
        customer = Customer(customer_id, personal_info)
        customer.register(contact_info)
        
        # Assert
        assert customer.status == CustomerStatus.ACTIVE
        assert customer.contact_info.email == "john@example.com"
        
        # Check domain event
        events = customer.get_uncommitted_events()
        assert len(events) == 1
        assert isinstance(events[0], CustomerRegistered)
    
    def test_address_business_rules(self):
        """Test address business rules."""
        # Arrange
        customer = self._create_active_customer()
        addresses = [self._create_address() for _ in range(5)]
        
        # Act - add 5 addresses (maximum)
        for address in addresses:
            customer.add_address(address)
        
        # Assert - adding 6th address should fail
        with pytest.raises(DomainError, match="cannot have more than 5 addresses"):
            customer.add_address(self._create_address())
```

---

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Architecture Hub](../index.md) - Essential hexagonal architecture patterns for understanding DDD implementation
- [Getting Started](../../getting-started/index.md) - Framework installation and basic concepts required for domain modeling
- [Core Domain Layer](../layers/core-domain-layer.md) - Foundation layer concepts underlying DDD patterns

### **➡️ Next Steps**

- [Event Sourcing Implementation](./event-sourcing-implementation.md) - Event-driven architecture patterns building on DDD concepts
- [CQRS Architecture Guide](./cqrs-architecture-guide.md) - Command-Query separation patterns for complex domains
- [Development Hub](../../development/index.md) - Development practices for implementing DDD patterns

### **🔗 Related Sections**

- [API Reference Hub](../../api-reference/index.md) - Complete API documentation for domain classes and DDD implementation
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating DDD patterns in practice
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure services supporting domain models and aggregates
- [Testing Guide](../../development/testing/index.md) - Testing strategies for domain-driven design implementations

---

**📂 Architecture**: [Patterns Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
