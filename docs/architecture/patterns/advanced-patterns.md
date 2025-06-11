# 🏛️ Advanced Architecture Patterns

> **Function**: Advanced architectural patterns for hexagonal architecture | **Audience**: Senior architects, framework developers | **Status**: Production-Ready

[![Patterns](https://img.shields.io/badge/patterns-advanced-blue.svg)](./advanced-patterns-hub.md)
[![DDD](https://img.shields.io/badge/DDD-implemented-green.svg)](./domain-driven-design-patterns.md)
[![Event](https://img.shields.io/badge/event_sourcing-validated-orange.svg)](./event-sourcing-implementation.md)

**Advanced architectural patterns for FLX Framework including DDD, Event Sourcing, CQRS, and microservices patterns - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture](../index.md) → **📂 Section**: [Patterns](./index.md) → **📄 Current**: Advanced Patterns

### **📍 Learning Path Position**

```
[Architecture Hub](../index.md) → [Patterns Section](./index.md) → **[Advanced Patterns]** → [Domain-Driven Design](./domain-driven-design-patterns.md)
```

**⚠️ This document has been modularized for better accessibility. Please visit the [Advanced Patterns Hub](./advanced-patterns-hub.md) for structured navigation to all advanced patterns.**

## 🎯 Quick Navigation

This comprehensive guide has been broken down into focused, specialized documents for optimal learning:

### **🏛️ Core Patterns**

- **[Advanced Patterns Hub](advanced-patterns-hub.md)** - **Central navigation center**
- **[Domain-Driven Design Patterns](domain-driven-design-patterns.md)** - Rich domain models and bounded contexts
- **[Event Sourcing Implementation](event-sourcing-implementation.md)** - Event-driven state management
- **[CQRS Architecture Guide](cqrs-architecture-guide.md)** - Command-Query separation
- **[Microservices Patterns](microservices-patterns.md)** - Distributed service architecture
- **[Reactive Programming Guide](reactive-programming-guide.md)** - Async/await with reactive streams

### **🎓 Learning Paths**

- **Beginner**: Start with [Domain-Driven Design Patterns](domain-driven-design-patterns.md)
- **Intermediate**: Progress to [Event Sourcing Implementation](event-sourcing-implementation.md)
- **Advanced**: Master [Microservices Patterns](microservices-patterns.md)
- **Expert**: Combine with [Reactive Programming Guide](reactive-programming-guide.md)

---

## 📚 Modularized Content Overview

The original 1,179-line document has been restructured into focused modules following the **progressive disclosure pattern**:

### **🎯 Benefits of Modularization**

- **Focused Learning**: Each document covers one major pattern in depth
- **Progressive Complexity**: Learn at your own pace with clear prerequisites
- **Better Navigation**: Hub-based navigation with role-based access
- **Improved Maintenance**: Easier to update and maintain individual patterns
- **Enhanced Searchability**: Specific topics are easier to find and reference

## 🎯 Domain-Driven Design (DDD)

### **Bounded Contexts**

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

# Customer Aggregate Root
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
    
    def deactivate(self, reason: str) -> None:
        """Deactivate customer account."""
        if self.status == CustomerStatus.INACTIVE:
            raise DomainError("Customer already inactive")
        
        self.status = CustomerStatus.INACTIVE
        
        self.raise_event(CustomerDeactivated(
            customer_id=self.id,
            reason=reason,
            deactivation_date=datetime.utcnow()
        ))
        self.mark_modified()

# Value Objects
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

# Domain Events
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

### **Domain Services**

```python
# flx/domain/customers/services.py
from flx.core.domain import DomainService

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

## 📝 Event Sourcing

### **Event Store Implementation**

```python
# flx/infrastructure/event_store.py
from flx.core.events import EventStore, Event, EventStream
from flx.adapters.outbound.database import DatabaseAdapter

class FLXEventStore(EventStore):
    """FLX Event Store implementation with optimistic concurrency."""
    
    def __init__(self, database: DatabaseAdapter):
        self.database = database
    
    async def save_events(self, stream_id: str, events: list[Event],
                         expected_version: int) -> None:
        """Save events to stream with optimistic concurrency."""
        async with self.database.transaction() as tx:
            # Check current version
            current_version = await self._get_stream_version(tx, stream_id)
            
            if current_version != expected_version:
                raise ConcurrencyError(
                    f"Stream {stream_id} version mismatch. "
                    f"Expected {expected_version}, got {current_version}"
                )
            
            # Save events
            for i, event in enumerate(events):
                event_version = expected_version + i + 1
                await self._save_event(tx, stream_id, event, event_version)
            
            # Update stream metadata
            await self._update_stream_metadata(
                tx, stream_id, expected_version + len(events)
            )
    
    async def load_events(self, stream_id: str,
                         from_version: int = 0) -> EventStream:
        """Load events from stream starting from version."""
        query = """
            SELECT event_id, event_type, event_data, event_metadata, 
                   version, timestamp
            FROM events 
            WHERE stream_id = ? AND version > ?
            ORDER BY version ASC
        """
        
        rows = await self.database.fetch_all(query, [stream_id, from_version])
        
        events = []
        for row in rows:
            event = Event(
                event_id=row['event_id'],
                event_type=row['event_type'],
                data=json.loads(row['event_data']),
                metadata=json.loads(row['event_metadata']),
                version=row['version'],
                timestamp=row['timestamp']
            )
            events.append(event)
        
        return EventStream(stream_id=stream_id, events=events)
    
    async def load_aggregate(self, aggregate_id: str,
                           aggregate_type: type) -> AggregateRoot:
        """Load aggregate from event stream."""
        stream = await self.load_events(aggregate_id)
        
        # Create aggregate instance
        aggregate = aggregate_type.create_empty(aggregate_id)
        
        # Apply all events
        for event in stream.events:
            aggregate.apply_event(event)
        
        # Mark aggregate as loaded (clear pending events)
        aggregate.mark_events_as_committed()
        
        return aggregate
    
    async def save_aggregate(self, aggregate: AggregateRoot) -> None:
        """Save aggregate by persisting uncommitted events."""
        if not aggregate.has_uncommitted_events():
            return
        
        uncommitted_events = aggregate.get_uncommitted_events()
        expected_version = aggregate.version - len(uncommitted_events)
        
        await self.save_events(
            stream_id=str(aggregate.id),
            events=uncommitted_events,
            expected_version=expected_version
        )
        
        aggregate.mark_events_as_committed()

# Event-Sourced Aggregate
class EventSourcedCustomer(AggregateRoot):
    """Event-sourced customer aggregate."""
    
    def __init__(self, customer_id: CustomerId):
        super().__init__(entity_id=customer_id)
        self.personal_info: PersonalInfo | None = None
        self.contact_info: ContactInfo | None = None
        self.addresses: list[CustomerAddress] = []
        self.status = CustomerStatus.PENDING
        self.registration_date: datetime | None = None
    
    @classmethod
    def create(cls, customer_id: CustomerId, personal_info: PersonalInfo) -> 'EventSourcedCustomer':
        """Create new customer aggregate."""
        customer = cls(customer_id)
        
        # Raise creation event
        customer.raise_event(CustomerCreated(
            customer_id=customer_id,
            personal_info=personal_info,
            created_at=datetime.utcnow()
        ))
        
        return customer
    
    def register(self, contact_info: ContactInfo) -> None:
        """Register customer."""
        if self.status != CustomerStatus.PENDING:
            raise DomainError("Customer already registered")
        
        self.raise_event(CustomerRegistered(
            customer_id=self.id,
            contact_info=contact_info,
            registration_date=datetime.utcnow()
        ))
    
    # Event handlers (for rebuilding state from events)
    def _handle_customer_created(self, event: CustomerCreated) -> None:
        """Handle customer created event."""
        self.personal_info = event.personal_info
        self.registration_date = event.created_at
    
    def _handle_customer_registered(self, event: CustomerRegistered) -> None:
        """Handle customer registered event."""
        self.contact_info = event.contact_info
        self.status = CustomerStatus.ACTIVE
        if not self.registration_date:
            self.registration_date = event.registration_date
    
    def _handle_customer_email_changed(self, event: CustomerEmailChanged) -> None:
        """Handle email changed event."""
        if self.contact_info:
            self.contact_info = self.contact_info.with_email(event.new_email)
    
    def _handle_customer_address_added(self, event: CustomerAddressAdded) -> None:
        """Handle address added event."""
        # Ensure only one primary address
        if event.address.is_primary:
            for addr in self.addresses:
                addr.is_primary = False
        
        self.addresses.append(event.address)
```

### **Event Projections**

```python
# flx/projections/customer_projections.py
from flx.core.projections import Projection, ProjectionHandler

class CustomerListProjection(Projection):
    """Customer list view projection."""
    
    def __init__(self, database: DatabaseAdapter):
        super().__init__(name="customer_list")
        self.database = database
    
    @ProjectionHandler(CustomerCreated)
    async def handle_customer_created(self, event: CustomerCreated) -> None:
        """Handle customer created event."""
        await self.database.execute("""
            INSERT INTO customer_list_view (
                customer_id, first_name, last_name, status, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, [
            str(event.customer_id),
            event.personal_info.first_name,
            event.personal_info.last_name,
            "pending",
            event.created_at
        ])
    
    @ProjectionHandler(CustomerRegistered)
    async def handle_customer_registered(self, event: CustomerRegistered) -> None:
        """Handle customer registered event."""
        await self.database.execute("""
            UPDATE customer_list_view 
            SET status = 'active', email = ?, registered_at = ?
            WHERE customer_id = ?
        """, [
            event.contact_info.email,
            event.registration_date,
            str(event.customer_id)
        ])
    
    @ProjectionHandler(CustomerDeactivated)
    async def handle_customer_deactivated(self, event: CustomerDeactivated) -> None:
        """Handle customer deactivated event."""
        await self.database.execute("""
            UPDATE customer_list_view 
            SET status = 'inactive', deactivated_at = ?
            WHERE customer_id = ?
        """, [
            event.deactivation_date,
            str(event.customer_id)
        ])

class CustomerStatisticsProjection(Projection):
    """Customer statistics projection."""
    
    def __init__(self, cache: CacheAdapter):
        super().__init__(name="customer_statistics")
        self.cache = cache
    
    @ProjectionHandler(CustomerRegistered)
    async def handle_customer_registered(self, event: CustomerRegistered) -> None:
        """Update registration statistics."""
        today = event.registration_date.date().isoformat()
        
        # Increment daily registration count
        await self.cache.increment(f"registrations:daily:{today}")
        
        # Increment monthly registration count
        month = event.registration_date.strftime("%Y-%m")
        await self.cache.increment(f"registrations:monthly:{month}")
        
        # Update total customer count
        await self.cache.increment("customers:total")
    
    @ProjectionHandler(CustomerDeactivated)
    async def handle_customer_deactivated(self, event: CustomerDeactivated) -> None:
        """Update deactivation statistics."""
        today = event.deactivation_date.date().isoformat()
        
        # Increment daily deactivation count
        await self.cache.increment(f"deactivations:daily:{today}")
        
        # Decrement total active customer count
        await self.cache.decrement("customers:active")
```

## 🔄 CQRS (Command Query Responsibility Segregation)

### **Command Side**

```python
# flx/application/commands/customer_commands.py
from flx.core.commands import Command, CommandHandler
from flx.core.events import EventBus

class RegisterCustomerCommand(Command):
    """Command to register a new customer."""
    
    customer_id: CustomerId
    personal_info: PersonalInfo
    contact_info: ContactInfo
    initial_address: CustomerAddress | None = None

class ChangeCustomerEmailCommand(Command):
    """Command to change customer email."""
    
    customer_id: CustomerId
    new_email: str
    change_reason: str

class DeactivateCustomerCommand(Command):
    """Command to deactivate customer."""
    
    customer_id: CustomerId
    reason: str
    requested_by: str

# Command Handlers
class CustomerCommandHandlers:
    """Command handlers for customer operations."""
    
    def __init__(self, 
                 customer_repository: CustomerRepository,
                 event_bus: EventBus,
                 duplication_service: CustomerDuplicationService):
        self.customer_repository = customer_repository
        self.event_bus = event_bus
        self.duplication_service = duplication_service
    
    @CommandHandler(RegisterCustomerCommand)
    async def handle_register_customer(self, command: RegisterCustomerCommand) -> None:
        """Handle customer registration command."""
        # Check for duplicates
        is_duplicate = await self.duplication_service.is_duplicate(
            email=command.contact_info.email,
            phone=command.contact_info.phone
        )
        
        if is_duplicate:
            raise DomainError("Customer with this contact information already exists")
        
        # Create customer
        customer = EventSourcedCustomer.create(
            customer_id=command.customer_id,
            personal_info=command.personal_info
        )
        
        # Register customer
        customer.register(command.contact_info)
        
        # Add initial address if provided
        if command.initial_address:
            customer.add_address(command.initial_address)
        
        # Save customer
        await self.customer_repository.save(customer)
        
        # Publish domain events
        for event in customer.get_uncommitted_events():
            await self.event_bus.publish(event)
    
    @CommandHandler(ChangeCustomerEmailCommand)
    async def handle_change_customer_email(self, command: ChangeCustomerEmailCommand) -> None:
        """Handle email change command."""
        # Load customer
        customer = await self.customer_repository.get(command.customer_id)
        if not customer:
            raise EntityNotFoundError(f"Customer {command.customer_id} not found")
        
        # Check if new email is already in use
        is_duplicate = await self.duplication_service.is_duplicate(
            email=command.new_email
        )
        
        if is_duplicate:
            raise DomainError("Email address already in use")
        
        # Change email
        customer.change_email(command.new_email)
        
        # Save customer
        await self.customer_repository.save(customer)
        
        # Publish events
        for event in customer.get_uncommitted_events():
            await self.event_bus.publish(event)
    
    @CommandHandler(DeactivateCustomerCommand)
    async def handle_deactivate_customer(self, command: DeactivateCustomerCommand) -> None:
        """Handle customer deactivation command."""
        # Load customer
        customer = await self.customer_repository.get(command.customer_id)
        if not customer:
            raise EntityNotFoundError(f"Customer {command.customer_id} not found")
        
        # Deactivate customer
        customer.deactivate(command.reason)
        
        # Save customer
        await self.customer_repository.save(customer)
        
        # Publish events
        for event in customer.get_uncommitted_events():
            await self.event_bus.publish(event)
```

### **Query Side**

```python
# flx/application/queries/customer_queries.py
from flx.core.queries import Query, QueryHandler
from flx.infrastructure.read_models import CustomerReadModel

class GetCustomerQuery(Query):
    """Query to get customer by ID."""
    
    customer_id: CustomerId

class SearchCustomersQuery(Query):
    """Query to search customers."""
    
    search_term: str | None = None
    status_filter: CustomerStatus | None = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "registration_date"
    sort_order: str = "desc"

class GetCustomerStatisticsQuery(Query):
    """Query to get customer statistics."""
    
    date_range: DateRange | None = None
    group_by: str = "day"  # day, week, month

# Query Handlers
class CustomerQueryHandlers:
    """Query handlers for customer read operations."""
    
    def __init__(self, 
                 read_model: CustomerReadModel,
                 cache: CacheAdapter):
        self.read_model = read_model
        self.cache = cache
    
    @QueryHandler(GetCustomerQuery)
    async def handle_get_customer(self, query: GetCustomerQuery) -> CustomerView | None:
        """Handle get customer query."""
        # Try cache first
        cache_key = f"customer:view:{query.customer_id}"
        cached_view = await self.cache.get(cache_key)
        
        if cached_view:
            return CustomerView.parse_obj(cached_view)
        
        # Load from read model
        customer_data = await self.read_model.get_customer(query.customer_id)
        
        if not customer_data:
            return None
        
        customer_view = CustomerView(**customer_data)
        
        # Cache for 1 hour
        await self.cache.set(cache_key, customer_view.dict(), ttl=3600)
        
        return customer_view
    
    @QueryHandler(SearchCustomersQuery)
    async def handle_search_customers(self, query: SearchCustomersQuery) -> CustomerSearchResult:
        """Handle customer search query."""
        # Build search criteria
        criteria = {}
        
        if query.search_term:
            criteria['search_term'] = query.search_term
        
        if query.status_filter:
            criteria['status'] = query.status_filter
        
        # Execute search
        result = await self.read_model.search_customers(
            criteria=criteria,
            page=query.page,
            page_size=query.page_size,
            sort_by=query.sort_by,
            sort_order=query.sort_order
        )
        
        return CustomerSearchResult(
            customers=[CustomerListView(**customer) for customer in result['items']],
            total_count=result['total_count'],
            page=query.page,
            page_size=query.page_size,
            total_pages=math.ceil(result['total_count'] / query.page_size)
        )
    
    @QueryHandler(GetCustomerStatisticsQuery)
    async def handle_get_customer_statistics(self, query: GetCustomerStatisticsQuery) -> CustomerStatistics:
        """Handle customer statistics query."""
        # Generate cache key
        cache_key = f"customer:stats:{query.group_by}"
        if query.date_range:
            cache_key += f":{query.date_range.start}:{query.date_range.end}"
        
        # Try cache first (5 minute TTL for statistics)
        cached_stats = await self.cache.get(cache_key)
        if cached_stats:
            return CustomerStatistics.parse_obj(cached_stats)
        
        # Calculate statistics
        stats_data = await self.read_model.get_customer_statistics(
            date_range=query.date_range,
            group_by=query.group_by
        )
        
        statistics = CustomerStatistics(**stats_data)
        
        # Cache for 5 minutes
        await self.cache.set(cache_key, statistics.dict(), ttl=300)
        
        return statistics

# Read Models and Views
class CustomerView(BaseModel):
    """Customer detail view."""
    
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    status: CustomerStatus
    registration_date: datetime
    addresses: list[CustomerAddressView]
    account_settings: dict[str, Any]

class CustomerListView(BaseModel):
    """Customer list item view."""
    
    customer_id: str
    full_name: str
    email: str
    status: CustomerStatus
    registration_date: datetime
    last_activity: datetime | None

class CustomerSearchResult(BaseModel):
    """Customer search result."""
    
    customers: list[CustomerListView]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class CustomerStatistics(BaseModel):
    """Customer statistics."""
    
    total_customers: int
    active_customers: int
    registrations_today: int
    registrations_this_month: int
    deactivations_today: int
    growth_rate: float
    time_series: list[CustomerTimeSeriesPoint]
```

## 🏗️ Microservices Architecture

### **Service Boundaries**

```python
# flx/microservices/customer_service.py
from flx.core.microservices import MicroserviceBase

class CustomerMicroservice(MicroserviceBase):
    """Customer management microservice."""
    
    def __init__(self):
        super().__init__(
            service_name="customer-service",
            version="1.0.0",
            dependencies=["notification-service", "audit-service"]
        )
        
        # Service-specific configuration
        self.database_config = DatabaseConfig(
            host=os.getenv("CUSTOMER_DB_HOST"),
            database=os.getenv("CUSTOMER_DB_NAME")
        )
        
        # Message broker for inter-service communication
        self.message_broker = MessageBroker(
            broker_url=os.getenv("MESSAGE_BROKER_URL")
        )
    
    async def initialize(self) -> None:
        """Initialize microservice."""
        # Initialize database connection
        self.database = await DatabaseAdapter.create(self.database_config)
        
        # Initialize repositories
        self.customer_repository = CustomerRepository(self.database)
        
        # Initialize command/query handlers
        self.command_handlers = CustomerCommandHandlers(
            customer_repository=self.customer_repository,
            event_bus=self.event_bus,
            duplication_service=CustomerDuplicationService(self.customer_repository)
        )
        
        self.query_handlers = CustomerQueryHandlers(
            read_model=CustomerReadModel(self.database),
            cache=self.cache
        )
        
        # Register API endpoints
        await self.register_endpoints()
        
        # Subscribe to external events
        await self.subscribe_to_events()
    
    async def register_endpoints(self) -> None:
        """Register HTTP API endpoints."""
        
        @self.router.post("/customers")
        async def create_customer(request: CreateCustomerRequest) -> CustomerResponse:
            """Create new customer endpoint."""
            command = RegisterCustomerCommand(
                customer_id=CustomerId.generate(),
                personal_info=request.personal_info,
                contact_info=request.contact_info,
                initial_address=request.initial_address
            )
            
            await self.command_bus.send(command)
            
            return CustomerResponse(
                customer_id=str(command.customer_id),
                status="created"
            )
        
        @self.router.get("/customers/{customer_id}")
        async def get_customer(customer_id: str) -> CustomerView:
            """Get customer endpoint."""
            query = GetCustomerQuery(customer_id=CustomerId(customer_id))
            result = await self.query_bus.send(query)
            
            if not result:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            return result
        
        @self.router.get("/customers")
        async def search_customers(
            search_term: str = None,
            status: CustomerStatus = None,
            page: int = 1,
            page_size: int = 20
        ) -> CustomerSearchResult:
            """Search customers endpoint."""
            query = SearchCustomersQuery(
                search_term=search_term,
                status_filter=status,
                page=page,
                page_size=page_size
            )
            
            return await self.query_bus.send(query)
    
    async def subscribe_to_events(self) -> None:
        """Subscribe to external domain events."""
        
        # Subscribe to order events from order service
        @self.message_broker.subscribe("order.created")
        async def handle_order_created(event: OrderCreated) -> None:
            """Handle order created from order service."""
            # Update customer last activity
            await self.customer_repository.update_last_activity(
                event.customer_id, 
                event.created_at
            )
        
        # Subscribe to payment events
        @self.message_broker.subscribe("payment.completed")
        async def handle_payment_completed(event: PaymentCompleted) -> None:
            """Handle payment completed event."""
            # Update customer payment history
            customer = await self.customer_repository.get(event.customer_id)
            if customer:
                customer.record_payment(event.amount, event.payment_date)
                await self.customer_repository.save(customer)

# Service Registry and Discovery
class ServiceRegistry:
    """Service registry for microservice discovery."""
    
    def __init__(self, registry_backend: RegistryBackend):
        self.backend = registry_backend
        self.services: dict[str, ServiceInfo] = {}
    
    async def register_service(self, service: MicroserviceBase) -> None:
        """Register service with registry."""
        service_info = ServiceInfo(
            name=service.service_name,
            version=service.version,
            host=service.host,
            port=service.port,
            health_check_url=f"http://{service.host}:{service.port}/health",
            metadata=service.metadata
        )
        
        await self.backend.register(service_info)
        self.services[service.service_name] = service_info
    
    async def discover_service(self, service_name: str) -> ServiceInfo | None:
        """Discover service by name."""
        if service_name in self.services:
            return self.services[service_name]
        
        service_info = await self.backend.discover(service_name)
        if service_info:
            self.services[service_name] = service_info
        
        return service_info
    
    async def get_healthy_instances(self, service_name: str) -> list[ServiceInfo]:
        """Get healthy instances of a service."""
        return await self.backend.get_healthy_instances(service_name)

# Inter-Service Communication
class InterServiceClient:
    """Client for inter-service communication."""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.registry = service_registry
        self.http_client = httpx.AsyncClient()
    
    async def call_service(self, service_name: str, endpoint: str,
                          method: str = "GET", data: dict = None) -> dict:
        """Call another microservice."""
        service_info = await self.registry.discover_service(service_name)
        if not service_info:
            raise ServiceNotFoundError(f"Service {service_name} not found")
        
        url = f"http://{service_info.host}:{service_info.port}{endpoint}"
        
        try:
            if method == "GET":
                response = await self.http_client.get(url)
            elif method == "POST":
                response = await self.http_client.post(url, json=data)
            elif method == "PUT":
                response = await self.http_client.put(url, json=data)
            elif method == "DELETE":
                response = await self.http_client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise InterServiceCommunicationError(
                f"Failed to call {service_name}: {str(e)}"
            )
```

### **Service Orchestration**

```python
# flx/microservices/orchestration.py
from flx.core.orchestration import Saga, SagaStep

class CustomerRegistrationSaga(Saga):
    """Saga for customer registration across multiple services."""
    
    def __init__(self, inter_service_client: InterServiceClient):
        super().__init__(saga_name="customer_registration")
        self.client = inter_service_client
    
    @SagaStep(name="create_customer_record")
    async def create_customer_record(self, context: SagaContext) -> SagaStepResult:
        """Step 1: Create customer record."""
        try:
            result = await self.client.call_service(
                "customer-service",
                "/customers",
                method="POST",
                data=context.customer_data
            )
            
            context.customer_id = result["customer_id"]
            return SagaStepResult.success(data={"customer_id": result["customer_id"]})
            
        except Exception as e:
            return SagaStepResult.failure(error=str(e))
    
    @SagaStep(name="create_customer_record", compensation=True)
    async def compensate_create_customer_record(self, context: SagaContext) -> SagaStepResult:
        """Compensation: Delete customer record."""
        try:
            await self.client.call_service(
                "customer-service",
                f"/customers/{context.customer_id}",
                method="DELETE"
            )
            return SagaStepResult.success()
        except Exception as e:
            return SagaStepResult.failure(error=str(e))
    
    @SagaStep(name="setup_customer_account")
    async def setup_customer_account(self, context: SagaContext) -> SagaStepResult:
        """Step 2: Setup customer account in account service."""
        try:
            account_data = {
                "customer_id": context.customer_id,
                "account_type": context.account_type,
                "initial_settings": context.account_settings
            }
            
            result = await self.client.call_service(
                "account-service",
                "/accounts",
                method="POST",
                data=account_data
            )
            
            context.account_id = result["account_id"]
            return SagaStepResult.success(data={"account_id": result["account_id"]})
            
        except Exception as e:
            return SagaStepResult.failure(error=str(e))
    
    @SagaStep(name="setup_customer_account", compensation=True)
    async def compensate_setup_customer_account(self, context: SagaContext) -> SagaStepResult:
        """Compensation: Delete customer account."""
        try:
            await self.client.call_service(
                "account-service",
                f"/accounts/{context.account_id}",
                method="DELETE"
            )
            return SagaStepResult.success()
        except Exception as e:
            return SagaStepResult.failure(error=str(e))
    
    @SagaStep(name="send_welcome_notification")
    async def send_welcome_notification(self, context: SagaContext) -> SagaStepResult:
        """Step 3: Send welcome notification."""
        try:
            notification_data = {
                "customer_id": context.customer_id,
                "email": context.customer_data["email"],
                "template": "welcome_email",
                "data": {
                    "customer_name": context.customer_data["first_name"],
                    "account_id": context.account_id
                }
            }
            
            await self.client.call_service(
                "notification-service",
                "/notifications",
                method="POST",
                data=notification_data
            )
            
            return SagaStepResult.success()
            
        except Exception as e:
            # Notification failure shouldn't fail the entire saga
            return SagaStepResult.success(warning=f"Notification failed: {str(e)}")

# Saga Execution Engine
class SagaExecutionEngine:
    """Engine for executing sagas with compensation logic."""
    
    def __init__(self):
        self.active_sagas: dict[str, SagaExecution] = {}
    
    async def execute_saga(self, saga: Saga, context: SagaContext) -> SagaResult:
        """Execute saga with automatic compensation on failure."""
        saga_id = context.saga_id
        execution = SagaExecution(saga=saga, context=context)
        self.active_sagas[saga_id] = execution
        
        try:
            # Execute saga steps
            for step in saga.steps:
                step_result = await step.execute(context)
                execution.add_step_result(step, step_result)
                
                if step_result.status == SagaStepStatus.FAILED:
                    # Execute compensation logic
                    await self._compensate_saga(execution)
                    return SagaResult.failure(
                        saga_id=saga_id,
                        failed_step=step.name,
                        error=step_result.error
                    )
            
            # All steps succeeded
            return SagaResult.success(saga_id=saga_id)
            
        except Exception as e:
            # Unexpected error - compensate and fail
            await self._compensate_saga(execution)
            return SagaResult.failure(
                saga_id=saga_id,
                error=str(e)
            )
        finally:
            # Cleanup
            del self.active_sagas[saga_id]
    
    async def _compensate_saga(self, execution: SagaExecution) -> None:
        """Execute compensation steps in reverse order."""
        completed_steps = execution.get_completed_steps()
        
        # Execute compensations in reverse order
        for step in reversed(completed_steps):
            if step.has_compensation():
                try:
                    await step.compensate(execution.context)
                except Exception as e:
                    # Log compensation failure but continue
                    logger.error(f"Compensation failed for step {step.name}: {e}")
```

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Hexagonal Architecture Foundation**](../design/unified-architecture-guide.md) - Core architectural patterns essential for understanding advanced patterns
- [**Framework Architecture Guide**](../design/flx-framework-architecture-guide.md) - FLX Framework architecture foundations required for advanced pattern implementation
- [**Port-Adapter Patterns**](../ports/index.md) - Port and adapter concepts fundamental to advanced pattern implementation

### **➡️ Implementation Next Steps**

- [**Domain-Driven Design Patterns**](./domain-driven-design-patterns.md) - Detailed DDD implementation patterns and bounded context design
- [**Event Sourcing Implementation**](./event-sourcing-implementation.md) - Complete event sourcing patterns and event store implementation
- [**SOLID Principles Implementation**](./solid-principles-implementation.md) - SOLID principles application in hexagonal architecture

### **🔗 Related Implementation Topics**

- [**Infrastructure Service Patterns**](../../infrastructure/service-patterns.md) - Infrastructure services supporting advanced architectural patterns
- [**Testing Advanced Patterns**](../../development/testing/hexagonal-testing-guide.md) - Testing strategies for complex architectural patterns and domain logic
- [**API Reference for Pattern Implementation**](../../api-reference/core-api-reference.md) - Core API documentation for entities, aggregates, and domain events
- [**Real-World Pattern Examples**](../../examples/real-world-implementations.md) - Production examples demonstrating advanced patterns in practice
- [**Performance Optimization for Patterns**](../../optimization/performance/optimization-guide.md) - Performance considerations for advanced architectural patterns
- [**Security Implementation in Patterns**](../../security/architecture/security-architecture.md) - Security patterns and considerations for advanced architectures

---

**📂 Content Document** | **🏠 Parent**: [Architecture Patterns Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11

**🏛️ Your FLX application now supports enterprise-grade architectural patterns with domain-driven design, event sourcing, CQRS, and microservices!**
