# Testing Patterns

**Analysis Date:** 2026-01-31

## Test Framework

### Runner

- **Framework**: pytest 9.0+
- **Config**: `pyproject.toml` in each project
- **Coverage**: pytest-cov with 80% minimum (enforced)

### Run Commands

```bash
# All tests
PYTHONPATH=src poetry run pytest

# Watch mode (requires pytest-watch)
PYTHONPATH=src poetry run pytest-watch tests/

# With coverage (80% minimum enforced)
PYTHONPATH=src poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Unit tests only
PYTHONPATH=src poetry run pytest -m unit

# Integration tests only
PYTHONPATH=src poetry run pytest -m integration

# Specific file
PYTHONPATH=src poetry run pytest tests/unit/test_result.py -v

# Specific test
PYTHONPATH=src poetry run pytest tests/unit/test_result.py::TestFlextResult::test_ok_creates_success -v

# Fast feedback (last failed, fail fast)
PYTHONPATH=src poetry run pytest --lf --ff -x
```

## Test File Organization

### Location

- **Unit tests**: `tests/unit/test_*.py`
- **Integration tests**: `tests/integration/test_*.py`
- **E2E tests**: `tests/e2e/test_*.py`
- **Benchmarks**: `tests/benchmark/test_*.py`
- **Helpers**: `tests/helpers/` (fixtures, factories)

### File Naming

- **Test files**: `test_*.py` or `*_test.py`
- **Match source structure**: `src/module.py` → `tests/unit/test_module.py`
- **Example**: `src/flext_core/result.py` → `tests/unit/test_result.py`

### Structure

```
flext-core/
├── src/
│   ├── flext_core/
│   │   ├── result.py
│   │   ├── config.py
│   │   └── models.py
│   └── flext_tests/
│       └── ...test helpers...
└── tests/
    ├── unit/
    │   ├── test_result.py
    │   ├── test_config.py
    │   ├── test_models.py
    │   └── test_result_monad.py
    ├── integration/
    │   ├── test_container_integration.py
    │   └── patterns/
    │       └── test_architectural_patterns.py
    ├── benchmark/
    │   ├── test_container_performance.py
    │   └── test_container_memory.py
    └── helpers/
        ├── factories.py
        ├── scenarios.py
        └── __init__.py
```

## Test Structure

### Test Class Organization

```python
"""Test module docstring with copyright."""

from __future__ import annotations

import pytest
from flext_core import FlextResult as r


class TestFlextResult:
    """Test FlextResult type and methods."""

    def test_ok_creates_success_result(self) -> None:
        """Test that ok() creates a successful result."""
        result = r[str].ok("value")
        assert result.is_success
        assert result.value == "value"

    def test_fail_creates_failure_result(self) -> None:
        """Test that fail() creates a failure result."""
        result = r[str].fail("error message")
        assert result.is_failure
        assert result.error == "error message"

    @pytest.mark.unit
    def test_flat_map_chains_operations(self) -> None:
        """Test monadic composition with flat_map."""
        result = (
            r[int].ok(5)
            .flat_map(lambda x: r[int].ok(x * 2))
            .flat_map(lambda x: r[int].ok(x + 1))
        )
        assert result.is_success
        assert result.value == 11

    @pytest.mark.unit
    def test_map_transforms_success_value(self) -> None:
        """Test value transformation with map."""
        result = r[int].ok(10).map(lambda x: x * 2)
        assert result.is_success
        assert result.value == 20

    @pytest.mark.error_path
    def test_map_ignores_failure_value(self) -> None:
        """Test that map skips failures."""
        result = r[int].fail("error").map(lambda x: x * 2)
        assert result.is_failure
        assert result.error == "error"


class TestFlextResultEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.boundary
    def test_result_with_none_value(self) -> None:
        """Test result containing None."""
        # None is a valid value
        result = r[int | None].ok(None)
        assert result.is_success
        assert result.value is None

    @pytest.mark.boundary
    def test_result_with_empty_string_error(self) -> None:
        """Test result with empty error message."""
        result = r[str].fail("")
        assert result.is_failure
        assert result.error == ""
```

### Naming Convention (MANDATORY)

**Pattern**: `test_<function>_<scenario>_<expected_result>`

```python
# ✅ GOOD - Clear test names
def test_validate_email_with_valid_email_returns_true(self) -> None: ...
def test_validate_email_with_invalid_email_returns_false(self) -> None: ...
def test_process_with_empty_list_returns_empty_result(self) -> None: ...
def test_authenticate_with_invalid_credentials_fails(self) -> None: ...

# ❌ BAD - Vague names
def test_validation(self) -> None: ...
def test_email(self) -> None: ...
def test_process(self) -> None: ...
```

