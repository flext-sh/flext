# FLEXT Agent Instructions

**Python 3.13+ monorepo** with 30+ subprojects. Enterprise data platform using Railway-Oriented Programming, CQRS, and Clean Architecture.

## Quick Reference

```bash
make check              # lint + type-check (quick validation)
make validate           # full pipeline: lint + types + security + test
make PROJECT=flext-core validate  # single project

# Single test (from subproject dir or workspace)
cd flext-core && poetry run pytest tests/test_file.py::test_name -v
poetry run pytest -k "pattern" -v          # match by pattern
poetry run pytest -m unit -v               # unit tests only
poetry run pytest --lf -x                  # last failed, stop on first
PYTHONPATH=flext-core/src poetry run pytest flext-core/tests/unit/test_result.py -v
```

## Package Management (MANDATORY - Poetry Only)

**All Python package operations MUST use Poetry commands:**

```bash
# Add new dependency
poetry add <package>                    # Production dependency
poetry add --group dev <package>        # Development dependency

# Update dependencies
poetry update <package>                 # Update specific package
poetry update                           # Update all packages

# Remove dependency
poetry remove <package>

# Install from lock file (reproducible builds)
poetry install                          # All dependencies
poetry install --only main              # Production only
poetry install --sync                   # Sync with lock file

# Show dependency info
poetry show <package>                   # Package details
poetry show --tree                      # Dependency tree
```

**FORBIDDEN**: Direct `pip install`, `pip uninstall`, or manual `pyproject.toml` edits for dependencies.

## Build/Lint/Test Commands

| Command | Description |
|---------|-------------|
| `make lint` | Ruff linting (ZERO violations) |
| `make format` | Auto-format with Ruff |
| `make type-check` | Pyrefly (ZERO errors) |
| `make test` | Tests with 80% coverage |
| `make test-fast` | Tests without coverage |
| `make validate` | Full pipeline (before PR) |

## Code Style

### Import Order & Short Aliases (MANDATORY)

```python
"""Module docstring."""
from __future__ import annotations

import sys                              # 1. Standard library
from pydantic import BaseModel          # 2. Third-party
from flext_core.result import r         # 3. Local with short aliases
from flext_core.typings import t, T, U
from flext_core.constants import c
from flext_core.protocols import p
from flext_core.models import m
from flext_core.utilities import u
from flext_core.exceptions import e
from flext_core.context import x
```

### Type Annotations (Python 3.13+)

```python
def process(items: list[str]) -> dict[str, int]: ...
def maybe(x: str | None) -> bool: ...       # NOT Optional[str]

# Centralized types require FULL namespace
config: t.Types.ConfigurationDict = {}
status: c.Core.CommonStatus = c.Core.CommonStatus.OK
```

### Railway-Oriented Programming

```python
from flext_core.result import r

def validate_user(data: dict) -> r[User]:
    """Return r[T] instead of raising exceptions."""
    if not data.get("email"):
        return r[User].fail("Email required")
    return r[User].ok(User(**data))

# Chain operations
result = validate_input(data).flat_map(transform).flat_map(save)
if result.is_success:
    user = result.value
```

### Naming Conventions

- **Classes**: `PascalCase` (`Flext` prefix for framework)
- **Functions/Variables**: `snake_case`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Type aliases**: Short lowercase (`r`, `t`, `c`, `p`, `m`, `u`, `e`, `x`)

## Architecture

### Module Tiers (Lower NEVER imports higher)

```
Tier 0: constants.py, typings.py, protocols.py  (ZERO internal imports)
Tier 1: models.py, utilities.py
Tier 2: servers/*.py
Tier 3: services/*.py, api.py
```

## Testing

- **80% coverage minimum** enforced
- **Real implementations** over mocks
- **Naming**: `test_<function>_<scenario>_<expected>`

```python
def test_validate_user_with_valid_email_returns_success():
    data = {"email": "user@example.com"}  # Arrange
    result = validate_user(data)           # Act
    assert result.is_success               # Assert
```

