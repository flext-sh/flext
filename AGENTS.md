# FLEXT

<!-- BEGIN AI-HUB MANAGED UNIVERSAL CORE -->
<!-- UNIVERSAL-GOVERNANCE v4 -->

## Universal Agent Engineering Core

`~/.agents` is the sole universal authority. AI Hub distributes and configures it but
never competes with it. Project law may be stricter; the newest explicit operator
instruction prevails and lower authority must be reconciled.

### P0 — Tests validate config/settings changes by construction

Tests, golden files, and executable documentation (including markdown examples and
docstring snippets) must remain valid when config or settings change. They are never
allowed to hardcode, freeze, or implicitly assume the values that exist today.

- The canonical owner of every configurable fact is `config/*.yaml`, `settings`, or the
  generator that derives from them. Tests only validate that owner.
- Expected values owned by config/settings must be read from the same typed SSOT
  production reads, or proven through a generator/consumer round-trip.
- A test that breaks on a legitimate config/settings change is a test defect. Fix the
  test; never freeze the configuration to keep the test green.
- This rule applies to all test tiers, markdown examples, and docstring snippets
  validated by the pytest plugin.
- Literal expectations in tests are reserved for immutable external protocol contracts,
  not for values the project owns through config/settings.

1. **Truth with evidence.** Claims require the exact command, working directory, exit
   status, decisive output, and bounded scope.
2. **Research before mutation.** Read current authority, intent, owner Bead,
   implementation owner, consumers, generated projections, concurrent WIP, and
   validation route. Never invent behavior or results.
3. **One active intent.** Preserve the goal, target, Bead, exclusions, phase, required
   gates, and stop condition through delegation and continuation.
4. **Root cause and one owner.** Change the canonical owner and complete the cutover. No
   bypass, fallback, shim, suppression, hardcode, fake, duplicate route, silent default,
   or old-and-new coexistence.
5. **Fix forward.** Preserve shared work; never destructively discard unknown changes.
   Re-read mutable files and classify relevant paths and hunks.
6. **Typed and generated boundaries.** Parse untrusted input once into canonical types.
   Change sources, not projections; regenerate and prove idempotence.
7. **Continuous green.** No completion while the project or environment is broken,
   partially migrated, dirty from task WIP, ahead of remote, missing real-use QA, or
   carrying stale generated output or docs. Run native global and changed-scope gates;
   Python requires Ruff, Pyrefly, Pyright, Mypy, and Pytest coverage plus applicable
   build and integrated validation. Lint and type gates cover `examples/`, `scripts/`,
   and `tests/` with the same rigor as production source: blanket
   `per-file-ignores`/exclude patterns that hide violations in those trees are
   prohibited (operator law 2026-07-20). The only permitted exceptions are test-idiom
   rules explicitly justified per rule (e.g. `S101` assert usage, `PT` pytest
   conventions). Every violation in those trees is fixed at its root, never masked.
8. **Beads is execution truth.** Beads owns work, plans, memory, dependencies, status,
   evidence, and closure. GitHub is its continuous external coordination, PR, review,
   and CI mirror after the orchestrator organizes Beads completely.
9. **Separated roles.** The orchestrator coordinates, owns semantic Beads state,
   validates, approves or rejects merges, rolls out, and closes; it does not implement.
   Workers directly implement one Bead in one branch and worktree but never merge or
   close. The standing documenter continuously audits, updates, validates, and removes
   stale canonical skills, ADRs, docs, Python docstrings, examples, and executable
   snippets under the same validated PR flow; the governance/CI helper also remains
   active.
10. **No stall by reporting.** Five-minute status reports include the agent table and
    epic evolution and never pause execution. Compaction, continuation, and status
    transfer context only.
11. **Historical material is evidence only.** Archives, generated or tool homes,
    backups, sessions, caches, and legacy trees are never live authority.
12. **Stop only for a real blocker.** Ask one precise question only when authority

    conflicts or an action would be destructive; otherwise continue to the observable
    stop condition.

13. **Short validated slices.** Deliver in small, independently validated

    units that merge to the integration branch quickly — one Bead, one reviewable PR,
    hours not days. Mega-lanes and long-lived WIP are defects; the orchestrator splits
    any unit that cannot merge green within a session.

14. **Living documentation.** Project knowledge is durable, never rebuilt

    per session. On entering a project, read its docs first and validate key claims
    quickly against live reality. Every change that produces new understanding or
    behavior updates the affected docs in the SAME change; stale docs are defects filed
    as beads, never worked around.

