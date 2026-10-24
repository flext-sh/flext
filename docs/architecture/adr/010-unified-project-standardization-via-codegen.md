# ADR-010 — Unified project standardization via flext-infra codegen and flext-tests

> **Amended by ADR-018** (generator declarations): its filename-to-letter tables, closed
> folder lists and advisory-gate lists are superseded; see
> [ADR-018](018-generator-declarations.md).

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
  - [1. Single standardization surface (SSOT)](#1-single-standardization-surface-ssot)
  - [2. Common verb surface for every project](#2-common-verb-surface-for-every-project)
  - [3. Canonical structure, facades, and naming (measured, then enforced)](#3-canonical-structure-facades-and-naming-measured-then-enforced)
  - [3a. Namespaced runtime directories via settings](#3a-namespaced-runtime-directories-via-settings)
  - [3b. Semantic discovery and automated rewiring](#3b-semantic-discovery-and-automated-rewiring)
  - [4. Three ordered phases (same strategy as ADR-007/008/009)](#4-three-ordered-phases-same-strategy-as-adr-007008009)
  - [5. Applicability to independent and external projects](#5-applicability-to-independent-and-external-projects)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

- **Status:** Accepted contract; consolidation and consumer runtime acceptance remain
  in progress under the active Bead.
- **Date:** 2026-07-18
- **Last updated:** 2026-10-23
- **Target line:** FLEXT `0.12.0-dev`, with `0.13.0` as the forward baseline.
- **Scope:** One common, generated base for every project the workspace coordinates —
  root workspace, internal FLEXT packages, loose internal projects (treated as
  independent), and declared independent FLEXT applications —
  covering Make verbs, scripts, tests, `.venv`/mise/direnv setup, `pyproject.toml`,
  package `**init**.py` facades, directory layout, and canonical module/class/prefix
  naming for `src`, `tests`, `examples`, `scripts`. Third-party repositories remain
  outside the FLEXT architecture boundary and retain their upstream layout and commands.
- **Tracking:** the active branch-matched Bead and its dependencies.
- **Complements:** ADR-003 (topology/profiles), ADR-004 (Make/codegen SSOT ownership),
  ADR-005 (config/settings/constants/templates/schemas SSOT and facade layering),
  ADR-007 (operational kernel/CLI/transactional conform), ADR-008 (neutral consumer
  boundaries), ADR-009 (ecosystem coordination).

This ADR does not create a new owner. It unifies and hardens the existing
`flext-infra codegen` engine (SSOT `codegen.yaml` with `tooling.yaml`) and the
`flext-tests` shared base across the declared supported profiles.

## Context

The workspace already has the right owners:

- `flext-infra` owns the shared projection planner and publisher used by generation
  and conformance (ADR-004). Packaged policy lives under
  `flext-infra/src/flext_infra/config/`; `templates.entries` declares each template
  source, destination, profile and ownership instead of a second handwritten catalog.
- `flext-tests` owns shared public fixtures; `flext-infra` owns the native suite runner
  and Make integration.
- ADR-005 fixes facade layering `c -> t -> p -> m -> u` and the one-owner rule for
  `constants.py`/`utilities.py`/`api.py`/`base.py`/`_settings.py`/`_config.py` and their
  `_constants/*`, `_utilities/*` private namespaces.

What is missing is not another tool. It is three things: a single validated standard
that every project — including loose internal projects and external applications — is
measured against; a validation-first rollout that reports drift before it rewrites; and
enforcement so the base cannot silently diverge again.

## Decision

Adopt one generated, enforced standardization base owned by `flext-infra` codegen +
`flext-tests`, applied to every project through three ordered phases.

### 1. Single standardization surface (SSOT)

The standard is data, not prose. It lives only in:

- `flext-infra/.../config/codegen.yaml` — toolchain, Make operations, typed scaffold
  policy and `templates.entries`. Managed-file views derive from that single catalog.
- `flext-infra/.../config/tooling.yaml` — tool versions and tool config (ruff, pyrefly,
  pyright, mypy, pytest) rendered into `pyproject.toml`.
- each parent's `.gitmodules` — the sole member list; each repository's own typed
  declarations — kind and genuine local deltas.
- `flext-tests` — shared fixtures and `conftest` base.

No project hand-maintains these facts. Any per-project need is expressed through
validated `custom.mk` handlers (ADR-004) or declared config, never a fork of the base.

### 2. Common verb surface for every project

For the bounded `flext-0029c` native-bootstrap task, the
[local-law exception](../../../.agents/skills/flext-law/SKILL.md#sources-generation-and-commands)
requires direct public `flext-infra` CLI diagnosis, runtime, refactoring and gates,
with Make integration last. Documentation alignment precedes worker coding and
real runtime proof precedes test changes. This does not relax the common surface
below for other work or establish implementation acceptance.

The common interface is exactly `setup`, `upg`, `gen`, `mod`, `fix`, `fmt`, `check`,
`tests`, `help`, `build` and `clean`, projected by `make help` from the typed catalog.
Each operation retains its own effect; callers do not invent selectors or aliases.
Product-specific commands stay with their declaring projects. Publication, deployment,
tags and other external effects remain explicitly triggered. Standalone FLEXT projects
own only themselves and never inspect neighbors (ADR-003).

`setup` provisions the declared toolchain, `.venv` via uv, and environment integration.
`gen` owns rendering managed `pyproject.toml`, `.mise.toml`, and `.python-version` from
the toolchain SSOT; setup is not a competing renderer.

**Lifecycle correction adopted 2026-10-23.** Documentation and the selected tracker
record the intended contract before implementation; tests are changed only after
the real behavior is implemented. They exercise native operations and observable
effects, not mocks, assertions derived from the implementation, duplicated policy
values or fallback execution. README, guides, instructions, ADRs and canonical
skills must remain consistent through their actual source and projection owners.
The active work item records acceptance; this decision alone proves no green rollout.

**Native-flow trust amendment (`flext-0029c`, 2026-10-24).** Native Mise/uv
declarations and lock consistency replace independent pre-install Python setup
admission; they are not claimed equivalent to it. Generation publishes native
declarations, explicit upgrade resolves and writes locks, and setup uses official
Mise acquisition, native locked tool provisioning, then `uv sync --locked` into
the owned physical `.venv` without changing declarations or locks. Root CI checks out
declared members and uses the same native uv workspace/lock noneditably; independent
checkouts keep their own project contracts. Suppliers use native pyproject sources
and locks. Retire the environment supplier selector, persisted selection, synthetic
resolver, copied setup-admission artifact and its consumers together.

Only after native Mise/uv installation succeeds do existing typed owners verify
environment, locks and provenance and retain the independently consumed stdlib
authenticated-import guard. Preserve original bytes, source-change rejection,
atomic-reader handoff and first tracebacks. This post-install proof cannot attest
the preceding installation. No premature framework import, copied installer,
AWK/shell lock parser, installer port, fallback or alternate producer replaces the
native tools. Wider
Make/direnv integration is coordinated with `flext-itpd1.4.13`; bounded repeated
native QA and causal revalidation precede test changes. This contract does not
claim implementation, distribution or acceptance.

`make gen` delegates to the same generation owner in workspace and standalone profiles.
Local workspace generation covers the root and eligible managed members; `CI=Y`
selects only the target project. Generation publishes managed facades and lazy exports
from source declarations. Its required staged-consumer and publication checks remain
mandatory; they do not become a global lint, typing or suite run. Application checking
belongs to `check`, and `tests` executes the complete applicable suite once with the
persistent Testmon database.

Explicit new-project generation reuses the existing project/scaffold models and conform
planner. The target declares its identity, integration, kind and provenance; Git/worktree
preparation occurs before generation. An established non-Python repository with
those declarations may receive its complete generated layer, including Python
automation files. Missing metadata alone is not scaffold intent; previously tracked
metadata and authored content retain their separate checks. Setup owns installation
and runtime bootstrap. Generation does not initialize remotes or create a synthetic
commit.

Full-file generated outputs are not hand-edited. Merged outputs preserve authored
content outside managed regions; scaffold-only content remains authored after creation.
Invalid declarations, unsupported templates and transaction conflicts retain their
original failure. Source evidence and destination preimages remain independently
authenticated. An older projection is repaired through its current owner, never an alias
or a manual Makefile patch.

### 3. Canonical structure, facades, and naming (measured, then enforced)

The generated base fixes one structure for `src`, `tests`, `examples`, `scripts`:

- Package facades: `constants.py`, `typings.py`, `protocols.py`, `models.py`,
  `utilities.py`, `settings.py`, `config.py`, exposing `c/t/p/m/u` (+ operational
  `r/e/x/h/d/s`); private declarations in `_constants/*`, `_typings/*`, `_protocols/*`,
  `_models/*`, `_utilities/*`, `_settings.py`, `_config.py`.
- Composition: `api.py` is the thin MRO facade; `base.py` holds the shared MRO base and
  Result helpers; `cli.py` holds declarative routes.
- `**init**.py` are generated from `static_package_init.py.j2` / `lazy_init_root.py.j2`,
  preserving lazy public exports and ADR-005's model/import contract; never hand-written
  re-export sprawl.
- Naming is one scheme, rendered/validated by codegen: class prefix per project
  namespace (e.g. `Flext<Project>`, `DataOP<Concern>`, `DcBackup<Concern>`,
  `Dcdoc<Verb>Service`), sub-prefixes per concern, canonical subdirectory names, and
  module names matching the facet they own.

Naming and structure are first reported as drift, then rewritten, then enforced (phases
below). No parallel/legacy structural branch survives a green cycle.

### 3a. Namespaced runtime directories via `settings`

Every project resolves its filesystem roots only through `settings`, never through
ad-hoc `Path.home()`/`os.environ` derivations. `flext-core` `FlextSettings` (layer-0)
exposes five XDG-aware directories:

| Field         | Linux default                               | Purpose                |
| ------------- | ------------------------------------------- | ---------------------- |
| `work_dir`    | `$XDG_CACHE_HOME` or `~/.cache/<ns>`        | scratch/cache          |
| `data_dir`    | `$XDG_DATA_HOME` or `~/.local/share/<ns>`   | durable data           |
| `config_dir`  | `$XDG_CONFIG_HOME` or `~/.config/<ns>`      | configuration          |
| `state_dir`   | `$XDG_STATE_HOME` or `~/.local/state/<ns>`  | state                  |
| `runtime_dir` | `$XDG_RUNTIME_DIR/<ns>` or `<work_dir>/run` | ephemeral sockets/PIDs |

macOS and Windows map to their native equivalents (`~/Library/...`,
`%LOCALAPPDATA%`/`%APPDATA%`). Consumers read `settings.data_dir` etc.; deriving these
paths by hand is drift that Phase 3 enforcement rejects.

**`<ns>` is the consuming application's namespace, not the library's.** The segment
`<ns>` MUST be the namespace of the running application — the project that uses
`flext-core` as its entrypoint — and is shared by every library and function call at
runtime. When `flext-tap-oracle` runs, all directories are
`~/.cache/flext-tap-oracle/…`, `~/.config/flext-tap-oracle/…`, etc., even when a
`flext-cli`, `flext-meltano`, or `flext-core` function resolves a path internally. A
library MUST NEVER use its own name (`flext-cli`) for the directory segment; it uses the
running app's namespace.

**Resolution rule (owned by `flext-core` `FlextSettings`).** Two things stay separate:

- Normal settings fields keep the per-subclass namespaced pattern (each project reads
  its own `settings` singleton and its own namespaced sections).
- The directory properties (`cache_dir`, `work_dir`, `data_dir`, `config_dir`,
  `state_dir`, `runtime_dir`) are NOT per-subclass. They ALWAYS resolve from the
  **root project namespace held by the settings root singleton** — a single shared
  source — never from the `env_prefix` of the subclass that happens to access them. A
  `flext-cli`/`flext-meltano`/`flext-core` call under application X therefore returns
  `~/.<root>/X/…`; a library MUST NEVER use its own name for the directory segment.

Namespace precedence for that root value, registration being **optional**:

1. `FlextSettings.set_app_namespace("flext-tap-oracle")` — an entrypoint may declare the
   application identity once (first-wins).
2. `FLEXT_APP_NAMESPACE` — environment override when no bootstrap ran.
3. **Root project namespace (default)** — otherwise the running project's own namespace
   prevails; registration is never mandatory.

Per-application overrides use `<APPNS>_<NAME>_DIR` (e.g. `FLEXT_TAP_ORACLE_WORK_DIR`);
namespaces that are not a single safe path segment are rejected.

**Implementation ownership.** The `flext-core` `FlextSettings` change that binds the
`*_dir` resolution to the settings root singleton is implemented by the `flext-core`
maintenance lane, not by this standardization work. This ADR only fixes the contract
every consumer must follow; consumer adoption and enforcement are tracked in Beads.

### 3b. Semantic discovery and automated rewiring

Class and symbol movement is derived from live sources: typed module paths, AST/Rope
identities, and LSP reference resolution. A checked-in list that maps individual
classes, files, confidence labels, or rewrite targets is a second owner and is
prohibited. Unknown or ambiguous ownership fails at the classifier; it never falls back
to a guessed namespace or an inert/manual-review entry.

`make mod` owns this cutover. It inventories every governed repository, applies safe
ast-grep rewrites, performs semantic consumer rewiring, removes the superseded owner,
and then validates Ruff, Pyrefly, and local LSP diagnostics before accepting the fixed
point. Detection-only findings keep the invocation red but do not prevent independent
actionable rewrites from being applied first. Every phase emits causal progress in less
than 60 seconds; quiet, truncated, capped, or warning-suppressing evidence is invalid.

**Shared semantic publication.** Generation and structural modification reuse the same
typed project information, Rope engine, source authority and transaction publisher.
Each operation completes its own coherent change, including dependent facades and package
exports; neither recursively invokes another public Make verb. A source rewrite does
not require a second implementation of generation to become complete.

The generating owner renders package exports from source declarations and proves the
selected managed output. Handwritten changes are adoption inputs with explicit ownership,
not permission to overwrite authored regions because a render differs. Every consumed
source identity and destination preimage is authenticated before publication.

Git repositories and local Git operations are owned by `flext-infra`; GitHub and the CRG
runtime are owned by ai-hub. FLEXT may consume public ai-hub commands, hooks, MCP
routes, or `ai-hub-*` daemons as optional discovery enrichment. It never imports ai-hub
or CRG as a library. Absence of that optional host runtime does not fail the
deterministic local cutover; if an available integration is selected, its first error
propagates without normalization.

### 4. Three ordered phases (same strategy as ADR-007/008/009)

1. **Contract and observation.** Reconcile documentation, configuration, tracker and
   relevant canonical skills, then establish current behavior through the real public
   consumer. Read-only drift observations are evidence, not permission to rewrite.
2. **Implementation.** Use the operation that owns the change in bounded,
   deletion-first batches (ADR-005 §5). Preserve business behavior and authored input,
   remove superseded routes and prove the resulting public runtime.
3. **Confirmation and enforcement.** Only after real behavior is proven, align tests
   through public boundaries and run the complete applicable suite once. The existing
   typed gate and rule owners enforce the standard; no copied policy or alternate
   validation engine is introduced.

### 5. Applicability to independent and external projects

Standalone first-party FLEXT projects consume the same generated base through the
`standalone` profile. Third-party and non-FLEXT repositories instead follow their
upstream architecture, toolchain, runtime floor, release, and deployment contracts;
FLEXT may govern only neutral association/provenance metadata around them. This
preserves ADR-008/009 dependency direction without imposing FLEXT facades on foreign
code.

## Consequences

- One base setup and common operation surface serve the declared governed profiles
  from their existing SSOT.
- Structure, facades, `**init**.py`, and naming are generated and enforced, not
  re-invented per project.
- Drift is caught before it lands; the base cannot silently fork again.
- Independent FLEXT projects consume that base; non-FLEXT and third-party projects
  preserve their own contracts without a reverse dependency.

## Verification contract

1. Two consecutive root `make gen` runs are green and byte-idempotent on the
   standardized set; every managed file matches the rendered SSOT.
2. The standardization audit reports zero drift for verbs, layout, facades,
   `**init**.py`, toolchain/pyproject, and naming on enforced projects.
3. `make mod` reports zero actionable and detection-only findings after AST/semantic
   rewire and zero Ruff, Pyrefly, or local LSP diagnostics. When an ai-hub CRG/LSP route
   is available and selected, its distinct runtime evidence is recorded without making
   host availability a FLEXT prerequisite.
4. `make tests` executes the complete applicable suite once, retains the canonical
   Testmon database, and consumes `flext-tests` public behavior fixtures.
5. Independent FLEXT projects pass the same gates; non-FLEXT projects preserve upstream
   conventions with no reverse `flext-*` dependency (ADR-008).

These conditions describe completed standardization, not a receipt that it has occurred.
Known findings and remediation items remain open until their owners are repaired and
the declared runtime and gate evidence is complete. Generation fixed point and
functional release evidence remain blocking; no residual waiver is implied.

Current execution and measured status belong to the active branch-matched Bead.
Historical runtime snapshots and workspace-local plans cannot prove today's integration
tip or authorize another execution route. The versioned recovery contract is
`docs/ways-of-working/stabilization-checkpoint-0.12.md`.

## References

- [ADR-003 — Manifest-owned topology, profiles](003-workspace-tooling-hub-distribution.md)
- [ADR-004 — Generated Make and codegen SSOT](004-generated-make-codegen-ssot-flext-infra.md)
- [ADR-005 — Config/settings/constants/templates/schemas SSOT](005-config-settings-constants-templates-schemas-ssot.md)
- [ADR-007 — Performance optimization of worktree transactions and mutating CLI commands](007-worktree-transaction-performance.md)
- [ADR-008 — Neutral consumer boundaries](008-neutral-consumer-boundaries.md)
- [ADR-009 — Ecosystem coordination](009-ecosystem-coordination-and-library-evaluation.md)
- [Ecosystem coordination](../ecosystem-coordination.md)
- SSOT: `flext-infra/config/codegen.yaml`, `flext-infra/config/tooling.yaml`; templates
  under `flext_infra/templates/project/base/`.

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Align generation, standards, consumers and
  validation with current sources.
- This note records planning reconciliation only. It does not change the ADR's recorded
  maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
