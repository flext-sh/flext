# FLEXT Testing Guide

Comprehensive testing strategies for FLEXT applications, plugins, and integrations. This guide covers the complete testing pyramid from unit tests to end-to-end testing with practical examples and best practices.

## 🎯 Testing Philosophy

FLEXT follows a comprehensive testing strategy based on the testing pyramid, ensuring reliable and maintainable code through multiple levels of testing that align with hexagonal architecture principles.

### Core Testing Principles

- **Test-Driven Development**: Write tests before implementation when possible
- **Comprehensive Coverage**: Target >90% test coverage across the codebase
- **Fast Feedback**: Unit tests complete in <1 second, full suite in <5 minutes
- **Reliable**: Tests are deterministic, independent, and reproducible
- **Maintainable**: Tests are easy to understand, update, and extend
- **Architecture-Aligned**: Tests respect hexagonal architecture boundaries

## 📊 Testing Pyramid

```
              ┌─────────────────┐
              │   E2E Tests     │  ← 10% - Full system integration
              │   (Slow)        │    - Real external connections
              │                 │    - Complete user workflows
              │                 │    - Production-like environments
              ├─────────────────┤
              │ Integration     │  ← 20% - Component interactions
              │ Tests (Medium)  │    - Adapter ↔ Infrastructure
              │                 │    - Port ↔ Adapter integration
              │                 │    - Database operations
              ├─────────────────┤
              │   Unit Tests    │  ← 70% - Isolated components
              │   (Fast)        │    - Domain logic testing
              │                 │    - Pure function testing
              │                 │    - Mocked dependencies
              └─────────────────┘
```

### Test Distribution Guidelines

- **70% Unit Tests**: Focus on business logic, domain entities, and pure functions
- **20% Integration Tests**: Test component interactions and adapter implementations
- **10% End-to-End Tests**: Validate complete workflows with real systems

## 🧪 Testing Framework Stack

### Core Testing Tools

| Tool               | Purpose                   | Usage in FLEXT            |
| ------------------ | ------------------------- | ----------------------- |
| **pytest**         | Test runner and framework | Primary testing tool    |
| **pytest-asyncio** | Async testing support     | Test async operations   |
| **pytest-mock**    | Mocking and patching      | Isolate dependencies    |
| **pytest-cov**     | Coverage reporting        | Measure test coverage   |
| **pytest-xdist**   | Parallel test execution   | Speed up test execution |
| **factory-boy**    | Test data factories       | Generate test data      |
| **fakeredis**      | Redis mocking             | Test cache operations   |
| **httpx**          | HTTP testing              | Test HTTP adapters      |

### Test Configuration

```python
# pytest.ini
[tool:pytest]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/flext",
    "--cov-report=html:reports/coverage/html",
    "--cov-report=term-missing",
    "--cov-report=json:reports/coverage/coverage.json",
    "--cov-fail-under=90",
    "--tb=short"
]
markers = [
    "unit: Unit tests for isolated components",
    "integration: Integration tests for component interactions",
    "e2e: End-to-end tests with real systems",
    "slow: Slow running tests (>1 second)",
    "oracle: Oracle database specific tests",
    "redis: Redis cache specific tests",
    "http: HTTP adapter specific tests",
    "performance: Performance and load tests"
]
```

## 🔧 Unit Testing

Unit tests focus on testing individual components in isolation, particularly domain logic and business rules.

### Testing Domain Entities

