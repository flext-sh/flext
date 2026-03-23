# Testing Patterns

**Analysis Date:** 2026-03-23

## Test Framework

**Runner:**
- pytest 8.4+
- Configuration: `pyproject.toml` `[tool.pytest.ini_options]`
- Key settings:
  - `minversion = "8.0"`
  - `python_files = ["*_test.py", "*_tests.py", "test_*.py"]`
  - `python_classes = ["Test*"]`
  - `addopts = ["--strict-markers"]`
  - `enable_assertion_pass_hook = true`

**Assertion Library:**
- pytest's built-in assertions (no pytest-sugar, but available for enhanced output)
- Pydantic `ValidationError` for model validation assertions
- Helper assertions in `tests.conftest`: `assert_validates()`, `assert_rejects()`

**Run Commands:**
```bash
make test              # Run all tests
make test-unit        # Run unit tests only
make test-integration # Run integration tests
make test-coverage    # Run with coverage report
make test-watch       # Watch mode (if available)
```

Coverage:
- Tool: pytest-cov
- Report type: Coverage percentage with missing line counts
- Target: 45% minimum (configured as `fail_under` in pyproject.toml)
- View coverage: Run with `pytest --cov=src --cov-report=html`

## Test File Organization

**Location:**
- Co-located with source: `src/module.py` → `tests/unit/test_module.py`
- Integration tests: Separate `tests/integration/` directory
- Test infrastructure: `tests/infra/` or `tests/conftest.py` for shared fixtures
- Utilities/helpers: `tests/unit/helpers/` or `tests/unit/test_utils.py`

**Naming:**
- Test classes: `Test{Module}` (e.g., `TestResult`, `TestModels`, `TestDispatcher`)
- Test functions: `test_{feature}_{scenario}` (e.g., `test_creation_success`, `test_map_with_ok`)
- Parametrized tests: `test_{feature}[{param_id}]` (pytest generates suffix)
- Fixtures: lowercase with snake_case (e.g., `clean_container`, `temp_file`, `mock_service`)

**Structure:**
```
flext-core/
├── tests/
│   ├── conftest.py              # Root pytest configuration & global fixtures
│   ├── test_utils.py            # Shared test utilities
│   ├── unit/
│   │   ├── test_result.py       # Unit tests for result.py
│   │   ├── test_models.py       # Unit tests for models.py
│   │   ├── helpers/
│   │   │   └── scenarios.py     # Test scenario definitions
│   │   └── contracts/           # Type contracts for tests
│   └── integration/
│       ├── test_service.py      # Integration tests
│       └── patterns/            # Pattern validation tests
```

## Test Structure

**Suite Organization:**
```python
from __future__ import annotations

import pytest
from flext_tests import t, tm, u
from pydantic import BaseModel, ConfigDict, Field

from flext_core import r, FlextModels as m


class TestResult:
    """Test suite for r - railway-oriented result handling."""

    class ResultScenario(BaseModel):
        """Parameterized test scenario."""

        model_config = ConfigDict(frozen=True)
        name: str
        operation: str
        value: t.NormalizedValue
        is_success_expected: bool = True

    # Class-level test data
    SCENARIOS = [
        ResultScenario(name="ok_string", operation="creation_success", value="test"),
        ResultScenario(
            name="fail_string",
            operation="creation_failure",
            value="error",
            is_success_expected=False,
        ),
    ]

    @pytest.mark.unit
    def test_creation_success(self):
        """Test creating successful result."""
        result = r[str].ok("value")
        assert result.is_ok()

    @pytest.mark.unit
    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_result_operations(self, scenario):
        """Test result operations via parametrization."""
        # Use scenario.* for data-driven testing
        if scenario.is_success_expected:
            result = r[str].ok(scenario.value)
            assert result.is_ok()
```

**Patterns:**
- Setup: Fixtures via `@pytest.fixture` in conftest.py (never setUp/tearDown methods)
- Teardown: Use fixture yield pattern or autouse fixtures that auto-cleanup
- Assertion: Direct pytest assertions, not `self.assertEqual()`
- Parametrization: Use `@pytest.mark.parametrize` with list of scenarios or individual values
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e` for test categorization

## Mocking

**Framework:** `pytest-mock` (provides `mocker` fixture)

**Patterns:**
```python
from unittest.mock import Mock, patch
import pytest


class TestService:
    def test_with_mocker(self, mocker):
        """Mock using pytest-mock fixture."""
        mock_logger = mocker.Mock()
        mocker.patch("flext_core.loggings.logger", mock_logger)

        # Execute code that uses logger
        result = my_function()

        # Assert mock was called correctly
        mock_logger.info.assert_called_once()

    @pytest.mark.unit
    def test_with_patch(self):
        """Mock using unittest.mock.patch."""
        with patch("module.external_service") as mock_service:
            mock_service.return_value = "mocked_data"
            result = function_using_service()
            mock_service.assert_called_once()
```

**What to Mock:**
- External APIs (HTTP clients, databases, file systems)
- Time-dependent operations (use `freezegun` for time mocking)
- Randomness (random seeds or mocking `random` module)
- Expensive operations (database queries when testing logic, not integration)
- IO operations (file reads/writes when unit testing, use temp dirs in integration)

**What NOT to Mock:**
- Pydantic models (use real instances with test data)
- Business logic under test (test actual behavior)
- Result types (`r[T]`) – construct real instances
- Domain objects (entities, aggregates) – use real models with test data
- Utility functions already tested elsewhere – reuse them

## Fixtures and Factories

**Test Data:**
```python
# fixture in conftest.py
@pytest.fixture
def sample_data() -> Mapping[str, t.NormalizedValue]:
    """Provide sample test data."""
    return {
        "string": "test_value",
        "integer": 42,
        "list": ["item1", "item2"],
    }


