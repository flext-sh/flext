# FLX Testing Framework

## Overview

The FLX Testing Framework provides a comprehensive testing infrastructure specifically designed for hexagonal architecture applications. It offers specialized testing engines, adapter mocks, and utilities that understand the unique patterns and requirements of port-adapter architecture.

## Architecture Principles

### Testing Hexagonal Architecture

- **Port Testing**: Test inbound and outbound port contracts independently
- **Adapter Testing**: Test adapter implementations against port interfaces
- **Domain Isolation**: Test domain logic without external dependencies
- **Integration Testing**: Test complete workflows through the hexagon
- **Contract Testing**: Ensure adapters conform to port specifications

### Testing Strategies

- **Unit Testing**: Isolated testing of individual components
- **Integration Testing**: Testing component interactions
- **End-to-End Testing**: Complete workflow testing
- **Contract Testing**: Interface compliance verification
- **Performance Testing**: Load and stress testing

## Directory Structure

```
testing/
├── __init__.py         # Testing framework exports
├── adapters/           # Mock adapters for testing
│   ├── __init__.py
│   ├── analytics.py    # Analytics adapter mocks
│   ├── api.py         # API adapter mocks
│   ├── cache.py       # Cache adapter mocks
│   ├── cli.py         # CLI adapter mocks
│   ├── database.py    # Database adapter mocks
│   ├── events.py      # Event adapter mocks
│   ├── http.py        # HTTP adapter mocks
│   └── logging.py     # Logging adapter mocks
├── engines/            # Testing engines for different components
│   ├── __init__.py
│   ├── base.py        # Base testing engine
│   ├── authentication_engine.py
│   ├── cache_engine.py
│   ├── comprehensive_test_engine.py
│   ├── database_engine.py
│   ├── http_engine.py
│   ├── logging_engine.py
│   ├── messaging_engine.py
│   ├── metrics_engine.py
│   ├── observability_engine.py
│   ├── runtime_engine.py
│   └── test_orchestrator.py
└── README.md          # This documentation
```

## Components

### Testing Engines (`engines/`)

Testing engines provide specialized testing infrastructure for different types of adapters and components. Each engine understands the specific patterns and requirements of its domain.

#### Base Testing Engine (`base.py`)

```python
from flx.testing.engines.base import BaseTestEngine

class MyTestEngine(BaseTestEngine):
    async def setup_test_environment(self):
        # Setup test-specific environment
        pass

    async def cleanup_test_environment(self):
        # Cleanup after tests
        pass
```

#### Database Testing Engine (`database_engine.py`)

**⚠️ Validated Implementation**: Based on actual source code in `/flx/src/flx/testing/engines/database_engine.py`

```python
from flx.testing.engines.database_engine import DatabaseTestEngine

async def test_user_repository():
    # Actual API - no context manager support in current implementation
    engine = DatabaseTestEngine("test_database")
    
    try:
        # Run comprehensive database tests
        metrics = await engine.run_all_tests()
        
        # Access test results
        assert metrics.success_rate > 95.0  # High quality threshold
        assert metrics.failed_tests == 0     # Zero tolerance for failures
        
        # Run specific CRUD tests
        crud_results = await engine.test_crud_operations()
        for result in crud_results:
            assert result.success, f"CRUD test failed: {result.message}"
    
    finally:
        # Cleanup resources
        await engine.cleanup()
```

#### HTTP Testing Engine (`http_engine.py`)

```python
from flx.testing.engines.http_engine import HTTPTestEngine

async def test_api_client():
    async with HTTPTestEngine() as engine:
        # Engine provides mock HTTP server
        engine.mock_response("/users", {"users": [{"id": 1, "name": "Test"}]})

        client = APIClient(base_url=engine.base_url)
        users = await client.get_users()

        assert len(users) == 1
        assert users[0]["name"] == "Test"
```

### Mock Adapters (`adapters/`)

