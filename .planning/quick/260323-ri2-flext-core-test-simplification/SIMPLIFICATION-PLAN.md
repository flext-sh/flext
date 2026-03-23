# flext-core/tests Simplification Plan

**Date**: 2026-03-23
**Scope**: `flext-core/tests/unit/` (154 files, ~43,600 lines)
**Target**: ~95 files, ~28,000 lines — **35% reduction with zero coverage loss**

---

## Root Cause

Test suite grew through coverage-target campaigns. Each phase added `*_full_coverage.py`,
`*_coverage_100.py`, `test_automated_*.py`, and `test_coverage_*.py` files independently,
without deduplication. The result: 3–5 files per module, 20 files with identical boilerplate
padding blocks, and 4 files whose names encode obsolete coverage percentages.

---

## Execution Phases (ordered by risk)

### Phase 1 — Delete empty/stub files (ZERO risk, ~1,460 lines)

These contain only `from __future__ import annotations` + a docstring, or 1 assertion
testing infrastructure imports rather than the module under test.

| File | Lines | Reason |
|------|-------|--------|
| `test_utilities_validators_new.py` | 3 | Empty stub — "tests removed after API deletion" |
| `test_utilities_pattern_full_coverage.py` | 3 | Empty stub — "obsolete after API deletion" |
| `test_constants_full_coverage.py` | 19 | 1 boilerplate assertion, zero module tests |
| `test_utilities_conversion_full_coverage.py` | 21 | Boilerplate-only |
| `test_utilities_deprecation_full_coverage.py` | 24 | Boilerplate-only |
| `test_models_container_full_coverage.py` | 26 | Boilerplate-only |
| `test_dispatcher_reliability_full_coverage.py` | 27 | Boilerplate-only |
| `test_utilities_pagination_full_coverage.py` | 31 | Boilerplate-only |
| `test_settings_full_coverage.py` | 37 | Boilerplate-only |
| `test_models_handler_full_coverage.py` | 48 | Boilerplate-only |
| `test_models_service_full_coverage.py` | 54 | Boilerplate-only |
| `test_utilities_args_full_coverage.py` | 75 | Boilerplate-only |
| `test_utilities_checker_full_coverage.py` | 189 | Boilerplate-only |
| `test_utilities_model_full_coverage.py` | 68 | Boilerplate-only |
| `test_utilities_reliability_full_coverage.py` | 87 | Boilerplate-only |
| `test_models_settings_full_coverage.py` | 84 | Boilerplate-only |
| `test_models_collections_full_coverage.py` | ~100 | Boilerplate-only |
| `test_models_validation_full_coverage.py` | ~100 | Boilerplate-only |
| `test_service_full_coverage.py` | ~120 | Boilerplate-only |
| `test_utilities_collection_full_coverage.py` | 195 | Boilerplate-only |
| `test_exceptions_full_coverage.py` | 78 | Boilerplate stub — 1 real assertion |

**How to delete**: `mv <file> <file>.bak` (never `rm`) per CLAUDE.md safe-delete policy

---

### Phase 2 — Delete coverage-number files (LOW risk, ~1,025 lines)

Files named after coverage targets. All unique tests within them must be cherry-picked
into the corresponding primary file BEFORE deletion.

| File | Lines | Cherry-pick into |
|------|-------|-----------------|
| `test_coverage_76_lines.py` | 192 | `test_result.py` — Result bool/or ops all duplicated |
| `test_final_75_percent_push.py` | 324 | `test_result.py`, `test_exceptions.py` — scattered padding |
| `test_phase2_coverage_final.py` | 179 | `test_settings_coverage.py` — Settings + Result coverage |
| `test_models_79_coverage.py` | 330 | `test_models.py` — DDD model coverage padding |

**Process**: Read each file → identify any test not in primary → move it → delete the file.

---

### Phase 3 — Merge `test_automated_*.py` into primary files (MEDIUM risk, ~1,578 lines)

These are AI-generated files with overlapping coverage. All unique tests must be
verified against the primary before deletion.

