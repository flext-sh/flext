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

## Zero Tolerance for "Hacks" (Mandatory — No Exception)

All forms of dynamic evaluation, runtime patching, and hidden imports are strictly prohibited:

1. **`model_rebuild()`** — PROHIBITED. Fix the graph or use Protocols.
2. **Inline/Lazy Imports** — PROHIBITED. Imports must be top-level.
3. **`try-except ImportError`** — PROHIBITED for dependency bridging.
4. **`cast()`** — PROHIBITED in production code (except core `result.py`).
5. **`eval()` / `exec()`** — PROHIBITED.
6. **`getattr()` / `setattr()` / `globals()` / `locals()`** — PROHIBITED for architecture or dynamic logic.

## Rules

> **Rule**: See `AGENTS.md` §2 Architecture Law and §4 Import Law for canonical namespace alias and inheritance requirements.

- This skill focuses on implementation-level patterns, anti-patterns, and concrete examples.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.
- **AXIOMATIC**: Compatibility wrappers (`def old(): return new()`), non-business validation fallbacks, legacy code maintenance of ANY kind, and `OldName = NewName` compatibility aliases are TOTALLY FORBIDDEN and ABOMINABLE. Legacy code is DELETED on contact and replaced with the canonical pattern. No grace period, no deprecation path, no "we'll remove it later".
- **AXIOMATIC**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance. The most base class MUST inherit from Pydantic v2 `BaseModel` (or FLEXT base models). Loose functions, standalone classes without MRO lineage, and modules without nested class facades are FORBIDDEN.
- **AXIOMATIC**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features. `Field()` with `description`/`title`/`examples` for ALL declarations. Minimize custom validators — prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`). `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). FORBIDDEN in models: init helpers, unnecessary `@property`, simple getters/setters, wrappers. USE: `@computed_field`, `model_post_init`, `PrivateAttr`. Enums/Literals from `c.*`, config from `s.*`. Internal state via `PrivateAttr`. Nested classes MAY have business methods but ALL properties use `Field()`/`PrivateAttr`. `models.py`/`_models/` for models ONLY. If not using a feature — REVIEW and USE it.

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

## Simple Runtime Aliases Only (Mandatory)

**Never** use `FlextRuntime.Aliases.*()` to define package-level runtime aliases. Use **simple runtime aliases only**: direct assignment to the facade class (e.g. `c = FlextConstants`, `m = FlextModels`, `r = FlextResult`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = FlextDecorators`, `e = FlextExceptions`, `h = FlextHandlers`, `s = FlextService`, `x = FlextMixins`). No alias registry or staticmethod layer for defining these; MRO protocol only. Runtime helpers come from **x** (FlextMixins) via MRO.

```python
# ✅ CORRECT
c = FlextConstants
m = FlextModels
x = FlextMixins
```

```python
# ❌ FORBIDDEN
c = FlextRuntime.Aliases.constants()
m = FlextRuntime.Aliases.models()
```

## Namespace Inheritance Pattern

> **Rule**: See `AGENTS.md` §2 Architecture Law and §4 Import Law for normative alias and MRO composition requirements.

Downstream projects inherit parent facade classes to compose namespaces. This avoids duplicate aliases, assignment-based type errors, and invariance issues.

### Project runtime alias only; MRO protocol (subprojects)

Access through **project runtime alias only**; no subdivision. Subprojects: nested classes for organization, then **class-level aliases at facade root** so call sites use `m.Foo`, `m.Bar` only (never `m.ProjectName.Foo` or `m.TargetOracle.Foo`). **Simple runtime aliases only** in **init** (e.g. `c = FlextConstants`, `m = FlextModels`); never FlextRuntime.Aliases or any registry. MRO protocol only; direct methods.

```python
# models.py — inherit parent, define nested namespace, then alias at root
from flext_meltano import FlextMeltanoModels

class FlextTargetOracleModels(FlextMeltanoModels, FlextDbOracleModels):
    class TargetOracle:
        class ExecuteResult(FlextMeltanoModels.ArbitraryTypesModel):
            name: str

    # Class-level alias at root: flat namespace (m.ExecuteResult, not m.TargetOracle.ExecuteResult)
    ExecuteResult = TargetOracle.ExecuteResult

m = FlextTargetOracleModels
```

```python
# Runtime usage — only runtime alias m; access is flat
from .models import m
from flext_core import r

schema = m.Meltano.SingerSchemaMessage.model_validate(data)
result = r[m.ExecuteResult].ok(m.ExecuteResult(name="x"))
```

## .new/Swap Protocol for Large Modifications

For large modifications to existing models or protocols, use the `.new` file pattern:

1. Create a `.new` file with the modified version
2. Verify the new version works correctly
3. Swap the `.new` file with the original
4. Delete the backup

This prevents partial modifications and ensures atomic updates.

## MRO Verification

Verify inheritance chain with: `[c.__name__ for c in cls.__mro__]`

Example:

```python
from .models import m
print([c.__name__ for c in m.__mro__])
# Output: ['FlextTargetOracleModels', 'FlextMeltanoModels', 'FlextDbOracleModels', 'FlextModels', 'object']
```

Anti-patterns:

- **Defining runtime aliases via `FlextRuntime.Aliases.*`** — forbidden. Use simple aliases only: `c = FlextConstants`, `m = FlextModels`, `r = FlextResult`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = FlextDecorators`, `e = FlextExceptions`, `h = FlextHandlers`, `s = FlextService`, `x = FlextMixins`. No separate alias registry or staticmethod layer for package **init**.
- Prefer `m.ExecuteResult` when a class-level alias exists; `m.TargetOracle.Foo` is allowed in subprojects
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
