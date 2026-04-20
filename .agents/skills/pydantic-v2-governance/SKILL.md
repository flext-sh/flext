---
name: pydantic-v2-governance
description: Internal Pydantic v2 governance patterns for the FLEXT 34-project monorepo. Use when creating models, validators, or working with Pydantic v2 features across the codebase — codifies HARD rules, forbidden structures, facade-only imports, and the no-recursion-outside-JsonValue rule.

---

# Pydantic v2 Governance

**Reviewed**: 2026-04-20 | **Scope**: Canonical Pydantic v2 governance — HARD rules checklist, forbidden structures, facade-only imports, no-recursion-outside-JsonValue

## Scope

- `.agents/skills/pydantic-v2-governance/`
- All 34 FLEXT projects (`src/`, `tests/`, `examples/`)
- Codifies ACTUAL codebase patterns, not theoretical best practices

## References

- `AGENTS.md` §3.1-§3.3 — Code Law (canonical governance)
- `.agents/skills/lib-pydantic-v2/SKILL.md` — Pydantic v2 API rules
- `.agents/skills/pydantic-v2-patterns/SKILL.md` — Advanced patterns
- `flext-core/src/flext_core/_models/cqrs.py:82-101` — Annotated pattern
- `flext-core/src/flext_core/_models/base.py:53-102` — TypeAdapter caching
- `flext-core/src/flext_core/protocols.py:1-100` — Protocol patterns
- `flext-core/src/flext_core/typings.py:1-150` — Type system foundation
- `flext-core/AGENTS.md` — Project-level pointer

## Rules

- **Policy Authority**: `AGENTS.md` §3.1-§3.3 is supreme law. This skill documents IMPLEMENTATION patterns.
- **Codebase Evidence**: Every pattern MUST reference actual codebase files.
- **No Contradiction**: This skill extends `lib-pydantic-v2` and `pydantic-v2-patterns`, never contradicts them.
- **Alias-first consumption**: Pydantic-facing contracts are consumed via `c`, `p`, `t`, `m`, `u` (and `s` for service facades), not framework-direct usage patterns in consumers.
- **Mandatory Pydantic v2 Mastery**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY across ALL 34 projects (`src/`, `tests/`, `examples/`). Every class extends `m.BaseModel` (or FLEXT base models like `m.Value`, `m.Entity`, `m.FrozenModel`) via MRO.
- **m.Field() for ALL declarations**: Use `m.Field()` with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts.
- **Secrets**: Use `m.SecretStr` / `up.SecretBytes` for secrets (never plain `str`).
- **ConfigDict**: Use `model_config = m.ConfigDict(...)` on every model. Standalone `*Config` classes or `class Config:` blocks FORBIDDEN.
- **Minimize custom validators**: Prefer built-in constraints through the facade (`m.Field(ge=0, le=100)`, `m.StringConstraints()`, `Literal[...]`, `m.constr`, `m.conint`) before writing a custom validator.
- **FORBIDDEN in models**: initialization helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@u.computed_field`, `model_post_init`, `u.PrivateAttr`) and canonical field names such as `success`, `failure`, `expired`, `healthy`.
- **Enums/Mappings/Literals**: From `constants.py` (`c.*`), settings from `settings.py` (`s.*`).
- **JSON**: Via `model_dump_json()`, `model_validate_json()`, and cached `m.TypeAdapter` through the registry in `flext-core/src/flext_core/_typings/typeadapters.py` — never raw `json.loads()`/`json.dumps()` in consumers.
- **Internal state**: Via `u.PrivateAttr` — never bare `self._x`.
- **Nested classes**: MAY have business methods but ALL properties use `m.Field()`/`u.PrivateAttr`.
- **models.py/_models/**: For model definitions ONLY.
- **Centralized runtime carriers**: Prefer one `m.<Domain>.*State` or `m.<Domain>.*Status` model per service concern over many tiny pass-through carrier models and dict round-trips.

## Recursive Types — single permitted source

- **Only `pydantic.JsonValue`** (re-exported as `t.JsonValue` / `t.Cli.JsonValue`) is permitted as a recursive type anywhere in the workspace.
- **FORBIDDEN**: introducing any other recursive `type X = ...` alias, any recursive `RootModel` self-reference, or any manual `t.Recursive*` alias in `src/`. Existing legacy recursive aliases marked for refactor MUST NOT be expanded — the call site MUST be rewritten to use `t.JsonValue` or a flat composed alias.
- Verification: `rg -n "type\s+[A-Z][A-Za-z]+\s*=\s*[^\n]*\\b\\1\\b" --type py src/` → every hit must either be `t.JsonValue` itself or a legacy alias with an explicit `# refactor: replace with t.JsonValue` comment.

