---
name: flext-law
description: Apply the FLEXT-only architecture, workspace, generation, import, and fleet delta over canonical global execution governance.
---

# FLEXT Law

## Composition

Architecture decisions are recorded under `docs/architecture/adr/`; the
ADR records there are the durable rationale this law enforces.

This repository is the sole owner of the skill named `flext-law`. AI Hub
projects it but does not author it. Generic conduct, lane safety, evidence,
Make-command selection, and completion gates remain owned by:

- `~/.agents/AGENTS.md`
- `~/.agents/skills/project-wide/shell/make-check/SKILL.md`
- `~/.agents/skills/agent-wide/verification/verification-loop/SKILL.md`

Read those skills and root `AGENTS.md`; this file adds only FLEXT domain law.

## Architecture and imports

- Dependency direction is `flext-core <- consumers`. `flext-infra` owns build,
  conform, codegen, and policy; it is never a runtime dependency.
- Facades compose in strict order `c -> t -> p -> m -> u`, with operational
  `r/e/x/h/d/s`. Reverse imports are `TYPE_CHECKING`-only.
- The canonical responsibility map is: `c` constants, `t` type aliases, `p`
  dependency protocols, `m` Pydantic v2 data models, and `u` pure utilities.
  `settings` owns external inputs, `config` owns validated derivation, `base`
  owns reusable foundations, `services` owns use cases, `api` is the sole
  composition root, and `cli` is a thin transport adapter when the project
  declares a CLI. Do not create competing long-name or alias layers.
- Family part shape (ADR-014, `$flext-family-shape`): the five private
  families each begin with `base.py`; a part file nests entities directly
  (models/enums/protocols/behavior, one level) — top-level orphan classes and
  pure namespace-wrapper children are forbidden and repaired only through
  `make mod` Rope rules (one YAML per rule) replicating changes via
  the shared `do(changes)` cycle wrapped in `FlextInfraUtilitiesSafety`.
- Dependencies cross use-case boundaries through `p` protocols and are
  provided explicitly by `api`. A service may not construct infrastructure,
  read process-global configuration, or resolve a dependency by string,
  reflection, service locator, hidden singleton, or module global. A container
  owned by `flext-core` may wire the graph only at the composition root.
- Each package has one thin `api.py` MRO facade and one simple generated root
  `__init__.py` with automatic lazy public exports. Custom import routers,
  eager alternatives, compatibility aliases, and duplicate facades are
  forbidden.
- Lazy-init re-export (generated root `__init__.py`, PEP 562): the root
  re-exports the canonical facade letters `ALIAS_NAMES = {c, t, m, p, u, r, d,
  e, h, s, x, tc}` (owner `flext_infra._constants.validate`) resolved in this
  order — (1) **local facade files** present in the directory win
  (`constants.py→c`, `typings.py→t`, `protocols.py→p`, `models.py→m`,
  `utilities.py→u`, `config.py→config`, `settings.py→settings`); (2) the
  **operational letters** (`r`, `d`, `e`, `h`, `s`, `x`) are inherited from the
  highest upstream flext library (`flext_cli`, which sources them from
  `flext_core`) through
  `FlextInfraCodegenLazyInitPlannerAliasesMixin._resolve_aliases` /
  `_resolve_inherited_alias_source`; (3) a **local redeclaration published in
  `__all__` overrides the inherited ancestor**; (4) `Flext*` long-name classes
  re-export only modules from the **current directory** — never subdirectories,
  parents, or siblings. The facade-letter set derives from the statically
  indexed workspace source (`_export_names_for_package`), never the ambient
  installed/editable venv surface (the flext-b3xmn divergence fix: local venv
  and pinned CI checkout must render identically). Consumers import only
  `from <namespace> import <symbol>` with `<symbol> ∈ pkg.__all__` (R1).
- Service exposure follows the canonical short alias: `base.py` imports `s`
  from `flext_core`, the package root lazily re-exports `s`, and consumers use
  `from <namespace> import s`. Never rename it to `core_s` or substitute an
  alternative service-base import.