Mock adapters provide test doubles for external systems, allowing isolated testing of business logic without external dependencies.

#### Database Mock (`database.py`)

```python
from flx.testing.adapters.database import MockDatabaseAdapter

async def test_user_service():
    # Setup mock database
    db_mock = MockDatabaseAdapter()
    db_mock.add_mock_data("users", [
        {"id": "1", "email": "test@example.com", "name": "Test User"}
    ])

    # Test service with mock
    service = UserService(database=db_mock)
    user = await service.get_user("1")

    assert user.name == "Test User"
```

#### HTTP Mock (`http.py`)

```python
from flx.testing.adapters.http import MockHTTPAdapter

async def test_external_api_integration():
    # Setup mock HTTP adapter
    http_mock = MockHTTPAdapter()
    http_mock.mock_get("/api/users/1", {
        "id": "1",
        "name": "External User",
        "status": "active"
    })

    # Test service with mock
    service = ExternalUserService(http_client=http_mock)
    user = await service.fetch_user("1")

    assert user.status == "active"
```

## Usage Examples

### Unit Testing Domain Services

```python
import pytest
from flx.testing.adapters import MockDatabaseAdapter, MockEventAdapter

class TestUserService:
    @pytest.fixture
    async def service(self):
        # Setup mocks
        db = MockDatabaseAdapter()
        events = MockEventAdapter()

        # Create service with mocks
        service = UserService(
            user_repository=UserRepository(db),
            event_publisher=EventPublisher(events)
        )

        return service, db, events

    async def test_create_user(self, service):
        service, db, events = service

        # Test user creation
        user_data = {"email": "test@example.com", "name": "Test User"}
        user = await service.create_user(user_data)

        # Verify user was created
        assert user.email == "test@example.com"

        # Verify database interaction
        assert db.was_called("save")

        # Verify event was published
        assert events.was_called("publish")
        published_events = events.get_published_events()
        assert len(published_events) == 1
        assert published_events[0].type == "UserCreated"
```

### Integration Testing with Test Engines

```python
import pytest
from flx.testing.engines import (
    DatabaseTestEngine,
    HTTPTestEngine,
    MessagingTestEngine
)

class TestUserWorkflow:
    @pytest.fixture
    async def test_environment(self):
        # Setup complete test environment
        db_engine = DatabaseTestEngine()
        http_engine = HTTPTestEngine()
        msg_engine = MessagingTestEngine()

        await db_engine.start()
        await http_engine.start()
        await msg_engine.start()

        # Configure application with test engines
        app = Application(
            database=db_engine.get_adapter(),
            http_client=http_engine.get_adapter(),
            message_bus=msg_engine.get_adapter()
        )

        yield app, db_engine, http_engine, msg_engine

        # Cleanup
        await db_engine.stop()
        await http_engine.stop()
        await msg_engine.stop()

    async def test_complete_user_registration_workflow(self, test_environment):
        app, db_engine, http_engine, msg_engine = test_environment

        # Mock external email service
        http_engine.mock_post("/send-email", {"status": "sent"})

        # Execute user registration
        result = await app.register_user({
            "email": "newuser@example.com",
            "name": "New User",
            "password": "securepassword"
        })

        # Verify user was created in database
        users = await db_engine.query("SELECT * FROM users WHERE email = %s",
                                     ("newuser@example.com",))
        assert len(users) == 1
        assert users[0]["name"] == "New User"

        # Verify welcome email was sent
        email_requests = http_engine.get_requests("/send-email")
        assert len(email_requests) == 1
        assert "newuser@example.com" in email_requests[0]["body"]

        # Verify events were published
        events = msg_engine.get_published_messages()
        user_created_events = [e for e in events if e["type"] == "UserCreated"]
        assert len(user_created_events) == 1
```

### Contract Testing for Adapters

