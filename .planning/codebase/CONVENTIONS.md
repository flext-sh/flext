# Coding Conventions

**Analysis Date:** 2026-01-31

## Naming Patterns

### Files

- **Module files**: `snake_case.py` (lowercase with underscores)
  - `result.py`, `constants.py`, `protocols.py`, `utilities.py`
  - Internal modules: `_models/base.py`, `_utilities/configuration.py`
  - Public facades export single main class: `models.py` exports `FlextModels`

- **Test files**: `test_*.py` or `*_test.py`
  - Examples: `test_result.py`, `test_result_monad.py`
  - Located in `tests/` subdirectories matching `src/` structure
  - Organized by type: `tests/unit/`, `tests/integration/`, `tests/benchmark/`

### Functions

- **snake_case** with descriptive verbs
  - `validate_email()`, `process_data()`, `fetch_active_users()`
  - Private: `_validate_internal()`, `_format_output()`
  - Avoid: `process`, `handle`, `data`, `do_stuff`, `temp`

### Classes

- **PascalCase** with `Flext` prefix for main classes
  - `FlextResult`, `FlextConfig`, `FlextContainer`, `FlextLogger`
  - `FlextModels`, `FlextConstants`, `FlextProtocols`, `FlextUtilities`
  - Nested classes describe domain: `FlextModels.Entity.AggregateRoot`, `m.Cqrs.Command`

- **Internal classes**: `_ClassName` prefix
  - `_FlextConfigInternal`, `_ResultHelpers`
  - Exported via facade class (e.g., `FlextModels`)

- **Protocol classes**: No prefix, pure interface names
  - `class Result(Protocol)`, `class Config(Protocol)`
  - Organized in namespace hierarchy: `Foundation.Result`, `Domain.Service`

### Variables

- **snake_case** throughout
  - Local: `user_id`, `config_name`, `is_valid`
  - Module-level: `_default_timeout`, `_logger`
  - Private: `_internal_state`

- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
  - Access via `c.Namespace.CONSTANT_NAME`
  - Examples: `c.Core.DEFAULT_TIMEOUT`, `c.Ldif.RFC2849_ENTRY_SEPARATOR`

### Type Variables & Aliases

- **Module-level TypeVars**: Single or two letters from `flext_core.typings`
  - `T`, `U`, `R`, `E`, `P` - imported, never locally defined
  - Examples: `T_co` (covariant), `T_contra` (contravariant)

- **Type aliases**: Use `t.Types.*` namespace (centralized)
  - `t.Types.StringDict`, `t.Types.ConfigurationDict`
  - Access via: `from flext_core.typings import t`
  - Never: `from flext_core import typings as t` (breaks mypy resolution)

- **Short aliases** (runtime imports): Single letters
  - `from flext_core.result import r` → `r[T].ok()`, `r[T].fail()`
  - `from flext_core.constants import c` → `c.Core.TIMEOUT`
  - `from flext_core.models import m` → `m.Entity.Value`
  - `from flext_core.protocols import p` → `p.Foundation.Result`
  - `from flext_core.typings import t` → `t.Types.StringDict`
  - `from flext_core.utilities import u` → `u.Result.assert_success()`
  - `from flext_core.exceptions import e` → `e.ValidationError`

## Code Style

### Formatting

- **Line length**: 88 characters maximum (ruff-shared.toml)
- **Indentation**: 4 spaces per level
- **Quotes**: Double quotes `"string"` (ruff enforces)
- **Imports**: Sorted by ruff with isort
  - Standard library first
  - Third-party next
  - Local imports last
  - Within each group: alphabetical

### Imports

**Import Order (MANDATORY)**:

```python
from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Protocol, TypeVar

from pydantic import BaseModel
from returns.result import Result

from flext_core.result import r
from flext_core.typings import t, T
from flext_core.constants import c
from flext_core.models import m
from flext_core.protocols import p

from .local_module import LocalClass
```

**Path Aliases (MANDATORY)**:

- Never use: `from flext_core import typings as t` → breaks mypy
- Always use: `from flext_core.typings import t` → proper resolution
- Root imports allowed for classes only: `from flext_core import FlextResult` (via `__init__.py`)

**Forbidden Patterns**:

- ❌ `TYPE_CHECKING` blocks (use `from __future__ import annotations`)
- ❌ Lazy imports in functions
- ❌ Circular imports (use protocols instead)
- ❌ Relative imports beyond one level: `from ...module` (use absolute)

### Docstrings

**One-liner** for simple functions:

```python
def validate_email(email: str) -> bool:
    """Check if email format is valid."""
    return "@" in email
```

**Multi-line** for complex logic, public APIs, and classes:

