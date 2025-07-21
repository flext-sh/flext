# CLAUDE.QUALITY.md

This file provides guidance to Claude Code about the ongoing quality standardization work across the FLEXT workspace.

## Current Quality Standardization Mission

**CRITICAL CONTEXT**: We are in the middle of a systematic, zero-tolerance quality standardization process across ALL 25+ FLEXT projects. This is NOT optional work - it's mandatory enterprise-grade quality enforcement.

## What We're Doing

### Phase: Comprehensive Linting Error Elimination

We are systematically fixing ALL linting errors across every FLEXT project with ZERO TOLERANCE for violations. This is based on extensive previous work that identified recurring patterns of quality issues.

### Current Progress Status

#### ✅ COMPLETED (Zero Linting Errors)

- **flext-core** - 0 errors (COMPLETED)
- **flext-api** - 0 errors (COMPLETED)
- **flext-auth** - 0 errors (COMPLETED)
- **flext-grpc** - 0 errors (COMPLETED)

#### 🔄 IN PROGRESS

- **flext-observability** - 324 errors remaining (mainly test type annotations)
  - Context manager errors FIXED (PYI036 violations)
  - Need to fix: missing type annotations in tests (ANN001, ANN201)
  - Need to add: docstrings for test packages (D104)
- **flext-meltano** - 9 errors identified, needs attention

#### ⏳ PENDING (Identified but not started)

- **flext-plugin** - 45+ errors (complex refactoring needed)
- **flext-web** - Not checked yet
- **flext-cli** - Not checked yet
- **All Singer projects** (10+ projects) - Not checked yet
- **All dbt projects** (4 projects) - Not checked yet
- **Extension projects** (6 projects) - Not checked yet
- **Enterprise applications** (2 projects) - Not checked yet

## Critical Patterns Fixed So Far

### 1. Context Manager Type Annotations (PYI036)

**Pattern**: Fixed in flext-observability

```python
# ❌ BEFORE (violates PYI036)
def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:

# ✅ AFTER (correct annotations)
def __exit__(
    self,
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: types.TracebackType | None,
) -> None:
```

**Required Import**: `import types` (must be runtime import, not in TYPE_CHECKING)

### 2. Logging Anti-patterns (G201)

**Pattern**: Fixed across multiple projects

```python
# ❌ BEFORE
logger.error("message", exc_info=True)

# ✅ AFTER  
logger.exception("message")
```

### 3. Missing Type Annotations (ANN001, ANN201)

**Pattern**: Systematic across all projects

```python
# ❌ BEFORE
def function():
def test_function(self, fixture):

# ✅ AFTER
def function() -> None:
def test_function(self, fixture: Any) -> None:
```

### 4. UTC Datetime Usage (DTZ003)

**Pattern**: Fixed in flext-observability

```python
# ❌ BEFORE
datetime.utcnow()

# ✅ AFTER
from datetime import UTC
datetime.now(UTC)
```

### 5. Mutable Class Attributes (RUF012)

**Pattern**: Found in flext-plugin

```python
# ❌ BEFORE
class Config:
    items: list[str] = []

# ✅ AFTER
from typing import ClassVar
class Config:
    items: ClassVar[list[str]] = []
```

## Systematic Approach

### 1. Project-by-Project Execution

```bash
# For each project:
cd /home/marlonsc/flext/PROJECT_NAME
make lint  # Identify all violations
# Fix systematically by error type
make lint  # Verify 0 errors
```

### 2. Error Type Prioritization

1. **PYI036** (Context managers) - Critical for proper typing
2. **G201** (Logging) - Critical for observability
3. **DTZ003** (UTC datetime) - Critical for timezone handling
4. **RUF012** (ClassVar) - Critical for class safety
5. **ANN001/ANN201** (Type annotations) - Required for strict typing
6. **D104** (Docstrings) - Documentation compliance

### 3. Quality Gate Enforcement

```bash
# MANDATORY after each project completion:
make check  # Must return 0 violations
```

## Next Steps for Continuation

### Immediate Priority (Current Session)

1. **Complete flext-observability**:
   - Fix remaining 324 test annotation errors
   - Add missing docstrings for test packages
   - Achieve 0 linting errors

2. **Fix flext-meltano** (9 errors):
   - Check error types and apply systematic fixes
   - Follow established patterns

### Next Session Priority

