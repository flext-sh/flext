---
name: pydantic-v2-patterns
description: Advanced Pydantic v2 implementation patterns for FLEXT — TypeAdapter caching, RootModel vs BaseModel, Annotated validators, discriminated unions, computed_field, PrivateAttr, facade-only imports. Use when implementing complex model hierarchies, chaining validators, resolving v1-to-v2 migration errors, or writing FLEXT-compliant models.
---

# Pydantic v2 Patterns

**Reviewed**: 2026-04-20 | **Scope**: Implementation depth that complements `pydantic-v2-governance` and `lib-pydantic-v2` — TypeAdapter caching, RootModel vs BaseModel, Annotated validators, discriminated unions, facade-only imports

## Scope

- Advanced Pydantic v2 usage across FLEXT 34-project workspace (`src/`, `tests/`, `examples/`).
- Pattern families: validators, computed fields, discriminated unions, serializers, strict mode, TypeAdapter caching, RootModel containers, Annotated rule composition, facade-only imports.
- Companion skill: `pydantic-v2-governance` (HARD rules checklist + forbidden structures). This skill covers HOW; governance covers WHAT MUST NOT happen.

## References

- `AGENTS.md` — §3 Code Law
- `.agents/skills/pydantic-v2-governance/SKILL.md` — Model HARD Rules checklist + Forbidden structures
- `.agents/skills/lib-pydantic-v2/SKILL.md` — Pydantic v2 API policy (complementary)
- `.agents/skills/flext-constants-discipline/SKILL.md` — `c.*` constants primitives
- `.agents/skills/flext-type-system/SKILL.md` — `p.*`/`t.*`/`m.*` ownership
- Code anchors (read before implementing):
  - `flext-core/src/flext_core/_typings/typeadapters.py` — canonical TypeAdapter registry
  - `flext-core/src/flext_core/models/containers.py` — canonical RootModel (`ConfigMap`)
  - `flext-core/src/flext_core/models/domain_event.py` — canonical `Annotated[..., BeforeValidator]`
  - `flext-core/src/flext_core/models/settings.py`
  - `flext-core/src/flext_core/_utilities/pydantic.py` — internal `FlextUtilitiesPydantic` (alias `up`, used only inside flext-core to break c/t/p/m/u cycles)
  - `flext-core/src/flext_core/models/pydantic.py` — internal `FlextModelsPydantic` (alias `mp`, same role)

## Rules