- Declaration layers are pure data. Behavior belongs in utilities, services,
  bases, facades, or CLI layers. Owned data crosses boundaries through typed
  Pydantic v2 models and project `t.*`/`p.*` contracts. Pydantic practice —
  model MRO presets, `p`/`r` contracts, conversions, validation,
  serialization, and the removal catalog — follows the `pydantic-development`
  skill; symbols reach consumers only through `m`/`t`/`u`.
- Model annotations must resolve at their declaring owner through runtime-safe
  imports. Preserve generated lazy exports and facade direction; `model_rebuild`,
  eager-export rewrites, and compatibility aliases are not import-cycle repairs.

## Runtime and language floor

- Every first-party FLEXT source, test, example, script, template, and generated
  surface targets the exact Python floor declared by the workspace toolchain;
  the current FLEXT floor is Python 3.13 with Pydantic 2.
- Use precise annotations and the strongest native language features available
  at that floor. Downgrading syntax, importing compatibility typing layers, or
  weakening an owned type to `Any`, `object`, an unparameterized collection, or
  an unchecked mapping is forbidden.
- Runtime-floor changes start at the workspace toolchain and dependency SSOT,
  then update templates, generated config, static analyzers, tests, CI, build,
  and deployment as one atomic migration. Consumers never select a lower floor.

## Release, deployment, and activation

- Development produces one immutable, typed candidate through the workspace
  Make owner. Release identifies that candidate by version and digest; deploy
  associates it with one declared environment and configuration projection;
  activation atomically switches the runtime to that already-validated
  candidate. These stages are distinct and may not rebuild one another's input.
- `settings` reads deployment inputs, `config` validates and derives runtime
  configuration, `services` execute use cases, `api` wires dependencies, and
  `cli` only translates command input and propagates the first failure.
- Staging validates the exact artifact with the shipped public surface before
  activation. Runtime evidence must prove artifact digest, environment
  association, configuration identity, process or endpoint health, and rollback
  target. A successful build or test is not deployment evidence.

## Sources, generation, and commands

- `config/*.yaml`, typed settings, schemas, and generator policy are the SSOT.
  Change the owner, regenerate every projection, and remove the superseded
  implementation in the same cutover.
- Generated facets, root imports, managed `pyproject.toml` sections, Make
  surfaces, CI, and documentation are never hand-edited at consumers. Their
  canonical owner is `flext-infra` plus explicit `config/` overlays.
- Run setup, conform, codegen, docs, checks, tests, WAZA, and publication only
  through the active workspace root Make dispatcher. A missing or broken verb
  is repaired generically in `flext-infra`, then reused by workspace and
  standalone projects; it is never bypassed.
- Invoke the standard Make verbs directly. Each verb performs its fixed
  operation without an effect selector or parameter-dependent execution mode.
  Generation and repair always write their results; verification verbs retain
  their validation contract. Never add a replacement toggle or a guard for
  retired inputs. Agents never add `WHAT=` or `PROJECT=` to setup, generation,
  repair, formatting, checking, or testing.
- Structural rewires run through `make mod`. Its canonical FLEXT engine
  composes `ast-grep` rewrites, Rope semantic refactors, and real
  `pyright-langserver` diagnostics before the fixed point is accepted.
  Repetitive manual call-site editing is prohibited; change the codemod or its
  typed automation owner and let that pipeline propagate the cutover.
- Symbol placement and nesting are discovered from the live typed module path,
  AST/Rope identities, and LSP references. Hand-maintained symbol/class mapping
  catalogs, copied path registries, inert entries, and review-only confidence
  lists are forbidden; ambiguity fails at the discovery owner instead of
  selecting a fallback. The reusable classifier or planner survives only on
  the appropriate public `c/t/p/m/u` facade.