```python
import pytest
from flx.testing.contracts import PortContractTest
from flx.ports.outbound.database import UserRepositoryPort

class TestUserRepositoryContract(PortContractTest):
    """Test that database adapters conform to UserRepositoryPort contract."""

    port_interface = UserRepositoryPort

    @pytest.fixture(params=[
        "flx.adapters.outbound.database.PostgreSQLUserRepository",
        "flx.adapters.outbound.database.MySQLUserRepository",
        "flx.adapters.outbound.database.MongoUserRepository"
    ])
    async def adapter(self, request):
        # Create adapter instance for testing
        adapter_class = self.load_class(request.param)
        adapter = adapter_class(test_mode=True)
        await adapter.connect()
        yield adapter
        await adapter.disconnect()

    async def test_create_user_contract(self, adapter):
        """Test that all adapters can create users according to contract."""
        user_data = {
            "email": "contract@example.com",
            "name": "Contract Test User"
        }

        # Contract: create_user should return User with generated ID
        user = await adapter.create_user(user_data)
        assert user.id is not None
        assert user.email == "contract@example.com"
        assert user.name == "Contract Test User"

    async def test_find_user_contract(self, adapter):
        """Test that all adapters can find users according to contract."""
        # Setup: Create a user first
        user = await adapter.create_user({
            "email": "findme@example.com",
            "name": "Find Me"
        })

        # Contract: find_by_id should return the same user
        found_user = await adapter.find_by_id(user.id)
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == user.email

        # Contract: find_by_id with invalid ID should return None
        not_found = await adapter.find_by_id("invalid-id")
        assert not_found is None
```

### Performance Testing

```python
import pytest
import asyncio
import time
from flx.testing.engines import DatabaseTestEngine
from flx.testing.performance import PerformanceTest

class TestUserServicePerformance(PerformanceTest):
    """Performance tests for user service operations."""

    @pytest.fixture
    async def service_setup(self):
        engine = DatabaseTestEngine()
        await engine.start()

        # Pre-populate with test data
        await engine.populate_test_data("users", 10000)

        service = UserService(
            user_repository=UserRepository(engine.get_adapter())
        )

        yield service
        await engine.stop()

    @pytest.mark.performance
    async def test_user_lookup_performance(self, service_setup):
        """Test that user lookup meets performance requirements."""
        service = service_setup

        # Performance requirement: 95% of lookups under 100ms
        async def lookup_operation():
            return await service.get_user("user-5000")

        results = await self.run_performance_test(
            operation=lookup_operation,
            iterations=1000,
            max_concurrent=50
        )

        # Verify performance requirements
        assert results.p95_response_time < 0.1  # 100ms
        assert results.success_rate > 0.99      # 99% success rate
        assert results.throughput > 500         # 500 ops/sec

    @pytest.mark.performance
    async def test_bulk_operations_performance(self, service_setup):
        """Test bulk operations performance."""
        service = service_setup

        # Test creating 1000 users in batches
        start_time = time.time()

        tasks = []
        for i in range(100):  # 100 batches of 10 users each
            batch = [
                {"email": f"bulk{j}@example.com", "name": f"Bulk User {j}"}
                for j in range(i * 10, (i + 1) * 10)
            ]
            tasks.append(service.create_users_batch(batch))

        await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Should create 1000 users in under 5 seconds
        assert total_time < 5.0

        # Verify all users were created
        user_count = await service.get_user_count()
        assert user_count >= 11000  # 10000 initial + 1000 new
```

## Test Configuration

### Test Environment Configuration

```yaml
# tests/config/test_config.yaml
testing:
  mode: "test"

  databases:
    test:
      driver: "sqlite"
      url: ":memory:"
      create_tables: true

    integration:
      driver: "postgresql"
      url: "postgresql://test:test@localhost/test_db"
      cleanup_after_test: true

  http:
    mock_server:
      port: 8888
      record_requests: true

    real_server:
      base_url: "http://localhost:8080"
      timeout: 5.0

  messaging:
    provider: "memory"
    auto_ack: true
    preserve_order: true

  performance:
    enabled: true
    thresholds:
      response_time_p95: 100  # milliseconds
      success_rate: 0.99
      throughput: 500  # operations per second
```

