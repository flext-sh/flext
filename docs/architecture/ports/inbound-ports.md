# Inbound Ports Guide - Architecture

> **Function**: Guide for implementing inbound ports in hexagonal architecture | **Audience**: API developers, CLI builders, integration engineers | **Status**: Stable

[![Ports](https://img.shields.io/badge/layer-ports-yellow.svg)](./index.md)
[![Hexagonal](https://img.shields.io/badge/pattern-hexagonal-blue.svg)](../hexagonal-architecture-hub.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT%200.4.0-orange.svg)](../../index.md)

**Complete guide for inbound ports that enable external systems to drive the application**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture Hub](../index.md) → **📂 Sub-Hub**: [Ports Hub](./index.md) → **📄 Current**: Inbound Ports

### **📍 Learning Path Position**

```
[Port Interface Definitions](./ports-interface-definitions.md) → **[Inbound Ports]** → [Outbound Ports](./outbound-ports.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Ports Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [Adapter Implementation](../adapters/implementation-guide.md)

---

## 📋 **Overview**

Inbound ports (driving ports) define the interfaces through which external actors interact with the domain layer. They represent the application's entry points and are implemented by inbound adapters.

### **Key Principles**

- **External Entry Points**: How external systems drive the application
- **Domain Protection**: Shield domain from external system details
- **Use Case Implementation**: Express application use cases as port interfaces
- **Technology Independence**: No coupling to specific frameworks

### **Prerequisites**

- Understanding of [Hexagonal Architecture](../hexagonal-architecture-hub.md)
- Knowledge of [Port Interface Definitions](./ports-interface-definitions.md)
- Familiarity with [Core Domain Layer](../core-domain-layer.md)

---

## 📚 **Inbound Port Types**

Based on actual implementation in `/flext/src/flext/ports/inbound/`:

### **1. Command Ports**

For executing domain commands (write operations):

```python
from typing import Protocol, TypeVar, Any
from flext.domain.commands import Command

TCommand = TypeVar('TCommand', bound=Command)
TResult = TypeVar('TResult')

class CommandPort(Protocol):
    """Port for executing domain commands."""

    async def execute(self, command: TCommand) -> TResult:
        """Execute a single domain command."""
        ...

    async def execute_batch(self, commands: List[TCommand]) -> List[TResult]:
        """Execute multiple commands in a transaction."""
        ...
```

**Real Implementation Example:**

```python
from flext.application.commands import CreateOrderCommand

class OrderCommandPort(Protocol):
    """Port for order-related commands."""

    async def create_order(self, command: CreateOrderCommand) -> str:
        """Create new order, return order ID."""
        ...

    async def cancel_order(self, order_id: str, reason: str) -> None:
        """Cancel existing order."""
        ...
```

### **2. Query Ports**

For executing domain queries (read operations):

```python
from typing import Protocol, TypeVar, List
from flext.domain.queries import Query

TQuery = TypeVar('TQuery', bound=Query)
TResult = TypeVar('TResult')

class QueryPort(Protocol):
    """Port for executing domain queries."""

    async def execute(self, query: TQuery) -> TResult:
        """Execute a domain query."""
        ...

    async def execute_batch(self, queries: List[TQuery]) -> List[TResult]:
        """Execute multiple queries."""
        ...
```

**Real Implementation Example:**

```python
from flext.application.queries import GetOrderQuery, OrderDTO

class OrderQueryPort(Protocol):
    """Port for order-related queries."""

    async def get_order(self, order_id: str) -> OrderDTO:
        """Get order by ID."""
        ...

    async def list_customer_orders(self, customer_id: str) -> List[OrderDTO]:
        """List all orders for customer."""
        ...
```

### **3. API Ports**

For HTTP REST/GraphQL endpoints:

```python
from typing import Protocol, Dict, Any
from flext.core.types import RequestContext, ResponseContext

class ApiPort(Protocol):
    """Port for HTTP API operations."""

    async def handle_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Any,
        context: RequestContext
    ) -> ResponseContext:
        """Handle incoming HTTP request."""
        ...

    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI specification."""
        ...
```

**Real Implementation Example:**

```python
class OrderApiPort(Protocol):
    """Port for order API endpoints."""

    async def create_order_endpoint(
        self,
        customer_id: str,
        items: List[Dict],
        context: RequestContext
    ) -> ResponseContext:
        """Create order API endpoint."""
        ...

    async def get_order_endpoint(
        self,
        order_id: str,
        context: RequestContext
    ) -> ResponseContext:
        """Get order API endpoint."""
        ...
```

### **4. CLI Ports**

For command-line interface operations:

```python
from typing import Protocol, List, Dict, Any

class CliPort(Protocol):
    """Port for command-line interface operations."""

    async def execute_command(
        self,
        command: str,
        args: List[str],
        options: Dict[str, Any]
    ) -> int:
        """Execute CLI command and return exit code."""
        ...

    def get_help(self, command: str) -> str:
        """Get help text for command."""
        ...

    def list_commands(self) -> List[str]:
        """List available commands."""
        ...
```

**Real Implementation Example:**

```python
class OrderCliPort(Protocol):
    """Port for order CLI commands."""

    async def create_order_cli(
        self,
        customer_email: str,
        product_ids: List[str],
        options: Dict[str, Any]
    ) -> int:
        """CLI command to create order."""
        ...

    async def list_orders_cli(
        self,
        customer_email: str,
        options: Dict[str, Any]
    ) -> int:
        """CLI command to list customer orders."""
        ...
```

### **5. Event Handler Ports**

For receiving external events:

```python
from typing import Protocol, Any
from flext.domain.events import ExternalEvent

class EventHandlerPort(Protocol):
    """Port for handling external events."""

    async def handle_event(self, event: ExternalEvent) -> None:
        """Handle incoming external event."""
        ...

    async def register_handler(
        self,
        event_type: str,
        handler: Callable[[ExternalEvent], None]
    ) -> None:
        """Register event handler."""
        ...
```

---

## 🔧 **Implementation Patterns**

### **CQRS Pattern Integration**

Separating commands and queries:

```python
class OrderServicePort(Protocol):
    """Combined port following CQRS pattern."""

    # Commands (writes)
    async def create_order(self, command: CreateOrderCommand) -> str:
        ...

    async def update_order(self, command: UpdateOrderCommand) -> None:
        ...

    # Queries (reads)
    async def get_order(self, query: GetOrderQuery) -> OrderDTO:
        ...

    async def list_orders(self, query: ListOrdersQuery) -> List[OrderDTO]:
        ...
```

### **Use Case Driven Ports**

Organizing by business use cases:

```python
class CustomerManagementPort(Protocol):
    """Port for customer management use cases."""

    async def register_customer(self, data: CustomerRegistrationData) -> str:
        """Use case: Register new customer."""
        ...

    async def update_customer_profile(self, customer_id: str, data: ProfileData) -> None:
        """Use case: Update customer profile."""
        ...

    async def deactivate_customer(self, customer_id: str, reason: str) -> None:
        """Use case: Deactivate customer account."""
        ...
```

### **Context-Aware Ports**

Including request context for security and tracing:

```python
from flext.core.context import ExecutionContext

class SecureOrderPort(Protocol):
    """Security-aware order port."""

    async def create_order(
        self,
        command: CreateOrderCommand,
        context: ExecutionContext
    ) -> str:
        """Create order with security context."""
        ...

    async def get_order(
        self,
        order_id: str,
        context: ExecutionContext
    ) -> OrderDTO:
        """Get order with access control."""
        ...
```

---

## 🧪 **Testing Inbound Ports**

### **Mock Implementations**

```python
class MockOrderPort(OrderServicePort):
    """Mock implementation for testing."""

    def __init__(self):
        self.orders: Dict[str, Order] = {}

    async def create_order(self, command: CreateOrderCommand) -> str:
        order_id = str(uuid.uuid4())
        order = Order.from_command(command, order_id)
        self.orders[order_id] = order
        return order_id

    async def get_order(self, query: GetOrderQuery) -> OrderDTO:
        order = self.orders.get(query.order_id)
        if not order:
            raise OrderNotFoundError(query.order_id)
        return OrderDTO.from_entity(order)
```

### **Integration Testing**

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
async def test_order_api_integration():
    """Test real API integration."""
    client = TestClient(app)

    # Create order via API
    response = client.post("/orders", json={
        "customer_id": "123",
        "items": [{"product_id": "456", "quantity": 2}]
    })

    assert response.status_code == 201
    order_id = response.json()["order_id"]

    # Get order via API
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Port Interface Definitions](./ports-interface-definitions.md) - Complete port catalog and contracts
- [Hexagonal Architecture](../hexagonal-architecture-hub.md) - Architectural foundation understanding
- [Core Domain Layer](../core-domain-layer.md) - Domain concepts that ports expose

### **Next Steps**

- [Outbound Ports Guide](./outbound-ports.md) - Complementary outbound port patterns
- [Adapter Implementation](../adapters/implementation-guide.md) - Implementing inbound adapters
- [Port Implementation Guide](./port-implementation-guide.md) - Creating ports step-by-step

### **Related Topics**

- [CQRS Pattern](../patterns/cqrs-patterns.md) - Command Query Responsibility Segregation
- [API Design](../../guides/api/rest-api-guide.md) - REST API implementation
- [CLI Development](../../development/cli/cli-guide.md) - Command-line interface patterns

---

## 🆘 **Common Issues**

### **Overly Complex Port Interfaces**

```python
# ❌ Wrong: Too many responsibilities
class MegaServicePort(Protocol):
    async def create_user(self, data: UserData) -> str: ...
    async def send_email(self, email: EmailData) -> None: ...
    async def log_activity(self, activity: str) -> None: ...

# ✅ Correct: Single responsibility
class UserServicePort(Protocol):
    async def create_user(self, data: UserData) -> str: ...

class NotificationPort(Protocol):
    async def send_email(self, email: EmailData) -> None: ...
```

### **Infrastructure Leakage**

```python
# ❌ Wrong: HTTP details in port
class OrderPort(Protocol):
    async def create_order(self, request: HttpRequest) -> HttpResponse: ...

# ✅ Correct: Domain-focused interface
class OrderPort(Protocol):
    async def create_order(self, command: CreateOrderCommand) -> str: ...
```

---

**📂 Hub**: [Ports Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+

---

**Last Updated**: 2025-06-11 | **Validation**: ✅ Source Code Verified
