# 📚 FLX Framework - Documentation

> **Module**: Comprehensive documentation for FLX framework including architecture guides, development workflows, and API references | **Audience**: Developers, Architects, Technical Writers | **Status**: Production Ready

## 📋 **Overview**

Complete documentation ecosystem for the FLX (Framework Layered eXecution) enterprise Python automation framework. This documentation provides comprehensive guides, architectural patterns, API references, and best practices for developing, deploying, and maintaining FLX-based applications.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Framework](../README.md) → **📂 Current**: Documentation

---

## 🎯 **Module Purpose**

This documentation module serves as the comprehensive knowledge base for the FLX framework, providing detailed guidance on architecture patterns, development workflows, deployment strategies, and operational best practices for enterprise-grade Python automation systems.

### **Key Documentation Areas**

- **Architecture Guides** - Hexagonal architecture, DDD, and design patterns
- **Development Documentation** - Setup, workflows, and coding standards
- **API References** - Complete API documentation with examples
- **Deployment Guides** - Production deployment and configuration
- **Operational Manuals** - Monitoring, maintenance, and troubleshooting
- **Best Practices** - Coding standards, security, and performance guidelines

---

## 📁 **Documentation Structure**

```
docs/
├── architecture/
│   ├── overview.md               # Architecture overview and principles
│   ├── hexagonal-architecture.md # Hexagonal architecture implementation
│   ├── domain-driven-design.md   # DDD patterns and practices
│   ├── event-sourcing.md         # Event sourcing implementation
│   ├── cqrs-patterns.md          # Command Query Responsibility Segregation
│   └── microservices.md          # Microservices architecture patterns
├── development/
│   ├── setup-guide.md            # Development environment setup
│   ├── coding-standards.md       # Coding standards and conventions
│   ├── testing-guide.md          # Testing strategies and practices
│   ├── debugging-guide.md        # Debugging techniques and tools
│   ├── plugin-development.md     # Plugin development guide
│   └── contributing.md           # Contribution guidelines
├── api/
│   ├── core-api.md               # Core framework API reference
│   ├── domain-api.md             # Domain layer API documentation
│   ├── application-api.md        # Application layer API documentation
│   ├── infrastructure-api.md     # Infrastructure layer API documentation
│   └── adapters-api.md           # Adapters API documentation
├── deployment/
│   ├── production-deployment.md  # Production deployment guide
│   ├── environment-config.md     # Environment configuration
│   ├── docker-deployment.md      # Docker deployment strategies
│   ├── kubernetes-deployment.md  # Kubernetes deployment patterns
│   └── monitoring-setup.md       # Monitoring and observability setup
├── operations/
│   ├── monitoring-guide.md       # System monitoring and alerting
│   ├── maintenance-guide.md      # System maintenance procedures
│   ├── troubleshooting.md        # Common issues and solutions
│   ├── performance-tuning.md     # Performance optimization guide
│   └── security-guide.md         # Security best practices
├── tutorials/
│   ├── getting-started.md        # Getting started tutorial
│   ├── building-first-app.md     # First application tutorial
│   ├── advanced-patterns.md      # Advanced development patterns
│   ├── integration-examples.md   # Integration examples and tutorials
│   └── migration-guide.md        # Migration from other frameworks
└── reference/
    ├── configuration-reference.md # Complete configuration reference
    ├── cli-reference.md          # Command-line interface reference
    ├── error-codes.md            # Error codes and troubleshooting
    ├── glossary.md               # Technical glossary
    └── changelog.md              # Framework changelog and updates
```

---

## 🏗️ **Architecture Documentation**

### **Hexagonal Architecture Guide (architecture/hexagonal-architecture.md)**

````markdown
# Hexagonal Architecture in FLX Framework

## Overview

The FLX framework implements hexagonal architecture (Ports and Adapters)
to achieve:

- **Testability**: Easy unit testing with mock adapters
- **Flexibility**: Swap implementations without core changes
- **Maintainability**: Clear separation of concerns
- **Scalability**: Modular design supports growth

## Architecture Layers

### 1. Domain Layer (Business Logic Core)

```python
# Pure business logic with no external dependencies
class User:
    def __init__(self, user_id: UserId, email: Email):
        self._user_id = user_id
        self._email = email
        self._domain_events: List[DomainEvent] = []

    def change_email(self, new_email: Email) -> None:
        if self._email == new_email:
            return

        old_email = self._email
        self._email = new_email

        self._domain_events.append(
            UserEmailChangedEvent(self._user_id, old_email, new_email)
        )
```
````

### 2. Application Layer (Use Cases)

