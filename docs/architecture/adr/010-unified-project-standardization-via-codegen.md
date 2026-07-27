# ADR-010 — Unified project standardization (Make, scripts, tests, structure) via flext-infra codegen and flext-tests

- **Status:** Accepted (planning) — targets the `0.20.0-dev` line
- **Date:** 2026-07-18
- **Target line:** FLEXT `0.20.0-dev` (early development and planning). This is a
  forward standardization contract; it does not retro-fit the `0.12.0-dev`
  release line.
- **Scope:** One common, generated base for every project the workspace
  coordinates — root workspace, internal FLEXT packages, loose internal projects
  (treated as independent), and external/independent applications (`dcdoc`,
  DataOP, DcBackup) — covering Make verbs, scripts, tests, `.venv`/mise/direnv
  setup, `pyproject.toml`, package `**init**.py` facades, directory layout, and
  canonical module/class/prefix naming for `src`, `tests`, `examples`, `scripts`.
- **Tracking:** ecosystem-standardization epic and children (labelled
  `branch:0.20.0-dev`).
- **Complements:** ADR-003 (topology/profiles), ADR-004 (Make/codegen SSOT
  ownership), ADR-005 (config/settings/constants/templates/schemas SSOT and
  facade layering), ADR-007 (operational kernel/CLI/transactional conform),
  ADR-008 (neutral consumer boundaries), ADR-009 (ecosystem coordination).

This ADR does not create a new owner. It unifies and hardens the existing
`flext-infra codegen` pipeline (SSOT `codegen.yaml` with `tooling.yaml`) and the
`flext-tests` shared base, so one generated base works for every project forever.

## Context

The workspace already has the right owners:

- `flext-infra codegen conform` is the sole conformance/generation interface
  (ADR-004), rendering managed files from `codegen.yaml`/`tooling.yaml` and the
  templates under `flext_infra/templates/` (`base_verbs.mk.j2`, `base_venv.mk.j2`,
  `project/base/{Makefile,pyproject.toml,.mise.toml,python-version,custom.mk}.j2`,
  `module_skeleton.py.j2`, `static_package_init.py.j2`, `lazy_init_root.py.j2`).
- `flext-tests` owns the shared test base and generic Make test behavior.
- ADR-005 fixes facade layering `c -> t -> p -> m -> u` and the one-owner rule
  for `constants.py`/`utilities.py`/`api.py`/`base.py`/`_settings.py`/`_config.py`
  and their `_constants/*`, `_utilities/*` private namespaces.

What is missing is not another tool. It is three things: a single validated standard that
every project — including loose internal projects and external applications — is
measured against; a validation-first rollout that reports drift before it
rewrites; and enforcement so the base cannot silently diverge again.

## Decision

Adopt one generated, enforced standardization base owned by `flext-infra`
codegen + `flext-tests`, applied to every project through three ordered phases.

### 1. Single standardization surface (SSOT)

The standard is data, not prose. It lives only in:

- `flext-infra/.../config/codegen.yaml` — `toolchain`, `profiles`, `make.verbs`,
  `managed_files`, `scaffold`, `templates`, `repositories`, `workspaces`.
- `flext-infra/.../config/tooling.yaml` — tool versions and tool config
  (ruff, pyrefly, pyright, mypy, pytest) rendered into `pyproject.toml`.
- `flext-tests` — shared fixtures, `conftest` base, and generic test verbs.

No project hand-maintains these facts. Any per-project need is expressed through
validated `custom.mk` handlers (ADR-004) or declared config, never a fork of the
base.

### 2. Common verb surface for every project

Every project — root, member, loose internal (independent), and external —
exposes the same public Make verbs from `base_verbs.mk`: `help`, `boot`,
`build`, `check`, `fmt`, `scan`, `docs`, `docs-serve`, `test`, `val`, and
`fix-enforcement`, plus the operational verbs defined by ADR-004. Loose internal
projects use the `standalone` profile and behave exactly like independent
projects: they own only themselves and never inspect neighbors (ADR-003).

