# FLX Testing Framework - Comprehensive Guide

> **Cross-References:**
>
> - [Testing Hexagonal Architecture](./TESTING_HEXAGONAL_ARCHITECTURE.md) - Testing patterns for hexagonal architecture
> - [Core API Reference](../api-reference/core-api-reference.md) - Framework APIs and testing interfaces
> - [Development Standards](./standardization-plan.md) - Code quality and testing standards

## Overview

The FLX testing framework provides comprehensive testing capabilities designed specifically for hexagonal architecture applications. It includes specialized testing engines for different system components and mock adapters that implement the same port contracts as production counterparts.

## Architecture Overview

The testing framework follows a hierarchical pattern with clear separation between testing engines (orchestration) and testing adapters (mocking):

```
┌─────────────────────┐
│ TestOrchestrator    │ ◄── Coordinates multiple engines
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│   BaseTestEngine    │ ◄── Common testing infrastructure
└─────────────────────┘
           │
           ▼
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ Component Engines   │ Infrastructure      │ Integration         │
│ • Authentication    │ Engines            │ Engines            │
│ • Cache             │ • Database         │ • Comprehensive     │
│ • HTTP              │ • Messaging        │ • Observability     │
│ • Logging           │ • Runtime          │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
           │
           ▼
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Test Cases        │◄───┤ Testing Adapters ├───►│   Port Contracts│
└─────────────────────┘    └──────────────────┘    └─────────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │ Predictable Data │
                        │ & Behavior       │
                        └──────────────────┘
```

---

## Testing Engines

### Base Engine Foundation

**Purpose**: Foundation for all testing engines providing common functionality.

**Key Features:**

- Test result collection and reporting
- Error handling and exception management
- Test lifecycle management (setup, execution, teardown)
- Metrics collection and performance tracking
- Configuration management for test execution

**Usage:**

```python
from flext.testing.engines.base import BaseTestEngine

class CustomTestEngine(BaseTestEngine):
    async def run_specific_tests(self) -> TestResult:
        # Implement custom test logic
        pass
```

### Component Testing Engines

#### Authentication Engine

**Purpose**: Testing authentication and authorization mechanisms.

**Test Coverage:**

- User authentication flows
- Token validation and expiration
- Permission and role-based access control
- Multi-factor authentication scenarios
- SSO and federated authentication
- Security policy enforcement

**Implementation Example:**

```python
from flext.testing.engines.authentication_engine import AuthenticationEngine

engine = AuthenticationEngine()
results = await engine.test_user_authentication({
    "username": "testuser",
    "password": "testpass",
    "expected_roles": ["user", "customer"]
})

# Verify authentication results
assert results.authentication_successful
assert "user" in results.assigned_roles
assert results.token_expiry > datetime.utcnow()
```

#### Cache Engine

**Purpose**: Testing caching strategies and cache implementations.

**Test Coverage:**

- Cache hit/miss ratios
- TTL and expiration behavior
- Cache invalidation patterns
- Memory usage and performance
- Distributed cache consistency
- Cache warming and eviction policies

**Performance Testing:**

```python
from flext.testing.engines.cache_engine import CacheEngine

engine = CacheEngine()
results = await engine.test_cache_performance({
    "operations": 1000,
    "key_pattern": "user:{}",
    "value_size": 1024
})

# Analyze performance metrics
assert results.average_latency < 1.0  # ms
assert results.hit_ratio > 0.95
assert results.memory_usage < engine.max_memory
```

#### HTTP Engine

**Purpose**: Testing HTTP client and server interactions.

**Test Coverage:**

- HTTP method support (GET, POST, PUT, DELETE)
- Request/response validation
- Error handling and status codes
- Timeout and retry behavior
- Load testing and performance
- SSL/TLS and security headers

**Load Testing Example:**

