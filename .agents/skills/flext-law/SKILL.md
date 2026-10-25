---
name: flext-law
description:
  Apply the FLEXT-only architecture, workspace, generation, import, and fleet delta over
  canonical global execution governance.
---

# FLEXT Law

## Composition

Architecture decisions are recorded under `docs/architecture/adr/`; the ADR records
there are the durable rationale this law enforces.

This repository is the sole owner of the skill named `flext-law`. AI Hub projects it but
does not author it. Generic conduct, lane safety, evidence, Make-command selection, and
completion gates remain owned by:

- `~/.agents/AGENTS.md`
- `~/.agents/skills/project-wide/shell/make-check/SKILL.md`
- `~/.agents/skills/agent-wide/verification/verification-loop/SKILL.md`

Read those skills and root `AGENTS.md`; this file adds only FLEXT domain law.
Before code changes, consult, align and adjust memory (tracker memories), `AGENTS.md`,
docs, README, ADRs, rules, applicable local and global skills and Beads at their
canonical owners, in root `AGENTS.md` contract item 8's order (operator order
2026-10-25, tracker memory `operator-order-2026-10-25-docs-first-before-code`);
repeat consultation at phase and context boundaries. Code inside docstrings and
Markdown is held to the same rules, kept current, tested and formatted (tracker
memory `operator-order-2026-10-25-embedded-code-same-rules`, ADR-028 Decision 9).
The global engineering and observable-runtime rules own the order: documentation
first, implementation and exercised real public runtime next, test changes last. Their prohibitions on mocks, patches, fakes, tautologies,
mutable config/settings hardcodes and fallbacks apply; immutable external protocol
literals and SSOT-owned defaults remain legitimate. Source changes and AI Hub's
installed delivery remain separate evidence. Global governance is authored under
`~/agents/`, not in its installed `~/.agents/` projections.

## Architecture and imports

- Dependency direction is `flext-core <- consumers`. `flext-infra` owns build, conform,
  codegen, and policy; it is never a runtime dependency.
- Facades compose in strict order `c -> t -> p -> m -> u`, with operational
  `r/e/x/h/d/s`. Reverse imports are `TYPE_CHECKING`-only.
- The canonical responsibility map is: `c` constants, `t` type aliases, `p` dependency
  protocols, `m` Pydantic v2 data models, and `u` pure utilities. `settings` owns
  external inputs, `config` owns validated derivation, `base` owns reusable foundations,
  `services` orchestrate use cases, `api` is the sole composition root, and `cli` is a
  thin transport adapter when the project declares a CLI. Do not create competing
  long-name or alias layers.
- Facade boundary (ADR-028; law text in root `AGENTS.md` "Facade boundary"): external
  libraries enter only through the owning domain's `c/t/p/m/u` (layer-0 config/settings
  for their foundation libraries); their types are named only through `t`/`p`; modules
  outside `c/t/p/m/u` and `api` are orchestrators with no facade-kind declarations,
  explicit or implicit; static enforcement lives only in flext-infra's declarative
  catalog. Before writing any import or module-level name outside a facade, place it in
  its family first.
  The same ADR owns automated correction (Decision 8), governed code examples (9),
  native tool use (11), validation in the real tree (12), the `make mod` pipeline
  order (13), Pydantic completeness and entity equality (14), capability-named
  exports with no library name outside the facades (15), maximum CA/DI decoupling
  with jscpd and qlty at zero (16), rope as the workspace model and refactoring
  engine (17), generalized minimal rules (18) and the two allowed `u` imports in
  models with `_models/pydantic.py` (19); this skill restates none of them. Each of
  Decisions 15–19 and the examples clause of 9 quotes its 2026-10-25 operator order
  verbatim with its tracker key.
