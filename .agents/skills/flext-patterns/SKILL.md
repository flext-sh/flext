---
name: flext-patterns
description: Repository-native implementation patterns for result flow, DI, logging, and typed boundaries. Use when selecting or standardizing implementation style.

---

# Flext Patterns

**Reviewed**: 2026-04-06 | **Scope**: Evidence-backed skill refresh and rule alignment

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
- `.agents/skills/flext-mro-namespace-rules/SKILL.md`

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
- **Hacks**: Canonical "Zero Hacks" rule in `AGENTS.md` §3.4.
- **Rule**: Compatibility wrappers (`def old(): return new()`), non-business validation fallbacks, legacy code maintenance of ANY kind, and `OldName = NewName` compatibility aliases are FORBIDDEN and forbidden. Legacy code is DELETED on contact and replaced with the canonical pattern. No grace period, no deprecation path, no "we'll remove it later".
- **Rule**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance. The most base class MUST inherit from Pydantic v2 `BaseModel` (or FLEXT base models). Loose functions, standalone classes without MRO lineage, and modules without nested class facades are FORBIDDEN.
- **Rule**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features. `u.Field()` with `description`/`title`/`examples` for ALL declarations. Minimize custom validators — prefer built-in constraints (`u.Field(ge=0)`, `StringConstraints()`, `Literal`). `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). FORBIDDEN in models: init helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, wrappers. USE: `@u.computed_field`, `model_post_init`, `u.PrivateAttr`. Enums/Literals from `c.*`, settings from `s.*`. Internal state via `u.PrivateAttr`. Nested classes MAY have business methods but ALL properties use `u.Field()`/`u.PrivateAttr`. `models.py`/`models/` for models ONLY. Result/status booleans use canonical names like `success` and `failure`. If not using a feature — REVIEW and USE it.
- **Rule**: Failure paths are DSL-first. Prefer `e.fail_*`, `r.fail_op`, `r.fail_exc`, and service-level DSL wrappers over ad-hoc `r.fail("...")` strings in runtime/application code. Use direct `r.fail(...)` only when implementing result primitives or when explicit passthrough payload semantics are required.
- **Rule**: Delete conversion layers, fallback branches, compatibility shims, and pass-through proxies before introducing any new abstraction. Prefer canonical `flext-core` and `flext-cli` contracts, JSON-capable types, settings, and DSL surfaces over local reinvention.

## Pattern Catalog

- **Pydantic Consumption via `m` Facade** — All Pydantic objects (m.BaseModel, u.Field, ConfigDict, validators) accessed via `m.*` in MRO-nested classes
- ROP (`r` monadic chains)
- DI (`FlextContainer` singleton + scoped instances via `c`, `p`)
- DDD (entity/value/service models via `m`)
- CQRS (handler command/query separation via `m.Commands`, `m.Queries`)
- Event-Driven patterns in service/dispatcher flows
- Hexagonal ports/adapters boundaries
- Validation/middleware pipeline composition
- Factory/Adapter t.JsonValue-creation integration patterns
- **Namespace Inheritance** (cross-project `m`, `c`, `t`, `u`, `p` composition via MRO)
- **Service Facade** (`api.py` MRO composition of `services/*.py` mixins — see §2.5 of AGENTS.md)

## Service Facade Pattern (`api.py` + `base.py` + `services/`)

> **Rule**: See `AGENTS.md` §2.5 for the canonical specification.

Projects providing a main service class use the **MRO service facade pattern**: one facade in `api.py` composing all service mixins from `services/`. A typed base class in `base.py` provides shared infrastructure (settings, logger, container).

```python
from __future__ import annotations

from typing import Annotated, override

from flext_core import m, p, r, s, t, u


class FlextObservabilityTracingMixin:
    """Tracing concern — one mixin per concern, composed via MRO."""

    @staticmethod
    def _build_trace(
        span_name: t.NonEmptyStr,
    ) -> "FlextObservability.Observability.TraceResult":
        """Trace construction stub for MRO composition."""
        return FlextObservability.Observability.TraceResult(
            trace_id="trace-1",
            span_name=span_name,
        )


class FlextObservabilityMetricsMixin:
    """Metrics concern — one mixin per concern, composed via MRO."""


class FlextObservabilityHealthMixin:
    """Health concern — one mixin per concern, composed via MRO."""


class FlextObservability(
    FlextObservabilityTracingMixin,
    FlextObservabilityMetricsMixin,
    FlextObservabilityHealthMixin,
    s[m.ArbitraryTypesModel],
):
    """Facade: single class per module, domain methods inherited via MRO."""

    span_name: Annotated[t.NonEmptyStr, u.Field(description="Initial span name")]

    class Observability:
        """Local domain namespace."""

        class TraceResult(m.ArbitraryTypesModel):
            """Trace result model — one model class per domain concept."""

            trace_id: Annotated[
                t.NonEmptyStr,
                u.Field(description="Distributed trace id"),
            ]
            span_name: Annotated[t.NonEmptyStr, u.Field(description="Span name")]

    @override
    def execute(self) -> p.Result[m.ArbitraryTypesModel]:
        """Domain execution composes mixins through MRO."""
        trace = self._build_trace(self.span_name)
        return r[m.ArbitraryTypesModel].ok(trace)
```

**Anti-patterns**:

```python
# FORBIDDEN — standalone service classes (not mixins, no MRO composition)
from __future__ import annotations


class FlextObservabilityMonitor:
    """Standalone class — not composable via MRO, bypasses facade."""

    def __init__(self) -> None:
        """Illustrates the anti-pattern."""
```

**Reference implementations**: `flext-cli`, `flext-ldif`, `flext-observability`.

## Simple Runtime Aliases Only (Mandatory)

**Never** use `u.Aliases.*()` to define package-level runtime aliases. Use **simple runtime aliases only**: direct assignment to the facade class (e.g. `c = FlextConstants`, `m = FlextModels`, `r = r`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = d`, `e = e`, `h = h`, `s = s`, `x = x`). No alias registry or staticmethod layer for defining these; MRO protocol only. Runtime helpers come from **x** (x) via MRO.

```python
# CORRECT
from __future__ import annotations


class FlextConstants:
    """Stub constants facade for illustration."""


class FlextModels:
    """Stub models facade for illustration."""


c = FlextConstants
m = FlextModels
```

```python
# FORBIDDEN — alias registry / staticmethod wrappers
from __future__ import annotations


class _AliasRegistry:
    """Illustrates the anti-pattern."""

    @staticmethod
    def constants() -> type:
        """Stub."""
        return type("FlextConstants", (), {})

    @staticmethod
    def models() -> type:
        """Stub."""
        return type("FlextModels", (), {})


c = _AliasRegistry.constants()
m = _AliasRegistry.models()
```

## Namespace Inheritance Pattern

> **Rule**: See `AGENTS.md` §2 Architecture Law and §4 Import Law for normative alias and MRO composition requirements.

Downstream projects inherit parent facade classes to compose namespaces. This avoids duplicate aliases, assignment-based type errors, and invariance issues.

### Project runtime alias only; MRO protocol (subprojects)

Access through the **project runtime alias only**, while preserving the organic nested path emitted by MRO. Use `m.TargetOracle.ExecuteResult`, `u.Infra.parse_semver`, and `c.Tests.ERR_OK_FAILED`. Do not add class-level aliases at the facade root to flatten domain-local symbols. **Simple runtime aliases only** in `__init__.py` (e.g. `c = FlextConstants`, `m = FlextModels`); never `u.Aliases` or any registry.

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, p, r, t, u


class FlextTargetOracleModels(m):
    """Consumer facade — inherits flext_core m via MRO, adds one namespace."""

    class TargetOracle:
        """One local domain namespace owned by the facade."""

        class ExecuteResult(m.ArbitraryTypesModel):
            """Domain-local model accessed as m.TargetOracle.ExecuteResult."""

            name: Annotated[t.NonEmptyStr, u.Field(description="Resource name")]


def build_result(
    name: t.NonEmptyStr,
) -> p.Result[FlextTargetOracleModels.TargetOracle.ExecuteResult]:
    """Runtime usage — access keeps the organic domain path."""
    return r[FlextTargetOracleModels.TargetOracle.ExecuteResult].ok(
        FlextTargetOracleModels.TargetOracle.ExecuteResult(name=name)
    )
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
from __future__ import annotations

from flext_core import m


def print_mro() -> None:
    """Inspect MRO chain of the runtime facade alias."""
    names = [cls.__name__ for cls in m.__mro__]
    print(names)
```

Anti-patterns:

- **Defining runtime aliases via `u.Aliases.*`** — forbidden. Use simple aliases only: `c = FlextConstants`, `m = FlextModels`, `r = r`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = d`, `e = e`, `h = h`, `s = s`, `x = x`. No separate alias registry or staticmethod layer for package **init**.
- **Flattening domain-local classes at the facade root** — forbidden. Keep `m.TargetOracle.ExecuteResult`, not `m.ExecuteResult`.
- **Manual wrapper nesting for private mixins** — forbidden. Compose `models/*` and `_utilities/*` mixins in the facade MRO instead of writing `class Docker(tk): ...`.
- `from flext_meltano import m` — duplicate alias surface
- `class Meltano: X = Parent.Meltano.X` — assignment not valid as type
- Inheriting `FlextModels` when parent namespaces are needed — loses `m.Meltano.*`

## MRO Integrity Rule (Zero Tolerance)

Runtime classes **MUST NOT** redeclare or change anything they receive via MRO.
If `FlextProjectConstants(FlextConstants)` already inherits `Platform` via MRO,
do NOT create a subclass of it anywhere in the child hierarchy.

```python
from __future__ import annotations

from typing import Final


class FlextConstants:
    """Stub base constants facade for illustration."""


# FORBIDDEN — redeclares Platform received via MRO
class FlextDbOracleConstantsBad(FlextConstants):
    """Bad: shadows a name already present on the parent chain."""

    class DbOracle:
        """Illustrates the anti-pattern of re-inheriting a parent class."""

        class Platform(FlextConstants):
            """WRONG — Platform should not re-inherit FlextConstants."""

            LOOPBACK_IP: Final[str] = "127.0.0.1"


# CORRECT — new namespace class, no MRO shadowing
class FlextDbOracleConstants(FlextConstants):
    """Good: plain local namespace owned by this facade."""

    class DbOracle:
        """Project-local namespace under the constants facade."""

        class Platform:
            """Plain class — independent namespace, no parent shadowing."""

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
from __future__ import annotations

from flext_core import r


def _to_lower(v: str) -> r[str]:
    return r[str].ok(v.lower())


def transform(value: str) -> r[str]:
    """Railway composition: ok → map → flat_map with typed result flow."""
    return r[str].ok(value).map(str.strip).flat_map(_to_lower)
```

## Workflow

1. Find closest existing pattern for the target behavior.
2. Reuse pattern with minimal adaptation.
3. Verify no anti-patterns (raw dict envelopes, direct external DI imports).
4. Confirm consistency with tests/type checks.

## Examples

### Good: Domain Model with MRO-nested Pydantic models via `m` facade

```python
from __future__ import annotations

from typing import Annotated, Self

from flext_core import c, m, p, r, t, u


class FlextOrderItem(m.ArbitraryTypesModel):
    """Order item model — one class per module via MRO composition."""

    sku: Annotated[t.NonEmptyStr, u.Field(description="Stock keeping unit")]
    quantity: Annotated[int, u.Field(default=1, ge=1, description="Unit count")]

    @u.field_validator("sku", mode="before")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        """Uppercase and strip the SKU before validation."""
        return value.upper().strip()


class FlextOrderCreateCommand(m.Command):
    """Create-order command — inherits m.Command flat namespace via MRO."""

    model_config = m.ConfigDict(extra="forbid")

    customer_id: Annotated[t.NonEmptyStr, u.Field(description="Customer id")]
    items: Annotated[
        list[FlextOrderItem],
        u.Field(description="Items to purchase", min_length=1),
    ]

    @u.model_validator(mode="after")
    def validate_order(self) -> Self:
        """Ensure the order contains at least one item."""
        if not self.items:
            msg = "Order must have at least one item"
            raise ValueError(msg)
        return self


def build_order() -> p.Result[FlextOrderCreateCommand]:
    """Construct a well-formed order via railway-oriented result flow."""
    cmd = FlextOrderCreateCommand(
        customer_id="cust_123",
        items=[FlextOrderItem(sku="WIDGET", quantity=5)],
    )
    return r[FlextOrderCreateCommand].ok(cmd)
```

### Good: ROP with typed result flow

```python
from __future__ import annotations

from flext_core import r


def _recover(_err: str) -> r[int]:
    return r[int].ok(0)


def compute() -> r[int]:
    """Preserves typed success/failure flow with explicit recovery."""
    return r[int].ok(10).map(lambda v: v * 2).lash(_recover)
```

Why good: preserves typed success/failure flow with explicit recovery.

**FORBIDDEN**: Custom `dict[str, Any]` result envelopes. Use `r[T]` result flow with `r.ok()` / `r.fail()`. Custom envelopes duplicate the core result abstraction and weaken type safety.

Bad:

```python
from __future__ import annotations


class _FakeProvidersModule:
    """Stub illustrating the DI bypass anti-pattern."""

    class DynamicContainer:
        """Stub container."""


providers = _FakeProvidersModule()
services = providers.DynamicContainer()
```

Why bad: imports infrastructure directly instead of using runtime/container bridge APIs.

Bad:

```python
from __future__ import annotations


def bad_context_logger(user_id: str) -> dict[str, str]:
    """Manual dict payload instead of structured logging context."""
    logger: dict[str, str] = {"scope": "request"}
    logger["user_id"] = user_id
    return logger
```

Why bad: bypasses structured context APIs (`bind_global_context`, `scoped_context`) and loses standardized log behavior.

Bad:

```python
from __future__ import annotations


class DomainAPIOperationsA:
    """Duplicate operation wrapper never consumed by the facade."""


class DomainAPIOperationsB:
    """Duplicate operation wrapper never consumed by the facade."""
```

Why bad: multiplies maintenance surface and drifts from the canonical facade API.

Bad:

```python
from __future__ import annotations


class NewDirectAPI:
    """Canonical API."""


# Compatibility alias that hides the canonical call site
LegacyAPI = NewDirectAPI
```

Why bad: keeps obsolete surfaces alive, delays full reference migration, and prevents true source reduction.

Bad:

```python
from __future__ import annotations


class DomainFacade:
    """Canonical facade."""

    def do_work(self, payload: str) -> str:
        """Do the real work."""
        return payload.upper()


def do_work(payload: str) -> str:
    """Pass-through wrapper duplicating the facade surface."""
    return DomainFacade().do_work(payload)
```

Why bad: free-function pass-through wrappers duplicate the class surface and inflate code without adding domain behavior.

Bad:

```python
from __future__ import annotations


class CanonicalNamespace:
    """Canonical namespace."""


# Namespace alias hides the canonical access path
SomeNamespace = CanonicalNamespace
```

Why bad: namespace aliases hide canonical access paths and spread non-essential compatibility names across the codebase.

Bad:

```python
from __future__ import annotations

from enum import Enum


class Status(Enum):
    """Canonical status enum."""

    ACTIVE = "active"


# Duplicate alias multiplies symbols and forces compatibility maintenance
STATUS_ACTIVE = Status.ACTIVE
```

Why bad: duplicated alias constants multiply symbols and force broad compatibility maintenance; prefer direct enum member usage at call sites.

## Verification

Make gates:

- `make check PROJECT=flext-core` — lint + type gates enforce pattern contracts
- `make test PROJECT=flext-core` — pattern usage exercised by test suite
- `make val PROJECT=flext-core VALIDATE_GATES=complexity` — complexity gates

Pattern checks:

- `rg -n "\.map\(|\.flat_map\(|\.lash\(|\.recover\(" flext-core/src/flext_core/result.py`
- `rg -n "class FlextContainer|def register\(|def get_typed\(" flext-core/src/flext_core/container.py`
- `rg -n "class FlextLogger|bind_global_context|scoped_context" flext-core/src/flext_core/loggings.py`
- `rg -n "CQRS|Event-Driven|Hexagonal|Pipeline|Factory|Adapter|DDD" flext-core/docs/architecture/patterns.md`
