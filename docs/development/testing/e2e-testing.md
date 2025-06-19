# End-to-End Testing Guide

## Overview

End-to-end (E2E) testing in the FLX framework validates complete business workflows from the user's perspective, ensuring that all system components work together correctly in realistic scenarios.

## E2E Testing Strategy

### Testing Philosophy

- **User-Centric**: Tests simulate real user interactions and business scenarios
- **Complete Workflows**: Test entire business processes from start to finish
- **Production-Like Environment**: Use configuration and data similar to production
- **Minimal but Critical**: Focus on high-value scenarios that cover core business flows
- **External Dependencies**: Test with real external services when possible

### Test Pyramid Position

E2E tests should represent ~5% of your total test suite:

- High value: Test critical business scenarios
- Slow execution: Accept longer run times for comprehensive validation
- Expensive maintenance: Minimize number while maximizing coverage

## E2E Test Categories

### 1. API Endpoint Testing

```python
from flx.testing.e2e import APITestClient
import pytest

class TestOrderAPIWorkflow:
    @pytest.fixture
    async def api_client(self):
        client = APITestClient(base_url="http://localhost:8000")
        await client.authenticate("test_user", "test_password")
        yield client
        await client.close()

    async def test_complete_order_lifecycle(self, api_client):
        """Test complete order workflow through API endpoints."""

        # 1. Create customer
        customer_data = {
            "name": "Test Customer",
            "email": "customer@example.com",
            "phone": "+1-555-0123"
        }
        customer_response = await api_client.post("/api/customers", customer_data)
        assert customer_response.status_code == 201
        customer_id = customer_response.json()["id"]

        # 2. Create product
        product_data = {
            "name": "Test Product",
            "price": 99.99,
            "category": "electronics",
            "stock": 100
        }
        product_response = await api_client.post("/api/products", product_data)
        assert product_response.status_code == 201
        product_id = product_response.json()["id"]

        # 3. Create order
        order_data = {
            "customer_id": customer_id,
            "items": [
                {"product_id": product_id, "quantity": 2}
            ],
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            }
        }
        order_response = await api_client.post("/api/orders", order_data)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]

        # 4. Process payment
        payment_data = {
            "order_id": order_id,
            "payment_method": "credit_card",
            "card_token": "test_card_token"
        }
        payment_response = await api_client.post("/api/payments", payment_data)
        assert payment_response.status_code == 200
        assert payment_response.json()["status"] == "approved"

        # 5. Verify order status
        order_status = await api_client.get(f"/api/orders/{order_id}")
        assert order_status.json()["status"] == "confirmed"
        assert order_status.json()["total_amount"] == 199.98

        # 6. Ship order
        shipping_data = {
            "tracking_number": "TEST123456",
            "carrier": "TestShip"
        }
        ship_response = await api_client.post(f"/api/orders/{order_id}/ship", shipping_data)
        assert ship_response.status_code == 200

        # 7. Verify final order state
        final_order = await api_client.get(f"/api/orders/{order_id}")
        assert final_order.json()["status"] == "shipped"
        assert final_order.json()["tracking_number"] == "TEST123456"
```

### 2. CLI Application Testing

```python
from flx.testing.e2e import CLITestRunner
import tempfile
import os

class TestCLIWorkflow:
    @pytest.fixture
    def cli_runner(self):
        return CLITestRunner(cli_command="flx-cli")

    @pytest.fixture
    def temp_project_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            yield temp_dir
            os.chdir(original_cwd)

    async def test_project_creation_and_deployment(self, cli_runner, temp_project_dir):
        """Test complete project lifecycle through CLI."""

        # 1. Initialize new project
        init_result = await cli_runner.run([
            "init", "test-project",
            "--template", "basic",
            "--framework", "flx"
        ])
        assert init_result.exit_code == 0
        assert "Project created successfully" in init_result.output

        # 2. Configure project
        config_result = await cli_runner.run([
            "config", "set",
            "--database-url", "postgresql://test:test@localhost/test_db",
            "--cache-backend", "redis",
            "--log-level", "INFO"
        ])
        assert config_result.exit_code == 0

        # 3. Generate scaffolding
        scaffold_result = await cli_runner.run([
            "generate", "entity", "User",
            "--fields", "name:str,email:str,active:bool"
        ])
        assert scaffold_result.exit_code == 0
        assert os.path.exists("src/entities/user.py")

        # 4. Run tests
        test_result = await cli_runner.run(["test", "--coverage"])
        assert test_result.exit_code == 0
        assert "All tests passed" in test_result.output

        # 5. Build project
        build_result = await cli_runner.run(["build", "--environment", "production"])
        assert build_result.exit_code == 0
        assert os.path.exists("dist/")

        # 6. Deploy to staging
        deploy_result = await cli_runner.run([
            "deploy", "staging",
            "--config", "staging.yaml",
            "--dry-run"
        ])
        assert deploy_result.exit_code == 0
        assert "Deployment plan validated" in deploy_result.output
```