- Family part shape (ADR-014, `$flext-family-shape`): the five private families each
  begin with `base.py`; a part file nests entities directly
  (models/enums/protocols/behavior, one level) — top-level orphan classes and pure
  namespace-wrapper children are forbidden and repaired only through `make mod` Rope
  rules (one YAML per rule) replicating changes via the shared `do(changes)` cycle
  wrapped in `FlextInfraUtilitiesSafety`.
- Dependencies cross use-case boundaries through `p` protocols and are provided
  explicitly by `api`. A service may not construct infrastructure, read process-global
  configuration, or resolve a dependency by string, reflection, service locator, hidden
  singleton, or module global. A container owned by `flext-core` may wire the graph only
  at the composition root. Pluggable implementations (LDIF/LDAP servers and their
  equivalents) are injected only by DI, never chosen from a registry, priority list or
  ready-made list, and their users never know which one they hold (root `AGENTS.md`
  "Pluggable capabilities arrive only by DI"; tracker memory
  `operator-order-2026-10-25-servers-di-never-registry`). The shared `c/t/p/m/u`
  families and services understand only the RFC, its extensions and metadata, never a
  dialect name, and no dialect knows another (tracker memories
  `operator-order-2026-10-25-facades-rfc-extensions-metadata-only` and
  `operator-order-2026-10-25-dialects-never-know-each-other`).
- Each package has one thin `api.py` MRO facade and one simple generated root
  `__init__.py` with automatic lazy public exports. Custom import routers, eager
  alternatives, compatibility aliases, and duplicate facades are forbidden.
- The project and its runtime work 100% of the time: one active slice completes
  `gen` → `fmt` → `fix` → `mod` → `check` → `tests` in every touched repository,
  runtime proof and the integration merge before anything else starts; nothing is
  skipped, deferred or parked; red or incomplete work is never committed, tested or
  pushed except to a preservation ref outside the working and integration branches
  (ADR-029; root `AGENTS.md` contract item 9).
- A removed or renamed public signature that still has consumers follows the
  deprecated-signature window (ADR-028 Decision 7; tracker memory
  `operator-ruling-2026-10-24-deprecated-signature-window`). It stays a marked
  pass-through to its new owner until the fleet and external census is zero, and is
  then deleted. This window is the route to zero compatibility code, not an alias
  exception.
- Lazy-init re-export (generated root `__init__.py`, PEP 562): the root re-exports the
  canonical facade letters `ALIAS_NAMES = {c, t, m, p, u, r, d, e, h, s, x, tc}` (owner
  `flext_infra._constants.validate`) resolved in this order — (1) **local facade files**
  present in the directory win (`constants.py→c`, `typings.py→t`, `protocols.py→p`,
  `models.py→m`, `utilities.py→u`, `config.py→config`, `settings.py→settings`); (2) the
  **operational letters** (`r`, `d`, `e`, `h`, `s`, `x`) are inherited from the highest
  upstream flext library (`flext_cli`, which sources them from `flext_core`) through
  `u.Infra.lazy_init_resolve_aliases`
  (nearest declaring, then nearest serving parent); (3) a **local redeclaration
  published in `__all__` overrides the inherited ancestor**; (4) `Flext*` long-name
  classes re-export only modules from the **current directory** — never
  subdirectories, parents, or siblings.
  The facade-letter set derives from the statically indexed workspace source
  (`u.Infra` `_lazy_init_package_names`), never the ambient installed/editable venv
  surface (the flext-b3xmn divergence fix: local venv and pinned CI checkout must render
  identically). Consumers import only `from <namespace> import <symbol>` with
  `<symbol> ∈ pkg.__all__` (R1).
- Service exposure follows the canonical short alias: `base.py` imports `s` from
  `flext_core`, the package root lazily re-exports `s`, and consumers use
  `from <namespace> import s`. Never rename it to `core_s` or substitute an alternative
  service-base import.
