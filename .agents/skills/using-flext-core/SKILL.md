---
name: using-flext-core
description: 'Use when consuming flext-core structural facades, typed results, settings, DI, runtime context, logging, dispatch, handlers, catalogs, or bootstrap services.'
license: MIT
metadata:
  version: 2.0.0
---
# Using flext-core

The v0.13 architecture is an accepted migration target. Confirm the live API before
editing consumers; never simulate the target with compatibility wrappers.

## Public surfaces

| Surface | Contract |
| --- | --- |
| `c/t/p/m/u` | structural constants, types, protocols, models, and utilities |
| `e` | structured error taxonomy |
| `r[T]` | typed success/failure flow |
| `FlextSettings` | typed configuration root |
| `FlextDi` | dependency-injector bridge and graph wiring |
| `FlextContainer` | scoped dependency store and resolver |
| `FlextContext` | execution values and metadata |
| `FlextRuntime` | normalization and validation only |
| `FlextLogger` | structured logging and context binding |
| `s` | runtime bootstrapper |
| `FlextDispatcher` | dispatch and handler registration |
| `FlextHandler` | individual handler contract |
| `FlextCatalog` | typed extension storage |
| `d` | narrow automation decorators |

`x` and `FlextRegistry` are removed from the forward public architecture. Do not add
new dependencies on them. Structural facades must not absorb operational behavior.

## Workflow

1. Classify the concern using the public-surface table.
2. Inspect the live export and accepted target contract.
3. Use the public facade, protocol, or runtime class; never a private module or
   third-party framework hidden behind flext-core.
4. Return `r[T]` from fallible application work and translate external failures at
   the adapter boundary.
5. Validate the consumer and any changed owner with import, type, and focused tests.

## Result example

```python
from __future__ import annotations

from flext_core import r


def safe_divide(dividend: float, divisor: float) -> r[float]:
    if divisor == 0:
        return r[float].fail("division_by_zero")
    return r.ok(dividend / divisor)
```

Do not replace a failure with `None`, unwrap a result in application flow, or catch a
broad exception merely to return success.

## DI and extensions

- Application code consumes injected dependencies or `u.get_*`/`u.require_*` helpers.
- Only `FlextDi` bridges `dependency_injector`.
- `FlextContainer` resolves dependencies; it does not dispatch messages.
- `FlextCatalog` stores extensions; services choose and invoke them.
- `FlextDispatcher` registers handlers and dispatches commands, queries, and events.

## References

- [`flext-architecture-layers`](../flext-architecture-layers/SKILL.md)
- [`lib-returns`](../lib-returns/SKILL.md)
- [`lib-dependency-injector`](../lib-dependency-injector/SKILL.md)
- [`docs/architecture/baseline-v0.13.0.md`](../../../docs/architecture/baseline-v0.13.0.md)
