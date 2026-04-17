---
phase: 08-workaround-residual-cleanup
plan: 02
subsystem: exception-handling
tags: [workaround-cleanup, exception-specificity, sys-exit-compliance]
dependency_graph:
  requires: [08-01]
  provides: [WA-03-complete, WA-04-verified]
  affects: [flext-api, flext-core, flext-ldif, flext-target-ldif, flext-tap-oracle-wms]
tech_stack:
  added: []
  patterns: [specific-exception-catches]
key_files:
  created: []
  modified:
    - flext-api/src/flext_api/serializers.py
    - flext-core/src/flext_core/context.py
    - flext-ldif/src/flext_ldif/services/conversion.py
    - flext-target-ldif/src/flext_target_ldif/writer.py
    - flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py
decisions:
  - "Pydantic ValidationError narrowed to ValueError/TypeError/KeyError in tap-oracle-wms (model_validate raises these)"
  - "context.py simplified error handling — TypeError-only catch removes dead isinstance branch"
metrics:
  duration: 2min
  completed: "2026-03-25"
  tasks: 3
  files: 5
---

# Phase 08 Plan 02: Remove Remaining except Exception Violations Summary

Removed 7 `except Exception` violations from 5 production src/ files and verified WA-04 sys.exit compliance.

## Tasks Completed

### Task 1: Remove Exception from catch tuples in 4 files (241e7e3)

Removed `Exception` from catch tuples in 5 sites across 4 files:

- `serializers.py`: `(ValidationError, Exception)` -> `ValidationError`
- `context.py` (2 sites): `(TypeError, Exception)` -> `TypeError` (also simplified error_msg logic)
- `conversion.py`: `(ValueError, TypeError, AttributeError, RuntimeError, Exception)` -> 4 specific types
- `writer.py`: `(RuntimeError, ValueError, TypeError, OSError, Exception)` -> 4 specific types

### Task 2: Replace bare except Exception in tap-oracle-wms/tap.py (4e9c288)

Replaced 2 bare `except Exception` catches:

- Line 120 (flext_config property): `except (ValueError, TypeError, KeyError)` — covers Pydantic model_validate failures
- Line 251 (initialize method): `except (ValueError, TypeError, KeyError, FlextTapOracleWmsConfigurationError)` — covers settings validation + custom error from property

### Task 3: Verify WA-04 sys.exit compliance (verification only)

All 9 `sys.exit()` calls in production src/ (non-`__main__.py` files) are inside `if __name__ == "__main__":` guards:

| File | Line | Guard |
|------|------|-------|
| flext-dbt-oracle-wms/cli.py | 120 | L119 `if __name__` |
| flext-dbt-ldif/cli.py | 168 | L167 `if __name__` |
| flext-quality/style_validator.py | 782 | L777 `if __name__` |
| flext-quality/content_analyzer.py | 910 | L905 `if __name__` |
| flext-infra/path_sync.py | 467 | L466 `if __name__` |
| flext-tap-oracle-oic/tap_client.py | 474 | L473 `if __name__` |
| flext-target-oracle/target_refactored.py | 54 | L53 `if __name__` |
| algar-oud-mig/cli.py | 751 | L750 `if __name__` |
| flext-infra/extra_paths.py | 580 | L579 `if __name__` |

WA-04 fully compliant per D-06/D-07/D-08 rationale.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- [x] flext-api/src/flext_api/serializers.py — modified, zero Exception catches
- [x] flext-core/src/flext_core/context.py — modified, zero Exception catches
- [x] flext-ldif/src/flext_ldif/services/conversion.py — modified, zero Exception catches
- [x] flext-target-ldif/src/flext_target_ldif/writer.py — modified, zero Exception catches
- [x] flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py — modified, zero Exception catches
- [x] Commit 241e7e3 exists
- [x] Commit 4e9c288 exists
- [x] ruff clean on all 5 files
