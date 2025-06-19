# FLX Testing Framework - Complete Documentation Hub

> **Comprehensive testing documentation for FLX hexagonal architecture applications**
>
> **Cross-References:**
>
> - [Testing Hexagonal Architecture](./TESTING_HEXAGONAL_ARCHITECTURE.md) - Architectural testing patterns
> - [Core API Reference](../api-reference/core-api-reference.md) - Testing APIs and interfaces
> - [Testing Structure Guide](./testing-structure.md) - Test organization patterns

## Documentation Navigation

This hub organizes all FLX testing documentation into logical sections. Each specialized guide provides detailed coverage of specific testing aspects while maintaining cross-references to related topics.

### 🧪 **Core Testing Framework**

- **[Testing Framework Overview](#framework-overview)** - Core concepts and architecture
- **[Testing Engines](./testing-engines.md)** - Specialized test execution engines
- **[Testing Adapters](./testing-adapters.md)** - Mock implementations and stubs
- **[Hexagonal Testing Patterns](./hexagonal-testing-guide.md)** - Architecture-specific testing

### 🎯 **Testing by Scope**

- **[Unit Testing Guide](./unit-testing-guide.md)** - Component isolation testing
- **[Integration Testing Guide](./integration-testing-guide.md)** - Component interaction testing
- **[End-to-End Testing Guide](./e2e-testing-guide.md)** - Complete workflow testing

### 🏗️ **Testing by Architecture Layer**

- **[Core Domain Testing](./core-testing.md)** - Domain logic testing
- **[Ports Testing](./ports-testing.md)** - Port contract testing
- **[Adapters Testing](./adapters-testing.md)** - Adapter implementation testing
- **[Infrastructure Testing](./infrastructure-testing.md)** - Infrastructure layer testing

### 🔗 **Integration-Specific Testing**

- **[FLX-WMS E2E Testing](./flx-wms-e2e-testing.md)** - Oracle WMS integration testing
- **[FLX-OIC E2E Testing](./flx-oic-e2e-testing.md)** - Oracle OIC integration testing

### 📊 **Testing Analysis & Reports**

- **[Test Coverage Analysis](./reports/test-coverage-analysis.md)** - Coverage metrics and analysis

---

## Framework Overview

The FLX Testing Framework provides a comprehensive testing infrastructure specifically designed for hexagonal architecture applications. It offers specialized testing engines, adapter mocks, and utilities that understand the unique patterns and requirements of port-adapter architecture.

### Architecture Principles

#### Testing Hexagonal Architecture

- **Port Testing**: Test inbound and outbound port contracts independently
- **Adapter Testing**: Test adapter implementations against port interfaces
- **Domain Isolation**: Test domain logic without external dependencies
- **Integration Testing**: Test complete workflows through the hexagon
- **Contract Testing**: Ensure adapters conform to port specifications

#### Testing Strategies

- **Unit Testing**: Isolated testing of individual components
- **Integration Testing**: Testing component interactions
- **End-to-End Testing**: Complete workflow testing
- **Contract Testing**: Interface compliance verification

### Framework Architecture

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
│ • HttpClient        │ • FileSystem       │ • Workflow          │
│ • Logger            │ • MessageQueue     │ • Oracle Systems   │
└─────────────────────┴─────────────────────┴─────────────────────┘
           │                      │                      │
           ▼                      ▼                      ▼
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ Testing Adapters    │ Infrastructure      │ Integration         │
│ • Mock Auth         │ Adapters           │ Test Suites        │
│ • Mock Cache        │ • Test Database    │ • WMS E2E Tests     │
│ • Mock HTTP         │ • Mock FileSystem  │ • OIC E2E Tests     │
│ • Mock Logger       │ • Mock MQ          │ • Full Workflows    │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

## Quick Start

### Basic Test Setup

```python
from flx.testing import DeclarativeTestEngine, create_test_engine
from flx.testing.adapters import MockHttpAdapter, MockDatabaseAdapter

# Create test engine with mock adapters
engine = create_test_engine({
    'http_adapter': MockHttpAdapter(),
    'database_adapter': MockDatabaseAdapter()
})

# Run tests
async def test_basic_workflow():
    result = await engine.run_test_scenario('basic_entity_creation')
    assert result.success
```

### Advanced Testing Patterns

```python
from flx.testing import TestOrchestrator
from flx.testing.engines import (
    ComponentTestEngine,
    InfrastructureTestEngine,
    IntegrationTestEngine
)

# Orchestrate multiple testing engines
orchestrator = TestOrchestrator([
    ComponentTestEngine(),
    InfrastructureTestEngine(),
    IntegrationTestEngine()
])

# Run comprehensive test suite
results = await orchestrator.run_all_tests()
```

## Testing Engine Categories

### Component Engines

Focused on testing individual framework components:

- **AuthenticationEngine**: Tests authentication flows and security
- **CacheEngine**: Tests caching mechanisms and invalidation
- **HttpClientEngine**: Tests HTTP communication patterns
- **LoggerEngine**: Tests logging functionality and formats

### Infrastructure Engines

Focused on testing infrastructure layer components:

- **DatabaseEngine**: Tests database operations and transactions
- **FileSystemEngine**: Tests file operations and storage
- **MessageQueueEngine**: Tests message handling and queues

### Integration Engines

Focused on testing complete system integrations:

- **ComprehensiveEngine**: Full system workflow testing
- **WorkflowEngine**: Business process testing
- **OracleIntegrationEngine**: Oracle systems integration testing

## Testing Adapter Categories

### Mock Adapters

Implement the same port contracts as production adapters while providing controllable, predictable behavior for testing scenarios:

```python
# Example mock adapter implementation
class MockHttpAdapter(HttpPort):
    """Mock HTTP adapter for testing"""

    def __init__(self):
        self.responses = {}
        self.requests = []

    async def get(self, url: str) -> HttpResponse:
        self.requests.append(('GET', url))
        return self.responses.get(url, HttpResponse(status=200, data={}))

    def setup_response(self, url: str, response: HttpResponse):
        """Configure mock response for testing"""
        self.responses[url] = response
```

### Infrastructure Test Adapters

Specialized adapters for infrastructure testing:

- **TestDatabaseAdapter**: In-memory database for testing
- **MockFileSystemAdapter**: Virtual file system for testing
- **MockMessageQueueAdapter**: In-memory message queue for testing

## Best Practices

### Test Organization

- Organize tests by architectural layer (domain, application, infrastructure)
- Use descriptive test names that explain business scenarios
- Group related tests in test classes or modules
- Maintain clear separation between unit, integration, and E2E tests

### Mock Management

- Use dependency injection to provide mock adapters
- Configure mocks at the beginning of each test
- Reset mock state between tests
- Verify mock interactions when testing integration points

### Test Data Management

- Use factories for creating test data
- Maintain test data isolation between tests
- Use realistic but safe test data
- Clean up test data after test execution

## Integration with Development Workflow

### Continuous Integration

```yaml
# Example CI configuration for testing
test_pipeline:
  unit_tests:
    - pytest tests/unit/ -v
  integration_tests:
    - pytest tests/integration/ -v
  e2e_tests:
    - pytest tests/e2e/ -v
  coverage:
    - pytest --cov=flx tests/ --cov-report=html
```

### Development Commands

```bash
# Run all tests
make test

# Run specific test categories
make test-unit
make test-integration
make test-e2e

# Run tests with coverage
make test-coverage

# Run specific test engine
pytest -k "test_authentication_engine"
```

## Advanced Topics

### Custom Test Engines

Learn how to create custom test engines for specific testing scenarios:

- [Creating Custom Test Engines](./testing-engines.md#custom-engines)
- [Engine Configuration Patterns](./testing-engines.md#configuration)

### Performance Testing

Specialized approaches for testing performance in hexagonal architecture:

- [Performance Testing Strategies](./testing-framework.md#performance-testing)
- [Load Testing with Mock Adapters](./testing-adapters.md#load-testing)

### Oracle Integration Testing

Comprehensive testing approaches for Oracle system integrations:

- [WMS Integration Testing](./flx-wms-e2e-testing.md)
- [OIC Integration Testing](./flx-oic-e2e-testing.md)

## Troubleshooting

### Common Testing Issues

- **Mock Configuration**: Ensure mocks are properly configured before test execution
- **Test Isolation**: Verify tests don't share state or dependencies
- **Async Testing**: Use proper async/await patterns in test code
- **Resource Cleanup**: Ensure proper cleanup of test resources

### Debugging Test Failures

- Use verbose test output to understand failure context
- Check mock interaction logs for integration issues
- Verify test data setup and teardown procedures
- Use debugging tools to step through test execution

## Related Documentation

### Framework Documentation

- [FLX Core Framework](../architecture/core-domain-layer.md)
- [Hexagonal Architecture](../architecture/hexagonal-architecture-guide.md)
- [Adapter Implementation](../architecture/adapters-implementation-guide.md)

### Development Guides

- [Development Workflow](./standardization-plan.md)
- [Code Quality Standards](./documentation-standards.md)
- [API Reference](../api-reference/)

---

**This hub provides comprehensive access to all FLX testing documentation while preserving the specialized focus of individual guides. Each linked document provides detailed coverage of specific testing aspects, ensuring no valuable information is lost while improving overall organization and accessibility.**
