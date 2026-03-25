---
phase: 08-workaround-residual-cleanup
plan: 01
subsystem: workspace-wide
tags: [workaround-cleanup, exception-handling, logging, WA-03, WA-04, WA-05]
dependency_graph:
  requires: []
  provides: [WA-03-compliant, WA-04-compliant, WA-05-compliant]
  affects: [flext-quality, flext-core, flext-observability, flext-meltano, flext-oracle-wms, flext-web, flext-auth, flext-db-oracle, flext-grpc, flext-plugin, flext-target-oracle-wms]
tech_stack:
  added: []
  patterns: [structlog-logging, specific-exception-handling]
key_files:
  created: []
  modified:
    - flext-quality/src/flext_quality/docs/scheduled_maintenance.py
    - flext-quality/docs/maintenance/scheduled_maintenance.py
    - flext-core/tests/unit/test_context.py
    - flext-observability/tests/integration/test_phase_11_integration.py
    - flext-meltano/tests/unit/test_tap_abstractions.py
    - flext-meltano/tests/unit/test_services.py
    - flext-oracle-wms/tests/oracle_wms_focused_discovery.py
    - flext-oracle-wms/tests/oracle_wms_complete_discovery.py
    - flext-oracle-wms/tests/oracle_wms_optimized_discovery.py
    - flext-oracle-wms/tests/test_declarative.py
    - flext-web/tests/unit/test_utilities.py
    - flext-web/tests/integration/test_examples.py
    - flext-plugin/examples/03_docker_integration.py
    - flext-auth/examples/simple_usage_08.py
    - flext-auth/examples/basic_refactored_usage_06.py
    - flext-db-oracle/examples/07_sqlalchemy2.py
    - flext-db-oracle/examples/05_simple_working.py
    - flext-meltano/examples/01_simple_working.py
    - flext-grpc/examples/03_error_handling_patterns.py
    - flext-oracle-wms/examples/03_complete_functionality_showcase.py
    - flext-oracle-wms/examples/02_singleton_config.py
    - flext-oracle-wms/examples/01_basic_usage.py
    - flext-web/examples/02_api_usage.py
    - flext-web/examples/01_basic_service.py
    - flext-target-oracle-wms/examples/03_error_handling.py
    - examples/advanced_processing_example.py
    - fix_dollar.py
decisions:
  - "structlog.get_logger() for scheduled_maintenance.py print() replacement (not FlextLogger — module is standalone quality tooling)"
  - "D-03 exemptions preserved: conftest_factory.py, docker_test_manager.py, docker_infra.py keep bare except Exception:"
  - "Observability integration test uses (AssertionError, RuntimeError, ValueError, TypeError) tuple for module-level smoke blocks"
metrics:
  duration: 4min
  completed: 2026-03-25
---

# Phase 08 Plan 01: Workaround Residual Cleanup Summary

Eliminated all residual workaround violations: 2 bare print() replaced with structlog, ~45 bare except Exception: replaced with specific types across tests/examples, WA-04 verified compliant.

## Tasks Completed

### Task 1: Fix print() in production + verify WA-04 compliance

- Replaced `print(message)` with `logger.info(message)` in both `scheduled_maintenance.py` files
- Added `import structlog` and module-level `logger = structlog.get_logger(__name__)`
- Fixed bare `except Exception:` to `(OSError, ValueError)` in docs copy
- Verified WA-03: zero `except Exception:` in any `src/` production code
- Verified WA-04: all `sys.exit()` calls inside `if __name__ == "__main__":` guards

### Task 2: Fix bare except Exception: in tests and examples

**Tests fixed (26 occurrences across 10 files):**
- flext-core/tests: `(KeyError, RuntimeError)` for context get/set operations
- flext-observability/tests: `(AssertionError, RuntimeError, ValueError, TypeError)` for integration smoke tests (10 occurrences)
- flext-meltano/tests: specific types for tap abstractions and service method tests
- flext-oracle-wms/tests: `(RuntimeError, OSError, ValueError, KeyError)` for Oracle DB discovery scripts (7 occurrences)
- flext-web/tests: `(ImportError, RuntimeError, ValueError, TypeError, AttributeError, AssertionError, OSError)` for example integration tests (5 occurrences), `(ValueError, TypeError)` for validation test

**Examples fixed (16 occurrences across 14 files):**
- Socket operations: `OSError`
- Main entry points: `(RuntimeError, ValueError, OSError)`
- DB config: `(ValueError, OSError, RuntimeError)`
- Data processing: `(KeyError, ValueError, TypeError)`

**Other:** fix_dollar.py (2 occurrences) fixed to `(subprocess.CalledProcessError, OSError)`

**D-03 exemptions preserved (5 occurrences in 3 files):**
- `flext-ldif/tests/support/conftest_factory.py` (3) — test cleanup utility
- `flext-meltano/tests/helpers/docker_test_manager.py` (1) — infrastructure cleanup
- `flext-ldap/tests/_utilities/docker_infra.py` (1) — infrastructure cleanup

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED
