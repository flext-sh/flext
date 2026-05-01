---
name: testing-patterns
description: Testing discipline for Python/pytest in FLEXT — public-API-only assertions, real-flow-over-mocks, enforcement warnings as failures, golden-file examples, AAA structure, r[T] result assertions, facade-only imports. Use when writing or reviewing any test, fixture, or example.
---

# Testing Patterns

**Reviewed**: 2026-04-20 | **Scope**: Python/pytest testing discipline — public-API-only, no-mock-pretend, enforcement warnings as failures, golden-file examples, facade-only imports in tests

## Scope

- Test files across all 34 FLEXT Python subprojects (`tests/**`).
- `flext-core/tests/` — core test suite patterns.
- `conftest.py` files — shared fixtures.
- `examples/**` across every project — treated as integration tests via golden `.expected` snapshots.

## References

- `AGENTS.md` — canonical governance source
- `.agents/skills/pydantic-v2-governance/SKILL.md` — Model HARD rules the tests must also respect
- `.agents/skills/pydantic-v2-patterns/SKILL.md` — facade-only imports (applies to tests equally)
- `.agents/skills/flext-mro-namespace-rules/SKILL.md`
- `.agents/skills/scripts-testing/SKILL.md` — test infrastructure (complementary)
- `.agents/skills/lib-returns/SKILL.md` — `r[T]` testing patterns
- <https://docs.pytest.org/en/stable/>

## Rules

- **AAA structure**: Arrange, Act, Assert — one logical assertion per test. Descriptive names: `test_<unit>_<scenario>_<expected>`.
- **Tests validate stable, public behavior** — never private implementation details. BANNED assertions: internal warning strings, traceback text, private helper names (`hasattr(obj, "_private")`), temporary alias spellings, internal class names, exact MRO composition. If behavior is unchanged and only internals moved, the test MUST be rewritten.
- **Public API only**: tests exercise `tm.that(...)`, `tm.ok(...)`, public classmethods, documented methods. `obj._helper is None`, `obj._cache is not None` assertions are violations even when they pass.
- **Structural contracts over concrete carriers**: prefer asserting observable `p.*`, `t.*`, or `r.*` behavior over asserting the exact concrete helper class used internally.
- **Real flow over mocks**: mocks are allowed ONLY at true I/O boundaries that cannot be instantiated in-process (remote HTTP/IdP/DB, external message brokers). Mocks of services, models, repositories, or any in-process class are FORBIDDEN — rewrite to use the real class with a test fixture. Tests that cannot reach the real path MUST be deleted, not retrofitted with fakes.
- **Result assertions**: `r[T]` outcomes are asserted via `.success`/`.failure` + `.unwrap()`/`.error`. Never introspect the `Ok` / `Err` concrete carriers.
- **Enforcement warnings are failures**: every project's test suite MUST treat `UserWarning` from HARD-rule enforcement (`_flext_enforcement_exempt`, model HARD-rule `UserWarning`s, etc.) as a failure. Configure `filterwarnings = ["error::UserWarning"]` in `pyproject.toml`.
- **No test-only code in production**: if a `src/` symbol exists only to support tests, DELETE it from production and move the fixture logic into `tests/`.
- **Golden-file examples**: every file under `examples/` MUST have a matching `.expected` snapshot; `pytest` runs the example and diffs stdout/stderr. Prose-only examples are forbidden.
- **Same discipline as production**: tests are NOT exempt from typing, Pydantic v2, architectural, or import rules. Test fixtures MUST use `m.Field()`, typed models, and `r[T]` returns. Test data MUST use `t.*` types from `typings.py`.
- **Test facades** use `TestsFlext<Project><Tier>` naming and keep test-only scope under `<Domain>.Tests`. Legacy `Flext<Project>Test<Tier>` names are migration debt.
- **Facade-only imports**: direct `from pydantic import ...` / `from pydantic_core import ...` is BANNED in tests (same rule as production). Every Pydantic construct goes through the canonical aliases `m.*` / `u.*` (e.g. `m.Field`, `m.ConfigDict`, `m.BeforeValidator`, `u.PrivateAttr`, `u.computed_field`, `u.field_validator`, `u.model_validator`). JSON via `model_dump_json()`, `model_validate_json()`, cached `m.TypeAdapter` — never raw `json.loads()`/`json.dumps()`.
- **No compatibility wrappers / legacy aliases** in test code. Legacy test patterns are DELETED and replaced with canonical patterns.
- **All 4 linters clean**: every test change passes ruff + mypy + pyright + pyrefly with ZERO errors. Per-line suppressions require real citations + business necessity. Global suppressions are FORBIDDEN.
- **Never delete failing tests to make CI pass** — fix the code instead.
- **Refactor alignment**: when production code is simplified by removing wrappers, converters, or compatibility layers, tests must be rewritten in the same cycle to target the remaining public behavior and shared `conftest.py` fixtures rather than the removed internals.

