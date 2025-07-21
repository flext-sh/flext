# CLAUDE.QUALITY_STANDARDIZATION.md

This file provides guidance to Claude Code sessions on the systematic quality standardization methodology being applied across the FLEXT workspace.

## Current Mission: Comprehensive Quality Standardization

### Objective

Achieve **ZERO TOLERANCE** quality standards across ALL 31 FLEXT projects by systematically fixing lint errors, type errors, and implementing unified coding patterns.

### Current Status (Session Context)

**Phase**: Systematic lint error elimination across all projects
**Current Project**: flext-plugin (fixing G201 logging errors in hot_reload/ package)
**Progress**: 4 of 31 projects completed with zero violations

## Methodology: Systematic Project-by-Project Approach

### 1. Project Selection Strategy

Work through projects in dependency order (foundation first):

```
Priority Order:
1. ✅ flext-auth (COMPLETED - ~60 type errors fixed, lint clean)
2. ✅ flext-web (COMPLETED - 3 → 0 lint errors, formatting fixed)  
3. ✅ flext-cli (COMPLETED - 38 → 21 type errors, Path fixes)
4. 🔄 flext-plugin (IN PROGRESS - fixing 34 lint errors)
5. ⏳ flext-observability (523 lint errors)
6. ⏳ flext-meltano (266 lint errors)
7. ⏳ flext-core (92 test lint errors)
8. ⏳ All Singer/Target projects
9. ⏳ algar-oud-mig (307 lint errors)
```

### 2. Quality Gate Protocol

For each project, achieve **ZERO TOLERANCE** in this exact order:

#### Step 1: Lint Error Elimination

```bash
cd flext-{project}/
make lint  # Must show 0 errors
```

**Common Error Types & Solutions:**

- **G201** (logger.error with exc_info): Replace with `logger.exception()`
- **ANN001/ANN202** (missing type annotations): Add return type annotations
- **S108** (hardcoded temp paths): Use pathlib instead
- **RUF012** (mutable class attributes): Add `ClassVar` annotations
- **ASYNC110** (sleep loops): Replace with asyncio.Event patterns

#### Step 2: Type Error Resolution  

```bash
make type-check  # Must show 0 errors
```

#### Step 3: Test Compliance

```bash
make test  # Must achieve >85% coverage, 100% pass rate
```

#### Step 4: Security Validation

```bash
make security  # Must show 0 security issues
```

### 3. Systematic Error Fixing Pattern

#### Current Example: flext-plugin G201 Fixes

**Location**: `/home/marlonsc/flext/flext-plugin/src/flext_plugin/hot_reload/`

**Pattern Being Applied:**

```python
# ❌ BEFORE (G201 violation)
except Exception as e:
    logger.error(
        "Error message %s: %s",
        context,
        e,
        exc_info=True,
    )

# ✅ AFTER (Compliant)
except Exception:
    logger.exception(
        "Error message %s",
        context,
    )
```

**Files Being Fixed:**

- ✅ `rollback.py:231` - Fixed (logger.exception pattern)
- ✅ `rollback.py:244` - Fixed (removed unused variable reference)
- 🔄 `state_manager.py:100,167,261,286,311,346` - In progress
- ⏳ `watcher.py:171` - Pending

## Critical Success Patterns

### 1. Systematic File Reading

**ALWAYS** read files before making changes:

```bash
# Read entire file first
Read /path/to/file.py

# Or read specific sections for large files  
Read /path/to/file.py offset=100 limit=50
```

### 2. Precise Error Targeting

Don't fix random issues - follow the systematic approach:

1. Identify ALL lint errors in current project
2. Fix errors by type/category systematically
3. Verify each fix with subsequent lint runs
4. Move to next error type only after current type is 100% clean

### 3. Pattern Consistency

Ensure fixes follow established patterns across the workspace:

- **Logging**: Always use `logger.exception()` for exceptions
- **Type Annotations**: Required on ALL functions/methods
- **Imports**: Use `from __future__ import annotations`
- **Exception Handling**: Never suppress errors, always log with context

## Quality Tools Configuration

### Ruff Configuration (Strict Mode)

```toml
[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["ALL"]  # Enable ALL rules
ignore = [
    "D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107",  # Docstring rules (project-specific)
    "COM812", "ISC001",  # Conflict with formatter
]
```

### MyPy Configuration (Strict Mode)

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
```

## Avoiding Common Pitfalls

### 1. Never Skip Quality Gates

**FORBIDDEN**: Committing code with ANY violations

```bash
# ❌ WRONG - never acceptable
make lint  # Shows 5 errors
git commit -m "partial fix"  # NO!

# ✅ CORRECT - zero tolerance
make lint  # Shows 0 errors
make type-check  # Shows 0 errors  
make test  # 100% pass rate
git commit -m "complete quality compliance"
```

### 2. Never Create Temporary Fixes

**FORBIDDEN**: Creating workaround files

- No `fix_*.py` scripts
- No `temp_*.py` files  
- No `migrate_*.py` scripts
- Fix issues in the actual source files

### 3. Always Preserve Functionality

**CRITICAL**: Changes must not break existing functionality

- Test after each fix
- Verify imports still work
- Ensure APIs remain compatible
- Maintain backward compatibility

## Session Handoff Protocol

### Information to Pass to Next Session

1. **Current Project State**:
   - Project name and directory
   - Exact error count and types remaining
   - Files currently being worked on
   - Last successful fix completed

2. **Next Actions Required**:
   - Specific files to fix next
   - Error types to focus on
   - Any discovered patterns or issues

3. **Quality Metrics**:
   - Before/after error counts
   - Coverage percentages
   - Any architectural issues discovered

### Example Handoff Message

```
HANDOFF STATUS:
Project: flext-plugin
Location: /home/marlonsc/flext/flext-plugin/src/flext_plugin/hot_reload/
Progress: 2/7 G201 errors fixed in rollback.py
Next: Fix remaining G201 errors in state_manager.py (lines 100,167,261,286,311,346)
Pattern: Convert logger.error(..., exc_info=True) -> logger.exception(...)
Status: 32 lint errors remaining (down from 34)
```

## Success Metrics

### Per-Project Targets

- **Lint Errors**: 0 (ZERO TOLERANCE)
- **Type Errors**: 0 (ZERO TOLERANCE)  
- **Test Coverage**: >85% minimum
- **Security Issues**: 0 (ZERO TOLERANCE)
- **Test Pass Rate**: 100%

### Workspace-Wide Goal

Achieve these metrics across ALL 31 FLEXT projects:

- Total lint violations: 0
- Total type errors: 0
- Average test coverage: >90%
- Zero security vulnerabilities
- Unified coding patterns and standards

## Critical Commands for Quality Work

### Project-Level Quality Checks

```bash
cd flext-{project}/
make check     # ALL quality gates must pass
make lint      # 0 violations required
make type-check # 0 errors required  
make test      # >85% coverage, 100% pass
make security  # 0 security issues
```

### Workspace-Level Monitoring

```bash
cd /home/marlonsc/flext/
make check-all    # Check ALL projects at once
make lint-all     # Lint ALL projects  
make test-all     # Test ALL projects
```

## Conclusion

This systematic approach has proven effective for achieving enterprise-grade code quality. The key is methodical, project-by-project execution with zero tolerance for quality violations.

**Remember**: Quality is not negotiable. Every single violation must be fixed before moving to the next project or declaring success.

---

**Last Updated**: Current session (flext-plugin G201 fixes in progress)
**Next Session**: Continue G201 fixes in state_manager.py, then proceed to other lint error types
