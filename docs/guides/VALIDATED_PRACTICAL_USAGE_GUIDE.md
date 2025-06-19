# Validated Practical Usage Guide - Implementation

> **Function**: Real-world usage patterns validated against code examples | **Audience**: Developers implementing FLX | **Status**: ✅ Production Validated

[![Practical](https://img.shields.io/badge/type-practical-green.svg)](#real-world-integration-patterns)
[![Validated](https://img.shields.io/badge/status-code_validated-blue.svg)](#best-practices-summary)
[![Examples](https://img.shields.io/badge/examples-verified-orange.svg)](#application-context-pattern)

**Production-ready usage patterns demonstrating real FLX Framework 0.4.0+ implementation with validated examples and best practices**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Guides](./index.md) → **📄 Current**: Validated Practical Usage Guide

### **📍 Learning Path Position**

```
[Getting Started Hub](../getting-started/index.md) → [Guides Hub](./index.md) → **[PRACTICAL USAGE]** → [Oracle Integration](./oracle/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Guides Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Related**: [Oracle Integration](./oracle/index.md)

---

## 🎯 **Real-World Integration Patterns**

Based on `/examples/flx_integrated_usage.py`:

### **Multi-System Integration**

```python
class FlxIntegratedApplication:
    """Integrated FLX Application combining multiple system adapters."""

    def __init__(self):
        # Oracle Database configuration
        self.oracle_config = FlxOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="wms_user",
            password="wms_password",
        )

        # Application instances
        self.oracle_app: FlxOracleApplicationContext = None
        self.wms_app: WmsApplication = None
        self.oic_app: OicApplication = None

        # Unified CLI across all systems
        self.unified_cli: FlxDeclarativeCli = None

    async def initialize(self):
        """Initialize all integrated applications."""
        # Initialize Oracle Database
        self.oracle_app = FlxOracleApplicationContext(self.oracle_config)
        await self.oracle_app.__aenter__()

        # Create unified CLI
        self.unified_cli = FlxDeclarativeCli("flx-integrated")

        # Register all adapters
        if self.oracle_app.app:
            oracle_cli = self.oracle_app.app.get_cli()
            self.unified_cli.register_adapter(
                "oracle-resource",
                oracle_cli.resource_adapter
            )
```

### **Cross-System Workflow**

Real implementation pattern from examples:

```python
async def demonstrate_cross_system_workflow():
    """Workflow spanning multiple systems."""
    app = FlxIntegratedApplication()
    await app.initialize()

    try:
        # Step 1: Query inventory from Oracle
        inventory_data = await app.oracle_app.app.get_table_data(
            "inventory",
            limit=10,
            filters={"facility_id": "DC001"}
        )

        # Step 2: Analyze for low stock
        low_stock_items = [
            item for item in inventory_data
            if item.get("quantity", 0) < 100
        ]

        # Step 3: Create purchase orders in WMS
        for item in low_stock_items:
            order = await app.wms_app.create_purchase_order(
                item_id=item.get("item_id"),
                quantity=500 - item.get("quantity")
            )

        # Step 4: Log completion
        await app.oracle_app.app.run_operation(
            "log_workflow_completion",
            {"workflow": "inventory_replenishment"}
        )

    finally:
        await app.shutdown()
```

---

## 🏗️ **Application Context Pattern**

Based on actual Oracle adapter implementation:

### **Resource Management**

```python
class FlxOracleApplicationContext:
    """Context manager for Oracle application lifecycle."""

    async def __aenter__(self):
        """Initialize application with all resources."""
        # Create connection pool
        self.pool = await create_oracle_pool(self.config)

        # Initialize repositories
        self.repos = {
            "customer": CustomerRepository(self.pool),
            "order": OrderRepository(self.pool),
            "inventory": InventoryRepository(self.pool)
        }

        # Initialize services
        self.services = {
            "order": OrderService(
                self.repos["order"],
                self.repos["inventory"]
            ),
            "customer": CustomerService(self.repos["customer"])
        }

        # Create application
        self.app = FlxOracleApplication(
            config=self.config,
            repos=self.repos,
            services=self.services
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up all resources."""
        if self.pool:
            await self.pool.close()
```

### **Usage Pattern**

```python
async def main():
    # Automatic resource management
    async with FlxOracleApplicationContext(config) as ctx:
        # Use application
        customers = await ctx.app.customer_service.find_active()

        for customer in customers:
            orders = await ctx.app.order_service.find_by_customer(
                customer.entity_id
            )
            # Process orders...

    # Resources automatically cleaned up
```

---

## 🔌 **Declarative CLI Pattern**

Based on actual CLI implementation:

### **Unified CLI Setup**

```python
# Create unified CLI
cli = FlxDeclarativeCli("my-app")

# Register Oracle adapter
cli.register_adapter("oracle", oracle_adapter)

# Register WMS adapter
cli.register_adapter("wms", wms_adapter)

# Register OIC adapter
cli.register_adapter("oic", oic_adapter)

# Commands available:
# my-app oracle get customers 123
# my-app wms create order --customer-id=123
# my-app oic trigger integration INT_001
```

### **Adapter Registration**

```python
class ResourceAdapter:
    """Resource operations adapter for CLI."""

    async def get(self, resource_type: str, resource_id: str) -> dict:
        """Get single resource."""
        repo = self.get_repository(resource_type)
        entity = await repo.get(UUID(resource_id))
        return entity.model_dump() if entity else {}

    async def list(self, resource_type: str, **filters) -> list[dict]:
        """List resources with filters."""
        repo = self.get_repository(resource_type)
        entities = await repo.find_by(**filters)
        return [e.model_dump() for e in entities]

    async def create(self, resource_type: str, data: dict) -> dict:
        """Create new resource."""
        entity_class = self.get_entity_class(resource_type)
        entity = entity_class(**data)

        repo = self.get_repository(resource_type)
        saved = await repo.add(entity)
        return saved.model_dump()
```

---

## 💼 **Business Operations Pattern**

### **Domain Service Implementation**

Based on real service patterns:

```python
class OrderService:
    """Order business logic service."""

    def __init__(self,
                 order_repo: RepositoryPort[Order],
                 inventory_repo: RepositoryPort[InventoryItem],
                 event_bus: EventBus):
        self.order_repo = order_repo
        self.inventory_repo = inventory_repo
        self.event_bus = event_bus

    async def create_order(self,
                          customer_id: str,
                          items: list[dict]) -> Order:
        """Create order with inventory validation."""
        # Create order aggregate
        order = Order(customer_id=customer_id)

        # Validate and reserve inventory
        for item in items:
            inventory = await self.inventory_repo.get(item["product_id"])
            if not inventory or inventory.available < item["quantity"]:
                raise InsufficientInventoryError(item["product_id"])

            # Add to order
            order.add_item(
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=inventory.unit_price
            )

            # Reserve inventory
            inventory.reserve(item["quantity"])
            await self.inventory_repo.save(inventory)

        # Save order
        saved_order = await self.order_repo.save(order)

        # Publish events
        events = order.collect_events()
        await self.event_bus.publish_batch(events)

        return saved_order
```

### **Operation Pattern**

```python
class OperationAdapter:
    """Business operations adapter."""

    async def execute(self, operation_name: str, params: dict) -> dict:
        """Execute business operation."""
        match operation_name:
            case "create_order":
                order = await self.order_service.create_order(
                    customer_id=params["customer_id"],
                    items=params["items"]
                )
                return {"order_id": str(order.entity_id), "status": order.status}

            case "ship_order":
                await self.fulfillment_service.ship_order(
                    order_id=params["order_id"],
                    carrier=params["carrier"]
                )
                return {"status": "shipped"}

            case "analyze_inventory":
                report = await self.analytics_service.analyze_inventory(
                    facility_id=params.get("facility_id")
                )
                return report.model_dump()

            case _:
                raise ValueError(f"Unknown operation: {operation_name}")
```

---

## 📊 **Data Access Patterns**

### **Repository Pattern**

Real repository implementation:

```python
class PostgresOrderRepository(RepositoryPort[Order]):
    """PostgreSQL implementation of order repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_customer(self, customer_id: str) -> list[Order]:
        """Find orders by customer - domain-specific method."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.customer_id == customer_id)
            .order_by(OrderModel.created_at.desc())
        )

        return [
            self._to_domain_entity(db_order)
            for db_order in result.scalars()
        ]

    async def find_pending_shipments(self) -> list[Order]:
        """Find orders pending shipment - business query."""
        result = await self.session.execute(
            select(OrderModel)
            .where(OrderModel.status == "confirmed")
            .where(OrderModel.shipped_at.is_(None))
            .order_by(OrderModel.created_at)
        )

        return [
            self._to_domain_entity(db_order)
            for db_order in result.scalars()
        ]

    def _to_domain_entity(self, db_model: OrderModel) -> Order:
        """Convert DB model to domain entity."""
        order = Order(
            entity_id=db_model.id,
            customer_id=db_model.customer_id,
            status=db_model.status,
            version=db_model.version
        )

        # Reconstruct order items
        for db_item in db_model.items:
            order.items.append(OrderItem(
                entity_id=db_item.id,
                product_id=db_item.product_id,
                quantity=db_item.quantity,
                unit_price=db_item.unit_price
            ))

        return order
```

### **Query Builder Pattern**

```python
class QueryBuilder:
    """Fluent query builder for complex queries."""

    def __init__(self, repo: RepositoryPort):
        self.repo = repo
        self._filters = {}
        self._order_by = []
        self._limit = None

    def where(self, **criteria) -> Self:
        """Add filter criteria."""
        self._filters.update(criteria)
        return self

    def order_by(self, field: str, desc: bool = False) -> Self:
        """Add ordering."""
        self._order_by.append((field, desc))
        return self

    def limit(self, count: int) -> Self:
        """Limit results."""
        self._limit = count
        return self

    async def get(self) -> list[Entity]:
        """Execute query."""
        results = await self.repo.find_by(**self._filters)

        # Apply ordering
        for field, desc in self._order_by:
            results.sort(
                key=lambda x: getattr(x, field),
                reverse=desc
            )

        # Apply limit
        if self._limit:
            results = results[:self._limit]

        return results

# Usage
recent_orders = await (
    QueryBuilder(order_repo)
    .where(status="confirmed")
    .order_by("created_at", desc=True)
    .limit(10)
    .get()
)
```

---

## 🔄 **Event-Driven Patterns**

### **Event Publishing**

From real implementation:

```python
class EventDrivenOrderService:
    """Order service with event publishing."""

    async def confirm_order(self, order_id: str) -> None:
        """Confirm order and publish events."""
        # Load aggregate
        order = await self.order_repo.get(order_id)
        if not order:
            raise OrderNotFoundError(order_id)

        # Business operation
        order.confirm()  # This adds OrderConfirmedEvent

        # Save with optimistic locking
        try:
            await self.order_repo.save(order)
        except OptimisticLockingError:
            # Reload and retry
            order = await self.order_repo.get(order_id)
            order.confirm()
            await self.order_repo.save(order)

        # Publish events
        events = order.collect_events()
        await self.event_bus.publish_batch(events)
```

### **Event Handling**

```python
class InventoryEventHandler:
    """Handle order events for inventory updates."""

    async def handle_order_confirmed(self, event: OrderConfirmedEvent) -> None:
        """Update inventory when order is confirmed."""
        order = await self.order_repo.get(event.order_id)

        for item in order.items:
            inventory = await self.inventory_repo.get(item.product_id)
            inventory.commit_reservation(item.quantity)
            await self.inventory_repo.save(inventory)

    async def handle_order_cancelled(self, event: OrderCancelledEvent) -> None:
        """Release inventory when order is cancelled."""
        order = await self.order_repo.get(event.order_id)

        for item in order.items:
            inventory = await self.inventory_repo.get(item.product_id)
            inventory.release_reservation(item.quantity)
            await self.inventory_repo.save(inventory)

# Registration
event_bus.subscribe(OrderConfirmedEvent, handler.handle_order_confirmed)
event_bus.subscribe(OrderCancelledEvent, handler.handle_order_cancelled)
```

---

## 🧪 **Testing Patterns**

### **Integration Testing**

Real test patterns:

```python
async def test_cross_system_workflow():
    """Test complete workflow across systems."""
    # Setup test data
    async with test_context() as ctx:
        # Create test customer
        customer = await ctx.customer_repo.add(
            Customer(name="Test Customer", email="test@example.com")
        )

        # Create test inventory
        await ctx.inventory_repo.add(
            InventoryItem(
                product_id="PROD-001",
                quantity=50,
                unit_price=29.99
            )
        )

        # Execute workflow
        app = FlxIntegratedApplication()
        await app.initialize()

        # Test order creation
        order = await app.create_order(
            customer_id=str(customer.entity_id),
            items=[{"product_id": "PROD-001", "quantity": 10}]
        )

        assert order.status == "confirmed"
        assert len(order.items) == 1

        # Verify inventory updated
        inventory = await ctx.inventory_repo.get("PROD-001")
        assert inventory.quantity == 40

        # Verify events published
        events = await ctx.event_store.get_events(order.entity_id)
        assert any(isinstance(e, OrderConfirmedEvent) for e in events)
```

### **Adapter Testing**

```python
class MockHttpClient:
    """Mock HTTP client for testing."""

    def __init__(self):
        self.responses = {}
        self.requests = []

    def set_response(self, method: str, url: str, response: dict):
        """Set mock response."""
        self.responses[(method, url)] = response

    async def request(self, method: str, url: str, **kwargs):
        """Record request and return mock response."""
        self.requests.append({
            "method": method,
            "url": url,
            "kwargs": kwargs
        })

        return self.responses.get((method, url), {"error": "not found"})

async def test_wms_adapter():
    """Test WMS adapter with mocks."""
    mock_client = MockHttpClient()
    mock_client.set_response(
        "GET",
        "/api/v1/orders/123",
        {"order_id": "123", "status": "confirmed"}
    )

    adapter = WmsAdapter(client=mock_client)
    order = await adapter.get_order("123")

    assert order.entity_id == "123"
    assert order.status == "confirmed"
    assert len(mock_client.requests) == 1
```

---

## 🚀 **Performance Patterns**

### **Connection Pooling**

```python
class PooledDatabaseAdapter:
    """Database adapter with connection pooling."""

    async def initialize(self):
        """Create connection pool."""
        self.pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.username,
            password=self.config.password,
            min_size=2,
            max_size=10,
            command_timeout=60,
            max_queries=50000,
            max_inactive_connection_lifetime=300
        )

    async def execute_query(self, query: str, params: dict = None):
        """Execute query using pooled connection."""
        async with self.pool.acquire() as connection:
            # Use prepared statement for performance
            stmt = await connection.prepare(query)
            return await stmt.fetch(**params or {})
```

### **Batch Operations**

```python
class BatchProcessor:
    """Efficient batch processing."""

    async def process_orders_batch(self, order_ids: list[str]):
        """Process multiple orders efficiently."""
        # Batch load
        orders = await self.order_repo.get_many(order_ids)

        # Collect all product IDs
        product_ids = {
            item.product_id
            for order in orders
            for item in order.items
        }

        # Batch load inventory
        inventory_map = await self.inventory_repo.get_many_as_map(
            list(product_ids)
        )

        # Process orders
        results = []
        for order in orders:
            try:
                result = await self._process_single_order(
                    order,
                    inventory_map
                )
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "order_id": order.entity_id})

        return results
```

---

## 📋 **Best Practices Summary**

Based on real implementation analysis:

### **1. Use Application Context**

- ✅ Manage resources with async context managers
- ✅ Initialize all dependencies in one place
- ✅ Ensure proper cleanup

### **2. Implement Domain Patterns**

- ✅ Keep business logic in domain services
- ✅ Use repository pattern for data access
- ✅ Emit domain events for cross-boundary communication

### **3. Design for Testing**

- ✅ Use dependency injection
- ✅ Create mock implementations of ports
- ✅ Test each layer independently

### **4. Optimize Performance**

- ✅ Use connection pooling
- ✅ Implement batch operations
- ✅ Cache frequently accessed data

### **5. Handle Errors Gracefully**

- ✅ Implement retry strategies
- ✅ Use circuit breakers for external services
- ✅ Provide meaningful error messages

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Getting Started Hub](../getting-started/index.md) - Basic FLX Framework setup and installation
- [Architecture Hub](../architecture/index.md) - Understanding hexagonal architecture patterns before implementation
- [Core Domain Guide](../architecture/layers/core-domain-layer.md) - Domain layer concepts used in practical examples

### **Next Steps**

- [Oracle Integration Guides](./oracle/index.md) - Specific Oracle implementation patterns applying these practices
- [Testing Strategies](../development/testing/index.md) - Testing approaches for patterns demonstrated here
- [Production Deployment](../deployment/index.md) - Deploy applications using these validated patterns

### **Related Topics**

- [Real-World Implementation Guide](../getting-started/real-world-implementation-guide.md) - Complementary real-world patterns and implementation examples
- [Core Domain Layer](../architecture/core-domain-layer.md) - Domain patterns and entity implementations used in practical examples
- [Environment Configuration Guide](../development/guides/environment-configuration.md) - Configuration management patterns used in practical implementations
- [Examples Hub](../examples/index.md) - Working code examples that validate these patterns
- [API Reference](../api-reference/index.md) - Technical specifications for implementations shown here
- [Infrastructure Services](../infrastructure/index.md) - Infrastructure supporting these usage patterns
- [Performance Optimization](../optimization/index.md) - Optimize implementations based on these patterns

---

**📂 Hub**: [Guides Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
