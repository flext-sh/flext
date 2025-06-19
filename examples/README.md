# 📚 PyAuto Examples - Complete Usage Demonstrations

> **Function**: Comprehensive examples demonstrating PyAuto enterprise patterns and integrations | **Audience**: Developers, Solution Architects, Integration Engineers | **Status**: Production Examples

[![Python](https://img.shields.io/badge/python-3.9%2B-orange.svg)](https://www.python.org/)
[![Async](https://img.shields.io/badge/async-asyncio-blue.svg)](https://docs.python.org/3/library/asyncio.html)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](https://alistair.cockburn.us/hexagonal-architecture/)
[![DDD](https://img.shields.io/badge/pattern-DDD-purple.svg)](https://martinfowler.com/tags/domain%20driven%20design.html)

## 📋 **Overview**

Complete collection of production-ready examples demonstrating PyAuto enterprise patterns, integrations, and best practices. Each example includes comprehensive error handling, logging, and follows hexagonal architecture principles with Domain-Driven Design patterns.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../README.md) → **📂 Current**: Examples

---

## 🎯 **Example Categories**

### **Core Architecture Examples**

| Example                                                       | Description                              | Complexity | Key Patterns                    |
| ------------------------------------------------------------- | ---------------------------------------- | ---------- | ------------------------------- |
| [async_ddd_example.py](#async-ddd)                            | Domain-Driven Design with async patterns | ⭐⭐⭐     | DDD, Async, Repository          |
| [async_domain_integration_demo.py](#async-domain-integration) | Cross-domain integration patterns        | ⭐⭐⭐⭐   | Event Sourcing, CQRS            |
| [async_infrastructure_usage.py](#async-infrastructure)        | Infrastructure layer implementation      | ⭐⭐⭐     | Hexagonal, Dependency Injection |

### **Integration Examples**

| Example                                                    | Description                        | Complexity | Technologies        |
| ---------------------------------------------------------- | ---------------------------------- | ---------- | ------------------- |
| [flx_integrated_usage.py](#flx-integration)                | Complete FLX framework integration | ⭐⭐⭐⭐   | FLX, Plugin System  |
| [flx_meltano_integration_example.py](#meltano-integration) | Meltano pipeline integration       | ⭐⭐⭐⭐   | Meltano, Singer SDK |
| [fastapi_integration_example.py](#fastapi-integration)     | FastAPI web service integration    | ⭐⭐⭐     | FastAPI, REST API   |

### **Resilience Examples**

| Example                                                      | Description                            | Complexity | Patterns               |
| ------------------------------------------------------------ | -------------------------------------- | ---------- | ---------------------- |
| [circuit_breaker_example.py](#circuit-breaker)               | Circuit breaker pattern implementation | ⭐⭐⭐     | Circuit Breaker, Retry |
| [circuit_breaker_simple_example.py](#circuit-breaker-simple) | Simplified circuit breaker usage       | ⭐⭐       | Basic Resilience       |
| [circuit_breaker_working.py](#circuit-breaker-working)       | Production circuit breaker patterns    | ⭐⭐⭐⭐   | Advanced Resilience    |

### **Service Examples**

| Example                                                        | Description                      | Complexity | Technologies             |
| -------------------------------------------------------------- | -------------------------------- | ---------- | ------------------------ |
| [advanced_infra_services_example.py](#advanced-services)       | Advanced infrastructure services | ⭐⭐⭐⭐   | DI, Service Layer        |
| [standardized_infra_services_usage.py](#standardized-services) | Standardized service patterns    | ⭐⭐⭐     | Service Architecture     |
| [daemon_usage_example.py](#daemon-usage)                       | Background daemon services       | ⭐⭐⭐     | Daemon, Background Tasks |

### **Plugin System Examples**

| Example                                                  | Description                 | Complexity | Patterns             |
| -------------------------------------------------------- | --------------------------- | ---------- | -------------------- |
| [flx_cli_plugin_example.py](#cli-plugin)                 | CLI plugin development      | ⭐⭐       | Plugin Architecture  |
| [flx_declarative_plugin_example.py](#declarative-plugin) | Declarative plugin patterns | ⭐⭐⭐     | Configuration-Driven |

### **Domain-Specific Examples**

| Example                                                   | Description                     | Complexity | Domain         |
| --------------------------------------------------------- | ------------------------------- | ---------- | -------------- |
| [declarative_projects_examples.py](#declarative-projects) | Project management patterns     | ⭐⭐⭐     | Project Domain |
| [wms_cli_example.py](#wms-cli)                            | Warehouse Management System CLI | ⭐⭐       | WMS Domain     |

---

## 🚀 **Quick Start**

### **Prerequisites**

```bash
# Install PyAuto with all dependencies
cd /path/to/pyauto
poetry install --extras "all"

# Set environment variables
export ORACLE_HOST=your-oracle-host
export ORACLE_PORT=1521
export ORACLE_SERVICE_NAME=your-service
export ORACLE_USERNAME=your-username
export ORACLE_PASSWORD=your-password
```

### **Running Examples**

```bash
# Basic async DDD example
python examples/async_ddd_example.py

# Complete FLX integration
python examples/flx_integrated_usage.py

# Circuit breaker patterns
python examples/circuit_breaker_example.py

# FastAPI integration
python examples/fastapi_integration_example.py
```

---

## 📖 **Detailed Examples**

### **async_ddd_example.py** {#async-ddd}

**Purpose**: Demonstrates Domain-Driven Design patterns with async/await

**Key Features**:

- Domain entities with business logic
- Repository pattern implementation
- Service layer orchestration
- Event-driven architecture

**Usage**:

```python
from examples.async_ddd_example import UserDomainService, OrderProcessingService

# Initialize domain services
user_service = UserDomainService(user_repository)
order_service = OrderProcessingService(order_repository)

# Process business operations
user = await user_service.create_premium_user(user_data)
order = await order_service.process_order(order_data, user)
```

**Architecture Pattern**:

```
Domain Layer (Business Logic)
├── Entities (User, Order)
├── Value Objects (Email, Money)
├── Domain Services (UserDomainService)
└── Domain Events (UserCreated, OrderProcessed)

Application Layer (Use Cases)
├── Command Handlers
├── Query Handlers
└── Event Handlers

Infrastructure Layer (Technical Concerns)
├── Repositories (Database Access)
├── External Services (API Clients)
└── Event Bus (Message Publishing)
```

### **async_domain_integration_demo.py** {#async-domain-integration}

**Purpose**: Cross-domain integration with event sourcing and CQRS

**Key Features**:

- Event sourcing implementation
- CQRS pattern separation
- Cross-domain communication
- Eventual consistency handling

**Usage**:

```python
# Command side (writes)
command_handler = CreateOrderCommandHandler(event_store)
await command_handler.handle(CreateOrderCommand(order_data))

# Query side (reads)
query_handler = OrderProjectionQueryHandler(read_model)
order_view = await query_handler.get_order_summary(order_id)
```

### **circuit_breaker_example.py** {#circuit-breaker}

**Purpose**: Resilience patterns for external service calls

**Key Features**:

- Circuit breaker implementation
- Retry with exponential backoff
- Fallback mechanisms
- Health monitoring

**Usage**:

```python
from examples.circuit_breaker_example import ResilientHttpClient

# Configure circuit breaker
client = ResilientHttpClient(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=requests.RequestException
)

# Make resilient calls
try:
    response = await client.get("https://api.external-service.com/data")
except CircuitBreakerOpenException:
    # Handle circuit breaker open state
    response = get_cached_data()
```

### **flx_integrated_usage.py** {#flx-integration}

**Purpose**: Complete FLX framework integration example

**Key Features**:

- Plugin system usage
- Dependency injection
- Configuration management
- Service orchestration

**Usage**:

```python
# Initialize FLX application
app = FlxApplication()
await app.initialize()

# Register plugins
app.register_plugin(OraclePlugin(oracle_config))
app.register_plugin(HttpPlugin(http_config))

# Use services
oracle_repo = app.get_service(OracleRepository)
http_client = app.get_service(HttpClient)
```

### **fastapi_integration_example.py** {#fastapi-integration}

**Purpose**: REST API development with FastAPI integration

**Key Features**:

- FastAPI application setup
- Dependency injection integration
- Error handling middleware
- OpenAPI documentation

**Usage**:

```python
# Run the FastAPI application
uvicorn examples.fastapi_integration_example:app --reload

# API endpoints available at:
# GET /health - Health check
# POST /users - Create user
# GET /users/{user_id} - Get user
# PUT /users/{user_id} - Update user
```

### **flx_meltano_integration_example.py** {#meltano-integration}

**Purpose**: Data pipeline integration with Meltano

**Key Features**:

- Singer SDK integration
- Custom tap/target development
- Meltano plugin configuration
- Data transformation pipelines

**Usage**:

```python
# Configure Meltano pipeline
pipeline = MeltanoPipeline([
    ("tap-oracle-wms", oracle_config),
    ("target-postgres", postgres_config)
])

# Run data extraction and loading
await pipeline.run()
```

---

## 🏗️ **Architecture Patterns**

### **Hexagonal Architecture Implementation**

All examples follow hexagonal architecture principles:

```
┌─────────────────────────────────────────────────────────┐
│                    Domain Layer                         │
│              (Business Logic Core)                      │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│               Application Layer                         │
│             (Use Cases & Services)                      │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│            Ports (Interfaces)                          │
│       ┌─────────────────┬─────────────────┐            │
│       │   Inbound       │    Outbound     │            │
│       │   (Commands)    │  (Repositories) │            │
└───────┴─────────────────┴─────────────────┴────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              Adapters                                   │
│  ┌─────────────────┬─────────────────────────────────┐  │
│  │    Inbound      │       Outbound                  │  │
│  │  (REST API)     │   (Database, HTTP)              │  │
│  └─────────────────┴─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### **Domain-Driven Design Patterns**

```python
# Domain Entity
class User:
    def __init__(self, user_id: UserId, email: Email, status: UserStatus):
        self._user_id = user_id
        self._email = email
        self._status = status
        self._domain_events: List[DomainEvent] = []

    def activate(self) -> None:
        if self._status == UserStatus.ACTIVE:
            raise UserAlreadyActiveError()

        self._status = UserStatus.ACTIVE
        self._domain_events.append(UserActivatedEvent(self._user_id))

# Repository Interface (Port)
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]: ...

# Repository Implementation (Adapter)
class OracleUserRepository(UserRepository):
    async def save(self, user: User) -> None:
        # Implementation details
        pass
```

---

## 🔧 **Configuration Examples**

### **Database Configuration**

```python
# Database settings for examples
DATABASE_CONFIG = {
    "oracle": {
        "host": "oracle.company.com",
        "port": 1521,
        "service_name": "PROD",
        "username": "app_user",
        "password": "secure_password",
        "pool_size": 10,
        "max_overflow": 20
    }
}
```

### **HTTP Client Configuration**

```python
# HTTP client settings
HTTP_CONFIG = {
    "timeout": 30,
    "retry_attempts": 3,
    "circuit_breaker": {
        "failure_threshold": 5,
        "recovery_timeout": 60
    }
}
```

### **Logging Configuration**

```python
# Structured logging setup
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}
```

---

## 🧪 **Testing Examples**

### **Unit Testing Pattern**

```python
@pytest.mark.asyncio
async def test_user_creation_domain_logic():
    """Test user creation with domain validation."""
    # Arrange
    user_data = {
        "email": "john@example.com",
        "name": "John Doe"
    }

    # Act
    user = User.create(user_data)

    # Assert
    assert user.email.value == "john@example.com"
    assert user.status == UserStatus.PENDING
    assert len(user.domain_events) == 1
    assert isinstance(user.domain_events[0], UserCreatedEvent)
```

### **Integration Testing Pattern**

```python
@pytest.mark.asyncio
async def test_complete_user_workflow(oracle_repository):
    """Test complete user workflow with real database."""
    # Arrange
    user_service = UserService(oracle_repository)

    # Act
    user = await user_service.create_user({
        "email": "test@example.com",
        "name": "Test User"
    })

    activated_user = await user_service.activate_user(user.id)

    # Assert
    assert activated_user.status == UserStatus.ACTIVE

    # Verify persistence
    retrieved_user = await oracle_repository.get_by_id(user.id)
    assert retrieved_user.status == UserStatus.ACTIVE
```

---

## 📊 **Performance Considerations**

### **Async Best Practices**

```python
# Good: Concurrent execution
async def process_orders_concurrently(orders: List[Order]) -> List[ProcessedOrder]:
    tasks = [process_single_order(order) for order in orders]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Bad: Sequential execution
async def process_orders_sequentially(orders: List[Order]) -> List[ProcessedOrder]:
    results = []
    for order in orders:
        result = await process_single_order(order)  # Blocks other operations
        results.append(result)
    return results
```

### **Connection Pooling**

```python
# Configure connection pools in examples
DATABASE_POOL_CONFIG = {
    "pool_size": 10,           # Base pool size
    "max_overflow": 20,        # Additional connections
    "pool_pre_ping": True,     # Validate connections
    "pool_recycle": 3600       # Recycle after 1 hour
}
```

---

## 🚨 **Error Handling Patterns**

### **Comprehensive Error Management**

```python
class BusinessLogicError(Exception):
    """Base class for business logic errors."""
    pass

class UserNotFoundError(BusinessLogicError):
    """User not found in the system."""
    pass

async def get_user_safely(user_id: UserId) -> User:
    """Get user with comprehensive error handling."""
    try:
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        raise InfrastructureError("Database unavailable") from e

    except Exception as e:
        logger.error(f"Unexpected error getting user {user_id}: {e}")
        raise SystemError("Internal system error") from e
```

---

## 🔗 **Cross-References**

### **Related Components**

- [FLX Core](../flx/README.md) - Framework foundation
- [FLX Database Oracle](../flx-database-oracle/README.md) - Database integration
- [TAP Oracle WMS](../tap-oracle-wms/README.md) - Data extraction
- [Target Oracle WMS](../target-oracle-wms/README.md) - Data loading

### **External Documentation**

- [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html) - DDD patterns
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) - Architecture reference
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - FastAPI integration
- [Meltano Documentation](https://docs.meltano.com/) - Data pipeline integration

### **Best Practices**

- [Python Async Best Practices](https://docs.python.org/3/library/asyncio-dev.html) - Async programming
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - Architecture principles
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID) - Design principles

---

**📂 Component**: Examples | **🏠 Root**: [PyAuto Home](../README.md) | **Framework**: PyAuto 1.0.0+ | **Updated**: 2025-06-19
