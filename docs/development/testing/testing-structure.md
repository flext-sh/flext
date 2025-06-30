# FLEXT Test Suite - Comprehensive Testing Framework

Enterprise-grade test suite for the FLEXT framework following hexagonal architecture principles, domain-driven design patterns, and modern testing best practices.

## 🧪 Testing Philosophy

The FLEXT test suite embodies:

- **Hexagonal Architecture Testing**: Clear separation between domain logic, ports, and adapters
- **Test Pyramid Compliance**: Strong foundation of unit tests, selective integration tests, minimal E2E tests
- **Domain-Driven Testing**: Tests that reflect business requirements and domain language
- **Behavior-Driven Development**: Tests that describe system behavior from user perspective
- **Production Readiness**: Tests that validate production scenarios and edge cases

## 📁 Test Structure & Organization

```
tests/
├── unit/              # Fast, isolated tests for individual components
│   ├── core/          # Domain layer: entities, value objects, services
│   ├── application/   # Application services and command/query handlers
│   ├── adapters/      # Adapter implementations with mocked dependencies
│   ├── ports/         # Port interface contracts and specifications
│   ├── infra/         # Infrastructure services and utilities
│   └── infrastructure/ # Legacy infrastructure tests (being migrated)
├── integration/       # Component interaction and boundary testing
│   ├── test_adapter_port_integration.py    # Port-adapter contracts
│   ├── test_application_integration.py     # Application service orchestration
│   ├── test_infrastructure_integration.py  # Infrastructure component coordination
│   └── test_logging_integration.py         # Logging system integration
├── e2e/              # End-to-end user workflow validation
│   └── test_logging_e2e.py                # Complete logging workflow
├── hexagonal/        # Hexagonal architecture compliance testing
│   ├── test_architecture_boundaries.py     # Architectural boundary enforcement
│   ├── test_dependency_injection.py        # DI container validation
│   ├── test_e2e_hexagonal_flow.py         # Complete hexagonal flow testing
│   ├── test_adapter_implementation.py      # Adapter compliance testing
│   └── test_port_contracts.py             # Port contract validation
├── conftest.py       # Central pytest configuration and shared fixtures
├── conftest_original.py  # Legacy configuration (being phased out)
├── conftest_simple.py   # Simplified configuration for specific test contexts
└── pytest_logging.ini  # Logging configuration for test runs
```

## 🎯 Test Categories & Coverage

### Unit Tests (`unit/`) - Foundation Layer

**Purpose**: Test individual components in complete isolation
**Coverage Target**: >95% code coverage
**Execution Time**: <2 seconds total

#### Core Domain Tests (`unit/core/`)

- **`test_base.py`**: Core architectural patterns and mixins
  - Domain object immutability and equality
  - Identifiable entity patterns
  - Timestamped and versionable behaviors
  - Advanced architecture pattern validation
- **`test_entities.py`**: Entity and aggregate root behavior
  - Entity lifecycle management
  - Aggregate root event handling
  - Business logic enforcement
  - Version increment validation
- **`test_events.py`**: Domain event system validation
  - Event creation and immutability
  - Event type name generation
  - Event serialization/deserialization
  - FLEXT domain event extensions
- **`test_logging.py`**: Logging system core functionality
  - FlextLogLevel enumeration and ordering
  - FlextLogger synchronous/asynchronous patterns
  - Structured logging with metadata
- **`test_value_objects.py`**: Value object implementations
  - Immutability and equality enforcement
  - Complex value objects (Email, Money, Address)
  - Validation and business rule enforcement

#### Application Layer Tests (`unit/application/`)

- **Container & DI Tests**: Service container and dependency injection
- **Service Tests**: Application service orchestration
- **Command/Query Handlers**: CQRS pattern implementation

#### Infrastructure Tests (`unit/infra/`)

- **Configuration**: Hierarchical configuration management
- **Caching**: Multi-level caching strategies
- **Database**: Repository pattern implementations
- **Messaging**: Event bus and message handling
- **Observability**: Metrics, health checks, and monitoring

### Integration Tests (`integration/`) - Interaction Layer

**Purpose**: Test component interactions and boundary compliance
**Coverage Target**: >85% integration scenario coverage
**Execution Time**: <30 seconds total

#### Key Integration Scenarios

- **Port-Adapter Integration**: Validates that adapters correctly implement port contracts
- **Application Service Integration**: Tests complete application service orchestration
- **Infrastructure Integration**: Validates infrastructure component coordination
- **Logging Integration**: End-to-end logging system validation

### End-to-End Tests (`e2e/`) - System Layer

**Purpose**: Test complete user workflows and system behavior
**Coverage Target**: >90% critical user journey coverage
**Execution Time**: <2 minutes total

#### User Workflow Validation

- **Logging E2E**: Complete logging workflow from domain events to infrastructure
- **CLI Commands**: Command-line interface interaction testing
- **API Endpoints**: HTTP API request/response validation

### Hexagonal Architecture Tests (`hexagonal/`) - Architectural Compliance

**Purpose**: Enforce hexagonal architecture principles and boundaries
**Coverage Target**: 100% architectural rule compliance

#### Architectural Validation

- **Boundary Enforcement**: Validates clean separation between layers
- **Dependency Direction**: Ensures dependencies point inward toward domain
- **Port Contract Compliance**: Validates all adapters implement port contracts
- **Adapter Implementation**: Tests adapter behavior and lifecycle

## 🚀 Running Tests

### Basic Test Execution

```bash
# Run all tests with coverage
make test

# Run all tests with detailed output
pytest -v

# Run specific test categories
pytest tests/unit                    # Unit tests only
pytest tests/integration            # Integration tests only
pytest tests/e2e                   # End-to-end tests only
pytest tests/hexagonal             # Architecture compliance tests

# Run specific test files
pytest tests/unit/core/test_entities.py
pytest tests/integration/test_logging_integration.py
```

### Advanced Test Execution

```bash
# Run with coverage reporting
pytest --cov=flext --cov-report=html --cov-report=term-missing

# Run specific test methods
pytest tests/unit/core/test_entities.py::TestEntity::test_entity_creation
pytest tests/unit/core/test_base.py::TestAdvancedArchitecturePatterns::test_event_driven_architecture_pattern

# Run tests matching pattern
pytest -k "test_entity"
pytest -k "test_logging and not slow"

# Run with markers
pytest -m "not slow"               # Skip slow tests
pytest -m "integration"           # Only integration tests
pytest -m "hexagonal"            # Only architecture tests

# Parallel test execution
pytest -n auto                   # Auto-detect CPU cores
pytest -n 4                     # Use 4 worker processes

# Debug mode
pytest -s                       # Don't capture output
pytest --pdb                   # Drop into debugger on failure
pytest --pdbcls=IPython.terminal.debugger:Pdb  # Use IPython debugger
```

### Performance Testing

```bash
# Profile test execution time
pytest --durations=10            # Show 10 slowest tests
pytest --durations=0            # Show all test durations

# Memory profiling
pytest --profile-svg            # Generate memory profile

# Benchmark specific functionality
pytest tests/unit/core/test_entities.py --benchmark-only
```

## 🏗️ Test Fixtures & Infrastructure

### Core Fixtures (`conftest.py`)

```python
@pytest.fixture(scope="session")
async def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def flext_application():
    """Create test FLEXT application with all adapters."""
    app = FlextApplication(
        name="test-app",
        config=TestConfig(),
        adapters=[
            TestHttpAdapter(),
            TestDatabaseAdapter(),
            TestCacheAdapter()
        ]
    )
    await app.initialize()
    yield app
    await app.cleanup()

@pytest.fixture
async def service_container():
    """Create dependency injection container for tests."""
    container = ServiceContainer()
    container.initialize()

    # Register test services
    container.register_singleton(ILogger, TestLogger())
    container.register_service(ICache, InMemoryCache)
    container.register_factory(IDatabase, lambda: TestDatabase())

    yield container
    await container.cleanup()

@pytest.fixture
def mock_adapters(mocker):
    """Create mock adapters for isolated testing."""
    return {
        'http': mocker.Mock(spec=HttpAdapter),
        'database': mocker.Mock(spec=DatabaseAdapter),
        'cache': mocker.Mock(spec=CacheAdapter),
        'events': mocker.Mock(spec=EventAdapter)
    }
```

### Domain Testing Fixtures

```python
@pytest.fixture
def sample_user_entity():
    """Create sample user entity for testing."""
    return User(
        username="test_user",
        email=Email("test@example.com"),
        profile=UserProfile(
            first_name="Test",
            last_name="User",
            birth_date=date(1990, 1, 1)
        )
    )

@pytest.fixture
def sample_domain_events():
    """Create sample domain events for testing."""
    return [
        UserRegisteredEvent(
            aggregate_id=uuid4(),
            username="test_user",
            email="test@example.com"
        ),
        UserProfileUpdatedEvent(
            aggregate_id=uuid4(),
            profile_changes={"first_name": "Updated"}
        )
    ]
```

