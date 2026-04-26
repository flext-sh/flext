---
name: flext-import-rules
description: Enforces import ordering, alias conventions, and abstraction boundaries for the FLEXT 33-project monorepo (PEP 623, TYPE_CHECKING rules, no bare pydantic/structlog in consumers). Use when adding imports to any Python file, resolving circular imports, auditing import boundary violations, or checking whether a cross-project import is permitted by AGENTS.md §4.

---

# FLEXT Import Rules

**Reviewed**: 2026-04-26 | **Scope**: Evidence-backed skill refresh and rule alignment

## Hard Start Card (mandatory)

1. Imports at top-level only.
2. Respect order: future, stdlib, third-party, first-party, local.
3. Use canonical aliases only (`c m p t u r d e h s x`).
4. Do not import private modules from sibling projects.
5. In wrappers (`tests/examples/scripts`), import aliases from local wrapper package only.
6. Same-project cross-facade runtime imports are forbidden (except documented exceptions).
7. Validate with `ruff` and `pyrefly` immediately after import changes.

**One-line execution flow:**
`CHECK LAYER -> IMPORT FROM CANONICAL FACADE -> KEEP ORDER -> RUN RUFF/PYREFLY`

**Immediate failure conditions:**
- import added without checking `AGENTS.md` §4 matrix
- direct framework import in consumer project when abstraction exists
- same-project cross-facade runtime import without explicit exception

> **Verified from**: Static analysis of all `.py` files in `flext-core` and consuming projects on 2026-02-17.
> **Rule**: See `AGENTS.md` §4 Import Law for canonical aliases, import order, and prohibited import forms.

## Pre-Action Gate

Before any new import: AGENTS.md §0.D SSOT search keys + §4 Import Law + §2.7 Library Abstraction Boundaries. Inline imports inside functions: §3.4.

## Scope

- Import architecture and conventions for `flext-core` and all consuming projects.
- Canonical alias usage, tier-safe dependencies, and MRO-safe namespace composition.

## References

- `AGENTS.md`
- `.agents/skills/flext-architecture-layers/SKILL.md`
- `.agents/skills/flext-mro-namespace-rules/SKILL.md`
- `ruff-shared.toml`
- `flext-core/src/flext_core/`

## Rules

- Enforce import order: future, stdlib, third-party, first-party, local.
- Enforce architecture directionality and private-module boundaries.
- Use canonical aliases (`c`, `m`, `p`, `t`, `u`, `r`, `d`, `e`, `h`, `s`, `x`) at usage sites.
- Treat Pydantic objects and validators as consumed through `c`, `p`, `t`, `m`, `u` (and `s` for service facades) instead of direct framework-shaped usage in consumer layers.
- In wrapper surfaces (`tests/`, `examples/`, `scripts/`), import canonical aliases from the local wrapper package (`from tests import c, m, p, t, u`, `from examples import c, m, t`, `from scripts import c, m, t, u`) — never from sibling projects.
- Keep same-project public facades isolated at runtime; only the `TYPE_CHECKING` matrix from `AGENTS.md` §4 allows same-project cross-facade type references.
- **Hacks**: Canonical "Zero Hacks" rule in `AGENTS.md` §3.4.

## Instructions

- Apply import changes in dependency-tier order when refactoring shared modules.
- Validate both syntax and architectural intent after every import migration batch.
- Prefer public facades; avoid direct imports from private `_` modules in subprojects.

## Workflow

1. Inventory current import style and violations.
2. Apply canonical import form aligned with module tier.
3. Fix cross-project inheritance/import boundaries.
4. Re-run quality gates and targeted searches.

## Examples

```python
from __future__ import annotations

from typing import Annotated

from flext_core import c, m, p, r, t, u


class PayloadModel(m.Value):
    """Value object representing a named payload."""

    name: Annotated[t.NonEmptyStr, u.Field(description="Payload name")]


def parse_name(value: PayloadModel) -> p.Result[str]:
    """Parse the name field, failing on empty string."""
    if value.name == c.DEFAULT_EMPTY_STRING:
        return r[str].fail("name is missing")
    return r[str].ok(value.name)
```

## Detailed Import Rules

Full import rule enforcement is in [references/import-rules-detail.md](references/import-rules-detail.md). Load it when you need rule-level detail on:

- `from __future__ import annotations` + `from collections.abc import Mapping, Sequence` requirements
- Import ordering (future / stdlib / third-party / first-party / local)
- Cross-project import rules and tier enforcement
- Facade alias patterns (`c`, `m`, `t`, `u`, `p`) and where each is sourced
- TYPE_CHECKING policy and lazy `__init__.py` loading
- Ruff import configuration and suppression rules
- MRO namespace composition patterns and circular import resolution
