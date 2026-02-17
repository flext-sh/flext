# Phase 1: Core Completion + Pattern Establishment

**Duration**: 3-4 days  
**Status**: Ready to start  
**Beads Issues**: flext-fin, flext-pf3, flext-5dr, flext-jt2, flext-nya

## Overview

Phase 1 is the **foundation phase** that establishes all patterns and infrastructure for the entire migration. All subsequent phases depend on the patterns created here.

**Key Deliverables**:

1. TypeGuard infrastructure (replaces cast())
2. Hierarchical Pydantic model patterns
3. Standard ConfigDict settings
4. Modern validator patterns
5. Updated AGENTS.md documentation

---

## Task 1.1: Create TypeGuard Infrastructure

**Beads Issue**: flext-fin  
**Duration**: 1 day  
**Depends On**: None

### Objective

Create comprehensive TypeGuard utilities that will replace all 627 cast() usages across the monorepo.

### Files to Create/Modify

#### New File: `flext-core/src/flext_core/utilities/guards.py`

```python
"""Type guards for runtime type narrowing (replaces cast())."""
from __future__ import annotations

from typing import TypeGuard

from flext_core.typings import t


class Guards:
    """Type guards for common Flext types."""

    @staticmethod
    def is_config(obj: object) -> TypeGuard[m.Core.Config]:
        """Check if object is a Config model."""
        return isinstance(obj, m.Core.Config)

    @staticmethod
    def is_context(obj: object) -> TypeGuard[m.Core.Context]:
        """Check if object is a Context model."""
        return isinstance(obj, m.Core.Context)

    @staticmethod
    def is_result_success(obj: object) -> TypeGuard[m.Result.Success]:
        """Check if object is a successful Result."""
        return isinstance(obj, m.Result.Success)

    @staticmethod
    def is_result_failure(obj: object) -> TypeGuard[m.Result.Failure]:
        """Check if object is a failed Result."""
        return isinstance(obj, m.Result.Failure)

    @staticmethod
    def is_dict_with_keys(obj: object, *keys: str) -> TypeGuard[dict]:
        """Check if object is a dict with specific keys."""
        return isinstance(obj, dict) and all(k in obj for k in keys)

    @staticmethod
    def is_list_of(obj: object, item_type: type) -> TypeGuard[list]:
        """Check if object is a list of specific type."""
        return isinstance(obj, list) and all(isinstance(item, item_type) for item in obj)
```

#### New File: `flext-core/src/flext_core/testing/guards.py`

```python
"""Test-specific type guards for fixtures and test data."""
from __future__ import annotations

from typing import TypeGuard


class TestGuards:
    """Type guards for test fixtures and mock data."""

    @staticmethod
    def is_user_response(obj: object) -> TypeGuard[dict]:
        """Check if object is a user response fixture."""
        return (
            isinstance(obj, dict)
            and "user_id" in obj
            and "email" in obj
            and "created_at" in obj
        )

    @staticmethod
    def is_config_response(obj: object) -> TypeGuard[dict]:
        """Check if object is a config response fixture."""
        return (
            isinstance(obj, dict)
            and "app_name" in obj
            and "version" in obj
        )

    @staticmethod
    def is_error_response(obj: object) -> TypeGuard[dict]:
        """Check if object is an error response fixture."""
        return (
            isinstance(obj, dict)
            and "error_code" in obj
            and "message" in obj
        )
```

### Validation Checklist

- [ ] `flext_core/utilities/guards.py` created with 5+ guards
- [ ] `flext_core/testing/guards.py` created with test guards
- [ ] All guards have proper TypeGuard return types
- [ ] Guards are exported in `__init__.py`
- [ ] Type checking passes: `pyrefly flext-core/src/flext_core/utilities/guards.py`
- [ ] Linting passes: `ruff check flext-core/src/flext_core/utilities/guards.py`

### Commit Message

```
feat(flext-core): add TypeGuard infrastructure for type narrowing

- Create utilities/guards.py with 5+ common TypeGuards
- Create testing/guards.py with test fixture guards
- Replace cast() usage with TypeGuard pattern
- Enables type-safe narrowing without type: ignore
```