### AAA Pattern (Arrange-Act-Assert)

```python
def test_user_creation_with_valid_data_succeeds(self) -> None:
    """Test user creation with valid data."""
    # ARRANGE - Setup test data
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
    }

    # ACT - Execute the operation
    result = create_user(user_data)

    # ASSERT - Verify the result
    assert result.is_success
    assert result.value.name == "John Doe"
    assert result.value.email == "john@example.com"
```

## Test Types

### Unit Tests (Fast, Isolated)

- **Location**: `tests/unit/test_*.py`
- **Marker**: `@pytest.mark.unit`
- **Speed**: < 1ms per test
- **Dependencies**: Mock ALL external services

```python
import pytest
from unittest.mock import Mock

@pytest.mark.unit
def test_calculate_total_with_items_returns_sum(self) -> None:
    """Test calculation logic without database."""
    items = [
        {"price": 10.0},
        {"price": 20.0},
        {"price": 30.0},
    ]
    total = calculate_total(items)
    assert total == 60.0

@pytest.mark.unit
def test_validate_user_with_missing_email_fails(self) -> None:
    """Test validation without external services."""
    user_data = {"name": "John"}
    result = validate_user(user_data)
    assert result.is_failure
    assert "email" in result.error.lower()
```

**Mocking Pattern**:

```python
from unittest.mock import Mock, patch

@pytest.mark.unit
def test_handler_calls_service_on_message(self) -> None:
    """Test handler delegates to service."""
    # Create mock service
    mock_service = Mock()
    mock_service.execute.return_value = r[dict].ok({"result": "data"})

    # Create handler with mock
    handler = MessageHandler(service=mock_service)

    # Execute
    result = handler.handle(Message(type="test"))

    # Assert
    assert result.is_success
    mock_service.execute.assert_called_once()
```

### Integration Tests (Real Dependencies)

- **Location**: `tests/integration/test_*.py`
- **Marker**: `@pytest.mark.integration`
- **Dependencies**: Use REAL services (test database, test containers)
- **Scope**: Test service-to-service interactions

```python
import pytest
from flext_core import FlextContainer

@pytest.mark.integration
def test_service_with_real_config_integration(self, test_container: FlextContainer) -> None:
    """Test service with real configuration."""
    # Get real service from container
    config = test_container.get_config()
    service = UserService(config=config)

    # Execute with real setup
    result = service.fetch_user_by_email("user@example.com")

    # Assert real behavior
    assert result.is_success or result.is_failure  # Both valid states

@pytest.mark.integration
def test_database_transaction_rollback(self, test_db) -> None:
    """Test transaction rollback with real database."""
    # Use real test database
    user = test_db.create_user(name="Test")
    test_db.delete_user(user.id)

    # Verify deletion
    assert test_db.get_user(user.id) is None
```

### E2E Tests (Complete Workflows)

- **Location**: `tests/e2e/test_*.py`
- **Marker**: `@pytest.mark.e2e`
- **Scope**: Complete request → response cycles
- **Used for**: Critical user journeys only

```python
@pytest.mark.e2e
def test_user_signup_complete_workflow(self) -> None:
    """Test complete user signup workflow."""
    # User creation
    signup_result = api_client.signup({
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secure123",
    })
    assert signup_result.status_code == 201

    # Email verification
    verify_result = api_client.verify_email(signup_result.email_token)
    assert verify_result.status_code == 200

    # Login
    login_result = api_client.login({
        "email": "alice@example.com",
        "password": "secure123",
    })
    assert login_result.status_code == 200
    assert "auth_token" in login_result.json()
```

## Fixtures and Factories

### Pytest Fixtures

```python
# tests/helpers/factories.py
import pytest
from flext_core import FlextContainer, FlextLogger

@pytest.fixture
def test_container() -> FlextContainer:
    """Provide test container with all services."""
    container = FlextContainer()
    # Setup test configuration
    return container

@pytest.fixture
def test_logger() -> FlextLogger:
    """Provide test logger instance."""
    return FlextLogger.get_logger("test")

@pytest.fixture
def test_database(monkeypatch) -> TestDatabase:
    """Provide test database with cleanup."""
    db = TestDatabase()
    db.connect()
    yield db
    db.cleanup()  # Teardown

@pytest.fixture(scope="session")
def test_data() -> dict:
    """Provide static test data (session scope)."""
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ],
    }
```

### Fixture Usage

```python
def test_with_fixtures(self, test_container, test_logger) -> None:
    """Test using injected fixtures."""
    service = test_container.get("service")
    test_logger.info("Starting test")
    result = service.execute()
    assert result.is_success
```

