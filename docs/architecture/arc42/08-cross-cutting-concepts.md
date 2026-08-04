# 8. Cross-cutting Concepts

**Reviewed**: 2026-07-12 | **Scope**: Concepts applied uniformly across the FLEXT workspace

This chapter collects the concepts that apply to every building block instead
of a single one. They are the invariants a reviewer can assume anywhere in
any `flext-*` package.

## Table of Contents

- [8. Cross-cutting Concepts](#8-cross-cutting-concepts)
  - [8.1 Result Railway](#81-result-railway)
  - [8.2 Strict Typing](#82-strict-typing)
  - [8.3 Configuration and Settings SSOT](#83-configuration-and-settings-ssot)
  - [8.4 MRO Composition](#84-mro-composition)
  - [8.5 Pydantic 2-way Boundary](#85-pydantic-2-way-boundary)
  - [8.6 Enforcement as Data](#86-enforcement-as-data)
  - [8.7 Continuous Green](#87-continuous-green)

## 8.1 Result Railway

Every fallible application path returns `r[T]` (`FlextResult`): success
carries the typed payload, failure carries a typed error with context. Raw
exceptions are never used for control flow inside the workspace; exceptions
from external libraries are converted to `r.fail(...)` at the boundary. The
railway composes with `map`/`flat_map`-style chaining so error handling is
structural, not scattered `try/except`.

## 8.2 Strict Typing

Python 3.13+ typing, modern forms only: builtin generics, `X | Y` unions,
`type` statements, structural protocols. `Any` and bare `object` are
forbidden. Composite types use `t.*` aliases (`t.MappingOf[K, V]`,
`t.SequenceOf[T]`, …) with `| None` on the outside for nullability.
Type-checking is a gate, not a suggestion: Ruff, Pyrefly, Pyright, and Mypy
all run in CI.

## 8.3 Configuration and Settings SSOT

One access form, workspace-wide:

```python
from <namespace> import config, settings

config.<Project>.<domain>    # validated, frozen, namespaced
settings.<Project>.<domain>  # env-bound subset
```

The payload is validated exactly once while the frozen singleton is
constructed, and access never re-reads, re-validates, or passes through a
getter/proxy. This is the target configuration architecture described by
[ADR-005](../adr/005-config-settings-constants-templates-schemas-ssot.md);
individual packages adopt it as their config models land. Facets never
re-derive, hardcode, or re-read a source that `config`/`settings` already own.

## 8.4 MRO Composition

Shared behavior is composed through MRO mixins and facade inheritance, not
through helper modules, compatibility wrappers, or duplicate utility chains.
One canonical class/namespace owns each concern; consumers inherit or import
the facade. Standalone "compat" aliases, pass-through proxies, and parallel
old+new surfaces are removed in the same cycle they are replaced.

<!-- mro-wkii.17.26 (agent: codex) — make thin-domain-facade decomposition a cross-cutting MRO invariant. -->
### 8.4.1 Facade Decomposition

Composition modules remain thin regardless of layer. A `<domain>.py` facade
owns the only external import path and composes small responsibility mixins from
its adjacent `_<domain>/*.py` private package. This applies equally to facets,
operational facades, services, codegen, refactor, dependency, validation, and
tooling modules. Private package initializers use static explicit re-exports or
remain empty; generated PEP 562 lazy exports are reserved for the production
package root.

Before a decomposition, Rope provides the semantic dependency graph and SCC
evidence; `rg` and `sg` prove textual consumers, lazy maps, MRO bases, entry
points, and `__all__`. The cutover moves behavior, updates all consumers, and
deletes the superseded path atomically. Keeping `__unit__.py`, forwarding
wrappers, compatibility aliases, duplicate implementations, or parallel
old/new paths is forbidden.

## 8.5 Pydantic 2-way Boundary

Every owned payload that crosses a boundary is a Pydantic model from the `m`
facet: `model_validate(...)` on the way in, `model_dump(...)` /
`model_dump_json(...)` on the way out. The round-trip is the contract.
`dict`, `TypedDict`, `NamedTuple`, `dataclass`, and JSON-typed payloads are
forbidden as data contracts. Custom validators are the last resort, used only
when no declarative form exists; derived values are computed by a factory in
`u` and stored as plain fields, keeping models behavior-free.

## 8.6 Enforcement as Data

Static enforcement is configured data, not ad-hoc per-rule code. The target
owner is the `flext-infra` enforcement configuration and engine; this section
describes the intended architecture rather than claiming that every package or
configuration record is already present in the current checkout.

## 8.7 Continuous Green

The tree is importable and collectable at every instant, not only at mission
end. Every edit batch is validated before the next one: fresh-import smoke,
`ruff --no-fix`, typecheck, and scoped tests — all green. A red gate is an
active incident: work stops, the root cause is fixed at the source, and only
then does work continue. Fixes are forward-only; rollbacks of existing work
are forbidden.
