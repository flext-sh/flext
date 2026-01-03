# Plan: Fix All Pytest Failures Across FLEXT Projects

**Created**: 2026-01-02
**Status**: PENDING
**Priority**: HIGH

## Goal

Fix ALL pytest failures across FLEXT core projects to achieve green test suites with 80%+ coverage.

## Scope

Projects (in dependency order):

1. flext-core (foundation - fix first)
2. flext-cli (depends on flext-core)
3. flext-ldif (depends on flext-core)
4. flext-ldap (depends on flext-core, flext-ldif)

## Current State

| Project    | Tests | Passed | Failed | Status       |
| ---------- | ----- | ------ | ------ | ------------ |
| flext-core | 3486  | 3447   | 39     | Failures     |
| flext-cli  | ~500  | 0      | ALL    | Import Error |
| flext-ldif | 3005  | ~2900  | ~50+   | Failures     |
| flext-ldap | 270   | 269    | 1      | Failures     |

No hanging tests detected - all tests complete within timeout.

## Failure Pattern Analysis

### Pattern 1: NoneType in Decorators (~25 failures in flext-core)

**Error:**
```
AttributeError: 'NoneType' object has no attribute 'is_failure'
AttributeError: 'NoneType' object has no attribute 'is_success'
```

**Location:** `flext-core/src/flext_core/decorators.py:1079`

**Root Cause:** The `_bind_operation_context` function returns `None` instead of a Result object when the decorated function doesn't return a Result.

Fix Strategy:

- Review decorator logic in `decorators.py`
- Ensure decorated functions always return `r[T]`
- Add guard to handle None returns gracefully

### Pattern 2: Missing API Methods (2 failures in flext-core)

Error:

```text
AttributeError: type object 'FlextTestsUtilities' has no attribute 'validate_pipeline'
```

Location: `tests/unit/test_utilities_validation.py:883, 895`

Root Cause: API method `validate_pipeline` was renamed or removed from `FlextTestsUtilities`.

Fix Strategy:

- Find the new method name (suggestion: `validate_positive`)
- Update test to use correct API
- Or restore the method if accidentally removed

### Pattern 3: Singleton Configuration Errors (4 failures in flext-core)

Error:

```text
ValidationError: Class FlextSettings does not have get_global_instance method
ValidationError: Class SingletonClassForTest does not have get_global_instance method
```

Location: `flext-core/src/flext_core/_utilities/configuration.py:568`

Root Cause: Singleton pattern API changed - classes no longer have `get_global_instance` method.

Fix Strategy:

- Review singleton pattern implementation
- Update tests to use new singleton API
- Or restore `get_global_instance` method

### Pattern 4: Pydantic Model Validation (1+ failures in flext-core)

Error:

```text
pydantic_core._pydantic_core.ValidationError: 16 validation errors for Customer
```

Location: `tests/unit/test_coverage_models.py:581`

Root Cause: Pydantic v2 strict validation - test data doesn't match model field requirements.

Fix Strategy:

- Review `Customer` model field definitions
- Update test data to match Pydantic v2 validation rules
- Use proper type coercion or `model_validate()` with strict=False

### Pattern 5: Missing Model Namespace (BLOCKS flext-cli)

Error:

```text
AttributeError: type object 'Cli' has no attribute 'Entity'
```

Location: `flext-cli/tests/conftest.py` (import time)

Root Cause: `FlextCliModels.Cli.Entity` class was moved or renamed.

Fix Strategy:

- Find where `Entity` model now lives
- Update imports in conftest.py
- This is a BLOCKING issue - must fix first for flext-cli

### Pattern 6: Model Serialization (1 failure in flext-ldap)

Error:

```text
AssertionError: Missing... (test_sync_stats_serialization)
```

Location: `tests/unit/test_models.py`

Root Cause: `SyncStats` model serialization changed - likely field name or structure change.

Fix Strategy:

- Review `SyncStats` model `model_dump()` output
- Update test expectations to match current serialization

### Pattern 7: Migration Quirks Logic (Multiple in flext-ldif)

Error:

```text
FAILED test_oid_acl_conversion_oid_to_rfc
```