```python
# tests/unit/test_domain_entities.py
import pytest
from datetime import datetime
from flext import Flx
from flext.core.exceptions import FlextValidationError

class TestDomainEntities:
    """Unit tests for FLEXT domain entities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.flext = Flx()

    def test_base_entity_creation(self):
        """Test basic entity creation and properties."""
        entity = self.flext.Entities.BaseEntity(name="Test Entity")

        assert entity.name == "Test Entity"
        assert entity.id.startswith("ent_")
        assert isinstance(entity.created_at, datetime)
        assert entity.active is True
        assert entity.is_valid()

    def test_entity_id_uniqueness(self):
        """Test that entities get unique IDs."""
        entity1 = self.flext.Entities.BaseEntity(name="Entity 1")
        entity2 = self.flext.Entities.BaseEntity(name="Entity 2")

        assert entity1.id != entity2.id

    def test_business_entity_validation(self):
        """Test business entity validation rules."""
        # Valid business entity
        entity = self.flext.Entities.BusinessEntity(
            name="Acme Corp",
            business_type="Enterprise"
        )
        assert entity.is_valid()
        assert entity.business_type == "Enterprise"

        # Invalid business entity (empty business_type)
        with pytest.raises(FlextValidationError):
            self.flext.Entities.BusinessEntity(
                name="Invalid Corp",
                business_type=""
            )

    def test_aggregate_root_events(self):
        """Test aggregate root domain event functionality."""
        aggregate = self.flext.Entities.AggregateRoot(name="Order Aggregate")

        # Initially no events
        assert len(aggregate.get_domain_events()) == 0

        # Raise domain events
        aggregate.raise_domain_event("OrderCreated", {"order_id": "123"})
        aggregate.raise_domain_event("ItemAdded", {"item_id": "456"})

        events = aggregate.get_domain_events()
        assert len(events) == 2
        assert events[0].event_type == "OrderCreated"
        assert events[1].event_type == "ItemAdded"

        # Clear events
        aggregate.clear_domain_events()
        assert len(aggregate.get_domain_events()) == 0

    @pytest.mark.parametrize("name,expected_valid", [
        ("Valid Name", True),
        ("valid_name_123", True),
        ("", False),           # Empty name
        ("   ", False),        # Whitespace only
        ("a" * 300, False),    # Too long
    ])
    def test_entity_name_validation(self, name, expected_valid):
        """Test entity name validation rules."""
        if expected_valid:
            entity = self.flext.Entities.BaseEntity(name=name)
            assert entity.is_valid()
        else:
            with pytest.raises(FlextValidationError):
                self.flext.Entities.BaseEntity(name=name)
```

### Testing Value Objects

```python
# tests/unit/test_value_objects.py
import pytest
from flext import Flx
from flext.core.exceptions import FlextValidationError

class TestValueObjects:
    """Unit tests for FLEXT value objects."""

    def setup_method(self):
        """Set up test fixtures."""
        self.flext = Flx()

    def test_contact_info_creation(self):
        """Test contact info value object creation."""
        contact = self.flext.ValueObjects.ContactInfo(
            email="john.doe@example.com",
            phone="+1-555-0123",
            address="123 Main St, City, ST 12345"
        )

        assert contact.email == "john.doe@example.com"
        assert contact.phone == "+1-555-0123"
        assert contact.address == "123 Main St, City, ST 12345"

    def test_contact_info_immutability(self):
        """Test that contact info is immutable."""
        contact = self.flext.ValueObjects.ContactInfo(
            email="john.doe@example.com",
            phone="+1-555-0123"
        )

        # Value objects should be immutable
        with pytest.raises(AttributeError):
            contact.email = "new.email@example.com"

    def test_domain_event_creation(self):
        """Test domain event value object creation."""
        event = self.flext.ValueObjects.FlextDomainEvent(
            event_type="UserRegistered",
            aggregate_id="user_123",
            aggregate_type="User",
            event_data={"email": "user@example.com", "role": "customer"}
        )

        assert event.event_type == "UserRegistered"
        assert event.aggregate_id == "user_123"
        assert event.aggregate_type == "User"
        assert event.event_data["email"] == "user@example.com"
        assert event.event_id.startswith("evt_")
        assert event.occurred_at is not None

    @pytest.mark.parametrize("email,expected_valid", [
        ("valid@example.com", True),
        ("user.name+tag@domain.co.uk", True),
        ("invalid-email", False),
        ("@example.com", False),
        ("user@", False),
        ("", False),
    ])
    def test_email_validation(self, email, expected_valid):
        """Test email validation in contact info."""
        if expected_valid:
            contact = self.flext.ValueObjects.ContactInfo(email=email)
            assert contact.email == email
        else:
            with pytest.raises(FlextValidationError):
                self.flext.ValueObjects.ContactInfo(email=email)
```