1. **flext-plugin** (45+ errors - complex):
   - This will need significant refactoring
   - Focus on ClassVar annotations and type fixes
   - May require multiple sessions

2. **Systematic project expansion**:
   - flext-web
   - flext-cli
   - All Singer projects (10+)
   - All dbt projects (4)
   - Extension projects (6)

## Critical Rules for Continuation

### ZERO TOLERANCE POLICIES

1. **Never skip or ignore linting errors**
   - Every error must be fixed, not suppressed
   - Use proper fixes, not quick hacks

2. **Never break existing functionality**
   - Always run tests after fixes
   - Verify functionality works after changes

3. **Follow established patterns**
   - Use the same fix patterns documented above
   - Don't invent new approaches for solved problems

4. **Maintain architectural integrity**
   - Don't add dependencies to fix errors
   - Use existing project patterns and imports

### Required Tools for Each Project

```bash
# Standard verification sequence:
make lint       # Must show 0 errors when complete
make type-check # Must pass
make test       # Must pass
```

### Error Categories Requiring Specific Approaches

#### Type Annotation Errors (ANN001, ANN201)

- **Tests**: Add return type annotations to all test functions
- **Fixtures**: Add proper type hints for pytest fixtures
- **Mock parameters**: Use `Any` for mock objects in tests

#### Import Errors (TC003)

- **Move to TYPE_CHECKING**: Only for type-only imports
- **Keep runtime**: For imports used at runtime (like `types`)

#### Context Manager Errors (PYI036)

- **Add types import**: `import types` (runtime)
- **Fix annotations**: Use proper BaseException and TracebackType

#### Security Errors (S108)

- **Use pathlib**: Replace hardcoded paths with Path objects
- **Use temp directories**: Proper temporary file handling

## Success Metrics

### Per Project

- **Linting errors**: 0 (ZERO TOLERANCE)
- **Type errors**: 0 (ZERO TOLERANCE)
- **Test pass rate**: 100%
- **Coverage**: Maintained or improved

### Workspace Level

- **Projects completed**: Track progress through all 25+ projects
- **Pattern consistency**: Same fixes applied consistently
- **No regressions**: Previous projects maintain 0 errors

## Tools and Commands

### Essential Commands

```bash
# Project setup
cd /home/marlonsc/flext/PROJECT_NAME

# Error identification
make lint | head -50  # See first errors
make lint | grep -E "(ERROR|WARN)" | wc -l  # Count total

# Error type analysis
make lint | grep "PYI036" | wc -l  # Context managers
make lint | grep "ANN001" | wc -l  # Missing annotations
make lint | grep "G201" | wc -l    # Logging errors

# Verification
make check  # Must pass 100%
```

### File Patterns to Focus On

- `tests/**/*.py` - Usually need type annotations
- `src/**/logging.py` - Context manager issues
- `src/**/simple_api.py` - Context manager issues
- `src/**/config.py` - ClassVar annotations needed
- `src/**/base.py` - Variable naming issues

## Communication with User

### Progress Reporting

- Always report current error counts
- Show before/after comparisons
- Highlight patterns fixed
- Document any complex issues encountered

### Quality Gate Confirmations

- Confirm 0 errors achieved per project
- Run verification commands
- Update completion status

## Recovery Instructions

If a session gets interrupted:

1. **Check current project status**:

   ```bash
   cd /home/marlonsc/flext/flext-observability  # or current project
   make lint | wc -l  # Check remaining errors
   ```

2. **Identify last completed project**:
   - Check this file for ✅ COMPLETED status
   - Verify with `make lint` in each completed project

3. **Continue from current position**:
   - Resume with the project showing errors
   - Apply the documented patterns
   - Follow the systematic approach

4. **Update this file**:
   - Mark completed projects as ✅ COMPLETED
   - Update error counts for in-progress projects
   - Document any new patterns discovered

## Documentation Updates Required

When patterns change or new issues are discovered:

1. **Update this file** with new patterns
2. **Update CLAUDE.md** if workspace-level changes needed
3. **Update project-specific CLAUDE.md** files if needed

---

**STATUS**: Active quality standardization in progress
**CURRENT FOCUS**: flext-observability (324 errors) → flext-meltano (9 errors) → flext-plugin (45+ errors)
**COMPLETION TARGET**: All 25+ projects with 0 linting errors
**PRIORITY**: CRITICAL - Zero tolerance quality enforcement
