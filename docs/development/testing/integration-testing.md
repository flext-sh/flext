# Integration Testing Guide

## Overview

Integration testing in the FLX framework validates component interactions and ensures that different layers of the hexagonal architecture work together correctly while maintaining clear boundaries and contracts.

## Integration Testing Strategy

### Testing Scope

- **Adapter-Port Integration**: Verify adapters correctly implement port contracts
- **Cross-Layer Communication**: Test communication between application and domain layers
- **External System Integration**: Validate integration with real external services
- **Workflow Testing**: Test complete business workflows across multiple components

### Test Categories

#### 1. Port-Adapter Contract Testing

```python
from flx.testing.contracts import PortContractTest
from flx.ports.outbound import UserRepositoryPort
from flx.adapters.outbound import PostgreSQLUserRepository

class TestUserRepositoryContract(PortContractTest):
    """Verify that PostgreSQL adapter conforms to UserRepository port contract."""
    
    port_interface = UserRepositoryPort
    
    @pytest.fixture
    async def adapter(self):
        # Setup test database
        adapter = PostgreSQLUserRepository(test_db_config)
        await adapter.connect()
        yield adapter
        await adapter.disconnect()

    async def test_save_user_contract(self, adapter):
        """Test save operation according to port contract."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "status": "active"
        }
        
        # Port contract: save should return user with generated ID
        saved_user = await adapter.save(user_data)
        
        assert saved_user.id is not None
        assert saved_user.name == "Test User"
        assert saved_user.email == "test@example.com"

    async def test_find_user_contract(self, adapter):
        """Test find operation according to port contract."""
        # Setup: Save a user first
        user = await adapter.save({"name": "Find Me", "email": "findme@example.com"})
        
        # Port contract: find should return exact same user
        found_user = await adapter.find_by_id(user.id)
        
        assert found_user.id == user.id
        assert found_user.name == user.name
        assert found_user.email == user.email
        
        # Port contract: find with invalid ID should return None
        not_found = await adapter.find_by_id("invalid-id")
        assert not_found is None
```

#### 2. Application-Domain Integration

```python
from flx.application.services import OrderApplicationService
from flx.domain.services import PricingService
from flx.testing.fixtures import test_database, test_repositories

class TestOrderApplicationIntegration:
    @pytest.fixture
    async def service_setup(self, test_database):
        # Real repositories with test database
        order_repo = OrderRepository(test_database)
        product_repo = ProductRepository(test_database)
        
        # Real domain services
        pricing_service = PricingService()
        
        # Application service with real dependencies
        app_service = OrderApplicationService(
            order_repo=order_repo,
            product_repo=product_repo,
            pricing_service=pricing_service
        )
        
        return app_service, order_repo, product_repo

    async def test_create_order_with_pricing_calculation(self, service_setup):
        """Test complete order creation workflow with real pricing calculation."""
        app_service, order_repo, product_repo = service_setup
        
        # Setup test data
        product = await product_repo.save({
            "name": "Test Product",
            "base_price": 100.00,
            "category": "electronics"
        })
        
        # Execute order creation
        order_request = {
            "customer_id": "cust-123",
            "items": [
                {"product_id": product.id, "quantity": 2}
            ],
            "discount_code": "SAVE10"
        }
        
        result = await app_service.create_order(order_request)
        
        # Verify complete workflow
        assert result.success is True
        
        saved_order = await order_repo.find_by_id(result.order_id)
        assert saved_order is not None
        assert saved_order.total_amount == 180.00  # 2 * 100 - 10% discount
        assert len(saved_order.items) == 1
        assert saved_order.items[0].product_id == product.id
```

#### 3. External Service Integration

```python
from flx.adapters.outbound import EmailServiceAdapter
from flx.testing.external import ExternalServiceTest

class TestEmailServiceIntegration(ExternalServiceTest):
    """Integration tests with real email service (using test environment)."""
    
    @pytest.fixture
    async def email_adapter(self):
        # Use test email service configuration
        adapter = EmailServiceAdapter(
            api_url=settings.TEST_EMAIL_API_URL,
            api_key=settings.TEST_EMAIL_API_KEY
        )
        await adapter.connect()
        yield adapter
        await adapter.disconnect()

    @pytest.mark.integration
    @pytest.mark.external_service
    async def test_send_email_to_real_service(self, email_adapter):
        """Test email sending with real external service."""
        email_data = {
            "to": "test@example.com",
            "subject": "Integration Test Email",
            "body": "This is a test email from integration tests",
            "template": "test_template"
        }
        
        result = await email_adapter.send_email(email_data)
        
        assert result.success is True
        assert result.message_id is not None
        
        # Verify with external service if possible
        status = await email_adapter.get_delivery_status(result.message_id)
        assert status in ["sent", "delivered", "queued"]
```

#### 4. Database Integration Testing