```python
from flext.testing.engines.http_engine import HttpEngine

engine = HttpEngine()
results = await engine.test_api_endpoints({
    "base_url": "https://api.example.com",
    "endpoints": ["/users", "/orders", "/products"],
    "concurrent_requests": 50
})

# Validate load test results
assert results.success_rate > 0.99
assert results.average_response_time < 100  # ms
assert results.p95_response_time < 200  # ms
```

### Infrastructure Testing Engines

#### Database Engine

**Purpose**: Testing database operations and data persistence.

**Test Coverage:**

- CRUD operation performance
- Transaction handling and rollback
- Connection pooling and concurrency
- Query optimization and execution plans
- Data integrity and constraints
- Migration and schema changes

**Transaction Testing:**

```python
from flext.testing.engines.database_engine import DatabaseEngine

engine = DatabaseEngine()
results = await engine.test_transaction_integrity({
    "operations": ["insert", "update", "delete"],
    "table": "users",
    "concurrent_connections": 10
})

# Verify transaction integrity
assert results.all_transactions_committed
assert results.no_data_corruption
assert results.concurrent_safety_maintained
```

#### Messaging Engine

**Purpose**: Testing message queues and event-driven communication.

**Test Coverage:**

- Message publishing and consumption
- Queue durability and persistence
- Message ordering and delivery guarantees
- Dead letter queue handling
- Message routing and filtering
- Pub/sub pattern validation

**Throughput Testing:**

```python
from flext.testing.engines.messaging_engine import MessagingEngine

engine = MessagingEngine()
results = await engine.test_message_throughput({
    "queue": "test-queue",
    "message_count": 1000,
    "concurrent_producers": 5,
    "concurrent_consumers": 3
})

# Analyze messaging performance
assert results.messages_processed == 1000
assert results.message_loss_rate == 0.0
assert results.average_processing_time < 10  # ms
```

### System-Level Testing Engines

#### Observability Engine

**Purpose**: Testing comprehensive system observability and monitoring.

**Test Coverage:**

- Distributed tracing validation
- Health check endpoints
- System resource monitoring
- Application performance monitoring
- Error tracking and alerting
- Service dependency mapping

**System Monitoring:**

```python
from flext.testing.engines.observability_engine import ObservabilityEngine

engine = ObservabilityEngine()
results = await engine.test_system_observability({
    "services": ["api", "database", "cache"],
    "trace_sampling": 0.1,
    "monitoring_duration": 300
})

# Verify observability coverage
assert results.trace_coverage > 0.95
assert results.health_checks_passing
assert len(results.detected_dependencies) >= 3
```

#### Runtime Engine

**Purpose**: Testing runtime environment and system behavior.

**Test Coverage:**

- Application startup and shutdown
- Resource utilization and limits
- Environment variable handling
- Process management and supervision
- System integration and compatibility
- Performance under load

**System Performance:**

```python
from flext.testing.engines.runtime_engine import RuntimeEngine

engine = RuntimeEngine()
results = await engine.test_system_performance({
    "load_pattern": "steady",
    "duration": 600,
    "target_rps": 100
})

# Validate system performance
assert results.sustained_target_rps
assert results.memory_usage_stable
assert results.cpu_usage < 80  # percent
```

### Comprehensive Testing Engine

**Purpose**: Orchestrating comprehensive testing across all system components.

**Test Coverage:**

- End-to-end workflow validation
- Cross-component integration testing
- System-wide performance testing
- Failure scenario and resilience testing
- Complete user journey validation
- System capacity and scalability testing

**Full System Test:**

```python
from flext.testing.engines.comprehensive_test_engine import ComprehensiveTestEngine

engine = ComprehensiveTestEngine()
results = await engine.run_comprehensive_test_suite({
    "test_scenarios": ["normal_load", "peak_load", "failure_recovery"],
    "duration": 1800,  # 30 minutes
    "coverage_threshold": 80
})

# Comprehensive validation
assert results.all_scenarios_passed
assert results.coverage_percentage >= 80
assert results.no_critical_failures
```

---

## Testing Adapters (Mocks)

