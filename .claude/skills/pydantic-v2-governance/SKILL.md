---
name: pydantic-v2-governance
description: Internal Pydantic v2 governance patterns for FLEXT 33-project monorepo. Use when creating models, validators, or working with Pydantic v2 features across the codebase.

---

# Pydantic v2 Governance

**Reviewed**: 2026-02-22 | **Scope**: Canonical Pydantic v2 patterns from FLEXT codebase

## Scope

- `.claude/skills/pydantic-v2-governance/`
- All 33 FLEXT projects (`src/`, `tests/`, `examples/`)
- Codifies ACTUAL codebase patterns, not theoretical best practices

## References

- `AGENTS.md` §3.1-§3.3 — Code Law (canonical governance)
- `.claude/skills/lib-pydantic-v2/SKILL.md` — Pydantic v2 API rules
- `.claude/skills/pydantic-v2-patterns/SKILL.md` — Advanced patterns
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
- **Mandatory Pydantic v2 Mastery**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features to their fullest across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class extends `BaseModel` (or FLEXT base models) via MRO.
- **u.Field() for ALL declarations**: Use `u.Field()` with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts.
- **Secrets**: Use `SecretStr`/`SecretBytes` for secrets.
- **ConfigDict**: Use `model_config = ConfigDict(...)` for settings — standalone `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`).
- **Minimize custom validators**: Prefer built-in constraints (`u.Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`, `conint`).
- **FORBIDDEN in models**: initialization helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@u.computed_field`, `model_post_init`, `u.PrivateAttr`) and canonical field names such as `success`, `failure`, `expired`, `healthy`.
- **Enums/Mappings/Literals**: From `constants.py` (`c.*`), settings from `settings.py` (`s.*`).
- **JSON**: Via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`.
- **Internal state**: Via `u.PrivateAttr` — never bare `self._x`.
- **Nested classes**: MAY have business methods but ALL properties use `u.Field()`/`u.PrivateAttr`.
- **models.py/_models/**: For model definitions ONLY.
- **Centralized runtime carriers**: Prefer one `m.<Domain>.*State` or `m.<Domain>.*Status` model per service concern over many tiny pass-through carrier models and dict round-trips.

## Instructions

> Full governance patterns are in [references/governance-patterns.md](references/governance-patterns.md). Load it for detailed patterns.

Key rules (quick reference):

- Use `Annotated[T | None, u.Field(...)]` for nullable fields, NOT `Annotated[T, u.Field(...)] | None`
- Every `BaseModel` subclass needs `ConfigDict(...)` — never `class Config:`
- All fields declared via `u.Field()` with description/examples metadata
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

            name: Annotated[t.NonEmptyStr, u.Field(description="User display name")]
            email: Annotated[t.NonEmptyStr, u.Field(description="User email")]

    @override
    def execute(self) -> p.Result[m.Value]:
        """Create user through the facade."""
        user = FlextGovernance.Governance.User(
            name="alice",
            email="alice@example.com",
        )
        return r[m.Value].ok(user)
```

Why good: one facade per module, nested domain namespace, MRO via `s[T]`, canonical `r[T].ok()`.

Bad:

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    """v1-style Config class — FORBIDDEN in FLEXT."""

    model_config = ConfigDict(extra="forbid")

    name: str  # No u.Field() metadata
    email: str  # No validation
    tags: list[str] = []  # Mutable default bug
```

Why bad: v1 `Config` class, no `u.Field()` metadata, mutable default bug.

## Verification

```bash
# Confirm skill exists
ls -1 .claude/skills/pydantic-v2-governance/SKILL.md

# Confirm frontmatter
rg -n "^name:|^description:" .claude/skills/pydantic-v2-governance/SKILL.md

# Confirm sections
for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" .claude/skills/pydantic-v2-governance/SKILL.md || echo "MISSING $s"; done

# Confirm no v1 patterns in codebase
rg -n "@validator\(" --glob "**/*.py" flext-core/src/ flext-grpc/src/
rg -n "\.dict\(\)|\.json\(\)" --glob "**/*.py" flext-core/src/
rg -n "class Config:" --glob "**/*.py" flext-core/src/

# Confirm no model_rebuild
rg -n "model_rebuild\(" --glob "**/*.py" flext-core/src/ flext-core/tests/

# Confirm TypeAdapter caching pattern
rg -n "ClassVar\[TypeAdapter" flext-core/src/flext_core/_models/base.py

# Confirm Annotated pattern
rg -n "Annotated\[.*\|.*None.*u.Field" flext-core/src/flext_core/_models/cqrs.py

# Run validation
make validate PROJECT=flext-core
make validate PROJECT=flext-core FIX=1
```
