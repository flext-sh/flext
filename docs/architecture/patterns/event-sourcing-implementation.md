# Event Sourcing Implementation - Architecture

> **Function**: Event-driven state management and audit trails with event store | **Audience**: Senior developers, architects, domain experts | **Status**: ✅ Advanced

[![Event Sourcing](https://img.shields.io/badge/pattern-Event_Sourcing-purple.svg)](#event-store-implementation)
[![Architecture](https://img.shields.io/badge/architecture-advanced-blue.svg)](./advanced-patterns-hub.md)
[![Audit](https://img.shields.io/badge/audit-complete_trail-green.svg)](#temporal-queries)

**Advanced event sourcing implementation with event store, temporal queries, and optimistic concurrency for FLEXT Framework 0.4.0+**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture](../index.md) → **📂 Patterns**: [Advanced Patterns Hub](./advanced-patterns-hub.md) → **📄 Current**: Event Sourcing Implementation

### **📍 Learning Path Position**

```
[Domain-Driven Design Patterns](./domain-driven-design-patterns.md) → **[EVENT SOURCING]** → [CQRS Architecture Guide](./cqrs-architecture-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Advanced Patterns Hub](./advanced-patterns-hub.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [CQRS Guide](./cqrs-architecture-guide.md)

---

## 📋 **Overview**

Event Sourcing in FLEXT provides a complete audit trail and enables sophisticated event-driven architectures. Instead of storing current state, we store a sequence of events that led to the current state.

### **Key Benefits**

- **🕰️ Complete Audit Trail**: Every change is recorded as an event
- **🔄 Temporal Queries**: Query system state at any point in time
- **🎯 Event-Driven Architecture**: Natural integration with event buses
- **🧪 Testing**: Easy to test with event replay
- **📊 Analytics**: Rich event data for business intelligence

---

## 🏪 Event Store Implementation

### **Core Event Store**

```python
# flext/infrastructure/event_store.py
from flext.core.events import EventStore, Event, EventStream
from flext.adapters.outbound.database import DatabaseAdapter

class FLXEventStore(EventStore):
    """FLEXT Event Store implementation with optimistic concurrency."""

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
```

---

## 🎭 Event-Sourced Aggregates

### **Event-Sourced Customer Aggregate**

```python
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

---

## 📊 Event Projections

### **Read Model Projections**

```python
# flext/projections/customer_projections.py
from flext.core.projections import Projection, ProjectionHandler

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

---

## 🔍 Temporal Queries

### **Point-in-Time Queries**

```python
class CustomerTemporalQueries:
    """Temporal queries for customer data."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    async def get_customer_at_time(self, customer_id: CustomerId,
                                 at_time: datetime) -> EventSourcedCustomer | None:
        """Get customer state at specific point in time."""
        # Load all events up to the specified time
        stream = await self.event_store.load_events(str(customer_id))

        # Filter events to only include those before at_time
        filtered_events = [
            event for event in stream.events
            if event.timestamp <= at_time
        ]

        if not filtered_events:
            return None

        # Rebuild aggregate state
        customer = EventSourcedCustomer(customer_id)
        for event in filtered_events:
            customer.apply_event(event)

        return customer

    async def get_customer_history(self, customer_id: CustomerId,
                                 from_time: datetime = None,
                                 to_time: datetime = None) -> list[Event]:
        """Get customer event history within time range."""
        stream = await self.event_store.load_events(str(customer_id))

        # Filter by time range
        filtered_events = stream.events

        if from_time:
            filtered_events = [
                event for event in filtered_events
                if event.timestamp >= from_time
            ]

        if to_time:
            filtered_events = [
                event for event in filtered_events
                if event.timestamp <= to_time
            ]

        return filtered_events

    async def get_customers_created_between(self, start_date: datetime,
                                          end_date: datetime) -> list[CustomerId]:
        """Get customers created within date range."""
        # This would typically use a projection or event index
        # For demonstration, we'll show the concept

        query = """
            SELECT DISTINCT stream_id
            FROM events
            WHERE event_type = 'CustomerCreated'
            AND timestamp BETWEEN ? AND ?
        """

        rows = await self.event_store.database.fetch_all(
            query, [start_date, end_date]
        )

        return [CustomerId(row['stream_id']) for row in rows]
```

---

## ⚡ Event Store Optimizations

### **Snapshotting**

```python
class SnapshotStore:
    """Store for aggregate snapshots to optimize loading."""

    def __init__(self, database: DatabaseAdapter):
        self.database = database

    async def save_snapshot(self, aggregate: AggregateRoot) -> None:
        """Save aggregate snapshot."""
        snapshot_data = {
            'aggregate_id': str(aggregate.id),
            'aggregate_type': aggregate.__class__.__name__,
            'version': aggregate.version,
            'data': aggregate.to_dict(),
            'timestamp': datetime.utcnow()
        }

        await self.database.execute("""
            INSERT OR REPLACE INTO snapshots
            (aggregate_id, aggregate_type, version, data, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, [
            snapshot_data['aggregate_id'],
            snapshot_data['aggregate_type'],
            snapshot_data['version'],
            json.dumps(snapshot_data['data']),
            snapshot_data['timestamp']
        ])

    async def load_snapshot(self, aggregate_id: str,
                          aggregate_type: type) -> tuple[AggregateRoot, int] | None:
        """Load latest snapshot for aggregate."""
        query = """
            SELECT version, data, timestamp
            FROM snapshots
            WHERE aggregate_id = ? AND aggregate_type = ?
            ORDER BY version DESC
            LIMIT 1
        """

        row = await self.database.fetch_one(query, [
            aggregate_id, aggregate_type.__name__
        ])

        if not row:
            return None

        # Reconstruct aggregate from snapshot
        data = json.loads(row['data'])
        aggregate = aggregate_type.from_dict(data)
        aggregate._version = row['version']

        return aggregate, row['version']

class OptimizedEventStore(FLXEventStore):
    """Event store with snapshot optimization."""

    def __init__(self, database: DatabaseAdapter, snapshot_frequency: int = 100):
        super().__init__(database)
        self.snapshot_store = SnapshotStore(database)
        self.snapshot_frequency = snapshot_frequency

    async def load_aggregate(self, aggregate_id: str,
                           aggregate_type: type) -> AggregateRoot:
        """Load aggregate with snapshot optimization."""
        # Try to load from snapshot first
        snapshot_result = await self.snapshot_store.load_snapshot(
            aggregate_id, aggregate_type
        )

        if snapshot_result:
            aggregate, snapshot_version = snapshot_result

            # Load events after snapshot
            stream = await self.load_events(aggregate_id, snapshot_version)

            # Apply events after snapshot
            for event in stream.events:
                aggregate.apply_event(event)
        else:
            # No snapshot, load from beginning
            aggregate = await super().load_aggregate(aggregate_id, aggregate_type)

        aggregate.mark_events_as_committed()
        return aggregate

    async def save_aggregate(self, aggregate: AggregateRoot) -> None:
        """Save aggregate and create snapshot if needed."""
        await super().save_aggregate(aggregate)

        # Create snapshot if version is multiple of snapshot frequency
        if aggregate.version % self.snapshot_frequency == 0:
            await self.snapshot_store.save_snapshot(aggregate)
```

---

## 🧪 Testing Event Sourcing

### **Event Sourcing Tests**

```python
class TestEventSourcedCustomer:
    """Test event-sourced customer behavior."""

    async def test_customer_creation_and_replay(self):
        """Test customer creation and event replay."""
        # Arrange
        customer_id = CustomerId.generate()
        personal_info = PersonalInfo(first_name="John", last_name="Doe")
        contact_info = ContactInfo(email="john@example.com")

        # Act - create and modify customer
        customer = EventSourcedCustomer.create(customer_id, personal_info)
        customer.register(contact_info)
        customer.change_email("john.doe@example.com")

        # Get all events
        events = customer.get_uncommitted_events()

        # Create new instance and replay events
        replayed_customer = EventSourcedCustomer(customer_id)
        for event in events:
            replayed_customer.apply_event(event)

        # Assert - state should be identical
        assert replayed_customer.status == CustomerStatus.ACTIVE
        assert replayed_customer.contact_info.email == "john.doe@example.com"
        assert replayed_customer.personal_info.first_name == "John"

    async def test_optimistic_concurrency(self):
        """Test optimistic concurrency control."""
        # This would test the event store concurrency mechanisms
        pass

    async def test_temporal_queries(self):
        """Test temporal query capabilities."""
        # Test querying state at different points in time
        pass
```

---

## 🚀 Performance Considerations

### **Best Practices**

1. **Snapshot Strategy**: Use snapshots for aggregates with many events
2. **Event Indexing**: Index events by aggregate type and timestamp
3. **Projection Updates**: Use eventual consistency for projections
4. **Event Versioning**: Plan for event schema evolution
5. **Storage Optimization**: Consider event compression for old events

### **Monitoring and Metrics**

```python
class EventStoreMetrics:
    """Metrics for event store performance."""

    def __init__(self, metrics_adapter: MetricsAdapter):
        self.metrics = metrics_adapter

    async def record_event_append(self, stream_id: str, event_count: int,
                                duration_ms: float) -> None:
        """Record event append metrics."""
        await self.metrics.increment('event_store.events_appended', event_count)
        await self.metrics.histogram('event_store.append_duration_ms', duration_ms)

    async def record_aggregate_load(self, aggregate_type: str,
                                  event_count: int, duration_ms: float,
                                  used_snapshot: bool) -> None:
        """Record aggregate loading metrics."""
        await self.metrics.increment('event_store.aggregates_loaded')
        await self.metrics.histogram('event_store.load_duration_ms', duration_ms)
        await self.metrics.histogram('event_store.events_replayed', event_count)

        if used_snapshot:
            await self.metrics.increment('event_store.snapshot_hits')
        else:
            await self.metrics.increment('event_store.snapshot_misses')
```

---

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Domain-Driven Design Patterns](./domain-driven-design-patterns.md) - DDD fundamentals required for understanding event-sourced aggregates
- [Advanced Patterns Hub](./advanced-patterns-hub.md) - Advanced architectural pattern foundations
- [Core Domain Layer](../layers/core-domain-layer.md) - Domain layer concepts essential for event sourcing

### **Next Steps**

- [CQRS Architecture Guide](./cqrs-architecture-guide.md) - Command-Query separation patterns that complement event sourcing
- [Microservices Patterns](./microservices-patterns.md) - Distributed systems applying event sourcing patterns
- [Infrastructure Services](../../infrastructure/index.md) - Infrastructure supporting event store implementation

### **Related Topics**

- [Testing Advanced Patterns](../../development/testing/index.md) - Testing strategies for event-sourced systems
- [Performance Optimization](../../optimization/index.md) - Optimizing event store and projection performance
- [Database Adapters](../../api-reference/adapters/index.md) - Database integration for event store implementation
- [Oracle Integration](../../guides/oracle/index.md) - Enterprise integration patterns using event sourcing

---

**📂 Hub**: [Advanced Patterns Hub](./advanced-patterns-hub.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
