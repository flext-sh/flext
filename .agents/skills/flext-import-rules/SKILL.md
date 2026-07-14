---
name: flext-import-rules
description: 'Use this skill to enforce import ordering, alias conventions, and abstraction
  boundaries for the FLEXT 33-project monorepo (PEP 623, TYPE_CHECKING rules, no bare
  pydantic/structlog in consumers). Use when adding imports to any Python file, resolving
  circular imports, auditing imports. DO NOT USE FOR: questions unrelated to flext-import-rules
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Import Rules

**UTILITY SKILL**

Enforces import hygiene, alias conventions, and abstraction boundaries across the FLEXT monorepo.

## USE FOR

- Adding or reorganizing imports in any Python file.
- Resolving circular imports.
- Auditing imports for wildcard, relative, or direct-framework violations.

## DO NOT USE FOR

- Questions unrelated to FLEXT import rules.
- Creating projects or architecture from scratch.

## Workflow

1. Inventory current imports against the rules below.
2. Rewrite to the canonical form.
3. Run `ruff check <file>` and `pyrefly check <file>`.

## Critical rules

- Required header: `from __future__ import annotations` and `from collections.abc import Mapping, Sequence`.
- **ADR-005:** `flext-core` `src/` must **not** import `flext-cli`/`flext-infra` (runtime cycle-free `infra → cli → core`); no direct `jinja2`/`yaml`/`jsonschema` import in consumers — route through `u.Cli.*`. See `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.
- Absolute imports are mandatory in implementation modules. The only relative-import
  exception is a generated internal package `__init__.py`, which re-exports direct
  sibling symbols with the exact same-name form `from .module import Name as Name`.
  Wildcards remain forbidden everywhere.
- Import `flext_core` via root namespace using canonical aliases (`c`, `m`, `p`, `r`, `t`, `u`, ...).
- Facade owner modules that MRO-extend an upstream FLEXT facade import that upstream short alias directly and use it as the base class (`from flext_cli import m`; `class FlextPluginModels(m): ...`; `m = FlextPluginModels`).
- Project `base.py` may import upstream runtime `s` as the service MRO base and publish local `s` exactly once.
- Project `api.py` imports the composed runtime facade class and publishes the package operational alias.
- Bridge external frameworks (pydantic, structlog, oracledb, ldap3, grpc, sqlalchemy) through `flext_core` or the project-specific wrapper; do not import them directly in consumers.
- Use `TYPE_CHECKING` only for type-only symbols and the generated PEP 562 map at
  the production package root; internal package initializers are eager static
  re-exports and never use `TYPE_CHECKING` to emulate lazy loading. Do not hide cycles.

## Good examples

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
from pathlib import Path

from flext_core import c, m, r, t, u
```

Generated internal initializer:

```python
# AUTO-GENERATED FILE — Regenerate with: make gen
"""Services package."""

from __future__ import annotations

from .auth import FlextCliAuth as FlextCliAuth

__all__: tuple[str, ...] = ("FlextCliAuth",)
```

## Bad examples

```python notest
# Illustrative anti-patterns — these imports violate FLEXT import discipline.
from .utils import helper  # relative import outside a generated internal initializer
from flext_core import *  # wildcard
from typing import Dict, List  # legacy typing
import oracledb  # direct framework; use flext_db_oracle wrapper
```

## Import order

1. `from __future__ import annotations`
2. `from collections.abc import Mapping, Sequence`
3. stdlib
4. third-party
5. first-party (`flext_core.*`, `flext_*`)
6. local package

Within each group: `import x` before `from x import y`, alphabetical, one per line.

## MRO import matrix

| File | `c`/`t`/`p`/`m`/`u` source | Others |
|------|----------------|--------|
| `models/*.py` | parent | own package |
| `_utilities/*.py` | parent for `u` | own package |
| facade files | parent short alias for the facade being extended | own package |
| `base.py` | upstream runtime `s` | own package plus private MRO mixins |
| `api.py` | composed runtime facade class | own package |
| services/servers/tests | own package | own package |

Parent = most advanced MRO package; `flext-core` uses its own package.

## Tier enforcement

Only import lower tiers:

```
constants/typings → runtime → protocols → models → utilities → logging/container → dispatcher
```

## Validation

```bash
ruff check --no-fix <file>
ruff format --check <file>
pyrefly check <file>
mypy <file>
pyright <file>
```

## References

- [references/import-rules-detail.md](references/import-rules-detail.md)
- `.agents/skills/coding-standards/SKILL.md` — general coding standards quick-reference
