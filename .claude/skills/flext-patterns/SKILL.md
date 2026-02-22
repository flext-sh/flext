<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Pattern Catalog](#pattern-catalog)
- [Namespace Inheritance Pattern](#namespace-inheritance-pattern)
- [MRO Integrity Rule (Zero Tolerance)](#mro-integrity-rule-zero-tolerance)
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

> **Rule**: See `CLAUDE.md` §2 Architecture Law and §4 Import Law for canonical namespace alias and inheritance requirements.

- This skill focuses on implementation-level patterns, anti-patterns, and concrete examples.

## Pattern Catalog

- ROP (`FlextResult` monadic chains)
- DI (`FlextContainer` singleton + scoped instances)
- DDD (entity/value/service models)
- CQRS (handler command/query separation)
- Event-Driven patterns in service/dispatcher flows
- Hexagonal ports/adapters boundaries
- Validation/middleware pipeline composition
- Factory/Adapter object-creation integration patterns
- **Namespace Inheritance** (cross-project `m`, `c`, `t`, `u`, `p` composition via MRO)

## Namespace Inheritance Pattern

> **Rule**: See `CLAUDE.md` §2 Architecture Law and §4 Import Law for normative alias and MRO composition requirements.

Downstream projects inherit parent facade classes to compose namespaces. This avoids duplicate aliases, assignment-based type errors, and invariance issues.

```python
# models.py — inherit parent, define local domain namespace
from flext_meltano import FlextMeltanoModels

class FlextTargetOracleModels(FlextMeltanoModels):
    class TargetOracle:
        class ExecuteResult(FlextMeltanoModels.ArbitraryTypesModel):
            name: str

m = FlextTargetOracleModels
# m.Meltano.*       → from FlextMeltanoModels via MRO
# m.TargetOracle.*  → local domain
```

```python
# Runtime usage — only import m
from .models import m
from flext_core import r

schema = m.Meltano.SingerSchemaMessage.model_validate(data)
result = r[m.TargetOracle.ExecuteResult].ok(m.TargetOracle.ExecuteResult(name="x"))
```

Anti-patterns:
- `from flext_meltano import FlextMeltanoModels as m_meltano` — duplicate alias surface
- `class Meltano: X = Parent.Meltano.X` — assignment not valid as type
- Inheriting `FlextModels` when parent namespaces are needed — loses `m.Meltano.*`

## MRO Integrity Rule (Zero Tolerance)

Runtime classes **MUST NOT** redeclare or change anything they receive via MRO.
If `FlextProjectConstants(FlextConstants)` already inherits `Platform` via MRO,
do NOT create a subclass of it anywhere in the child hierarchy.

```python
# ❌ FORBIDDEN — redeclares Platform received via MRO
class FlextDbOracleConstants(FlextConstants):
    class DbOracle:
        class Platform(FlextConstants.Platform):  # WRONG!
            LOOPBACK_IP: Final[str] = "127.0.0.1"

# ✅ CORRECT — new namespace class, no MRO shadowing
class FlextDbOracleConstants(FlextConstants):
    class DbOracle:
        class Platform:  # plain class, independent namespace
            LOOPBACK_IP: Final[str] = "127.0.0.1"
```

This applies to ALL facade hierarchies (`c`, `m`, `p`, `u`, `t`).
The child class already has every parent inner class via MRO — re-inheriting
from them creates confusing duplicates and breaks type identity.

## Instructions
- Anchor new code to nearby proven implementations in same module family.
- For fallible operations use `ok/fail + map/flat_map/lash` chains.
- For context-aware logging use bind/scope patterns instead of manual dict payload assembly.
- Prefer `t.*` contracts for payload typing and `p.*` protocols for interfaces.
- Delete unreferenced operation wrappers when a canonical facade already implements the same behavior (do not keep duplicate module families alive).
- In domain packages, remove generic helper re-implementations when `flext-core` primitives already provide equivalent behavior.
- For protocol payloads (Singer/CLI/API), prefer canonical Pydantic message models over repeated ad-hoc dict key/type checks in handlers.

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

Bad:

```python
STATUS_ACTIVE = Status.ACTIVE
```

Why bad: duplicated alias constants multiply symbols and force broad compatibility maintenance; prefer direct enum member usage at call sites.

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