## 🧪 Testing Patterns & Best Practices

### Domain Logic Testing

```python
class TestUserEntity:
    """Test user entity behavior and business rules."""

    def test_user_creation_with_valid_data(self):
        """Test that user can be created with valid data."""
        user = User(
            username="john_doe",
            email=Email("john@example.com")
        )

        assert user.username == "john_doe"
        assert isinstance(user.email, Email)
        assert user.email.value == "john@example.com"
        assert user.is_active is True  # Default state

    def test_user_email_validation(self):
        """Test that invalid email raises validation error."""
        with pytest.raises(ValidationError, match="Invalid email format"):
            User(
                username="john_doe",
                email=Email("invalid-email")
            )

    def test_user_deactivation_business_rule(self):
        """Test user deactivation business logic."""
        user = User(username="john_doe", email=Email("john@example.com"))

        # Business rule: User must be active to deactivate
        user.deactivate(reason="Account suspended")

        assert user.is_active is False
        assert user.deactivation_reason == "Account suspended"
        assert user.deactivated_at is not None
```

### Async Testing Patterns

```python
class TestAsyncRepository:
    """Test async repository patterns."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_user(self, db_session):
        """Test saving and retrieving user from repository."""
        repo = SqlUserRepository(db_session)
        user = User(username="test", email=Email("test@example.com"))

        # Save user
        await repo.save(user)

        # Retrieve user
        found_user = await repo.get_by_id(user.id)

        assert found_user is not None
        assert found_user.username == user.username
        assert found_user.email == user.email

    @pytest.mark.asyncio
    async def test_repository_transaction_rollback(self, db_session):
        """Test repository transaction rollback on error."""
        repo = SqlUserRepository(db_session)

        with pytest.raises(BusinessRuleViolationError):
            async with repo.unit_of_work() as uow:
                user = User(username="test", email=Email("test@example.com"))
                await repo.save(user)

                # Simulate business rule violation
                raise BusinessRuleViolationError("Test error")

        # Verify rollback - user should not exist
        found_user = await repo.get_by_username("test")
        assert found_user is None
```

### Mock Testing Patterns

```python
class TestCommandHandlers:
    """Test command handlers with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_create_user_command_success(self, mocker):
        """Test successful user creation command."""
        # Setup mocks
        mock_repo = mocker.Mock(spec=UserRepository)
        mock_event_bus = mocker.Mock(spec=EventBus)
        mock_logger = mocker.Mock(spec=FlextLogger)

        # Configure mock behavior
        mock_repo.get_by_username.return_value = None  # User doesn't exist
        mock_repo.save.return_value = None
        mock_event_bus.publish.return_value = None

        # Create handler with mocked dependencies
        handler = CreateUserCommandHandler(
            user_repo=mock_repo,
            event_bus=mock_event_bus,
            logger=mock_logger
        )

        # Execute command
        command = CreateUserCommand(
            username="john_doe",
            email="john@example.com"
        )
        result = await handler.handle(command)

        # Verify behavior
        assert result.success is True
        assert result.user_id is not None

        # Verify interactions
        mock_repo.get_by_username.assert_called_once_with("john_doe")
        mock_repo.save.assert_called_once()
        mock_event_bus.publish.assert_called_once()

        # Verify event was published
        published_event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(published_event, UserCreatedEvent)
        assert published_event.username == "john_doe"
```

### Integration Testing Patterns

```python
class TestUserServiceIntegration:
    """Test user service with real database integration."""

    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(
        self,
        flext_application,
        db_session
    ):
        """Test complete user registration with all components."""
        # Get services from container
        user_service = flext_application.get_service(UserService)
        event_bus = flext_application.get_service(EventBus)

        # Setup event handler to capture events
        captured_events = []

        async def capture_event(event):
            captured_events.append(event)

        await event_bus.subscribe(UserCreatedEvent, capture_event)

        # Execute registration
        result = await user_service.register_user(
            username="integration_test",
            email="integration@example.com",
            password="secure_password"
        )

        # Verify result
        assert result.success is True
        assert result.user_id is not None

        # Verify user was persisted
        user_repo = flext_application.get_service(UserRepository)
        saved_user = await user_repo.get_by_id(result.user_id)
        assert saved_user is not None
        assert saved_user.username == "integration_test"

        # Verify event was published
        assert len(captured_events) == 1
        assert isinstance(captured_events[0], UserCreatedEvent)
```

## ⚙️ Test Configuration