- Declaration layers are pure data. Behavior belongs in `u`; services, bases, facades
  and CLI layers orchestrate it. Owned data crosses boundaries through typed Pydantic v2
  models
  and project `t.*`/`p.*` contracts. Pydantic practice — model MRO presets, `p`/`r`
  contracts, conversions, validation, serialization, and the removal catalog — follows
  the `pydantic-development` skill; symbols reach consumers only through `m`/`t`/`u`.
- Model annotations must resolve at their declaring owner through runtime-safe imports.
  Preserve generated lazy exports and facade direction; `model_rebuild`, eager-export
  rewrites, and compatibility aliases are not import-cycle repairs. Completeness at
  import is ADR-028 Decision 14.

## Runtime and language floor

- Every first-party FLEXT source, test, example, script, template, and generated surface
  targets the exact Python floor declared by the workspace toolchain; the current FLEXT
  floor is Python 3.13 with Pydantic 2.
- Use precise annotations and the strongest native language features available at that
  floor. Downgrading syntax, importing compatibility typing layers, or weakening an
  owned type to `Any`, `object`, an unparameterized collection, or an unchecked mapping
  is forbidden.
- Runtime-floor changes start at the workspace toolchain and dependency SSOT, then
  update templates, generated config, static analyzers, tests, CI, build, and deployment
  as one atomic migration. Consumers never select a lower floor.

## Release, deployment, and activation

- Development produces one immutable, typed candidate through the workspace Make owner.
  Release identifies that candidate by version and digest; deploy associates it with one
  declared environment and configuration projection; activation atomically switches the
  runtime to that already-validated candidate. These stages are distinct and may not
  rebuild one another's input.
- `settings` reads deployment inputs, `config` validates and derives runtime
  configuration, `services` execute use cases, `api` wires dependencies, and `cli` only
  translates command input and propagates the first failure.
- Staging validates the exact artifact with the shipped public surface before
  activation. Runtime evidence must prove artifact digest, environment association,
  configuration identity, process or endpoint health, and rollback target. A successful
  build or test is not deployment evidence.

## Sources, generation, and commands

