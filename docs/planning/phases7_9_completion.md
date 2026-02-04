# Phases 7-9: Test Suite, Problem Project, and Final Validation

**Timeline**: Days 25-35 (after Phases 2-6 complete)  
**Strategy**: Sequential execution with increasing scope  
**Dependency**: Phases 1-6 must complete successfully

---

## Phase 7: Test Suite Migration (Days 25-28)

**Duration**: 4 days  
**Goal**: Eliminate all ~500 cast() usages in test files

### Overview

Phase 7 focuses on test files across all projects. This is the largest single category of cast() usage (~500 instances).

**Strategy**:
1. Create comprehensive test TypeGuard library
2. Migrate tests by project (largest first)
3. Verify coverage maintained

### Task 7.1: Create Test TypeGuard Library

**Duration**: 1 day

#### New File: `flext-core/testing/guards.py` (Enhanced)

Expand the test guards created in Phase 1 with project-specific guards:

```python
"""Comprehensive test TypeGuards for all projects."""
from __future__ import annotations

from typing import TypeGuard


class TestGuards:
    """Base test guards."""
    
    @staticmethod
    def is_user_response(obj: object) -> TypeGuard[dict]:
        """Check if object is a user response fixture."""
        return (
            isinstance(obj, dict)
            and "user_id" in obj
            and "email" in obj
        )
    
    @staticmethod
    def is_config_response(obj: object) -> TypeGuard[dict]:
        """Check if object is a config response fixture."""
        return (
            isinstance(obj, dict)
            and "app_name" in obj
            and "version" in obj
        )


class LdifTestGuards:
    """LDIF-specific test guards."""
    
    @staticmethod
    def is_entry_fixture(obj: object) -> TypeGuard[dict]:
        """Check if object is an LDIF entry fixture."""
        return (
            isinstance(obj, dict)
            and "dn" in obj
            and "attributes" in obj
        )


class CliTestGuards:
    """CLI-specific test guards."""
    
    @staticmethod
    def is_command_fixture(obj: object) -> TypeGuard[dict]:
        """Check if object is a command fixture."""
        return (
            isinstance(obj, dict)
            and "name" in obj
            and "args" in obj
        )


class WebTestGuards:
    """Web-specific test guards."""
    
    @staticmethod
    def is_request_fixture(obj: object) -> TypeGuard[dict]:
        """Check if object is a request fixture."""
        return (
            isinstance(obj, dict)
            and "method" in obj
            and "endpoint" in obj
        )
```

#### Update conftest.py in Each Project

Add project-specific guards to `tests/conftest.py`:

```python
"""Test configuration and fixtures."""
from flext_core.testing.guards import TestGuards, LdifTestGuards

# Re-export for use in tests
__all__ = ["TestGuards", "LdifTestGuards"]
```

**Validation**:
- [ ] Test guards created in flext-core/testing/
- [ ] conftest.py updated in each project
- [ ] Guards exported and accessible in tests

**Commit**:
```
test(flext-core): create comprehensive test TypeGuard library
```

### Task 7.2: Migrate Tests by Project

**Duration**: 2.5 days

**Projects** (by cast() count in tests):
1. flext-core (~150 cast())
2. flext-ldif (~80 cast())
3. flext-tap-* (~100 cast() combined)
4. flext-target-* (~100 cast() combined)
5. flext-dbt-* (~30 cast() combined)
6. flext-cli (~20 cast())
7. flext-web (~20 cast())

#### Migration Pattern

```python
# BEFORE
from typing import cast

def test_process_config():
    data = {"app_name": "test", "version": "1.0"}
    config = cast(dict, data)
    assert config["app_name"] == "test"

# AFTER
from flext_core.testing.guards import TestGuards

def test_process_config():
    data = {"app_name": "test", "version": "1.0"}
    if TestGuards.is_config_response(data):
        assert data["app_name"] == "test"
    else:
        pytest.fail("Invalid config fixture")
```

#### Execution Steps

For each project:

1. **Identify all cast() in tests**
   ```bash
   grep -r "cast(" flext-{project}/tests/ | wc -l
   ```