`setup`/`boot` provisions the identical environment everywhere: mise-pinned
Python `3.13` and uv `0.9.21`, `.venv` via uv, direnv (`.envrc`), and
`pyproject.toml`/`.mise.toml`/`.python-version` rendered from the toolchain SSOT.

### 3. Canonical structure, facades, and naming (measured, then enforced)

The generated base fixes one structure for `src`, `tests`, `examples`,
`scripts`:

- Package facades: `constants.py`, `typings.py`, `protocols.py`, `models.py`,
  `utilities.py`, `settings.py`, `config.py`, exposing `c/t/p/m/u` (+ operational
  `r/e/x/h/d/s`); private declarations in `_constants/*`, `_typings/*`,
  `_protocols/*`, `_models/*`, `_utilities/*`, `_settings.py`, `_config.py`.
- Composition: `api.py` is the thin MRO facade; `base.py` holds the shared MRO
  base and Result helpers; `cli.py` holds declarative routes.
- `**init**.py` are generated from `static_package_init.py.j2` /
  `lazy_init_root.py.j2` — never hand-written re-export sprawl.
- Naming is one scheme, rendered/validated by codegen: class prefix per project
  namespace (e.g. `Flext<Project>`, `DataOP<Concern>`, `DcBackup<Concern>`,
  `Dcdoc<Verb>Service`), sub-prefixes per concern, canonical subdirectory names,
  and module names matching the facet they own.

Naming and structure are first reported as drift, then rewritten, then enforced
(phases below). No parallel/legacy structural branch survives a green cycle.

### 3a. Namespaced runtime directories via `settings`

Every project resolves its filesystem roots only through `settings`, never
through ad-hoc `Path.home()`/`os.environ` derivations. `flext-core`
`FlextSettings` (layer-0) exposes five XDG-aware directories:

| Field | Linux default | Purpose |
| --- | --- | --- |
| `work_dir` | `$XDG_CACHE_HOME` or `~/.cache/<ns>` | scratch/cache |
| `data_dir` | `$XDG_DATA_HOME` or `~/.local/share/<ns>` | durable data |
| `config_dir` | `$XDG_CONFIG_HOME` or `~/.config/<ns>` | configuration |
| `state_dir` | `$XDG_STATE_HOME` or `~/.local/state/<ns>` | state |
| `runtime_dir` | `$XDG_RUNTIME_DIR/<ns>` or `<work_dir>/run` | ephemeral sockets/PIDs |

macOS and Windows map to their native equivalents (`~/Library/...`,
`%LOCALAPPDATA%`/`%APPDATA%`). Consumers read `settings.data_dir` etc.; deriving
these paths by hand is drift that Phase 3 enforcement rejects.

**`<ns>` is the consuming application's namespace, not the library's.** The
segment `<ns>` MUST be the namespace of the running application — the project
that uses `flext-core` as its entrypoint — and is shared by every library and
function call at runtime. When `flext-tap-oracle` runs, all directories are
`~/.cache/flext-tap-oracle/…`, `~/.config/flext-tap-oracle/…`, etc., even when a
`flext-cli`, `flext-meltano`, or `flext-core` function resolves a path
internally. A library MUST NEVER use its own name (`flext-cli`) for the
directory segment; it uses the running app's namespace.

**Resolution rule (owned by `flext-core` `FlextSettings`).** Two things stay
separate:

- Normal settings fields keep the per-subclass namespaced pattern (each project
  reads its own `settings` singleton and its own namespaced sections).
- The directory properties (`cache_dir`, `work_dir`, `data_dir`, `config_dir`,
  `state_dir`, `runtime_dir`) are NOT per-subclass. They ALWAYS resolve from the
  **root project namespace held by the settings root singleton** — a single
  shared source — never from the `env_prefix` of the subclass that happens to
  access them. A `flext-cli`/`flext-meltano`/`flext-core` call under application
  X therefore returns `~/.<root>/X/…`; a library MUST NEVER use its own name for
  the directory segment.

Namespace precedence for that root value, registration being **optional**:

