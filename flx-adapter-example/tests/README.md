# 🧪 FLX Adapter Example - Test Suite

> **Module**: Comprehensive test suite for FLX adapter example with unit, integration, and performance testing | **Audience**: QA Engineers, Developers, Test Automation Engineers | **Status**: Production Ready

## 📋 **Overview**

Complete testing framework for the FLX Adapter Example project, demonstrating enterprise testing patterns including unit tests, integration tests, performance testing, and end-to-end validation. This test suite serves as a reference implementation for testing FLX framework components.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Adapter Example](../README.md) → **📂 Current**: Test Suite

---

## 🎯 **Module Purpose**

This test module provides comprehensive testing coverage for the FLX Adapter Example, demonstrating best practices for testing hexagonal architecture components, domain logic validation, infrastructure integration, and performance characteristics in enterprise environments.

### **Key Testing Areas**

- **Unit Testing** - Domain logic and business rule validation
- **Integration Testing** - Component interaction and data flow validation
- **Performance Testing** - Load testing and performance benchmarking
- **Contract Testing** - API contract validation and compatibility
- **End-to-End Testing** - Complete workflow validation
- **Security Testing** - Authentication and authorization validation

---

## 📁 **Test Structure**

```
tests/
├── unit/
│   ├── test_domain_models.py        # Domain entity and value object tests
│   ├── test_application_services.py # Application service unit tests
│   ├── test_business_logic.py       # Business rule validation tests
│   └── test_value_objects.py        # Value object validation tests
├── integration/
│   ├── test_adapter_integration.py  # Adapter integration tests
│   ├── test_database_integration.py # Database interaction tests
│   ├── test_api_integration.py      # API endpoint integration tests
│   └── test_external_services.py    # External service integration tests
├── performance/
│   ├── test_load_performance.py     # Load testing scenarios
│   ├── test_stress_testing.py       # Stress testing validation
│   ├── test_memory_usage.py         # Memory usage profiling
│   └── test_response_times.py       # Response time benchmarking
├── e2e/
│   ├── test_complete_workflows.py   # End-to-end workflow tests
│   ├── test_user_journeys.py        # User journey validation
│   └── test_system_integration.py   # System integration validation
├── contract/
│   ├── test_api_contracts.py        # API contract testing
│   ├── test_database_contracts.py   # Database contract validation
│   └── test_event_contracts.py      # Event contract testing
├── security/
│   ├── test_authentication.py       # Authentication testing
│   ├── test_authorization.py        # Authorization validation
│   └── test_input_validation.py     # Input validation security tests
├── fixtures/
│   ├── database_fixtures.py         # Database test data fixtures
│   ├── api_fixtures.py              # API test data fixtures
│   └── domain_fixtures.py           # Domain object test fixtures
├── conftest.py                      # Pytest configuration and shared fixtures
└── pytest.ini                       # Pytest configuration settings
```

---

## 🔧 **Test Categories**

### **1. Unit Tests (unit/)**

#### **Domain Model Testing (test_domain_models.py)**

