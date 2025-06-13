# Testing Strategies for Hexagonal Architecture in FLX

> **Function**: Comprehensive testing strategies for hexagonal architecture (Ports & Adapters) patterns | **Audience**: Test engineers, developers | **Status**: ✅ Stable

[![Testing](https://img.shields.io/badge/testing-strategies-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](../../architecture/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Complete testing strategies specifically tailored for hexagonal architecture (Ports & Adapters) patterns implemented in the FLX framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Testing**: [Testing Hub](./index.md) → **📄 Current**: Hexagonal Testing Strategies

### **📍 Learning Path Position**

```
[Testing Hub](./index.md) → **[HEXAGONAL STRATEGIES]** → [Hexagonal Testing Guide](./hexagonal-testing-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Testing Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Tests](../../../flx/tests/)
- **🔗 Related**: [Hexagonal Testing Guide](./hexagonal-testing-guide.md), [Port Testing](./ports-testing.md)

---

This guide provides comprehensive testing strategies specifically tailored for hexagonal architecture (Ports & Adapters) patterns implemented in the FLX framework. It covers domain-driven testing approaches, port-adapter testing, and integration strategies that maintain architectural boundaries.

## Table of Contents

1. [Architectural Testing Principles](#architectural-testing-principles)
2. [Domain Layer Testing](#domain-layer-testing)
3. [Port Interface Testing](#port-interface-testing)
4. [Adapter Testing Strategies](#adapter-testing-strategies)
5. [Application Service Testing](#application-service-testing)
6. [Integration Testing Patterns](#integration-testing-patterns)
7. [Testing Dependency Injection](#testing-dependency-injection)
8. [Mocking and Test Doubles](#mocking-and-test-doubles)
9. [Performance and Load Testing](#performance-and-load-testing)
10. [Testing Best Practices](#testing-best-practices)

## Architectural Testing Principles

### 1. Respect Architectural Boundaries

Tests should respect the same boundaries as the production code:

```python
# ✅ GOOD - Domain tests don't depend on infrastructure
def test_user_domain_logic():
    user = User(username="john", email="john@example.com")
    user.change_email("new@example.com")
    assert user.email == "new@example.com"

# ❌ BAD - Domain test importing infrastructure concerns
def test_user_with_database():
    from flx.infra.database import DatabaseConnection  # Wrong layer!
    # ... domain test should not know about database
```

### 2. Test the Right Things at the Right Level

- **Domain Layer**: Business logic, invariants, and rules
- **Port Layer**: Interface contracts and behaviors
- **Adapter Layer**: Protocol implementations and external integrations
- **Application Layer**: Orchestration and workflow coordination

### 3. Use the Test Pyramid

```
    /\     E2E Tests (Few)
   /  \    Integration Tests (Some)
  /____\   Unit Tests (Many)
```

## Domain Layer Testing

### Testing Entities and Aggregates

```python
import pytest
from datetime import UTC, datetime
from flx.core.entities import User, AggregateRoot
from flx.core.domain.value_objects import Email, UserId

class TestUserAggregate:
    """Test user aggregate root following DDD patterns."""

    def test_user_creation_with_valid_data(self):
        """Test user creation validates required fields."""
        user = User(
            username="john_doe",
            email=Email("john@example.com"),
            full_name="John Doe"
        )

        assert user.username == "john_doe"
        assert user.email.value == "john@example.com"
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_email_change_generates_event(self):
        """Test domain events are generated for important changes."""
        user = User(username="john", email=Email("john@example.com"))

        user.change_email(Email("new@example.com"))

        events = user.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "UserEmailChangedEvent"
        assert events[0].new_email == "new@example.com"

    def test_user_invariants_are_enforced(self):
        """Test business invariants are enforced at domain level."""
        user = User(username="john", email=Email("john@example.com"))

        # Username cannot be empty
        with pytest.raises(ValueError, match="Username cannot be empty"):
            user.change_username("")

        # Email must be valid format
        with pytest.raises(ValueError, match="Invalid email format"):
            user.change_email(Email("invalid-email"))

    def test_aggregate_version_control(self):
        """Test optimistic locking through version control."""
        user = User(username="john", email=Email("john@example.com"))
        initial_version = user.version

        user.change_username("john_updated")

        assert user.version == initial_version + 1
```

### Testing Value Objects

```python
class TestEmailValueObject:
    """Test email value object immutability and validation."""

    def test_email_creation_and_validation(self):
        """Test email value object validates format."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"
        assert email.domain == "example.com"

    def test_email_immutability(self):
        """Test value objects are immutable."""
        email = Email("test@example.com")

        with pytest.raises(AttributeError):
            email.value = "changed@example.com"  # Should fail

    def test_email_equality(self):
        """Test value object equality semantics."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2  # Same value
        assert email1 != email3  # Different value
        assert hash(email1) == hash(email2)  # Same hash
```

### Testing Domain Services

```python
class TestUserDomainService:
    """Test domain services that implement business logic."""

    def test_password_policy_validation(self):
        """Test domain service enforces password policies."""
        policy_service = PasswordPolicyService()

        # Valid password
        assert policy_service.is_valid("SecureP@ssw0rd123") is True

        # Invalid passwords
        assert policy_service.is_valid("weak") is False
        assert policy_service.is_valid("NoSpecialChars123") is False
        assert policy_service.is_valid("no-uppercase-123!") is False

    def test_user_uniqueness_check(self):
        """Test domain service checks business rules."""
        users = [
            User(username="john", email=Email("john@example.com")),
            User(username="jane", email=Email("jane@example.com"))
        ]

        uniqueness_service = UserUniquenessService(users)

        # Unique username/email should pass
        assert uniqueness_service.is_username_unique("bob") is True
        assert uniqueness_service.is_email_unique("bob@example.com") is True

        # Duplicate should fail
        assert uniqueness_service.is_username_unique("john") is False
        assert uniqueness_service.is_email_unique("john@example.com") is False
```

## Port Interface Testing

### Testing Inbound Ports (Command/Query Handlers)

```python
class TestUserCommandHandler:
    """Test command handlers as inbound ports."""

    @pytest.fixture
    def mock_user_repository(self, mocker):
        """Mock repository for isolated testing."""
        return mocker.Mock(spec=UserRepository)

    @pytest.fixture
    def mock_event_publisher(self, mocker):
        """Mock event publisher for isolated testing."""
        return mocker.Mock(spec=EventPublisher)

    @pytest.fixture
    def handler(self, mock_user_repository, mock_event_publisher):
        """Create handler with mocked dependencies."""
        return CreateUserCommandHandler(
            user_repository=mock_user_repository,
            event_publisher=mock_event_publisher
        )

    @pytest.mark.asyncio
    async def test_create_user_command_success(self, handler, mock_user_repository, mock_event_publisher):
        """Test successful user creation through command handler."""
        # Arrange
        command = CreateUserCommand(
            username="john",
            email="john@example.com",
            full_name="John Doe"
        )
        mock_user_repository.save.return_value = None
        mock_user_repository.find_by_username.return_value = None  # No existing user

        # Act
        result = await handler.handle(command)

        # Assert
        assert result.username == "john"
        mock_user_repository.save.assert_called_once()
        mock_event_publisher.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_command_duplicate_username(self, handler, mock_user_repository):
        """Test command handler enforces business rules."""
        # Arrange
        existing_user = User(username="john", email=Email("existing@example.com"))
        mock_user_repository.find_by_username.return_value = existing_user

        command = CreateUserCommand(
            username="john",  # Duplicate username
            email="john@example.com",
            full_name="John Doe"
        )

        # Act & Assert
        with pytest.raises(DuplicateUsernameError):
            await handler.handle(command)

        mock_user_repository.save.assert_not_called()
```

### Testing Outbound Ports (Repository Interfaces)

```python
class TestUserRepositoryContract:
    """Contract tests for user repository implementations."""

    @pytest.fixture
    def repository(self):
        """Override in subclasses for different implementations."""
        return InMemoryUserRepository()

    @pytest.mark.asyncio
    async def test_save_and_find_by_id(self, repository):
        """Test basic save and retrieve operations."""
        user = User(username="john", email=Email("john@example.com"))

        await repository.save(user)
        found_user = await repository.find_by_id(user.id)

        assert found_user is not None
        assert found_user.username == user.username
        assert found_user.email == user.email

    @pytest.mark.asyncio
    async def test_find_by_username(self, repository):
        """Test finding users by username."""
        user = User(username="john", email=Email("john@example.com"))
        await repository.save(user)

        found_user = await repository.find_by_username("john")
        assert found_user is not None
        assert found_user.username == "john"

        not_found = await repository.find_by_username("nonexistent")
        assert not_found is None

    @pytest.mark.asyncio
    async def test_update_user(self, repository):
        """Test user updates maintain consistency."""
        user = User(username="john", email=Email("john@example.com"))
        await repository.save(user)

        user.change_email(Email("new@example.com"))
        await repository.update(user)

        updated_user = await repository.find_by_id(user.id)
        assert updated_user.email.value == "new@example.com"
        assert updated_user.version == user.version
```

## Adapter Testing Strategies

### Testing Database Adapters

```python
class TestSQLAlchemyUserRepository(TestUserRepositoryContract):
    """Test SQLAlchemy repository implementation."""

    @pytest.fixture
    async def database_session(self):
        """Create test database session."""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSession(engine) as session:
            yield session

    @pytest.fixture
    def repository(self, database_session):
        """Create repository with test database session."""
        return SQLAlchemyUserRepository(session=database_session)

    @pytest.mark.asyncio
    async def test_database_constraints_enforced(self, repository):
        """Test database-specific constraints."""
        user1 = User(username="john", email=Email("john@example.com"))
        user2 = User(username="john", email=Email("jane@example.com"))  # Same username

        await repository.save(user1)

        with pytest.raises(IntegrityError):
            await repository.save(user2)  # Should fail due to unique constraint

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, repository, database_session):
        """Test transaction behavior on errors."""
        user = User(username="john", email=Email("john@example.com"))

        try:
            async with database_session.begin():
                await repository.save(user)
                raise Exception("Simulated error")
        except Exception:
            pass

        # User should not be saved due to rollback
        found_user = await repository.find_by_username("john")
        assert found_user is None
```

### Testing HTTP Adapters

```python
class TestHTTPAdapter:
    """Test HTTP adapter implementations."""

    @pytest.fixture
    def mock_http_client(self, mocker):
        """Mock HTTP client for testing."""
        return mocker.Mock(spec=httpx.AsyncClient)

    @pytest.fixture
    def http_adapter(self, mock_http_client):
        """Create HTTP adapter with mocked client."""
        adapter = HTTPAdapter(base_url="https://api.example.com")
        adapter._client = mock_http_client
        return adapter

    @pytest.mark.asyncio
    async def test_get_request_success(self, http_adapter, mock_http_client):
        """Test successful GET request."""
        # Arrange
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "John"}
        mock_http_client.get.return_value = mock_response

        # Act
        result = await http_adapter.get("/users/1")

        # Assert
        assert result == {"id": 1, "name": "John"}
        mock_http_client.get.assert_called_once_with(
            "https://api.example.com/users/1"
        )

    @pytest.mark.asyncio
    async def test_http_error_handling(self, http_adapter, mock_http_client):
        """Test HTTP error handling."""
        # Arrange
        mock_http_client.get.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=mocker.Mock(), response=mocker.Mock()
        )

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await http_adapter.get("/users/999")
```

## Application Service Testing

### Testing Command/Query Services

```python
class TestUserApplicationService:
    """Test application services orchestrating use cases."""

    @pytest.fixture
    def mock_dependencies(self, mocker):
        """Create all mocked dependencies."""
        return {
            'user_repository': mocker.Mock(spec=UserRepository),
            'email_service': mocker.Mock(spec=EmailService),
            'event_publisher': mocker.Mock(spec=EventPublisher),
            'password_hasher': mocker.Mock(spec=PasswordHasher)
        }

    @pytest.fixture
    def service(self, mock_dependencies):
        """Create service with mocked dependencies."""
        return UserApplicationService(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_register_user_use_case(self, service, mock_dependencies):
        """Test complete user registration use case."""
        # Arrange
        command = RegisterUserCommand(
            username="john",
            email="john@example.com",
            password="SecureP@ssw0rd",
            full_name="John Doe"
        )

        mock_dependencies['user_repository'].find_by_username.return_value = None
        mock_dependencies['user_repository'].find_by_email.return_value = None
        mock_dependencies['password_hasher'].hash.return_value = "hashed_password"

        # Act
        result = await service.register_user(command)

        # Assert
        assert result.success is True
        assert result.user_id is not None

        # Verify orchestration
        mock_dependencies['user_repository'].save.assert_called_once()
        mock_dependencies['email_service'].send_welcome_email.assert_called_once()
        mock_dependencies['event_publisher'].publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_rollback_on_email_failure(self, service, mock_dependencies):
        """Test transaction rollback when external service fails."""
        # Arrange
        command = RegisterUserCommand(
            username="john",
            email="john@example.com",
            password="SecureP@ssw0rd",
            full_name="John Doe"
        )

        mock_dependencies['user_repository'].find_by_username.return_value = None
        mock_dependencies['user_repository'].find_by_email.return_value = None
        mock_dependencies['password_hasher'].hash.return_value = "hashed_password"
        mock_dependencies['email_service'].send_welcome_email.side_effect = EmailServiceError()

        # Act & Assert
        with pytest.raises(UserRegistrationError):
            await service.register_user(command)

        # Verify rollback occurred
        mock_dependencies['user_repository'].delete.assert_called_once()
```

## Integration Testing Patterns

### Testing Port-Adapter Integration

```python
class TestUserRepositoryIntegration:
    """Integration tests between ports and adapters."""

    @pytest.fixture
    async def real_database(self):
        """Use real database for integration tests."""
        # Use TestContainers or Docker Compose for real DB
        engine = create_async_engine("postgresql://test:test@localhost/test_db")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        try:
            yield engine
        finally:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_repository_with_real_database(self, real_database):
        """Test repository with real database."""
        async with AsyncSession(real_database) as session:
            repository = SQLAlchemyUserRepository(session=session)

            # Create user
            user = User(username="john", email=Email("john@example.com"))
            await repository.save(user)

            # Verify persistence
            found_user = await repository.find_by_username("john")
            assert found_user is not None
            assert found_user.id == user.id
```

### Testing Event Flow Integration

```python
class TestEventFlowIntegration:
    """Test event publishing and handling integration."""

    @pytest.fixture
    def event_bus(self):
        """Create real event bus for integration testing."""
        return InMemoryEventBus()  # or Redis/RabbitMQ for full integration

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_registration_event_flow(self, event_bus):
        """Test complete event flow from command to handlers."""
        # Arrange
        user_repository = InMemoryUserRepository()
        email_service = MockEmailService()

        command_handler = CreateUserCommandHandler(
            user_repository=user_repository,
            event_publisher=event_bus
        )

        event_handler = UserRegisteredEventHandler(
            email_service=email_service
        )

        event_bus.subscribe(UserRegisteredEvent, event_handler.handle)

        # Act
        command = CreateUserCommand(
            username="john",
            email="john@example.com",
            full_name="John Doe"
        )

        user = await command_handler.handle(command)
        await event_bus.process_pending_events()

        # Assert
        assert email_service.emails_sent == 1
        assert email_service.last_email_to == "john@example.com"
```

## Testing Dependency Injection

### Testing Container Configuration

```python
class TestDependencyContainer:
    """Test dependency injection container configuration."""

    def test_container_wiring(self):
        """Test all dependencies are properly wired."""
        container = Container()
        container.wire()

        # Test resolution of complex dependency graphs
        user_service = container.user_application_service()

        assert isinstance(user_service.user_repository, UserRepository)
        assert isinstance(user_service.email_service, EmailService)
        assert isinstance(user_service.event_publisher, EventPublisher)

    def test_container_with_test_overrides(self):
        """Test container with test-specific overrides."""
        container = Container()

        # Override with test implementations
        container.user_repository.override(InMemoryUserRepository())
        container.email_service.override(MockEmailService())

        user_service = container.user_application_service()

        assert isinstance(user_service.user_repository, InMemoryUserRepository)
        assert isinstance(user_service.email_service, MockEmailService)
```

## Mocking and Test Doubles

### Using Different Types of Test Doubles

```python
# Dummy - Object passed around but not used
class DummyEmailService:
    async def send_email(self, *args, **kwargs):
        pass  # Does nothing

# Fake - Working implementation with shortcuts
class FakeUserRepository:
    def __init__(self):
        self._users = {}

    async def save(self, user: User) -> None:
        self._users[user.id] = user

    async def find_by_id(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

# Stub - Provides canned responses
class StubEmailService:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        if self.should_fail:
            raise EmailServiceError("Failed to send")
        return True

# Mock - Verifies behavior and interactions
class MockUserRepository:
    def __init__(self):
        self.save_calls = []
        self.find_calls = []

    async def save(self, user: User) -> None:
        self.save_calls.append(user)

    async def find_by_id(self, user_id: UserId) -> User | None:
        self.find_calls.append(user_id)
        return None

    def verify_save_called_once_with(self, expected_user: User):
        assert len(self.save_calls) == 1
        assert self.save_calls[0] == expected_user
```

## Performance and Load Testing

### Testing Adapter Performance

```python
class TestDatabasePerformance:
    """Performance tests for database adapters."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_bulk_user_creation_performance(self, database_session):
        """Test bulk operations meet performance requirements."""
        repository = SQLAlchemyUserRepository(session=database_session)

        users = [
            User(username=f"user_{i}", email=Email(f"user_{i}@example.com"))
            for i in range(1000)
        ]

        start_time = time.time()

        for user in users:
            await repository.save(user)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 5.0  # 5 seconds max for 1000 users

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_access(self, database_session):
        """Test repository handles concurrent access."""
        repository = SQLAlchemyUserRepository(session=database_session)

        async def create_user(i):
            user = User(username=f"user_{i}", email=Email(f"user_{i}@example.com"))
            await repository.save(user)
            return user

        # Create users concurrently
        tasks = [create_user(i) for i in range(100)]
        users = await asyncio.gather(*tasks)

        assert len(users) == 100
        assert all(user.id is not None for user in users)
```

## Testing Best Practices

### 1. Follow the AAA Pattern

```python
@pytest.mark.asyncio
async def test_user_creation():
    # Arrange
    username = "john"
    email = "john@example.com"

    # Act
    user = User(username=username, email=Email(email))

    # Assert
    assert user.username == username
    assert user.email.value == email
```

### 2. Use Descriptive Test Names

```python
# ✅ GOOD - Describes what is being tested
def test_user_creation_with_valid_email_succeeds():
    pass

def test_user_creation_with_invalid_email_raises_validation_error():
    pass

# ❌ BAD - Unclear what is being tested
def test_user():
    pass

def test_email_validation():
    pass
```

### 3. Test Edge Cases and Error Conditions

```python
class TestUserEmailValidation:
    """Test email validation edge cases."""

    @pytest.mark.parametrize("invalid_email", [
        "",
        "invalid",
        "@example.com",
        "user@",
        "user..double.dot@example.com",
        "user@.example.com",
    ])
    def test_invalid_email_formats_raise_validation_error(self, invalid_email):
        """Test various invalid email formats are rejected."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email(invalid_email)

    @pytest.mark.parametrize("valid_email", [
        "user@example.com",
        "user.name@example.com",
        "user+tag@example.co.uk",
        "123@example.com",
    ])
    def test_valid_email_formats_are_accepted(self, valid_email):
        """Test various valid email formats are accepted."""
        email = Email(valid_email)
        assert email.value == valid_email
```

### 4. Use Test Fixtures for Common Setup

```python
@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        username="john",
        email=Email("john@example.com"),
        full_name="John Doe"
    )

@pytest.fixture
async def user_repository():
    """Create in-memory repository for testing."""
    return InMemoryUserRepository()

@pytest.fixture
async def user_service(user_repository, mock_email_service):
    """Create user service with test dependencies."""
    return UserApplicationService(
        user_repository=user_repository,
        email_service=mock_email_service
    )
```

### 5. Isolate Tests from External Dependencies

```python
# ✅ GOOD - Uses test doubles
@pytest.mark.asyncio
async def test_user_registration_with_mocked_email_service(mocker):
    mock_email_service = mocker.Mock(spec=EmailService)
    mock_email_service.send_welcome_email.return_value = True

    service = UserService(email_service=mock_email_service)
    await service.register_user(user_data)

    mock_email_service.send_welcome_email.assert_called_once()

# ❌ BAD - Depends on external email service
@pytest.mark.asyncio
async def test_user_registration_with_real_email_service():
    email_service = SMTPEmailService()  # Real external dependency
    service = UserService(email_service=email_service)
    await service.register_user(user_data)  # Might fail due to network/SMTP issues
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Overview](../../architecture/index.md) - Understanding hexagonal architecture principles
- [Hexagonal Testing Guide](./hexagonal-testing-guide.md) - Comprehensive testing implementation strategies
- [Port Implementation](../../architecture/ports/index.md) - Port interface design patterns

### **Next Steps**

- [Integration Testing Guide](./integration-testing-guide.md) - Cross-component integration strategies
- [Performance Testing](./performance-testing.md) - System performance validation
- [E2E Testing Guide](./e2e-testing-guide.md) - Complete user journey testing

### **Related Topics**

- [Testing Ports](./ports-testing.md) - Focused port testing approaches
- [Testing Adapters](./adapters-testing.md) - Adapter-specific testing patterns
- [Unit Testing Guide](./unit-testing-guide.md) - Component-level testing strategies

---

**📂 Hub**: [Testing Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11

This comprehensive testing guide ensures that your hexagonal architecture implementation is thoroughly tested at all levels while maintaining architectural boundaries and principles.
