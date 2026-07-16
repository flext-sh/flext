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

## Runtime versus declaration-only imports

Use `TYPE_CHECKING` only when the imported symbol is absent from every runtime
expression. If code instantiates, inherits, registers, dispatches, or performs
an `isinstance` check with the symbol, keep the import at runtime. Moving it
behind `TYPE_CHECKING` is a hidden-cycle bypass, not a cycle fix.