## Model HARD Rules Checklist (enforcement)

Every new or touched Pydantic model MUST satisfy these non-negotiable rules. Each `UserWarning` emitted by the enforcement layer is a FAILURE, not a nag.

- **`model_config = m.ConfigDict(...)`** present on every `BaseModel`/`RootModel` subclass. `frozen=True` for settings/values, `strict=True` for public contracts.
- **No `class Config:`** blocks anywhere. v1 syntax is banned.
- **Immutable defaults**: `default_factory=lambda: MappingProxyType({})` for empty maps, `default_factory=frozenset` for empty sets, `default_factory=tuple` for empty tuples. Never bare `= {}`, `= set()`, `= []`.
- **`u.PrivateAttr` for internal state** — never `self._foo: X = ...` in `__init__`, never module-level helpers bound to models.
- **`@u.computed_field`** replaces every `@property` on a model.
- **Validators**:
  - single-field coercion → `Annotated[T, m.BeforeValidator(u.normalize_X)]` / `m.AfterValidator(...)`.
  - cross-field / instance-bound → `@u.model_validator(mode="after")` returning `Self`.
  - `@u.field_validator` only when `Annotated[...]` is genuinely unworkable.
- **No helpers on models** — every domain operation lives in `u.*`. Models expose fields, `@computed_field`, and validators. Period.
- **`validate_default=True`** on every field whose default flows through a normalizer.
- **No `model_rebuild()`** — use bare sibling names in Pydantic field annotations inside namespace classes (see `feedback_no_model_rebuild.md`).
- **No `cast()` / `Any` / `object` as field type** — always the most restrictive real type.
- **`m.SecretStr`** for secrets (never plain `str`).
- **`m.Discriminator(...) + m.Tag(...)`** for discriminated unions; no isinstance ladders on RootModel.
- **Boolean field names**: `success`, `failure`, `expired`, `healthy` — never `is_*` / `has_*`.
- **Namespace exposure**: every model lives inside `m.<Project>.*` / `m.*`. No bare top-level `class Foo(BaseModel):` in production modules.

## Forbidden Structures (use these replacements)

| Forbidden | Replacement |
| --- | --- |
| `typing.TypedDict` | `class X(m.BaseModel): ...` or `class X(m.RootModel[Mapping[...]]): ...` |
| `@dataclasses.dataclass` | `class X(m.BaseModel): model_config = m.ConfigDict(frozen=True)` |
| `typing.NamedTuple` / `collections.namedtuple` | frozen `m.BaseModel` |
| `pydantic.dataclasses.dataclass` | `m.BaseModel` subclass |
| Module-scope `dict[...]` / `list[...]` / `set[...]` constants | `StrEnum` / `Final[frozenset[Literal[...]]]` / `MappingProxyType(...)` (see flext-constants-discipline) |
| `typing.TypeVar` / `typing.TypeAlias` / `typing.Generic` | PEP 695 `class Foo[T]` / `def f[T]` / `type X = ...` |
| `typing.Optional[T]` / `typing.Union[A, B]` | `T | None` / `A | B` |
| `class Config:` inline on a model | `model_config = m.ConfigDict(...)` |

Every deviation requires an explicit SKILL exemption with a named owner and a planned migration ticket.

## Instructions

> Full governance patterns are in [references/governance-patterns.md](references/governance-patterns.md). Load it for detailed patterns.

Key rules (quick reference):