For `flext-0029c` only, the operator's direct-public-CLI route supersedes the
Make-only requirements in this law, the session router and parent instructions:
native-bootstrap diagnosis, real runtime, semantic refactoring and applicable gates
use the existing public `flext-infra` CLI; Make integration is last. This is not
a project-wide CLI relaxation or permission to invoke private workers or raw tools.
The [execution-context contract](../../../flext-infra/docs/guides/execution-context.md#native-bootstrap-task-route-flext-0029c)
owns the task's approved provisioning boundary and documentation-before-code
sequence. Implementation approval is separate from this documentation slice,
which executes no runtime, gates or distribution and proves no runtime readiness.
Universal rules and skills remain authored in `~/agents/`, not installed projections.

The approved native-bootstrap target uses one root uv workspace, with declared
submodules checked out in root CI and noneditable installation there. Locks follow
ADR-030 (tracker memory `operator-ruling-2026-10-25-member-locks-uv-mise-upg-guard`,
superseding the earlier root-only lock decision): member `uv.lock` and `mise.lock`
are kept and formed by each member, the workspace lock is their composition, only
`make upg` writes locks behind its guard (committed code and gitlinks for editable
setups; guard implementation pending), and exact SHAs pin the dependency hierarchy.
Independent checkouts retain native project contracts; external suppliers use native
pyproject sources, never environment-selected suppliers, persisted selection or
synthetic resolver views. A consumer (external project or standalone FLEXT checkout)
develops against a local FLEXT tree only through `make setup FLEXT=<path>`, which
installs the locked FLEXT distributions `<path>` provides as editable into its own
`.venv` (tracker memory `operator-ruling-2026-10-24-setup-flext-editable-param`).
Official Mise acquisition and native locked tool installation
precede `uv sync --locked` into the owned physical `.venv`. No custom Python or
AWK/shell lock/installer parser, copied setup admission or installed Infra check runs
before provision succeeds. Native declarations and lock consistency replace the
stronger independent pre-install supplier admission; post-provision provenance does
not attest an earlier install. Preserve actual source-authenticated imports as a
separate runtime guard, not a bootstrap dependency. These are target contracts;
the active Bead and coordinator own implementation, runtime/gate and rollout evidence.

Keep the independently consumed post-install stdlib guard and hand off to existing
typed environment, lock and provenance owners as soon as the installed runtime
permits. Coordinate wider Make/direnv integration with `flext-itpd1.4.13`.
Repeated bounded native QA after causal repairs and for convergence follows the
canonical command rule's task exception; tests change only after real subsystem
and cold-bootstrap proof. Do not restore the retired pre-install admission.

- `config/*.yaml`, typed settings, schemas, and generator policy are the SSOT. Change
  the owner, regenerate every projection, and remove the superseded implementation in
  the same cutover.
- Generated facets, root imports, managed `pyproject.toml` sections, Make surfaces, CI,
  and documentation are never hand-edited at consumers. Their canonical owner is
  `flext-infra` plus explicit `config/` overlays.
- Run setup, conform, codegen, docs, checks, tests, WAZA, and publication only through
  the active workspace root Make dispatcher. A missing or broken verb is repaired
  generically in `flext-infra`, then reused by workspace and standalone projects; it is
  never bypassed.
- Invoke the standard Make verbs directly. Each verb performs its fixed operation
  without an effect selector or parameter-dependent execution mode. Generation and
  repair always write their results; verification verbs retain their validation
  contract. Never add a replacement toggle or a guard for retired inputs. Agents never
  add `WHAT=` or `PROJECT=` to setup, generation, repair, formatting, checking, or
  testing.
- The common Make surface is `setup`, `upg`, `gen`, `mod`, `fix`, `fmt`, `check`,
  `tests`, `help`, `build` and `clean`. Repository-owned product commands remain
  explicit extensions. Former subverbs are absorbed into their operation owner,
  never retained as aliases or a second pipeline.
- `tests` executes the complete applicable suite once with the persistent
  Testmon database. It has no incremental prepass or file/full public aliases.
  Generation and modification complete their own coherent changes, including
  required dependent projections, through the same typed plans and semantic
  publication engine; neither recursively runs another public operation.
- Reconcile canonical documentation and governance before each implementation
  slice, prove the real public consumer next, and change tests only afterward.
  Tests never use mocks, implementation-shaped assertions, tautologies, copied
  configuration values or fallback execution.
- Apply the global command rule's operation-ownership contract transitively through
  Make prerequisites, hooks and Python callbacks. Shared planning or publication
  machinery does not authorize generation, installation, lock resolution or quality
  checking inside a different operation. A missing initial input is prepared through
  its explicit owner; it never selects a fallback producer.
- Generators emit only what is declared (ADR-018, rule
  `~/agents/rules/flext/generator-declarations.md`): a facade letter belongs to the
  module that declares it in its explicit `__all__`; an `__init__.py` propagates and
  never declares; internal tiers (`tests/`, `examples/`, `scripts/`, any root folder
  with Python) are detected, inherit by class MRO and declare their own letter; `src/`
  is public, the rest internal. No filename→letter table, closed folder list,
  advisory-gate list, single-file guard or validator bypass exists; a derivation
  replaces each, and the permission that tolerated a hack dies in the same commit.
  Every module is one nested class with nothing loose; the existing rules for that are
  `error`. Exceptions exist only by explicit operator authorization, one bead each.
- Structural rewires run through `make mod`. Its canonical FLEXT engine composes
  `ast-grep` rewrites and Rope semantic refactors. Native symbol resolution and
  publication integrity belong to that transformation; independent quality and
  fresh-import diagnostics belong to explicit verification. Repetitive manual
  call-site editing is prohibited; change the codemod or its typed automation owner
  and let that pipeline propagate the cutover.
- Symbol placement and nesting are discovered from the live typed module path, AST/Rope
  identities, and LSP references. Hand-maintained symbol/class mapping catalogs, copied
  path registries, inert entries, and review-only confidence lists are forbidden;
  ambiguity fails at the discovery owner instead of selecting a fallback. The reusable
  classifier or planner survives only on the appropriate public `c/t/p/m/u` facade.
- Git repositories and local Git operations belong to `flext-infra`. GitHub and CRG
  belong to ai-hub. When ai-hub publishes commands, hooks, MCP routes, or `ai-hub-*`
  daemons, FLEXT may consume those public runtime protocols as optional enrichment; it
  never imports ai-hub or CRG as a library. An absent optional host runtime is not a
  FLEXT error. Once an available integration is selected, its first failure remains
  visible and is never normalized.
- A detection-only AST finding keeps the final gate red but never blocks safe actionable
  rewrites in the same `make mod` invocation. Apply the mechanical cut, perform the
  semantic rewire, delete the superseded owner, and repeat until both classes are zero.
  Never stop before apply merely because a later semantic finding still requires repair.
- Long native phases emit causal progress at intervals below 60 seconds. Piping through
  `tail`, truncating/capping output, quiet flags, warning filters, and wrappers that
  hide the first traceback are forbidden evidence paths.
- `flext-tests` owns reusable fixtures and behavior helpers. Packages consume them
  through public facades rather than creating local copies.
- FLEXT tests exercise only public facades and observable runtime behavior. They use
  `tm`, canonical `c/t/p/m/u` contracts, the unified `conftest.py`, and typed shared
  fixtures instead of mocks, internal assertions, copied setup, or hardcoded
  project-owned values. Every test run retains the canonical testmon cache, including an
  explicitly requested full run.
- Connectivity-test prerequisites and availability skips follow root `AGENTS.md`,
  section "Production Readiness And Connectivity Tests"; they never waive failures
  from an available service or disable pure unit/integration behavior checks.

## Fleet integration continuity

- Accumulating unintegrated local or remote lanes, abandoned worktrees, or hidden WIP
  is a critical failure. Do not start another implementation batch while its previous
  slice lacks an explicit integration disposition and current validation evidence.
- Stash creation, WIP-hiding stash workflows, rebase, force-push, and destructive
  checkout/reset/clean are forbidden. Inspect existing stashes read-only; preserve and
  reconcile their work through an authorized, reviewable integration slice before any
  retirement. Never clear or drop them merely to obtain a clean census.
- Resolve each repository's declared integration branch and refresh its remote before
  work, after validation, and before publication. Prove the lane contains that tip;
  adopt new integration commits with a non-rewriting merge, never a history replacement.
- Keep one active owner per checkout. Reuse and reconcile existing lanes instead of
  duplicating work. Dirty or divergent input is preserved, attributed, and fixed forward.
- Land independently validated member slices first. Update superproject gitlinks only
  after proving the member commits are on their respective remote integration branches.
- Retire a branch or worktree only after fresh ancestor proof, complete WIP accounting,
  and retirement authorization. A preservation branch is not evidence of integration.
- A current lane, a published lane, and a stable integration tip are separate receipts.
  Report behind/ahead counts, unpublished WIP, and remaining red gates explicitly;
  neither a fetch nor a synchronization merge proves the integration is stable.

## Tracker: central Beads via direnv

- Every `bd` invocation runs inside the rig checkout environment:
  `direnv exec <repo> bd ...`. Never call `bd` with a manually exported port, host, or
  database.
- The activation contract is generated, not hand-written: `.envrc` / `.envrc.local`
  carry `AGENTS_GAS_CITY_ROOT` (city identity), the port from the city's runtime
  publication (`.gc/runtime/packs/dolt/dolt-state.json`), and the rig's database from
  `.beads/metadata.json` (`dolt.mode: server`). If a generation erases the server
  choice, fix the model or template owner and regenerate; never initialize an embedded
  database or persist host/port manually.
- A rig keeps its own database identity on the city's single managed Dolt server.
  Identity mismatch is repaired only with the native
  `gc rig set-endpoint <rig> --inherit` run in the city; a metadata read is not
  connectivity proof — confirm with a real `direnv exec <repo> bd show <id> --json`.

## Approved plan reconciliation and TODO projection

For explicitly authorized reconciliation, compose the global
`~/.agents/skills/tool/plan-reconciliation/SKILL.md` and its complete references;
do not copy its procedure here. The approved FLEXT scope tracked by `flext-tvkbj`
adds these boundaries:

- Read one entire plan, its companions, addenda and attachments; classify every claim
  against current authority and evidence. Transfer useful guidance to the smallest
  maintained documentation, ADR or skill owner and valid pending work to Beads before
  retirement. Reconciliation does not authorize implementing historical proposals.
- Retire only the exact reviewed path after complete transfer, attachment accounting,
  backlink repair and validation are recorded in Beads. Re-read source revisions and
  shared destinations immediately before deletion; changed inputs require renewed
  adjudication. No bulk deletion, next-plan advance or inferred disposition while the
  current plan has unresolved doubt or incomplete transfer. Collection and private-plan
  publication require their own authorization; this contract enables neither.
- Beads remains the sole execution truth. The approved `TODO.md` contract is an
  AI Hub-generated, **versioned projection**, never a manually maintained checklist.
  Explicit Bead project metadata references AI Hub's canonical project identity; its
  typed owner defines the key. Do not infer ownership or reuse Jira's `external_ref`.
- Each workspace root, member and standalone project view includes only its own
  nonterminal issues of every type, including blocked, deferred and active work.
  Shared tracker storage and dependencies never authorize root/member aggregation.
  AI Hub owns generation and automatic convergence; it never stages, commits or pushes.
  Do not hand-edit or ignore `TODO.md`, or substitute manual output for unavailable
  automation. Approval and this law are not evidence of implemented or active delivery.

## Resume entry points

- Namespace/runtime handoff and execution context:
  `flext-infra/docs/guides/execution-context.md` (the former
  `docs/roadmap/namespace-automation-handoff-2026-09-14.md` no longer exists).
- Gas City task `flext-itpd1.3` under epic `flext-itpd1` owns recovery coordination.
  Sibling workstreams `flext-itpd1.2` (documentation) and `flext-itpd1.4` (Make
  machinery) retain their bounded ownership; the coordinator owns Beads, serialized
  gates, integration, and closure. Workers implement assigned repairs but never merge or
  close Beads.
- Session plans under `.kilo/plans/` remain local evidence and resume context, never a
  published authority or second queue. Follow the explicitly approved recovery plan, not
  whichever filename is newest. Approval to use a private plan does not authorize
  copying or publishing it.
- Stabilization runbook (canonical cycle, tracker contract, landing):
  `docs/ways-of-working/stabilization-checkpoint-0.12.md`.

## Fleet boundary

- First-party FLEXT members and standalone repositories consume the same branch-matched
  law, Make control plane, and generated conventions.
- Third-party forks and content-only repositories are not FLEXT members: do not impose
  FLEXT architecture, dependency injection, typing modernization, language features,
  lint, generation, or package layout on them. Follow the upstream architecture, style,
  runtime floor, toolchain, build, release, and deployment protocol. Local governance is
  limited to typed provenance, association, credentials, artifact identity, environment
  ownership, and runtime verification metadata in a bounded `config/` overlay.
- Workspace and standalone CI are generated once by `flext-infra conform`. Exceptions
  are configuration overlays, never duplicate pipelines or custom implementations.
- Historical branches, archives, generated outputs, and other worktrees are evidence
  only. The active branch-matched canonical sources define behavior.
