# 5. Building Block View

**Reviewed**: 2026-07-12 | **Scope**: Static structure of the FLEXT workspace

This chapter describes the static decomposition of the FLEXT monorepo: the
package layering, the canonical structure every `flext-*` package shares, and
the facade model that is the single public surface of each package.

## Table of Contents

- [5. Building Block View](#5-building-block-view)
  - [5.1 Workspace Level](#51-workspace-level)
  - [5.2 Package Level](#52-package-level)
  - [5.3 Facade Level](#53-facade-level)
  - [5.4 Operational Layer](#54-operational-layer)

## 5.1 Workspace Level

The workspace is a Git workspace of independently versioned `flext-*`
packages under one root. The dependency direction is one-way and enforced:

```text
flext-core ──> flext-cli ──> flext-infra
     │
     └──────> flext-tests ──> all consumer packages (flext-ldap, flext-api, ...)
```

| Package | Responsibility |
| --- | --- |
| `flext-core` | Runtime foundation: result railway (`r[T]`), settings/config base, container, logging, service runtime. Stdlib-only at runtime; never imports cli/infra. |
| `flext-cli` | Universal CLI/template/config engine: Typer model-driven commands, Jinja2 templates, YAML/JSON/CSV/TOML I/O, output rendering. |
| `flext-infra` | Workspace automation and enforcement: quality gates, docs engine, codegen, dependency sync. All static enforcement rules live as Pydantic-validated YAML data under `flext-infra/config/`. |
| `flext-tests` | Test framework: fixtures, runtime aliases (`tm/tv/tt`), `Tests*` models, pytest dispatcher for the enforcement catalog. |
| consumers | Domain packages (LDAP, LDIF, Oracle, gRPC, Meltano taps/targets, API, auth, observability, …). They import the foundation packages; the foundation never imports them. |

Cross-project imports flow consumer → foundation freely at runtime; the
reverse direction is forbidden.

## 5.2 Package Level

Every `flext-*` package has exactly one canonical structure — alternative
layouts are removed, not maintained in parallel:

```text
flext-<name>/
├── src/flext_<name>/
│   ├── **init**.py          # export-only; generated lazy-init manifest
│   ├── api.py               # thin MRO facade over the composed runtime class
│   ├── cli.py               # CLI surface (flext-cli model-driven commands)
│   ├── base.py              # service base; publishes the package `s` singleton base
│   ├── constants.py         # public `c` facade
│   ├── models.py            # public `m` facade
│   ├── protocols.py         # public `p` facade
│   ├── typings.py           # public `t` facade
│   ├── utilities.py         # public `u` facade
│   ├── config.py            # project config singleton (`config.<Ns>.*`)
│   ├── settings.py          # env-bound settings singleton (`settings.<Ns>.*`)
│   ├── services/            # thin domain facades plus private `_domain/` parts
│   └── _constants/ _models/ _protocols/ _typings/ _utilities/   # thin facet facades plus private domain parts
├── tests/                   # one unified conftest.py; unit/ integration/ e2e/; fixtures/
├── config/                  # execution parametrization (YAML, SSOT per ADR-005)
├── docs/                    # project documentation (hand-written + generated/)
└── pyproject.toml
```

`config.py` and `settings.py` are the SSOT for all parametrization: every
facet consumes `from <namespace> import config, settings` and reads the
validated namespaced singletons directly — no intermediaries, proxies, or
re-derivation.

## 5.3 Facade Level

The public surface of a package is exactly the alias set `c, m, t, p, u`
(plus operational aliases, see 5.4), each a namespace class composed by MRO:

- **`c` — constants**: defaults and invariants. Pure declaration
  (`StrEnum`/`IntEnum`/`Literal`/`Final`/immutable containers); no behavior.
- **`t` — typings**: type aliases and generic contracts. Pure declaration.
- **`p` — protocols**: structural contracts (`Protocol`). Declaration only;
  imports `m` under `TYPE_CHECKING` (reverse direction).
- **`m` — models**: Pydantic 2-way models only — `model_validate` in,
  `model_dump` out. Fields only; no methods. Imports `p` under
  `TYPE_CHECKING`.
- **`u` — utilities**: all behavior of the declaration facets. Functions and
  classes that compute, transform, and validate live here, never in `c/t/p/m`.

Import direction is strict `c → t → p → m → u` (later may import earlier at
runtime; reverse is `TYPE_CHECKING`-only). Facade owner modules extend the
upstream FLEXT facade by MRO and rebind the local alias at the bottom of the
module.

<!-- mro-wkii.17.26 (agent: codex) — document the universal thin-domain-facade building block requested by the
operator. -->
### 5.3.1 Thin Domain Facade

Every module that owns more than one implementation responsibility is split
into one thin MRO/composition facade and one matching private package of focused
parts:

```text
<layer>/
├── <domain>.py              # sole facade and external import path
└── _<domain>/
    ├── **init**.py          # static explicit re-exports or empty
    ├── <responsibility_a>.py
    └── <responsibility_b>.py
```

For example, `_utilities/rope.py` composes focused mixins from
`_utilities/_rope/*.py`. The same shape governs `c/t/p/m/u`, operational
facades, services, codegen, refactor, dependency, validation, and tooling
domains. External consumers never import private parts. PEP 562 lazy export is
generated only in the production package root; private and subdirectory
initializers are static or empty. A move updates every consumer and removes the
old path in one continuously green cutover, leaving no `**unit**.py`, wrapper,
compatibility alias, duplicate implementation, or parallel path.

## 5.4 Operational Layer

Runtime behavior is exposed through the operational aliases composed over
`flext-core`:

| Alias | Facade | Role |
| --- | --- | --- |
| `r` | `FlextResult` | Result railway `r[T]` — the only fallible-path contract |
| `e` | `FlextExceptions` | Typed exception hierarchy |
| `x` | `FlextMixins` | Reusable behavior mixins |
| `h` | `FlextHandlers` | Handler abstractions |
| `d` | `FlextDecorators` | Cross-cutting decorators |
| `s` | `FlextService` | Service base/runtime; `base.py` publishes the project service base |

`api.py` is a thin MRO facade over the composed runtime class and publishes
the package operational entry point; `services/*` hold the actual behavior,
composed by MRO. `cli.py` exposes the command surface through the `flext-cli`
model-driven engine.