### Testing Mixins

```python
# tests/unit/test_mixins.py
import pytest
from flext import Flx

class TestMixins:
    """Unit tests for FLEXT mixins."""

    def setup_method(self):
        """Set up test fixtures."""
        self.flext = Flx()

    def test_status_mixin(self):
        """Test status mixin functionality."""
        class TestEntity(
            self.flext.Entities.BaseEntity,
            self.flext.Mixins.Status
        ):
            pass

        entity = TestEntity(name="Test Entity")

        # Initially active
        assert entity.active is True
        assert entity.is_active()

        # Deactivate
        entity.deactivate()
        assert entity.active is False
        assert not entity.is_active()

        # Reactivate
        entity.activate()
        assert entity.active is True
        assert entity.is_active()

    def test_config_mixin(self):
        """Test configuration mixin functionality."""
        class TestEntity(
            self.flext.Entities.BaseEntity,
            self.flext.Mixins.Config
        ):
            pass

        entity = TestEntity(name="Test Entity")

        # Set configuration
        entity.set_config("max_connections", 100)
        entity.set_config("timeout", 30.0)
        entity.set_config("enable_ssl", True)

        # Get configuration
        assert entity.get_config("max_connections") == 100
        assert entity.get_config("timeout") == 30.0
        assert entity.get_config("enable_ssl") is True
        assert entity.get_config("non_existent") is None
        assert entity.get_config("non_existent", "default") == "default"

        # Check configuration existence
        assert entity.has_config("max_connections")
        assert not entity.has_config("non_existent")

        # Remove configuration
        entity.remove_config("timeout")
        assert not entity.has_config("timeout")

    def test_metadata_mixin(self):
        """Test metadata mixin functionality."""
        class TestEntity(
            self.flext.Entities.BaseEntity,
            self.flext.Mixins.Metadata
        ):
            pass

        entity = TestEntity(name="Test Entity")

        # Add metadata
        entity.add_metadata("environment", "production")
        entity.add_metadata("region", "us-east-1")
        entity.add_metadata("version", "1.2.3")

        # Get metadata
        assert entity.get_metadata("environment") == "production"
        assert entity.get_metadata("region") == "us-east-1"
        assert entity.get_metadata("version") == "1.2.3"
        assert entity.get_metadata("non_existent") is None

        # Get all metadata
        all_metadata = entity.get_all_metadata()
        assert all_metadata["environment"] == "production"
        assert all_metadata["region"] == "us-east-1"
        assert all_metadata["version"] == "1.2.3"

        # Remove metadata
        entity.remove_metadata("version")
        assert entity.get_metadata("version") is None

    def test_combined_mixins(self):
        """Test entity with multiple mixins."""
        class AdvancedEntity(
            self.flext.Entities.BaseEntity,
            self.flext.Mixins.Status,
            self.flext.Mixins.Config,
            self.flext.Mixins.Metadata
        ):
            pass

        entity = AdvancedEntity(name="Advanced Entity")

        # Test all capabilities work together
        entity.set_config("mode", "production")
        entity.add_metadata("datacenter", "us-west-2")
        entity.deactivate()

        assert entity.get_config("mode") == "production"
        assert entity.get_metadata("datacenter") == "us-west-2"
        assert not entity.is_active()
```

## 🔗 Integration Testing

Integration tests verify that components work correctly together, particularly testing adapter implementations with their infrastructure services.

### Testing Adapter Integration