```python
class UserApplicationService:
    def __init__(
        self,
        user_repository: UserRepository,  # Port
        email_service: EmailService,      # Port
        event_bus: EventBus              # Port
    ):
        self._user_repository = user_repository
        self._email_service = email_service
        self._event_bus = event_bus

    async def change_user_email(
        self,
        user_id: UserId,
        new_email: Email
    ) -> None:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        user.change_email(new_email)
        await self._user_repository.save(user)

        for event in user.domain_events:
            await self._event_bus.publish(event)
```

### 3. Ports (Interfaces)

```python
# Inbound Ports (Application Interfaces)
class UserManagementPort(ABC):
    @abstractmethod
    async def change_user_email(self, user_id: UserId, email: Email) -> None:
        pass

# Outbound Ports (Infrastructure Interfaces)
class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        pass
```

### 4. Adapters (Implementation)

```python
# Inbound Adapter (REST API)
@app.post("/users/{user_id}/email")
async def change_user_email(
    user_id: str,
    email_data: EmailChangeRequest,
    user_service: UserManagementPort = Depends()
):
    await user_service.change_user_email(
        UserId(user_id),
        Email(email_data.email)
    )
    return {"status": "success"}

# Outbound Adapter (Database)
class SqlAlchemyUserRepository(UserRepository):
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        # Database implementation
        pass
```

````

### **Domain-Driven Design Guide (architecture/domain-driven-design.md)**

```markdown
# Domain-Driven Design in FLX Framework

## Core Concepts

### 1. Entities
Objects with identity that persist over time:

```python
@dataclass
class Order:
    """Order entity with business identity."""

    id: OrderId
    customer_id: CustomerId
    items: List[OrderItem]
    status: OrderStatus
    created_at: datetime

    def add_item(self, product_id: ProductId, quantity: int, price: Money) -> None:
        if self.status != OrderStatus.DRAFT:
            raise OrderNotModifiableError("Cannot modify non-draft order")

        item = OrderItem(product_id, quantity, price)
        self.items.append(item)

        # Domain event
        self._domain_events.append(
            OrderItemAddedEvent(self.id, item)
        )

    def calculate_total(self) -> Money:
        return sum(item.total_price for item in self.items)
````

### 2. Value Objects

Objects without identity, defined by their values:

```python
@dataclass(frozen=True)
class Email:
    """Email value object with validation."""

    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise InvalidEmailError(self.value)

    def _is_valid_email(self, email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

@dataclass(frozen=True)
class Money:
    """Money value object with currency support."""

    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise InvalidMoneyAmountError("Amount cannot be negative")

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"Cannot add {self.currency} and {other.currency}")

        return Money(self.amount + other.amount, self.currency)
```

### 3. Aggregates

Consistency boundaries for related entities:

```python
class OrderAggregate:
    """Order aggregate root managing consistency."""

    def __init__(self, order: Order):
        self._order = order
        self._domain_events: List[DomainEvent] = []

    def add_item(self, product_id: ProductId, quantity: int, price: Money) -> None:
        # Business rule: Check inventory before adding
        if not self._inventory_service.is_available(product_id, quantity):
            raise InsufficientInventoryError(product_id, quantity)

        self._order.add_item(product_id, quantity, price)

        # Reserve inventory
        self._domain_events.append(
            InventoryReservationRequestedEvent(product_id, quantity)
        )

    def confirm_order(self) -> None:
        if not self._order.items:
            raise EmptyOrderError("Cannot confirm empty order")

        self._order.status = OrderStatus.CONFIRMED

        self._domain_events.append(
            OrderConfirmedEvent(self._order.id, self._order.calculate_total())
        )
```

````

---

## 🚀 **Development Documentation**

### **Setup Guide (development/setup-guide.md)**

```markdown
# FLX Framework Development Setup

## Prerequisites

- Python 3.9+
- Poetry 1.5+
- Docker 20.0+
- Git 2.30+

## Quick Setup

```bash
# Clone repository
git clone https://github.com/company/flx-framework.git
cd flx-framework

# Run automated setup
./scripts/development/setup_dev_env.py

# Verify installation
poetry run python -c "import flx; print('FLX Framework installed successfully!')"
````

## Manual Setup

### 1. Python Environment

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Create virtual environment
poetry install --extras "dev,test,docs"

# Activate environment
poetry shell
```

### 2. Database Setup

```bash
# Start development databases
docker-compose -f docker-compose.dev.yml up -d

# Run migrations
poetry run alembic upgrade head

# Verify database connection
poetry run python scripts/development/test_db_connection.py
```

### 3. Configuration

```bash
# Copy environment template
cp config/development.yaml.template config/development.yaml

# Edit configuration
vim config/development.yaml
```

## Development Workflow

### Running Tests

```bash
# Unit tests
poetry run pytest tests/unit/

# Integration tests
poetry run pytest tests/integration/

# All tests with coverage
poetry run pytest --cov=flx tests/
```

### Code Quality

```bash
# Format code
poetry run black flx/

# Check linting
poetry run ruff check flx/