### 3. Business Scenario Testing

```python
from flx.testing.e2e import BusinessScenarioTest
from flx.testing.fixtures import e2e_database, external_services

class TestECommerceBusinessScenarios(BusinessScenarioTest):

    @pytest.fixture
    async def e2e_environment(self, e2e_database, external_services):
        """Setup complete E2E test environment."""
        # Initialize system with test data
        await self.setup_test_data(e2e_database)

        # Configure external service mocks
        await external_services.configure_payment_service()
        await external_services.configure_email_service()
        await external_services.configure_shipping_service()

        yield e2e_database, external_services

        # Cleanup
        await self.cleanup_test_data(e2e_database)

    async def test_seasonal_sale_campaign(self, e2e_environment):
        """Test complete seasonal sale campaign workflow."""
        db, external_services = e2e_environment

        # 1. Admin creates sale campaign
        campaign_id = await self.create_sale_campaign({
            "name": "Summer Sale 2024",
            "discount_percentage": 25,
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",
            "applicable_categories": ["clothing", "accessories"]
        })

        # 2. Customer browses products during sale
        customer_session = await self.create_customer_session("summer_shopper@example.com")

        # 3. Customer adds sale items to cart
        cart_id = await customer_session.create_cart()
        await customer_session.add_to_cart(cart_id, "summer-dress", quantity=2)
        await customer_session.add_to_cart(cart_id, "sunglasses", quantity=1)

        # 4. Customer proceeds to checkout
        cart_total = await customer_session.get_cart_total(cart_id)
        assert cart_total["discount_applied"] == 37.50  # 25% of $150
        assert cart_total["final_amount"] == 112.50

        # 5. Customer completes purchase
        order_id = await customer_session.checkout(cart_id, {
            "payment_method": "credit_card",
            "shipping_address": self.default_shipping_address()
        })

        # 6. Verify order processing
        order = await self.get_order_details(order_id)
        assert order["status"] == "confirmed"
        assert order["campaign_id"] == campaign_id
        assert order["discount_amount"] == 37.50

        # 7. Verify external service interactions
        assert external_services.payment_service.was_called_with_amount(112.50)
        assert external_services.email_service.sent_confirmation_email()

        # 8. Verify inventory updates
        summer_dress_stock = await self.get_product_stock("summer-dress")
        assert summer_dress_stock == 98  # Started with 100, sold 2

        # 9. Verify analytics tracking
        campaign_stats = await self.get_campaign_statistics(campaign_id)
        assert campaign_stats["orders_count"] == 1
        assert campaign_stats["total_discount_given"] == 37.50

    async def test_customer_support_ticket_resolution(self, e2e_environment):
        """Test complete customer support workflow."""
        db, external_services = e2e_environment

        # 1. Customer creates support ticket
        ticket_id = await self.create_support_ticket({
            "customer_email": "help_needed@example.com",
            "subject": "Order not received",
            "order_id": "ORD-12345",
            "priority": "medium",
            "description": "I placed an order 5 days ago but haven't received it yet."
        })

        # 2. System auto-assigns to support agent
        ticket = await self.get_ticket_details(ticket_id)
        assert ticket["status"] == "assigned"
        assert ticket["assigned_agent"] is not None

        # 3. Support agent investigates
        agent_session = await self.create_agent_session(ticket["assigned_agent"])

        # 4. Agent looks up order history
        order_history = await agent_session.lookup_order_history("ORD-12345")
        assert order_history["shipping_status"] == "delayed"

        # 5. Agent updates ticket with findings
        await agent_session.update_ticket(ticket_id, {
            "status": "in_progress",
            "internal_notes": "Order delayed due to shipping issue. Expediting delivery.",
            "customer_update": "We've identified a shipping delay and are expediting your order."
        })

        # 6. Agent initiates expedited shipping
        await agent_session.expedite_shipping("ORD-12345")

        # 7. Customer receives notification
        assert external_services.email_service.sent_update_notification()

        # 8. Agent resolves ticket
        await agent_session.resolve_ticket(ticket_id, {
            "resolution": "expedited_shipping",
            "resolution_notes": "Order expedited, delivery expected tomorrow"
        })

        # 9. Verify ticket closure
        final_ticket = await self.get_ticket_details(ticket_id)
        assert final_ticket["status"] == "resolved"
        assert final_ticket["resolution_time_hours"] < 24
```

### 4. Performance and Load Testing