# Use in test
def test_with_sample_data(self, sample_data):
    result = process(sample_data)
    assert result.is_ok()
```

**Location:**
- Global fixtures: `tests/conftest.py` (auto-discovered by pytest)
- Module-specific: `tests/unit/test_module.py::conftest_<module>()` or same file
- Test class fixtures: `@pytest.fixture` methods in test class (less preferred)
- Reusable helpers: `tests/unit/helpers/scenarios.py` for scenario classes

**Fixture Patterns:**
- Use `@pytest.fixture` decorator (not class-based `setUp`)
- Yield for cleanup: `yield value` instead of return for auto-cleanup
- Scope: `scope="function"` (default, per test), `scope="module"`, `scope="session"`
- Autouse: `autouse=True` for fixtures that always run (e.g., global cleanup)

```python
@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global singletons after each test."""
    yield
    FlextContainer.reset_for_testing()
    FlextSettings.reset_for_testing()


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for test files."""
    return tmp_path
```

## Coverage

**Requirements:** 45% minimum (configurable per project)

**View Coverage:**
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

**Configuration:**
- Located in `pyproject.toml` `[tool.coverage.report]`
- Settings:
  - `fail_under = 45` (fail build if coverage below this)
  - `precision = 2` (decimal places in reports)
  - `show_missing = true` (show uncovered lines)

## Test Types

**Unit Tests:**
- Scope: Single function/class in isolation
- Speed: Fast (< 100ms per test)
- Setup: Minimal, fixtures for clean state
- Location: `tests/unit/test_*.py`
- Markers: `@pytest.mark.unit`
- Examples: testing `Result.map()`, `Model.validate()`, `u.parse_uri()`

**Integration Tests:**
- Scope: Multiple components working together
- Speed: Moderate (can be seconds)
- Setup: Real instances, temp databases, mock external services
- Location: `tests/integration/test_*.py`
- Markers: `@pytest.mark.integration`
- Examples: testing DI container with services, dispatcher with handlers, CQRS flows

**E2E Tests:**
- Scope: Full application workflows
- Speed: Slow (requires full setup/teardown)
- Setup: Real or near-real environment
- Location: `tests/e2e/test_*.py` (if used)
- Markers: `@pytest.mark.e2e`
- Not extensively used in flext-core (integration tests are primary)

## Common Patterns

**Async Testing:**
```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test async code with pytest-asyncio."""
    result = await async_operation()
    assert result.is_ok()


# Or use: pytest-asyncio auto mode
# (set asyncio_mode = "auto" in pytest.ini)
```

**Error Testing:**
```python
from pydantic import ValidationError


def test_validation_failure():
    """Test that invalid data raises ValidationError."""
    with pytest.raises(ValidationError):
        m.MyModel(invalid_field="not_an_int")


def test_result_failure():
    """Test result failure cases."""
    result = r[str].fail("error message")
    assert result.is_fail()
    assert result.unwrap_or("default") == "default"
```

**Parametrized Testing:**
```python
# Inline parameter sets
@pytest.mark.parametrize(
    "input,expected",
    [
        ("valid_port", 8080),
        ("invalid_port", "error"),
        ("edge_case", 1),
    ],
)
def test_port_parsing(input, expected):
    result = parse_port(input)
    assert result == expected


# Class-level scenarios (DRY)
class TestResult:
    SCENARIOS = [
        {"name": "ok", "value": "success", "is_ok": True},
        {"name": "fail", "value": "error", "is_ok": False},
    ]

    @pytest.mark.parametrize("scenario", SCENARIOS)
    def test_result(self, scenario):
        result = create_result(scenario["value"])
        assert result.is_ok() == scenario["is_ok"]
```

**Test Isolation:**
```python
@pytest.fixture(autouse=True)
def isolated_state():
    """Ensure tests don't interfere via global state."""
    yield
    # Cleanup: clear singletons, reset registries, etc.
    FlextContainer.reset_for_testing()
    FlextSettings.reset_for_testing()


# Avoid sharing mutable fixtures
@pytest.fixture
def clean_container():
    """Fresh container per test."""
    container = FlextContainer()
    container.clear_all()
    return container
```

## Markers

**Available Markers** (configured in `pyproject.toml`):
- `@pytest.mark.unit` – Unit tests (fast, isolated)
- `@pytest.mark.integration` – Integration tests (multiple components)
- `@pytest.mark.e2e` – End-to-end tests (full workflows)
- `@pytest.mark.docker` – Tests requiring Docker
- `@pytest.mark.slow` – Slow-running tests
- `@pytest.mark.stress` – Stress/load tests
- `@pytest.mark.performance` – Performance benchmarks
- `@pytest.mark.resilience` – Resilience/reliability tests
- `@pytest.mark.edge_cases` – Edge case validation
- `@pytest.mark.advanced` – Advanced pattern tests
- `@pytest.mark.architecture` – Architecture validation tests
- `@pytest.mark.ddd` – Domain-driven design pattern tests
- `@pytest.mark.coverage` – Coverage-focused tests
- `@pytest.mark.core` – Core functionality tests

Use strictly: `@pytest.mark.unit` not `@pytest.mark.test_unit`.

## Test Naming Checklist

- Test class: `Test{Module}` (matches `pytest_classes`)
- Test function: `test_{feature}_{scenario}`
- File name: `test_{module}.py` (matches `pytest_files`)
- Fixtures: snake_case (not CamelCase)
- Test data: Define as class attributes (SCENARIOS, FIXTURES) or fixtures
- Parametrization: Use `@pytest.mark.parametrize` with clear IDs
- Markers: Always include at least one tier marker (`@pytest.mark.unit` or `@pytest.mark.integration`)

---

*Testing analysis: 2026-03-23*
