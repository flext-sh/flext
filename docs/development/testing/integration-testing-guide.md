# 🔗 FLX Integration Testing Guide

> **Function**: Component interaction testing for hexagonal architecture | **Audience**: Developers, test engineers, system architects | **Status**: Production-Ready

[![Testing](https://img.shields.io/badge/testing-integration-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](../../architecture/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Comprehensive integration testing guide for FLX component interactions, port-adapter contracts, and cross-layer data flow validation with realistic testing scenarios**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Section**: [Testing](./index.md) → **📄 Current**: Integration Testing Guide

### **📍 Learning Path Position**

```
[Testing Hub](./index.md) → [Unit Testing](./unit-testing-guide.md) → **[Integration Testing Guide]** → [E2E Testing](./e2e-testing-guide.md)
```

Advanced testing guide focusing on component interactions, boundary validation, and cross-layer data flow in hexagonal architecture systems.

## Integration Testing Philosophy

FLX integration testing embodies:

- **Realistic Interactions**: Test actual component integration with minimal mocking
- **Boundary Validation**: Verify port-adapter contracts and layer boundaries
- **Data Flow Testing**: Validate end-to-end data transformation and persistence
- **Error Propagation**: Test how errors flow through architectural layers
- **Performance Validation**: Ensure acceptable performance under realistic loads

## Test Structure & Organization

```
tests/integration/
├── adapters/                  # Adapter-port integration tests
│   ├── database/             # Database adapter integration
│   │   ├── test_user_repository_integration.py
│   │   ├── test_transaction_management.py
│   │   └── test_connection_pooling.py
│   ├── http/                 # HTTP adapter integration
│   │   ├── test_rest_client_integration.py
│   │   ├── test_authentication_flow.py
│   │   └── test_error_handling.py
│   ├── messaging/            # Message broker integration
│   │   ├── test_event_publishing.py
│   │   ├── test_message_consumption.py
│   │   └── test_dead_letter_handling.py
│   └── cache/               # Cache adapter integration
│       ├── test_redis_integration.py
│       └── test_cache_consistency.py
├── application/              # Application service integration
│   ├── test_command_handler_integration.py
│   ├── test_query_handler_integration.py
│   ├── test_application_service_orchestration.py
│   └── test_cross_service_communication.py
├── cross_layer/              # Cross-layer integration tests
│   ├── test_domain_to_infrastructure.py
│   ├── test_event_driven_workflows.py
│   ├── test_transaction_boundaries.py
│   └── test_error_propagation.py
├── infrastructure/           # Infrastructure service integration
│   ├── test_configuration_loading.py
│   ├── test_logging_integration.py
│   ├── test_monitoring_integration.py
│   └── test_health_check_integration.py
├── workflows/               # Complete workflow integration
│   ├── test_user_registration_workflow.py
│   ├── test_data_processing_pipeline.py
│   └── test_error_recovery_workflows.py
└── conftest.py             # Integration test fixtures and setup
```

## Core Integration Testing Patterns

### Port-Adapter Integration Testing

```python
class TestUserRepositoryIntegration:
    """Test user repository adapter integrates correctly with database port."""

    @pytest.fixture
    async def db_session(self):
        """Create real database session for integration testing."""
        engine = create_async_engine(
            "postgresql+asyncpg://test:test@localhost/test_db",
            echo=True  # Log SQL for debugging
        )

        async with engine.begin() as conn:
            # Setup test schema
            await conn.run_sync(Base.metadata.create_all)

        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            yield session
            # Cleanup happens automatically via rollback

    @pytest.fixture
    def user_repository(self, db_session):
        """Create user repository with real database session."""
        return SqlUserRepository(session=db_session)

    @pytest.mark.asyncio
    async def test_save_and_retrieve_integration(self, user_repository):
        """Test complete save and retrieve cycle with real database."""
        # Arrange
        user = User(
            username="integration_test",
            email=Email("integration@example.com")
        )
        original_id = user.id

        # Act - Save user
        await user_repository.save(user)

        # Act - Retrieve user
        retrieved_user = await user_repository.find_by_id(original_id)

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == original_id
        assert retrieved_user.username == "integration_test"
        assert retrieved_user.email.value == "integration@example.com"
        assert retrieved_user.created_at is not None

    @pytest.mark.asyncio
    async def test_repository_transaction_integration(self, user_repository, db_session):
        """Test repository respects database transaction boundaries."""
        # Arrange
        user1 = User(username="user1", email=Email("user1@example.com"))
        user2 = User(username="user2", email=Email("user2@example.com"))

        # Act - Save within transaction
        try:
            async with db_session.begin():
                await user_repository.save(user1)
                await user_repository.save(user2)

                # Simulate error after saves
                raise Exception("Simulated transaction error")
        except Exception:
            await db_session.rollback()

        # Assert - Both users should not exist due to rollback
        found_user1 = await user_repository.find_by_username("user1")
        found_user2 = await user_repository.find_by_username("user2")

        assert found_user1 is None
        assert found_user2 is None

    @pytest.mark.asyncio
    async def test_repository_query_performance(self, user_repository):
        """Test repository query performance with realistic data volume."""
        # Arrange - Create multiple users
        users = [
            User(username=f"user_{i}", email=Email(f"user{i}@example.com"))
            for i in range(100)
        ]

        # Save all users
        for user in users:
            await user_repository.save(user)

        # Act - Measure query performance
        start_time = time.time()
        all_users = await user_repository.find_all()
        query_time = time.time() - start_time

        # Assert
        assert len(all_users) >= 100
        assert query_time < 1.0  # Should complete within 1 second
```

### Application Service Integration Testing

```python
class TestUserServiceIntegration:
    """Test user service integrates correctly with all dependencies."""

    @pytest.fixture
    async def integrated_dependencies(self, db_session):
        """Create real dependencies for integration testing."""
        # Real repository with database
        user_repository = SqlUserRepository(session=db_session)

        # Real event bus with in-memory implementation
        event_bus = InMemoryEventBus()

        # Real logger with test configuration
        logger = FlxLogger(
            level=LogLevel.DEBUG,
            format=LogFormat.JSON
        )

        return {
            'user_repository': user_repository,
            'event_bus': event_bus,
            'logger': logger
        }

    @pytest.fixture
    def user_service(self, integrated_dependencies):
        """Create user service with real dependencies."""
        return UserService(
            user_repo=integrated_dependencies['user_repository'],
            event_bus=integrated_dependencies['event_bus'],
            logger=integrated_dependencies['logger']
        )

    @pytest.mark.asyncio
    async def test_user_registration_full_integration(self, user_service, integrated_dependencies):
        """Test complete user registration workflow with all real components."""
        # Arrange
        event_bus = integrated_dependencies['event_bus']
        captured_events = []

        # Subscribe to events
        async def capture_event(event):
            captured_events.append(event)

        await event_bus.subscribe(UserRegisteredEvent, capture_event)

        # Act
        result = await user_service.register_user(
            username="integration_user",
            email="integration@example.com",
            password="secure_password123"
        )

        # Assert service result
        assert result.success is True
        assert result.user_id is not None
        assert result.errors == []

        # Assert user was persisted
        user_repo = integrated_dependencies['user_repository']
        saved_user = await user_repo.find_by_id(result.user_id)

        assert saved_user is not None
        assert saved_user.username == "integration_user"
        assert saved_user.email.value == "integration@example.com"
        assert saved_user.is_active is True

        # Assert events were published
        assert len(captured_events) == 1
        assert isinstance(captured_events[0], UserRegisteredEvent)
        assert captured_events[0].username == "integration_user"
        assert captured_events[0].user_id == result.user_id

    @pytest.mark.asyncio
    async def test_duplicate_user_error_integration(self, user_service, integrated_dependencies):
        """Test duplicate user error handling across all layers."""
        # Arrange - Create existing user
        await user_service.register_user(
            username="existing_user",
            email="existing@example.com",
            password="password123"
        )

        # Act - Attempt to create duplicate
        result = await user_service.register_user(
            username="existing_user",  # Same username
            email="different@example.com",
            password="password456"
        )

        # Assert
        assert result.success is False
        assert result.user_id is None
        assert "Username already exists" in result.errors[0]

        # Verify no duplicate was created
        user_repo = integrated_dependencies['user_repository']
        users_with_username = await user_repo.find_by_username("existing_user")

        # Should only find the original user
        assert users_with_username is not None
        assert users_with_username.email.value == "existing@example.com"
```

### Cross-Layer Integration Testing

```python
class TestCrossLayerIntegration:
    """Test integration across hexagonal architecture layers."""

    @pytest.fixture
    async def full_application_stack(self, db_session):
        """Create complete application stack for testing."""
        # Infrastructure layer
        config = TestConfiguration()
        logger = FlxLogger(level=LogLevel.DEBUG)
        event_bus = InMemoryEventBus()

        # Adapter layer
        user_repository = SqlUserRepository(session=db_session)
        notification_adapter = InMemoryNotificationAdapter()

        # Application layer
        user_service = UserService(
            user_repo=user_repository,
            event_bus=event_bus,
            logger=logger
        )

        notification_service = NotificationService(
            notification_adapter=notification_adapter,
            event_bus=event_bus,
            logger=logger
        )

        # Subscribe notification service to user events
        await event_bus.subscribe(UserRegisteredEvent, notification_service.handle_user_registered)

        return {
            'user_service': user_service,
            'notification_service': notification_service,
            'event_bus': event_bus,
            'user_repository': user_repository,
            'notification_adapter': notification_adapter
        }

    @pytest.mark.asyncio
    async def test_event_driven_workflow_integration(self, full_application_stack):
        """Test complete event-driven workflow across all layers."""
        # Arrange
        user_service = full_application_stack['user_service']
        notification_adapter = full_application_stack['notification_adapter']

        # Act - Register user (should trigger notification)
        result = await user_service.register_user(
            username="event_test_user",
            email="event@example.com",
            password="password123"
        )

        # Give event processing time to complete
        await asyncio.sleep(0.1)

        # Assert - User was created
        assert result.success is True

        # Assert - Notification was sent
        sent_notifications = notification_adapter.get_sent_notifications()
        assert len(sent_notifications) == 1

        notification = sent_notifications[0]
        assert notification['type'] == 'welcome_email'
        assert notification['recipient'] == 'event@example.com'
        assert 'event_test_user' in notification['content']

    @pytest.mark.asyncio
    async def test_error_propagation_integration(self, full_application_stack):
        """Test how errors propagate through the architecture layers."""
        # Arrange
        user_service = full_application_stack['user_service']
        notification_adapter = full_application_stack['notification_adapter']

        # Configure notification adapter to fail
        notification_adapter.set_failure_mode(True)

        # Act - Register user (notification should fail but user creation should succeed)
        result = await user_service.register_user(
            username="error_test_user",
            email="error@example.com",
            password="password123"
        )

        # Give event processing time to complete
        await asyncio.sleep(0.1)

        # Assert - User creation succeeded despite notification failure
        assert result.success is True

        # Assert - User was persisted
        user_repo = full_application_stack['user_repository']
        saved_user = await user_repo.find_by_id(result.user_id)
        assert saved_user is not None

        # Assert - Notification failure was logged but didn't affect user creation
        assert len(notification_adapter.get_sent_notifications()) == 0
        assert notification_adapter.get_error_count() == 1
```

### Infrastructure Integration Testing

```python
class TestInfrastructureIntegration:
    """Test infrastructure component integration."""

    @pytest.mark.asyncio
    async def test_configuration_loading_integration(self):
        """Test configuration loading from multiple sources."""
        # Arrange - Create test configuration files
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            config_file.write_text("""
            database:
              url: postgresql://localhost/test
              pool_size: 10

            logging:
              level: INFO
              format: json
            """)

            # Set environment override
            os.environ['FLX_DATABASE__POOL_SIZE'] = '20'

            try:
                # Act
                config_manager = ConfigManager(config_path=config_file)
                config_adapter = ConfigAdapter(config_manager=config_manager)

                # Assert - File values loaded
                assert config_adapter.get('database.url') == 'postgresql://localhost/test'
                assert config_adapter.get('logging.level') == 'INFO'

                # Assert - Environment override applied
                assert config_adapter.get('database.pool_size') == 20

            finally:
                # Cleanup
                os.environ.pop('FLX_DATABASE__POOL_SIZE', None)

    @pytest.mark.asyncio
    async def test_logging_integration_full_stack(self, db_session):
        """Test logging integration across all application layers."""
        # Arrange
        log_capture = LogCapture()
        logger = FlxLogger(
            level=LogLevel.DEBUG,
            handlers=[log_capture]
        )

        user_repository = SqlUserRepository(session=db_session)
        user_service = UserService(
            user_repo=user_repository,
            event_bus=InMemoryEventBus(),
            logger=logger
        )

        # Act - Perform operation that generates logs
        await user_service.register_user(
            username="logging_test",
            email="logging@example.com",
            password="password123"
        )

        # Assert - Logs were generated at different layers
        logs = log_capture.get_logs()

        # Service layer logs
        service_logs = [log for log in logs if 'UserService' in log.get('logger', '')]
        assert len(service_logs) > 0

        # Repository layer logs
        repo_logs = [log for log in logs if 'Repository' in log.get('logger', '')]
        assert len(repo_logs) > 0

        # Verify log structure
        for log in logs:
            assert 'timestamp' in log
            assert 'level' in log
            assert 'message' in log
            assert 'correlation_id' in log  # Request correlation
```

## Performance Integration Testing

### Load Testing Integration

```python
class TestPerformanceIntegration:
    """Test performance characteristics under realistic loads."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_user_registration_performance(self, full_application_stack):
        """Test system performance under concurrent load."""
        user_service = full_application_stack['user_service']

        async def register_user(index):
            """Register a single user."""
            return await user_service.register_user(
                username=f"perf_user_{index}",
                email=f"perf{index}@example.com",
                password="password123"
            )

        # Act - Register 50 users concurrently
        start_time = time.time()

        tasks = [register_user(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        execution_time = time.time() - start_time

        # Assert - All registrations succeeded
        successful_results = [r for r in results if not isinstance(r, Exception) and r.success]
        assert len(successful_results) == 50

        # Assert - Performance within acceptable limits
        assert execution_time < 10.0  # Should complete within 10 seconds

        # Assert - No data corruption
        user_repo = full_application_stack['user_repository']
        all_users = await user_repo.find_all()
        perf_users = [u for u in all_users if u.username.startswith('perf_user_')]
        assert len(perf_users) == 50

    @pytest.mark.asyncio
    async def test_database_connection_pooling_integration(self, db_session):
        """Test database connection pooling under load."""
        # Arrange
        repository = SqlUserRepository(session=db_session)

        async def create_and_find_user(index):
            """Create user and immediately find it."""
            user = User(
                username=f"pool_user_{index}",
                email=Email(f"pool{index}@example.com")
            )
            await repository.save(user)
            return await repository.find_by_id(user.id)

        # Act - Perform 20 concurrent database operations
        tasks = [create_and_find_user(i) for i in range(20)]
        results = await asyncio.gather(*tasks)

        # Assert - All operations succeeded
        assert len(results) == 20
        assert all(user is not None for user in results)

        # Assert - No connection pool exhaustion
        # (Would manifest as exceptions in results)
        exceptions = [r for r in results if isinstance(r, Exception)]
        assert len(exceptions) == 0
```

## Test Data Management

### Database Test Fixtures

```python
# conftest.py - Integration test fixtures

@pytest.fixture(scope="session")
async def test_database_engine():
    """Create test database engine for integration tests."""
    # Use test database
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_flx",
        echo=False,  # Set to True for SQL debugging
        pool_size=5,
        max_overflow=10
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db_session(test_database_engine):
    """Create database session with automatic rollback."""
    async_session = async_sessionmaker(
        test_database_engine,
        expire_on_commit=False
    )

    async with async_session() as session:
        # Start transaction
        async with session.begin():
            yield session
            # Automatic rollback happens here

@pytest.fixture
def integration_test_data():
    """Create standard test data for integration tests."""
    return {
        'users': [
            {
                'username': 'test_user_1',
                'email': 'user1@example.com',
                'password': 'password123'
            },
            {
                'username': 'test_user_2',
                'email': 'user2@example.com',
                'password': 'password456'
            }
        ],
        'organizations': [
            {
                'name': 'Test Organization',
                'domain': 'test.com'
            }
        ]
    }
```

## Troubleshooting Integration Test Issues

### Database Connection Issues

```python
# Problem: Database connection failures
# Solution: Proper connection management and error handling

@pytest.fixture
async def robust_db_session():
    """Database session with connection retry logic."""
    max_retries = 3
    retry_delay = 1.0

    for attempt in range(max_retries):
        try:
            engine = create_async_engine(
                DATABASE_URL,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600   # Recycle connections hourly
            )

            async with engine.begin() as conn:
                # Test connection
                await conn.execute(text("SELECT 1"))

            async_session = async_sessionmaker(engine)
            async with async_session() as session:
                yield session
                break

        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)
```

### Event Processing Issues

```python
# Problem: Race conditions in event processing
# Solution: Proper synchronization and timing

class TestEventSynchronization:
    """Test event processing synchronization."""

    @pytest.mark.asyncio
    async def test_event_processing_completion(self, event_bus):
        """Ensure all events are processed before assertions."""
        processed_events = []

        async def event_handler(event):
            # Simulate processing time
            await asyncio.sleep(0.1)
            processed_events.append(event)

        await event_bus.subscribe(TestEvent, event_handler)

        # Publish event
        await event_bus.publish(TestEvent(data="test"))

        # Wait for processing to complete
        timeout = 5.0
        start_time = time.time()

        while len(processed_events) == 0 and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.01)

        assert len(processed_events) == 1
        assert processed_events[0].data == "test"
```

### Memory Leaks in Integration Tests

```python
# Problem: Memory accumulation across test runs
# Solution: Proper cleanup and resource management

class TestResourceManagement:
    """Test proper resource cleanup."""

    def test_memory_cleanup_after_integration_test(self):
        """Verify memory is cleaned up after integration tests."""
        import gc
        import psutil
        import os

        # Measure memory before test
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss

        # Run resource-intensive operation
        # ... test operations here ...

        # Force garbage collection
        gc.collect()

        # Measure memory after cleanup
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before

        # Assert memory increase is reasonable (< 50MB)
        assert memory_increase < 50 * 1024 * 1024
```

## Best Practices Summary

### Integration Test Design

1. **Realistic Dependencies**: Use real implementations where possible
2. **Isolated Environment**: Each test should have clean state
3. **Transaction Management**: Proper database transaction handling
4. **Event Processing**: Ensure asynchronous events complete
5. **Error Scenarios**: Test failure modes and recovery

### Performance Considerations

1. **Execution Time**: Keep integration tests under 30 seconds each
2. **Resource Usage**: Monitor memory and connection usage
3. **Parallel Execution**: Design tests for concurrent execution
4. **Load Testing**: Include realistic load scenarios

### Data Management

1. **Test Data Isolation**: Each test creates its own data
2. **Database Cleanup**: Automatic rollback after each test
3. **Fixture Reuse**: Efficient fixture management
4. **Data Consistency**: Verify data integrity across operations

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Unit Testing Guide**](./unit-testing-guide.md) - Foundation testing patterns required for effective integration testing
- [**Testing Hub Foundation**](./index.md) - Overview of testing framework architecture and comprehensive testing strategy
- [**Hexagonal Architecture Guide**](../../architecture/design/unified-architecture-guide.md) - Architecture patterns essential for understanding component boundaries and integration points

### **➡️ Implementation Next Steps**

- [**E2E Testing Guide**](./e2e-testing-guide.md) - Complete workflow testing that builds upon integration test foundations
- [**Hexagonal Testing Guide**](./hexagonal-testing-guide.md) - Specialized testing patterns for architectural compliance and boundary validation
- [**Testing Framework Implementation**](./testing-framework.md) - Advanced testing framework setup and declarative testing techniques

### **🔗 Related Implementation Topics**

- [**Infrastructure Testing Patterns**](../../infrastructure/operational-excellence.md) - Infrastructure service testing and production monitoring that extends integration testing principles
- [**Database Integration Patterns**](../../guides/oracle/oracle-integration-comprehensive-guide.md) - Database-specific integration testing strategies for Oracle and other systems
- [**Performance Testing Optimization**](../../optimization/performance/optimization-guide.md) - Performance testing techniques and load testing strategies for integrated systems
- [**Security Testing Implementation**](../../security/architecture/security-architecture.md) - Security testing patterns and authentication validation in integrated environments
- [**API Testing Strategies**](../../api-reference/core-api-reference.md) - API testing approaches that complement integration testing
- [**Event-Driven Architecture Testing**](../../architecture/patterns/event-driven-patterns.md) - Event processing validation and message flow testing in distributed systems

---

**📂 Content Document** | **🏠 Parent**: [Testing Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