| Source | Lines | Merge into |
|--------|-------|-----------|
| `test_automated_result.py` | 150 | `test_result.py` |
| `test_automated_runtime.py` | 120 | `test_runtime.py` |
| `test_automated_container.py` | 137 | `test_container.py` |
| `test_automated_context.py` | 88 | `test_context.py` |
| `test_automated_dispatcher.py` | 76 | `test_dispatcher.py` (new) |
| `test_automated_service.py` | 86 | `test_service.py` |
| `test_automated_loggings.py` | 60 | `test_loggings.py` (new) |
| `test_automated_exceptions.py` | 171 | `test_exceptions.py` |
| `test_automated_decorators.py` | 76 | `test_decorators.py` |
| `test_automated_handlers.py` | 100 | `test_handlers.py` |
| `test_automated_registry.py` | 70 | `test_registry.py` |
| `test_automated_mixins.py` | 90 | `test_mixins.py` |
| `test_automated_settings.py` | 140 | `test_settings.py` (primary) |
| `test_automated_architecture.py` | 61 | Keep separately — unique |
| `test_automated_utilities.py` | 53 | `test_utilities.py` |

---

### Phase 4 — Consolidate module clusters (HIGHEST impact, ~5,500 lines saved)

Each cluster has 3–5 files testing the same module. Merge into one well-organized file.
Within each merged file: use `@pytest.mark.parametrize` to replace duplicated bodies.

#### 4a: Result cluster → `test_result.py` (keep + enrich)
- Absorb: `test_result_coverage_100.py` (517), `test_result_full_coverage.py` (149), `test_result_additional.py` (~100)
- Keep separate: `test_result_exception_carrying.py` (414) — distinct concern
- Target: single `test_result.py` ≤ 800 lines

#### 4b: Runtime cluster → `test_runtime.py` (keep + enrich)
- Absorb: `test_runtime_full_coverage.py` (1073), `test_runtime_coverage_100.py` (292)
- Target: single `test_runtime.py` ≤ 1,300 lines

#### 4c: Container cluster → `test_container.py` (keep + enrich)
- Absorb: `test_container_full_coverage.py` (783)
- Keep separate: `test_models_container.py` (384) — different concern (models vs lifecycle)
- Target: single `test_container.py` ≤ 900 lines

#### 4d: Context cluster → `test_context.py` (keep + enrich)
- Absorb: `test_context_full_coverage.py` (213), `test_context_coverage_100.py` (433), `test_coverage_context.py` (~200)
- Target: single `test_context.py` ≤ 800 lines

#### 4e: Dispatcher cluster → `test_dispatcher.py` (new primary)
- Absorb: `test_dispatcher_full_coverage.py` (207), `test_dispatcher_minimal.py` (180), `test_dispatcher_di.py` (30), `test_dispatcher_timeout_coverage_100.py` (229)
- Keep separate: `test_dispatcher_reliability.py` (90) — timing-dependent, distinct
- Target: single `test_dispatcher.py` ≤ 400 lines

#### 4f: Service cluster → `test_service.py` (keep + enrich)
- Absorb: `test_service_coverage_100.py` (93), `test_service_additional.py` (64)
- Keep separate: `test_service_bootstrap.py` (~120) — bootstrap lifecycle
- Target: single `test_service.py` ≤ 350 lines

#### 4g: Loggings cluster → `test_loggings.py` (new primary)
- Absorb: `test_loggings_full_coverage.py` (575), `test_coverage_loggings.py` (649), `test_loggings_error_paths_coverage.py` (52)
- Keep separate: `test_loggings_strict_returns.py` (211) — r[bool] contract testing
- Target: single `test_loggings.py` ≤ 700 lines

#### 4h: Exceptions cluster → `test_exceptions.py` (keep + enrich)
- Absorb: `test_coverage_exceptions.py` (434)
- Target: single `test_exceptions.py` ≤ 1,000 lines

#### 4i: Utilities mapper cluster → `test_utilities_mapper.py` (new primary)
- Absorb: `test_utilities_mapper_coverage_100.py` (526), `test_utilities_data_mapper.py` (178)
- Target: single `test_utilities_mapper.py` ≤ 1,400 lines

#### 4j: Utilities collection cluster → `test_utilities_collection.py` (new primary)
- Absorb: `test_collection_utilities_coverage_100.py` (303), `test_collections_coverage_100.py` (350)
- Target: single `test_utilities_collection.py` ≤ 1,200 lines

#### 4k: Decorators cluster → `test_decorators.py` (keep + enrich)
- Absorb: `test_decorators_full_coverage.py` (608), `test_decorators_discovery_full_coverage.py`
- Target: single `test_decorators.py` ≤ 700 lines