```python
# tests/integration/test_cache_adapter.py
import pytest
import pytest_asyncio
from flext.adapters.outbound.cache import CacheAdapter
from flext.infra.cache.cache_service import CacheService
from flext.core.exceptions import FlextConnectionError

@pytest.mark.integration
class TestCacheAdapterIntegration:
    """Integration tests for cache adapter."""

    @pytest.fixture
    async def cache_adapter(self):
        """Create cache adapter for testing."""
        adapter = CacheAdapter()
        adapter.configure({
            "backend": "memory",
            "memory_cache_size": 100,
            "default_ttl": 300
        })

        await adapter.connect()
        yield adapter
        await adapter.disconnect()

    async def test_adapter_service_integration(self, cache_adapter):
        """Test adapter properly delegates to cache service."""
        # Verify service is created and connected
        assert cache_adapter._cache_service is not None
        assert isinstance(cache_adapter._cache_service, CacheService)

        # Test operations work through adapter
        await cache_adapter.set("test_key", "test_value")
        value = await cache_adapter.get("test_key")
        assert value == "test_value"

        # Test health check integration
        health = await cache_adapter.health_check()
        assert health["status"] == "healthy"
        assert "backend_type" in health

    async def test_adapter_error_handling(self, cache_adapter):
        """Test adapter error handling with service failures."""
        await cache_adapter.disconnect()

        # Operations should raise appropriate errors
        with pytest.raises(FlextConnectionError):
            await cache_adapter.get("test_key")

        with pytest.raises(FlextConnectionError):
            await cache_adapter.set("test_key", "value")

    async def test_adapter_lifecycle_management(self):
        """Test adapter lifecycle management."""
        adapter = CacheAdapter()

        # Initially not connected
        assert not adapter.is_connected()
        assert adapter._cache_service is None

        # Configure and connect
        adapter.configure({"backend": "memory"})
        await adapter.connect()

        assert adapter.is_connected()
        assert adapter._cache_service is not None

        # Disconnect
        await adapter.disconnect()
        assert not adapter.is_connected()
```

### Testing Unified Manager Integration

```python
# tests/integration/test_unified_manager.py
import pytest
import pytest_asyncio
from flext.infra.adapters import UnifiedAdapterManager
from flext.adapters.outbound.cache import CacheAdapter
from flext.adapters.outbound.http import HttpAdapter

@pytest.mark.integration
class TestUnifiedManagerIntegration:
    """Integration tests for unified adapter manager."""

    @pytest.fixture
    async def configured_manager(self):
        """Create configured manager with test adapters."""
        manager = UnifiedAdapterManager(
            enable_messaging_features=True,
            instance_cache_size=100
        )

        # Create and configure adapters
        cache_adapter = CacheAdapter()
        cache_adapter.configure({"backend": "memory"})

        http_adapter = HttpAdapter()
        http_adapter.configure({"timeout": 30.0})

        # Register adapters
        manager.register("cache", cache_adapter)
        manager.register("http", http_adapter)

        await manager.initialize()
        yield manager
        await manager.stop()

    async def test_manager_adapter_lifecycle(self, configured_manager):
        """Test manager controls adapter lifecycle."""
        # Start all adapters
        results = await configured_manager.start_batch(
            ["cache", "http"],
            parallel=True
        )

        assert results["cache"] is True
        assert results["http"] is True

        # Verify adapters are running
        cache_adapter = configured_manager.get_adapter("cache")
        http_adapter = configured_manager.get_adapter("http")

        assert cache_adapter.is_connected()
        assert http_adapter.is_connected()

        # Stop all adapters
        results = await configured_manager.stop_batch(
            ["cache", "http"],
            parallel=True
        )

        assert results["cache"] is True
        assert results["http"] is True

        assert not cache_adapter.is_connected()
        assert not http_adapter.is_connected()

    async def test_manager_health_monitoring(self, configured_manager):
        """Test manager health monitoring capabilities."""
        await configured_manager.start_batch(["cache", "http"], parallel=True)

        # Individual health checks
        cache_health = await configured_manager.health_check_adapter("cache")
        assert cache_health["status"] == "healthy"

        http_health = await configured_manager.health_check_adapter("http")
        assert http_health["status"] == "healthy"

        # Comprehensive health check
        all_health = await configured_manager.health_check_all()
        assert "cache" in all_health
        assert "http" in all_health
        assert all_health["cache"]["status"] == "healthy"
        assert all_health["http"]["status"] == "healthy"

    async def test_manager_performance_metrics(self, configured_manager):
        """Test manager performance monitoring."""
        await configured_manager.start_batch(["cache", "http"], parallel=True)

        # Get performance metrics
        metrics = configured_manager.get_performance_metrics()

        assert "running_adapters" in metrics
        assert "error_adapters" in metrics
        assert "cache_utilization" in metrics
        assert "total_adapters" in metrics

        assert metrics["running_adapters"] == 2
        assert metrics["error_adapters"] == 0
        assert metrics["total_adapters"] == 2

    async def test_manager_batch_operations(self, configured_manager):
        """Test manager batch operation efficiency."""
        import time

        # Time sequential operations
        start_time = time.perf_counter()
        await configured_manager.start_adapter("cache")
        await configured_manager.start_adapter("http")
        sequential_time = time.perf_counter() - start_time

        await configured_manager.stop_adapter("cache")
        await configured_manager.stop_adapter("http")

        # Time parallel operations
        start_time = time.perf_counter()
        await configured_manager.start_batch(["cache", "http"], parallel=True)
        parallel_time = time.perf_counter() - start_time

        # Parallel should be faster than sequential
        assert parallel_time < sequential_time
        print(f"Sequential: {sequential_time:.3f}s, Parallel: {parallel_time:.3f}s")
```