2. **Create project-specific guards** (if needed)
   ```python
   # In tests/conftest.py
   class ProjectTestGuards:
       @staticmethod
       def is_specific_fixture(obj: object) -> TypeGuard[dict]:
           ...
   ```

3. **Replace cast() with TypeGuards**
   - Batch replace by fixture type
   - Verify type checking after each batch

4. **Run tests**
   ```bash
   pytest flext-{project}/tests/ -v
   ```

5. **Verify coverage**
   ```bash
   pytest flext-{project}/tests/ --cov=flext_{project} --cov-report=term-missing
   ```

**Validation**:
- [ ] Zero cast() in all test files
- [ ] All tests passing
- [ ] 80%+ coverage maintained
- [ ] Type checking passes

**Commits** (per project):
```
test(flext-core): eliminate cast() from tests using TypeGuards
test(flext-ldif): eliminate cast() from tests using TypeGuards
test(flext-tap-*): eliminate cast() from tests using TypeGuards
test(flext-target-*): eliminate cast() from tests using TypeGuards
test(flext-dbt-*): eliminate cast() from tests using TypeGuards
test(flext-cli): eliminate cast() from tests using TypeGuards
test(flext-web): eliminate cast() from tests using TypeGuards
```

### Task 7.3: Verify Test Coverage

**Duration**: 0.5 days

**Steps**:
1. Run full test suite: `make test`
2. Verify 80%+ coverage maintained
3. Fix any coverage gaps
4. Document any exceptions

**Validation**:
- [ ] `make test` passes
- [ ] 80%+ coverage across all projects
- [ ] No coverage regressions

**Commit**:
```
test: verify 80%+ coverage maintained after cast() elimination
```

---

## Phase 8: Problem Project (Days 29-32)

**Duration**: 4 days  
**Goal**: Fix flext-tap-oracle-wms (100+ type errors)

### Overview

flext-tap-oracle-wms is isolated in its own phase due to:
- 100+ type errors
- Missing imports
- Complex dependency issues
- Risk of blocking other work

### Task 8.1: Import Structure Fixes

**Duration**: 1.5 days

**Current Issues**:
- Missing config module imports
- Missing exceptions module imports
- Circular dependencies

**Steps**:

1. **Analyze Import Errors**
   ```bash
   make type-check PROJECT=flext-tap-oracle-wms 2>&1 | grep "import"
   ```

2. **Fix Missing Imports**
   - Add missing config imports
   - Add missing exceptions imports
   - Resolve circular dependencies

3. **Verify Import Structure**
   ```bash
   python -c "import flext_tap_oracle_wms; print('OK')"
   ```

**Validation**:
- [ ] All imports resolve
- [ ] No circular dependencies
- [ ] Module loads successfully

**Commit**:
```
fix(flext-tap-oracle-wms): resolve missing imports and circular dependencies
```

### Task 8.2: Type Error Resolution

**Duration**: 1.5 days

**Current Issues**:
- 100+ type errors
- bad-override errors
- Missing attributes on FlextModels/FlextTypes

**Steps**:

1. **Categorize Type Errors**
   ```bash
   make type-check PROJECT=flext-tap-oracle-wms 2>&1 | sort | uniq -c | sort -rn
   ```

2. **Fix by Category**
   - bad-override errors (inheritance issues)
   - Missing attributes (model definitions)
   - Type mismatches (function signatures)

3. **Verify Type Checking**
   ```bash
   make type-check PROJECT=flext-tap-oracle-wms
   ```

**Validation**:
- [ ] Zero type errors
- [ ] `pyrefly` passes

**Commits** (per category):
```
fix(flext-tap-oracle-wms): resolve bad-override errors
fix(flext-tap-oracle-wms): add missing model attributes
fix(flext-tap-oracle-wms): fix type mismatches in function signatures
```

### Task 8.3: Model Migration

**Duration**: 1 day

**Steps**:

1. **Apply Phase 1 Patterns**
   - Convert any remaining TypedDicts
   - Remove any remaining cast()
   - Standardize ConfigDict

2. **Verify Consistency**
   - Models follow hierarchical pattern
   - ConfigDict settings standard
   - No TypedDict or cast()

3. **Run Full Validation**
   ```bash
   make validate PROJECT=flext-tap-oracle-wms
   ```

