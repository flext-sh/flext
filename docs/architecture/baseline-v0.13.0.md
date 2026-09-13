# FLEXT Workspace Baseline v0.13.0

<!-- TOC START -->
- [Status](#status)
- [Purpose](#purpose)
- [Governed Scope](#governed-scope)
- [Authority](#authority)
- [Forward Public Surface](#forward-public-surface)
  - [Core Class Matrix](#core-class-matrix)
  - [Namespace Composition Classes](#namespace-composition-classes)
- [Core Class Contracts](#core-class-contracts)
  - [FlextRuntime](#flextruntime)
  - [FlextDi](#flextdi)
  - [FlextLogger](#flextlogger)
  - [FlextContext](#flextcontext)
  - [FlextContainer](#flextcontainer)
  - [s](#s)
  - [FlextDispatcher](#flextdispatcher)
  - [FlextHandler](#flexthandler)
  - [FlextCatalog](#flextcatalog)
  - [d](#d)
- [DI Baseline](#di-baseline)
- [Alias Baseline](#alias-baseline)
- [Extension Baseline](#extension-baseline)
- [Project Naming Baseline](#project-naming-baseline)
- [Workspace Taxonomy](#workspace-taxonomy)
  - [Tests](#tests)
  - [Examples](#examples)
  - [Scripts](#scripts)
- [Expansion Rules](#expansion-rules)
- [Migration Entry Points](#migration-entry-points)
- [References](#references)
<!-- TOC END -->

## Status

- Version: `0.13.0`
- Status: Accepted baseline for implementation
- Scope: Workspace-wide platform baseline

## Purpose

This document defines the FLEXT workspace platform baseline for `0.13.0`.

It replaces vague or stale architecture narratives with direct rules for:

- public class names
- class responsibilities
- dependency injection
- extension storage
- project naming
- workspace taxonomy
- migration direction

If this document conflicts with older architecture overviews, project-level architecture notes, or legacy refactoring
plans, this baseline wins until the conflicting document is migrated.

## Governed Scope

This baseline governs the FLEXT workspace by project group.

| Group                      | Projects                                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Platform core              | `flext-core`, `flext-tests`, `flext-infra`, `flext-quality`                                                               |
| Platform capabilities      | `flext-cli`, `flext-api`, `flext-auth`, `flext-web`, `flext-grpc`, `flext-observability`, `flext-plugin`, `flext-meltano` |
| Domain packages            | `flext-ldap`, `flext-ldif`, `flext-db-oracle`, `flext-oracle-wms`, `flext-oracle-oic`                                     |
| Integrations               | all `flext-tap-*`, `flext-target-*`, `flext-dbt-*` projects                                                               |
| Shared testing and tooling | `flext-tests`, `flext-infra`, `flext-quality`                                                                             |

Non-FLEXT directories that may exist in the repository are outside the root FLEXT portal and must be documented locally
in their own trees.

## Authority

This baseline governs:

- the forward public surface of `flext-core`
- the naming and file layout of workspace packages
- the vocabulary used in migration work
- the taxonomy of `tests/`, `examples/`, and `scripts/`

Per-project docs are subordinate to this baseline until each project is migrated.

## Forward Public Surface

### Core Class Matrix

| Current class     | Target class      | File                             | Role                                   | Public methods                                                                                                               | Decision                             |
| ----------------- | ----------------- | -------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| `FlextConstants`  | `FlextConstants`  | `constants.py`                   | Root constants facade                  | namespace facade only                                                                                                        | Keep                                 |
| `FlextTypes`      | `FlextTypes`      | `typings.py`                     | Root types facade                      | namespace facade only                                                                                                        | Keep                                 |
| `FlextProtocols`  | `FlextProtocols`  | `protocols.py`                   | Root protocols facade                  | namespace facade only                                                                                                        | Keep                                 |
| `FlextModels`     | `FlextModels`     | `models.py`                      | Root models facade                     | namespace facade only                                                                                                        | Keep                                 |
| `FlextUtilities`  | `FlextUtilities`  | `utilities.py`                   | Root utilities facade                  | namespace facade only                                                                                                        | Keep                                 |
| `FlextSettings`   | `FlextSettings`   | `settings.py`                    | Typed configuration root               | `shared`, `build`, `add`, `load`                                                                                             | Keep and narrow                      |
| `r`               | `r`               | `result.py`                      | Success and failure contract           | existing result surface                                                                                                      | Keep                                 |
| `e`               | `e`               | `exceptions.py`                  | Structured error taxonomy              | error models and serializers                                                                                                 | Keep and narrow                      |
| `FlextRuntime`    | `FlextRuntime`    | `runtime.py`                     | Normalization and validation           | `to_container`, `to_metadata`, `validate_many`, `ensure_utc`                                                                 | Keep, remove DI ownership            |
| none              | `FlextDi`         | `di.py`                          | Bridge to `dependency_injector`        | `build`, `add_service`, `add_factory`, `add_resource`, `bind_config`, `wire`, `unwire`                                       | Add                                  |
| `FlextLogger`     | `FlextLogger`     | `logger.py`                      | Structured logging and context binding | `get`, `bind`, `unbind`, `scope`, `clear_scope`, `from_context`                                                              | Keep, move from `loggings.py`        |
| `FlextContext`    | `FlextContext`    | `context.py`                     | Execution context only                 | `get`, `set`, `has`, `remove`, `clear`, `clone`, `merge`, `export`, `get_meta`, `set_meta`                                   | Keep and narrow                      |
| `FlextContainer`  | `FlextContainer`  | `container.py`                   | Runtime dependency store and resolver  | `shared`, `scope`, `add_service`, `add_factory`, `add_resource`, `get`, `require`, `has`, `list`, `remove`, `wire`, `unwire` | Keep and reshape                     |
| `s`               | `s`               | `service.py`                     | Runtime bootstrapper                   | `make_settings`, `make_context`, `make_container`, `make_runtime`, `run`                                                     | Keep and narrow                      |
| `FlextDispatcher` | `FlextDispatcher` | `dispatcher.py`                  | Message dispatch and handler binding   | `dispatch`, `publish`, `add`, `add_many`, `remove`, `has`, `list`, `clear`                                                   | Keep and absorb handler registration |
| `h`               | `FlextHandler`    | `handler.py`                     | Individual handler contract            | `handle`, `run`, `validate`, `can_handle`, `from_callable`                                                                   | Rename and narrow                    |
| `FlextRegistry`   | `FlextCatalog`    | `catalog.py`                     | Typed extension storage                | `add`, `add_many`, `get`, `require`, `has`, `list`, `remove`, `clear`                                                        | Replace                              |
| `d`               | `d`               | `decorators.py`                  | Automation wrappers                    | `inject`, `log`, `measure`, `scope`, `compose`, `result`, `retry`, `timeout`                                                 | Keep and narrow                      |
| `x`               | none              | removed from public architecture | legacy behavior bucket                 | none                                                                                                                         | Remove from the public platform      |
| `FlextVersion`    | `FlextVersion`    | `__version__.py`                 | package metadata only                  | metadata only                                                                                                                | Keep, not architectural              |
| `LazyNamespace`   | `LazyNamespace`   | `lazy.py`                        | export protocol only                   | internal export protocol                                                                                                     | Keep internal                        |

### Namespace Composition Classes

The workspace currently exports many family composition classes from underscored packages, including:

- `FlextConstants*`
- `FlextModels*`
- `FlextProtocols*`
- `FlextTypes*`
- `FlextUtilities*`

These classes remain valid for namespace composition and MRO assembly inside the family facades, but they are not
forward runtime primitives. The forward architecture baseline is defined by the root public classes in the matrix above.

Application and orchestration code should target:

- `FlextConstants`
- `FlextTypes`
- `FlextProtocols`
- `FlextModels`
- `FlextUtilities`
- the runtime classes in the matrix above

## Core Class Contracts

### FlextRuntime

- Role: normalization and validation only
- Ownership:
  - value normalization
  - metadata normalization
  - batch validation
  - UTC normalization
- Public methods:
  - `to_container`
  - `to_metadata`
  - `validate_many`
  - `ensure_utc`
- Explicit exclusions:
  - no DI bridge
  - no container creation
  - no logger creation
  - no bootstrap responsibilities

### FlextDi

- Role: only bridge to `dependency_injector`
- Ownership:
  - build the dependency graph
  - add service values
  - add factories
  - add resources
  - bind typed settings
  - wire and unwire targets
- Public methods:
  - `build`
  - `add_service`
  - `add_factory`
  - `add_resource`
  - `bind_config`
  - `wire`
  - `unwire`
- Explicit exclusions:
  - no service orchestration
  - no business selection logic
  - no plugin storage

### FlextLogger

- Role: structured logging and context binding
- Ownership:
  - logger retrieval
  - scoped binding
  - unbinding
  - context-aware logger creation
- Public methods:
  - `get`
  - `bind`
  - `unbind`
  - `scope`
  - `clear_scope`
  - `from_context`
- Explicit exclusions:
  - no runtime inheritance
  - no DI creation
  - no generic automation helpers

### FlextContext

- Role: execution context only
- Ownership:
  - scoped execution values
  - metadata propagation
  - cloning and merging
  - export and serialization support
- Public methods:
  - `get`
  - `set`
  - `has`
  - `remove`
  - `clear`
  - `clone`
  - `merge`
  - `export`
  - `get_meta`
  - `set_meta`
- Explicit exclusions:
  - no service location
  - no container ownership
  - no nested public service helper classes

### FlextContainer

- Role: runtime dependency store and resolver
- Ownership:
  - scoped container instances
  - service values
  - factories
  - resources
  - lookup and requirement APIs
  - wiring hooks
- Public methods:
  - `shared`
  - `scope`
  - `add_service`
  - `add_factory`
  - `add_resource`
  - `get`
  - `require`
  - `has`
  - `list`
  - `remove`
  - `wire`
  - `unwire`
- Explicit exclusions:
  - no message dispatch logic
  - no plugin catalog logic
  - no context orchestration

### s

- Role: only runtime bootstrapper
- Ownership:
  - create settings
  - create context
  - create container
  - assemble runtime state
  - expose a direct execution contract for facades and service bases
- Public methods:
  - `make_settings`
  - `make_context`
  - `make_container`
  - `make_runtime`
  - `run`
- Explicit exclusions:
  - no plugin storage
  - no handler registry duties
  - no compatibility surfaces

### FlextDispatcher

- Role: only message dispatch and handler registration
- Ownership:
  - dispatch commands and queries
  - publish events
  - register and remove handlers
  - report handler inventory
- Public methods:
  - `dispatch`
  - `publish`
  - `add`
  - `add_many`
  - `remove`
  - `has`
  - `list`
  - `clear`
- Explicit exclusions:
  - no plugin storage
  - no settings bootstrapping
  - no DI ownership

### FlextHandler

- Role: only individual handler contract and execution pipeline
- Ownership:
  - message validation
  - single-handler execution
  - capability checks
  - callable adaptation
- Public methods:
  - `handle`
  - `run`
  - `validate`
  - `can_handle`
  - `from_callable`
- Explicit exclusions:
  - no batch registry behavior
  - no plugin storage
  - no runtime bootstrap

### FlextCatalog

- Role: only typed extension storage
- Ownership:
  - add and remove extensions
  - retrieve and require extensions
  - inventory and clearing
- Public methods:
  - `add`
  - `add_many`
  - `get`
  - `require`
  - `has`
  - `list`
  - `remove`
  - `clear`
- Explicit exclusions:
  - no handler registration
  - no dispatch
  - no extension invocation pipelines

### d

- Role: only automation wrappers
- Ownership:
  - injection wrappers
  - logging wrappers
  - measurement wrappers
  - scope wrappers
  - result wrappers
  - retry and timeout wrappers
- Public methods:
  - `inject`
  - `log`
  - `measure`
  - `scope`
  - `compose`
  - `result`
  - `retry`
  - `timeout`
- Explicit exclusions:
  - no container creation shortcuts
  - no hidden runtime creation
  - no compatibility aliases such as `combined`

## DI Baseline

The `0.13.0` workspace DI model has four layers.

1. `FlextDi` builds and wires the dependency graph.
2. `FlextContainer` stores and resolves runtime dependencies.
3. `s` bootstraps settings, context, container, and runtime state.
4. `u` is the flat consumption surface used outside the bootstrap path.

Application code must not touch `dependency_injector` directly.

Application code must use:

- `settings`
- `self.context`
- `self.container`
- `self.runtime`
- `u.get_*`
- `u.require_*`

`FlextRuntime` is not part of the DI bootstrap path anymore.

## Alias Baseline

The only structural aliases are:

- `c` for constants
- `t` for types
- `p` for protocols
- `m` for models
- `u` for utilities

Rules:

- `c/t/p/m/u` never import `api.py`, `base.py`, `services/*`, or project facades and services.
- helpers belong in `u`
- orchestration belongs outside the structural aliases
- application code targets the local facade alias, not underscored internals

Operational aliases are not part of the forward structural baseline. They may continue to exist during migration, but
they must not accumulate new architectural responsibilities.

## Extension Baseline

`registry` is no longer a first-class architectural word in the forward platform.

The platform stores extensions through `FlextCatalog`.

Extension invocation logic stays in project services and facades, not in the catalog.

The required split is:

- `FlextCatalog` stores extensions
- services and facades select the extension to use
- services and facades execute the extension pipeline

This baseline intentionally removes hybrid storage classes that both keep plugins and behave like handler registries.

## Project Naming Baseline

Project-local extension classes must use direct nouns with simple names.

Required examples:

- `FlextLdifServers`
- `FlextAuthProviders`
- `FlextApiComponents`
- `FlextCliCommands`
- `FlextCliOptions`
- `FlextPlugins`

Rules:

- ban composed architecture names such as `RuntimeKernel`, `HandlerRegistry`, or similar framework-heavy labels
- ban nested public namespaces such as `FlextSomething.DI`
- prefer a single direct noun for the public class and keep architectural detail in the document, not in the class name

## Workspace Taxonomy

### Tests

The only forward test taxonomy is:

- `tests/unit/`
- `tests/integration/`
- `tests/architecture/`
- `tests/performance/`
- `tests/fixtures/`

Explicit removals:

- `examples/tests`
- `tests/examples`, except `tests/integration/examples`
- filename suffixes `_cov`, `_real`, `_smoke`

### Examples

Examples are executable public examples only.

Rules:

- use semantic filenames only, for example `config_example.py`
- keep support code in `examples/support/`
- do not keep test files inside `examples/`

Explicit removals:

- numbered example filenames such as `ex_01_*`
- numbered example filenames such as `01_basic_usage.py`
- helper models like `models/exNN.py`

### Scripts

The only forward script taxonomy is:

- `scripts/analysis/`
- `scripts/migration/`
- `scripts/validation/`
- `scripts/maintenance/`

Rules:

- scripts are automation only
- if code is reused by `src/`, `tests/`, or `examples/`, it belongs in `u` or a governed project package, not in
  `scripts/`

## Expansion Rules

New FLEXT packages must adopt this baseline from the start.

Specific rules:

- new packages must expose local `c/t/p/m/u` facades
- new packages must use direct class names and the workspace taxonomy from this baseline
- non-FLEXT projects in the same repository are not governed by this root portal

## Migration Entry Points

This baseline is implemented alongside:

- the formal decision record in [ADR-002](./adr/002-v0-13-0-platform-baseline.md)
- the practical migration guide in [Migration to v0.13.0](../guides/migration-to-v0.13.0.md)

## References

- [Architecture ADR Index](./adr/README.md)
- [Workspace Architecture Index](./README.md)
- [Migration to v0.13.0](../guides/migration-to-v0.13.0.md)
- [Workspace Documentation Portal](../index.md)