```python
from flx.testing.e2e import LoadTestRunner
import asyncio

class TestSystemPerformance:

    async def test_concurrent_order_processing(self):
        """Test system performance under concurrent load."""
        load_runner = LoadTestRunner(
            base_url="http://localhost:8000",
            concurrent_users=50,
            test_duration_seconds=60
        )

        async def order_workflow():
            """Single user order workflow."""
            async with load_runner.create_session() as session:
                # Create customer
                customer = await session.create_customer()

                # Browse products
                products = await session.get_products(limit=10)
                selected_product = products[0]

                # Add to cart and checkout
                cart = await session.create_cart()
                await session.add_to_cart(cart["id"], selected_product["id"], 1)
                order = await session.checkout(cart["id"])

                return order["id"]

        # Run load test
        results = await load_runner.run_load_test(order_workflow)

        # Verify performance requirements
        assert results.average_response_time < 2.0  # 2 seconds
        assert results.success_rate > 0.95  # 95% success rate
        assert results.peak_throughput > 25  # 25 orders/second
        assert results.error_rate < 0.05  # Less than 5% errors

    async def test_database_performance_under_load(self):
        """Test database performance during peak usage."""
        db_load_runner = DatabaseLoadTestRunner()

        # Simulate high read/write load
        results = await db_load_runner.run_mixed_workload(
            read_percentage=70,
            write_percentage=30,
            concurrent_connections=20,
            duration_seconds=30
        )

        # Verify database performance
        assert results.average_query_time < 0.1  # 100ms
        assert results.connection_pool_efficiency > 0.9  # 90%
        assert results.deadlock_count == 0
```

## E2E Test Environment Setup

### Test Data Management

```python
from flx.testing.data import TestDataManager

class E2ETestDataManager(TestDataManager):
    """Manage test data for E2E tests."""

    async def setup_realistic_dataset(self):
        """Create realistic test data that mirrors production."""

        # Create customers with realistic profiles
        customers = await self.create_customers([
            {"type": "premium", "order_history": "frequent"},
            {"type": "standard", "order_history": "occasional"},
            {"type": "new", "order_history": "none"}
        ])

        # Create product catalog with proper categories
        products = await self.create_product_catalog([
            {"category": "electronics", "count": 50, "price_range": (10, 500)},
            {"category": "clothing", "count": 100, "price_range": (20, 200)},
            {"category": "books", "count": 200, "price_range": (5, 50)}
        ])

        # Create historical orders for realistic scenarios
        await self.create_order_history(customers, products, months=6)

        return {
            "customers": customers,
            "products": products,
            "categories": ["electronics", "clothing", "books"]
        }
```

### External Service Configuration

```python
from flx.testing.external import ExternalServiceManager

@pytest.fixture(scope="session")
async def external_services():
    """Configure external services for E2E testing."""
    service_manager = ExternalServiceManager()

    # Configure test payment service
    await service_manager.configure_payment_service({
        "provider": "test_provider",
        "success_rate": 0.95,  # 95% success rate
        "response_delay": 0.5   # 500ms response time
    })

    # Configure test email service
    await service_manager.configure_email_service({
        "capture_emails": True,  # Capture but don't send
        "delivery_simulation": True
    })

    # Configure test shipping service
    await service_manager.configure_shipping_service({
        "provider": "test_shipping",
        "tracking_simulation": True
    })

    yield service_manager

    await service_manager.cleanup()
```

## Test Execution and Reporting

### CI/CD Integration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
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

      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements-test.txt

      - name: Start application
        run: |
          flx-cli start --environment test --background
          sleep 10  # Wait for application to start

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ \
            --maxfail=3 \
            --timeout=300 \
            --html=e2e-report.html \
            --self-contained-html

      - name: Upload test report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: e2e-test-report
          path: e2e-report.html
```

## Best Practices

### Test Design Principles

1. **Independent Tests**: Each test should be able to run independently
2. **Realistic Scenarios**: Use production-like data and workflows
3. **Stable Assertions**: Focus on business outcomes, not implementation details
4. **Clear Test Names**: Describe the business scenario being tested

### Maintenance Strategies

1. **Page Object Pattern**: For UI-based E2E tests, use page objects
2. **Data Builders**: Create reusable builders for complex test data
3. **Retry Logic**: Implement retry logic for flaky external dependencies
4. **Test Environment Isolation**: Ensure test environments don't interfere

### Debugging and Troubleshooting

1. **Detailed Logging**: Log all test steps and external service interactions
2. **Screenshot Capture**: For UI tests, capture screenshots on failure
3. **Service Health Checks**: Verify external services before running tests
4. **Test Data Inspection**: Provide easy access to test data for debugging

## Related Documentation

- [Testing Overview](overview.md) - Testing strategy and philosophy
- [Unit Testing](unit-testing.md) - Unit testing patterns
- [Integration Testing](integration-testing.md) - Integration testing strategies

---

_This guide provides comprehensive patterns for end-to-end testing in the FLX framework, ensuring complete business workflows function correctly in production-like environments._
