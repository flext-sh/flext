# Unit Testing Guide

## Overview

Unit testing in the FLX framework focuses on testing individual components in isolation, following hexagonal architecture principles where domain logic is completely separated from infrastructure concerns.

## Unit Testing Principles

### Core Guidelines

- **Fast Execution**: Tests should run in milliseconds, not seconds
- **Complete Isolation**: No external dependencies (databases, APIs, file systems)
- **Deterministic**: Same input always produces same output
- **Single Responsibility**: Each test validates one specific behavior
- **Clear Intent**: Test names describe the scenario and expected outcome

### Domain Layer Testing

#### Testing Entities and Value Objects

```python
from flext.core.entities import Customer
from flext.core.domain.value_objects import Email, Money
import pytest

class TestCustomer:
    def test_create_customer_with_valid_data(self):
        # Arrange
        email = Email("customer@example.com")

        # Act
        customer = Customer(name="Test Customer", email=email)

        # Assert
        assert customer.name == "Test Customer"
        assert customer.email.value == "customer@example.com"
        assert customer.is_active is True

    def test_customer_deactivation_raises_domain_event(self):
        # Arrange
        customer = Customer(name="Test Customer", email=Email("test@example.com"))

        # Act
        customer.deactivate("Business closure")

        # Assert
        assert customer.is_active is False
        events = customer.get_domain_events()
        assert len(events) == 1
        assert events[0].event_type == "CustomerDeactivated"
```

#### Testing Domain Services

```python
from flext.domain.services import PricingService
from flext.testing.fixtures import product_factory, discount_factory

class TestPricingService:
    @pytest.fixture
    def pricing_service(self):
        return PricingService()

    def test_calculate_price_with_volume_discount(self, pricing_service):
        # Arrange
        product = product_factory(base_price=Money(100, "USD"))
        discount = discount_factory(type="volume", threshold=10, rate=0.15)

        # Act
        final_price = pricing_service.calculate_price(
            product=product,
            quantity=15,
            applicable_discounts=[discount]
        )

        # Assert
        assert final_price.amount == 85.00  # 15% discount applied
        assert final_price.currency == "USD"
```

### Application Layer Testing

#### Testing Command Handlers

```python
from flext.application.handlers import CreateOrderHandler
from flext.application.commands import CreateOrderCommand
from flext.testing.mocks import MockOrderRepository, MockEventPublisher

class TestCreateOrderHandler:
    @pytest.fixture
    async def handler_setup(self):
        order_repo = MockOrderRepository()
        event_publisher = MockEventPublisher()
        handler = CreateOrderHandler(order_repo, event_publisher)
        return handler, order_repo, event_publisher

    async def test_create_order_success(self, handler_setup):
        # Arrange
        handler, order_repo, event_publisher = handler_setup
        command = CreateOrderCommand(
            customer_id="cust-123",
            items=[{"product_id": "prod-456", "quantity": 2}]
        )

        # Act
        result = await handler.handle(command)

        # Assert
        assert result.success is True
        assert order_repo.was_called("save")
        assert event_publisher.was_called("publish")

        published_events = event_publisher.get_published_events()
        assert len(published_events) == 1
        assert published_events[0].event_type == "OrderCreated"
```

### Adapter Testing (with Mocks)

#### Testing Outbound Adapters

```python
from flext.adapters.outbound import EmailAdapter
from flext.testing.mocks import MockEmailService

class TestEmailAdapter:
    @pytest.fixture
    def adapter_setup(self):
        email_service = MockEmailService()
        adapter = EmailAdapter(email_service)
        return adapter, email_service

    async def test_send_notification_email(self, adapter_setup):
        # Arrange
        adapter, email_service = adapter_setup
        notification = {
            "to": "customer@example.com",
            "subject": "Order Confirmation",
            "template": "order_confirmation",
            "data": {"order_id": "ord-123"}
        }

        # Act
        result = await adapter.send_notification(notification)

        # Assert
        assert result.success is True
        assert email_service.was_called("send")

        sent_email = email_service.get_last_sent_email()
        assert sent_email["to"] == "customer@example.com"
        assert "ord-123" in sent_email["body"]
```

#### Testing Inbound Adapters

```python
from flext.adapters.inbound import OrderWebhookAdapter
from flext.testing.mocks import MockOrderService

class TestOrderWebhookAdapter:
    @pytest.fixture
    def adapter_setup(self):
        order_service = MockOrderService()
        adapter = OrderWebhookAdapter(order_service)
        return adapter, order_service

    async def test_process_payment_webhook(self, adapter_setup):
        # Arrange
        adapter, order_service = adapter_setup
        webhook_payload = {
            "event": "payment.completed",
            "order_id": "ord-123",
            "payment_id": "pay-456",
            "amount": 150.00
        }

        # Act
        result = await adapter.process_webhook(webhook_payload)

        # Assert
        assert result.status == "processed"
        assert order_service.was_called("update_payment_status")

        service_call = order_service.get_last_call("update_payment_status")
        assert service_call["order_id"] == "ord-123"
        assert service_call["status"] == "paid"
```

## Testing Utilities and Fixtures

### Factory Pattern for Test Data

```python
# tests/factories.py
import factory
from flext.core.entities import Customer, Product, Order

class CustomerFactory(factory.Factory):
    class Meta:
        model = Customer

    name = factory.Faker("company")
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '')}@example.com")
    is_active = True

class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    name = factory.Faker("word")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    category = factory.Faker("word")
```

### Custom Assertions

```python
# tests/assertions.py
def assert_domain_event_raised(entity, event_type, **expected_data):
    """Assert that a specific domain event was raised by an entity."""
    events = entity.get_domain_events()
    matching_events = [e for e in events if e.event_type == event_type]

    assert len(matching_events) > 0, f"No {event_type} event found"

    if expected_data:
        event = matching_events[0]
        for key, value in expected_data.items():
            assert getattr(event, key) == value, f"Event {key} mismatch"

def assert_repository_interaction(mock_repo, method, times=1, **expected_args):
    """Assert that repository was called with expected parameters."""
    assert mock_repo.call_count(method) == times

    if expected_args:
        last_call = mock_repo.get_last_call(method)
        for key, value in expected_args.items():
            assert last_call[key] == value
```

## Best Practices

### Test Organization

1. **Group by Feature**: Organize tests by business feature, not technical layer
2. **Descriptive Names**: Use clear, behavior-focused test names
3. **Arrange-Act-Assert**: Follow AAA pattern consistently
4. **One Assert per Concept**: Test one logical concept per test method

### Mock Strategy

1. **Mock Dependencies**: Mock all external dependencies at unit level
2. **Verify Interactions**: Assert on important method calls, not just return values
3. **Realistic Data**: Use realistic test data that matches production scenarios
4. **Reset Between Tests**: Ensure mocks are clean for each test

### Performance Guidelines

- Unit tests should run in < 10ms each
- Full unit test suite should complete in < 30 seconds
- Use pytest markers to categorize tests by speed
- Parallel execution for large test suites

## Related Documentation

- [Testing Overview](overview.md) - Testing strategy and philosophy
- [Integration Testing](integration-testing.md) - Integration testing patterns
- [Testing Framework Architecture](../testing-framework.md) - Framework testing infrastructure

---

_This guide provides comprehensive patterns for unit testing in the FLX framework following hexagonal architecture principles._