### Factory Functions

```python
# tests/helpers/factories.py
from flext_core import FlextResult as r

class TestUserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create_user(**kwargs) -> dict:
        """Create test user with defaults."""
        return {
            "id": 1,
            "name": kwargs.get("name", "Test User"),
            "email": kwargs.get("email", "test@example.com"),
            "active": kwargs.get("active", True),
        }

    @staticmethod
    def create_users(count: int) -> list[dict]:
        """Create multiple test users."""
        return [
            TestUserFactory.create_user(
                id=i,
                name=f"User {i}",
                email=f"user{i}@example.com",
            )
            for i in range(count)
        ]


# Usage in tests
def test_process_users(self) -> None:
    """Test processing users."""
    users = TestUserFactory.create_users(5)
    result = process_users(users)
    assert result.is_success
    assert len(result.value) == 5
```

## Coverage Requirements

### Minimum Coverage: 80%

**Enforce with**:

```bash
PYTHONPATH=src poetry run pytest \
  --cov=src/flext_core \
  --cov-report=term-missing \
  --cov-fail-under=80
```

### Must Cover

- ✅ All public function/method logic paths
- ✅ All success and failure scenarios
- ✅ All conditional branches (if/else)
- ✅ Exception handling paths
- ✅ Error cases in FlextResult
- ✅ All public API endpoints

### Can Exclude

- ❌ `if __name__ == "__main__":` blocks
- ❌ Generated code (protobuf, migrations)
- ❌ Simple getters/setters with no logic
- ❌ Abstract/stub implementations

### Check Coverage

```bash
# Full report with line-by-line coverage
PYTHONPATH=src poetry run pytest \
  --cov=src/flext_core \
  --cov-report=html  # Creates htmlcov/index.html

# List uncovered lines
PYTHONPATH=src poetry run pytest \
  --cov=src/flext_core \
  --cov-report=term-missing:skip-covered
```

## Markers (Organization)

### Standard Markers (pytest.ini)

```python
# Use markers for selective test execution
@pytest.mark.unit              # Fast unit tests
@pytest.mark.integration       # Slow integration tests
@pytest.mark.e2e               # Complete workflows
@pytest.mark.slow              # Takes > 1 second
@pytest.mark.performance       # Performance benchmarks
@pytest.mark.benchmark         # pytest-benchmark tests
@pytest.mark.boundary          # Edge cases and limits
@pytest.mark.error_path        # Error scenarios
@pytest.mark.happy_path        # Success scenarios
@pytest.mark.regression        # Regression testing
@pytest.mark.architecture      # Architectural patterns
@pytest.mark.ddd               # Domain-driven design
@pytest.mark.smoke             # Smoke tests
@pytest.mark.skip              # Skip test
```

### Using Markers

```bash
# Run only unit tests
PYTHONPATH=src poetry run pytest -m unit

# Run everything except slow tests
PYTHONPATH=src poetry run pytest -m "not slow"

# Run integration tests only
PYTHONPATH=src poetry run pytest -m integration

# Run both unit and integration
PYTHONPATH=src poetry run pytest -m "unit or integration"

# Run error path tests
PYTHONPATH=src poetry run pytest -m error_path
```

## Common Test Patterns

### Testing FlextResult Success Path

```python
@pytest.mark.unit
def test_operation_returns_success_with_value(self) -> None:
    """Test successful operation."""
    result = r[str].ok("success_value")

    assert result.is_success
    assert result.value == "success_value"
    assert result.error is None
```

### Testing FlextResult Failure Path

```python
@pytest.mark.error_path
def test_operation_returns_failure_with_error(self) -> None:
    """Test failed operation."""
    result = r[str].fail("error message")

    assert result.is_failure
    assert result.error == "error message"
    assert result.value is None
```

### Testing Monadic Chaining

```python
@pytest.mark.unit
def test_flat_map_chains_results(self) -> None:
    """Test monadic composition."""
    result = (
        r[int].ok(5)
        .flat_map(lambda x: r[int].ok(x * 2))
        .flat_map(lambda x: r[int].ok(x + 1))
        .map(lambda x: str(x))
    )

    assert result.is_success
    assert result.value == "11"
```

### Testing Error Propagation

```python
@pytest.mark.error_path
def test_flat_map_stops_on_error(self) -> None:
    """Test error stops execution chain."""
    result = (
        r[int].ok(5)
        .flat_map(lambda x: r[int].fail("error"))
        .flat_map(lambda x: r[int].ok(x * 2))  # Never executes
    )

    assert result.is_failure
    assert result.error == "error"
```