- **Alias-first consumption (consumers)**: every Pydantic construct is accessed through `m.*` / `u.*` from `flext_core` (or the project's MRO-extended package). Never mix direct `pydantic` imports in consumers. The `up` / `mp` aliases are reserved for INTERNAL flext-core modules that would otherwise cycle on `c/t/p/m/u` during bootstrap — do not use them outside `flext-core/src/flext_core/_*`.
- **Every model extends a FLEXT base via MRO** (`m.BaseModel`, `m.Value`, `m.ArbitraryTypesModel`, `m.FrozenModel`). Loose classes without MRO lineage are forbidden.
- **Validator phases are explicit**:
  - `u.field_validator(..., mode="before")` for normalization/coercion.
  - `u.field_validator(..., mode="after")` for typed semantic checks bound to the field.
  - `u.model_validator(mode="after")` for cross-field invariants (returns `Self`).
  - `Annotated[T, m.BeforeValidator(fn)]` / `m.AfterValidator(fn)` preferred over decorator when the rule is reusable across fields.
- **Computed fields pure and deterministic** — `@u.computed_field` replaces every `@property` on a model.
- **Serializers explicit and scope-limited** — no hidden state.
- **Strict mode for boundaries**: `model_config = m.ConfigDict(strict=True, frozen=True)` for public contracts and settings.
- **Discriminated unions** via `Annotated[A | B | C, m.Discriminator("kind")]` with `Literal[...]` tags — no isinstance ladders.
- **No helpers on models**: only fields + `Annotated` validators + `@computed_field` + `@model_validator`. Domain operations live in `u.*`.
- **Error messages stable** — tests and operators depend on them.
- **Legacy code is DELETED on contact**. No compatibility wrappers, no fallbacks, no v1 aliases.

### TypeAdapter Caching (canonical)

- **Single registry**: every `TypeAdapter[T]` lives on `FlextTypesTypeAdapters` in `flext-core/src/flext_core/_typings/typeadapters.py`. Never inline `m.TypeAdapter(T)` at a call site.
- **Pattern**: `ClassVar[m.TypeAdapter[T] | None] = None` slot + `@classmethod` factory that lazy-builds on first call (see `json_value_adapter`, `flat_container_mapping_adapter`, etc.).
- **Exposure**: consumers receive the adapter re-exported as `Final[m.TypeAdapter[T]]` through their owning `t.*` facade (e.g. `t.Cli.JSON_VALUE_ADAPTER`).
- **No subclassing**: `FlextTypesTypeAdapters` is closed. Add the new slot + factory there.
- **Verification**: `rg -n "TypeAdapter\(" --type py --glob '!flext-core/src/flext_core/_typings/typeadapters.py' --glob '!**/.venv/**'` → expect zero hits outside the canonical registry + per-consumer facade typings module.

### RootModel vs BaseModel Decision

- **RootModel[T]** wraps exactly one value (mapping, sequence, scalar union, discriminated union). The model IS the value.
- **BaseModel** covers two or more structured fields. Never force multiple concepts into a RootModel via `.root[0]`, `.root[1]` indexing.
- **Name the concept** (`m.ConfigMap`, `m.MetricSet`, `m.EventLog`) — never the shape (`m.DictStrContainer`).
- **Raw `type X = dict[str, Y]` / `type X = list[Y]` aliases are FORBIDDEN** when the shape appears in any Pydantic field annotation — wrap in `RootModel`.
- **Access** via `.root` at I/O boundaries; never add `.to_dict()` helpers.

### Annotated Validators — where to attach rules

- **Reusable / single-field**: attach at the annotation via `Annotated[T, m.BeforeValidator(u.normalize_x)]` or `m.AfterValidator(...)`. Callable MUST live in `flext-core/_utilities/*` under a named function (never inline lambda).
- **Cross-field / instance-bound**: `@u.model_validator(mode="after")` returning `Self`.
- **Single-field but complex, non-reusable**: `@u.field_validator` escape hatch when `Annotated[...]` genuinely does not fit.
- Always `validate_default=True` on fields whose default flows through a normalizer.

### Facade-Only Imports (banned vs required)

| BANNED | REQUIRED (consumer) |
| --- | --- |
| `import pydantic` | `from flext_core import c, m, p, t, u` (+ `r` / `s` as needed) |
| `from pydantic import Field, BaseModel, ...` | access via `m.Field`, `m.BaseModel`, `m.ConfigDict`, `u.computed_field`, `u.field_validator`, `u.model_validator`, `u.PrivateAttr`, `m.BeforeValidator`, `m.AfterValidator`, `m.Discriminator`, `m.Tag`, `m.SecretStr`, `m.TypeAdapter`, `m.ValidationError` |
| `from pydantic_core import ...` | same — via `m.*` / `u.*` |
| `from pydantic.dataclasses import dataclass` | `class X(m.BaseModel): model_config = m.ConfigDict(frozen=True)` |

Internal flext-core escape (ONLY inside `flext-core/src/flext_core/_*`): `from flext_core import  FlextUtilitiesPydantic as up` / `from flext_core import  FlextModelsPydantic as mp`. This is NOT a consumer pattern — it exists solely to break initialization cycles in `c/t/p/m/u`.

If a facade symbol is missing, ADD it to `flext-core/_utilities/pydantic.py` / `models/pydantic.py` FIRST (with tests), re-export through the right facade (`m.*` or `u.*`), THEN consume downstream via the canonical alias.

Verification: `rg -n "^(import pydantic|from pydantic|from pydantic_core)" --type py --glob '!flext-core/src/flext_core/models/pydantic.py' --glob '!flext-core/src/flext_core/_utilities/pydantic.py' --glob '!flext-core/src/flext_core/_typings/typeadapters.py' --glob '!**/.venv/**'` → zero hits.

## Instructions

> Full reference patterns live in `references/patterns-detail.md` when loaded. The sections above cover the mandatory rules.

Pattern families available in references:

- **Validators**: `@u.field_validator`, `@u.model_validator`, reusable `Annotated` aliases with constraints.
- **Computed fields**: `@u.computed_field` with `cached_property` semantics and FLEXT examples.
- **Discriminated unions**: `m.Discriminator(...)` with `Literal[...]` tags for polymorphic parsing.
- **Serializers**: `@u.field_serializer`, `@u.model_serializer`, `model_dump()` control.
- **Strict mode**: `model_config = m.ConfigDict(strict=True)` patterns.
- **TypeAdapter**: caching strategy, `ClassVar[m.TypeAdapter[T] | None]` slot + classmethod factory.

## Workflow

1. Read `pydantic-v2-governance` HARD Rules Checklist and Forbidden Structures.
2. Read `lib-pydantic-v2` for API policy deltas.
3. Select the needed pattern family (validators, computed fields, unions, serializers, strict mode, TypeAdapter, RootModel, Annotated).
4. Locate nearest repository anchor (Scope section) and copy the structure.
5. Adapt names/types while preserving validation phase semantics.
6. Add focused tests for parse failures, invariant failures, computed outputs, serializer output.
7. Run verification greps (see each rule block) to ensure no drift.

## Examples

### Good — facade-only validators and computed fields

```python
from __future__ import annotations

from typing import Annotated, Self

from flext_core import m, p, r, t, u


class FlextExampleModels(m):
    """Consumer model facade — nested domain namespace via MRO."""

    class Example:
        class Window(m.Value):
            """Window with separated validation phases."""

            model_config = m.ConfigDict(frozen=True, strict=True, extra="forbid")

            start: Annotated[
                t.NonNegativeInt, m.Field(default=0, validate_default=True)
            ]
            end: Annotated[t.NonNegativeInt, m.Field(default=0, validate_default=True)]
            label: Annotated[
                t.NonEmptyStr,
                m.BeforeValidator(u.normalize_label),
                m.Field(description="Window label"),
            ]

            @u.model_validator(mode="after")
            def validate_window(self) -> Self:
                if self.end < self.start:
                    msg = "end must be >= start"
                    raise ValueError(msg)
                return self


def demo_window() -> p.Result[int]:
    w = FlextExampleModels.Example.Window(start=1, end=4, label="ok")
    return r[int].ok(w.end - w.start)
```

Why good: facade-only imports, MRO-nested domain, `Annotated` for reusable normalization, `model_validator(after)` for cross-field invariant, frozen + strict contract, no helpers on the model.

### Good — discriminated union via facade

```python
from __future__ import annotations

from typing import Annotated, Literal

from flext_core import m


class FlextExampleModels(m):
    class Example:
        class Ok(m.Value):
            model_config = m.ConfigDict(frozen=True, strict=True)
            kind: Annotated[Literal["ok"], m.Field(frozen=True)] = "ok"
            value: Annotated[int, m.Field(description="Payload value")]

        class Err(m.Value):
            model_config = m.ConfigDict(frozen=True, strict=True)
            kind: Annotated[Literal["err"], m.Field(frozen=True)] = "err"
            error: Annotated[str, m.Field(description="Failure reason")]

        # Bare sibling names are valid inside the nested class body; no model_rebuild needed.
        type Envelope = Annotated[Ok | Err, m.Discriminator("kind")]
```

Why good: facade-only imports, `Annotated[..., m.Field(...)]` for every field, frozen+strict contracts, bare sibling names in the discriminated union (no string forward refs, no `model_rebuild`), `Discriminator` routed through `mp.*`, polymorphism without isinstance ladders.

### Bad — direct `pydantic` import and side-effectful validator

```text
# FORBIDDEN
from pydantic import BaseModel, Field, field_validator, Discriminator

class Window(BaseModel):
    start: int = 0
    end: int = 0

    @field_validator("start", mode="before")
    @classmethod
    def mixed_logic(cls, value):
        # coercion + side effects mixed in a validator
        logger = get_logger(__name__)
        logger.info("validating", value=value)   # side effect
        return int(value)
```

Why bad: direct `pydantic` imports bypass the workspace facade; validator has I/O side effects; no Annotated composition; model is not nested under a facade MRO; no frozen/strict contract. This exact pattern is BANNED by AGENTS.md §3 and the Pydantic facade rule above.

## Verification

- `ls -1 .agents/skills/pydantic-v2-patterns/SKILL.md`
- `rg -n "^name:|^description:" .agents/skills/pydantic-v2-patterns/SKILL.md`
- `for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" .agents/skills/pydantic-v2-patterns/SKILL.md || echo "MISSING $s"; done`
- `rg -n "TypeAdapter\(" --type py --glob '!flext-core/src/flext_core/_typings/typeadapters.py' --glob '!**/.venv/**'`
- `rg -n "^(import pydantic|from pydantic|from pydantic_core)" --type py --glob '!flext-core/src/flext_core/models/pydantic.py' --glob '!flext-core/src/flext_core/_utilities/pydantic.py' --glob '!flext-core/src/flext_core/_typings/typeadapters.py' --glob '!**/.venv/**'`
- `rg -n "up\.field_validator\(|up\.model_validator\(|up\.computed_field|mp\.Discriminator\(|mp\.BeforeValidator\(|strict=True" flext-core/src/flext_core/models/base.py flext-core/src/flext_core/models/settings.py flext-core/src/flext_core/models/domain_event.py flext-core/src/flext_core/_typings/typeadapters.py`