### Mock Architecture

Testing adapters implement the same port contracts as production adapters while providing controllable, predictable behavior for testing scenarios.

### Core Testing Adapters

#### Database Adapter

In-memory database adapter for testing data persistence logic.

**Features:**

- SQL query simulation
- Transaction testing
- Connection pool simulation
- Database error scenario testing

**Usage:**

```python
from flext.testing.adapters.database import MockDatabaseAdapter

adapter = MockDatabaseAdapter()
await adapter.execute("INSERT INTO users (name) VALUES (?)", ["Test User"])
users = await adapter.fetch_all("SELECT * FROM users")

# Verify database operations
assert len(users) == 1
assert users[0]["name"] == "Test User"
```

#### Cache Adapter

In-memory cache implementation for testing cache-dependent functionality.

**Features:**

- TTL and expiration testing
- Cache miss/hit scenario simulation
- Memory-based storage (no external dependencies)
- Cache invalidation pattern testing

**TTL Testing:**

```python
from flext.testing.adapters.cache import MockCacheAdapter
import asyncio

adapter = MockCacheAdapter()
await adapter.set("key", "value", ttl=1)  # 1 second TTL

# Test immediate retrieval
value = await adapter.get("key")
assert value == "value"

# Test expiration
await asyncio.sleep(1.1)
expired_value = await adapter.get("key")
assert expired_value is None
```

#### HTTP Adapter

HTTP client adapter for testing external HTTP service integrations.

**Features:**

- HTTP method simulation (GET, POST, PUT, DELETE)
- Response status code control
- Header and payload validation
- Network error simulation

**Response Mocking:**

```python
from flext.testing.adapters.http import MockHttpAdapter

adapter = MockHttpAdapter()
adapter.set_response("GET", "/api/users", 200, {"users": []})
adapter.set_response("POST", "/api/users", 201, {"id": "123"})

# Test API interactions
users_response = await adapter.get("/api/users")
assert users_response.status_code == 200
assert users_response.json() == {"users": []}

create_response = await adapter.post("/api/users", json={"name": "Test"})
assert create_response.status_code == 201
```

#### Events Adapter

Event publishing and subscription testing adapter.

**Features:**

- Event publication simulation
- Subscription pattern testing
- Event ordering and timing validation
- Event handler testing

**Event Flow Testing:**

```python
from flext.testing.adapters.events import MockEventsAdapter

adapter = MockEventsAdapter()

# Setup event handler
events_received = []
async def event_handler(event_type, data):
    events_received.append((event_type, data))

adapter.subscribe("user.created", event_handler)

# Publish events
await adapter.publish("user.created", {"user_id": "123"})
await adapter.publish("user.created", {"user_id": "456"})

# Verify event handling
assert len(events_received) == 2
assert events_received[0][1]["user_id"] == "123"
```

---

## Advanced Testing Patterns

### Engine Composition

Combine multiple engines for comprehensive testing:

```python
class ApiIntegrationEngine(BaseTestEngine):
    def __init__(self):
        super().__init__()
        self.http_engine = HttpEngine()
        self.auth_engine = AuthenticationEngine()
        self.db_engine = DatabaseEngine()

    async def test_authenticated_api_flow(self):
        # Test authentication first
        auth_result = await self.auth_engine.test_user_login(credentials)
        assert auth_result.success

        # Use authenticated session for API calls
        api_result = await self.http_engine.test_with_auth(auth_result.token)
        assert api_result.authorized

        # Verify database state
        db_result = await self.db_engine.verify_data_consistency()
        assert db_result.consistent

        return self.aggregate_results([auth_result, api_result, db_result])
```

### Dependency Injection Testing

```python
from flext.application.container import ServiceContainer
from flext.ports.outbound.database import DatabasePort
from flext.testing.adapters.database import MockDatabaseAdapter

# Setup container with mock adapter
container = ServiceContainer()
mock_db = MockDatabaseAdapter()
container.bind(DatabasePort, mock_db)

# Service under test will receive mock adapter
service = container.resolve(UserService)

# Test service behavior
await service.create_user({"name": "Test User"})
assert mock_db.was_called_with("INSERT INTO users")
```

