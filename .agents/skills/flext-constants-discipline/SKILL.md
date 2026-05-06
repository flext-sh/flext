---
name: flext-constants-discipline
description: Canonical constants layout using StrEnum, IntEnum, Literal, frozenset, MappingProxyType, tuple and Final. Use when adding or refactoring any c.* constant across the workspace.
---

# FLEXT Constants Discipline

**Reviewed**: 2026-04-19 | **Scope**: c.* constants tier, closed-set enumerations, immutable read-only maps and tuples

## Scope

- `flext-core/src/flext_core/_constants/**`
- Any consumer project's `constants.py` / `_constants/**` that exposes members under `c.<Project>.*`.

## References

- `AGENTS.md` — §5 constants rules
- `flext-core/src/flext_core/_constants/base.py`
- `flext-core/src/flext_core/_constants/infra.py`
- `.agents/skills/flext-mro-namespace-rules/SKILL.md`
- `.agents/skills/rules-flext-core/SKILL.md`

## Rules

- **Closed sets of tokens** (status, mode, kind, phase) MUST be `StrEnum` or `IntEnum`. Never `t.StrSequence`, never `Literal[...]` lists pretending to be enums.
- **Small literal unions** (≤4 values used as type hints, not iteration) MUST be a PEP 695 `type <Name> = Literal["a", "b"]` alias in the typings tier.
- **Membership tests** MUST use `Final[frozenset[Literal[...]]]`. Never `set[str]`, never mutable set literals.
- **Read-only maps** MUST be `Final[Mapping[K, V]] = MappingProxyType({...})`. Never raw `dict[...]` at module scope.
- **Ordered sequences** MUST be `Final[tuple[T, ...]]`. Never `list[T]` at module scope.
- **Scalar sentinels / names** MUST be `Final[X]`. Never bare assignments without `Final[...]`.
- **Namespace everything**: each constant lives under `c.<Project>.<Category>.<Name>`. No module-top-level constants, no flat aliases on the facade.
- **No raw `list` / `set` / `dict` at module scope** — forbidden in production code. Tests may use ephemeral collections inside fixtures only.
- **No `ClassVar[t.StrSequence]` as enum surrogate** — if it's a closed set of tokens, migrate to `StrEnum`.
- **Rich types only**: prefer `StrEnum` over `Literal` for runtime iteration; prefer `frozenset[Literal[...]]` over `t.StrSequence` for membership.

## Instructions

- Before introducing a new constant, identify the category: token set, literal union, membership set, read-only map, ordered list, scalar sentinel.
- Pick the matching rich-type primitive (see Rules).
- Place the constant inside the appropriate nested namespace under `c.<Project>.<Category>`.
- Wrap maps with `MappingProxyType(...)` immediately at definition site. Never expose a mutable `dict`.
- Wrap sets with `frozenset(...)` immediately at definition site. Never expose a mutable `set`.
- For tuples, annotate `Final[tuple[X, ...]]` (homogeneous) or `Final[tuple[X, Y, Z]]` (heterogeneous).
- Document each enum member with a one-line comment only when the name alone does not convey meaning.
- When migrating existing `ClassVar[tuple[...]]` enum surrogates → `StrEnum`, update every call site to `c.<Project>.<Category>.MEMBER_NAME` and run `ruff check` to catch stragglers.

## Workflow

1. Grep for raw module-scope collections in the target project:
   - `rg -n "^[A-Z_]+\s*[:=]\s*(\[|\{|dict\(|list\(|set\()" src/ --type py`.
2. For each hit, pick the canonical form from Rules.
3. Relocate into the `c.<Project>.<Category>` namespace.
4. Update consumers.
5. Validate: `ruff check`, `pyrefly check`, `pytest -q`.

## Examples

Good — closed token set:

```python
# flext-core/_constants/base.py
from enum import StrEnum


class FlextConstantsBase:
    class Encoding(StrEnum):
        DEFAULT = "utf-8"
        LATIN1 = "latin-1"
```

Why good: enum discipline, namespace access via `c.Encoding.DEFAULT`, no tuple surrogate.

Good — read-only map:

```python
from collections.abc import Mapping
from types import MappingProxyType
from typing import Final


class FlextConstantsBase:
    HEADER_MAP: Final[t.StrMapping] = MappingProxyType({
        "content-type": "application/json",
        "accept": "application/json",
    })
```

Why good: immutable, type-annotated, namespaced.

Good — membership frozen set:

```python
from typing import Final, Literal


class FlextConstantsBase:
    TRUE_TOKENS: Final[frozenset[Literal["1", "true", "yes", "on"]]] = frozenset({
        "1",
        "true",
        "yes",
        "on",
    })
```

Why good: closed membership test, literal-typed, frozen.

Bad — module-scope raw dict:

```python
# FORBIDDEN
HEADER_MAP = {"content-type": "application/json"}  # mutable, untyped, un-namespaced
```

Why bad: mutable at import; consumers can patch; no type guarantees; violates constants tier.

Bad — ClassVar tuple enum surrogate:

```python
from typing import ClassVar


class Attrs:
    USER_IDS: ClassVar[t.StrSequence] = (
        "cn",
        "uid",
        "sAMAccountName",
    )  # should be StrEnum
```

Why bad: strings are indistinguishable from free-form values; `Attrs.USER_IDS[0]` is magic; migration to `StrEnum` exposes a schema.

## Verification

- `rg -n "^[A-Z_]+\s*[:=]\s*(\[|\{)" --type py src/ --glob '!**/.venv/**'` → expect zero module-scope raw collections in production code.
- `rg -n "ClassVar\[tuple\[str" --type py src/` → audit each hit: migrate to StrEnum or justify.
- `rg -n "type\s+[A-Z][A-Za-z]+\s*=\s*Literal\[" --type py src/` → every Literal alias lives in the typings tier, not inline inside a model.
- `ruff check src/` → 0.
- `pyrefly check src/` → 0.