1. `FlextSettings.set_app_namespace("flext-tap-oracle")` — an entrypoint may
   declare the application identity once (first-wins).
2. `FLEXT_APP_NAMESPACE` — environment override when no bootstrap ran.
3. **Root project namespace (default)** — otherwise the running project's own
   namespace prevails; registration is never mandatory.

Per-application overrides use `<APPNS>_<NAME>_DIR`
(e.g. `FLEXT_TAP_ORACLE_WORK_DIR`); namespaces that are not a single safe path
segment are rejected.

**Implementation ownership.** The `flext-core` `FlextSettings` change that binds
the `*_dir` resolution to the settings root singleton is implemented by the
`flext-core` maintenance lane, not by this standardization work. This ADR only
fixes the contract every consumer must follow; consumer adoption and enforcement
are tracked in Beads.

### 4. Three ordered phases (same strategy as ADR-020/008/009)

1. **Validation-first.** `flext-infra codegen conform --mode check` plus a
   standardization audit reports every drift (missing verbs, non-standard
   layout, wrong facade/`**init**`, naming violations, toolchain/pyproject
   drift, non-standard tests/scripts/examples) across all projects, with zero
   writes. Output is evidence, not a rewrite.
2. **Refactoring.** `flext-infra codegen conform --mode apply` (and the
   `flext-tests` base) migrates each project to the standard in bounded,
   ownership-scoped batches, deletion-first (ADR-005 §5), one cut per concern,
   no compatibility shim, each batch validated (`ruff`/`pyrefly`/`pytest`).
3. **Enforcement.** The standard becomes declarative enforcement data in
   `flext-infra/config/enforcement/*.yaml` evaluated by the rope-semantic engine
   (ADR-005 §6), so drift fails a gate instead of returning silently. Every
   project runs the same `check`/`val` gates.

### 5. Applicability to independent and external projects

Loose internal projects and external applications (`dcdoc`, DataOP, DcBackup)
consume the same generated base through the `standalone` profile and their own
`flext-infra` invocation. This never changes the dependency law of ADR-008/009:
`flext-infra` is invoked as external tooling and never imported by an
application, and no `flext-*` package depends on an application. Standardization
is generation and validation, not runtime composition.

## Consequences

- One base setup (venv/mise/direnv/pyproject) and one verb surface work in every
  project, forever, from a single SSOT.
- Structure, facades, `**init**.py`, and naming are generated and enforced, not
  re-invented per project.
- Drift is caught before it lands; the base cannot silently fork again.
- Independent and external projects get the same standard without any reverse
  dependency.

## Verification contract

1. `flext-infra codegen conform --mode check --scope all` is green (byte-idempotent)
   on the standardized set; every managed file matches the rendered SSOT.
2. The standardization audit reports zero drift for verbs, layout, facades,
   `**init**.py`, toolchain/pyproject, and naming on enforced projects.
3. Enforcement rules exist as `flext-infra/config/enforcement/*.yaml` data and a
   naming/structure violation fails `check`/`val`.
4. `flext-tests` base yields identical generic `test` behavior across projects.
5. Independent/external projects pass the same gates with no `flext-*`
   reverse dependency (ADR-008 gate stays green).

## References

- [ADR-003 — Manifest-owned topology, profiles](003-workspace-tooling-hub-distribution.md)
- [ADR-004 — Generated Make and codegen SSOT](004-generic-make-framework-in-flext-tests.md)
- [ADR-005 — Config/settings/constants/templates/schemas SSOT](005-config-settings-constants-templates-schemas-ssot.md)
- [ADR-007 — Performance optimization of worktree transactions and mutating CLI
  commands](007-worktree-transaction-performance.md)
- [ADR-008 — Neutral consumer boundaries](008-neutral-consumer-boundaries.md)
- [ADR-009 — Ecosystem coordination](009-ecosystem-coordination-and-library-evaluation.md)
- [Ecosystem coordination](../ecosystem-coordination.md)
- SSOT: `flext-infra/src/flext_infra/config/codegen.yaml`, `tooling.yaml`;
  templates under `flext_infra/templates/`.
