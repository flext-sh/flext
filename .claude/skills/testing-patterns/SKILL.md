---
name: testing-patterns
description: Testing patterns, anti-patterns, and guidelines for Python/pytest in FLEXT — fixtures, parameterization, mocking strategy, FlextResult testing, and TDD. Use when writing or reviewing tests.
---

# Testing Patterns

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival — consolidates 4 disabled skills

## Scope

- Test files across all FLEXT Python subprojects
- `flext-core/tests/` — core test suite patterns
- `conftest.py` files — shared fixtures

## References

- <https://docs.pytest.org/en/stable/>
- `.claude/skills/scripts-testing/SKILL.md` — test infrastructure (complementary)
- `.claude/skills/lib-returns/SKILL.md` — FlextResult testing patterns

## Rules

- Follow AAA pattern: Arrange, Act, Assert — one logical assertion per test.
- Name tests descriptively: `test_<unit>_<scenario>_<expected>`.
- Mock external dependencies (DB, network, filesystem) — never real services in unit tests.
- Test FlextResult operations by asserting `.is_success`/`.is_failure` and `.value`/`.error`.
- Never delete failing tests to make CI pass — fix the code instead.

## Instructions

### Test Structure (AAA)

```python
def test_user_creation_with_valid_data_returns_success():
    # Arrange
    data = {"name": "Alice", "email": "alice@example.com"}

    # Act
    result = create_user(data)

    # Assert
    assert result.is_success
    assert result.value.name == "Alice"
```

### Testing FlextResult

```python
from flext_core import r

def test_ok_result_contains_value():
    result = r[int].ok(42)
    assert result.is_success
    assert result.value == 42

def test_fail_result_contains_error():
    result = r[int].fail("not found")
    assert result.is_failure
    assert "not found" in result.error

def test_map_transforms_success_value():
    result = r[int].ok(5).map(lambda x: x * 2)
    assert result.value == 10

def test_flat_map_chains_results():
    result = r[int].ok(5).flat_map(lambda x: r[str].ok(str(x)))
    assert result.value == "5"
```

### Fixtures (conftest.py)

```python
import pytest

@pytest.fixture
def sample_user() -> User:
    return User(name="Test", email="test@example.com")

@pytest.fixture
def db_session(tmp_path):
    db = create_test_db(tmp_path / "test.db")
    yield db
    db.close()
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input_val,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase_transforms_correctly(input_val: str, expected: str):
    assert input_val.upper() == expected
```

### Mocking Strategy

```python
from unittest.mock import Mock, patch

def test_service_calls_repository():
    mock_repo = Mock()
    mock_repo.find.return_value = User(name="Alice")
    service = UserService(repo=mock_repo)

    result = service.get_user("123")

    mock_repo.find.assert_called_once_with("123")
    assert result.is_success
```

### Anti-Patterns to Avoid

**Testing mock behavior instead of real behavior**:

```python
# BAD: tests that the mock works, not the code
mock_service.process.return_value = "done"
result = mock_service.process("data")
assert result == "done"  # proves nothing about real code
```

**Test-only methods in production code**:

```python
# BAD: adding methods just for tests
class UserService:
    def _test_get_internal_state(self):  # test pollution
        return self._state
```

**Incomplete mock data**:

```python
# BAD: mock returns simplified data that hides bugs
mock_api.get.return_value = {"id": 1}  # missing required fields
```

### Test Organization

```
tests/
  conftest.py            # shared fixtures
  unit/
    test_result.py       # unit tests grouped by module
    test_service.py
  integration/
    test_api.py           # integration tests
    conftest.py           # integration-specific fixtures
```

## Workflow

1. Write a failing test for the desired behavior (Red).
2. Write minimal code to make the test pass (Green).
3. Refactor while keeping tests green.
4. Run full suite: `make test` or `pytest tests/ -q`.
5. Check coverage if required: `pytest --cov=src tests/`.

## Examples

Good:

```python
def test_parse_config_with_missing_key_returns_failure():
    result = parse_config({"host": "localhost"})  # missing "port"
    assert result.is_failure
    assert "port" in result.error
```

Why good: descriptive name, tests specific failure scenario, asserts on error content.

Bad:

```python
def test_config():
    config = parse_config({"host": "localhost", "port": 8080})
    assert config
```

Why bad: vague name, no scenario described, `assert config` doesn't verify anything meaningful.

## Verification

```bash
rg -n "def test_" --glob "test_*.py" flext-core/tests/ | wc -l
rg -n "@pytest.fixture" --glob "conftest.py" flext-core/tests/
rg -n "is_success\|is_failure\|\.value\|\.error" --glob "test_*.py" flext-core/tests/
```
