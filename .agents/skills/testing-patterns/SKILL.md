---
name: testing-patterns
description: Testing patterns, anti-patterns, and guidelines for Python/pytest in FLEXT — fixtures, parameterization, mocking strategy, r testing, and TDD. Use when writing or reviewing tests.

---

# Testing Patterns

**Reviewed**: 2026-04-06 | **Scope**: Disabled skill revival — consolidates 4 disabled skills

## Scope

- Test files across all FLEXT Python subprojects
- `flext-core/tests/` — core test suite patterns
- `conftest.py` files — shared fixtures

## References

- `AGENTS.md` — canonical governance source
- <https://docs.pytest.org/en/stable/>
- `.agents/skills/flext-mro-namespace-rules/SKILL.md`
- `.agents/skills/scripts-testing/SKILL.md` — test infrastructure (complementary)
- `.agents/skills/lib-returns/SKILL.md` — r testing patterns

## Rules

- Follow AAA pattern: Arrange, Act, Assert — one logical assertion per test.
- Name tests descriptively: `test_<unit>_<scenario>_<expected>`.
- Mock external dependencies (DB, network, filesystem) — never real services in unit tests.
- Test r operations by asserting `.success`/`.failure` and `.value`/`.error`.
- Never delete failing tests to make CI pass — fix the code instead.
- **Rule**: Tests MUST verify stable, public behavior — not implementation details. Do NOT assert on internal warning strings, tracebacks, private helper names, temporary alias spellings, internal class names, exact MRO composition, or any detail that can change without changing module behavior. If behavior is unchanged and only internals moved, the test must be rewritten.
- **Rule**: Public-behavior assertions also exclude concrete carrier details when the contract is structural. Prefer asserting observable `p.*`, `t.*`, or `r.*` behavior over asserting the exact concrete helper class used internally.
- **Rule**: Tests MUST demonstrate the EXACT SAME strict typing, Pydantic v2, r, p, and architectural discipline as production code. Test files are NOT exempt from ANY rule. Test fixtures MUST use `u.Field()`, typed models, and `r[T]` returns. Test data MUST use `t.*` types from `typings.py`. Test assertions on r MUST use `.success`/`.failure` and `.value`/`.error`. There is NO "test-only" relaxation of any typing, structural, or Pydantic v2 rule. Tests that violate these rules are themselves violations.
- **Rule**: Test facades use `TestsFlext<Project><Tier>` naming and keep test-only scope under `<Domain>.Tests`. Legacy `Flext<Project>Test<Tier>` names and flat nested wrappers around private mixins are migration debt, not patterns to repeat.
- **Rule**: ALL code in tests MUST follow "Pydantic v2 way": `u.Field()` for field declarations, `ConfigDict(...)` for settings, validation centralized in models via `@u.field_validator`/`@u.model_validator`/`@u.computed_field`. Enums/Mappings/Literals from `constants.py` (`c.*`). JSON via `model_dump_json()`, `model_validate_json()`, `TypeAdapter` — never raw `json.loads()`/`json.dumps()`. Test models MUST inherit via MRO from FLEXT base models.
- **Rule**: Compatibility wrappers, non-business validation fallbacks, legacy test code, and `OldName = NewName` compatibility aliases are FORBIDDEN in test code. Legacy test patterns are DELETED and replaced with canonical patterns.
- **Rule**: Every test change MUST pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors. Linter suppression comments are FORBIDDEN without real internet citations, business necessity, and per-line scope. Global suppressions are FORBIDDEN.

## Instructions

### Test Structure (AAA)

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, p, r, t


class UserRecord(m.ArbitraryTypesModel):
    """User record stub for the example."""

    name: Annotated[t.NonEmptyStr, u.Field(description="User name")]
    email: Annotated[t.NonEmptyStr, u.Field(description="User email")]


def create_user(name: str, email: str) -> p.Result[UserRecord]:
    """Create a user from raw inputs."""
    return r[UserRecord].ok(UserRecord(name=name, email=email))


def test_user_creation_with_valid_data_returns_success() -> None:
    """AAA pattern: arrange, act, assert."""
    # Arrange
    name = "Alice"
    email = "alice@example.com"

    # Act
    result = create_user(name=name, email=email)

    # Assert
    assert result.success
    assert result.unwrap().name == "Alice"
```

### Testing r

```python
from __future__ import annotations

from flext_core import r


def test_ok_result_contains_value() -> None:
    """ok() result exposes the value via unwrap()."""
    result = r[int].ok(42)
    assert result.success
    assert result.unwrap() == 42


def test_fail_result_contains_error() -> None:
    """fail() result exposes the error message."""
    result = r[int].fail("not found")
    assert result.failure
    assert result.error is not None
    assert "not found" in result.error


def test_map_transforms_success_value() -> None:
    """map() chains a pure transformation on the success branch."""
    result = r[int].ok(5).map(lambda x: x * 2)
    assert result.unwrap() == 10


def _int_to_str(x: int) -> r[str]:
    return r[str].ok(str(x))


def test_flat_map_chains_results() -> None:
    """flat_map() chains another r-returning computation."""
    result = r[int].ok(5).flat_map(_int_to_str)
    assert result.unwrap() == "5"