```python
def process_entries(entries: list[dict]) -> r[list[dict]]:
    """Process LDIF entries with validation and transformation.

    Validates each entry structure, applies transformation rules,
    and returns composed result.

    Args:
        entries: List of LDIF entries as dictionaries

    Returns:
        FlextResult containing processed entries or error message

    Raises:
        Does not raise; returns failures in FlextResult

    Example:
        >>> result = process_entries([{"dn": "cn=user"}])
        >>> assert result.is_success
    """
```

**Class docstrings**:

```python
class FlextResult[T_co]:
    """Type-safe result for operation composition.

    Provides success/failure handling with monadic helpers for
    railway-oriented programming patterns.

    Attributes:
        value: Success value (if is_success)
        error: Error message (if is_failure)
        is_success: Boolean indicating success state
    """
```

**Module docstrings** (at file top):

```python
"""Type-safe result type for operations.

Provides success/failure handling with monadic helpers for composing
operations without exceptions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""
```

### Comments

**When to comment**:

- Complex algorithms that aren't self-obvious
- Non-obvious business logic
- Workarounds with explanation of why
- References to external standards (RFC numbers, LDAP specs)

**When NOT to comment**:

- Self-documenting code (good names eliminate need)
- Loop iterations (use descriptive variable names)
- If statements with clear conditions
- Obvious class/function purposes (use docstring instead)

**Example - Good**:

```python
# RFC 2849 requires DN normalization before comparison
normalized_dn = ldap.dn.escape_dn_chars(dn)

# Exponential backoff with jitter to avoid thundering herd
backoff = min(initial_backoff * (2 ** attempt), max_backoff) + random.random()
```

**Example - Bad**:

```python
# Loop through users
for user in users:

# Check if valid
if len(email) > 0:
```

## Import Organization

**Order (MANDATORY)**:

1. `from __future__ import annotations` (always first if present)
2. Standard library (`sys`, `os`, `json`, etc.)
3. Type imports (`typing`, `collections.abc`)
4. Third-party (`pydantic`, `returns`, etc.)
5. Local flext_core (`FlextResult`, `FlextConfig`, etc.)
6. Local project imports (same package)
7. Relative imports (current package subdirectories)

**Example - Complete Pattern**:

```python
"""Module docstring first."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Protocol, TypeVar
from collections.abc import Callable, Iterable

from pydantic import BaseModel, Field
from returns.result import Result

from flext_core.result import r
from flext_core.typings import t, T
from flext_core.constants import c
from flext_core.models import m
from flext_core.protocols import p

from . import local_module
from ._internal.helpers import helper_function
```

## Error Handling

### FlextResult Pattern (Railway-Oriented Programming)

**MANDATORY**: All operations that can fail return `r[T]` (FlextResult):

```python
from flext_core.result import r

def validate_user_data(data: dict) -> r[dict]:
    """Validate user data, returning result."""
    if not data.get("email"):
        return r[dict].fail("Email is required")
    if len(data["email"]) < 5:
        return r[dict].fail("Email too short")
    return r[dict].ok(data)
```

**Chaining Operations** (monadic composition):

```python
result = (
    validate_user_data(user_dict)
    .flat_map(lambda user: save_to_database(user))  # Chain operations
    .map(lambda saved_user: format_response(saved_user))  # Transform success
    .map_error(lambda error: log_error(error))  # Handle errors
)

# Check result
if result.is_success:
    user = result.value  # Extract success value
elif result.is_failure:
    error = result.error  # Extract error message
```

**Result Creation** (MANDATORY pattern):

```python
# ✅ CORRECT - Use r[T] alias
return r[User].ok(user_instance)
return r[User].fail("User not found")

# ✅ CORRECT - Type parameter matches return type
def get_user(user_id: int) -> r[User]:
    return r[User].ok(User(id=user_id))

# ❌ FORBIDDEN - Exception-based error handling
try:
    return User.query.get(user_id)  # DON'T DO THIS
except Exception as e:
    raise UserNotFound(str(e))  # DON'T DO THIS
```

**No Exceptions in Core Logic**:

- ✅ Use `r[T]` for failures
- ✅ Use `r[T].fail("message")` for errors
- ✅ Chain with `.map()`, `.flat_map()`, `.map_error()`
- ❌ Don't raise exceptions (use FlextResult instead)

### Result Accessors

```python
result = r[str].ok("value")

# Extract value (MANDATORY - no .unwrap())
value = result.value  # or result.data (both work)

# Check state
if result.is_success:
    # Process result.value
elif result.is_failure:
    # Process result.error
```

## Logging

**Framework**: `structlog` via `FlextLogger`

```python
from flext_core import FlextLogger

class MyService:
    def __init__(self) -> None:
        self._logger = FlextLogger.get_logger(__name__)

    def process(self, data: dict) -> None:
        """Process data with structured logging."""
        self._logger.info("Processing started", data_keys=list(data.keys()))
        # ... logic ...
        self._logger.info("Processing complete", item_count=len(data))
```