Location: `tests/unit/test_migration_pipeline_quirks.py`

Root Cause: OID to RFC ACL conversion logic or expected values changed.

Fix Strategy:

- Review quirks handling implementation
- Verify expected conversion results
- Update test data or fix conversion logic

## Implementation Plan

### Phase 1: Fix flext-core Foundation (MUST DO FIRST)

All other projects depend on flext-core. Fix these first.

#### Task 1.1: Fix Decorator NoneType Returns

- [ ] Read `decorators.py:1079` and understand `_bind_operation_context`
- [ ] Add null check before accessing `.is_failure`/`.is_success`
- [ ] Or fix root cause: ensure decorated functions return Result
- [ ] Run tests to verify fix

#### Task 1.2: Fix Missing validate_pipeline API

- [ ] Search for `validate_pipeline` in codebase
- [ ] Find replacement method or restore it
- [ ] Update tests in `test_utilities_validation.py`

#### Task 1.3: Fix Singleton get_global_instance

- [ ] Review `configuration.py:568` singleton validation
- [ ] Either restore method or update tests to new API
- [ ] Fix 4 affected tests

#### Task 1.4: Fix Pydantic Customer Model

- [ ] Read `Customer` model definition
- [ ] Review test data in `test_coverage_models.py:581`
- [ ] Update test data to match Pydantic v2 validation

#### Task 1.5: Verify flext-core Green

- [ ] Run full test suite: `make test`
- [ ] Ensure 0 failures
- [ ] Verify 79%+ coverage maintained

### Phase 2: Fix flext-cli Import Error

#### Task 2.1: Find Entity Model Location

- [ ] Search for `Entity` class in flext-cli and flext-core
- [ ] Determine correct import path

#### Task 2.2: Fix conftest.py Import

- [ ] Update `FlextCliModels.Cli.Entity` reference
- [ ] Verify tests can be collected

#### Task 2.3: Run flext-cli Tests

- [ ] Run full test suite
- [ ] Fix any additional failures
- [ ] Verify 75%+ coverage

### Phase 3: Fix flext-ldif Failures

#### Task 3.1: Fix Migration Quirks Tests

- [ ] Review `test_migration_pipeline_quirks.py`
- [ ] Verify OID/ACL conversion logic
- [ ] Update test expectations or fix logic

#### Task 3.2: Fix Remaining Failures

- [ ] Run tests to identify all failures
- [ ] Categorize and fix each pattern
- [ ] Verify 75%+ coverage

### Phase 4: Fix flext-ldap Failure

#### Task 4.1: Fix SyncStats Serialization

- [ ] Read `SyncStats` model
- [ ] Review `test_sync_stats_serialization` expected values
- [ ] Update test or model as needed
- [ ] Verify 75%+ coverage

### Phase 5: Cross-Project Validation

#### Task 5.1: Full Workspace Validation

- [ ] Run `make validate` from workspace root
- [ ] Verify all 4 projects pass
- [ ] Document any remaining issues

## Progress Tracking

- [ ] Phase 1: Fix flext-core Foundation
- [ ] Phase 2: Fix flext-cli Import Error
- [ ] Phase 3: Fix flext-ldif Failures
- [ ] Phase 4: Fix flext-ldap Failure
- [ ] Phase 5: Cross-Project Validation

Total Tasks: 13 | Completed: 0 | Remaining: 13

## Constraints

- Follow FLEXT patterns (Result[T], full namespaces, no Any/cast)
- Maintain 79%+ coverage for flext-core, 75%+ for others
- Use Pydantic v2 APIs (no v1 patterns)
- Fix in dependency order (flext-core first)

## Risks

1. Decorator changes may break production code - Review carefully before changing
2. Missing API may be intentional - Check git history for removal reason
3. Pydantic v2 migration incomplete - May reveal more issues

## Working Set

Branch: main

Key files:

- `flext-core/src/flext_core/decorators.py`
- `flext-core/src/flext_core/_utilities/configuration.py`
- `flext-cli/tests/conftest.py`
- `flext-ldif/tests/unit/test_migration_pipeline_quirks.py`
- `flext-ldap/tests/unit/test_models.py`
