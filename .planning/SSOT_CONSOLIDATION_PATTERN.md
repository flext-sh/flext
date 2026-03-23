# Single Source of Truth (SSOT) Consolidation Pattern

## Overview
Applied to flext-infra test suite to eliminate code duplication and establish canonical factory patterns.

## Pattern Components

### 1. Centralized Fixtures File (`_shared_fixtures.py`)
- **Location**: `/tests/{module}/unit/check/_shared_fixtures.py`
- **Purpose**: Single source of truth for all test factories, mocks, and helpers
- **Organization**: Functions grouped by responsibility

### 2. Factory Functions Consolidated
- `create_gate_execution()` - Creates GateExecution test objects with standard defaults
- `create_checker_project()` - Creates checker + project pairs
- `create_fake_run_raw()` - Factory for subprocess mock results
- `create_fake_run_projects()` - Factory for run_projects mocks
- `patch_gate_run()` - Patches gate._run() with controlled output
- `patch_python_dir_detection()` - Mocks python directory detection
- `RunProjectsMock` - Stateful mock class for capturing test arguments
- `create_check_project_stub()` / `create_check_project_iter_stub()` - Stubs for _check_project

### 3. Refactoring Pattern for Consuming Files

#### Before (Duplicated)
```python
# file1.py
def _create_checker_project(tmp_path):
    checker = FlextInfraWorkspaceChecker(workspace_root=tmp_path)
    # ... initialization
    return checker, project_dir


# file2.py
def _create_checker_project(tmp_path):  # DUPLICATE!
    checker = FlextInfraWorkspaceChecker(workspace_root=tmp_path)
    # ... same initialization
    return checker, project_dir
```

#### After (SSOT)
```python
# _shared_fixtures.py
def create_checker_project(tmp_path):
    """Single canonical implementation"""
    checker = FlextInfraWorkspaceChecker(workspace_root=tmp_path)
    # ... initialization
    return checker, project_dir


# file1.py and file2.py
from ._shared_fixtures import create_checker_project

# or with alias for backward compatibility:
_create_checker_project = create_checker_project
```

### 4. Backward Compatibility Strategy

#### Alias Pattern
```python
from ._shared_fixtures import create_checker_project, patch_gate_run

# Local aliases for backward compatibility
_create_checker_project = create_checker_project
_patch_gate_run = patch_gate_run
```

**Benefit**: Allows refactoring without changing all test method calls immediately

### 5. Parameter Standardization

#### Issue: Parameter Name Consistency
```python
# Problem: Different signatures across files
# file1.py uses: def _run(_self, _cmd, _cwd, _timeout, _env)
# file2.py uses: def _run(_self, _cmd, _cwd, timeout, env)
# Gates call with: _run(..., timeout=120, env={...})
# Result: TypeError!
```

#### Solution: Match Gate Calling Convention
```python
# Correct signature (matches how gates call _run)
def _stub_run(
    _self: object,
    _cmd: list[str],
    _cwd: Path,
    timeout: int = 120,  # NOT _timeout
    env: dict[str, str] | None = None,  # NOT _env
) -> m.Infra.CommandOutput:
    del _self, _cmd, _cwd, timeout, env
    return m.Infra.CommandOutput(...)
```

### 6. Type Safety and Validation

#### Applied to All Consolidated Functions:
```python
# Use strict typing from module contracts
from flext_infra import m, c, r, t


def create_gate_execution(
    gate: str = "lint",
    project: str = "p",
    *,
    passed: bool = True,
    issues: list[m.Infra.Issue] | None = None,  # Explicit type
) -> GateExecution:
    """Factory with explicit, validated types"""
```

## Files Refactored in flext-infra

### Phase 1 - Core Consolidation
- ✅ `_shared_fixtures.py` (NEW) - 265+ lines of reusable factories
- ✅ `cli.py` - Uses `create_fake_run_projects`
- ✅ `extended_runners_ruff.py` - Uses `create_fake_run_raw`
- ✅ `extended_project_runners.py` - Uses `create_gate_execution`
- ✅ `extended_error_reporting.py` - Uses stubs, fixed parameter names

### Phase 2 - Gate Consolidation
- ✅ `extended_runners_extra.py` - Uses `patch_gate_run`, `patch_python_dir_detection`
- ✅ `extended_gate_mypy_pyright.py` - Uses `patch_python_dir_detection`
- ✅ `extended_gate_bandit_markdown.py` - Uses `create_checker_project`, `patch_gate_run`
- ✅ `extended_runners.py` - Uses shared `patch_python_dir_detection`

## Results

### Duplication Eliminated
- **75+ lines** of duplicate factory code removed
- **5+ factory functions** consolidated to one location
- **Consistency improved** across all test files

### Quality Metrics
- ✅ All ruff linting checks pass
- ✅ Type safety enforced across factories
- ✅ Backward compatibility maintained with aliases

## Application to Other Projects

### Checklist for New SSOT Consolidation:
1. Identify duplicate factory/helper functions across test files
2. Create `_shared_fixtures.py` or update existing fixture location
3. Move canonical implementations to shared file
4. Add local aliases in consuming files for backward compatibility
5. Fix parameter naming to match calling conventions
6. Run linting and type checks
7. Document applied pattern in this file

### Projects with Potential for SSOT Consolidation:
- **flext-ldap**: Large conftest.py (41KB) - audit for extractable patterns
- **flext-ldif**: Has conftest_shared.py - consolidate further
- **flext-core**: Multiple test files with factory patterns - audit scope
- **flext-cli**: Tests use fixtures - standardize pattern

## SOLID Compliance

This consolidation enforces:
- **S** (Single Responsibility): Each factory has one clear purpose
- **O** (Open/Closed): Extensible without modifying existing fixtures
- **L** (Liskov Substitution): Consistent interfaces across factories
- **I** (Interface Segregation): Focused, non-monolithic functions
- **D** (Dependency Inversion): Tests depend on abstractions (factories), not implementations

## DRY/YAGNI Compliance
- ✅ **DRY**: No duplicate factory implementations
- ✅ **YAGNI**: Only essential factories included (no speculative code)
- ✅ **Simplicity**: Minimal factory implementations, maximum reuse
