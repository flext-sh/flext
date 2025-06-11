# 🧪 FLX Unit Testing Guide

> **Function**: Foundation-level testing for individual components | **Audience**: Developers, test engineers | **Status**: Production-Ready

[![Testing](https://img.shields.io/badge/testing-unit-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](../../architecture/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Comprehensive unit testing guide for FLX hexagonal architecture components with isolation patterns, mocking strategies, and domain-driven testing principles**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Section**: [Testing](./index.md) → **📄 Current**: Unit Testing Guide

### **📍 Learning Path Position**

```
[Testing Hub](./index.md) → [Comprehensive Testing](./testing-comprehensive-guide.md) → **[Unit Testing Guide]** → [Integration Testing](./integration-testing-guide.md)
```

Foundational testing guide focusing on individual component isolation, fast execution, and comprehensive coverage of domain logic, adapters, and infrastructure components.

## Unit Testing Philosophy

FLX unit testing embodies:

- **Complete Isolation**: Each component tested independently with mocked dependencies
- **Fast Execution**: Tests run in <100ms each, full suite in <5 seconds
- **Domain Focus**: Business logic validation without infrastructure concerns
- **Behavioral Testing**: Tests describe "what" the component does, not "how"
- **High Coverage**: >95% line coverage with meaningful assertions

## Test Structure & Organization

```
tests/unit/
├── adapters/              # Adapter implementations with mocked ports
│   ├── database/          # Database adapter implementations
│   ├── http/              # HTTP client adapters
│   ├── messaging/         # Message queue adapters
│   └── test_logging_adapters.py  # Logging adapter tests
├── application/           # Application services and orchestration
│   ├── commands/          # Command handler tests
│   ├── queries/           # Query handler tests
│   └── services/          # Application service tests
├── core/                  # Pure domain logic tests
│   ├── entities/          # Domain entity tests
│   ├── events/            # Domain event tests
│   ├── services/          # Domain service tests
│   └── value_objects/     # Value object tests
├── infra/                 # Infrastructure component tests
│   ├── config/            # Configuration management tests
│   ├── logging/           # Logging infrastructure tests
│   ├── monitoring/        # Metrics and health check tests
│   └── persistence/       # Repository implementation tests
├── infrastructure/        # Legacy infrastructure tests (migrating)
├── ports/                 # Port interface contract tests
│   ├── inbound/           # Inbound port tests
│   ├── outbound/          # Outbound port tests
│   └── test_logging_ports.py  # Logging port tests
└── conftest.py            # Unit test fixtures and configuration
```

## Core Domain Testing (`unit/core/`)

### Entity Testing Patterns

```python
class TestUserEntity:
    """Test user entity business logic and invariants."""

    def test_user_creation_with_valid_data(self):
        """Test user entity creation with valid business data."""
        # Arrange
        username = "john_doe"
        email = Email("john@example.com")
        
        # Act
        user = User(username=username, email=email)
        
        # Assert
        assert user.username == username
        assert user.email == email
        assert user.is_active is True  # Default business state
        assert user.created_at is not None
        assert user.version == 1  # Initial version

    def test_user_email_change_business_rule(self):
        """Test email change validates business rules."""
        # Arrange
        user = User(username="john", email=Email("john@old.com"))
        original_version = user.version
        
        # Act
        user.change_email(Email("john@new.com"))
        
        # Assert
        assert user.email.value == "john@new.com"
        assert user.version == original_version + 1  # Version increment
        assert len(user.domain_events) == 1  # Event generated
        assert isinstance(user.domain_events[0], UserEmailChangedEvent)

    def test_user_deactivation_business_logic(self):
        """Test user deactivation follows business rules."""
        # Arrange
        user = User(username="john", email=Email("john@example.com"))
        deactivation_reason = "Account suspended for policy violation"
        
        # Act
        user.deactivate(reason=deactivation_reason)
        
        # Assert
        assert user.is_active is False
        assert user.deactivation_reason == deactivation_reason
        assert user.deactivated_at is not None
        
        # Verify business rule: cannot deactivate already inactive user
        with pytest.raises(BusinessRuleViolationError):
            user.deactivate("Already inactive")

    def test_user_entity_immutability_patterns(self):
        """Test entity immutability and defensive copying."""
        # Arrange
        user = User(username="john", email=Email("john@example.com"))
        original_events = user.domain_events.copy()
        
        # Act - External modification attempt
        external_events = user.domain_events
        external_events.append("malicious_event")
        
        # Assert - Internal state unchanged
        assert user.domain_events == original_events
        assert "malicious_event" not in user.domain_events
```

### Value Object Testing

```python
class TestEmailValueObject:
    """Test email value object validation and behavior."""

    def test_valid_email_creation(self):
        """Test valid email addresses are accepted."""
        valid_emails = [
            "test@example.com",
            "user.name+tag@domain.co.uk",
            "x@y.co"
        ]
        
        for email_str in valid_emails:
            email = Email(email_str)
            assert email.value == email_str
            assert str(email) == email_str

    def test_invalid_email_validation(self):
        """Test invalid email addresses are rejected."""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "",
            "user space@domain.com"
        ]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError, match="Invalid email format"):
                Email(invalid_email)

    def test_email_equality_and_hashing(self):
        """Test email value object equality and hashing behavior."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("different@example.com")
        
        # Equality
        assert email1 == email2
        assert email1 != email3
        
        # Hashing (for use in sets/dicts)
        email_set = {email1, email2, email3}
        assert len(email_set) == 2  # email1 and email2 are same

    def test_email_immutability(self):
        """Test email value objects are immutable."""
        email = Email("test@example.com")
        
        # Should not have settable attributes
        with pytest.raises(AttributeError):
            email.value = "changed@example.com"
```

### Domain Event Testing

```python
class TestDomainEvents:
    """Test domain event creation and behavior."""

    def test_domain_event_creation(self):
        """Test domain event creation with required data."""
        # Arrange
        aggregate_id = uuid4()
        username = "john_doe"
        email = "john@example.com"
        
        # Act
        event = UserCreatedEvent(
            aggregate_id=aggregate_id,
            username=username,
            email=email
        )
        
        # Assert
        assert event.aggregate_id == aggregate_id
        assert event.username == username
        assert event.email == email
        assert event.occurred_at is not None
        assert event.event_id is not None
        assert event.event_type == "UserCreatedEvent"

    def test_domain_event_serialization(self):
        """Test domain event serialization for persistence."""
        # Arrange
        event = UserCreatedEvent(
            aggregate_id=uuid4(),
            username="john_doe",
            email="john@example.com"
        )
        
        # Act
        serialized = event.to_dict()
        deserialized = UserCreatedEvent.from_dict(serialized)
        
        # Assert
        assert deserialized.aggregate_id == event.aggregate_id
        assert deserialized.username == event.username
        assert deserialized.email == event.email
        assert deserialized.occurred_at == event.occurred_at

    def test_domain_event_immutability(self):
        """Test domain events are immutable after creation."""
        event = UserCreatedEvent(
            aggregate_id=uuid4(),
            username="john_doe",
            email="john@example.com"
        )
        
        # Should not be able to modify event data
        with pytest.raises(AttributeError):
            event.username = "changed_username"
        
        with pytest.raises(AttributeError):
            event.occurred_at = datetime.now()
```

## Application Layer Testing (`unit/application/`)

### Command Handler Testing

```python
class TestCreateUserCommandHandler:
    """Test create user command handler with mocked dependencies."""

    @pytest.fixture
    def mock_dependencies(self, mocker):
        """Create mocked dependencies for command handler."""
        return {
            'user_repository': mocker.Mock(spec=UserRepository),
            'event_bus': mocker.Mock(spec=EventBus),
            'logger': mocker.Mock(spec=FlxLogger)
        }

    @pytest.fixture
    def command_handler(self, mock_dependencies):
        """Create command handler with mocked dependencies."""
        return CreateUserCommandHandler(
            user_repo=mock_dependencies['user_repository'],
            event_bus=mock_dependencies['event_bus'],
            logger=mock_dependencies['logger']
        )

    @pytest.mark.asyncio
    async def test_successful_user_creation(self, command_handler, mock_dependencies):
        """Test successful user creation command execution."""
        # Arrange
        command = CreateUserCommand(
            username="john_doe",
            email="john@example.com"
        )
        
        # Configure mocks
        mock_dependencies['user_repository'].exists_by_username.return_value = False
        mock_dependencies['user_repository'].save.return_value = None
        mock_dependencies['event_bus'].publish.return_value = None
        
        # Act
        result = await command_handler.handle(command)
        
        # Assert
        assert result.success is True
        assert result.user_id is not None
        assert result.errors == []
        
        # Verify interactions
        mock_dependencies['user_repository'].exists_by_username.assert_called_once_with("john_doe")
        mock_dependencies['user_repository'].save.assert_called_once()
        mock_dependencies['event_bus'].publish.assert_called_once()
        
        # Verify event type
        published_event = mock_dependencies['event_bus'].publish.call_args[0][0]
        assert isinstance(published_event, UserCreatedEvent)
        assert published_event.username == "john_doe"

    @pytest.mark.asyncio
    async def test_duplicate_username_error(self, command_handler, mock_dependencies):
        """Test command fails when username already exists."""
        # Arrange
        command = CreateUserCommand(
            username="existing_user",
            email="john@example.com"
        )
        
        # Configure mocks - user already exists
        mock_dependencies['user_repository'].exists_by_username.return_value = True
        
        # Act
        result = await command_handler.handle(command)
        
        # Assert
        assert result.success is False
        assert result.user_id is None
        assert "Username already exists" in result.errors[0]
        
        # Verify no save or event publishing occurred
        mock_dependencies['user_repository'].save.assert_not_called()
        mock_dependencies['event_bus'].publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_repository_error_handling(self, command_handler, mock_dependencies):
        """Test command handler handles repository errors gracefully."""
        # Arrange
        command = CreateUserCommand(
            username="john_doe",
            email="john@example.com"
        )
        
        # Configure mocks - repository raises exception
        mock_dependencies['user_repository'].exists_by_username.return_value = False
        mock_dependencies['user_repository'].save.side_effect = DatabaseError("Connection failed")
        
        # Act & Assert
        with pytest.raises(DatabaseError):
            await command_handler.handle(command)
        
        # Verify logging occurred
        mock_dependencies['logger'].error.assert_called()
```

## Adapter Testing (`unit/adapters/`)

### Database Adapter Testing

```python
class TestSqlUserRepository:
    """Test SQL user repository with mocked database session."""

    @pytest.fixture
    def mock_session(self, mocker):
        """Create mocked database session."""
        return mocker.Mock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository with mocked session."""
        return SqlUserRepository(session=mock_session)

    @pytest.mark.asyncio
    async def test_save_user_executes_correct_sql(self, repository, mock_session):
        """Test save user generates correct SQL operations."""
        # Arrange
        user = User(username="john_doe", email=Email("john@example.com"))
        
        # Act
        await repository.save(user)
        
        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Verify correct user data was added
        added_user = mock_session.add.call_args[0][0]
        assert added_user.username == "john_doe"
        assert added_user.email == "john@example.com"

    @pytest.mark.asyncio
    async def test_find_by_username_query_construction(self, repository, mock_session):
        """Test find by username constructs correct query."""
        # Arrange
        username = "john_doe"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = UserModel(
            id=uuid4(),
            username=username,
            email="john@example.com"
        )
        mock_session.execute.return_value = mock_result
        
        # Act
        user = await repository.find_by_username(username)
        
        # Assert
        assert user is not None
        assert user.username == username
        
        # Verify query was executed
        mock_session.execute.assert_called_once()
        executed_query = mock_session.execute.call_args[0][0]
        
        # Verify query contains username filter
        query_str = str(executed_query)
        assert "WHERE" in query_str
        assert "username" in query_str

    @pytest.mark.asyncio
    async def test_database_error_propagation(self, repository, mock_session):
        """Test database errors are properly propagated."""
        # Arrange
        user = User(username="john_doe", email=Email("john@example.com"))
        mock_session.commit.side_effect = SQLAlchemyError("Database connection lost")
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await repository.save(user)
        
        assert "Database connection lost" in str(exc_info.value)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()
```

## Infrastructure Testing (`unit/infra/`)

### Configuration Testing

```python
class TestConfigAdapter:
    """Test configuration adapter behavior."""

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Create mocked configuration manager."""
        mock = mocker.Mock(spec=ConfigManager)
        mock.get_all.return_value = {
            'database': {
                'url': 'postgresql://localhost/test',
                'pool_size': 10
            },
            'logging': {
                'level': 'INFO',
                'format': 'json'
            }
        }
        return mock

    @pytest.fixture
    def config_adapter(self, mock_config_manager):
        """Create config adapter with mocked manager."""
        return ConfigAdapter(config_manager=mock_config_manager)

    def test_get_nested_configuration_value(self, config_adapter):
        """Test retrieval of nested configuration values."""
        # Act
        db_url = config_adapter.get('database.url')
        pool_size = config_adapter.get('database.pool_size')
        log_level = config_adapter.get('logging.level')
        
        # Assert
        assert db_url == 'postgresql://localhost/test'
        assert pool_size == 10
        assert log_level == 'INFO'

    def test_get_missing_configuration_with_default(self, config_adapter):
        """Test default values for missing configuration."""
        # Act
        missing_value = config_adapter.get('missing.key', default='default_value')
        
        # Assert
        assert missing_value == 'default_value'

    def test_get_missing_configuration_without_default(self, config_adapter):
        """Test exception for missing required configuration."""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Configuration key 'missing.required' not found"):
            config_adapter.get('missing.required')

    def test_environment_variable_override(self, config_adapter, monkeypatch):
        """Test environment variables override configuration files."""
        # Arrange
        monkeypatch.setenv('FLX_DATABASE__URL', 'postgresql://override/db')
        
        # Act
        db_url = config_adapter.get('database.url')
        
        # Assert
        assert db_url == 'postgresql://override/db'
```

## Port Testing (`unit/ports/`)

### Port Contract Testing

```python
class TestUserRepositoryPort:
    """Test user repository port contract compliance."""

    def test_port_interface_completeness(self):
        """Test port interface defines all required methods."""
        # Arrange
        required_methods = [
            'save', 'find_by_id', 'find_by_username',
            'exists_by_username', 'delete', 'list_all'
        ]
        
        # Act
        port_methods = [method for method in dir(UserRepository) 
                       if not method.startswith('_')]
        
        # Assert
        for required_method in required_methods:
            assert required_method in port_methods, f"Missing required method: {required_method}"

    def test_port_method_signatures(self):
        """Test port methods have correct signatures."""
        import inspect
        
        # Test save method signature
        save_sig = inspect.signature(UserRepository.save)
        assert 'user' in save_sig.parameters
        assert save_sig.return_annotation == None
        
        # Test find_by_id method signature
        find_sig = inspect.signature(UserRepository.find_by_id)
        assert 'user_id' in find_sig.parameters
        assert 'Optional[User]' in str(find_sig.return_annotation)

    def test_port_inheritance_structure(self):
        """Test port follows proper inheritance hierarchy."""
        # Assert
        assert issubclass(UserRepository, Repository)
        assert hasattr(UserRepository, '__abstractmethods__')
        
        # Verify abstract methods are defined
        abstract_methods = UserRepository.__abstractmethods__
        assert 'save' in abstract_methods
        assert 'find_by_id' in abstract_methods
```

## Testing Utilities & Fixtures

### Common Test Fixtures

```python
# conftest.py - Unit test fixtures
import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime

from flx.core.entities import User
from flx.core.value_objects import Email
from flx.core.events import UserCreatedEvent

@pytest.fixture
def sample_user():
    """Create sample user for testing."""
    return User(
        username="test_user",
        email=Email("test@example.com")
    )

@pytest.fixture
def sample_user_data():
    """Create sample user data dictionary."""
    return {
        'username': 'test_user',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }

@pytest.fixture
def sample_domain_event():
    """Create sample domain event for testing."""
    return UserCreatedEvent(
        aggregate_id=uuid4(),
        username="test_user",
        email="test@example.com"
    )

@pytest.fixture
def mock_logger(mocker):
    """Create mock logger for testing."""
    return mocker.Mock(spec=FlxLogger)

@pytest.fixture
def mock_event_bus(mocker):
    """Create mock event bus for testing."""
    mock = mocker.Mock(spec=EventBus)
    mock.publish.return_value = None
    return mock

@pytest.fixture
def mock_user_repository(mocker):
    """Create mock user repository for testing."""
    mock = mocker.Mock(spec=UserRepository)
    mock.save.return_value = None
    mock.find_by_id.return_value = None
    mock.exists_by_username.return_value = False
    return mock
```

### Test Data Builders

```python
class UserTestBuilder:
    """Builder pattern for creating test users with various configurations."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset builder to default values."""
        self._username = "test_user"
        self._email = "test@example.com"
        self._active = True
        self._created_at = datetime.now()
        return self

    def with_username(self, username: str):
        """Set username for test user."""
        self._username = username
        return self

    def with_email(self, email: str):
        """Set email for test user."""
        self._email = email
        return self

    def inactive(self):
        """Make test user inactive."""
        self._active = False
        return self

    def created_days_ago(self, days: int):
        """Set creation date to specified days ago."""
        self._created_at = datetime.now() - timedelta(days=days)
        return self

    def build(self) -> User:
        """Build and return configured user."""
        user = User(
            username=self._username,
            email=Email(self._email)
        )
        
        # Apply configuration
        if not self._active:
            user.deactivate("Test deactivation")
            
        # Set creation time (using private access for testing)
        user._created_at = self._created_at
        
        return user

# Usage example
def test_user_builder_example():
    """Example of using UserTestBuilder in tests."""
    user = (UserTestBuilder()
           .with_username("john_doe")
           .with_email("john@example.com")
           .created_days_ago(30)
           .inactive()
           .build())
    
    assert user.username == "john_doe"
    assert not user.is_active
    assert user.created_at < datetime.now() - timedelta(days=29)
```

## Performance Testing for Unit Tests

### Execution Time Monitoring

```python
import pytest
import time
from functools import wraps

def time_limit(seconds):
    """Decorator to ensure test completes within time limit."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > seconds:
                pytest.fail(f"Test {func.__name__} took {execution_time:.3f}s, "
                          f"exceeded limit of {seconds}s")
            
            return result
        return wrapper
    return decorator

class TestPerformanceRequirements:
    """Test performance requirements for unit tests."""

    @time_limit(0.1)  # 100ms limit
    def test_user_creation_performance(self):
        """Test user creation completes within performance threshold."""
        # This test must complete in <100ms
        for _ in range(100):
            user = User(
                username=f"user_{_}",
                email=Email(f"user{_}@example.com")
            )
            assert user.is_active

    @time_limit(0.05)  # 50ms limit
    def test_value_object_validation_performance(self):
        """Test value object validation is fast enough."""
        # This test must complete in <50ms
        valid_emails = [f"user{i}@example.com" for i in range(50)]
        
        for email_str in valid_emails:
            email = Email(email_str)
            assert email.value == email_str

## Troubleshooting Unit Test Issues

### Common Unit Test Problems

#### Test Isolation Issues

```python
# Problem: Tests affecting each other
class ProblematicTestClass:
    shared_data = []  # ❌ Shared state between tests
    
    def test_first(self):
        self.shared_data.append("data")
        assert len(self.shared_data) == 1
    
    def test_second(self):
        # This may fail depending on test execution order
        assert len(self.shared_data) == 0

# Solution: Proper test isolation
class IsolatedTestClass:
    def setup_method(self):
        self.data = []  # ✅ Fresh data for each test
    
    def test_first(self):
        self.data.append("data")
        assert len(self.data) == 1
    
    def test_second(self):
        assert len(self.data) == 0  # ✅ Always passes
```

#### Mock Configuration Issues

```python
# Problem: Incorrectly configured mocks
def test_with_broken_mock(mocker):
    mock_repo = mocker.Mock(spec=UserRepository)
    # Mock not configured - returns Mock objects
    user = mock_repo.find_by_id("123")
    assert user.username == "test"  # ❌ Will fail

# Solution: Proper mock configuration
def test_with_configured_mock(mocker):
    mock_repo = mocker.Mock(spec=UserRepository)
    test_user = User(username="test", email=Email("test@example.com"))
    mock_repo.find_by_id.return_value = test_user
    
    user = mock_repo.find_by_id("123")
    assert user.username == "test"  # ✅ Will pass
```

#### Async Test Problems

```python
# Problem: Missing async/await
@pytest.mark.asyncio
async def test_broken_async():
    result = async_function()  # ❌ Missing await
    assert result is not None

# Solution: Proper async/await usage
@pytest.mark.asyncio
async def test_proper_async():
    result = await async_function()  # ✅ Proper await
    assert result is not None
```

### Performance Issues

#### Slow Unit Tests

```python
# Problem: Tests taking too long
def test_slow_operation():
    # Actual database connection in unit test ❌
    db = create_real_database_connection()
    result = db.query("SELECT * FROM large_table")
    assert len(result) > 0

# Solution: Use mocks for external dependencies
def test_fast_operation(mocker):
    # Mock database connection ✅
    mock_db = mocker.Mock()
    mock_db.query.return_value = [{"id": 1, "name": "test"}]
    
    result = mock_db.query("SELECT * FROM large_table")
    assert len(result) > 0
```

#### Memory Leaks in Tests

```python
# Problem: Tests consuming too much memory
class TestMemoryLeak:
    def setup_method(self):
        self.large_data = [i for i in range(1000000)]  # ❌ Large data kept in memory
    
    def test_operation(self):
        # Test uses large_data but doesn't clean up
        pass

# Solution: Efficient memory management
class TestMemoryEfficient:
    def test_operation(self):
        # Create minimal test data ✅
        test_data = [1, 2, 3]
        # Test logic here
        # Data automatically garbage collected
```

### Debugging Unit Tests

#### Test Discovery Issues

```bash
# Problem: Tests not discovered
pytest tests/unit/  # No tests found

# Diagnosis: Check test naming conventions
# ✅ Correct naming patterns:
# - Files: test_*.py or *_test.py
# - Classes: Test*
# - Functions: test_*

# ✅ Correct directory structure:
tests/
└── unit/
    ├── __init__.py  # Required for package discovery
    ├── test_entities.py
    └── test_services.py
```

#### Fixture Issues

```python
# Problem: Fixture not found
def test_user_creation(user_fixture):  # ❌ Fixture not defined
    assert user_fixture.username == "test"

# Solution: Define fixture properly
@pytest.fixture
def user_fixture():  # ✅ Properly defined fixture
    return User(username="test", email=Email("test@example.com"))

def test_user_creation(user_fixture):
    assert user_fixture.username == "test"
```

## Best Practices Summary

### Test Organization

1. **File Naming**: Use `test_*.py` pattern
2. **Class Naming**: Use `Test*` pattern for test classes
3. **Method Naming**: Use descriptive names that explain the scenario
4. **Directory Structure**: Mirror source code structure

### Test Quality

1. **Arrange-Act-Assert**: Clear test structure
2. **Single Responsibility**: One behavior per test
3. **Fast Execution**: Keep tests under 100ms each
4. **Deterministic**: Tests should always produce same result
5. **Independent**: Tests should not depend on each other

### Mocking Strategy

1. **Mock External Dependencies**: Database, HTTP, file system
2. **Use Spec**: Always specify `spec` parameter for mocks
3. **Configure Behavior**: Set return values and side effects
4. **Verify Interactions**: Assert method calls were made correctly

### Coverage Guidelines

1. **Line Coverage**: Aim for >95%
2. **Branch Coverage**: Test all conditional paths
3. **Edge Cases**: Test boundary conditions and error cases
4. **Business Logic**: Focus on domain logic coverage

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Testing Hub Foundation**](./index.md) - Overview of testing framework architecture and testing philosophy for comprehensive context
- [**Development Standards**](../standards/python-modernization-guide.md) - Code quality standards and development practices essential for effective unit testing
- [**Hexagonal Architecture Guide**](../../architecture/design/unified-architecture-guide.md) - Architecture patterns required for understanding component isolation and testing boundaries

### **➡️ Implementation Next Steps**

- [**Integration Testing Guide**](./integration-testing-guide.md) - Component interaction testing that builds upon unit test foundations
- [**Hexagonal Testing Guide**](./hexagonal-testing-guide.md) - Specialized testing patterns for ports, adapters, and domain layer validation
- [**Testing Framework Implementation**](./testing-framework.md) - Complete testing framework setup and advanced testing techniques

### **🔗 Related Implementation Topics**

- [**Code Quality Guide**](../guides/code-quality-guide.md) - Code quality standards and static analysis tools that support effective unit testing
- [**Development Workflow**](../guides/development-workflow.md) - Development process integration with testing cycles and quality gates
- [**API Reference for Testing**](../../api-reference/core-api-reference.md) - Core API documentation essential for comprehensive test coverage
- [**Infrastructure Testing Patterns**](../../infrastructure/operational-excellence.md) - Infrastructure service testing patterns that extend unit testing principles
- [**Security Testing Implementation**](../../security/architecture/security-architecture.md) - Security testing patterns and authentication validation strategies at the unit level
- [**Performance Testing Optimization**](../../optimization/performance/optimization-guide.md) - Performance testing techniques and benchmark validation for individual components

---

**📂 Content Document** | **🏠 Parent**: [Testing Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
```