15. **Runtime reality precedes implementation and tests.** Establish the correct
    behavior from the official external contract and the real consumer first. For
    generated or deployed artifacts, validate the staged artifact with that real
    consumer before deployment, restart, tests, or static gates. Then align the
    canonical implementation and models; only afterward may tests encode the observed
    behavior. Tests and static analysis are subordinate confirmation, never discovery
    authority, design input, a substitute for consumer validation, or permission to
    publish a runtime-broken artifact. A test that contradicts observed canonical
    behavior is corrected, never accommodated by production. Performance optimization is
    evidence-first: profile with cProfile to find the hot path before changing anything,
    then optimize with the project's typed OO/MRO/lazy-import patterns; accelerate test
    selection with impact analysis (e.g. pytest-testmon) and parallelism (pytest-xdist)
    rather than deleting or weakening coverage. See P0 above: tests of
    `config`/`settings` validate contracts and behavior for arbitrary valid values and
    read expected config-owned values from the same typed SSOT the consumer receives;
    they never freeze today's configured scalar, identifier, path, endpoint, model,
    ranking, or default. Goldens may lock structure, never mutable config/settings
    values.
16. **Parametrized config, generators, and managed binaries.** config, settings, and
    templates are the sole source of configuration and business rules; the correct
    generator produces every derived surface (never hand-edit a projection). ai-hub owns
    the installation of binaries and the provisioning of no product-, agent-, or
    daemon-specific hardcoded code anywhere — every such value is parametrized through
    config/settings/templates.
17. **Canonical command surface only.** Every build, check, test, generation, release,
    deploy, and validation action runs through the project's canonical standard Make
    verbs directly, or the project's documented canonical CLI — never through ad-hoc
    direct tool invocations that bypass the command's guards, locks, dry-run semantics,
    and evidence. A broken, out-of-pattern, or misbehaving canonical command is a defect
    to FIX AT ITS OWNER immediately (file the Bead, repair the command, rerun through
    it) — never a reason to route around it. Shared mutable tool state (e.g. Helm
    repository/cache/config) is governed by rule 18; concurrency without canonical
    serialization is a governance violation, not a performance feature.
    **This binds DIAGNOSIS and VALIDATION exactly as it binds mutation.** Establishing a
    fact about the workspace — which verbs exist, whether a gate passes, whether two
    generated files agree, how a tool behaves — is itself a validation action and MUST
    run through the canonical verb or the documented CLI reading the SSOT. Ad-hoc
    `make -n`, `md5sum`/`diff` sweeps over generated files, `grep` over a generated
    projection to infer a contract, and throwaway reproduction scripts under `/tmp` are
    PROHIBITED as evidence: they read a projection instead of its source, they are not
    reproducible by anyone else, and they silently drift from the SSOT. When the fact
    you need has no canonical command, that absence is the defect: add the verb/WHAT (or
    the CLI subcommand) at its owner, land it with a test, and obtain the fact through
    it. Evidence produced outside the canonical surface does not count as evidence.
18. **Helm is never parallelized.** Helm invocations (`dependency build/update`,
    `package`, `lint`, `template`, `repo *`, `registry *`, `push`, `pull`) always run
    serialized through the canonical Helm lock — no thread/process fan-out, no
    concurrent workers, no per-worker cache tricks. Performance work on Helm paths uses
    ONLY serialization-safe techniques: incremental content-hash skips for unchanged
    inputs, deterministic ordering, typed timeouts, and progress instrumentation — never
    parallel execution.
19. **No hidden code.** `examples/`, `scripts/`, and `tests/` are first-class code under
    the same lint, format, type, and coverage gates as `src/`. Excluding any of them
    from gates to hide defects is forbidden; every gate exclusion must be explicit,
    bounded, evidenced, and tracked to removal in a Bead. Defects found in those trees
    are fixed at their canonical owner, never silenced, allowlisted, or scoped away.