## 🌐 End-to-End Testing

End-to-end tests validate complete workflows using real external systems.

### E2E Test Setup

```python
# tests/e2e/conftest.py
import pytest
import asyncio
import docker
from typing import AsyncGenerator

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session scope."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def redis_container():
    """Start Redis container for E2E tests."""
    client = docker.from_env()

    # Start Redis container
    container = client.containers.run(
        "redis:7-alpine",
        ports={"6379/tcp": 6379},
        detach=True,
        auto_remove=True
    )

    # Wait for Redis to be ready
    await asyncio.sleep(2)

    yield container

    # Cleanup
    container.stop()

@pytest.fixture(scope="session")
async def postgres_container():
    """Start PostgreSQL container for E2E tests."""
    client = docker.from_env()

    # Start PostgreSQL container
    container = client.containers.run(
        "postgres:15-alpine",
        environment={
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password"
        },
        ports={"5432/tcp": 5432},
        detach=True,
        auto_remove=True
    )

    # Wait for PostgreSQL to be ready
    await asyncio.sleep(5)

    yield container

    # Cleanup
    container.stop()
```

### Complete Workflow Tests

```python
# tests/e2e/test_complete_workflows.py
import pytest
import pytest_asyncio
from flext import Flx
from flext.infra.adapters import UnifiedAdapterManager
from flext.adapters.outbound.cache import CacheAdapter
from flext.adapters.outbound.database import DatabaseAdapter

@pytest.mark.e2e
class TestCompleteWorkflows:
    """End-to-end tests for complete FLEXT workflows."""

    @pytest.fixture
    async def production_application(self, redis_container, postgres_container):
        """Create production-like application setup."""
        flext = Flx()

        # Configure cache adapter with real Redis
        cache_adapter = CacheAdapter()
        cache_adapter.configure({
            "backend": "redis",
            "redis_url": "redis://localhost:6379",
            "memory_cache_size": 1000
        })

        # Configure database adapter with real PostgreSQL
        db_adapter = DatabaseAdapter()
        db_adapter.configure({
            "url": "postgresql://test_user:test_password@localhost:5432/test_db",
            "pool_size": 10
        })

        # Set up unified manager
        manager = UnifiedAdapterManager()
        manager.register("cache", cache_adapter)
        manager.register("database", db_adapter)

        await manager.initialize()
        await manager.start()

        yield {
            "flext": flext,
            "manager": manager,
            "cache": cache_adapter,
            "database": db_adapter
        }

        await manager.stop()

    async def test_data_pipeline_workflow(self, production_application):
        """Test complete data pipeline workflow."""
        app = production_application
        cache = app["cache"]
        database = app["database"]

        # 1. Create domain entities
        flext = app["flext"]
        customer = flext.Entities.BusinessEntity(
            name="E2E Test Customer",
            business_type="Enterprise"
        )

        order = flext.Entities.AggregateRoot(name="E2E Test Order")

        # 2. Cache customer data
        customer_key = f"customer:{customer.id}"
        await cache.set(customer_key, {
            "id": customer.id,
            "name": customer.name,
            "business_type": customer.business_type,
            "created_at": customer.created_at.isoformat()
        }, ttl=3600)

        # 3. Verify cached data
        cached_customer = await cache.get(customer_key)
        assert cached_customer is not None
        assert cached_customer["name"] == customer.name

        # 4. Raise domain events
        order.raise_domain_event("OrderCreated", {
            "customer_id": customer.id,
            "order_id": order.id,
            "total_amount": 1500.00
        })

        order.raise_domain_event("OrderCompleted", {
            "completion_time": "2024-01-15T10:30:00Z",
            "status": "completed"
        })

        # 5. Verify events
        events = order.get_domain_events()
        assert len(events) == 2
        assert events[0].event_type == "OrderCreated"
        assert events[1].event_type == "OrderCompleted"

        # 6. Store events in database (simulated)
        event_data = []
        for event in events:
            event_data.append({
                "event_id": event.event_id,
                "event_type": event.event_type,
                "aggregate_id": event.aggregate_id,
                "event_data": event.event_data,
                "occurred_at": event.occurred_at.isoformat()
            })

        # 7. Verify complete workflow
        assert len(event_data) == 2
        assert event_data[0]["event_type"] == "OrderCreated"
        assert event_data[1]["event_type"] == "OrderCompleted"

        # 8. Clean up cache
        deleted = await cache.delete(customer_key)
        assert deleted

        # Verify cleanup
        cached_after_delete = await cache.get(customer_key)
        assert cached_after_delete is None

    async def test_error_recovery_workflow(self, production_application):
        """Test error recovery and resilience."""
        app = production_application
        manager = app["manager"]

        # Get initial health status
        initial_health = await manager.health_check_all()
        assert all(h["status"] == "healthy" for h in initial_health.values())

        # Simulate service interruption by stopping cache
        cache_adapter = app["cache"]
        await cache_adapter.disconnect()

        # Health check should detect the issue
        degraded_health = await manager.health_check_all()
        assert degraded_health["cache"]["status"] != "healthy"
        assert degraded_health["database"]["status"] == "healthy"

        # Recover cache service
        await cache_adapter.connect()

        # Health should recover
        recovered_health = await manager.health_check_all()
        assert recovered_health["cache"]["status"] == "healthy"
        assert recovered_health["database"]["status"] == "healthy"

    @pytest.mark.performance
    async def test_performance_under_load(self, production_application):
        """Test system performance under load."""
        import time
        import asyncio

        app = production_application
        cache = app["cache"]
        flext = app["flext"]

        # Generate test data
        test_entities = []
        for i in range(100):
            entity = flext.Entities.BaseEntity(name=f"Load Test Entity {i}")
            test_entities.append(entity)

        # Benchmark cache operations
        start_time = time.perf_counter()

        # Concurrent cache operations
        tasks = []
        for entity in test_entities:
            task = cache.set(f"load_test:{entity.id}", {
                "id": entity.id,
                "name": entity.name,
                "created_at": entity.created_at.isoformat()
            }, ttl=300)
            tasks.append(task)

        await asyncio.gather(*tasks)

        write_duration = time.perf_counter() - start_time

        # Benchmark read operations
        start_time = time.perf_counter()

        read_tasks = []
        for entity in test_entities:
            task = cache.get(f"load_test:{entity.id}")
            read_tasks.append(task)

        results = await asyncio.gather(*read_tasks)

        read_duration = time.perf_counter() - start_time

        # Performance assertions
        assert write_duration < 5.0  # 100 writes in under 5 seconds
        assert read_duration < 2.0   # 100 reads in under 2 seconds
        assert all(r is not None for r in results)  # All reads successful

        # Cleanup
        delete_tasks = []
        for entity in test_entities:
            task = cache.delete(f"load_test:{entity.id}")
            delete_tasks.append(task)

        await asyncio.gather(*delete_tasks)

        print(f"Performance Results:")
        print(f"  Write 100 items: {write_duration:.3f}s")
        print(f"  Read 100 items: {read_duration:.3f}s")
        print(f"  Write throughput: {100/write_duration:.1f} ops/sec")
        print(f"  Read throughput: {100/read_duration:.1f} ops/sec")
```

