---
name: flext-patterns
description: >-
  Use inside the FLEXT workspace when creating, refactoring, reviewing, or
  validating Python 3.13+ FLEXT packages. This is the repository-local protocol
  for PEP8, KISS, SOLID, Clean Architecture, DI, SSOT, Pydantic 2, c/t/p/m/u/r/s
  facades, MRO/OO, class-owned flext-cli routing, ports/adapters, Rope-first
  refactoring, and whole-project strict gates.
license: MIT
metadata:
  version: 2.3.0
---

# FLEXT Python Strict Patterns

**RIGID PROJECT SSOT SKILL** - this file is the concrete FLEXT repository
protocol. Global `.ai-hub` skills may only route agents here; they must not
duplicate project-specific structure, package names, facade law, or validation
commands.

## First Actions

1. Claim/update the active bead. Record TARGET, IMPACT, RISK, and disjoint file
   ownership before edits.
2. Read `AGENTS.md`, `docs/GOVERNANCE.md`, submodule `AGENTS.md`, active ADRs,
   `pyproject.toml`, `src/`, `tests/`, and the relevant local skills.
3. Inspect canonical references before inventing:
   - local FLEXT packages (`flext-core`, `flext-cli`, `flext-tests`, and the
     target package);
   - the active package's own tests and architecture docs;
   - `/home/marlonsc/algar-oud-mig` when the operator requests the Algar/FLEXT
     pattern as the comparison baseline.
4. Prove real imports for the target package and its upstream FLEXT facades.
   Missing imports are blockers, not reasons to create local substitutes.
5. Map current surfaces with `rg --files src tests` and `rg` all public symbols
   before moving or deleting anything.

## Source Layout

Python product code lives only under `src/<package>/`. Tests live only under
`tests/`.

```text
src/<package>/
  __init__.py        # export-only/lazy public package surface
  api.py             # one public MRO facade
  base.py            # project service base and shared runtime/DI behavior
  cli.py             # one class-owned flext-cli adapter
  constants.py       # c facade
  typings.py         # t facade
  protocols.py       # p facade and ports
  models.py          # m facade and Pydantic 2 models
  utilities.py       # u facade and pure helpers
  result.py          # r facade/re-export when exposed
  settings.py        # Pydantic settings boundary
  services/          # one public service class per module
  adapters/          # external IO boundaries only
  _constants/        # private facade parts
  _typings/
  _protocols/
  _models/
  _utilities/
tests/
```

Forbidden active Python roots: `lib/`, `cli/` packages, `application/`,
`domain/`, `composition/`, `scripts/`, generated `typings/`, `.pyi` shim trees,
`engine.py`, `runtime.py`, and parallel old+new package paths.

## Facades And Namespaces

- Use full facade filenames: `constants.py`, `typings.py`, `protocols.py`,
  `models.py`, `utilities.py`, `result.py`, `settings.py`.
- Do not create short modules `c.py`, `t.py`, `p.py`, `m.py`, `u.py`, `r.py`.
- Each facade exposes one public facade class plus the lowercase alias at the
  bottom.
- Local symbols live under one nested namespace token:
  `c.Project.*`, `t.Project.*`, `p.Project.*`, `m.Project.*`, `u.Project.*`,
  `settings.Project.*`.
- No flat aliases such as `Thing = m.Project.Thing` or
  `VALUE = c.Project.VALUE`.
- Large facades split into private part packages and recombine by MRO.

## Import Law

Leaf code imports project root facades:

```python
from __future__ import annotations

from package import c, m, p, r, s, settings, t, u
```

Allowed owner exceptions:

- `__init__.py` may use `flext_core.lazy` for lazy exports.
- `base.py` may import `flext_core.s`, `FlextContainer`, and upstream service
  bases required by the project; when it owns the service facade it publishes
  local `s` exactly once at module bottom.
- Facade modules that extend upstream `c`, `t`, `p`, `m`, or `u` import the
  upstream short alias and use it as the MRO base, then publish the local alias
  once at module bottom.
- Facade modules may import private local mixins.
- `cli.py` may import `from flext_cli import cli` and local facades.
- Adapters may import the external package they own as a boundary.

Forbidden in leaf runtime code:

- deep imports from `_models`, `_constants`, `_protocols`, `_typings`, or
  `_utilities`;
- direct `argparse`, `click`, `typer`, `rich`, `tabulate`, `prompt_toolkit`, or
  bespoke CLI frameworks;
- direct SDK/filesystem/environment/subprocess/database imports in services;
- `Any`, broad `object`, generated `.pyi`, local stub packages, `cast`, or type
  suppressions used to pass gates.

Install maintained `types-*` packages or define narrow `Protocol`s in `p` for
untyped external boundaries.

## API, Base, And Services

`api.py` is a near-empty public MRO facade over the composed runtime class and
publishes the package operational alias:

```python
from package.services.api_runtime import ProjectApiRuntime


class ProjectApi(ProjectApiRuntime):
    """Public facade composed through cooperative MRO."""


project = ProjectApi
```

`base.py` owns shared behavior:

- `class ProjectServiceBase(s, PrivateRuntimeMixin)` with `s = ProjectServiceBase` at the bottom;
- `_container_type: ClassVar[p.ContainerType] = FlextContainer` when the project
  resolves ports through the container;