### Failure Simulation and Chaos Testing

```python
async def chaos_testing():
    orchestrator = TestOrchestrator()

    # Register all engines
    for engine_type in [DatabaseEngine, CacheEngine, HttpEngine]:
        orchestrator.register_engine(engine_type.__name__, engine_type())

    # Inject failures systematically
    failure_scenarios = [
        {"component": "database", "failure": "connection_timeout"},
        {"component": "cache", "failure": "memory_pressure"},
        {"component": "http", "failure": "network_partition"}
    ]

    for scenario in failure_scenarios:
        results = await orchestrator.execute_with_failure_injection(scenario)
        assert results.system_recovered, f"System failed to recover from {scenario}"
        assert results.recovery_time < 30  # seconds
```

### Performance Benchmarking

```python
async def performance_benchmark():
    engines = {
        "cache": CacheEngine(),
        "database": DatabaseEngine(),
        "http": HttpEngine()
    }

    results = {}
    for name, engine in engines.items():
        results[name] = await engine.run_performance_tests({
            "duration": 300,
            "load_pattern": "ramp_up",
            "success_threshold": 99.9
        })

    # Generate performance report
    report = generate_performance_report(results)
    assert report.overall_performance_acceptable
    return report
```

---

## Configuration and Setup

### Testing Configuration

Configure engines through YAML configuration files:

```yaml
# test_engines_config.yaml
testing:
  engines:
    database:
      connection_string: "postgresql://test:test@localhost/testdb"
      max_connections: 10
      timeout: 30

    cache:
      provider: "redis"
      host: "localhost"
      port: 6379
      max_memory: "100MB"

    http:
      timeout: 10
      retry_attempts: 3
      concurrent_requests: 50

    authentication:
      providers: ["local", "oauth2", "saml"]
      session_timeout: 3600

  orchestrator:
    parallel_execution: true
    max_concurrent_engines: 5
    cleanup_timeout: 60
    report_format: "json"
```

### Test Environment Setup

```python
import pytest
from flext.testing import TestEnvironment

@pytest.fixture(scope="session")
async def test_environment():
    """Setup comprehensive test environment."""
    env = TestEnvironment()

    # Configure adapters
    env.configure_adapter("database", MockDatabaseAdapter())
    env.configure_adapter("cache", MockCacheAdapter())
    env.configure_adapter("http", MockHttpAdapter())

    # Setup engines
    env.register_engine("auth", AuthenticationEngine())
    env.register_engine("db", DatabaseEngine())
    env.register_engine("http", HttpEngine())

    await env.initialize()
    yield env
    await env.cleanup()

@pytest.fixture
def user_service(test_environment):
    """Create user service with test dependencies."""
    return test_environment.create_service(UserService)
```

---

## Test Orchestration

### Test Orchestrator

The Test Orchestrator coordinates execution of multiple testing engines:

**Key Features:**

- Engine registration and lifecycle management
- Test execution scheduling and parallelization
- Result aggregation and reporting
- Dependency management between test engines
- Resource allocation and cleanup
- Test environment management

**Usage:**

```python
from flext.testing.engines.test_orchestrator import TestOrchestrator

orchestrator = TestOrchestrator()
orchestrator.register_engine("auth", AuthenticationEngine())
orchestrator.register_engine("db", DatabaseEngine())
orchestrator.register_engine("http", HttpEngine())

# Run all engines in coordinated fashion
results = await orchestrator.execute_test_suite({
    "parallel_execution": True,
    "timeout": 3600,
    "cleanup_on_failure": True
})

# Analyze comprehensive results
assert results.all_engines_successful
assert results.total_execution_time < 3600
```

### Error Handling and Recovery

**Engine-Level Error Handling:**