**Patterns**:

- ✅ Use structured logging: `logger.info("message", key=value)`
- ✅ Log operation boundaries (start, complete, error)
- ✅ Include context: user_id, request_id, correlation_id
- ❌ Don't use f-strings in log messages (ruff: G004 ignored for legitimate use)
- ❌ Don't log sensitive data (passwords, tokens, PII)

## Function Design

### Size Guideline

- **Ideal**: 15-25 lines
- **Maximum**: 50 lines (beyond that, extract helpers)
- **Rationale**: Easier to test, understand, and reason about

### Parameters

- **Count**: Maximum 5 positional (use dataclass/model for more)
- **Typing**: All parameters must have type hints
- **Defaults**: Use for optional parameters

```python
# ✅ GOOD - Clear parameters with types
def create_user(
    name: str,
    email: str,
    age: int | None = None,
) -> r[User]:
    """Create user."""
    return r[User].ok(User(name=name, email=email, age=age))

# ✅ GOOD - Model for complex data
class UserRequest(BaseModel):
    name: str
    email: str
    age: int | None = None

def create_user(request: UserRequest) -> r[User]:
    """Create user from request."""
    return r[User].ok(User(**request.model_dump()))

# ❌ AVOID - Too many parameters
def create_user(
    name: str,
    email: str,
    phone: str,
    address: str,
    city: str,
    state: str,
    zip_code: str,
) -> User:
    # Extract to model instead
```

### Return Values

- **Use FlextResult**: All operations that can fail
- **Type parameter**: Must match actual return type
- **Consistent**: Either always void or always return something

```python
# ✅ CORRECT - Typed return
def fetch_user(user_id: int) -> r[User]:
    return r[User].ok(user)

# ✅ CORRECT - Void operation
def configure_logging() -> None:
    # Setup logging
    pass

# ❌ WRONG - Inconsistent (sometimes returns, sometimes doesn't)
def process_data(data: dict) -> dict | None:  # Avoid this pattern
```

## Module Design

### Exports (Public API)

**Single main class per module**:

```python
# ✅ CORRECT - One public class per module
class FlextConfig(BaseSettings):
    """Main public class."""

    class _Internal:
        """Nested private helpers."""

    @classmethod
    def get_global(cls) -> r[FlextConfig]:
        """Public class method."""
```

**Facade pattern for aggregation**:

```python
# models.py - aggregates _models/* into FlextModels
class FlextModels:
    """Facade exposing all model namespaces."""

    class Entity:
        Value = FlextValue  # From _models.entity
        Entity = FlextEntity

    class Cqrs:
        Command = FlextCommand  # From _models.cqrs
        Query = FlextQuery

# Usage
m = FlextModels
entry = m.Entity.Entity(...)
```

### Circular Import Prevention

**Strategy 1: Forward References** (PREFERRED):

```python
from __future__ import annotations

class ParentEntity:
    children: list[ChildEntity]  # Forward ref as string, works with __future__

class ChildEntity:
    parent: ParentEntity  # Now defined, no circular import
```

**Strategy 2: Protocol-Based Decoupling**:

```python
# protocols.py (Tier 0 - no imports from services)
class ServiceProtocol(Protocol):
    def execute(self, command: Command) -> r[Result]: ...

# services.py (Tier 3 - uses protocol, not concrete class)
def call_service(service: p.Domain.Service[T]) -> r[T]:
    return service.execute()  # No direct import needed
```

**Strategy 3: Dependency Injection**:

```python
class Handler:
    def __init__(self, service: p.Domain.Service[T]) -> None:
        # Service injected, no import needed
        self._service = service
```

## Conventions Summary

| Convention | Pattern | Example |
|-----------|---------|---------|
| **Files** | snake_case.py | `result.py`, `config.py` |
| **Functions** | snake_case() | `validate_email()` |
| **Classes** | PascalCase (with Flext prefix) | `FlextResult`, `FlextConfig` |
| **Constants** | c.NAMESPACE.NAME | `c.Core.TIMEOUT` |
| **Variables** | snake_case | `user_id`, `config_dict` |
| **Type params** | T, U, R (from flext_core.typings) | `def process[T]()` |
| **Line length** | 88 characters max | (enforced by ruff) |
| **Quotes** | Double quotes | `"string"` not `'string'` |
| **Imports** | From __future__ → stdlib → third-party → local | See order above |
| **Errors** | r[T] railway pattern | `r[T].ok()` or `r[T].fail()` |
| **Docstrings** | One-liner or multi-line | See docstring examples |

---

*Conventions analysis: 2026-01-31*
