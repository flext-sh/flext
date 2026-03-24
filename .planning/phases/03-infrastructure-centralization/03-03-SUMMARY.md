---
phase: 03-infrastructure-centralization
plan: 03
subsystem: infra
tags: [workarounds, subprocess, model-rebuild, antipatterns]

requires:
  - phase: 03-01
    provides: flext-infra subprocess wrapper (run_raw/run_checked/capture)
provides:
  - Zero workaround antipatterns WA-01 through WA-06 (except WA-05 print)
affects: [all-projects]

tech-stack:
  added: []
  patterns: [centralized-subprocess-execution, find-spec-feature-flags]

key-files:
  created: []
  modified:
    - flext-core/tests/models.py
    - flext-ldif/tests/conftest.py
    - flext-infra/src/flext_infra/_utilities/subprocess.py
    - flext-infra/src/flext_infra/workspace/workspace_makefile.py
    - flext-meltano/src/flext_meltano/singer/translator.py
    - flext-quality/src/flext_quality/utilities.py
    - gruponos-meltano-native/src/gruponos_meltano_native/orchestrator.py
    - gruponos-meltano-native/src/gruponos_meltano_native/core/external_command.py

key-decisions:
  - "Added input_data parameter to run_raw() for stdin support needed by Singer translator"
  - "WA-01 (ImportError) and WA-04 (sys.exit) already clean — no violations found in production code"

patterns-established:
  - "All subprocess execution routed through FlextInfraUtilitiesSubprocess"

requirements-completed: [WA-01, WA-02, WA-03, WA-04, WA-06]

duration: 12min
completed: 2026-03-24
---

# Phase 03 Plan 03: Workaround Eradication Summary

**Removed all model_rebuild() calls and routed 5 direct subprocess.run invocations through FlextInfraUtilitiesSubprocess wrapper with input_data support**

## Task 1: WA-01, WA-02, WA-04

**WA-01 (ImportError):** Zero violations found in production code. The matches in flext-tests/src/ are validator rules that *detect* the pattern, not instances of it.

**WA-02 (model_rebuild):** Removed 6 calls from `flext-core/tests/models.py` and cleaned up empty `_rebuild_pydantic_models()` helper from `flext-ldif/tests/conftest.py`.

**WA-04 (sys.exit):** The 2 instances in flext-quality are inside `if __name__ == "__main__":` guard blocks, which is the correct location. No fix needed.

## Task 2: WA-06, WA-03

**WA-06 (subprocess.run):** Replaced 5 direct calls across 4 projects:

| File | Before | After |
|------|--------|-------|
| flext-infra/workspace/workspace_makefile.py | subprocess.run git rev-parse | FlextInfraUtilitiesSubprocess.capture() |
| flext-meltano/singer/translator.py | subprocess.run with stdin input | FlextInfraUtilitiesSubprocess.run_raw(input_data=) |
| flext-quality/utilities.py | subprocess.run with timeout | FlextInfraUtilitiesSubprocess.run_raw() |
| gruponos-meltano-native/orchestrator.py | subprocess.run meltano jobs | FlextInfraUtilitiesSubprocess.run_raw() |
| gruponos-meltano-native/core/external_command.py | subprocess.run wrapper | FlextInfraUtilitiesSubprocess.run_raw() |

Added `input_data: bytes | None` parameter to `run_raw()` to support Singer translator's stdin piping.

**WA-03 (except Exception:):** Confirmed zero instances in production code.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added input_data parameter to run_raw()**
- **Found during:** Task 2
- **Issue:** Singer translator needs stdin piping (input= parameter) which the wrapper didn't support
- **Fix:** Added `input_data: bytes | None` parameter to `FlextInfraUtilitiesSubprocess.run_raw()` with automatic bytes-to-str decoding
- **Files modified:** flext-infra/src/flext_infra/_utilities/subprocess.py

## Verification Results

- WA-01: 0 `except ImportError` in production code
- WA-02: 0 `model_rebuild()` anywhere in repo
- WA-03: 0 `except Exception:` in production code
- WA-04: 0 `sys.exit()` outside `__main__` guards
- WA-06: 0 `subprocess.run` outside wrapper (flext-infra/_utilities/subprocess.py)
- Ruff: all modified files pass

## Known Stubs

None.