```python
from flx.infra.database import DatabaseConnectionManager
from flx.adapters.outbound import OrderRepository
from flx.testing.database import DatabaseIntegrationTest

class TestDatabaseIntegration(DatabaseIntegrationTest):
    """Test database operations with real database transactions."""
    
    @pytest.fixture
    async def db_setup(self):
        # Setup test database with transaction isolation
        db_manager = DatabaseConnectionManager(test_config)
        await db_manager.connect()
        
        # Start transaction for test isolation
        transaction = await db_manager.begin_transaction()
        
        repository = OrderRepository(db_manager)
        
        yield repository, db_manager
        
        # Rollback transaction after test
        await transaction.rollback()
        await db_manager.disconnect()

    async def test_repository_transaction_isolation(self, db_setup):
        """Test that repository operations work correctly within transactions."""
        repository, db_manager = db_setup
        
        # Create order within transaction
        order_data = {
            "customer_id": "cust-123",
            "status": "pending",
            "items": [
                {"product_id": "prod-456", "quantity": 1, "price": 50.00}
            ]
        }
        
        order = await repository.save(order_data)
        assert order.id is not None
        
        # Verify order exists within transaction
        found_order = await repository.find_by_id(order.id)
        assert found_order is not None
        assert found_order.customer_id == "cust-123"
        
        # Test transaction rollback (handled by fixture)
        # Order should not exist after transaction rollback
```

## Testing Infrastructure Services

### Message Queue Integration

```python
from flx.infra.messaging import MessageBroker
from flx.testing.messaging import MessageBrokerTest

class TestMessageBrokerIntegration(MessageBrokerTest):
    @pytest.fixture
    async def message_broker(self):
        broker = MessageBroker(
            broker_url=settings.TEST_REDIS_URL,
            queue_prefix="test_"
        )
        await broker.connect()
        yield broker
        await broker.cleanup_test_queues()
        await broker.disconnect()

    async def test_message_publishing_and_consumption(self, message_broker):
        """Test complete message flow through broker."""
        message_data = {
            "event_type": "order_created",
            "order_id": "ord-123",
            "timestamp": "2024-01-01T10:00:00Z"
        }
        
        # Publish message
        await message_broker.publish("order_events", message_data)
        
        # Consume message
        received_messages = []
        
        async def message_handler(message):
            received_messages.append(message)
        
        await message_broker.subscribe("order_events", message_handler)
        
        # Wait for message processing
        await asyncio.sleep(0.1)
        
        assert len(received_messages) == 1
        assert received_messages[0]["order_id"] == "ord-123"
```

## Test Environment Configuration

### Database Configuration

```python
# tests/conftest.py
@pytest.fixture(scope="session")
async def test_database():
    """Setup isolated test database for integration tests."""
    test_db_name = f"test_flx_{uuid.uuid4().hex[:8]}"
    
    # Create test database
    admin_conn = await create_admin_connection()
    await admin_conn.execute(f"CREATE DATABASE {test_db_name}")
    
    # Configure test database connection
    test_config = DatabaseConfig(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=test_db_name,
        username=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    
    # Run migrations
    await run_migrations(test_config)
    
    yield test_config
    
    # Cleanup: Drop test database
    await admin_conn.execute(f"DROP DATABASE {test_db_name}")
    await admin_conn.close()
```

### External Service Mocking

```python
from flx.testing.external import ExternalServiceMockServer

@pytest.fixture(scope="session")
async def mock_payment_service():
    """Mock external payment service for integration tests."""
    mock_server = ExternalServiceMockServer(port=8888)
    
    # Configure mock responses
    mock_server.add_endpoint(
        "POST", "/api/payments",
        response={"payment_id": "pay-123", "status": "approved"},
        status_code=200
    )
    
    await mock_server.start()
    yield mock_server
    await mock_server.stop()
```

## Test Execution and CI/CD

### Pytest Configuration

```ini
# pytest.ini
[tool:pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, with dependencies)
    external: Tests requiring external services
    database: Tests requiring database
    slow: Slow-running tests

addopts =
    --strict-markers
    --cov=src/flx
    --cov-report=html
    --cov-report=term-missing
    -v
```

### Test Execution Strategies

```bash
# Run only fast tests during development
pytest -m "not slow and not external"

# Run integration tests
pytest -m integration

# Run all tests including external services
pytest -m "not slow" --external-services

# Run with coverage
pytest --cov=src/flx --cov-report=html
```

## Best Practices

### Test Data Management

1. **Isolated Test Data**: Each test creates and cleans up its own data
2. **Realistic Scenarios**: Use production-like data volumes and complexity
3. **Test Factories**: Create reusable factories for complex test data
4. **Database Transactions**: Use transaction rollback for database test isolation

### Performance Considerations

1. **Test Database**: Use separate test database with faster configuration
2. **Parallel Execution**: Run integration tests in parallel when possible
3. **Selective Testing**: Use markers to run subsets of tests during development
4. **Resource Cleanup**: Ensure all resources are properly cleaned up

### Error Handling

1. **Failure Scenarios**: Test error conditions and recovery mechanisms
2. **Timeout Handling**: Test behavior under timeout conditions
3. **Resource Exhaustion**: Test behavior when resources are unavailable
4. **Network Failures**: Test resilience to network issues

## Related Documentation

- [Testing Overview](overview.md) - Testing strategy and philosophy
- [Unit Testing](unit-testing.md) - Unit testing patterns
- [E2E Testing](e2e-testing.md) - End-to-end testing scenarios

---

*This guide provides comprehensive patterns for integration testing in the FLX framework, ensuring robust component interactions while maintaining architectural boundaries.*
