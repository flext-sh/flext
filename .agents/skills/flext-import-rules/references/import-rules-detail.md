# FLEXT import routing examples

Load this reference only after identifying the declaration or runtime owner.
Replace `flext_plugin` with the package proved by the target workspace.

## Consumer imports

Import shared and project-owned declarations from public roots:

```python
from flext_core import c, m, p, r, t, u
from flext_plugin import config, settings
```

Do not bypass the root facade:

```python notest
from ._models import PluginSettings
from flext_plugin._utilities import PluginUtilities
from flext_core import *
```

## Facade owner

Only the local facade owner extends and republishes an upstream alias:

```python
from flext_cli import m


class FlextPluginModels(m):
    """Plugin model namespace."""


m = FlextPluginModels
```

Leaf consumers then use the local owner:

```python
from flext_plugin import m
```

Do not make each leaf reconstruct the inheritance chain or import an upstream
private implementation.

## External bridge owner

An external framework import belongs only in the package that owns its bridge.
For example, the canonical model owner may import Pydantic to declare the
validated public model; ordinary consumers retain that model object through
the owning package facade.

```python notest
# Consumer violation: the consumer invents a parallel model boundary.
from pydantic import BaseModel


class LocalPayload(BaseModel):
    value: str
```

### R8: TYPE_CHECKING and package initializers

Use `TYPE_CHECKING` only for symbols used solely in static-only positions — never a
name evaluated at runtime in an annotation (Pydantic field, PEP 526 assignment,
beartype signature, PEP 695 `type` RHS), and never to hide a reverse facade edge,
which is forbidden entirely (ADR-011) — plus the generated PEP 562 map at
the production package root. Every internal importable directory at arbitrary
depth has a generated static `__init__.py` with relative same-name re-exports of
direct sibling symbols and a sorted literal tuple `__all__`, including
`__all__ = ()` when it owns no direct export. Internal initializers never flatten
descendants and never use lazy loading. Do not hide cycles.

## Runtime versus declaration-only imports

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