## 🏭 Test Data Factories

Use factories to generate consistent test data across all test levels.

### Entity Factories

```python
# tests/factories.py
import factory
from datetime import datetime, timezone
from flext import Flx

class FlextEntityFactory:
    """Factory for creating FLEXT test entities."""

    def __init__(self):
        self.flext = Flx()

    def create_base_entity(self, **kwargs):
        """Create a base entity with default values."""
        defaults = {
            "name": factory.Faker("company").generate(),
        }
        defaults.update(kwargs)
        return self.flext.Entities.BaseEntity(**defaults)

    def create_business_entity(self, **kwargs):
        """Create a business entity with realistic data."""
        defaults = {
            "name": factory.Faker("company").generate(),
            "business_type": factory.Faker("random_element",
                elements=("Enterprise", "SMB", "Startup")).generate()
        }
        defaults.update(kwargs)
        return self.flext.Entities.BusinessEntity(**defaults)

    def create_aggregate_root(self, **kwargs):
        """Create an aggregate root with events."""
        defaults = {
            "name": f"Order {factory.Faker('uuid4').generate()[:8]}"
        }
        defaults.update(kwargs)

        aggregate = self.flext.Entities.AggregateRoot(**defaults)

        # Add some default events
        aggregate.raise_domain_event("EntityCreated", {
            "entity_id": aggregate.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        return aggregate

# Factory fixtures
@pytest.fixture
def entity_factory():
    """Provide entity factory for tests."""
    return FlextEntityFactory()

@pytest.fixture
def sample_entities(entity_factory):
    """Provide a set of sample entities."""
    return {
        "customer": entity_factory.create_business_entity(
            name="Acme Corporation",
            business_type="Enterprise"
        ),
        "order": entity_factory.create_aggregate_root(
            name="Order #12345"
        ),
        "user": entity_factory.create_base_entity(
            name="John Doe"
        )
    }
```