## Quality Thresholds

| Check | Tool | Threshold |
|-------|------|-----------|
| Coverage | pytest-cov | 80% minimum |
| Types | Pyrefly | ZERO errors |
| Linting | Ruff | ZERO violations |
| Security | Bandit | ZERO high/medium |

## Pydantic 2 Patterns (MANDATORY)

### TypeGuard Pattern (Replaces cast())

Use TypeGuards for type narrowing instead of cast():

```python
from flext_core.utilities import u

# Type-safe narrowing without cast()
if u.Guards.is_configuration_dict(data):
    config = data  # Type narrowed automatically
    config.app_name  # Safe access
```

Benefits:
- Type-safe narrowing without cast()
- No type: ignore comments
- Runtime validation
- Better IDE support

### Hierarchical Model Organization

Models are organized in nested namespaces for maximum reuse:

```python
from flext_core.models import m

config: m.Core.Config = ...
context: m.Core.Context = ...
result: m.Result.Success = ...
```

Pattern:
- `m.Base` - Standard ConfigDict
- `m.Core.*` - Core framework models
- `m.Result.*` - Result models
- `m.Data.*` - Data models

### ConfigDict Standards

All models use standard ConfigDict settings:

```python
model_config = ConfigDict(
    validate_assignment=True,
    use_enum_values=True,
    extra="forbid",
    str_strip_whitespace=True,
)
```

Settings:
- `validate_assignment`: Validate on attribute assignment
- `use_enum_values`: Serialize enums to values
- `extra="forbid"`: Reject unknown fields
- `str_strip_whitespace`: Clean string inputs

### Modern Validator Patterns (Pydantic 2.11+)

Use modern validators instead of deprecated patterns:

```python
from pydantic import field_validator, model_validator, computed_field

class User(BaseModel):
    email: str
    password: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if len(self.password) < 8:
            raise ValueError("Password too short")
        return self
    
    @computed_field
    @property
    def domain(self) -> str:
        return self.email.split("@")[1]
```

Patterns:
- `@field_validator`: Validate individual fields
- `@model_validator`: Validate entire model
- `@computed_field`: Computed properties

## Forbidden Patterns (ZERO TOLERANCE)

```python
from typing import Any          # NO Any
cast(SomeType, value)           # NO cast()
# type: ignore                  # NO type ignores
if TYPE_CHECKING:               # NO TYPE_CHECKING blocks
Optional[X]                     # Use X | None
TypedDict                       # Use Pydantic models instead
```

## Key Patterns

| Pattern | Usage |
|---------|-------|
| `r[T].ok(value)` | Success result |
| `r[T].fail(msg)` | Failure result |
| `result.flat_map(fn)` | Chain operations |
| `result.is_success` | Check success |
| `result.value` | Get value |
| `p.Domain.Service` | Protocol (full namespace) |
| `m.Entity.Entity` | Model (full namespace) |
| `c.Core.CONSTANT` | Constant (full namespace) |

## Dependency Injection

```python
from flext_core import FlextContainer, Provide, inject

container = FlextContainer()
# Auto-registered: "config", "logger", "context"

@inject
def my_handler(config=Provide["config"], logger=Provide["logger"]):
    logger.info("Executed", app_name=config.app_name)
```

## Error Handling

```python
def process_data(data: str) -> r[ProcessedData]:
    try:
        return r[ProcessedData].ok(parse(data))
    except ValueError as exc:
        return r[ProcessedData].fail(f"Parse error: {exc}")

result = process_data(input_data)
if result.is_failure:
    return r[FinalResult].fail(result.error)
return r[FinalResult].ok(transform(result.value))
```

## Before Committing

```bash
make check                    # Quick validation
make validate                 # Full validation (before PR)
```

## Task Management

Use `bd ready` to find work, `bd close <id>` to complete.