---

## Task 1.2: Migrate flext-core TypedDicts to Hierarchical Pydantic Models

**Beads Issue**: flext-pf3  
**Duration**: 1.5 days  
**Depends On**: Task 1.1

### Objective

Convert all 86 TypedDicts in flext-core to hierarchical Pydantic models with proper inheritance and organization.

### Current State Analysis

```bash
# Find all TypedDict definitions
grep -r "class.*TypedDict" flext-core/src/flext_core/typings.py | wc -l
# Expected: 86

# Find all TypedDict usages
grep -r "TypedDict" flext-core/src/ | grep -v "test" | wc -l
```

### Migration Strategy

#### Step 1: Analyze TypedDict Categories

Group the 86 TypedDicts into categories:

- **Config models**: DispatcherConfig, BatchConfig, etc.
- **Result models**: BatchResultDict, ProcessResultDict, etc.
- **Context models**: ContextDict, StateDict, etc.
- **Data models**: EntityDict, AttributeDict, etc.

#### Step 2: Create Base Model Class

In `flext-core/src/flext_core/models.py`:

```python
from pydantic import BaseModel, ConfigDict, Field

class FlextModels:
    """Hierarchical namespace for all Flext models."""

    class Base(BaseModel):
        """Base model with standard Flext configuration."""
        model_config = ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            extra="forbid",
            str_strip_whitespace=True,
        )

    class Core:
        """Core framework models."""

        class Config(FlextModels.Base):
            """Configuration models."""
            app_name: str = Field(description="Application name")
            version: str = Field(description="Version string")
            # ... other config fields

        class Context(FlextModels.Base):
            """Context models."""
            request_id: str = Field(description="Request ID")
            user_id: str | None = Field(None, description="User ID")
            # ... other context fields

    class Result:
        """Result models."""

        class Success(FlextModels.Base):
            """Successful result."""
            data: dict = Field(description="Result data")
            timestamp: str = Field(description="Timestamp")

        class Failure(FlextModels.Base):
            """Failed result."""
            error_code: str = Field(description="Error code")
            message: str = Field(description="Error message")
```

#### Step 3: Update All Imports

Replace all TypedDict imports:

```python
# BEFORE
from flext_core.typings import DispatcherConfig, BatchResultDict

# AFTER

config: m.Core.Config = ...
result: m.Result.Success = ...
```

#### Step 4: Update typings.py

Remove all TypedDict definitions, keep only type aliases:

```python
# flext-core/src/flext_core/typings.py
"""Type aliases and protocols (no TypedDict)."""


# Type aliases for convenience
ConfigType = m.Core.Config
ContextType = m.Core.Context
ResultType = m.Result.Success | m.Result.Failure
```

### Files to Modify

1. `flext-core/src/flext_core/models.py` - Add all 86 models
2. `flext-core/src/flext_core/typings.py` - Remove TypedDicts, keep aliases
3. `flext-core/src/flext_core/__init__.py` - Export models
4. All files importing TypedDicts - Update imports

### Validation Checklist

- [ ] All 86 TypedDicts converted to Pydantic models
- [ ] Hierarchical organization in FlextModels namespace
- [ ] All models inherit from FlextModels.Base
- [ ] All imports updated across flext-core
- [ ] Type checking passes: `pyrefly flext-core/src/`
- [ ] Linting passes: `ruff check flext-core/src/`
- [ ] Tests pass: `pytest flext-core/tests/ -v`
- [ ] Coverage maintained: `pytest flext-core/tests/ --cov=flext_core --cov-report=term-missing`

### Commit Strategy

Create atomic commits per category:

```bash
# Commit 1: Add base models and Config namespace
git commit -m "feat(flext-core): add hierarchical Config models

- Create FlextModels.Base with standard ConfigDict
- Create FlextModels.Core.Config namespace
- Convert 20 config-related TypedDicts"

# Commit 2: Add Result namespace
git commit -m "feat(flext-core): add hierarchical Result models

- Create FlextModels.Result namespace
- Convert 15 result-related TypedDicts"

# Commit 3: Add Context namespace
git commit -m "feat(flext-core): add hierarchical Context models

- Create FlextModels.Core.Context namespace
- Convert 25 context-related TypedDicts"

# Commit 4: Add Data namespace
git commit -m "feat(flext-core): add hierarchical Data models

- Create FlextModels.Data namespace
- Convert 26 data-related TypedDicts"

# Commit 5: Update imports and cleanup
git commit -m "refactor(flext-core): update imports to use hierarchical models

- Update all internal imports
- Remove TypedDict definitions from typings.py
- Update __init__.py exports"
```

