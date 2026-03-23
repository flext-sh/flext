# Phase 3: Merge test_automated_* into primary test files

## Results

| Automated File | Primary File | Archived? | Unique Tests Merged | Tests Moved |
|---|---|---|---|---|
| `test_automated_result.py` | `test_result.py` | Yes | 4 hypothesis property tests (identity, composition, left-unit laws, error propagation) | 4 |
| `test_automated_runtime.py` | `test_runtime.py` | Yes | 2 hypothesis type guard tests | 2 |
| `test_automated_container.py` | `test_container.py` | Yes | scoped container test + hypothesis roundtrip | 2 |
| `test_automated_context.py` | `test_context.py` | Yes | hypothesis set/get roundtrip | 1 |
| `test_automated_dispatcher.py` | `test_dispatcher_full_coverage.py` | Yes | None (all semantically covered) | 0 |
| `test_automated_service.py` | `test_service.py` | Yes | hypothesis execute test | 1 |
| `test_automated_loggings.py` | `test_loggings_full_coverage.py` | Yes | None (all semantically covered) | 0 |
| `test_automated_exceptions.py` | `test_exceptions.py` | Yes | 2 hypothesis tests (to_dict message, all types with arbitrary inputs) | 2 |
| `test_automated_decorators.py` | `test_decorators.py` | Yes | hypothesis railway division test | 1 |
| `test_automated_handlers.py` | `test_handlers.py` | Yes | hypothesis create_from_callable test | 1 |
| `test_automated_registry.py` | `test_registry.py` | Yes | hypothesis plugin roundtrip | 1 |
| `test_automated_mixins.py` | `test_mixins.py` | Yes | 4 tests (CQRS MetricsTracker, ContextStack, validate_with_result, hypothesis validation) | 4 |
| `test_automated_utilities.py` | `test_utilities.py` | Yes | 2 hypothesis tests (empty, generate) | 2 |
| `test_automated_settings.py` | `test_settings_coverage.py` (created) | Yes | All 10 tests (no prior primary existed) | 10 |
| `test_automated_architecture.py` | N/A | **Kept** | N/A | N/A |

## Totals

- **Files archived:** 14
- **Files kept as-is:** 1 (`test_automated_architecture.py`)
- **Total lines archived:** 1,517
- **Total unique tests merged:** 31
- **New file created:** `test_settings_coverage.py`
- **Lint status:** All checks passed (ruff)