```python
"""Unit tests for domain models and business logic."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from flx_adapter_example.domain.models import Customer, Order, Product
from flx_adapter_example.domain.value_objects import Email, Money, ProductId
from flx_adapter_example.domain.exceptions import (
    InvalidEmailError,
    InsufficientFundsError,
    OrderNotModifiableError
)

class TestCustomerDomain:
    """Test customer domain entity business logic."""

    def test_customer_creation_with_valid_data(self):
        """Test customer creation with valid data."""
        # Arrange
        email = Email("john.doe@example.com")
        name = "John Doe"

        # Act
        customer = Customer.create(email=email, name=name)

        # Assert
        assert customer.email == email
        assert customer.name == name
        assert customer.status == CustomerStatus.ACTIVE
        assert customer.created_at is not None
        assert len(customer.domain_events) == 1
        assert isinstance(customer.domain_events[0], CustomerCreatedEvent)

    def test_customer_email_change_generates_event(self):
        """Test that changing customer email generates domain event."""
        # Arrange
        customer = CustomerTestBuilder().build()
        new_email = Email("newemail@example.com")

        # Act
        customer.change_email(new_email)

        # Assert
        assert customer.email == new_email
        assert len(customer.domain_events) == 1
        assert isinstance(customer.domain_events[0], CustomerEmailChangedEvent)

    def test_customer_deactivation_prevents_modifications(self):
        """Test that deactivated customers cannot be modified."""
        # Arrange
        customer = CustomerTestBuilder().build()
        customer.deactivate()

        # Act & Assert
        with pytest.raises(CustomerNotActiveError):
            customer.change_email(Email("new@example.com"))

class TestOrderDomain:
    """Test order domain entity business logic."""

    def test_order_creation_with_valid_data(self):
        """Test order creation with valid customer."""
        # Arrange
        customer = CustomerTestBuilder().build()

        # Act
        order = Order.create(customer_id=customer.id)

        # Assert
        assert order.customer_id == customer.id
        assert order.status == OrderStatus.DRAFT
        assert order.total_amount == Money(Decimal('0.00'), 'USD')
        assert len(order.items) == 0

    def test_add_item_to_draft_order(self):
        """Test adding item to draft order."""
        # Arrange
        order = OrderTestBuilder().with_status(OrderStatus.DRAFT).build()
        product = ProductTestBuilder().build()
        quantity = 2

        # Act
        order.add_item(product.id, quantity, product.price)

        # Assert
        assert len(order.items) == 1
        assert order.items[0].product_id == product.id
        assert order.items[0].quantity == quantity
        assert order.total_amount == Money(product.price.amount * quantity, 'USD')

    def test_cannot_add_item_to_confirmed_order(self):
        """Test that items cannot be added to confirmed orders."""
        # Arrange
        order = OrderTestBuilder().with_status(OrderStatus.CONFIRMED).build()
        product = ProductTestBuilder().build()

        # Act & Assert
        with pytest.raises(OrderNotModifiableError):
            order.add_item(product.id, 1, product.price)

    def test_order_confirmation_validates_minimum_amount(self):
        """Test order confirmation validates minimum amount."""
        # Arrange
        order = OrderTestBuilder().with_empty_items().build()

        # Act & Assert
        with pytest.raises(EmptyOrderError):
            order.confirm()

class TestValueObjects:
    """Test value object validation and behavior."""

    def test_email_validation_with_valid_email(self):
        """Test email value object with valid email."""
        # Act
        email = Email("valid@example.com")

        # Assert
        assert email.value == "valid@example.com"

    def test_email_validation_with_invalid_email(self):
        """Test email value object with invalid email."""
        # Act & Assert
        with pytest.raises(InvalidEmailError):
            Email("invalid-email")

    def test_money_addition_with_same_currency(self):
        """Test money addition with same currency."""
        # Arrange
        money1 = Money(Decimal('10.00'), 'USD')
        money2 = Money(Decimal('20.00'), 'USD')

        # Act
        result = money1 + money2

        # Assert
        assert result.amount == Decimal('30.00')
        assert result.currency == 'USD'

    def test_money_addition_with_different_currency_fails(self):
        """Test money addition fails with different currencies."""
        # Arrange
        money1 = Money(Decimal('10.00'), 'USD')
        money2 = Money(Decimal('20.00'), 'EUR')

        # Act & Assert
        with pytest.raises(CurrencyMismatchError):
            money1 + money2
```

#### **Application Service Testing (test_application_services.py)**

```python
"""Unit tests for application services."""

import pytest
from unittest.mock import Mock, AsyncMock

from flx_adapter_example.application.services import CustomerApplicationService
from flx_adapter_example.domain.repositories import CustomerRepository
from flx_adapter_example.infrastructure.events import EventBus

class TestCustomerApplicationService:
    """Test customer application service use cases."""

    @pytest.fixture
    def mock_customer_repository(self):
        """Mock customer repository."""
        return Mock(spec=CustomerRepository)

    @pytest.fixture
    def mock_event_bus(self):
        """Mock event bus."""
        return Mock(spec=EventBus)

    @pytest.fixture
    def customer_service(self, mock_customer_repository, mock_event_bus):
        """Customer application service with mocked dependencies."""
        return CustomerApplicationService(
            customer_repository=mock_customer_repository,
            event_bus=mock_event_bus
        )

    @pytest.mark.asyncio
    async def test_create_customer_success(
        self,
        customer_service,
        mock_customer_repository,
        mock_event_bus
    ):
        """Test successful customer creation."""
        # Arrange
        customer_data = CustomerCreationData(
            email="john@example.com",
            name="John Doe"
        )
        mock_customer_repository.save = AsyncMock()
        mock_event_bus.publish = AsyncMock()

        # Act
        customer = await customer_service.create_customer(customer_data)

        # Assert
        assert customer.email.value == "john@example.com"
        assert customer.name == "John Doe"
        mock_customer_repository.save.assert_called_once_with(customer)
        mock_event_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_customer_with_duplicate_email_fails(
        self,
        customer_service,
        mock_customer_repository
    ):
        """Test customer creation fails with duplicate email."""
        # Arrange
        existing_customer = CustomerTestBuilder().build()
        mock_customer_repository.get_by_email = AsyncMock(return_value=existing_customer)

        customer_data = CustomerCreationData(
            email=existing_customer.email.value,
            name="Different Name"
        )

        # Act & Assert
        with pytest.raises(DuplicateEmailError):
            await customer_service.create_customer(customer_data)

    @pytest.mark.asyncio
    async def test_update_customer_email_success(
        self,
        customer_service,
        mock_customer_repository,
        mock_event_bus
    ):
        """Test successful customer email update."""
        # Arrange
        customer = CustomerTestBuilder().build()
        new_email = "newemail@example.com"

        mock_customer_repository.get_by_id = AsyncMock(return_value=customer)
        mock_customer_repository.save = AsyncMock()
        mock_event_bus.publish = AsyncMock()

        # Act
        await customer_service.update_customer_email(customer.id, new_email)

        # Assert
        assert customer.email.value == new_email
        mock_customer_repository.save.assert_called_once_with(customer)
        mock_event_bus.publish.assert_called_once()
```

### **2. Integration Tests (integration/)**

#### **Database Integration Testing (test_database_integration.py)**

```python
"""Integration tests for database operations."""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from flx_adapter_example.infrastructure.database import DatabaseAdapter
from flx_adapter_example.infrastructure.repositories import SqlAlchemyCustomerRepository

@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration with real database."""

    @pytest.fixture
    async def database_session(self):
        """Create test database session."""
        engine = create_async_engine(
            "postgresql+asyncpg://test:test@localhost:5432/test_db",
            echo=True
        )

        async_session = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session() as session:
            yield session
            await session.rollback()

    @pytest.fixture
    def customer_repository(self, database_session):
        """Customer repository with real database session."""
        return SqlAlchemyCustomerRepository(database_session)

    @pytest.mark.asyncio
    async def test_customer_save_and_retrieve(self, customer_repository):
        """Test customer save and retrieval from database."""
        # Arrange
        customer = CustomerTestBuilder().build()

        # Act
        await customer_repository.save(customer)
        retrieved_customer = await customer_repository.get_by_id(customer.id)

        # Assert
        assert retrieved_customer is not None
        assert retrieved_customer.id == customer.id
        assert retrieved_customer.email == customer.email
        assert retrieved_customer.name == customer.name

    @pytest.mark.asyncio
    async def test_customer_update_persistence(self, customer_repository):
        """Test customer updates are persisted correctly."""
        # Arrange
        customer = CustomerTestBuilder().build()
        await customer_repository.save(customer)

        # Act
        new_email = Email("updated@example.com")
        customer.change_email(new_email)
        await customer_repository.save(customer)

        # Retrieve and verify
        updated_customer = await customer_repository.get_by_id(customer.id)

        # Assert
        assert updated_customer.email == new_email

    @pytest.mark.asyncio
    async def test_customer_query_by_email(self, customer_repository):
        """Test querying customers by email."""
        # Arrange
        customer = CustomerTestBuilder().with_email("unique@example.com").build()
        await customer_repository.save(customer)

        # Act
        found_customer = await customer_repository.get_by_email(customer.email)

        # Assert
        assert found_customer is not None
        assert found_customer.id == customer.id

    @pytest.mark.asyncio
    async def test_database_transaction_rollback(self, database_session, customer_repository):
        """Test database transaction rollback functionality."""
        # Arrange
        customer = CustomerTestBuilder().build()

        # Act
        try:
            await customer_repository.save(customer)
            # Simulate error
            raise Exception("Simulated error")
        except Exception:
            await database_session.rollback()

        # Assert
        retrieved_customer = await customer_repository.get_by_id(customer.id)
        assert retrieved_customer is None
```