# Type checking
poetry run mypy flx/
```

````

### **Testing Guide (development/testing-guide.md)**

```markdown
# Testing Strategies for FLX Framework

## Testing Pyramid

### 1. Unit Tests (Fast, Isolated)
Test individual components in isolation:

```python
@pytest.mark.asyncio
async def test_user_email_change_domain_logic():
    """Test user email change business logic."""
    # Arrange
    user = User(UserId("123"), Email("old@example.com"))
    new_email = Email("new@example.com")

    # Act
    user.change_email(new_email)

    # Assert
    assert user.email == new_email
    assert len(user.domain_events) == 1
    assert isinstance(user.domain_events[0], UserEmailChangedEvent)
````

### 2. Integration Tests (Medium Speed, Multiple Components)

Test component interactions:

```python
@pytest.mark.integration
async def test_user_service_with_repository():
    """Test user service with real repository."""
    # Arrange
    async with test_database() as db:
        repository = SqlAlchemyUserRepository(db.session)
        service = UserApplicationService(repository, mock_email_service)

        # Create user
        user = await service.create_user(UserCreationData(
            email="test@example.com",
            name="Test User"
        ))

        # Act
        await service.change_user_email(user.id, Email("updated@example.com"))

        # Assert
        updated_user = await repository.get_by_id(user.id)
        assert updated_user.email.value == "updated@example.com"
```

### 3. End-to-End Tests (Slow, Full System)

Test complete user workflows:

```python
@pytest.mark.e2e
async def test_complete_user_registration_workflow():
    """Test complete user registration through API."""
    async with test_client() as client:
        # Register user
        response = await client.post("/api/users", json={
            "email": "newuser@example.com",
            "name": "New User"
        })
        assert response.status_code == 201

        user_id = response.json()["user_id"]

        # Verify user creation
        user_response = await client.get(f"/api/users/{user_id}")
        assert user_response.status_code == 200
        assert user_response.json()["email"] == "newuser@example.com"
```

## Test Patterns

### Mocking External Dependencies

```python
@pytest.fixture
def mock_email_service():
    with patch('flx.infrastructure.email.SmtpEmailService') as mock:
        mock.send_email.return_value = EmailSendResult(success=True)
        yield mock

async def test_user_creation_sends_welcome_email(mock_email_service):
    service = UserApplicationService(repository, mock_email_service)

    await service.create_user(user_data)

    mock_email_service.send_email.assert_called_once()
```

### Test Data Builders

```python
class UserTestDataBuilder:
    def __init__(self):
        self._email = "test@example.com"
        self._name = "Test User"
        self._status = UserStatus.ACTIVE

    def with_email(self, email: str) -> 'UserTestDataBuilder':
        self._email = email
        return self

    def with_inactive_status(self) -> 'UserTestDataBuilder':
        self._status = UserStatus.INACTIVE
        return self

    def build(self) -> User:
        return User(
            user_id=UserId.generate(),
            email=Email(self._email),
            name=self._name,
            status=self._status
        )

# Usage
user = UserTestDataBuilder().with_email("custom@example.com").build()
```

````

---

## 📖 **API Documentation**

### **Core API Reference (api/core-api.md)**

```markdown
# FLX Framework Core API Reference

## Container (Dependency Injection)

### Class: `Container`

Main dependency injection container for FLX framework.

#### Methods

##### `bind(interface: Type[T], implementation: Type[T]) -> None`
Bind interface to implementation.

**Parameters:**
- `interface`: Interface type to bind
- `implementation`: Implementation type

**Example:**
```python
container = Container()
container.bind(UserRepository, SqlAlchemyUserRepository)
````

##### `get(service_type: Type[T]) -> T`

Resolve service from container.

**Parameters:**

- `service_type`: Service type to resolve

**Returns:**

- Instance of requested service type

**Raises:**

- `ServiceNotFoundError`: If service not registered

**Example:**

```python
user_repo = container.get(UserRepository)
```

## Event Bus

### Class: `EventBus`

Handles domain event publishing and subscription.

#### Methods

##### `publish(event: DomainEvent) -> None`

Publish domain event to all subscribers.

**Parameters:**

- `event`: Domain event to publish

**Example:**

```python
event = UserCreatedEvent(user_id, email)
await event_bus.publish(event)
```

##### `subscribe(event_type: Type[DomainEvent], handler: EventHandler) -> None`

Subscribe handler to event type.

**Parameters:**

- `event_type`: Type of event to subscribe to
- `handler`: Event handler function

**Example:**

```python
async def handle_user_created(event: UserCreatedEvent):
    await send_welcome_email(event.user_id)

event_bus.subscribe(UserCreatedEvent, handle_user_created)
```

````

---

## 🚀 **Deployment Documentation**

### **Production Deployment Guide (deployment/production-deployment.md)**

```markdown
# Production Deployment Guide

