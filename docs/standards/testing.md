# Testing Standards

<!-- TOC START -->
- [Mindset](#mindset)
- [Structure (AAA)](#structure-aaa)
- [Imports in tests](#imports-in-tests)
- [Asserting results](#asserting-results)
- [Fixtures](#fixtures)
- [Singleton reset](#singleton-reset)
- [Golden files and examples](#golden-files-and-examples)
- [Parametrization](#parametrization)
- [What to avoid](#what-to-avoid)
- [Running tests](#running-tests)
- [Coverage](#coverage)
- [Related](#related)
<!-- TOC END -->

Guidelines for writing tests in the FLEXT monorepo. For the root engineering law, see `AGENTS.md`. For gate commands,
see `.agents/skills/flext-inviolable-rules/SKILL.md`.

## Mindset

- Tests protect behavior, not implementation.
- Prefer real flows over mocks when the cost is acceptable.
- A failing quality gate is a P0 incident; fix the root cause, do not suppress.

## Structure (AAA)

```python
def test_user_creation() -> None:
    # Arrange
    data = {"name": "Ada"}

    # Act
    user = m.User.model_validate(data)

    # Assert
    assert user.name == "Ada"
```

## Imports in tests

Use the same aliases as production code. Test facades may be named `TestsFlext<Project><Tier>` when the project exposes
one.

```python
from __future__ import annotations
```

## Asserting results

Use public API assertions. For `r[T]` results, assert on the public shape rather than private internals.

```python
def test_load_user() -> None:
    result = load_user(1)
    assert result.success
    assert result.unwrap().id == 1

    failure = load_user(-1)
    assert failure.failure
```

## Fixtures

Prefer project fixtures over ad-hoc setup. If a fixture does not exist, add it to the canonical `conftest.py` for the
affected tier.

```python
import pytest


@pytest.fixture
def sample_user() -> m.User:
    return m.User(id=1, name="Ada")
```

## Singleton reset

Rely on the autouse `reset_settings` fixture from `flext_tests`. When manual reset is required:

```python
from flext_core import FlextContainer, FlextSettings
from flext_tests import FlextTestsSettings

FlextSettings.reset_for_testing()
FlextTestsSettings.reset_for_testing()
FlextContainer.reset_for_testing()
```

## Golden files and examples

When output is stable and reviewable, prefer golden-file examples. Store them under
`tests/fixtures/` or the project-local equivalent. Update golden files
deliberately, never as a side effect of unrelated changes.

## Parametrization

Use `@pytest.mark.parametrize` for multi-case checks.

```python
import pytest


@pytest.mark.parametrize(("raw", "expected"), [("1", 1), ("42", 42)])
def test_parse_int(raw: str, expected: int) -> None:
    assert int(raw) == expected
```

## What to avoid

| Anti-pattern | Fix |
|--------------|-----|
| Testing private methods | test public behavior |
| Heavy mocking without real-flow fallback | prefer real dependencies or fakes |
| `assert True` smoke tests | assert a real invariant |
| Ignoring enforcement warnings | treat warnings as failures |
| Shared mutable fixtures | return fresh objects or use factories |

## Running tests

```bash
# narrow
make test PROJECT=<proj> MATCH=<expr>

# broad
make test PROJECT=<proj>
```

## Coverage

`pyproject.toml` sets `fail_under = 45` for the consolidated workspace. Project-local targets may be higher. Do not
lower the threshold to make a build pass.

## Related

- `AGENTS.md` — root engineering law
- `.agents/skills/flext-inviolable-rules/SKILL.md` — gate commands
- `.agents/skills/coding-standards/SKILL.md` — general coding standards
- `.agents/skills/flext-development-workflow/SKILL.md` — CI/CD lifecycle
