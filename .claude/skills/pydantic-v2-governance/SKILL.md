---

name: pydantic-v2-governance
description: Internal Pydantic v2 governance patterns for FLEXT 33-project monorepo. Use when creating models, validators, or working with Pydantic v2 features across the codebase.
triggers:
  - creating models, validators, or Pydantic v2 features across the monorepo
  - auditing Pydantic v2 governance patterns across 33 projects
  - ensuring internal Pydantic v2 compliance
  - reviewing model inheritance and composition patterns
  - checking for v1-syntax remnants in any project

---

<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [1. Field() → Annotated Pattern](#1-field--annotated-pattern)
  - [2. default_factory for Mutable Defaults](#2-defaultfactory-for-mutable-defaults)
  - [3. TypeAdapter Caching](#3-typeadapter-caching)
  - [4. Protocol vs ABC](#4-protocol-vs-abc)
  - [5. issubclass() Safety](#5-issubclass-safety)
  - [6. ConfigDict](#6-configdict)
  - [7. Validation Boundaries](#7-validation-boundaries)
  - [8. Anti-Patterns](#8-anti-patterns)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

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
- **Mandatory Pydantic v2 Mastery**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features to their fullest across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class extends `BaseModel` (or FLEXT base models) via MRO.
- **Field() for ALL declarations**: Use `Field()` with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts.
- **Secrets**: Use `SecretStr`/`SecretBytes` for secrets.
- **ConfigDict**: Use `model_config = ConfigDict(...)` for settings — standalone `*Config` classes TOTALLY FORBIDDEN (use `BaseSettings`/`ConfigDict`).
- **Minimize custom validators**: Prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`, `conint`).
- **FORBIDDEN in models**: initialization helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@computed_field`, `model_post_init`, `PrivateAttr`) and canonical field names such as `success`, `failure`, `expired`, `healthy`.
- **Enums/Mappings/Literals**: From `constants.py` (`c.*`), settings from `settings.py` (`s.*`).
- **JSON**: Via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`.
- **Internal state**: Via `PrivateAttr` — never bare `self._x`.
- **Nested classes**: MAY have business methods but ALL properties use `Field()`/`PrivateAttr`.
- **models.py/_models/**: For model definitions ONLY.
- **Centralized runtime carriers**: Prefer one `m.<Domain>.*State` or `m.<Domain>.*Status` model per service concern over many tiny pass-through carrier models and dict round-trips.


## Instructions

> Full governance patterns are in [references/governance-patterns.md](references/governance-patterns.md). Load it for detailed patterns.

Key rules (quick reference):
- Use `Annotated[T | None, Field(...)]` for nullable fields, NOT `Annotated[T, Field(...)] | None`
- Every `BaseModel` subclass needs `ConfigDict(...)` — never `class Config:`
- All fields declared via `Field()` with description/examples metadata
- `PrivateAttr` for internal state — never bare `self._x`
- `@computed_field` replaces `@property` everywhere
- Validators: `@field_validator` for field-level, `@model_validator(mode="after")` for cross-field
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
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "title": "User",
            "description": "User entity with strict validation",
        },
    )

    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="User full name",
            examples=["Alice Smith", "Bob Jones"],
        ),
    ]
    email: Annotated[
        str,
        Field(
            pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
            description="User email address",
            examples=["alice@example.com"],
        ),
    ]
    tags: t.StrSequence = Field(
        default_factory=list,
        description="User tags",
    )
```

Why good: Uses `Annotated` correctly, `Field()` with full metadata, `default_factory` for mutable default, `ConfigDict` for settings.

Bad:

```python
from pydantic import BaseModel


class User(BaseModel):
    class Config:  # ✗ v1 style
        extra = "forbid"

    name: str  # ✗ No Field() metadata
    email: str  # ✗ No validation
    tags: t.StrSequence = []  # ✗ Mutable default bug
```

Why bad: v1 `Config` class, no `Field()` metadata, mutable default bug.

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
rg -n "Annotated\[.*\|.*None.*Field" flext-core/src/flext_core/_models/cqrs.py

# Run validation
make validate PROJECT=flext-core
make validate PROJECT=flext-core FIX=1
```
