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
- **C:** Inherit `FlextConstants`/`FlextProtocols` for extension
- **D:** Integration projects inherit parent facade (e.g., `FlextMeltanoModels, FlextDbOracleModels`), never `FlextModels` directly
- **E:** Naming: `Flext<Tap|Target|Dbt><Domain><Models|Constants|Types|Utilities|Protocols>`

### R4F: MRO parent import matrix

| File | `m`/`u` source | others |
|------|----------------|--------|
| `models/*.py` | parent | own pkg |
| `_utilities/*.py` | parent for `u` | own pkg |
| facade files | parent for self alias | own pkg |
| services/servers/tests | own pkg | own pkg |

Parent = most advanced MRO package; flext-core uses own package.

### R5: Tier enforcement

Only import lower tiers: constants/typings → runtime → protocols → models → utilities → logging/container → dispatcher.

### R6: Private modules

`_` modules are implementation details; only their facade may import them.

### R7: Facade aliases

Each facade exposes a lowercase alias (`c`, `m`, `p`, `r`, `t`, `u`, ...).

### R8: TYPE_CHECKING

Use only for type-only symbols and `__init__.py` lazy loading. Do not hide cycles.

### R9: Ruff config

- `target-version = "py313"`
- `required-imports = ["from __future__ import annotations", "from collections.abc import Mapping, Sequence"]`
- Enforces `I001`, `I002`.

### R10: Forbidden

- `from flext_core import *`
- Relative imports
- `typing.List/Dict/Optional/Union`
- `eval`, dynamic `getattr` for architecture
- Shadowing aliases (e.g., `result` instead of `r`)

### R11: No double-assignment of facade aliases

Assign alias exactly once per facade.

### R12: MRO composition

Integration projects compose namespaces via inheritance, not name concatenation.

### R13: Library abstraction boundaries

Bridge external libs (pydantic, structlog, etc.) through `flext_core`. No direct framework imports in consumers.
