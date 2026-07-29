---
name: flext-architecture-layers
description: 'Use when assigning or moving flext-core runtime responsibilities, reviewing cross-package dependencies, or separating DI, context, dispatch, catalogs, handlers, and bootstrap behavior.'
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Architecture Layers

The accepted v0.13 baseline is the target architecture, not proof that every package
already conforms. Inspect live definitions and consumers before changing code.

## Responsibility matrix

| Owner | Owns | Must not own |
| --- | --- | --- |
| `FlextRuntime` | normalization and validation | DI, container/logger creation, bootstrap |
| `FlextDi` | dependency graph and framework bridge | orchestration, selection, extension storage |
| `FlextContainer` | scoped dependency storage/resolution | dispatch, catalogs, context orchestration |
| `FlextContext` | execution values and metadata | service location, container ownership |
| `FlextLogger` | structured logging and context binding | DI creation, runtime inheritance |
| `s` | settings/context/container/runtime bootstrap | registries, plugin storage, compatibility APIs |
| `FlextDispatcher` | message dispatch and handler registration | extension storage, DI, bootstrap |
| `FlextHandler` | one handler's validation/execution | batch registries or plugin storage |
| `FlextCatalog` | typed extension storage | dispatch or extension invocation |
| `d` | narrow automation decorators | hidden runtime/container creation |

## Workflow

1. Identify the live owner, target baseline owner, exports, and direct consumers.
2. Classify each behavior against the responsibility matrix and explicit exclusions.
3. Record the hard-cut path when live and target owners differ; do not add an alias.
4. Update the owner, public exports, and required consumers in one importable slice.
5. Run boundary checks plus owner and direct-consumer type/tests.

## Dependency invariants

- `c/t/p/m/u` never import `api.py`, `base.py`, services, or project application facades.
- Application code never imports `dependency_injector` or private `flext_core` modules.
- `FlextDi` builds, `FlextContainer` stores/resolves, `s` bootstraps, and `u` exposes
  flat consumption helpers; `FlextRuntime` is not a DI shortcut.
- `FlextCatalog` stores extensions; project services select and invoke them;
  `FlextDispatcher` registers handlers and dispatches messages.
- The public `x` bucket and generic `FlextRegistry` are not forward architecture.

## References

- [`docs/architecture/baseline-v0.13.0.md`](../../../docs/architecture/baseline-v0.13.0.md)
- [`docs/architecture/adr/002-v0-13-0-platform-baseline.md`](../../../docs/architecture/adr/002-v0-13-0-platform-baseline.md)
- [`rules/ban-private-module-import.yml`](rules/ban-private-module-import.yml)