- runtime bootstrap options point at the project settings type;
- helpers are real shared behavior, not decorative empty bases.

`services/` rules:

- one public `Project<Concern>` class per module;
- service classes inherit the package `s` alias or project service base;
- fallible service methods return `p.Result[T]` and construct values with `r`;
- services depend on `p.Project.*` ports, settings, facades, or services, not on
  concrete adapters or raw IO;
- no service contains CLI parsing or external SDK/process/database code.

## CLI Law

`cli.py` is the only CLI adapter and exposes one public `<Project>Cli` class.

- `<Project>Cli` owns app creation, route registration, handlers, and
  `main(self, args: t.StrSequence | None = None) -> int` or
  `run(self, args: t.StrSequence | None = None) -> p.Result[bool]` when the
  package's existing public contract uses Result-returning CLI execution.
- Use real `flext_cli` primitives: `m.Cli.ResultCommandRoute`,
  `cli.register_result_command`, `cli.register_result_route`, and
  `cli.execute_app`.
- Handlers delegate to the public facade or services and return `p.Result[T]`.
- No module-level command handlers, no `cli = ProjectCli()` singleton, no command
  catalog resolved dynamically, no `argparse`/`click`/`typer`/`rich`.
- The only allowed process adapter is guarded module execution:

  ```python
  if __name__ == "__main__":
      cli.exit(ProjectCli().main())
  ```

Console script metadata, when present, must enter this same `cli.py` surface and
must not revive old modules or add a compatibility wrapper.

## Pydantic 2 And Settings

- Data models live under `m.Project.*` and use Pydantic 2 primitives from the
  project/FLEXT facade.
- Dynamic inputs use `Model.model_validate(...)`.
- Boundary output uses `model_dump(mode="json")`.
- Settings live in `settings.py` as typed branches, not raw `os.environ` reads in
  services.
- No raw `@dataclass`, loose `TypedDict`, mutable domain globals, or ad hoc
  `dict[str, object]` envelopes for domain data.

## Ports And Adapters

- Ports are `Protocol`s under `p.Project.*`.
- Concrete IO lives only in `adapters/`, one public adapter class per module.
- Filesystem, environment, subprocess, network, database, parser, and SDK calls
  are adapter concerns.
- Adapters translate external exceptions once into `p.Result[T]`.
- Services resolve adapters through DI/container or receive a protocol instance.
- No fake success, sentinel `None`, boolean failure, fallback path, retry mask,
  or hidden exception demotion.

## Result Flow

- Every fallible operation returns `p.Result[T]`.
- Use `r[T].ok(...)`, `r[T].fail(...)`, `r.safe`,
  `r.create_from_callable(...)`, `.map`, `.flat_map`, and `.tap`.
- Do not use `r.ok(None)`; create a typed model or sentinel success value.
- Preserve root causes with `raise ... from exc` or by attaching the exception to
  the Result boundary.

## Flext-Infra Refactor Engine Rule

In `flext-infra`, structural rewrite behavior is Rope-first. Use the repository
Rope utilities, Rope services, and mnemonic service surfaces for source
navigation, symbol ownership, moves, renames, imports, and rewrite application.
AST or regular-expression rewrite paths are defects to migrate, not legacy paths
to preserve. Do not add, keep, or bless AST/regex structural logic in
`flext-infra`; migrate the implementation to the Rope layer and fail loud when
the Rope owner cannot prove the rewrite.

## Refactor Loop

1. Work in batches of at most five files.
2. Update every importer/caller/config/test/doc reference in the same batch for
   public/facade moves.
3. Remove superseded code in the same green change. No shim, fallback,
   compatibility path, TODO, suppression, or public old+new coexistence.
4. Accept concurrent/shared work as current truth. Never rollback, reset,
   restore, stash, clean, or revert another agent's work.
5. Refactor net LOC should trend negative unless the bead explicitly records a
   required structural split and the legacy deletion plan.

## Gate Contract

After every changed-file batch, run the target project's real gates:

```bash
python -c "import package; print('package-import-ok')"
ruff check src tests --no-fix
ruff format --check src tests
pyrefly check src tests
mypy src tests --show-error-codes
pyright src tests
pytest tests -q
git diff --check
```

For CLI packages, run the real CLI smoke (`python -m package.cli --help` or the
declared script). For broad refactors, also run coverage and the project-native
check/test surfaces declared by that repository.

For this monorepo, prefer native project gates:

```bash
make check PROJECT=<project> CHECK_GATES=lint,format,pyrefly,mypy,pyright
make test PROJECT=<project> MATCH=<scope>
```

Do not claim green from a narrow check when the requirement is project-wide.

## Delegation Prompt Contract

Every subagent/MCP prompt for FLEXT work must include:

```text
Supreme Rule: absolute truth only, with command + exit code + decisive output.
Supreme Law: root-cause only; no bypass, fallback, shim, compat, suppression,
stub, hardcode, generated pyi, Any/cast escape hatch, or old+new coexistence.
R18: after each <=5-file batch, import smoke + ruff --no-fix + pyrefly +
pyright + mypy + scoped tests must be green; public/facade moves update every
consumer in the same batch.
Fix-forward only: accept current tree and other agents' work; never
rollback/restore/reset/stash/clean/revert.
Owned paths: <exact files/directories>.
Exact validation commands: <project-wide commands from the Gate Contract>.
```
