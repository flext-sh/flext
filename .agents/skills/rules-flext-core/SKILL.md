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

- `AGENTS.md` — canonical governance source
- `flext-core/docs/architecture/overview.md`
- `flext-core/docs/architecture/clean-architecture.md`
- `flext-core/src/flext_core/result.py`
- `flext-core/src/flext_core/container.py`
- `flext-core/src/flext_core/runtime.py`
- `flext-core/src/flext_core/typings.py`
- `flext-core/src/flext_core/loggings.py`

## Rules

- Keep dependency direction inward only (L3 -> L2 -> L1 -> L0).
- Keep failure/success boundaries on `r` (`r`) and compose with `map/flat_map/lash`.
- Keep dependency-injector usage routed through runtime/container bridges.
- Keep shared type contracts centralized in `typings.py`. **Rule**: `Any`, `object`, and `Mapping[str, Any]` are FORBIDDEN — use `t.*` contracts exclusively. `None` in type unions only when business-required.
- Keep public `get_*`/`set_*`/`is_*` surfaces out of `flext-core`; deterministic values belong in fields or `@u.computed_field`, and result/status carriers use `success`/`failure`.
- Consume public API from `flext_core` exports in non-internal modules.
- For `flext-core/tests/`, assert module and facade behavior, not implementation details. Tests coupled to internal warning text, traceback fragments, local alias names, internal class names, or private MRO structure are invalid and must be rewritten to target stable external behavior.
- **Rule — Library Abstraction Responsibility**: flext-core is the ONLY project that may import and use `pydantic`, `dependency_injector`, `structlog`, `returns`, `orjson`, `pyyaml` directly. All consuming projects (`flext-cli`, `flext-ldap`, integration projects, etc.) MUST access these through flext-core's public abstractions (`m.*`, `c.*`, `p.*`, `t.*`, `u.*`). This boundary is inviolable and enforced via grep audits and linting rules.

## Instructions

- Reuse canonical aliases where established: `r`, `t`, `c`, `m`, `p`, `u`.
- Anchor behavior changes to concrete declarations before refactoring.
- For new exported symbols, update `flext-core/src/flext_core/__init__.py` deliberately.

```python
from __future__ import annotations

from flext_core import r


def run(value: str) -> object:
    return r[str].ok(value).map(str.strip)
```

## Workflow

1. Classify touched files by architecture layer.
2. Apply minimal change aligned with local pattern.
3. Verify imports/exports and boundary integrity.
4. Run lint/type/test checks for `flext-core`.

## Examples

Good (Result Railway):

```python
from __future__ import annotations

from flext_core import r


def _to_upper(v: str) -> p.Result[str]:
    return r[str].ok(v.upper())


result = r[str].ok("x").flat_map(_to_upper)
```

Why good: typed railway composition with explicit success chain.

Good (Library Abstraction Provider):

```python
from __future__ import annotations

from flext_core import c, m


class Settings(m.BaseModel):
    """Base settings class - abstracts pydantic for all consumers."""

    model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="ignore")


# In FlextCoreModels' __exports__
# m = FlextCoreModels  # Users import this facade, not BaseModel
```

Why good: flext-core owns pydantic integration; all other projects access through `m.Settings` alias.

Bad (Bypassing Container):

```python
from __future__ import annotations

# ❌ NEVER — bypasses u/FlextContainer bridge contract
# from dependency_injector import providers
_EXAMPLE_ONLY: str = "use u.Container instead of dependency_injector directly"
```

Why bad: bypasses `u`/`FlextContainer` bridge contract.

Bad (Library Abstraction Violation - if this were in flext-cli):

```python
from __future__ import annotations

# ❌ NEVER in flext-cli/src or other consuming projects
# from pydantic import BaseModel, u.Field
# from dependency_injector import containers
_EXAMPLE_ONLY: str = "use m.BaseModel and u.Container instead"
```

Why bad: consuming projects must use flext-core abstractions (`m.Settings`, `u.Container`) instead of direct library imports. Violates boundary and makes pydantic upgrade harder.

## Verification

Make gates (run after any flext-core change):

- `make check PROJECT=flext-core` — lint + format + type + security
- `make check PROJECT=flext-core CHECK_GATES=type` — type-check only
- `make val PROJECT=flext-core` — complexity + docstring gates
- `make test PROJECT=flext-core` — full test suite

Pattern checks:

- `rg -n "class r|\.flat_map\(|\.lash\(" flext-core/src/flext_core/result.py`
- `rg -n "class FlextContainer|def register\(|def get_typed\(" flext-core/src/flext_core/container.py`
- `rg -n "class u|class DependencyIntegration" flext-core/src/flext_core/runtime.py`
- `rg -n "TypeVar\(|TypeAlias|class FlextTypes" flext-core/src/flext_core/typings.py`
