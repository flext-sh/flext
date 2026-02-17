---
name: rules-flext-core
description: Authoritative rules for `flext-core` architecture, typing, result flow, DI, and logging boundaries. Use when modifying files under `flext-core/`.
---

# Rules Flext Core

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope
- `flext-core/src/flext_core/`
- `flext-core/docs/architecture/`
- `flext-core/pyproject.toml`

## References
- `flext-core/docs/architecture/overview.md`
- `flext-core/docs/architecture/clean-architecture.md`
- `flext-core/src/flext_core/result.py`
- `flext-core/src/flext_core/container.py`
- `flext-core/src/flext_core/runtime.py`
- `flext-core/src/flext_core/typings.py`
- `flext-core/src/flext_core/loggings.py`

## Rules
- Keep dependency direction inward only (L3 -> L2 -> L1 -> L0).
- Keep failure/success boundaries on `FlextResult` (`r`) and compose with `map/flat_map/lash`.
- Keep dependency-injector usage routed through runtime/container bridges.
- Keep shared type contracts centralized in `typings.py`.
- Consume public API from `flext_core` exports in non-internal modules.

## Instructions
- Reuse canonical aliases where established: `r`, `t`, `c`, `m`, `p`, `u`.
- Anchor behavior changes to concrete declarations before refactoring.
- For new exported symbols, update `flext-core/src/flext_core/__init__.py` deliberately.

```python
from flext_core import r

def run(value: str):
    return r[str].ok(value).map(str.strip)
```

## Workflow
1. Classify touched files by architecture layer.
2. Apply minimal change aligned with local pattern.
3. Verify imports/exports and boundary integrity.
4. Run lint/type/test checks for `flext-core`.

## Examples
Good:

```python
result = r[str].ok("x").flat_map(lambda v: r[str].ok(v.upper()))
```

Why good: typed railway composition with explicit success chain.

Bad:

```python
from dependency_injector import providers
```

Why bad: bypasses `FlextRuntime`/`FlextContainer` bridge contract.

## Verification
- `rg -n "class FlextResult|\.flat_map\(|\.lash\(" flext-core/src/flext_core/result.py`
- `rg -n "class FlextContainer|def register\(|def get_typed\(" flext-core/src/flext_core/container.py`
- `rg -n "class FlextRuntime|class DependencyIntegration" flext-core/src/flext_core/runtime.py`
- `rg -n "TypeVar\(|TypeAlias|class FlextTypes" flext-core/src/flext_core/typings.py`