**Validation**:
- [ ] Zero TypedDict
- [ ] Zero cast()
- [ ] Standard ConfigDict
- [ ] `make validate` passes

**Commit**:
```
refactor(flext-tap-oracle-wms): apply Pydantic 2 patterns and standardize models
```

---

## Phase 9: Final Validation & Documentation (Days 33-35)

**Duration**: 3 days  
**Goal**: Ensure complete migration and update documentation

### Task 9.1: Global Validation

**Duration**: 1 day

**Steps**:

1. **Full Monorepo Validation**
   ```bash
   make validate
   ```

2. **Verify Zero cast()**
   ```bash
   grep -r "cast(" flext-*/src/ flext-*/tests/ | grep -v "\.pyc" | wc -l
   # Expected: 0
   ```

3. **Verify Zero TypedDict**
   ```bash
   grep -r "TypedDict" flext-*/src/ | grep -v "\.pyc" | wc -l
   # Expected: 0 (or only in external contracts)
   ```

4. **Verify ConfigDict Standardization**
   ```bash
   grep -r "model_config = ConfigDict" flext-*/src/ | wc -l
   # Expected: 127+
   ```

**Validation**:
- [ ] `make validate` passes on full monorepo
- [ ] Zero cast() across all projects
- [ ] Zero TypedDict (all converted)
- [ ] ConfigDict standardized

**Commit**:
```
ci: verify full monorepo passes make validate
```

### Task 9.2: Test Coverage Verification

**Duration**: 0.5 days

**Steps**:

1. **Run Full Test Suite**
   ```bash
   make test
   ```

2. **Verify Coverage**
   ```bash
   pytest --cov=flext_* --cov-report=term-missing | grep -E "TOTAL|^flext"
   ```

3. **Fix Coverage Gaps**
   - Identify any projects below 80%
   - Add tests as needed

**Validation**:
- [ ] All tests passing
- [ ] 80%+ coverage across all projects
- [ ] No coverage regressions

**Commit**:
```
test: verify 80%+ coverage across all projects
```

### Task 9.3: Documentation Update

**Duration**: 1 day

**Files to Update**:

1. **AGENTS.md**
   - Add TypeGuard pattern section
   - Add hierarchical model pattern section
   - Add ConfigDict standards section
   - Add migration guide for future projects

2. **type-system-architecture.md** (create if needed)
   - Document type system design
   - Document model hierarchy
   - Document validation patterns

3. **MIGRATION_GUIDE.md** (create)
   - Step-by-step migration process
   - Pattern examples
   - Common pitfalls and solutions

#### AGENTS.md Additions

```markdown
## Pydantic 2 Migration Complete

### TypeGuard Pattern

Use TypeGuards for type narrowing instead of cast():

\`\`\`python
from flext_core.utilities.guards import Guards

if Guards.is_config(obj):
    obj.app_name  # Type narrowed, no cast() needed
\`\`\`

### Hierarchical Model Organization

Models are organized in nested namespaces:

\`\`\`python
from flext_core.models import m

config: m.Core.Config = ...
context: m.Core.Context = ...
result: m.Result.Success = ...
\`\`\`

### ConfigDict Standards

All models use standard ConfigDict:

\`\`\`python
model_config = ConfigDict(
    validate_assignment=True,
    use_enum_values=True,
    extra="forbid",
    str_strip_whitespace=True,
)
\`\`\`

### Modern Validators

Use Pydantic 2.11+ validators:

\`\`\`python
from pydantic import field_validator, model_validator, computed_field

class User(BaseModel):
    email: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email")
        return v.lower()
    
    @computed_field
    @property
    def domain(self) -> str:
        return self.email.split("@")[1]
\`\`\`
```

**Validation**:
- [ ] AGENTS.md updated with patterns
- [ ] type-system-architecture.md created/updated
- [ ] MIGRATION_GUIDE.md created
- [ ] All documentation links valid

**Commits**:
```
docs(AGENTS.md): add Pydantic 2 migration patterns and standards
docs: create type-system-architecture.md with design documentation
docs: create MIGRATION_GUIDE.md for future migrations
```

### Task 9.4: Cleanup and Issue Closure

