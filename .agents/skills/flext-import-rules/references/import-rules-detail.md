## Import Rules Summary

### R1: Required future annotations

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
```

### R2: Import order (ruff `I` rules)

Groups: future → stdlib → third-party → first-party (`flext_core.*`) → local.
Within group: `import x` before `from x import y`, alphabetical, one per line.

### R3: Import flext-core via root namespace

Always `from flext_core import c, m, p, r, t, u, ...`.

### R4: Subproject patterns

- **A:** `from flext_core import m, r, p, t`
- **B:** `from flext_core import FlextDispatcher`
- **C:** Facade owner modules inherit the upstream short alias for the facade being extended (`from flext_cli import c`; `class FlextPluginConstants(c): ...`; `c = FlextPluginConstants`)
- **D:** Integration projects inherit parent facade (e.g., `FlextMeltanoModels, FlextDbOracleModels`), never `FlextModels` directly
- **E:** Naming: `Flext<Tap|Target|Dbt><Domain><Models|Constants|Types|Utilities|Protocols>`
- **F:** `base.py` inherits upstream runtime `s` and private MRO utility mixins, then publishes local `s` once.
- **G:** `api.py` inherits the composed runtime facade class and publishes the package operational alias once.

### R4F: MRO parent import matrix

| File | `c`/`t`/`p`/`m`/`u` source | others |
|------|----------------|--------|
| `models/*.py` | parent | own pkg |
| `_utilities/*.py` | parent for `u` | own pkg |
| facade files | parent short alias for the facade being extended | own pkg |
| `base.py` | upstream runtime `s` | own pkg plus private MRO mixins |
| `api.py` | composed runtime facade class | own pkg |
| services/servers/tests | own pkg | own pkg |

Parent = most advanced MRO package; flext-core uses own package.

### R5: Tier enforcement

Only import lower tiers: constants/typings → runtime → protocols → models → utilities → logging/container → dispatcher.

### R6: Private modules

`_` modules are implementation details; only their facade may import them.

### R7: Facade aliases

Each facade exposes a lowercase alias (`c`, `m`, `p`, `r`, `t`, `u`, ...).

### R8: TYPE_CHECKING and package initializers

Use `TYPE_CHECKING` only for type-only symbols and the generated PEP 562 map at
the production package root. Every internal importable directory at arbitrary
depth has a generated static `__init__.py` with relative same-name re-exports of
direct sibling symbols and a sorted literal tuple `__all__`, including
`__all__ = ()` when it owns no direct export. Internal initializers never flatten
descendants and never use lazy loading. Do not hide cycles.

### R9: Ruff config

- `target-version = "py313"`
- `required-imports = ["from __future__ import annotations", "from collections.abc import Mapping, Sequence"]`
- Enforces `I001`, `I002`.

### R10: Forbidden

- `from flext_core import *`
- Relative imports outside generated internal package initializers
- `typing.List/Dict/Optional/Union`
- `eval`, dynamic `getattr` for architecture
- Shadowing aliases (e.g., `result` instead of `r`)

### R11: No double-assignment of facade aliases

Assign alias exactly once per facade.

Facade owner modules are the sanctioned self-rebind shape: import the upstream
short alias, use it as the MRO base, and publish the local alias once at module
bottom. Do not replace it with long-class imports solely to satisfy Pylance.
The same protection applies to `base.py` publishing local `s` and `api.py`
publishing the package operational alias.

### R12: MRO composition

Integration projects compose namespaces via inheritance, not name concatenation.

### R13: Library abstraction boundaries

Bridge external libs (pydantic, structlog, etc.) through `flext_core`. No direct framework imports in consumers.
