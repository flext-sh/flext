# FLX Command Layer Pattern

## Overview

The FLX Command Layer Pattern provides a unified way to handle business operations across multiple interfaces (CLI, REST API, Web, gRPC, etc.) while maintaining clean architecture principles and separation of concerns.

## Architecture

```
┌─────────────────────────────────────────────────┐
│           INTERFACE ADAPTERS LAYER              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐     │
│  │   CLI   │  │ REST API │  │    Web    │     │
│  │ (Fire)  │  │(FastAPI) │  │ (Socket)  │     │
│  └────┬────┘  └────┬─────┘  └─────┬─────┘     │
│       │            │               │            │
│       └────────────┴───────────────┘            │
│                    │                            │
│                    ▼                            │
│         ┌─────────────────────┐                │
│         │    COMMAND BUS      │                │
│         │  (Routes commands)  │                │
│         └──────────┬──────────┘                │
└────────────────────┼────────────────────────────┘
                     │
┌────────────────────┼────────────────────────────┐
│                    ▼                            │
│         ┌─────────────────────┐                │
│         │ COMMAND HANDLERS    │                │
│         │ (Business Logic)    │                │
│         └──────────┬──────────┘                │
│                    │                            │
│           APPLICATION LAYER                     │
└────────────────────┼────────────────────────────┘
                     │
┌────────────────────┼────────────────────────────┐
│                    ▼                            │
│         ┌─────────────────────┐                │
│         │   DOMAIN LAYER      │                │
│         │ (Entities, Rules)   │                │
│         └─────────────────────┘                │
└─────────────────────────────────────────────────┘
```

## Core Components

### 1. Commands and Queries

Commands represent intentions to change system state:

```python
from flx.core.commands import Command

class CreateOrderCommand(Command):
    """Command to create a new order."""

    customer_id: str
    items: list[dict[str, Any]]
    shipping_address: str
```

Queries represent requests for information without side effects:

```python
from flx.core.commands import Query

class GetOrderQuery(Query):
    """Query to retrieve an order."""

    order_id: str
    include_items: bool = True
```

### 2. Command Handlers

Handlers contain the business logic for processing commands:

```python
from flx.core.commands import CommandHandler, command_handler

@command_handler
class CreateOrderHandler(CommandHandler[CreateOrderCommand, dict]):
    """Handler for creating orders."""

    def __init__(self, order_service: OrderService):
        self.order_service = order_service

    async def handle(self, command: CreateOrderCommand) -> dict:
        """Execute the create order command."""
        order = await self.order_service.create_order(
            customer_id=command.customer_id,
            items=command.items,
            shipping_address=command.shipping_address
        )
        return {
            "order_id": order.id,
            "status": order.status,
            "total": order.total
        }
```

### 3. Command Bus

The command bus routes commands to their handlers:

```python
from flx.core.commands import CommandBus

# Create and configure command bus
command_bus = CommandBus()
command_bus.register_command_handler(CreateOrderCommand, CreateOrderHandler())

# Execute command from any interface
result = await command_bus.execute_command(
    CreateOrderCommand(
        customer_id="CUST-123",
        items=[{"sku": "PROD-001", "qty": 2}],
        shipping_address="123 Main St"
    )
)
```

## Implementation Guide for Child Projects

### Step 1: Define Your Commands

Create a module for your domain commands:

```python
# src/your_project/commands/warehouse_commands.py
from flx.core.commands import Command, Query

class ReceiveInventoryCommand(Command):
    """Command to receive inventory into warehouse."""

    warehouse_id: str
    items: list[dict[str, Any]]
    reference_number: str

class GetInventoryLevelQuery(Query):
    """Query to get current inventory levels."""

    warehouse_id: str
    sku: str | None = None
```

### Step 2: Implement Command Handlers

Create handlers for your commands:

```python
# src/your_project/handlers/warehouse_handlers.py
from flx.core.commands import CommandHandler, command_handler

@command_handler
class ReceiveInventoryHandler(CommandHandler[ReceiveInventoryCommand, dict]):
    """Handler for receiving inventory."""

    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    async def handle(self, command: ReceiveInventoryCommand) -> dict:
        """Process inventory receipt."""
        receipt = await self.warehouse_service.receive_inventory(
            warehouse_id=command.warehouse_id,
            items=command.items,
            reference=command.reference_number
        )
        return {
            "receipt_id": receipt.id,
            "items_received": len(receipt.items),
            "status": "completed"
        }
```

### Step 3: Create Your CLI Adapter

Use Fire to create a CLI that uses the command bus:

```python
# src/your_project/cli.py
import fire
from your_project.commands import create_command_bus

class WarehouseCLI:
    """Warehouse management CLI."""

    def __init__(self):
        self.command_bus = create_command_bus()

    def receive_inventory(self, warehouse_id: str, reference: str, items_json: str):
        """Receive inventory into warehouse."""
        import json
        items = json.loads(items_json)

        command = ReceiveInventoryCommand(
            warehouse_id=warehouse_id,
            items=items,
            reference_number=reference
        )

        result = asyncio.run(self.command_bus.execute_command(command))
        if result.success:
            print(f"Receipt created: {result.data['receipt_id']}")
        else:
            print(f"Error: {result.error}")

def main():
    fire.Fire(WarehouseCLI)
```

### Step 4: Create Your REST API Adapter

Use FastAPI to expose the same commands via REST:

```python
# src/your_project/api.py
from fastapi import FastAPI
from your_project.commands import create_command_bus

app = FastAPI(title="Warehouse API")
command_bus = create_command_bus()

@app.post("/api/v1/inventory/receive")
async def receive_inventory(request: ReceiveInventoryRequest):
    """Receive inventory via REST API."""
    command = ReceiveInventoryCommand(
        warehouse_id=request.warehouse_id,
        items=request.items,
        reference_number=request.reference_number
    )

    result = await command_bus.execute_command(command)
    if result.success:
        return result.data
    else:
        raise HTTPException(status_code=400, detail=result.error)
```

### Step 5: Configure Command Bus

Create a factory function to set up your command bus:

```python
# src/your_project/commands/__init__.py
from flx.core.commands import CommandBus

def create_command_bus() -> CommandBus:
    """Create configured command bus for warehouse domain."""
    command_bus = CommandBus()

    # Create services
    warehouse_service = WarehouseService()

    # Register handlers
    command_bus.register_command_handler(
        ReceiveInventoryCommand,
        ReceiveInventoryHandler(warehouse_service)
    )

    # Add middleware
    from flx.core.commands import LoggingMiddleware
    command_bus.add_middleware(LoggingMiddleware(logger))

    return command_bus
```

## Best Practices

### 1. Command Design

- **Immutable**: Commands should be immutable once created
- **Self-contained**: Include all data needed to execute the operation
- **Validated**: Use Pydantic for automatic validation
- **Named clearly**: Use imperative mood (CreateOrder, not OrderCreation)

### 2. Handler Implementation

- **Single Responsibility**: Each handler handles one command type
- **Dependency Injection**: Inject services through constructor
- **Error Handling**: Return clear error messages in CommandResult
- **Async by Default**: Use async/await for better performance

### 3. Testing

Commands and handlers are highly testable:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_receive_inventory_handler():
    # Arrange
    mock_service = AsyncMock()
    mock_service.receive_inventory.return_value = Receipt(id="R-123", items=[])

    handler = ReceiveInventoryHandler(mock_service)
    command = ReceiveInventoryCommand(
        warehouse_id="WH-001",
        items=[{"sku": "PROD-001", "qty": 10}],
        reference_number="PO-123"
    )

    # Act
    result = await handler.handle(command)

    # Assert
    assert result["receipt_id"] == "R-123"
    mock_service.receive_inventory.assert_called_once()
```

### 4. Middleware

Use middleware for cross-cutting concerns:

```python
class AuthorizationMiddleware(CommandMiddleware):
    """Check user permissions before executing commands."""

    async def process(self, command: Command, next_handler):
        # Check if user can execute this command
        if not self.user_can_execute(command):
            raise UnauthorizedError("User lacks permission")

        return await next_handler(command)
```

## Advanced Features

### 1. Command Metadata

Track command execution with metadata:

```python
command = CreateOrderCommand(
    customer_id="CUST-123",
    items=items
).with_metadata(
    source="rest_api",
    user_id="USER-456",
    correlation_id=request_id
)
```

### 2. Event Sourcing

Commands naturally support event sourcing:

```python
@command_handler
class CreateOrderHandler(CommandHandler[CreateOrderCommand, Order]):
    async def handle(self, command: CreateOrderCommand) -> Order:
        # Create order
        order = Order.create(command)

        # Publish domain events
        await self.event_bus.publish(
            OrderCreatedEvent(
                order_id=order.id,
                customer_id=command.customer_id,
                timestamp=command.metadata.timestamp
            )
        )

        return order
```

### 3. Command Validation

Add business rule validation:

```python
class CreateOrderCommand(Command):
    customer_id: str
    items: list[OrderItem]

    @field_validator('items')
    def validate_items(cls, items):
        if not items:
            raise ValueError("Order must have at least one item")
        return items
```

## Benefits

1. **Separation of Concerns**: Interface adapters don't contain business logic
2. **Testability**: Commands and handlers are easy to unit test
3. **Reusability**: Same business logic across multiple interfaces
4. **Maintainability**: Changes to business logic happen in one place
5. **Scalability**: Easy to add new interfaces or commands
6. **Traceability**: Commands provide natural audit trail

## Example Project Structure

```
your-project/
├── src/
│   └── your_project/
│       ├── __init__.py
│       ├── domain/           # Domain models
│       │   ├── __init__.py
│       │   ├── order.py
│       │   └── inventory.py
│       ├── commands/         # Commands and queries
│       │   ├── __init__.py
│       │   ├── order_commands.py
│       │   └── inventory_commands.py
│       ├── handlers/         # Command handlers
│       │   ├── __init__.py
│       │   ├── order_handlers.py
│       │   └── inventory_handlers.py
│       ├── services/         # Application services
│       │   ├── __init__.py
│       │   └── order_service.py
│       ├── adapters/         # Interface adapters
│       │   ├── __init__.py
│       │   ├── cli.py       # Fire CLI
│       │   ├── api.py       # FastAPI
│       │   └── grpc.py      # gRPC service
│       └── infrastructure/   # External integrations
│           ├── __init__.py
│           └── database.py
└── tests/
    ├── unit/
    │   ├── test_commands.py
    │   └── test_handlers.py
    └── integration/
        └── test_command_bus.py
```

## Migration from Direct Implementation

If you have existing code that directly implements business logic in CLI or API endpoints, here's how to migrate:

1. **Extract business logic** into command handlers
2. **Define commands** for each operation
3. **Update interfaces** to use command bus
4. **Add tests** for commands and handlers
5. **Remove old implementation** once verified

## Conclusion

The FLX Command Layer Pattern provides a robust foundation for building maintainable, testable, and scalable applications. By separating interface concerns from business logic, you can easily add new interfaces, modify business rules, and test your application thoroughly.

For more examples and advanced usage, see the FLX framework documentation and example projects.
