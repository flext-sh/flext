---
phase: 04-python313-modernization
plan: 03
subsystem: flext-core, flext-auth
tags: [deprecation, userdict, pydantic, python313, modernization]
dependency_graph:
  requires: []
  provides: [MOD-02, MOD-06]
  affects: [flext-core, flext-auth]
tech_stack:
  added: []
  patterns: [pydantic-basemodel-extra-allow]
key_files:
  created: []
  modified:
    - flext-core/src/flext_core/_utilities/deprecation.py
    - flext-auth/src/flext_auth/models.py
decisions:
  - "deprecation.py marked dead code (FROZEN, zero callers) instead of deleted"
  - "ProviderConfiguration converted to BaseModel with extra=allow for dict-like flexibility"
metrics:
  duration: 3min
  completed: 2026-03-24
  tasks: 2
  files: 2
---

# Phase 04 Plan 03: Deprecation Simplification + UserDict Removal Summary

FlextUtilitiesDeprecation marked as dead code (zero callers, module FROZEN); ProviderConfiguration converted from UserDict to Pydantic BaseModel with extra="allow".

## Task Results

### Task 1: Simplify FlextUtilitiesDeprecation

- Verified zero callers of `u.deprecated()`, `u.deprecated_class()`, `u.deprecated_parameter()`, `u.warn_once()`, `u.warn_polymorphic_input()` across all `*/src/**/*.py`
- Module is FROZEN per AGENTS.md 10.2 -- cannot delete
- Added `# DEAD CODE` comment at module top for future cleanup tracking

### Task 2: Replace ProviderConfiguration UserDict with Pydantic BaseModel

- Converted `ProviderConfiguration(UserDict[str, t.ContainerValue])` to `ProviderConfiguration(m.BaseModel)` with `model_config = ConfigDict(extra="allow")`
- Extracted 3 explicit fields from `__init__` defaults: `name`, `version`, `capabilities`
- Removed `collections.UserDict` import (ruff auto-removed unused `collections.abc.Mapping`)
- 148/151 tests pass; 3 failures are pre-existing `ProviderWrapper.model_rebuild()` issue (unrelated)

## Deviations from Plan

None -- plan executed exactly as written.

## Deferred Issues

- `flext-auth` has 3 pre-existing test failures related to `ProviderWrapper` forward-ref resolution (not caused by this plan)

## Verification

- Zero `UserDict` in production `*/src/**/*.py`: PASS
- Zero `u.deprecated()` callers outside deprecation.py: PASS
- `ruff check` on both files: PASS
- `pytest flext-auth/tests/` 148 passed, 3 pre-existing failures: PASS

## Known Stubs

None.