**Duration**: 0.5 days

**Steps**:

1. **Remove Deprecated Type Aliases**
   - Identify any old type aliases no longer needed
   - Remove from typings.py
   - Update imports

2. **Archive Migration Plan**
   - Move roadmap to docs/archive/
   - Create summary of what was done

3. **Close Beads Issues**
   ```bash
   bd close flext-fin flext-pf3 flext-5dr flext-jt2 flext-nya
   bd close <all other phase issues>
   ```

4. **Final Sync**
   ```bash
   git status
   git add .
   git commit -m "chore: cleanup after Pydantic 2 migration"
   git push
   ```

**Validation**:
- [ ] No deprecated type aliases
- [ ] Migration plan archived
- [ ] All Beads issues closed
- [ ] Changes pushed to remote

**Commit**:
```
chore: cleanup after Pydantic 2 migration completion
```

---

## Success Criteria for Phases 7-9

✅ **Test Suite**
- Zero cast() in all test files (~500 eliminated)
- All tests passing
- 80%+ coverage maintained

✅ **Problem Project**
- flext-tap-oracle-wms fully migrated
- Zero type errors
- Patterns consistent with rest of monorepo

✅ **Global Validation**
- `make validate` passes on full monorepo
- Zero cast() across ALL projects
- Zero TypedDict (all converted)
- ConfigDict standardized across 127+ models

✅ **Documentation**
- AGENTS.md updated with patterns
- type-system-architecture.md created
- MIGRATION_GUIDE.md created
- All links valid

✅ **Cleanup**
- Deprecated code removed
- Migration plan archived
- All Beads issues closed
- Changes pushed to remote

---

## Timeline Summary

| Phase | Duration | Days | Status |
|-------|----------|------|--------|
| Phase 1: Core | 4 days | 1-4 | Foundation |
| Phase 2: API + Infra | 3 days | 5-7 | Parallel |
| Phase 3: Data | 4 days | 8-11 | Sequential |
| Phase 4: Oracle + Meltano | 3 days | 12-14 | Parallel |
| Phase 5: Taps + Targets | 5 days | 15-19 | Parallel |
| Phase 6: DBT + User-Facing | 5 days | 20-24 | Parallel |
| Phase 7: Test Suite | 4 days | 25-28 | Sequential |
| Phase 8: Problem Project | 4 days | 29-32 | Sequential |
| Phase 9: Validation | 3 days | 33-35 | Sequential |
| **Total** | **35 days** | | |

**Savings from Parallelization**: ~10-12 days vs. sequential approach

---

## Final Metrics

### Before Migration
- 627 cast() usages
- 305 TypedDict definitions
- 249+ ConfigDict patterns (inconsistent)
- Multiple validator patterns (v1 and v2 mixed)

### After Migration
- ✅ 0 cast() usages
- ✅ 0 TypedDict definitions
- ✅ 127+ models with standard ConfigDict
- ✅ Modern Pydantic 2.11+ validators throughout
- ✅ All 29 projects passing `make validate`
- ✅ 80%+ test coverage maintained

---

## Rollback Plan

If critical issues arise at any phase:

1. **Identify Issue**: Document in Beads
2. **Create Tag**: `git tag phase-{N}-rollback`
3. **Rollback**: `git reset --hard phase-{N}-start`
4. **Analyze**: Determine root cause
5. **Retry**: Address issue and restart phase

---

## Post-Migration Maintenance

### Ongoing Standards

1. **New Projects**
   - Follow Phase 1 patterns from day 1
   - Use TypeGuards instead of cast()
   - Use hierarchical models
   - Use standard ConfigDict

2. **Code Reviews**
   - Check for cast() usage (forbidden)
   - Check for TypedDict usage (forbidden)
   - Check for ConfigDict consistency
   - Check for modern validator patterns

3. **Documentation**
   - Keep AGENTS.md updated
   - Keep MIGRATION_GUIDE.md current
   - Document any new patterns

### Monitoring

- **CI/CD**: Enforce zero cast() and TypedDict
- **Linting**: Add rules to prevent regressions
- **Type Checking**: Maintain strict mode
- **Coverage**: Maintain 80%+ threshold