### pytest.ini Configuration

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --maxfail=1
filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning:.*aiohttp.*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    hexagonal: marks tests as hexagonal architecture tests
    unit: marks tests as unit tests
    redis: requires redis server
    postgres: requires postgresql database
    external: requires external services
    performance: performance and load tests
```

### Coverage Configuration (.coveragerc)

```ini
[run]
source = src/flext
omit =
    */tests/*
    */migrations/*
    */test_*.py
    */__pycache__/*
    */venv/*
    */site-packages/*
branch = True
parallel = True

[report]
# Regexes for lines to exclude from consideration
exclude_lines =
    pragma: no cover
    def __repr__
    def __str__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

show_missing = True
skip_covered = False
precision = 2

[html]
directory = reports/coverage

[xml]
output = reports/coverage.xml
```

## 📊 Test Quality Metrics

### Coverage Targets

- **Unit Tests**: >95% line coverage, >90% branch coverage
- **Integration Tests**: >85% integration scenario coverage
- **E2E Tests**: >90% critical user journey coverage
- **Overall Project**: >92% combined coverage

### Performance Targets

- **Unit Test Suite**: <5 seconds execution time
- **Integration Test Suite**: <30 seconds execution time
- **E2E Test Suite**: <2 minutes execution time
- **Full Test Suite**: <3 minutes execution time

### Quality Gates

- All tests must pass before merge
- Coverage must not decrease
- No new linting violations
- Performance degradation <5%

## 🔧 Test Utilities & Helpers

### Test Data Builders

```python
class UserBuilder:
    """Builder pattern for creating test users."""

    def __init__(self):
        self.reset()

    def reset(self):
        self._username = "test_user"
        self._email = "test@example.com"
        self._active = True
        return self

    def with_username(self, username: str):
        self._username = username
        return self

    def with_email(self, email: str):
        self._email = email
        return self

    def inactive(self):
        self._active = False
        return self

    def build(self) -> User:
        user = User(
            username=self._username,
            email=Email(self._email)
        )
        if not self._active:
            user.deactivate("Test deactivation")
        return user

# Usage in tests
def test_user_builder():
    user = (UserBuilder()
           .with_username("john_doe")
           .with_email("john@example.com")
           .inactive()
           .build())

    assert user.username == "john_doe"
    assert not user.is_active
```

### Test Assertions

```python
def assert_user_equals(expected: User, actual: User):
    """Custom assertion for user equality."""
    assert actual.username == expected.username
    assert actual.email == expected.email
    assert actual.is_active == expected.is_active

def assert_event_published(event_bus_mock, event_type: Type[DomainEvent]):
    """Assert that specific event type was published."""
    published_events = [
        call.args[0] for call in event_bus_mock.publish.call_args_list
    ]
    assert any(isinstance(event, event_type) for event in published_events)
```

## 🏆 Testing Best Practices

### Code Quality Standards

1. **Test Naming**: Use descriptive names that explain the scenario

   - ✅ `test_user_registration_with_duplicate_username_raises_error`
   - ❌ `test_user_error`

2. **Test Structure**: Follow Arrange-Act-Assert pattern

   ```python
   def test_user_deactivation():
       # Arrange
       user = User(username="test", email=Email("test@example.com"))

       # Act
       user.deactivate("Account suspended")

       # Assert
       assert not user.is_active
       assert user.deactivation_reason == "Account suspended"
   ```

3. **Test Independence**: Each test should be completely independent
4. **Single Responsibility**: Each test should verify one behavior
5. **Fast Execution**: Use in-memory implementations for speed
6. **Deterministic**: Tests should produce consistent results

### Architectural Testing Guidelines

1. **Layer Isolation**: Test each layer independently
2. **Contract Testing**: Verify port-adapter contracts
3. **Boundary Testing**: Test architectural boundaries
4. **Dependency Direction**: Validate dependency flow

### Performance Testing Standards

1. **Execution Time**: Keep individual tests under 100ms
2. **Resource Usage**: Monitor memory and CPU usage
3. **Concurrency**: Test concurrent access patterns
4. **Load Testing**: Validate system under stress

## 📚 Related Documentation

- [Hexagonal Architecture Testing Guide](./hexagonal/README.md)
- [Domain Testing Patterns](./unit/core/README.md)
- [Integration Testing Strategies](./integration/README.md)
- [E2E Testing Framework](./e2e/README.md)
- [Test Configuration Guide](./conftest.py)

The FLEXT test suite provides comprehensive validation of the framework's hexagonal architecture, ensuring production-ready quality and architectural compliance through systematic testing at all levels.
