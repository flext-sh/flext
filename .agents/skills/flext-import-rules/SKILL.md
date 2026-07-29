---
name: flext-import-rules
description: 'Use when adding or reviewing Python imports, resolving cycles, composing MRO facades, or enforcing framework abstraction boundaries in any FLEXT package or first-class test/example/script.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Import Rules

Enforces import hygiene, alias conventions, and abstraction boundaries across the FLEXT monorepo.

## Workflow

1. Inventory current imports against the rules below.
2. Rewrite to the canonical form.
3. Run `ruff check <file>` and `pyrefly check <file>`.

## Critical rules

- Required header: `from __future__ import annotations` and `from collections.abc import Mapping, Sequence`.
- Absolute imports only in `src/`; no relative imports, no wildcards.
- Import `flext_core` via root namespace using canonical aliases (`c`, `m`, `p`, `r`, `t`, `u`, ...).
- Bridge external frameworks (pydantic, structlog, oracledb, ldap3, grpc, sqlalchemy) through `flext_core` or the project-specific wrapper; do not import them directly in consumers.
- Use `TYPE_CHECKING` only for type-only symbols and `__init__.py` lazy loading; do not hide cycles.

## Good examples

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
from pathlib import Path

from flext_core import c, m, r, t, u
```

## Bad examples

```python notest
# Illustrative anti-patterns — these imports violate FLEXT import discipline.
from .utils import helper  # relative import
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

| File | `m`/`u` source | Others |
|------|----------------|--------|
| `models/*.py` | parent | own package |
| `_utilities/*.py` | parent for `u` | own package |
| facade files | parent for self alias | own package |
| services/servers/tests | own package | own package |

Parent = most advanced MRO package; `flext-core` uses its own package.

## Tier enforcement

Only import lower tiers:

```
constants/typings → runtime → protocols → models → utilities → logging/container → dispatcher
```

## Validation

```bash
ruff check <file>
pyrefly check <file>
```

## References

- [references/import-rules-detail.md](references/import-rules-detail.md)
- `.agents/skills/coding-standards/SKILL.md` — general coding standards quick-reference
