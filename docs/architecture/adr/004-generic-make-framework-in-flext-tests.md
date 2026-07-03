# ADR-004 — Generic Make Framework Owned by `flext-tests`

- **Status:** Accepted
- **Date:** 2026-06-28
- **Scope:** root `Makefile`, `workspace_custom.mk`, `scripts/dispatch.py`,
  `scripts/cmd/**`, `flext-tests`, and `flext-infra` Makefile generation.
- **Supersedes:** Make registry logic owned directly by `scripts/lib/parsing.py`
  or by `flext-infra` constants/templates.

## Context

FLEXT uses promoted Make verbs backed by `scripts/cmd/<verb>/<what>.py` files
with `# /// flext-command` TOML headers. The first migration attempt duplicated
that contract in script-local dataclasses and a `flext_tests.make` package. That
violated the FLEXT namespace model because it bypassed the public `c/m/t/u`
facades and created a second source of truth for command metadata.

The operator also clarified that the generic Make framework must be reusable by
any workspace. Therefore `flext-infra` can generate FLEXT workspace artifacts,
but it must not own the generic command registry library.

## Decision

- `flext-tests` owns the generic Make command framework.
- Public access goes through canonical facades:
  - `c.Tests.MAKE_*` for constants.
  - `t.Tests.MakeToml*` for TOML/header typing.
  - `m.Tests.Make*` for Pydantic command, registry, and probe models.
  - `u.Tests.make_*` for discovery, parsing, validation, and help rendering.
- `scripts/lib` is a CLI adapter only. Its modules expose one namespace class
  each (`CommandRegistry`, `CommandRenderer`, `CommandExecution`,
  `SurfaceValidator`, and `CommandCli`), and `scripts.dispatch.Dispatch` is the
  public entrypoint namespace consumed by promoted command scripts.
- `flext-tests/src/flext_tests/_utilities` keeps the Make domain split by
  responsibility: `make_parsing`, `make_contract`, `make_registry`, and
  `make_rendering`. The composed public facade remains `u.Tests.make_*`.
- Surface probes are isolated in `scripts.lib.surface_probes.SurfaceProbeRunner`
  so static Makefile validation is not coupled to in-process route execution.
- `flext-infra` remains a consumer that renders/syncs the root Makefile from
  templates. It does not discover undeclared projects by dependency heuristics.
- The root `Makefile` public verbs are thin wrappers. They call
  `uv run --all-packages python -m scripts.dispatch <verb>` through the
  generated `FLEXT_MAKE_DISPATCH` variable and do not contain `WHAT` `case`
  catalogs.
- Heavy shell recipes remain private Make targets such as `_check_default`,
  `_test_default`, `_docs`, and `_clean_default`. Promoted command metadata may
  point to those private targets with `target = "..."`.
- A promoted command that declares `target = "..."` is metadata-only: no
  executable Python body may appear after the `flext-command` header. The
  generic `flext-tests` Make contract validates this so root scripts stay thin.
- Commands that mutate only for specific parameter values declare those
  predicates with `mutates_when`; the generic `flext-tests` registry validates
  the referenced params and renders them as conditional mutation in help.
- Governance/read-only shell sequences also go through private targets, for
  example `_status` and `_coordination`, rather than duplicating process lists
  in promoted scripts.
- `make docs DOCS_PHASE=<phase>` is a first-class registry-backed public verb.
  `make build WHAT=docs` remains a build-domain route to the same private
  `_docs` recipe.
- `FLEXT_MAKE_DISPATCH` is intentionally distinct from hub wrapper variables
  such as `WORKSPACE_DISPATCH` so the optional `workspace_custom.mk` include
  cannot override the FLEXT command path. It forwards declared workspace
  variables consumed by promoted commands, including the generated `PR_BRANCH`.
- Workspace project inventory is computed only from declared sources:
  `.gitmodules`, `tool.flext.workspace.members`, and
  `tool.uv.workspace.members`.
- `flext-infra check --what <gate>` is generic workspace tooling. When no
  explicit `--projects` value is provided, it calculates the project list from
  the declared workspace inventory above. A caller that needs a smaller scope
  must pass that scope explicitly.
- The root `.pre-commit-config.yaml` is a tracked generated artifact owned by
  `flext-infra` sync. Its hooks call
  `uv run --all-packages python -m flext_infra` for boundary, LOC cap, and
  manual-command validation; hooks must not call ad-hoc scripts or direct tool
  binaries.
- Superseded Make targets are removed from the active surface.
  Their removed body can be retained only under ignored `legado/` for local
  audit.
- `make test` keeps coverage enabled for full project runs. Focused runs
  selected by `FILE`, `FILES`, or `MATCH` omit `--cov` because their coverage
  percentage is not a project quality signal.

## Consequences

- The Make registry can be reused by any workspace that depends on
  `flext-tests`, not only this FLEXT monorepo.
- The active Makefile no longer attaches top-level projects just because their
  `pyproject.toml` depends on `flext-core`.
- External project names are not part of the workspace catalog, docs, templates,
  or promoted command helpers.
- Workspace pre-commit validation is reproducible in any declared workspace
  because hook project scope is computed from workspace metadata, not from
  hardcoded project names.
- Mutation remains explicit: command metadata must declare required `APPLY` for
  mutating commands or `mutates_when` predicates for conditional mutation, and
  the CLI boundary converts failed validations to exit 2.
- Static Make validation now checks that every public registry verb delegates to
  the dispatcher wrapper and that every declared private target exists. It no
  longer accepts or requires `WHAT` `case` blocks in the Makefile.

## Verification

- `u.Tests.make_discover(Path("scripts/cmd"))` returns a valid registry.
- `scripts.dispatch.Dispatch.discover()` delegates to `flext-tests` and exposes
  the same promoted verbs.
- `rg` finds no removed project-inventory variable names, heuristic
  undeclared-project text, or removed project names in the active workspace
  surface. Declared `.gitmodules` submodules remain canonical workspace
  inventory, not undeclared-project discovery.
- `uv run --all-packages python -m flext_infra check --what boundary` and
  `uv run --all-packages python -m flext_infra check --what loc-cap` must pass
  without requiring hardcoded project names.
- `pre-commit run --config .pre-commit-config.yaml --all-files` must execute
  only the generated `flext_infra` hooks.
- `make help`, `make makefile WHAT=all`, `make check WHAT=help`,
  `make test PROJECT=flext-tests MATCH=<existing-test>`, and dispatcher surface
  validation must pass before closing the migration.