## 📊 Test Coverage and Reporting

### Coverage Configuration

```python
# pyproject.toml
[tool.coverage.run]
source = ["src/flext"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/migrations/*",
    "*/venv/*",
    "*/.venv/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "@abstract",
    "@abstractmethod"
]
show_missing = true
skip_covered = false
precision = 2

[tool.coverage.html]
directory = "reports/coverage/html"

[tool.coverage.json]
output = "reports/coverage/coverage.json"
```

### Running Tests with Coverage

```bash
# Run all tests with coverage
pytest --cov=src/flext --cov-report=html --cov-report=term-missing

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m "e2e and not slow"     # E2E tests excluding slow ones

# Run tests in parallel
pytest -n auto                   # Auto-detect CPU cores
pytest -n 4                      # Use 4 workers

# Generate coverage reports
pytest --cov=src/flext --cov-report=html --cov-report=json --cov-report=term

# Performance testing
pytest -m performance --tb=short -v
```

## 🚀 Testing Best Practices

### Test Organization

1. **Follow AAA Pattern**: Arrange, Act, Assert in all tests
2. **One Assertion Per Test**: Focus each test on a single behavior
3. **Descriptive Names**: Test names should describe what is being tested
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Unit Tests**: Unit tests should complete in milliseconds

### Test Data Management