## Instructions

### Test Structure (AAA)

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, p, r, t


class UserRecord(m.ArbitraryTypesModel):
    """User record stub for the example."""

    name: Annotated[t.NonEmptyStr, m.Field(description="User name")]
    email: Annotated[t.NonEmptyStr, m.Field(description="User email")]


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

### Testing `r[T]`

```python
from __future__ import annotations

from flext_core import r


def test_ok_result_contains_value() -> None:
    result = r[int].ok(42)
    assert result.success
    assert result.unwrap() == 42


def test_fail_result_contains_error() -> None:
    result = r[int].fail("not found")
    assert result.failure
    assert result.error is not None
    assert "not found" in result.error


def test_map_transforms_success_value() -> None:
    result = r[int].ok(5).map(lambda x: x * 2)
    assert result.unwrap() == 10


def _int_to_str(x: int) -> r[str]:
    return r[str].ok(str(x))


def test_flat_map_chains_results() -> None:
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

    name: Annotated[t.NonEmptyStr, m.Field(description="User name")]
    email: Annotated[t.NonEmptyStr, m.Field(description="User email")]


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
    assert input_val.upper() == expected
```

### Real flow — no mock-pretend

Prefer real fixtures over mocks for any in-process class. Mocks only at true I/O boundaries (remote HTTP/IdP/DB). When a mock is genuinely required, use a narrow `p.*` protocol so the test substitutes structurally, not through `unittest.mock.Mock(spec=...)`.

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, p, r, t


class UserRecord(m.ArbitraryTypesModel):
    """User record."""

    name: Annotated[t.NonEmptyStr, m.Field(description="User name")]


class InMemoryUserRepo:
    """Real repository backed by a dict — substitutes the production repo in-process."""

    def __init__(self) -> None:
        self._store: dict[str, UserRecord] = {}

    def save(self, user_id: str, user: UserRecord) -> None:
        self._store[user_id] = user

    def find(self, user_id: str) -> UserRecord | None:
        return self._store.get(user_id)


class UserService:
    """Service under test — accepts any `p.UserRepo` structurally."""

    def __init__(self, repo: p.UserRepo) -> None:
        self._repo = repo

    def get_user(self, user_id: str) -> p.Result[UserRecord]:
        user = self._repo.find(user_id)
        if user is None:
            return r[UserRecord].fail(f"unknown user: {user_id}")
        return r[UserRecord].ok(user)


def test_service_returns_user_from_repo() -> None:
    repo = InMemoryUserRepo()
    repo.save("123", UserRecord(name="Alice"))
    service = UserService(repo=repo)

    result = service.get_user("123")

    assert result.success
    assert result.unwrap().name == "Alice"
