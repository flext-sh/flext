# Messaging Infrastructure - Infrastructure

> **Function**: Event-driven architecture and message bus patterns | **Audience**: Integration engineers, backend developers | **Status**: Stable

[![Infrastructure](https://img.shields.io/badge/layer-infrastructure-blue.svg)](./index.md)
[![Messaging](https://img.shields.io/badge/component-messaging-purple.svg)](../api-reference/infrastructure/messaging.md)
[![DDD](https://img.shields.io/badge/pattern-domain_driven-orange.svg)](../architecture/patterns/domain-driven-design.md)

**Asynchronous messaging infrastructure implementing DDD patterns with Dramatiq and Lato for the FLEXT Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Infrastructure Hub](./index.md) → **📄 Current**: Messaging Infrastructure

### **📍 Learning Path Position**

```
[Cache Infrastructure](./cache-infrastructure.md) → **[Messaging Infrastructure]** → [Security Infrastructure](./security-infrastructure.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Infrastructure Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Related**: [Event-Driven Architecture](../architecture/patterns/event-driven.md)

---

## 📋 **Overview**

The FLEXT messaging infrastructure provides a robust event-driven architecture foundation, integrating Dramatiq for background task processing and Lato for Domain-Driven Design (DDD) command/query handling.

### **Key Features**

- **DDD Integration**: Commands, queries, and domain events with Lato
- **Background Processing**: Async task execution with Dramatiq
- **Multiple Brokers**: Redis and RabbitMQ support
- **Actor Pattern**: Message handling with actor-based concurrency
- **Dead Letter Queues**: Automatic retry and failure handling

### **Prerequisites**

- Python 3.13+ with async support
- Redis or RabbitMQ for message broker
- Understanding of DDD patterns
- Basic knowledge of event-driven architecture

---

## 📚 **Architecture**

### **Message Bus Components**

Based on actual implementation in `/flext/src/flext/infra/messaging/`:

```python
from flext.infra.messaging import AsyncMessageBus
from lato import ApplicationContainer
import dramatiq

class AsyncMessageBus:
    """Integrates Lato DDD patterns with Dramatiq background processing."""

    def __init__(self, broker_type: str = "redis"):
        self._broker = self._create_broker(broker_type)
        self._container = ApplicationContainer()
        dramatiq.set_broker(self._broker)
```

### **Message Types**

1. **Commands**: Actions that change state
2. **Queries**: Read operations without side effects
3. **Events**: Notifications of state changes
4. **Tasks**: Background jobs and workflows

---

## 🔧 **Implementation**

### **Basic Message Bus Setup**

```python
from flext.infra.messaging import AsyncMessageBus
from lato import Command, Query, Event

# Initialize message bus
bus = AsyncMessageBus(broker_type="redis")
await bus.connect()

# Define messages
class CreateUserCommand(Command):
    username: str
    email: str

class UserCreatedEvent(Event):
    user_id: str
    username: str

class GetUserQuery(Query):
    user_id: str
```

### **Command Handling**

```python
from flext.infra.messaging.handlers import CommandHandler

class CreateUserHandler(CommandHandler[CreateUserCommand, str]):
    """Handle user creation commands."""

    async def handle(self, command: CreateUserCommand) -> str:
        # Create user in database
        user = await self.repository.create_user(
            username=command.username,
            email=command.email
        )

        # Publish domain event
        await self.bus.publish(UserCreatedEvent(
            user_id=user.id,
            username=user.username
        ))

        return user.id

# Register handler
bus.register_handler(CreateUserCommand, CreateUserHandler())

# Send command
user_id = await bus.send_command(CreateUserCommand(
    username="john_doe",
    email="john@example.com"
))
```

### **Event Handling**

```python
from flext.infra.messaging.handlers import EventHandler

class UserCreatedHandler(EventHandler[UserCreatedEvent]):
    """React to user creation events."""

    async def handle(self, event: UserCreatedEvent) -> None:
        # Send welcome email
        await self.email_service.send_welcome(event.user_id)

        # Update analytics
        await self.analytics.track_user_signup(event.user_id)

        # Initialize user preferences
        await self.preferences.create_defaults(event.user_id)

# Register multiple handlers for same event
bus.subscribe(UserCreatedEvent, UserCreatedHandler())
bus.subscribe(UserCreatedEvent, AnalyticsHandler())
bus.subscribe(UserCreatedEvent, NotificationHandler())
```

### **Background Tasks with Dramatiq**

```python
import dramatiq
from flext.infra.messaging.decorators import background_task

@background_task(queue="emails", max_retries=3)
async def send_email(recipient: str, subject: str, body: str):
    """Background task for sending emails."""
    async with EmailClient() as client:
        await client.send(
            to=recipient,
            subject=subject,
            body=body
        )

# Enqueue task
send_email.send(
    recipient="user@example.com",
    subject="Welcome!",
    body="Thank you for signing up"
)

# Delayed execution
send_email.send_with_options(
    args=("user@example.com", "Reminder", "Don't forget..."),
    delay=timedelta(hours=24)
)
```

### **Saga Pattern Implementation**

```python
class OrderSaga:
    """Multi-step business process orchestration."""

    def __init__(self, bus: AsyncMessageBus):
        self.bus = bus
        self.steps = []

    async def process_order(self, order_id: str):
        try:
            # Step 1: Reserve inventory
            await self.bus.send_command(ReserveInventoryCommand(order_id))
            self.steps.append("inventory_reserved")

            # Step 2: Process payment
            await self.bus.send_command(ProcessPaymentCommand(order_id))
            self.steps.append("payment_processed")

            # Step 3: Ship order
            await self.bus.send_command(ShipOrderCommand(order_id))
            self.steps.append("order_shipped")

        except Exception as e:
            # Compensate in reverse order
            await self.compensate()
            raise

    async def compensate(self):
        if "order_shipped" in self.steps:
            await self.bus.send_command(CancelShipmentCommand())
        if "payment_processed" in self.steps:
            await self.bus.send_command(RefundPaymentCommand())
        if "inventory_reserved" in self.steps:
            await self.bus.send_command(ReleaseInventoryCommand())
```

---

## 🏭 **Production Configuration**

### **Broker Auto-Detection**

FLEXT implements intelligent broker detection with automatic fallback:

```python
# Default behavior - no configuration needed
bus = AsyncMessageBus()  # Automatically tries Redis, falls back to in-memory

# Explicit configuration
bus = AsyncMessageBus(broker_type="auto")  # Same as default
bus = AsyncMessageBus(broker_type="redis")  # Redis only, fails if unavailable
bus = AsyncMessageBus(broker_type="memory")  # In-memory only
```

**Auto-detection strategy:**

1. **First**: Attempts Redis on `localhost:6379` (no authentication)
2. **Fallback**: If Redis unavailable → In-memory broker
3. **Result**: Works immediately even without Redis installed

### **Redis Broker Setup**

```yaml
# config/messaging.yaml
messaging:
  broker: redis
  redis:
    url: redis://redis-cluster:6379/0
    namespace: flext
    queue_ttl: 86400 # 24 hours
    result_ttl: 3600 # 1 hour

  queues:
    default:
      concurrency: 4
      max_retries: 3

    emails:
      concurrency: 2
      max_retries: 5
      min_backoff: 60

    analytics:
      concurrency: 8
      max_retries: 1
```

### **RabbitMQ Broker Setup**

```python
# For high-throughput scenarios
bus = AsyncMessageBus(
    broker_type="rabbitmq",
    broker_config={
        "url": "amqp://user:pass@rabbitmq:5672/",
        "exchange": "flext.events",
        "exchange_type": "topic",
        "durable": True,
        "delivery_mode": "PERSISTENT"
    }
)
```

### **Monitoring and Metrics**

```python
# Message bus metrics
metrics = await bus.get_metrics()
print(f"Messages processed: {metrics.processed_count}")
print(f"Failed messages: {metrics.failed_count}")
print(f"Average processing time: {metrics.avg_processing_time}ms")

# Queue monitoring
for queue_name, stats in metrics.queues.items():
    print(f"{queue_name}: {stats.pending} pending, {stats.active} active")
```

---

## 🧪 **Testing**

### **Unit Testing with Test Engine**

```python
import pytest
from flext.infra.messaging import AsyncMessageBus

@pytest.fixture
async def bus():
    bus = AsyncMessageBus(use_test_engine=True)
    await bus.connect()
    yield bus
    await bus.disconnect()

async def test_command_handling(bus):
    # Register test handler
    handler = Mock(return_value="user-123")
    bus.register_handler(CreateUserCommand, handler)

    # Send command
    result = await bus.send_command(CreateUserCommand(
        username="test",
        email="test@example.com"
    ))

    assert result == "user-123"
    handler.assert_called_once()
```

### **Integration Testing**

```python
@pytest.mark.integration
async def test_event_propagation():
    bus = AsyncMessageBus(broker_type="redis")
    events_received = []

    # Register event handler
    async def handler(event):
        events_received.append(event)

    bus.subscribe(UserCreatedEvent, handler)

    # Publish event
    await bus.publish(UserCreatedEvent(
        user_id="123",
        username="test_user"
    ))

    # Wait for processing
    await asyncio.sleep(0.1)

    assert len(events_received) == 1
    assert events_received[0].user_id == "123"
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Service Patterns](./service-patterns.md) - Understanding base infrastructure services
- [DDD Patterns](../architecture/patterns/domain-driven-design.md) - Domain-driven design concepts

### **Next Steps**

- [Event Sourcing](../guides/patterns/event-sourcing.md) - Building event-sourced systems
- [CQRS Implementation](../guides/patterns/cqrs.md) - Command Query Responsibility Segregation

### **Related Topics**

- [Background Jobs](../guides/background-processing/index.md) - Async job processing patterns
- [Integration Events](../guides/integration/event-integration.md) - Cross-system event handling

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Message Processing Failures**

```python
# Issue: Messages failing repeatedly
# Solution: Implement proper error handling
@background_task(max_retries=3, min_backoff=60)
async def process_with_retry(data):
    try:
        await risky_operation(data)
    except TemporaryError:
        # Will retry automatically
        raise
    except PermanentError:
        # Won't retry, send to dead letter queue
        raise dramatiq.Abort()
```

#### **Memory Issues with Large Messages**

```python
# Issue: Large messages causing memory problems
# Solution: Use message references
class LargeDataCommand(Command):
    data_reference: str  # S3 key or database ID

    async def get_data(self):
        return await storage.get(self.data_reference)
```

#### **Ordering Guarantees**

```python
# Issue: Messages processed out of order
# Solution: Use partition keys
await bus.publish(
    OrderEvent(order_id="123", status="shipped"),
    partition_key="order-123"  # All events for this order in same partition
)
```

---

**📂 Hub**: [Infrastructure Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLEXT 0.4.0+