```python
try:
    results = await engine.run_tests(test_config)
except EngineException as e:
    logger.error(f"Engine failed: {e}")
    # Handle engine-specific failures
except TestTimeoutException as e:
    logger.error(f"Test timed out: {e}")
    # Handle timeout scenarios
```

**Orchestrator Error Handling:**

```python
# Graceful degradation with partial failures
results = await orchestrator.execute_with_error_tolerance({
    "max_failures": 2,
    "continue_on_error": True,
    "cleanup_on_failure": True
})

if results.has_failures():
    # Generate partial report
    report = results.generate_partial_report()
    # Take corrective action
```

---

## Best Practices

### 1. Consistent Port Contracts

Ensure testing adapters implement the exact same interface as production adapters:

```python
class MockDatabaseAdapter(DatabasePort):
    async def execute(self, query: str, params: list = None) -> None:
        # Mock implementation matching production interface
        self._validate_query(query)
        self._record_call("execute", query, params)
        return self._execute_mock_query(query, params)
```

### 2. Predictable Behavior

Make test outcomes deterministic:

```python
# Good: Predictable responses
mock_api.set_response("/users", [{"id": "1", "name": "Test"}])

# Avoid: Random or time-dependent responses
# mock_api.set_random_response("/users")  # Don't do this
```

### 3. State Isolation

Reset adapter state between tests:

```python
@pytest.fixture
def mock_cache():
    adapter = MockCacheAdapter()
    yield adapter
    adapter.clear()  # Reset state after test
```

### 4. Realistic Error Simulation

Test edge cases and error scenarios:

```python
# Test timeout scenarios
mock_http.set_timeout("/slow-endpoint", 5.0)

# Test network failures
mock_http.set_network_error("/unreliable-service")

# Test partial failures
mock_db.set_intermittent_failure(failure_rate=0.1)
```

---

## Performance Considerations

- **Parallel Execution**: Engines support parallel test execution for improved performance
- **Resource Management**: Automatic cleanup and resource management to prevent test interference
- **Caching**: Test results and setup data are cached to reduce execution time
- **Batching**: Test operations are batched where possible to improve efficiency
- **In-Memory Storage**: Mock adapters use in-memory storage for fast test execution

---

## Integration with CI/CD

### GitHub Actions Integration

```yaml
name: Comprehensive Testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.13"

      - name: Run Comprehensive Tests
        run: |
          python -m pytest tests/ --cov=src/ --cov-report=xml
          python -m flext.testing.orchestrator --config=test_config.yaml

      - name: Generate Test Report
        run: |
          python -m flext.testing.reporting --output=test_report.html
```

### Test Reporting

```python
from flext.testing.reporting import TestReportGenerator

generator = TestReportGenerator()
report = await generator.generate_comprehensive_report({
    "engines": engine_results,
    "adapters": adapter_metrics,
    "coverage": coverage_data,
    "performance": performance_metrics
})

# Export in multiple formats
await report.export_html("test_report.html")
await report.export_json("test_results.json")
await report.export_junit("junit.xml")
```

---

## Related Documentation

### Framework Testing

- [Testing Hexagonal Architecture](./TESTING_HEXAGONAL_ARCHITECTURE.md) - Architectural testing patterns
- [Core API Reference](../api-reference/core-api-reference.md) - Testing APIs and interfaces

### Development

- [Development Standards](./standardization-plan.md) - Code quality and testing standards
- [Environment Configuration](./environment-configuration-guide.md) - Test environment setup

### Integration

- [Oracle Integration Guide](../guides/oracle-integration-comprehensive-guide.md) - Testing Oracle integrations
- [Performance Optimization](../optimization/comprehensive-optimization-guide.md) - Performance testing strategies

---

**Testing Framework Status**: ✅ **Production Ready**
**Coverage**: **Comprehensive** - All framework components
**Performance**: **Optimized** - Parallel execution and caching
**Integration**: **Complete** - CI/CD and reporting integration