### Pytest Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    contract: Contract tests
    slow: Slow running tests

addopts =
    --strict-markers
    --tb=short
    --cov=src/flx
    --cov-report=html
    --cov-report=term-missing

asyncio_mode = auto

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

## Best Practices

### Test Organization

1. **Separate by Layer**: Organize tests by architectural layer (domain, application, infrastructure)
2. **Use Factories**: Create test data factories for consistent test setup
3. **Isolate Tests**: Each test should be independent and not rely on other tests
4. **Mock External Systems**: Use mocks for external dependencies in unit tests

### Testing Patterns

1. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
2. **Given-When-Then**: Use BDD-style naming for complex scenarios
3. **Test Fixtures**: Use pytest fixtures for reusable test setup
4. **Parameterized Tests**: Test multiple scenarios with parametrized tests

### Performance Testing

1. **Baseline Metrics**: Establish performance baselines for critical operations
2. **Load Testing**: Test under realistic load conditions
3. **Resource Monitoring**: Monitor memory, CPU, and connection usage during tests
4. **Gradual Degradation**: Test behavior under increasing load

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -e .
        pip install -r requirements-test.txt

    - name: Run unit tests
      run: pytest tests/unit -m "not slow"

    - name: Run integration tests
      run: pytest tests/integration
      env:
        DATABASE_URL: postgresql://postgres:test@localhost/test_db

    - name: Run performance tests
      run: pytest tests/performance -m performance
      if: github.ref == 'refs/heads/main'

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Issues

1. **Test Database Conflicts**: Use separate test databases or transactions
2. **Async Test Issues**: Ensure proper async/await usage and event loop management
3. **Mock Configuration**: Verify mocks are properly configured before tests
4. **Resource Cleanup**: Ensure all resources are cleaned up after tests

### Debugging Tests

```python
import pytest
import logging

# Enable debug logging for specific modules
logging.getLogger("flx.adapters").setLevel(logging.DEBUG)
logging.getLogger("flx.testing").setLevel(logging.DEBUG)

@pytest.fixture
def debug_mode():
    """Enable debug mode for detailed test output."""
    import flx.testing
    flx.testing.set_debug_mode(True)
    yield
    flx.testing.set_debug_mode(False)

async def test_with_debugging(debug_mode):
    """Test with debug output enabled."""
    # Test implementation with detailed logging
    pass
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Getting Started Hub](../../getting-started/index.md) - Essential framework installation and setup before testing implementation
- [Architecture Hub](../../architecture/index.md) - Understanding hexagonal architecture patterns for effective testing strategies

### **Next Steps**

- [Development Hub](../index.md) - Comprehensive development tools and standards for implementing tests
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating testing patterns and best practices
- [API Reference Hub](../../api-reference/index.md) - Complete API documentation for components being tested

### **🔗 Related Implementation Topics**

- [**Infrastructure Testing Patterns**](../../infrastructure/operational-excellence.md) - Production infrastructure services and comprehensive testing engines for integration validation
- [**Oracle Testing Examples**](../../guides/oracle/oracle-integration-comprehensive-guide.md) - Real-world Oracle integration testing with practical adapter validation patterns
- [**Security Testing Implementation**](../../security/architecture/security-architecture.md) - Enterprise security testing patterns including authentication validation and authorization testing
- [**Migration Testing Strategies**](../../migration/tools/migration-tools.md) - Framework migration testing and automated validation tools for ensuring compatibility
- [**Performance Testing Optimization**](../../optimization/performance/optimization-guide.md) - Performance testing techniques and benchmark validation for hexagonal architecture components
- [**Deployment Testing Validation**](../../deployment/production-checklist.md) - Production deployment testing checklist and validation procedures

---

**📂 Hub**: [Testing Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