```

### Fixtures (conftest.py)

```python
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

import pytest

from flext_core import m, t


class UserFixture(m.ArbitraryTypesModel):
    """User fixture model."""

    name: Annotated[t.NonEmptyStr, u.Field(description="User name")]
    email: Annotated[t.NonEmptyStr, u.Field(description="User email")]


@pytest.fixture
def sample_user() -> UserFixture:
    """Deterministic sample user."""
    return UserFixture(name="Test", email="test@example.com")


@pytest.fixture
def db_path(tmp_path: Path) -> Iterator[Path]:
    """Isolated database file path per test."""
    path = tmp_path / "test.db"
    yield path
    if path.exists():
        path.unlink()
```

### Parameterized Tests

```python
from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("", ""),
    ],
)
def test_uppercase_transforms_correctly(input_val: str, expected: str) -> None:
    """Parameterized scenarios for the uppercase transformation."""
    assert input_val.upper() == expected
```

### Mocking Strategy

```python
from __future__ import annotations

from typing import Annotated
from unittest.mock import Mock

from flext_core import m, p, r, t


class UserRecord(m.ArbitraryTypesModel):
    """User record stub."""

    name: Annotated[t.NonEmptyStr, u.Field(description="User name")]


class UserService:
    """Service under test — stubbed for illustration."""

    def __init__(self, repo: Mock) -> None:
        """Store the repository reference."""
        self._repo = repo

    def get_user(self, user_id: str) -> p.Result[UserRecord]:
        """Look up a user via the repository."""
        user: UserRecord = self._repo.find(user_id)
        return r[UserRecord].ok(user)


def test_service_calls_repository() -> None:
    """Service delegates lookup to its repository dependency."""
    mock_repo = Mock()
    mock_repo.find.return_value = UserRecord(name="Alice")
    service = UserService(repo=mock_repo)

    result = service.get_user("123")

    mock_repo.find.assert_called_once_with("123")
    assert result.success
```

### Anti-Patterns to Avoid

**Testing mock behavior instead of real behavior**:

```python
from __future__ import annotations

from unittest.mock import Mock

# BAD: tests that the mock works, not the code
mock_service = Mock()
mock_service.process.return_value = "done"
result = mock_service.process("data")
assert result == "done"  # proves nothing about real code
```

**Testing internal implementation details instead of contract behavior**:

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, t


class CliResult(m.ArbitraryTypesModel):
    """Stub CLI execution result."""

    exit_code: Annotated[int, u.Field(description="Process exit code")]
    output: Annotated[t.NonEmptyStr, u.Field(description="Captured output")]


def make_result() -> CliResult:
    """Stub result for illustration."""
    return CliResult(exit_code=0, output="unexpected_success True")


result = make_result()

# GOOD: behavioral assertion
assert result.exit_code == 0
assert "unexpected_success True" in result.output
```

**Test-only methods in production code**:

```python
from __future__ import annotations


class UserService:
    """Illustrates the anti-pattern of test-only production methods."""

    def __init__(self) -> None:
        """Set up internal state."""
        self._state = "active"

    # BAD: adding methods just for tests
    def _test_get_internal_state(self) -> str:
        """Test pollution — exposes internals solely for tests."""
        return self._state
```

**Incomplete mock data**:

```python
from __future__ import annotations

from unittest.mock import Mock

# BAD: mock returns simplified data that hides bugs
mock_api = Mock()
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
4. Run full suite with standardized gate: `make test`.
5. For focused runs, use selectors: `make test PYTEST_ARGS="-k <expr>"`.

## Examples

Good:

```python
from __future__ import annotations

from collections.abc import Mapping

from flext_core import p, r


def parse_config(raw: Mapping[str, str | int]) -> p.Result[Mapping[str, str | int]]:
    """Require both host and port keys, return error otherwise."""
    if "port" not in raw:
        return r[Mapping[str, str | int]].fail("port is required")
    return r[Mapping[str, str | int]].ok(raw)


def test_parse_config_with_missing_key_returns_failure() -> None:
    """Descriptive name, specific failure scenario, asserts on error content."""
    result = parse_config({"host": "localhost"})  # missing "port"
    assert result.failure
    assert result.error is not None
    assert "port" in result.error
```

Why good: descriptive name, tests specific failure scenario, asserts on error content.

Bad:

```python
from __future__ import annotations

from collections.abc import Mapping

from flext_core import p, r


def parse_config(raw: Mapping[str, str | int]) -> p.Result[Mapping[str, str | int]]:
    """Stub matching the Good example."""
    return r[Mapping[str, str | int]].ok(raw)


def test_config() -> None:
    """Vague — no scenario, assertion reveals nothing about behavior."""
    settings = parse_config({"host": "localhost", "port": 8080})
    assert settings  # BAD: doesn't verify anything meaningful
```

Why bad: vague name, no scenario described, `assert settings` doesn't verify anything meaningful.

## Verification

```bash
make PROJECT=flext-core test
make PROJECT=flext-core validate
make PROJECTS="flext-core flext-api" test
```
