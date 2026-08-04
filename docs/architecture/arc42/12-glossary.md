# 12. Glossary

<!-- TOC START -->
- [Table of Contents](#table-of-contents)
- [12.1 Structure Terms](#121-structure-terms)
- [12.2 Facade Aliases](#122-facade-aliases)
- [12.3 Runtime Terms](#123-runtime-terms)
- [12.4 Process Terms](#124-process-terms)
<!-- TOC END -->

**Reviewed**: 2026-07-12 | **Scope**: Canonical terms used across FLEXT documentation

Terms are defined once here; other documents link instead of redefining.

## Table of Contents

- [12. Glossary](#12-glossary)
  - [12.1 Structure Terms](#121-structure-terms)
  - [12.2 Facade Aliases](#122-facade-aliases)
  - [12.3 Runtime Terms](#123-runtime-terms)
  - [12.4 Process Terms](#124-process-terms)

## 12.1 Structure Terms

| Term | Definition |
| --- | --- |
| **Workspace** | The FLEXT monorepo: one Git workspace of independently versioned `flext-*` packages. |
| **Package** | A single `flext-*` project with its own `pyproject.toml`, version, and release cycle. |
| **Facet** | One of the canonical declaration surfaces of a package (`c`, `t`, `p`, `m`, config, settings). Facets are pure declaration — no behavior. |
| **Private facet** | The `_constants/`, `_models/`, `_protocols/`, `_typings/`, `_utilities/` modules behind a public facade. |
| **SSOT** | Single Source of Truth — exactly one canonical owner per concern; everything else links or consumes. |
| **Lane** | A disjoint file-ownership scope claimed by one agent for parallel work, tracked in Beads. |

## 12.2 Facade Aliases

| Alias | Facade | Content |
| --- | --- | --- |
| `c` | constants | Defaults and invariants (`StrEnum`/`IntEnum`/`Literal`/`Final`). |
| `t` | typings | Type aliases and generic contracts. |
| `p` | protocols | Structural `Protocol` contracts. |
| `m` | models | Pydantic 2-way models — fields only, no methods. |
| `u` | utilities | All behavior of the declaration facets. |
| `r` | result | `FlextResult` railway — the fallible-path contract `r[T]`. |
| `e` | exceptions | Typed exception hierarchy. |
| `x` | mixins | Reusable behavior mixins. |
| `h` | handlers | Handler abstractions. |
| `d` | decorators | Cross-cutting decorators. |
| `s` | service | Service base/runtime; `base.py` publishes the project service base. |

## 12.3 Runtime Terms

| Term | Definition |
| --- | --- |
| **Result railway** | Error handling via `r[T]` composition instead of exceptions for control flow. |
| **Pydantic 2-way** | Payload contract: `model_validate(...)` in, `model_dump(...)` out; the round-trip is the contract. |
| **Config singleton** | The frozen, validated `config.<Project>.*` object built once at composition time. |
| **Settings singleton** | The env-bound `settings.<Project>.*` object; the settings-bound subset of configuration. |
| **MRO composition** | Behavior shared through class inheritance order (mixins + facades), never through helper modules. |
| **Code community** | A cluster of related code entities detected by the code-review-graph (Leiden algorithm); used for architecture pages and review scoping. |
| **Execution flow** | A call chain from an entry point (HTTP handler, CLI command, test) used for impact analysis. |

## 12.4 Process Terms

| Term | Definition |
| --- | --- |
| **Bead** | A unit of tracked work in the `bd` ledger (epic, task, bug); the mandatory work record for multi-agent sessions. |
| **Gate** | A quality check that must be green before work lands (lint, typecheck, tests, docs audit). |
| **Docs phase** | One stage of the docs pipeline: `generate` (mutating, requires `APPLY=Y`), `build` (strict), `validate`, `audit`. |
| **Generated surface** | Files under `docs/**/generated/` reproduced by the engine; read-only for humans. |
| **Continuous green** | The tree stays importable/collectable at every instant; a red gate is an active incident. |
| **Fix-forward** | Defects are corrected at the source going forward; rollback of existing work is forbidden. |
| **ADR** | Architecture Decision Record — durable decisions under `docs/architecture/adr/`. |