#### 4l: Handlers cluster → `test_handlers.py` (keep + enrich)
- Absorb: `test_handlers_full_coverage.py`, `test_handler_decorator_discovery.py`
- Target: single `test_handlers.py` ≤ 650 lines

#### 4m: Registry cluster → `test_registry.py` (keep + enrich)
- Absorb: `test_registry_full_coverage.py`
- Target: single `test_registry.py` ≤ 400 lines

#### 4n: Mixins cluster → `test_mixins.py` (keep + enrich)
- Absorb: `test_mixins_full_coverage.py` (590)
- Target: single `test_mixins.py` ≤ 700 lines

---

### Phase 5 — Relocate misplaced files (HOUSEKEEPING)

These test `flext_infra` tools, not `flext_core`. They belong in `flext-infra/tests/`:

- `test_refactor_cli_models_workflow.py`
- `test_refactor_migrate_to_class_mro.py`
- `test_refactor_namespace_enforcer.py`
- `test_refactor_policy_family_rules.py`
- `test_transformer_class_nesting.py`
- `test_transformer_helper_consolidation.py`
- `test_transformer_nested_class_propagation.py`

---

## Anti-patterns to eliminate during merge

When merging files, apply these rules to the resulting test:

1. **Boilerplate padding block** — Remove this block from all merged files (it appears
   in 20+ `*_full_coverage.py` files):
   ```python
   assert c.UNKNOWN_ERROR
   assert isinstance(m.Categories(), m.Categories)
   assert r[int].ok(1).is_success
   assert isinstance(t.ConfigMap({"k": 1}), t.ConfigMap)
   assert u.to_str(1) == "1"
   ```

2. **Coverage-number test names** — Rename any `test_push_coverage_to_76_percent` style
   functions to describe what they actually test.

3. **Duplicate fixture setup** — Where 3+ tests do `service = ComplexService(); service.x = val`,
   extract a parametrized fixture.

4. **Post-construction Pydantic mutation** — Replace `obj = Model(); obj.field = val` with
   `obj = Model(field=val)` per AGENTS.md convention.

---

## Files NOT to touch

- `tests/integration/` — separate tier, do not merge with unit
- `tests/benchmark/` — performance tests, keep isolated
- `tests/base.py`, `tests/conftest.py`, `tests/constants.py` — shared infrastructure
- `test_result_exception_carrying.py` — distinct concern (exception propagation)
- `test_loggings_strict_returns.py` — distinct concern (r[bool] contracts)
- `test_di_incremental.py` — DI incremental wiring, distinct pattern
- `test_di_services_access.py` — DI access patterns, distinct
- `test_utilities_cache_coverage_100.py` — cache module, distinct
- `test_utilities_type_checker_coverage_100.py` — type checker, distinct
- `test_utilities_type_guards_coverage_100.py` — type guards, distinct
- `test_utilities_guards_full_coverage.py` — guards, distinct
- `test_utilities_string_parser.py` — string parser, distinct
- `test_protocols.py` — protocol compliance, distinct
- `test_namespace_validator.py` — infra validator, distinct
- `test_version.py` — version module, standalone
- `test_deprecation_warnings.py` — deprecation warnings, distinct
- `test_config.py` — config, standalone
- `test_models.py` — primary DDD model tests

---

## Quality constraints for execution

Every merged file must pass:
```bash
make check PROJECT=flext-core CHECK_GATES=lint
make test PROJECT=flext-core PYTEST_ARGS="-k <test_name> -x -q"
```

No `type: ignore`, no `object`, no `cast()`, no `Any`.
Use `# noqa` only for existing suppressions that survive the merge.
`from __future__ import annotations` on every file.
All imports must be used (Pyright `reportUnusedImport`).

---

## Summary

| Phase | Action | Files removed | Lines saved | Risk |
|-------|--------|--------------|-------------|------|
| 1 | Delete empty/stub | -21 | -1,460 | Zero |
| 2 | Delete coverage-% files | -4 | -1,025 | Low |
| 3 | Merge automated→primary | -13 | -1,200 | Medium |
| 4 | Consolidate clusters | -40 | -5,500 | High |
| 5 | Relocate misplaced | -7 | 0 | Low |
| **Total** | | **-85 files** | **~9,185 lines** | |

End state: ~69 unit test files, ~27,000 lines, same coverage.