---

## Task 1.3: Eliminate cast() from flext-core src/

**Beads Issue**: flext-5dr  
**Duration**: 1 day  
**Depends On**: Task 1.1, Task 1.2

### Objective

Remove all 8 cast() usages in flext-core src/ and replace with TypeGuards.

### Current State

```bash
# Find all cast() usages in src/
grep -r "cast(" flext-core/src/ | grep -v test
# Expected: 8 usages
```

### Migration Pattern

```python
# BEFORE
from typing import cast

def process_config(data: dict) -> str:
    config = cast(m.Core.Config, data)
    return config.app_name

# AFTER
from flext_core.utilities.guards import Guards

def process_config(data: dict) -> str:
    if Guards.is_config(data):
        return data.app_name
    raise ValueError("Invalid config")
```

### Files to Modify

1. Find all files with cast() in flext-core/src/
2. Replace each cast() with appropriate TypeGuard
3. Update function signatures if needed

### Validation Checklist

- [ ] All 8 cast() usages removed from src/
- [ ] Replaced with TypeGuards from utilities/guards.py
- [ ] Type checking passes: `pyrefly flext-core/src/`
- [ ] Linting passes: `ruff check flext-core/src/`
- [ ] Tests pass: `pytest flext-core/tests/ -v`
- [ ] No `type: ignore` comments added

### Commit Message

```
refactor(flext-core): eliminate cast() from src/ using TypeGuards

- Replace 8 cast() usages with TypeGuard pattern
- Update affected functions with proper type narrowing
- No functional changes, only type safety improvements
```

---

## Task 1.4: Standardize ConfigDict Settings Across Models

**Beads Issue**: flext-jt2  
**Duration**: 0.5 days  
**Depends On**: Task 1.2

### Objective

Ensure all 127+ Pydantic models across flext-core use consistent ConfigDict settings.

### Standard Settings by Model Type

#### Production Models (Default)

```python
model_config = ConfigDict(
    validate_assignment=True,      # Validate on attribute assignment
    use_enum_values=True,          # Serialize enums to values
    extra="forbid",                # Reject unknown fields
    str_strip_whitespace=True,     # Clean string inputs
    frozen=False,                  # Mutable by default
)
```

#### Immutable Value Objects

```python
model_config = ConfigDict(
    frozen=True,                   # Immutable
    validate_assignment=True,
    extra="forbid",
)
```

#### API Response Models

```python
model_config = ConfigDict(
    extra="ignore",                # Ignore unknown fields from API
    validate_assignment=True,
    use_enum_values=True,
)
```

### Audit Checklist

- [ ] Review all 127+ models in flext-core
- [ ] Identify models missing ConfigDict
- [ ] Identify models with non-standard settings
- [ ] Document exceptions (if any)

### Standardization Tasks

1. Add ConfigDict to models missing it
2. Update non-standard settings to match pattern
3. Document any exceptions in comments

### Validation Checklist

- [ ] All models have ConfigDict
- [ ] Settings match documented patterns
- [ ] Type checking passes: `pyrefly flext-core/src/`
- [ ] Linting passes: `ruff check flext-core/src/`
- [ ] Tests pass: `pytest flext-core/tests/ -v`

### Commit Message

```
refactor(flext-core): standardize ConfigDict across all models

- Add ConfigDict to models missing it
- Standardize settings: validate_assignment, extra="forbid", etc.
- Document model type patterns in models.py
```

---

## Task 1.5: Validate flext-core and Update AGENTS.md

**Beads Issue**: flext-nya  
**Duration**: 0.5 days  
**Depends On**: Tasks 1.1-1.4

### Objective

Run full validation suite and update documentation with new patterns.

