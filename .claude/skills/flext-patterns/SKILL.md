<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Pattern Catalog](#pattern-catalog)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---
name: flext-patterns
description: Repository-native implementation patterns for result flow, DI, logging, and typed boundaries. Use when selecting or standardizing implementation style.
---

# Flext Patterns

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope

- Canonical pattern anchors:
  - `flext-core/src/flext_core/result.py`
  - `flext-core/src/flext_core/container.py`
  - `flext-core/src/flext_core/loggings.py`
  - `flext-core/src/flext_core/settings.py`

## References
- `flext-core/docs/architecture/patterns.md`
- `flext-core/docs/guides/railway-oriented-programming.md`
- `flext-core/src/flext_core/runtime.py`

## Rules
- Prefer existing repository patterns over ad-hoc abstractions.
- Use `FlextResult` composition at error boundaries.
- Keep DI through `FlextContainer` bridge methods.
- Use structured logging via `FlextLogger` context APIs.

## Pattern Catalog

- ROP (`FlextResult` monadic chains)
- DI (`FlextContainer` singleton + scoped instances)
- DDD (entity/value/service models)
- CQRS (handler command/query separation)
- Event-Driven patterns in service/dispatcher flows
- Hexagonal ports/adapters boundaries
- Validation/middleware pipeline composition
- Factory/Adapter object-creation integration patterns

## Instructions
- Anchor new code to nearby proven implementations in same module family.
- For fallible operations use `ok/fail + map/flat_map/lash` chains.
- For context-aware logging use bind/scope patterns instead of manual dict payload assembly.
- Prefer `t.*` contracts for payload typing and `p.*` protocols for interfaces.
- Delete unreferenced operation wrappers when a canonical facade already implements the same behavior (do not keep duplicate module families alive).
- In domain packages, remove generic helper re-implementations when `flext-core` primitives already provide equivalent behavior.

```python
from flext_core import r

def transform(value: str):
    return r[str].ok(value).map(str.strip).flat_map(lambda v: r[str].ok(v.lower()))
```

## Workflow
1. Find closest existing pattern for the target behavior.
2. Reuse pattern with minimal adaptation.
3. Verify no anti-patterns (raw dict envelopes, direct external DI imports).
4. Confirm consistency with tests/type checks.

## Examples
Good:

```python
result = r[int].ok(10).map(lambda v: v * 2).lash(lambda err: r[int].ok(0))
```

Why good: preserves typed success/failure flow with explicit recovery.

Bad:

```python
try:
    value = fn()
    return {"ok": True, "value": value}
except Exception as exc:
    return {"ok": False, "error": str(exc)}
```

Why bad: custom envelope duplicates core result abstraction and weakens type safety.

Bad:

```python
from dependency_injector import providers

services = providers.DynamicContainer()
```

Why bad: imports infrastructure directly instead of using runtime/container bridge APIs.

Bad:

```python
logger = {"scope": "request"}
logger["user_id"] = user_id
```

Why bad: bypasses structured context APIs (`bind_global_context`, `scoped_context`) and loses standardized log behavior.

Bad:

```python
# duplicate operation wrappers that are never consumed
class DomainAPIOperationsA: ...
class DomainAPIOperationsB: ...
```

Why bad: multiplies maintenance surface and drifts from the canonical facade API.

Bad:

```python
# compatibility aliases that hide canonical call sites
LegacyAPI = NewDirectAPI
```

Why bad: keeps obsolete surfaces alive, delays full reference migration, and prevents true source reduction.

Bad:

```python
def do_work(...):
    return DomainFacade().do_work(...)
```

Why bad: free-function pass-through wrappers duplicate the class surface and inflate code without adding domain behavior.

Bad:

```python
SomeNamespace = CanonicalNamespace
```

Why bad: namespace aliases hide canonical access paths and spread non-essential compatibility names across the codebase.

## Verification

Make gates:

- `make check PROJECT=flext-core` — lint + type gates enforce pattern contracts
- `make test PROJECT=flext-core` — pattern usage exercised by test suite
- `make validate PROJECT=flext-core VALIDATE_GATES=complexity` — complexity gates

Pattern checks:

- `rg -n "\.map\(|\.flat_map\(|\.lash\(|\.recover\(" flext-core/src/flext_core/result.py`
- `rg -n "class FlextContainer|def register\(|def get_typed\(" flext-core/src/flext_core/container.py`
- `rg -n "class FlextLogger|bind_global_context|scoped_context" flext-core/src/flext_core/loggings.py`
- `rg -n "CQRS|Event-Driven|Hexagonal|Pipeline|Factory|Adapter|DDD" flext-core/docs/architecture/patterns.md`