```

Why good: the test exercises the REAL `UserService` against a REAL in-memory repository; the only substitution is at a structural `p.UserRepo` boundary — no `unittest.mock.Mock`.

### Anti-Patterns (FORBIDDEN — do NOT copy)

**1. Mock-pretend of an in-process class**:

```text
# FORBIDDEN: in-process class mocked — tests the mock, not the code
mock_repo = Mock(spec=UserRepo)
mock_repo.find.return_value = UserRecord(name="Alice")
service = UserService(repo=mock_repo)
assert service.get_user("123").success
```

Why bad: the real `UserRepo` is instantiable in-process; substituting a `Mock` tests the mock's return value, not the service's real behavior. Rewrite with an in-memory fixture or a structural `p.*` protocol stub.

**2. Assertion on private state**:

```text
# FORBIDDEN: pins implementation detail
service = UserService(repo=InMemoryUserRepo())
assert hasattr(service, "_repo")        # private attribute check
assert service._cache is not None       # private attribute check
```

Why bad: refactoring away `_cache` or `_repo` breaks the test even when public behavior is unchanged. Assert on observable outcomes (the `r[T]` value) instead.

**3. Test-only method on a production class**:

```text
# FORBIDDEN: exposes internals solely for tests
class UserService:
    def _test_get_internal_state(self) -> str: ...   # test pollution
```

Why bad: production surface grows to satisfy tests. Remove the helper; widen the legitimate public contract or assert on a public side-effect.

**4. Incomplete mock payload**:

```text
# FORBIDDEN: mock returns fake-shape data that hides real schema drift
mock_api.get.return_value = {"id": 1}   # required fields missing
```

Why bad: the real API response schema is never exercised; schema drift goes undetected until production.

### Test Organization

```
tests/
  conftest.py            # shared fixtures
  unit/
    test_result.py       # unit tests grouped by module
    test_service.py
  integration/
    test_api.py          # integration tests
    conftest.py          # integration-specific fixtures
```

## Workflow

1. Write a failing test for the desired PUBLIC behavior (Red).
2. Write minimal code to make the test pass (Green).
3. Refactor while keeping tests green (Refactor).
4. Run full suite with standardized gate: `make test`.
5. For focused runs, use selectors: `make test PYTEST_ARGS="-k <expr>"`.
6. Add `filterwarnings = ["error::UserWarning"]` to `pyproject.toml` if not already present, then re-run.

## Examples

Good — behavior-focused, descriptive name:

```python
from __future__ import annotations

from collections.abc import Mapping

from flext_core import p, r


def parse_config(raw: t.MappingKV[str, str | int]) -> p.Result[Mapping[str, str | int]]:
    if "port" not in raw:
        return r[Mapping[str, str | int]].fail("port is required")
    return r[Mapping[str, str | int]].ok(raw)


def test_parse_config_with_missing_key_returns_failure() -> None:
    result = parse_config({"host": "localhost"})
    assert result.failure
    assert result.error is not None
    assert "port" in result.error
```

Why good: descriptive name, tests the specific failure scenario, asserts on public error content.

Bad — vague, meaningless assertion:

```text
def test_config() -> None:
    settings = parse_config({"host": "localhost", "port": 8080})
    assert settings   # doesn't verify anything — violates public-behavior rule
```

Why bad: no scenario described; `assert settings` is trivially true for any non-empty value; refactoring is un-guarded.

## Verification

- `rg -n 'hasattr\([^,]+,\s*[\"'"'"']_' --type py tests/ --glob '!**/.venv/**'` → expect zero hits.
- `rg -n '_[a-z_]+\s+is (None|not None)' --type py tests/` → audit every hit.
- `rg -n '@patch|MagicMock\(|Mock\(' --type py tests/` → every remaining hit MUST resolve to a true I/O boundary; otherwise rewrite.
- `rg -n "^(import pydantic|from pydantic|from pydantic_core)" --type py tests/ --glob '!**/.venv/**'` → zero hits.
- `PYTHONWARNINGS=error::UserWarning pytest -q` → clean exit.
- `make PROJECT=<name> test` + `make PROJECT=<name> val` — 0 errors, 0 warnings.