### Validation Steps

```bash
# Full validation
make validate PROJECT=flext-core

# Specific checks
make lint PROJECT=flext-core
make type-check PROJECT=flext-core
make test PROJECT=flext-core

# Coverage check
pytest flext-core/tests/ --cov=flext_core --cov-report=term-missing
```

### Expected Results

- ✅ Zero lint violations
- ✅ Zero type errors
- ✅ All tests passing
- ✅ 80%+ coverage maintained

### AGENTS.md Updates

Add new sections:

#### TypeGuard Pattern

```markdown
### TypeGuard Pattern (Replaces cast())

Use TypeGuards for type narrowing instead of cast():

\`\`\`python
from flext_core.utilities.guards import Guards

if Guards.is_config(obj):
obj.app_name # Type narrowed, no cast() needed
\`\`\`

Benefits:

- Type-safe narrowing
- No type: ignore comments
- Runtime validation
- Better IDE support
```

#### Hierarchical Model Pattern

```markdown
### Hierarchical Model Organization

Models are organized in nested namespaces for maximum reuse:

\`\`\`python

config: m.Core.Config = ...
context: m.Core.Context = ...
result: m.Result.Success = ...
\`\`\`

Pattern:

- FlextModels.Base - Standard ConfigDict
- FlextModels.Core.\* - Core framework models
- FlextModels.Result.\* - Result models
- FlextModels.Data.\* - Data models
```

#### ConfigDict Standards

```markdown
### ConfigDict Standards

All models use standard ConfigDict settings:

\`\`\`python
model_config = ConfigDict(
validate_assignment=True,
use_enum_values=True,
extra="forbid",
str_strip_whitespace=True,
)
\`\`\`

Exceptions documented in models.py
```

### Validation Checklist

- [ ] `make validate PROJECT=flext-core` passes
- [ ] Zero lint violations
- [ ] Zero type errors
- [ ] All tests passing
- [ ] 80%+ coverage maintained
- [ ] AGENTS.md updated with patterns
- [ ] Patterns documented with examples

### Commit Message

```
docs(flext-core): update AGENTS.md with Pydantic 2 patterns

- Add TypeGuard pattern documentation
- Add hierarchical model organization pattern
- Add ConfigDict standards
- Document migration patterns for other projects
```

---

## Success Criteria for Phase 1

✅ **Infrastructure**

- TypeGuard utilities created and tested
- Test guards available for all projects

✅ **Models**

- All 86 TypedDicts converted to Pydantic models
- Hierarchical organization in FlextModels namespace
- All models inherit from FlextModels.Base

✅ **Type Safety**

- Zero cast() in flext-core src/
- All replaced with TypeGuards
- Type checking passes

✅ **Standardization**

- All 127+ models have standard ConfigDict
- Settings consistent across project

✅ **Quality**

- `make validate PROJECT=flext-core` passes
- 80%+ coverage maintained
- Zero lint violations
- Zero type errors

✅ **Documentation**

- AGENTS.md updated with patterns
- Patterns documented with examples
- Ready for other projects to follow

---

## Timeline

| Task                            | Duration   | Start | End   |
| ------------------------------- | ---------- | ----- | ----- |
| 1.1: TypeGuard Infrastructure   | 1 day      | Day 1 | Day 1 |
| 1.2: TypedDict Migration        | 1.5 days   | Day 1 | Day 2 |
| 1.3: cast() Elimination         | 1 day      | Day 2 | Day 3 |
| 1.4: ConfigDict Standardization | 0.5 days   | Day 3 | Day 3 |
| 1.5: Validation & Docs          | 0.5 days   | Day 3 | Day 3 |
| **Total**                       | **4 days** |       |       |

---

## Rollback Plan

If issues arise:

1. **Before starting**: Create git tag `phase1-start`
2. **If critical issue**: `git reset --hard phase1-start`
3. **Document issue**: Create Beads issue with details
4. **Retry**: Address issue and restart task

---

## Next Phase

Once Phase 1 completes successfully:

- All patterns established
- Infrastructure ready
- Ready to parallelize Phases 2-6
- Other projects can follow Phase 1 patterns
