---
name: flext-import-rules
description: >-
  Enforce canonical FLEXT import routing, public facade boundaries,
  declaration-only imports, and cycle-free package direction. Use when adding
  or moving imports, resolving cycles, reviewing external-library boundaries,
  or composing c/m/p/r/t/u/s facades; do not use to invent a project layout.
---

# FLEXT import routing

Treat imports as dependency declarations. Read the target package's public
facade and dependency metadata before changing them; this skill is an
operating procedure, not the declaration SSOT.

## Procedure

1. Identify whether the file owns a facade/bridge or consumes one.
2. Import consumers from the owning package root and its canonical short
   aliases.
3. Let only the facade or bridge owner import its private implementation or
   external framework.
4. Keep runtime dependencies at runtime. Every name in a runtime-evaluated
   annotation (Pydantic field, PEP 526 assignment, beartype signature, PEP 695
   `type` RHS) is a runtime import. `TYPE_CHECKING` is reserved for symbols used
   ONLY in static-only positions; it is NEVER a way to hide a reverse facade edge
   (reverse edges are forbidden entirely — ADR-011).
5. Remove the superseded import path in the same change.
6. Run the target repository's configured Ruff and type gates.

## Invariants

- Use absolute imports in production code. Do not use relative or wildcard
  imports.
- Import FLEXT consumers through public package roots, such as
  `from flext_core import c, m, p, r, t, u`.
- Import project-owned `config` and `settings` from that project's public root;
  do not read environment variables or configuration files from leaf modules.
- Let a facade owner import the upstream short alias it extends, compose the
  local facade, and publish the local alias exactly once. Downstream consumers
  import that local alias from the package root.
- Let only the canonical bridge owner import Pydantic, Structlog, database
  drivers, template engines, or other external frameworks. Consumers import
  the validated model or wrapper from its owning FLEXT package.
- Keep private implementation imports inside their public facade/composition
  owner. A consumer importing a private module is an ownership violation.
- Preserve runtime direction `flext-infra -> flext-cli -> flext-core`; core must
  not import cli or infra at runtime.
- Never use `TYPE_CHECKING` to hide a runtime class, method, side effect, or
  dependency cycle. Move declaration-only contracts to their canonical
  protocol/type owner and fix runtime ownership at the source.
- Follow the repository's configured import ordering. Do not invent universal
  required imports that its configuration does not declare.

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
- Use `TYPE_CHECKING` only for symbols used solely in static-only positions (never
  a name evaluated at runtime in an annotation — ADR-011) and the generated PEP 562
  map at the production package root; internal package initializers are eager static
  re-exports and never use `TYPE_CHECKING` to emulate lazy loading. Never gate an
  annotation name or hide a reverse facade edge (reverse edges are forbidden). Do not hide cycles.

## Good examples

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
from pathlib import Path

from flext_core import c, m, r, p, t, u
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