- Git repositories and local Git operations belong to `flext-infra`. GitHub and
  CRG belong to ai-hub. When ai-hub publishes commands, hooks, MCP routes, or
  `ai-hub-*` daemons, FLEXT may consume those public runtime protocols as
  optional enrichment; it never imports ai-hub or CRG as a library. An absent
  optional host runtime is not a FLEXT error. Once an available integration is
  selected, its first failure remains visible and is never normalized.
- A detection-only AST finding keeps the final gate red but never blocks safe
  actionable rewrites in the same `make mod` invocation. Apply the
  mechanical cut, perform the semantic rewire, delete the superseded owner, and
  repeat until both classes are zero. Never stop before apply merely because a
  later semantic finding still requires repair.
- Long native phases emit causal progress at intervals below 60 seconds.
  Piping through `tail`, truncating/capping output, quiet flags, warning filters,
  and wrappers that hide the first traceback are forbidden evidence paths.
- `flext-tests` owns reusable fixtures and behavior helpers. Packages consume
  them through public facades rather than creating local copies.
- FLEXT tests exercise only public facades and observable runtime behavior.
  They use `tm`, canonical `c/t/p/m/u` contracts, the unified `conftest.py`, and
  typed shared fixtures instead of mocks, internal assertions, copied setup, or
  hardcoded project-owned values. Every test run retains the canonical testmon
  cache, including an explicitly requested full run.

## Tracker: central Beads via direnv

- Every `bd` invocation runs inside the rig checkout environment:
  `direnv exec <repo> bd ...`. Never call `bd` with a manually exported
  port, host, or database.
- The activation contract is generated, not hand-written: `.envrc` /
  `.envrc.local` carry `AGENTS_GAS_CITY_ROOT` (city identity), the port
  from the city's runtime publication (`.gc/runtime/packs/dolt/dolt-state.json`),
  and the rig's database from `.beads/metadata.json` (`dolt.mode: server`).
  If a generation erases the server choice, fix the model or template owner
  and regenerate; never initialize an embedded database or persist host/port
  manually.
- A rig keeps its own database identity on the city's single managed Dolt
  server. Identity mismatch is repaired only with the native
  `gc rig set-endpoint <rig> --inherit` run in the city; a metadata read is
  not connectivity proof — confirm with a real
  `direnv exec <repo> bd show <id> --json`.

## Resume entry points

- Stabilization handoff (state table, first failure, next action):
  `flext-infra/docs/roadmap/namespace-automation-handoff-2026-09-14.md`.
- Gas City task `flext-itpd1.3` under epic `flext-itpd1` owns recovery
  coordination. Sibling workstreams `flext-itpd1.2` (documentation) and
  `flext-itpd1.4` (Make machinery) retain their bounded ownership; the
  coordinator owns Beads, serialized gates, integration, and closure.
  Workers implement assigned repairs but never merge or close Beads.
- Session plans under `.kilo/plans/` remain local evidence and resume context,
  never a published authority or second queue. Follow the explicitly approved
  recovery plan, not whichever filename is newest. Approval to use a private
  plan does not authorize copying or publishing it.
- Stabilization runbook (canonical cycle, tracker contract, landing):
  `docs/ways-of-working/stabilization-checkpoint-0.12.md`.

## Fleet boundary

- First-party FLEXT members and standalone repositories consume the same
  branch-matched law, Make control plane, and generated conventions.
- Third-party forks and content-only repositories are not FLEXT members: do
  not impose FLEXT architecture, dependency injection, typing modernization,
  language features, lint, generation, or package layout on them. Follow the
  upstream architecture, style, runtime floor, toolchain, build, release, and
  deployment protocol. Local governance is limited to typed provenance,
  association, credentials, artifact identity, environment ownership, and
  runtime verification metadata in a bounded `config/` overlay.
- Workspace and standalone CI are generated once by `flext-infra conform`.
  Exceptions are configuration overlays, never duplicate pipelines or custom
  implementations.
- Historical branches, archives, generated outputs, and other worktrees are
  evidence only. The active branch-matched canonical sources define behavior.
