# FLEXT Testing Adapters

Mock and stub implementations for testing infrastructure components in the FLEXT hexagonal architecture framework.

## Overview

This module provides comprehensive testing adapters that implement the same port contracts as their production counterparts, enabling isolated unit testing and integration testing without external dependencies.

## Architecture

The testing adapters follow the **Ports and Adapters** pattern, implementing the same outbound port interfaces as production adapters while providing controllable, predictable behavior for testing scenarios.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Test Cases    │◄───┤ Testing Adapters ├───►│   Port Contracts│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Predictable Data │
                    │ & Behavior       │
                    └──────────────────┘
```

## Available Testing Adapters

### Analytics Adapter (`analytics.py`)

Mock implementation for analytics and metrics collection.

**Features:**

- Event tracking simulation
- Metrics aggregation testing
- Performance measurement validation
- Custom analytics pipeline testing

**Usage:**

```python
from flext.testing.adapters.analytics import MockAnalyticsAdapter

adapter = MockAnalyticsAdapter()
await adapter.track_event("user_action", {"user_id": "123"})
metrics = adapter.get_collected_metrics()
```

### API Adapter (`api.py`)

Mock HTTP API client for testing external service integrations.

**Features:**

- Configurable response simulation
- Request validation and recording
- Network failure simulation
- Rate limiting and timeout testing

**Usage:**

```python
from flext.testing.adapters.api import MockApiAdapter

adapter = MockApiAdapter()
adapter.set_response("/users/123", {"id": "123", "name": "Test User"})
response = await adapter.get("/users/123")
```

### Cache Adapter (`cache.py`)

In-memory cache implementation for testing cache-dependent functionality.

**Features:**

- TTL and expiration testing
- Cache miss/hit scenario simulation
- Memory-based storage (no external dependencies)
- Cache invalidation pattern testing

**Usage:**

```python
from flext.testing.adapters.cache import MockCacheAdapter

adapter = MockCacheAdapter()
await adapter.set("key", "value", ttl=60)
value = await adapter.get("key")
```

### CLI Adapter (`cli.py`)

Mock command-line interface for testing CLI interactions.

**Features:**

- Command execution simulation
- Argument parsing validation
- Output capturing and verification
- Error scenario simulation

**Usage:**

```python
from flext.testing.adapters.cli import MockCliAdapter

adapter = MockCliAdapter()
adapter.set_command_result("status", 0, "All systems operational")
result = adapter.execute("status")
```

### Database Adapter (`database.py`)

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
```

### Events Adapter (`events.py`)

Event publishing and subscription testing adapter.

**Features:**

- Event publication simulation
- Subscription pattern testing
- Event ordering and timing validation
- Event handler testing

**Usage:**

```python
from flext.testing.adapters.events import MockEventsAdapter

adapter = MockEventsAdapter()
await adapter.publish("user.created", {"user_id": "123"})
events = adapter.get_published_events()
```

### HTTP Adapter (`http.py`)

HTTP client adapter for testing external HTTP service integrations.

**Features:**

- HTTP method simulation (GET, POST, PUT, DELETE)
- Response status code control
- Header and payload validation
- Network error simulation

**Usage:**

```python
from flext.testing.adapters.http import MockHttpAdapter

adapter = MockHttpAdapter()
adapter.set_response("GET", "/api/users", 200, {"users": []})
response = await adapter.get("/api/users")
```

### Logging Adapter (`logging.py`)

Logging adapter for testing log output and levels.

**Features:**

- Log level filtering testing
- Log message validation
- Log formatting testing
- Structured logging verification

**Usage:**

```python
from flext.testing.adapters.logging import MockLoggingAdapter

adapter = MockLoggingAdapter()
adapter.info("Test message", extra={"user_id": "123"})
logs = adapter.get_captured_logs()
```

## Testing Patterns

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
```

### Behavior Verification

```python
# Arrange
mock_api = MockApiAdapter()
service = ExternalDataService(api=mock_api)

# Act
await service.fetch_user_data("123")

# Assert
assert mock_api.was_called_with("GET", "/users/123")
assert mock_api.call_count == 1
```

### Error Scenario Testing

```python
# Setup error scenario
mock_db = MockDatabaseAdapter()
mock_db.set_error("connection_lost")

# Test error handling
with pytest.raises(DatabaseConnectionError):
    await service.save_user(user_data)
```

### State Verification

```python
# Test state changes
mock_cache = MockCacheAdapter()
await service.update_user_preferences(user_id, preferences)

# Verify cache was updated
cached_prefs = await mock_cache.get(f"user:{user_id}:preferences")
assert cached_prefs == preferences
```

## Integration with Testing Engines

These adapters integrate seamlessly with the FLEXT testing engines:

```python
from flext.testing.engines import ComprehensiveTestEngine

engine = ComprehensiveTestEngine()
engine.register_adapter("database", MockDatabaseAdapter())
engine.register_adapter("cache", MockCacheAdapter())

# Run comprehensive tests with mock adapters
results = await engine.run_test_suite()
```

## Best Practices

### 1. Consistent Port Contracts

Ensure testing adapters implement the exact same interface as production adapters:

```python
class MockDatabaseAdapter(DatabasePort):
    async def execute(self, query: str, params: list = None) -> None:
        # Mock implementation matching production interface
        pass
```

### 2. Predictable Behavior

Make test outcomes deterministic:

```python
# Good: Predictable responses
mock_api.set_response("/users", [{"id": "1", "name": "Test"}])

# Avoid: Random or time-dependent responses
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
```

## Configuration

Testing adapters can be configured through environment variables or test configuration:

```yaml
# test_config.yaml
testing:
  adapters:
    database:
      type: "mock"
      initial_data: "fixtures/test_data.sql"
    cache:
      type: "memory"
      max_size: 1000
```

## Performance Considerations

- In-memory implementations for fast test execution
- Minimal overhead for high-frequency operations
- State tracking without persistence for speed
- Configurable delays for timing-sensitive tests

## TODO Items

- [ ] Add support for distributed system simulation
- [ ] Implement advanced failure scenario patterns
- [ ] Add performance profiling capabilities
- [ ] Create adapter behavior recording and playback
- [ ] Enhance error injection mechanisms

## Related Documentation

- [Testing Engines](../engines/README.md) - Test orchestration and execution
- [Core Testing](../../core/README.md) - Domain layer testing patterns
- [Integration Testing](../../../tests/integration/README.md) - Integration test strategies
