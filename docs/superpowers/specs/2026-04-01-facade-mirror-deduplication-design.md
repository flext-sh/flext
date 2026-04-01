# Facade Mirror Deduplication via Re-Export Pattern

**Date:** 2026-04-01
**Status:** Approved
**Scope:** 17 identical file pairs across 3 projects (~4,839 LOC)

## Problem

Public facade files are verbatim copies of their `_utilities/` counterparts.
The canonical pattern (flext-core) keeps implementation in `_utilities/` and
re-exports from the public module. These 17 pairs violate that pattern.

## Target Pairs

### flext-observability (14 pairs, ~4,480 LOC)

| Public file | Internal source |
|-------------|-----------------|
| `core.py` | `_utilities/_core.py` |
| `http_client_instrumentation.py` | `_utilities/_http_client_instrumentation.py` |
| `http_instrumentation.py` | `_utilities/_http_instrumentation.py` |
| `monitoring.py` | `_utilities/_monitoring.py` |
| `context.py` | `_utilities/_context.py` |
| `custom_metrics.py` | `_utilities/_custom_metrics.py` |
| `error_handling.py` | `_utilities/_error_handling.py` |
| `sampling.py` | `_utilities/_sampling.py` |
| `advanced_context.py` | `_utilities/_advanced_context.py` |
| `logging_integration.py` | `_utilities/_logging_integration.py` |
| `performance.py` | `_utilities/_performance.py` |
| `fields.py` | `_utilities/_fields.py` |
| `services.py` | `_utilities/_services.py` |
| `health.py` | `_utilities/_health.py` |

### flext-dbt-oracle-wms (1 pair, ~205 LOC)

| Public file | Internal source |
|-------------|-----------------|
| `client.py` | `_utilities/client.py` |

### flext-dbt-oracle (2 pairs, ~154 LOC)

| Public file | Internal source |
|-------------|-----------------|
| `simple_api.py` | `_utilities/simple_api.py` |
| `connections.py` | `_utilities/connections.py` |

## Re-Export Pattern

Each public file is replaced with a thin re-export stub:

```python
"""Re-export from internal module."""
from <package>._utilities.<module> import <Symbol1>, <Symbol2>

__all__ = ["Symbol1", "Symbol2"]
```

Implementation stays in `_utilities/` (source of truth).

## Execution Plan

### Wave 1: flext-observability (14 files)

For each pair:
1. Read `_utilities/_*.py` to identify exported symbols (classes, functions, constants)
2. Replace public file with re-export stub
3. Verify: `ruff check src/`, `pyrefly check src/`, `pyright src/`

### Wave 2: flext-dbt-oracle-wms + flext-dbt-oracle (3 files)

Same pattern, smaller scope.

### Wave 3: Validation

1. Run `pytest tests/` on each project
2. Run workspace-level `ruff check`
3. Verify no external imports broke via `scope callers`

### Wave 4: Governance

1. Add facade mirror prohibition rule to AGENTS.md
2. Update `flext-strict-refactoring` skill with re-export pattern
3. Create rope recipe `u.Infra.collapse_facade_mirror()` for future use

## Success Criteria

- Zero identical-code findings for facade mirrors in `qlty smells`
- All linters pass (ruff, pyrefly, pyright)
- All tests pass
- AGENTS.md updated with explicit rule