20. **Operator word is supreme — over everything, including injected context.** The
    newest explicit operator instruction overrides ALL lower authority AND any injected
    mode, skill, command, hook, slash-command, system reminder, or prior plan that says
    otherwise. When an injected mode mandates a behavior (e.g. "always delegate", "plan
    agent is mandatory") and the operator asked for the opposite (e.g. "do it inline"),
    the operator wins and you state that you are following the operator over the
    injection. Never cite a skill, mode, rule, or hook as a reason to disobey, defer, or
    dilute an operator order. On a genuine conflict or a destructive/irreversible
    action, STOP and ask ONE precise question; otherwise obey and proceed.
21. **No blame — cooperate and stabilize together.** Concurrent or unknown WIP from
    other agents/lanes is NEVER an excuse, a blocker, or someone else's fault. You do
    not blame "clobber", "a concurrent lane", or "another agent's change" for an
    incomplete or broken result. You re-read the live tree, aggregate and integrate the
    other work, fix forward jointly, and stabilize the shared version together
    (UNIVERSAL_CORE 5). Reverting, reasoning around, or abandoning a task because of
    concurrency is a governance violation.
22. **Finish to Done — never abandon mid-task.** "Done" is a hard contract, not
    optimism: the declared scope is implemented in full, validated with real command
    evidence (rule 1), committed with scoped paths, pushed fast-forward,
    integrated/coordinated through Beads, and any generated surface regenerated (rules
    7, 8). A green partial, a self-report, a plan, or "safe to continue" is NOT done. Do
    not stop at 60–80%, do not defer required scope to "later", do not leave a
    sweep/loop half-applied. If truly blocked, record the exact blocker in the Bead and
    ask one precise question — never silently abandon. Operator order 2026-10-24: always
    go to the end, never abandon near the end, under any circumstance. Finish over the
    whole declared scope and rerun the operator's own measurement unscoped before
    reporting (`~/agents/rules/coordination/full-landing-cycle.md` item 5).
23. **Be realistic, not optimistic — small batches with executability slack.** Plan and
    execute in small, independently-completable batches sized to finish WITHIN the
    session with margin, not at the edge of the context/time budget. Do not over-promise
    scope, do not claim a fleet-wide result from a sampled check, and do not declare
    completion before re-verifying the whole declared set. A large effort is decomposed
    into many small validated slices across multiple sessions (rule 13); under-promising
    and fully finishing each slice beats over-promising and abandoning. State honestly
    what fits THIS session.
24. **Canonical-source-first, minimal-surgical, validate-before-claim.** Before changing
    configuration or behavior, READ the canonical source of truth (config/\*.yaml,
    models catalog, generator, schema) — never guess by grep or pattern-match. Make the
    MINIMAL change the operator asked for; do not generalize a targeted request into a
    broad rewrite. Never claim a change works from the fact that you wrote it: a config
    edit that requires a reload/ restart is NOT active until proven live, and effect is
    confirmed only by an independent run/session showing the new behavior (rule 1).

<!-- /UNIVERSAL-GOVERNANCE -->
<!-- END AI-HUB MANAGED UNIVERSAL CORE -->

FLEXT is a Python 3.13 and Pydantic 2 workspace: this superproject and the `flext-*`
repositories that its `.gitmodules` declares, all built on `flext-core`. This file holds
the facts that bind every FLEXT repository. A member's `AGENTS.md` adds only its
package's facts; a standalone checkout reads this file from `flext-sh/flext` at the
branch it is built from. Each technical decision lives in its accepted ADR under
`docs/architecture/adr/`, the operator's words live in the Beads tracker (`bd`) under
the key a text cites, and Beads holds execution.

## FLEXT core

**Layout.**

- `flext-core` is the foundation every package depends on, and its runtime code
  imports no other `flext-*` package. `flext-cli` owns the CLI-adjacent domains; the
  Singer taps, targets and dbt projects are thin drivers over `flext-meltano`
  (ADR-006). `flext-infra` owns generation, refactoring and gates; it is a development
  dependency reached through its CLI and pytest plugin, never imported at runtime, and
  its source never imports `flext-tests`. `.gitmodules` alone lists the members
  (ADR-024).
- A repository keeps runtime configuration in its root `config/`, rule catalogs in
  `rules/`, generator templates in `templates/` and rule tests in `tests/rules/`, never
  under `src/<package>/`, and its distribution ships those trees (tracker
  `operator-order-2026-10-24-repo-layout-rules-templates-config`).
- Packages, modules and directories are named by responsibility in PEP 8 form: module
  files never start with `_`, facade directories always do, and no name is a number,
  a fragment or a library. A repository's kind is detected from its own facts, never
  declared (tracker `operator-order-2026-11-02-kind-detected`).

**Architecture.**

- Facades compose by MRO in the order `c` constants, `t` types, `p` protocols, `m`
  Pydantic models, `u` utilities, with `r e x h d s`; a later letter is imported only
  under `TYPE_CHECKING`, and no import cycle exists. A module declares one top-level
  class in every tier (`conftest.py` and `tests/fixtures/` hold the test fixtures). `c`,
  `t`, `p`, `m`, settings and config hold no behavior beyond Pydantic validators;
  behavior lives in `u`, and every other module only composes it (ADR-028).
- `api.py` is the composition root and injects dependencies as `p` protocols; no
  registry, priority list, locator, `ContextVar`, `lru_cache` or `ClassVar` selects one.
  Servers, dialects and other pluggable implementations are injected; shared code knows
  only the standard contract (RFC, extensions, metadata), and no implementation knows
  another (ADR-028 Decision 16).
- A library is imported and named only in the `c/t/p/m/u` module that adapts it (config
  and settings import their foundation); outward names describe the capability (`git_`,
  `refactor_`, `workspace_`), never the library (ADR-028 Decision 15). Only flext-cli's
  run owner and flext-core start processes; everything else calls `u.Cli.run`. Logging
  goes only through `u.trace`, `u.debug`, `u.info`, `u.warning`, `u.error`,
  `u.exception` and `u.critical`.
- A package exposes its declarations through its generated lazy `__init__.py`, which
  re-exports only what its own modules declare in `__all__`. Consumers import from the
  nearest package; a family module imports the upstream letters
  (`from flext_cli import c, t, p, m, u`) and its same-family siblings through the
  family package, never the letter it assembles (ADR-028 Decision 10). Nothing loads
  before first use except `flext_core.lazy` and the beartype bootstrap, which run once;
  config, settings and each standard API are singletons that load once, in under one
  second (tracker `operator-order-2026-10-25-load-benchmarks-subsecond`).
- `config` holds the validated business rules of `config/*.yaml` and `settings` the
  environment and CLI inputs. Both are layer zero, reached as
  `from <package> import config, settings`, and import only the standard library, their
  foundation and their own layer-zero helpers (ADR-005).
- Owned payloads are models on `m.*` presets, validated once at the boundary
  (`model_validate`, `model_validate_json`), dumped with `model_dump` and compared by
  value. Models compose by inheritance and composition, declare each field once at its
  owner, keep fields read-only unless code mutates them, and never import `u` (ADR-028
  Decisions 14 and 19).
- Types are `p` protocols or `t` aliases, never `Any`, `object` or `m.*`; `TypeForm`
  comes from `typing_extensions`. Every model and service has a `@runtime_checkable`
  protocol mirror with its name, base and module pattern; the mirror follows the model
  hierarchy, declares only its own members and is generated by `make gen` from the
  declarations read through Rope (tracker
  `operator-order-2026-11-02-protocol-mirrors-concrete` and
  `operator-answers-2026-11-03-one-page-law`). No owned `.pyi` stub or SDK mirror
  exists.

**Tools.**

- Rope owns Python semantics: analysis, renames, moves, signatures and imports,
  `TYPE_CHECKING` placement included. An authored ast-grep rule with its fix and
  fixture rewrites only a simple syntactic pattern. All rules are authored data in
  flext-infra's catalog, applied by `make mod` to every occurrence; no FLEXT code parses
  or rewrites Python with `ast`, LibCST, `tokenize` or regular expressions (tracker
  `operator-order-2026-10-28-exterminate-ast-libcst-fallbacks`).
- `check`, `gen` and `mod` are one pipeline over Rope and the catalog: `check` reports,
  `gen` projects declarations and templates, `mod` refactors. A generated file
  (initializers, facades, `pyproject.toml` sections, Makefiles, CI, documentation
  projections) changes only at its template or configuration in
  `Infra.codegen.templates.entries`.
- Ruff formats and lints with its flake8-type-checking family off as an axiom (tracker
  `operator-order-2026-11-02-ruff-type-checking-axiom-off`); Pyrefly, Pyright and Mypy
  check types under the tooling policy's limits; jscpd and qlty stay at zero, the
  license header being jscpd's only exception.
- Code in docstrings and Markdown obeys the same rules, stays current and runs in the
  documentation tests (ADR-028 Decision 9); docstrings follow the Google convention.

**Commands.**

- `make help` lists the verbs, run from the workspace root: `setup`, `upg`, `gen`,
  `mod`, `fix`, `fmt`, `check`, `tests`, `tests-full`, `help`, `build` and `clean`.
  `upg` alone writes the uv and mise locks (ADR-030); `setup` installs them, and
  `make setup FLEXT=<path>` installs a local FLEXT tree editable into a consumer;
  `check` only reads; `tests` runs the Testmon selection on its persistent database and
  `tests-full` the whole suite once without Testmon (ADR-029).
- A slice runs `gen`, `fmt`, `fix`, `mod`, `check` and `tests` in every repository it
  touches. A second `gen` changes nothing, `gen` followed by `check` is green, and
  `fmt` and `fix` change nothing in generated output (ADR-028 Decision 8).
- Each make invocation finishes within 60 s; a slower verb is profiled with cProfile and
  fixed at its cause (tracker `operator-order-2026-10-25-make-timeout-60s-cprofile`).
  Until the verbs are validated, lint verdicts come from direct `ruff check` and
  `pyrefly check` on explicit paths, run from the member root with its own
  configuration (tracker
  `operator-order-2026-11-02-direct-ruff-pyrefly-until-make-validated`).

**Gates.**

- Ruff and Pyrefly report zero errors across the governed workspace, and pytest passes
  under Testmon, before a phase advances (tracker
  `operator-order-2026-10-26-global-ruff-pyrefly-strict-lazy-exports`). `tests/`,
  `examples/` and `scripts/` meet the gates of `src/`, and
  `Infra.codegen.loc_cap.max_lines` caps module size.
- A rule key of Ruff, Pyrefly, Pyright, Mypy, jscpd or qlty (selection, severity, mode,
  `typeCheckingMode`, tier scope, `extraPaths`, environment bindings) changes only when
  the operator names the key, its old value, its new value and the reason (tracker
  `lint-rule-change-freeze-operator-order-2026-10`); regenerating a projection to match
  its catalog is not a change.
- An exception exists only as an axiom declared once in flext-infra's tooling
  configuration: one that lets Pydantic work, settles a conflict between tools, or lets
  two FLEXT patterns apply together (tracker
  `operator-order-2026-11-02-exceptions-axioms-only`). Every other ignore, suppression
  or exemption is removed together with what honors it.

**Tests.**

- Tests exercise public behavior through `flext-tests`: `tm` matchers, the canonical
  letters, one `conftest.py`, typed fixtures in `tests/fixtures/`, the
  `tests/{unit,integration,e2e}` layout and one nested `Tests<Unit>` class per module.
  They use no mocks or patches and read config-owned values from their owner. Settings
  and config are loaded from inside nested `c/t/p/m/u` classes, and config, settings,
  the API facade and CLI invocation carry load benchmarks.
- FLEXT's declared availability prerequisite: a test that needs an external service runs
  only when a local, untracked `.env` test environment is reachable, and is otherwise
  reported unmet, never passed; a Docker-dependent one does not run in CI. `.env` is
  never committed or printed.

**Compatibility.** A change rewires every consumer through Rope and deletes the old
name. A public signature still used outside the change stays a `warnings.deprecated`
delegation to its new owner (`compat: <old> -> <new>; fix: <rewire>`) until the census,
external consumers included, is zero (tracker
`operator-ruling-2026-10-24-deprecated-signature-window`).

**Rig and lanes.** The rig checkout stays on `0.12.0-dev` at its tip and takes hotfixes
and bugfixes; work happens in lanes merged with `--no-ff`. `upload-20261007` is a lane
promoted into `0.12.0-dev` once green, and the rig returns to the tip once its WIP is
preserved (tracker `operator-order-2026-11-02-rigs-on-integration`). Every member
integrates on `0.12.0-dev`, and a member commit lands before its gitlink moves. Dirty or
concurrent state never blocks work; only the `upg` lock guard requires committed state
(ADR-030). A remeasured bead gets one `val<YYYYMMDDTHHMM>` label with its evidence.

<!-- AIHUB-WORKSPACE-PROVIDERS-BEGIN -->

## Workspace providers

These routes are generated from provider-owned manifests.

- flext: read `.agents/skills/flext-context-routing/SKILL.md` first.

<!-- AIHUB-WORKSPACE-PROVIDERS-END -->

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->

## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the
`beads` skill at `.agents/skills/beads/SKILL.md` (project install) or
`~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use
the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking; do not create markdown TODO lists.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads
  context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory
  files.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data`
on your git remote; `.beads/issues.jsonl` is a passive export. See
<https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md> for details and
anti-patterns.

<!-- END BEADS CODEX SETUP -->