- Use `Annotated[T | None, m.Field(...)]` for nullable fields, NOT `Annotated[T, m.Field(...)] | None`
- Every `BaseModel` subclass needs `ConfigDict(...)` — never `class Config:`
- All fields declared via `m.Field()` with description/examples metadata
- `u.PrivateAttr` for internal state — never bare `self._x`
- `@u.computed_field` replaces `@property` everywhere
- Validators: `@u.field_validator` for field-level, `@u.model_validator(mode="after")` for cross-field
- Boolean fields: `success`, `failure`, `expired`, `healthy` — never `is_success`, `is_valid`
- No `model_rebuild()`, no `cast()`, no `Any`

## Workflow

1. Read `AGENTS.md` §3.1-§3.3 for supreme law
2. Read `lib-pydantic-v2` for API rules
3. Read `pydantic-v2-patterns` for advanced patterns
4. Locate nearest codebase example for the pattern you need
5. Copy structure from real implementation
6. Adapt names/types while preserving validation semantics
7. Run `make validate PROJECT=<name>` to verify
8. Run `make validate PROJECT=<name> FIX=1` to auto-fix

## Examples

Good:

```python
from __future__ import annotations

from typing import Annotated, override

from flext_core import m, p, r, s, t


class FlextGovernance(s[m.Value]):
    """Single facade per module — MRO-composed service with nested domain."""

    class Governance:
        """Domain namespace — nested models live here."""

        class User(m.Value):
            """User value object."""

            model_config = m.ConfigDict(frozen=True, strict=True)

            name: Annotated[t.NonEmptyStr, m.Field(description="User display name")]
            email: Annotated[t.NonEmptyStr, m.Field(description="User email")]

    @override
    def execute(self) -> p.Result[m.Value]:
        """Create user through the facade."""
        user = FlextGovernance.Governance.User(
            name="alice",
            email="alice@example.com",
        )
        return r[m.Value].ok(user)
```

Why good: one facade per module, nested domain namespace, MRO via `s[T]`, canonical `r[T].ok()`, facade-only imports (`c, m, p, r, s, t, u`), `frozen=True`/`strict=True` boundary contract, zero direct pydantic imports.

Bad (anti-pattern — FORBIDDEN):

```text
# FORBIDDEN: direct pydantic imports in a consumer
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str               # missing m.Field() metadata
    email: str              # no validation
    tags: list[str] = []    # mutable default
```

Why bad: bypasses the flext-core facade (direct `pydantic` import is BANNED in consumers — use canonical `m.*` / `u.*` aliases from `flext_core`); fields lack `m.Field()` metadata; mutable default bug; no MRO-nested domain namespace; no `frozen=True`/`strict=True` boundary contract. This exact pattern violates AGENTS.md §3 and §4 plus the Pydantic facade rule in `pydantic-v2-patterns`. (The `up`/`mp` internal aliases only exist inside `flext-core/src/flext_core/_*` to break bootstrap cycles — never as a consumer-facing pattern.)

## Verification

```bash
# Confirm skill exists
ls -1 .agents/skills/pydantic-v2-governance/SKILL.md

# Confirm frontmatter
rg -n "^name:|^description:" .agents/skills/pydantic-v2-governance/SKILL.md

# Confirm sections
for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" .agents/skills/pydantic-v2-governance/SKILL.md || echo "MISSING $s"; done

# Confirm no v1 patterns in codebase
rg -n "@validator\(" --glob "**/*.py" flext-core/src/ flext-grpc/src/
rg -n "\.dict\(\)|\.json\(\)" --glob "**/*.py" flext-core/src/
rg -n "class Config:" --glob "**/*.py" flext-core/src/

# Confirm no model_rebuild
rg -n "model_rebuild\(" --glob "**/*.py" flext-core/src/ flext-core/tests/

# Confirm TypeAdapter caching pattern
rg -n "ClassVar\[TypeAdapter" flext-core/src/flext_core/_models/base.py

# Confirm Annotated pattern
rg -n "Annotated\[.*\|.*None.*m.Field" flext-core/src/flext_core/_models/cqrs.py

# Run validation
make validate PROJECT=flext-core
make validate PROJECT=flext-core FIX=1
```