### **3. Performance Tests (performance/)**

#### **Load Performance Testing (test_load_performance.py)**

```python
"""Performance tests for load testing scenarios."""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median

@pytest.mark.performance
class TestLoadPerformance:
    """Performance tests for concurrent load scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_customer_creation_performance(self, customer_service):
        """Test performance of concurrent customer creation."""
        # Arrange
        concurrent_requests = 100
        customer_data_list = [
            CustomerCreationData(
                email=f"user{i}@example.com",
                name=f"User {i}"
            )
            for i in range(concurrent_requests)
        ]

        # Act
        start_time = time.time()
        tasks = [
            customer_service.create_customer(data)
            for data in customer_data_list
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Assert
        total_time = end_time - start_time
        successful_requests = sum(1 for r in results if not isinstance(r, Exception))
        requests_per_second = successful_requests / total_time

        assert successful_requests >= concurrent_requests * 0.95  # 95% success rate
        assert requests_per_second >= 50  # At least 50 requests per second
        assert total_time <= 5.0  # Complete within 5 seconds

    @pytest.mark.asyncio
    async def test_database_connection_pool_performance(self, database_adapter):
        """Test database connection pool performance under load."""
        # Arrange
        concurrent_connections = 50
        queries_per_connection = 10

        async def execute_queries():
            """Execute multiple queries on single connection."""
            query_times = []
            for _ in range(queries_per_connection):
                start = time.time()
                await database_adapter.execute_query("SELECT 1")
                end = time.time()
                query_times.append(end - start)
            return query_times

        # Act
        start_time = time.time()
        tasks = [execute_queries() for _ in range(concurrent_connections)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Flatten results
        all_query_times = [time for result in results for time in result]

        # Assert
        total_queries = concurrent_connections * queries_per_connection
        total_time = end_time - start_time
        queries_per_second = total_queries / total_time

        avg_query_time = mean(all_query_times)
        median_query_time = median(all_query_times)

        assert queries_per_second >= 100  # At least 100 queries per second
        assert avg_query_time <= 0.1  # Average query time <= 100ms
        assert median_query_time <= 0.05  # Median query time <= 50ms

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, customer_service):
        """Test memory usage during high load scenarios."""
        import psutil
        import os

        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Act - Create many customers
        tasks = []
        for i in range(1000):
            customer_data = CustomerCreationData(
                email=f"memtest{i}@example.com",
                name=f"Memory Test User {i}"
            )
            tasks.append(customer_service.create_customer(customer_data))

        await asyncio.gather(*tasks)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Assert
        assert memory_increase <= 100  # Memory increase should be <= 100MB

        # Cleanup and verify memory is released
        import gc
        gc.collect()

        cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_released = final_memory - cleanup_memory

        assert memory_released >= memory_increase * 0.8  # At least 80% memory released
```

### **4. End-to-End Tests (e2e/)**

#### **Complete Workflow Testing (test_complete_workflows.py)**