## Prerequisites

- Kubernetes cluster (1.24+)
- Helm 3.8+
- Docker registry access
- Database (PostgreSQL 14+)
- Redis cluster

## Deployment Process

### 1. Build and Push Images
```bash
# Build application image
docker build -t flx-app:1.0.0 .

# Push to registry
docker push registry.company.com/flx-app:1.0.0
````

### 2. Deploy with Helm

```bash
# Add FLX Helm repository
helm repo add flx-charts https://charts.company.com/flx

# Deploy to production
helm upgrade --install flx-production flx-charts/flx-framework \
  --namespace production \
  --values values-production.yaml \
  --set image.tag=1.0.0
```

### 3. Verify Deployment

```bash
# Check pod status
kubectl get pods -n production

# Check service health
kubectl exec -n production deployment/flx-app -- \
  python -c "from flx.health import health_check; print(health_check())"

# Run smoke tests
./scripts/deployment/run_smoke_tests.py --environment production
```

## Configuration

### Environment Variables

```yaml
# Production configuration
app:
  environment: production
  log_level: INFO

database:
  url: "postgresql://user:pass@db.company.com:5432/flx_prod"
  pool_size: 20

redis:
  url: "redis://redis.company.com:6379/0"

monitoring:
  prometheus_enabled: true
  jaeger_enabled: true
```

## Monitoring

### Health Checks

```yaml
# Kubernetes health check configuration
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Metrics Collection

```yaml
# Prometheus metrics configuration
metrics:
  enabled: true
  path: /metrics
  port: 9090

# Custom metrics
custom_metrics:
  - name: flx_requests_total
    type: counter
    description: Total number of requests

  - name: flx_request_duration_seconds
    type: histogram
    description: Request duration in seconds
```

````

---

## 🔧 **Operations Documentation**

### **Monitoring Guide (operations/monitoring-guide.md)**

```markdown
# FLX Framework Monitoring Guide

## Monitoring Stack

- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger
- **Alerting**: AlertManager + PagerDuty

## Key Metrics to Monitor

### Application Metrics
```python
# Request metrics
flx_http_requests_total{method="GET", endpoint="/api/users", status="200"}
flx_http_request_duration_seconds{method="GET", endpoint="/api/users"}

# Business metrics
flx_users_created_total
flx_orders_processed_total
flx_payment_transactions_total

# Error metrics
flx_errors_total{error_type="validation", component="user_service"}
flx_database_errors_total{database="primary", operation="select"}
````

### Infrastructure Metrics

```python
# Database metrics
flx_database_connections_active{database="primary"}
flx_database_query_duration_seconds{database="primary", query_type="select"}
flx_database_deadlocks_total{database="primary"}

# Cache metrics
flx_cache_hits_total{cache="redis"}
flx_cache_misses_total{cache="redis"}
flx_cache_evictions_total{cache="redis"}
```

## Alerting Rules

### Critical Alerts

```yaml
# High error rate
- alert: HighErrorRate
  expr: rate(flx_errors_total[5m]) > 0.1
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }} errors per second"

# Database connection issues
- alert: DatabaseConnectionFailure
  expr: flx_database_connections_active < 1
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Database connection failure"
    description: "No active database connections"
```

### Warning Alerts

```yaml
# High response time
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(flx_http_request_duration_seconds_bucket[5m])) > 2.0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High response time"
    description: "95th percentile response time is {{ $value }} seconds"
```

## Log Analysis

### Structured Logging Format

```json
{
  "timestamp": "2025-06-19T10:00:00Z",
  "level": "INFO",
  "logger": "flx.application.user_service",
  "message": "User created successfully",
  "context": {
    "user_id": "12345",
    "email": "user@example.com",
    "request_id": "req-abc123",
    "trace_id": "trace-xyz789"
  }
}
```

### Log Queries

```sql
-- Find all errors in the last hour
SELECT * FROM logs
WHERE level = 'ERROR'
AND timestamp > NOW() - INTERVAL '1 hour'

-- Find slow queries
SELECT * FROM logs
WHERE logger LIKE '%database%'
AND message LIKE '%duration%'
AND CAST(context->>'duration' AS FLOAT) > 1.0
```

```

---

## 🔗 **Cross-References**

### **Internal Documentation**

- [Component Overview](../README.md) - Complete FLX framework documentation
- [Source Implementation](../src/README.md) - FLX source code structure
- [Scripts and Utilities](../scripts/README.md) - Development and maintenance scripts

### **External References**

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) - Original architecture concept
- [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html) - DDD patterns and practices
- [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) - Event sourcing patterns

### **Framework Documentation**

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Web framework integration
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) - Database ORM
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation

---

**📂 Module**: Documentation | **🏠 Component**: [FLX Framework](../README.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-19
```
