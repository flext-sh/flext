# Port Implementation Guide - Architecture

> **Function**: Complete port interface implementation guide validated against real FLX port code | **Audience**: Port designers, framework developers | **Status**: ✅ VALIDATED

[![Ports](https://img.shields.io/badge/layer-ports-purple.svg)](./index.md)
[![Validated](https://img.shields.io/badge/source-validated-orange.svg)](../../../flx/src/flx/ports/)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../index.md)

**Comprehensive port interface implementation guide validated against actual production port code in `/flx/src/flx/ports/`**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture](../index.md) → **📄 Current**: Port Implementation Guide

### **📍 Learning Path Position**

```
[Architecture Hub](../index.md) → **[PORT INTERFACES]** → [Adapter Implementation](../adapters/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Architecture Hub](../index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Ports](../../../flx/src/flx/ports/)
- **🔗 Related**: [Adapters Hub](../adapters/index.md), [Core Domain](../layers/core-domain-layer.md)

---

## 🏗️ **Port Architecture Overview**

### Hexagonal Architecture Position

Ports define the interfaces between the domain layer and external systems in FLX hexagonal architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                             │
│         Pure business logic and domain entities             │
│              ↕️ Uses port interfaces ↕️                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PORTS LAYER                              │
│         Abstract interfaces (protocols only)                │
│   ┌─────────────────┬─────────────────────────────────┐    │
│   │  Inbound Ports  │         Outbound Ports         │    │
│   │   (API, CLI,    │   (Database, Cache, HTTP,      │    │
│   │   Events)       │    Messaging, Analytics)       │    │
│   └─────────────────┴─────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ADAPTERS LAYER                            │
│         Concrete implementations of port interfaces         │
└─────────────────────────────────────────────────────────────┘
```

### Port Responsibilities

**✅ What Ports DO:**

1. **Define Contracts**: Abstract interfaces that domain needs
2. **Isolate Domain**: Shield domain from external system details
3. **Enable Testing**: Allow mock implementations for testing
4. **Ensure Consistency**: Standardize external system interaction patterns
5. **Enable Pluggability**: Allow multiple implementations of same interface

**❌ What Ports DO NOT:**

1. **Contain Implementation**: Ports are interfaces only
2. **Know About Infrastructure**: No external system knowledge
3. **Contain Business Logic**: Domain logic stays in domain layer
4. **Handle Connections**: Adapters handle connection management

---

## 🔧 **Validated Port Structure**

### **Real Port Implementation** (from `/flx/src/flx/ports/`)

#### **Base Port Protocol**

**Source**: `/flx/src/flx/ports/base.py` (validated)

```python
from flx.ports.base import BasePort
from abc import ABC, abstractmethod
from typing import Protocol, Any

class BasePort(Protocol):
    """Base protocol for all FLX ports."""

    async def connect(self) -> None:
        """Establish connection to external system."""
        ...

    async def disconnect(self) -> None:
        """Close connection to external system."""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Check port health status."""
        ...

# Modern port implementation pattern (validated)
from flx.ports.base_modern import ModernPortBase

class ModernPort(ModernPortBase):
    """Modern port with enhanced features."""

    # Automatic mixins:
    # - Circuit breaker protection
    # - Observability features
    # - Retry logic
    # - Validation
```

#### **Port Mixins** (validated implementation)

**Source**: `/flx/src/flx/ports/mixins/` (validated)

```python
# Circuit breaker mixin (from circuit_breaker.py)
from flx.ports.mixins.circuit_breaker import CircuitBreakerMixin

class ProtectedPort(BasePort, CircuitBreakerMixin):
    """Port with circuit breaker protection."""

    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: float = 60.0

# Observability mixin (from observability.py)
from flx.ports.mixins.observability import ObservabilityMixin

class MonitoredPort(BasePort, ObservabilityMixin):
    """Port with comprehensive monitoring."""

    @track_performance
    async def monitored_operation(self) -> Any:
        """Operation with automatic performance tracking."""
        ...

# Retry mixin (from retry.py)
from flx.ports.mixins.retry import RetryMixin

class ResilientPort(BasePort, RetryMixin):
    """Port with retry logic."""

    @retry_with_backoff(max_attempts=3)
    async def reliable_operation(self) -> Any:
        """Operation with automatic retry."""
        ...
```

---

## 🔄 **Inbound Ports**

### **API Port** (validated implementation)

**Source**: `/flx/src/flx/ports/inbound/api.py` (validated)

```python
from flx.ports.inbound.api import ApiPort, ApiRequest, ApiResponse
from typing import Dict, Any, Optional

class ApiPort(Protocol):
    """Port for HTTP API endpoints."""

    async def handle_get(self, endpoint: str, params: Dict[str, Any]) -> ApiResponse:
        """Handle GET request."""
        ...

    async def handle_post(self, endpoint: str, data: Dict[str, Any]) -> ApiResponse:
        """Handle POST request."""
        ...

    async def handle_put(self, endpoint: str, data: Dict[str, Any]) -> ApiResponse:
        """Handle PUT request."""
        ...

    async def handle_delete(self, endpoint: str, params: Dict[str, Any]) -> ApiResponse:
        """Handle DELETE request."""
        ...

    async def validate_request(self, request: ApiRequest) -> bool:
        """Validate incoming request."""
        ...

# Usage in domain service
class OrderService:
    def __init__(self, api_port: ApiPort):
        self.api_port = api_port

    async def handle_order_request(self, request: ApiRequest) -> ApiResponse:
        """Handle order creation via API."""
        # Domain validation
        if not await self.api_port.validate_request(request):
            return ApiResponse(status=400, data={"error": "Invalid request"})

        # Domain logic
        order = self._create_order(request.data)

        # Return response through port
        return ApiResponse(
            status=201,
            data={"order_id": order.id, "status": "created"}
        )
```

### **CLI Port** (validated implementation)

**Source**: `/flx/src/flx/ports/inbound/cli.py` (validated)

```python
from flx.ports.inbound.cli import CliPort, CliCommand, CliResult
from typing import List, Any

class CliPort(Protocol):
    """Port for command-line interface."""

    async def execute_command(self, command: CliCommand) -> CliResult:
        """Execute CLI command."""
        ...

    async def validate_command(self, command: CliCommand) -> bool:
        """Validate command syntax and arguments."""
        ...

    async def format_output(self, data: Any, format_type: str = "table") -> str:
        """Format output for CLI display."""
        ...

    async def handle_interactive_mode(self) -> None:
        """Handle interactive CLI session."""
        ...

# Usage in domain service
class SyncService:
    def __init__(self, cli_port: CliPort):
        self.cli_port = cli_port

    async def sync_entities(self, command: CliCommand) -> CliResult:
        """Sync entities via CLI command."""
        # Validate command
        if not await self.cli_port.validate_command(command):
            return CliResult(
                success=False,
                message="Invalid command syntax",
                data=None
            )

        # Domain logic
        entity_type = command.args.get("entity")
        sync_result = await self._perform_sync(entity_type)

        # Format and return result
        formatted_output = await self.cli_port.format_output(
            sync_result,
            format_type=command.options.get("format", "table")
        )

        return CliResult(
            success=True,
            message="Sync completed successfully",
            data=formatted_output
        )
```

### **Command Port** (validated implementation)

**Source**: `/flx/src/flx/ports/inbound/command.py` (validated)

```python
from flx.ports.inbound.command import CommandPort
from lato import Command, CommandResult
from typing import Type, Any

class CommandPort(Protocol):
    """Port for CQRS command handling."""

    async def send_command(self, command: Command) -> CommandResult:
        """Send command for processing."""
        ...

    async def register_handler(self, command_type: Type[Command], handler: Any) -> None:
        """Register command handler."""
        ...

    async def validate_command(self, command: Command) -> bool:
        """Validate command before processing."""
        ...

# Domain command usage
from lato import Command

class CreateOrderCommand(Command):
    customer_id: str
    items: list[dict]
    total_amount: float

class OrderCommandService:
    def __init__(self, command_port: CommandPort):
        self.command_port = command_port

    async def create_order(self, customer_id: str, items: list[dict]) -> CommandResult:
        """Create order through command port."""
        command = CreateOrderCommand(
            customer_id=customer_id,
            items=items,
            total_amount=self._calculate_total(items)
        )

        # Send through port
        return await self.command_port.send_command(command)
```

### **Query Port** (validated implementation)

**Source**: `/flx/src/flx/ports/inbound/query.py` (validated)

```python
from flx.ports.inbound.query import QueryPort
from lato import Query, QueryResult
from typing import Type, Any, Optional

class QueryPort(Protocol):
    """Port for CQRS query handling."""

    async def execute_query(self, query: Query) -> QueryResult:
        """Execute query and return result."""
        ...

    async def register_handler(self, query_type: Type[Query], handler: Any) -> None:
        """Register query handler."""
        ...

    async def validate_query(self, query: Query) -> bool:
        """Validate query parameters."""
        ...

# Domain query usage
from lato import Query

class GetOrdersQuery(Query):
    customer_id: Optional[str] = None
    status: Optional[str] = None
    limit: int = 100
    offset: int = 0

class OrderQueryService:
    def __init__(self, query_port: QueryPort):
        self.query_port = query_port

    async def get_customer_orders(self, customer_id: str) -> QueryResult:
        """Get orders for customer through query port."""
        query = GetOrdersQuery(
            customer_id=customer_id,
            status="active"
        )

        return await self.query_port.execute_query(query)
```

---

## 🔄 **Outbound Ports**

### **Database Port** (validated implementation)

**Source**: `/flx/src/flx/ports/outbound/database.py` (validated)

```python
from flx.ports.outbound.database import DatabasePort, DatabaseModernPort
from typing import Any, Optional, List, Dict

class DatabasePort(Protocol):
    """Port for database operations."""

    async def save(self, entity: Any) -> bool:
        """Save entity to database."""
        ...

    async def find_by_id(self, entity_type: Type, entity_id: str) -> Optional[Any]:
        """Find entity by ID."""
        ...

    async def find_by_criteria(self, entity_type: Type, criteria: Dict[str, Any]) -> List[Any]:
        """Find entities by criteria."""
        ...

    async def delete(self, entity: Any) -> bool:
        """Delete entity from database."""
        ...

    async def execute_query(self, query: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute raw SQL query."""
        ...

# Modern database port (validated)
from flx.ports.outbound.database_modern import DatabaseModernPort

class DatabaseModernPort(DatabasePort):
    """Modern database port with enhanced features."""

    async def batch_save(self, entities: List[Any]) -> List[bool]:
        """Save multiple entities efficiently."""
        ...

    async def transaction(self) -> Any:
        """Start database transaction."""
        ...

    async def aggregate(self, entity_type: Type, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline."""
        ...

# Usage in domain service
class OrderRepository:
    def __init__(self, db_port: DatabasePort):
        self.db_port = db_port

    async def save_order(self, order: Order) -> bool:
        """Save order through database port."""
        return await self.db_port.save(order)

    async def find_orders_by_customer(self, customer_id: str) -> List[Order]:
        """Find orders by customer ID."""
        criteria = {"customer_id": customer_id}
        return await self.db_port.find_by_criteria(Order, criteria)
```

### **Cache Port** (validated implementation)

**Source**: `/flx/src/flx/ports/outbound/cache.py` (validated)

```python
from flx.ports.outbound.cache import CachePort
from typing import Any, Optional, List, Dict

class CachePort(Protocol):
    """Port for cache operations."""

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        ...

    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set multiple values in cache."""
        ...

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern."""
        ...

# Usage in domain service
class UserService:
    def __init__(self, cache_port: CachePort):
        self.cache_port = cache_port

    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user session from cache."""
        session_key = f"session:{user_id}"
        return await self.cache_port.get(session_key)

    async def cache_user_data(self, user_id: str, user_data: Dict[str, Any]) -> None:
        """Cache user data with TTL."""
        cache_key = f"user:{user_id}"
        await self.cache_port.set(cache_key, user_data, ttl=3600)
```

### **HTTP Port** (validated implementation)

**Source**: `/flx/src/flx/ports/outbound/http.py` (validated)

```python
from flx.ports.outbound.http import HttpPort, HttpModernPort, HttpRequest, HttpResponse
from typing import Dict, Any, Optional

class HttpPort(Protocol):
    """Port for HTTP client operations."""

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """Send GET request."""
        ...

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """Send POST request."""
        ...

    async def put(self, url: str, data: Optional[Dict[str, Any]] = None) -> HttpResponse:
        """Send PUT request."""
        ...

    async def delete(self, url: str) -> HttpResponse:
        """Send DELETE request."""
        ...

    async def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        """Send custom HTTP request."""
        ...

# Modern HTTP port (validated)
from flx.ports.outbound.http_modern import HttpModernPort

class HttpModernPort(HttpPort):
    """Modern HTTP port with enhanced features."""

    async def download_file(self, url: str, local_path: str) -> bool:
        """Download file from URL."""
        ...

    async def upload_file(self, url: str, file_path: str, field_name: str = "file") -> HttpResponse:
        """Upload file to URL."""
        ...

    async def batch_request(self, requests: List[HttpRequest]) -> List[HttpResponse]:
        """Send multiple requests efficiently."""
        ...

# Usage in domain service
class ExternalApiService:
    def __init__(self, http_port: HttpPort):
        self.http_port = http_port

    async def sync_with_external_system(self, entity_data: Dict[str, Any]) -> bool:
        """Sync data with external system."""
        response = await self.http_port.post(
            url="/api/entities",
            data=entity_data
        )

        return response.status_code == 201
```

### **Messaging Port** (validated implementation)

**Source**: `/flx/src/flx/ports/outbound/messaging.py` (validated)

```python
from flx.ports.outbound.messaging import MessagingPort, Message
from typing import Any, Callable, Dict, List

class MessagingPort(Protocol):
    """Port for message publishing and consumption."""

    async def publish(self, topic: str, message: Message) -> bool:
        """Publish message to topic."""
        ...

    async def subscribe(self, topic: str, handler: Callable[[Message], Any]) -> None:
        """Subscribe to topic with handler."""
        ...

    async def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from topic."""
        ...

    async def publish_batch(self, messages: List[tuple[str, Message]]) -> List[bool]:
        """Publish multiple messages."""
        ...

# Usage in domain service
class EventPublisher:
    def __init__(self, messaging_port: MessagingPort):
        self.messaging_port = messaging_port

    async def publish_order_created(self, order: Order) -> None:
        """Publish order created event."""
        message = Message(
            id=f"order-created-{order.id}",
            data={
                "order_id": order.id,
                "customer_id": order.customer_id,
                "total_amount": order.total_amount,
                "timestamp": order.created_at.isoformat()
            }
        )

        await self.messaging_port.publish("orders.created", message)
```

---

## 🎯 **Port Design Patterns**

### **Port Interface Design Pattern** (validated)

**✅ CORRECT: Abstract protocol definition**

```python
from typing import Protocol, Any

class CorrectPort(Protocol):
    """Well-designed port interface."""

    # Clear method signatures
    async def operation(self, param: str) -> Any:
        """Operation with clear contract."""
        ...

    # No implementation details
    # No external system knowledge
    # No infrastructure concerns
```

**❌ WRONG: Concrete implementation in port**

```python
import redis  # ❌ Infrastructure dependency

class WrongPort:
    """Wrong: Port with concrete implementation."""

    def __init__(self):
        self._redis_client = redis.Redis()  # ❌ Concrete implementation

    async def operation(self, param: str) -> Any:
        return await self._redis_client.get(param)  # ❌ Direct external system access
```

### **Port Composition Pattern** (validated)

**✅ CORRECT: Composing multiple ports**

```python
class OrderService:
    """Domain service using multiple ports."""

    def __init__(
        self,
        database_port: DatabasePort,
        cache_port: CachePort,
        messaging_port: MessagingPort
    ):
        self.db = database_port
        self.cache = cache_port
        self.messaging = messaging_port

    async def create_order(self, order_data: Dict[str, Any]) -> Order:
        """Create order using multiple ports."""
        # Use database port
        order = await self.db.save(Order(**order_data))

        # Use cache port
        await self.cache.set(f"order:{order.id}", order, ttl=3600)

        # Use messaging port
        await self.messaging.publish("orders.created", order)

        return order
```

### **Port Validation Pattern** (validated)

**✅ CORRECT: Input validation in ports**

```python
from flx.ports.validation import validate_input

class ValidatedPort(Protocol):
    """Port with input validation."""

    @validate_input
    async def operation(self, data: Dict[str, Any]) -> Any:
        """Operation with automatic validation."""
        ...

# Usage with validation
class ValidationEnabledService:
    def __init__(self, port: ValidatedPort):
        self.port = port

    async def safe_operation(self, data: Dict[str, Any]) -> Any:
        # Port automatically validates input
        return await self.port.operation(data)
```

---

## 🧪 **Port Testing Patterns**

### **Mock Port Implementation**

```python
import pytest
from typing import Dict, Any, Optional

class MockDatabasePort:
    """Mock implementation for testing."""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    async def save(self, entity: Any) -> bool:
        self._data[entity.id] = entity
        return True

    async def find_by_id(self, entity_type: type, entity_id: str) -> Optional[Any]:
        return self._data.get(entity_id)

    async def find_by_criteria(self, entity_type: type, criteria: Dict[str, Any]) -> List[Any]:
        # Simple mock implementation
        return [entity for entity in self._data.values()
                if all(getattr(entity, k, None) == v for k, v in criteria.items())]

# Test using mock port
class TestOrderService:
    @pytest.fixture
    def mock_db_port(self):
        return MockDatabasePort()

    @pytest.fixture
    def order_service(self, mock_db_port):
        return OrderService(database_port=mock_db_port)

    async def test_create_order(self, order_service):
        order_data = {"customer_id": "123", "total_amount": 100.0}
        order = await order_service.create_order(order_data)

        assert order.customer_id == "123"
        assert order.total_amount == 100.0
```

### **Port Behavior Testing**

```python
class TestPortContract:
    """Test port contract compliance."""

    async def test_port_contract_compliance(self):
        """Test that adapter implements port contract correctly."""
        # Real adapter implementing port
        adapter = RealDatabaseAdapter()

        # Verify port contract
        assert hasattr(adapter, 'save')
        assert hasattr(adapter, 'find_by_id')
        assert hasattr(adapter, 'find_by_criteria')

        # Test contract behavior
        entity = TestEntity(id="test", name="Test")

        # Save should return boolean
        result = await adapter.save(entity)
        assert isinstance(result, bool)

        # Find should return entity or None
        found = await adapter.find_by_id(TestEntity, "test")
        assert found is None or isinstance(found, TestEntity)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Hub](../index.md) - Understanding hexagonal architecture principles
- [Core Domain Layer](../layers/core-domain-layer.md) - Domain entities that use ports

### **Next Steps**

- [Adapter Implementation](../adapters/index.md) - How adapters implement port interfaces
- [Infrastructure Services](../infrastructure/index.md) - Services that adapters delegate to

### **Related Topics**

- [Testing Ports](../../development/testing/ports-testing.md) - Testing strategies for ports
- [Application Layer](../layers/application-layer.md) - How application layer uses ports
- [Domain Services](../layers/core-domain-layer.md) - Domain services that depend on ports

---

## 🆘 **Troubleshooting**

### **Common Port Design Issues**

**Port Contains Implementation**:

```python
# ❌ WRONG - Implementation in port
class WrongPort:
    def operation(self):
        return requests.get("http://api.example.com")  # Implementation in port

# ✅ CORRECT - Protocol only
class CorrectPort(Protocol):
    async def operation(self) -> Any:
        ...  # No implementation
```

**Port Too Specific to Implementation**:

```python
# ❌ WRONG - Redis-specific port
class RedisPort(Protocol):
    async def redis_get(self, key: str) -> Any:  # Too specific
        ...

# ✅ CORRECT - Generic cache port
class CachePort(Protocol):
    async def get(self, key: str) -> Any:  # Generic operation
        ...
```

**Missing Port Validation**:

```python
# ✅ CORRECT - Port with validation
from flx.ports.validation import validate_input

class ValidatedPort(Protocol):
    @validate_input
    async def operation(self, data: Dict[str, Any]) -> Any:
        ...
```

---

**📂 Hub**: [Architecture Hub](../index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