1. **Use Factories**: Generate consistent test data with factories
2. **Avoid Hardcoded Values**: Use parameterized tests for multiple scenarios
3. **Clean Setup/Teardown**: Ensure tests clean up after themselves
4. **Isolated Data**: Each test should use its own data

### Mocking Guidelines

1. **Mock External Dependencies**: Mock databases, HTTP services, file systems
2. **Don't Mock Domain Logic**: Test business logic without mocks
3. **Verify Interactions**: Use mocks to verify adapter calls
4. **Mock at Boundaries**: Mock at architecture boundaries (ports)

### Performance Testing

1. **Set Performance Budgets**: Define acceptable performance thresholds
2. **Test Under Load**: Simulate realistic load conditions
3. **Monitor Resource Usage**: Track memory and CPU usage
4. **Benchmark Regularly**: Run performance tests in CI/CD

## 🔧 Testing Utilities

### Custom Assertions

```python
# tests/assertions.py
def assert_valid_entity(entity):
    """Assert that an entity is valid."""
    assert entity is not None
    assert entity.id is not None
    assert entity.name is not None
    assert entity.created_at is not None
    assert entity.is_valid()

def assert_domain_event(event, expected_type, expected_aggregate_id=None):
    """Assert domain event properties."""
    assert event.event_type == expected_type
    assert event.event_id is not None
    assert event.occurred_at is not None

    if expected_aggregate_id:
        assert event.aggregate_id == expected_aggregate_id

def assert_adapter_health(health_result):
    """Assert adapter health check result."""
    assert "status" in health_result
    assert health_result["status"] in ["healthy", "unhealthy", "degraded"]

    if health_result["status"] == "healthy":
        assert "error" not in health_result or health_result["error"] is None
```

### Test Utilities

```python
# tests/utils.py
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

@asynccontextmanager
async def temporary_adapter(adapter_class, config: dict) -> AsyncGenerator:
    """Context manager for temporary adapter setup."""
    adapter = adapter_class()
    adapter.configure(config)

    try:
        await adapter.connect()
        yield adapter
    finally:
        await adapter.disconnect()

async def wait_for_condition(condition_func, timeout: float = 5.0):
    """Wait for a condition to become true."""
    start_time = asyncio.get_event_loop().time()

    while True:
        if condition_func():
            return True

        if asyncio.get_event_loop().time() - start_time > timeout:
            return False

        await asyncio.sleep(0.1)
```

## 📋 Testing Checklist

### Before Committing Code

- [ ] **All tests pass**: `pytest` runs without failures
- [ ] **Coverage threshold met**: >90% test coverage achieved
- [ ] **No flaky tests**: Tests are deterministic and reliable
- [ ] **Performance tests pass**: No performance regressions
- [ ] **Integration tests work**: Components integrate correctly
- [ ] **Documentation updated**: Test documentation reflects changes

### Test Quality Review

- [ ] **Clear test names**: Test names describe behavior being tested
- [ ] **Proper assertions**: Each test has meaningful assertions
- [ ] **Good coverage**: All important code paths are tested
- [ ] **Fast execution**: Unit tests complete quickly
- [ ] **Independent**: Tests don't depend on each other
- [ ] **Clean setup**: Tests properly initialize and clean up

---

**🧪 Ready to build reliable FLEXT applications with comprehensive testing!**
