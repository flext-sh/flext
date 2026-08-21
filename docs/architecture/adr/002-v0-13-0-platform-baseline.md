# ADR-002: v0.13.0 Platform Baseline

<!-- TOC START -->
- [Status](#status)
- [Context](#context)
- [Decision](#decision)
  - [Public Class Naming](#public-class-naming)
  - [Dependency Injection](#dependency-injection)
  - [Extension Storage](#extension-storage)
  - [Public Runtime Surface](#public-runtime-surface)
  - [Workspace Taxonomy](#workspace-taxonomy)
- [Consequences](#consequences)
  - [Positive Consequences](#positive-consequences)
  - [Negative Consequences](#negative-consequences)
- [Alternatives Considered](#alternatives-considered)
- [Implementation Notes](#implementation-notes)
- [References](#references)
<!-- TOC END -->

## Status

Accepted

## Context

The workspace has accumulated a set of architectural problems that now block coherent platform evolution.

The recurring issues are:

- hybrid registries that mix handler registration and plugin storage
- hidden DI spread across runtime helpers, containers, contexts, services, decorators, and mixins
- public mixin sprawl where cross-cutting behavior has become a catch-all public abstraction
- inconsistent naming across files, classes, tests, examples, and scripts
- unstable documentation where old architecture narratives conflict with current and target direction

These issues already appear across `flext-core` and are amplified in downstream FLEXT packages such as `flext-ldif` ,
`flext-auth` , `flext-api` , and `flext-cli` .

## Decision

We will adopt the `0.13.0` platform baseline defined in `docs/architecture/baseline-v0.13.0.md`.

### Public Class Naming

We will use simple direct public class names in the platform and in downstream projects.

We will not use:

- composed architecture-heavy names such as `RuntimeKernel`
- public nested namespaces such as `Something.DI`
- generic umbrella names such as `Registry` when the role is actually catalog, dispatcher, or handler

### Dependency Injection

We will make DI explicit through four public layers:

- `FlextDi`
- `FlextContainer`
- `s`
- `u`

Application code must not touch `dependency_injector` directly.

### Extension Storage

We will replace the generic public registry concept with explicit typed extension storage:

- `FlextCatalog` replaces extension registries
- `FlextDispatcher` owns handler registration and dispatch
- project services and facades own extension invocation

`FlextRegistry` is removed from the forward public architecture.

### Public Runtime Surface

We will keep a small direct runtime surface:

- `FlextRuntime`
- `FlextDi`
- `FlextLogger`
- `FlextContext`
- `FlextContainer`
- `s`
- `FlextDispatcher`
- `FlextHandler`
- `FlextCatalog`
- `d`

`x` is removed from the forward public architecture.

### Workspace Taxonomy

We will standardize the workspace layout for:

- tests
- examples
- scripts
- project-local extension naming

The baseline applies to FLEXT platform packages, domain packages, integrations, and future FLEXT packages.

Workspace execution uses one lifecycle owner: Gas Town. Make remains the
generated build, generation, validation, and release control plane. It does not
own worker lanes, worktrees, pull-request submission, or handoff.

## Consequences

### Positive Consequences

- DI becomes discoverable, auditable, and teachable
- extension storage and handler dispatch stop competing for the same abstraction
- project naming becomes predictable for maintainers and consumers
- documentation can become stable enough to support enforcement

### Negative Consequences

- this is a hard cut with no compatibility layer
- public names, files, and methods will change across the workspace
- documentation and enforcement must move together with the implementation

## Alternatives Considered

- Keep the current hybrid `FlextRegistry`
  - rejected because it keeps CQRS and extension storage coupled
- Keep hidden DI and only add more guidelines
  - rejected because the current hidden bootstrap is the source of repeated ambiguity
- Keep `x` public and try to prune it incrementally
  - rejected because the abstraction itself is the source of leakage
- Add compatibility aliases and parallel architecture layers
  - rejected because the workspace already suffers from duplicate narratives and duplicate entry points

## Implementation Notes

- The baseline is implemented through:
  - `docs/architecture/baseline-v0.13.0.md`
  - `docs/guides/migration-to-v0.13.0.md`
- Enforcement must follow the doc package:
  - guards in `flext-infra`
  - taxonomy checks
  - public API checks
  - import direction checks
- Non-FLEXT directories in the same repository are out of scope for the root portal and must be documented locally.

## References

- [FLEXT Workspace Baseline v0.13.0](../baseline-v0.13.0.md)
- [Migration to v0.13.0](../../guides/migration-to-v0.13.0.md)
- [ADR-001: Railway-Oriented Programming with r[T]](./001-railway-oriented-programming.md)