### Testing with Fixtures

```python
@pytest.mark.integration
def test_service_with_fixture(self, test_container: FlextContainer) -> None:
    """Test service using injected fixture."""
    # Get service from container
    service = test_container.get("user_service").value

    # Execute
    result = service.fetch_user(user_id=1)

    # Assert
    assert result.is_success
    assert result.value.id == 1
```

### Testing Parametrized Cases

```python
import pytest

@pytest.mark.parametrize(
    "email,is_valid",
    [
        ("test@example.com", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("test@", False),
    ],
)
def test_validate_email_parametrized(self, email: str, is_valid: bool) -> None:
    """Test email validation with multiple cases."""
    result = validate_email(email)
    if is_valid:
        assert result.is_success
    else:
        assert result.is_failure
```

## Anti-Patterns (What NOT to Do)

### ❌ Mocking Internal Code

```python
# WRONG - Don't mock your own code
@patch("flext_core.result.FlextResult.ok")
def test_function(self, mock_ok):
    # This defeats the purpose of testing
    mock_ok.return_value = r[str].ok("fake")
    result = function_under_test()
    # You're not actually testing anything
```

### ❌ Dependent Tests

```python
# WRONG - Tests depend on execution order
def test_1_create_user(self):
    self.user_id = create_user("Alice")

def test_2_get_user(self):
    # test_2 depends on test_1 running first
    user = get_user(self.user_id)
    assert user.name == "Alice"
```

### ❌ Flaky/Time-Dependent Tests

```python
# WRONG - Test is unreliable
def test_notification_sent(self):
    send_notification()
    time.sleep(1)  # Brittle - timing dependent
    assert notification_received()

# BETTER - Mock time or use events
def test_notification_queued(self):
    result = send_notification()
    assert result.is_success  # Just verify queuing
```

### ❌ Testing Implementation Details

```python
# WRONG - Testing how it works, not what it does
def test_internal_counter_increments(self):
    obj = MyClass()
    assert obj._counter == 0  # Testing private state
    obj.process()
    assert obj._counter == 1  # Still testing private state

# CORRECT - Test behavior
def test_process_increments_total(self):
    obj = MyClass()
    obj.process()
    assert obj.get_total() == 1  # Public interface
```

### ❌ Ignoring Failing Tests

```python
# WRONG - Never ignore failures
@pytest.mark.skip(reason="will fix later")
def test_important_feature(self):
    # This test never runs and is forgotten
    pass

# CORRECT - Fix or use xfail with reason
@pytest.mark.xfail(reason="known issue #123 being tracked")
def test_known_broken_feature(self):
    # Document why it fails, fix issue is tracked
    pass
```

## TDD Workflow

**Follow this cycle for every test**:

1. **RED** - Write failing test
   ```python
   def test_validate_password_with_short_password_fails(self) -> None:
       """Test that short passwords are rejected."""
       result = validate_password("123")
       assert result.is_failure
   ```

2. **VERIFY RED** - Run and confirm failure
   ```bash
   PYTHONPATH=src poetry run pytest test_validators.py::test_validate_password_with_short_password_fails -v
   # Output: FAILED ... (expected)
   ```

3. **GREEN** - Write minimal implementation
   ```python
   def validate_password(password: str) -> r[str]:
       """Validate password complexity."""
       if len(password) < 8:
           return r[str].fail("Password too short")
       return r[str].ok(password)
   ```

4. **VERIFY GREEN** - Confirm test passes
   ```bash
   PYTHONPATH=src poetry run pytest test_validators.py::test_validate_password_with_short_password_fails -v
   # Output: PASSED
   ```

5. **REFACTOR** - Improve code while keeping tests green
   ```bash
   # Keep running tests as you improve
   PYTHONPATH=src poetry run pytest tests/ -m unit --lf --ff -x
   ```

## Test Quality Checklist

Before marking tests complete:

- [ ] Every new function has at least one test
- [ ] Tests follow naming convention (`test_<func>_<scenario>_<result>`)
- [ ] Unit tests mock external dependencies
- [ ] Integration tests use real dependencies
- [ ] All tests pass (verified with `make test`)
- [ ] Coverage ≥ 80% (verified with coverage report)
- [ ] No flaky or time-dependent tests
- [ ] No dependent tests (each test is independent)
- [ ] Error paths tested (`@pytest.mark.error_path`)
- [ ] Happy paths tested (`@pytest.mark.happy_path`)
- [ ] Boundary conditions tested (`@pytest.mark.boundary`)
- [ ] Tests use real fixtures, not mockpatch
- [ ] Docstrings explain what is being tested

---

*Testing analysis: 2026-01-31*