```python
"""End-to-end tests for complete business workflows."""

import pytest
from httpx import AsyncClient

@pytest.mark.e2e
class TestCompleteWorkflows:
    """Test complete business workflows end-to-end."""

    @pytest.mark.asyncio
    async def test_complete_customer_order_workflow(self, api_client: AsyncClient):
        """Test complete customer and order workflow through API."""

        # 1. Create customer
        customer_response = await api_client.post("/api/customers", json={
            "email": "workflow@example.com",
            "name": "Workflow Test Customer"
        })
        assert customer_response.status_code == 201
        customer_id = customer_response.json()["customer_id"]

        # 2. Verify customer creation
        customer_details = await api_client.get(f"/api/customers/{customer_id}")
        assert customer_details.status_code == 200
        assert customer_details.json()["email"] == "workflow@example.com"

        # 3. Create product
        product_response = await api_client.post("/api/products", json={
            "name": "Test Product",
            "description": "Test product for workflow",
            "price": 99.99,
            "currency": "USD"
        })
        assert product_response.status_code == 201
        product_id = product_response.json()["product_id"]

        # 4. Create order
        order_response = await api_client.post("/api/orders", json={
            "customer_id": customer_id
        })
        assert order_response.status_code == 201
        order_id = order_response.json()["order_id"]

        # 5. Add item to order
        add_item_response = await api_client.post(
            f"/api/orders/{order_id}/items",
            json={
                "product_id": product_id,
                "quantity": 2
            }
        )
        assert add_item_response.status_code == 201

        # 6. Verify order total
        order_details = await api_client.get(f"/api/orders/{order_id}")
        assert order_details.status_code == 200
        assert order_details.json()["total_amount"] == 199.98
        assert len(order_details.json()["items"]) == 1

        # 7. Confirm order
        confirm_response = await api_client.post(f"/api/orders/{order_id}/confirm")
        assert confirm_response.status_code == 200

        # 8. Verify order status
        final_order = await api_client.get(f"/api/orders/{order_id}")
        assert final_order.status_code == 200
        assert final_order.json()["status"] == "CONFIRMED"

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, api_client: AsyncClient):
        """Test error handling in complete workflow."""

        # 1. Try to create customer with invalid email
        invalid_customer = await api_client.post("/api/customers", json={
            "email": "invalid-email",
            "name": "Invalid Customer"
        })
        assert invalid_customer.status_code == 400
        assert "Invalid email" in invalid_customer.json()["detail"]

        # 2. Try to access non-existent customer
        missing_customer = await api_client.get("/api/customers/non-existent-id")
        assert missing_customer.status_code == 404

        # 3. Create valid customer for next tests
        customer_response = await api_client.post("/api/customers", json={
            "email": "error@example.com",
            "name": "Error Test Customer"
        })
        customer_id = customer_response.json()["customer_id"]

        # 4. Try to create duplicate customer
        duplicate_customer = await api_client.post("/api/customers", json={
            "email": "error@example.com",
            "name": "Duplicate Customer"
        })
        assert duplicate_customer.status_code == 409
        assert "already exists" in duplicate_customer.json()["detail"]
```

---

## 🔧 **Test Configuration**

### **Pytest Configuration (conftest.py)**

```python
"""Pytest configuration and shared fixtures."""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from flx_adapter_example.main import create_app
from flx_adapter_example.infrastructure.database import get_database_session

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_database():
    """Create test database session."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_db",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def api_client(test_database):
    """Create test API client."""
    app = create_app()

    # Override database dependency
    app.dependency_overrides[get_database_session] = lambda: test_database

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def customer_service(test_database):
    """Create customer service with test dependencies."""
    repository = SqlAlchemyCustomerRepository(test_database)
    event_bus = InMemoryEventBus()
    return CustomerApplicationService(repository, event_bus)
```

### **Test Settings (pytest.ini)**

```ini
[tool:pytest]
minversion = 6.0
addopts =
    -ra
    --strict-markers
    --strict-config
    --cov=flx_adapter_example
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=90
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow running tests
    security: Security tests
asyncio_mode = auto
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete FLX Adapter Example documentation
- [Source Implementation](../src/README.md) - Source code structure and patterns
- [Scripts](../scripts/README.md) - Development and testing scripts

### **Testing Documentation**

- [Testing Guide](../../docs/development/testing-guide.md) - Testing strategies and patterns
- [Performance Testing](../../docs/testing/performance-testing.md) - Performance testing best practices
- [Security Testing](../../docs/testing/security-testing.md) - Security testing guidelines

### **External Testing Tools**

- [Pytest Documentation](https://docs.pytest.org/) - Python testing framework
- [AsyncIO Testing](https://docs.python.org/3/library/asyncio-dev.html) - Async testing patterns
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html) - Database testing

---

**📂 Module**: Test Suite | **🏠 Component**: [FLX Adapter Example](../README.md) | **Framework**: PyTest 7.0+ | **Updated**: 2025-06-19
