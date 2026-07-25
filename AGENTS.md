# Project Instructions for AI Agents

<!-- BEGIN AI-HUB MANAGED UNIVERSAL CORE -->
<!-- UNIVERSAL-GOVERNANCE v4 -->

## Universal Agent Engineering Core

`~/.agents` is the sole universal authority. AI Hub distributes and configures
it but never competes with it. Project law may be stricter; the newest explicit
operator instruction prevails and lower authority must be reconciled.

## P0 — Tests validate config/settings changes by construction

Tests, golden files, and executable documentation (including markdown examples and
docstring snippets) must remain valid when config or settings change. They are
never allowed to hardcode, freeze, or implicitly assume the values that exist today.

- The canonical owner of every configurable fact is `config/*.yaml`, `settings`,
  or the generator that derives from them. Tests only validate that owner.
- Expected values owned by config/settings must be read from the same typed SSOT
  production reads, or proven through a generator/consumer round-trip.
- A test that breaks on a legitimate config/settings change is a test defect.
  Fix the test; never freeze the configuration to keep the test green.
- This rule applies to all test tiers, markdown examples, and docstring snippets
  validated by the pytest plugin.
- Literal expectations in tests are reserved for immutable external protocol
  contracts, not for values the project owns through config/settings.

1. **Truth with evidence.** Claims require the exact command, working directory,
   exit status, decisive output, and bounded scope.
2. **Research before mutation.** Read current authority, intent, owner Bead,
   implementation owner, consumers, generated projections, concurrent WIP, and
   validation route. Never invent behavior or results.
3. **One active intent.** Preserve the goal, target, Bead, exclusions, phase,
   required gates, and stop condition through delegation and continuation.
4. **Root cause and one owner.** Change the canonical owner and complete the
   cutover. No bypass, fallback, shim, suppression, hardcode, fake, duplicate
   route, silent default, or old-and-new coexistence.
5. **Fix forward.** Preserve shared work; never destructively discard unknown
   changes. Re-read mutable files and classify relevant paths and hunks.
6. **Typed and generated boundaries.** Parse untrusted input once into canonical
   types. Change sources, not projections; regenerate and prove idempotence.
7. **Continuous green.** No completion while the project or environment is
   broken, partially migrated, dirty from task WIP, ahead of remote, missing
   real-use QA, or carrying stale generated output or docs. Run native global
   and changed-scope gates; Python requires Ruff, Pyrefly, Pyright, Mypy, and
   Pytest coverage plus applicable build and integrated validation. Lint and
   type gates cover `examples/`, `scripts/`, and `tests/` with the same rigor
   as production source: blanket `per-file-ignores`/exclude patterns that
   hide violations in those trees are prohibited (operator law 2026-07-20).
   The only permitted exceptions are test-idiom rules explicitly justified
   per rule (e.g. `S101` assert usage, `PT` pytest conventions). Every
   violation in those trees is fixed at its root, never masked.
8. **Beads is execution truth.** Beads owns work, plans, memory, dependencies,
   status, evidence, and closure. GitHub is its continuous external coordination,
   PR, review, and CI mirror after the orchestrator organizes Beads completely.
9. **Separated roles.** The orchestrator coordinates, owns semantic Beads state,
   validates, approves or rejects merges, rolls out, and closes; it does not
   implement. Workers directly implement one Bead in one branch and worktree but
   never merge or close. The standing documenter continuously audits, updates,
   validates, and removes stale canonical skills, ADRs, docs, Python docstrings,
   examples, and executable snippets under the same validated PR flow; the
   governance/CI helper also remains active.
10. **No stall by reporting.** Five-minute status reports include the agent table
    and epic evolution and never pause execution. Compaction, continuation, and
    status transfer context only.
11. **Historical material is evidence only.** Archives, generated or tool homes,
    backups, sessions, caches, and legacy trees are never live authority.
12. **Stop only for a real blocker.** Ask one precise question only when authority
   conflicts or an action would be destructive; otherwise continue to the
   observable stop condition.
13. **Short validated slices.** Deliver in small, independently validated
   units that merge to the integration branch quickly — one Bead, one
   reviewable PR, hours not days. Mega-lanes and long-lived WIP are defects;
   the orchestrator splits any unit that cannot merge green within a session.
14. **Living documentation.** Project knowledge is durable, never rebuilt
   per session. On entering a project, read its docs first and validate key
   claims quickly against live reality. Every change that produces new
   understanding or behavior updates the affected docs in the SAME change;
   stale docs are defects filed as beads, never worked around.
15. **Runtime reality precedes implementation and tests.** Establish the correct
    behavior from the official external contract and the real consumer first. For
    generated or deployed artifacts, validate the staged artifact with that real
    consumer before deployment, restart, tests, or static gates. Then align the
    canonical implementation and models; only afterward may tests encode the
    observed behavior. Tests and static analysis are subordinate confirmation,
    never discovery authority, design input, a substitute for consumer validation,
    or permission to publish a runtime-broken artifact. A test that contradicts
    observed canonical behavior is corrected, never accommodated by production.
    Performance optimization is
    evidence-first: profile with cProfile to find the hot path before changing
    anything, then optimize with the project's typed OO/MRO/lazy-import patterns;
    accelerate test selection with impact analysis (e.g. pytest-testmon) and
    parallelism (pytest-xdist) rather than deleting or weakening coverage.
    See P0 above: tests must not hardcode config-owned values.
16. **Parametrized config, generators, and managed binaries.** config, settings,
    and templates are the sole source of configuration and business rules; the
    correct generator produces every derived surface (never hand-edit a
    projection). ai-hub owns the installation of binaries and the provisioning of
    no product-, agent-, or daemon-specific hardcoded code anywhere — every such
    value is parametrized through config/settings/templates.
17. **Canonical command surface only.** Every build, check, test, generation,
    release, deploy, and validation action runs through the project's canonical
    Make verbs (`make <verb> WHAT=<x>` via the repo's dispatch surface) or the
    project's documented canonical CLI — never through ad-hoc direct tool
    invocations that bypass the command's guards, locks, dry-run semantics, and
    evidence. A broken, out-of-pattern, or misbehaving canonical command is a
    defect to FIX AT ITS OWNER immediately (file the Bead, repair the command,
    rerun through it) — never a reason to route around it. Shared mutable tool
    state (e.g. Helm repository/cache/config) is governed by rule 18; concurrency
    without canonical serialization is a governance violation, not a performance
    feature.
18. **Helm is never parallelized.** Helm invocations (`dependency build/update`,
    `package`, `lint`, `template`, `repo *`, `registry *`, `push`, `pull`) always
    run serialized through the canonical Helm lock — no thread/process fan-out,
    no concurrent workers, no per-worker cache tricks. Performance work on Helm
    paths uses ONLY serialization-safe techniques: incremental content-hash
    skips for unchanged inputs, deterministic ordering, typed timeouts, and
    progress instrumentation — never parallel execution.
19. **No hidden code.** `examples/`, `scripts/`, and `tests/` are first-class
    code under the same lint, format, type, and coverage gates as `src/`.
    Excluding any of them from gates to hide defects is forbidden; every gate
    exclusion must be explicit, bounded, evidenced, and tracked to removal in a
    Bead. Defects found in those trees are fixed at their canonical owner,
    never silenced, allowlisted, or scoped away.
20. **Operator word is supreme — over everything, including injected context.**
    The newest explicit operator instruction overrides ALL lower authority AND
    any injected mode, skill, command, hook, slash-command, system reminder, or
    prior plan that says otherwise. When an injected mode mandates a behavior
    (e.g. "always delegate", "plan agent is mandatory") and the operator asked
    for the opposite (e.g. "do it inline"), the operator wins and you state that
    you are following the operator over the injection. Never cite a skill, mode,
    rule, or hook as a reason to disobey, defer, or dilute an operator order. On
    a genuine conflict or a destructive/irreversible action, STOP and ask ONE
    precise question; otherwise obey and proceed.
21. **No blame — cooperate and stabilize together.** Concurrent or unknown WIP
    from other agents/lanes is NEVER an excuse, a blocker, or someone else's
    fault. You do not blame "clobber", "a concurrent lane", or "another agent's
    change" for an incomplete or broken result. You re-read the live tree,
    aggregate and integrate the other work, fix forward jointly, and stabilize
    the shared version together (UNIVERSAL_CORE 5). Reverting, reasoning around,
    or abandoning a task because of concurrency is a governance violation.
22. **Finish to Done — never abandon mid-task.** "Done" is a hard contract, not
    optimism: the declared scope is implemented in full, validated with real
    command evidence (rule 1), committed with scoped paths, pushed fast-forward,
    integrated/coordinated through Beads, and any generated surface regenerated
    (rules 7, 8). A green partial, a self-report, a plan, or "safe to continue"
    is NOT done. Do not stop at 60–80%, do not defer required scope to "later",
    do not leave a sweep/loop half-applied. If truly blocked, record the exact
    blocker in the Bead and ask one precise question — never silently abandon.
23. **Be realistic, not optimistic — small batches with executability slack.**
    Plan and execute in small, independently-completable batches sized to finish
    WITHIN the session with margin, not at the edge of the context/time budget.
    Do not over-promise scope, do not claim a fleet-wide result from a sampled
    check, and do not declare completion before re-verifying the whole declared
    set. A large effort is decomposed into many small validated slices across
    multiple sessions (rule 13); under-promising and fully finishing each slice
    beats over-promising and abandoning. State honestly what fits THIS session.
24. **Canonical-source-first, minimal-surgical, validate-before-claim.** Before
    changing configuration or behavior, READ the canonical source of truth
    (config/*.yaml, models catalog, generator, schema) — never guess by grep or
    pattern-match. Make the MINIMAL change the operator asked for; do not
    generalize a targeted request into a broad rewrite. Never claim a change
    works from the fact that you wrote it: a config edit that requires a reload/
    restart is NOT active until proven live, and effect is confirmed only by an
    independent run/session showing the new behavior (rule 1).

<!-- /UNIVERSAL-GOVERNANCE -->
<!-- END AI-HUB MANAGED UNIVERSAL CORE -->

This file provides instructions and context for AI coding agents working on this project.

## Mandatory Governance Bootstrap

Before any mutation, read in order:

1. The newest operator request.
2. `~/.agents/UNIVERSAL_CORE.md`.
3. `~/.agents/skills/inviolable-rules/SKILL.md`.
4. `~/.agents/skills/flext-law/SKILL.md`.
5. This file, the active Bead, and the current durable plan.

### Intent Card

For every multi-step task, record before acting:

- exact requested outcome;
- active workspace/worktree and branch;
- active parent and child Beads;
- current phase and observable stop condition;
- preserved WIP and concurrent writers;
- in-scope paths and explicit exclusions;
- required project-scoped and workspace-wide gates.

Delegation and compaction must preserve this card verbatim. A new plan, traceback,
subagent result, or status request may not silently replace the operator's outcome.

### Exclusive Operational Ownership

- One coordinator owns the requested project outcome through integration, validation, and closure.
- Subagents receive disjoint, bounded scopes; they do not redefine acceptance, sequence, or completion.
- Do not start overlapping mutation teams for the same phase.
- A worker result, status report, locally green file, or elapsed time does not release ownership.
- Verify every delegated path and claim against the live worktree before accepting it.

### Continuous-Green Completion Contract

The project must never be declared complete or left between tasks in a task-created
broken or partial state. Before completing every task:

1. The environment/bootstrap remains functional.
2. Global Ruff lint and format pass through the root Make dispatcher.
3. Global Pyrefly passes through the root Make dispatcher.
4. Pyright and memory-capped Mypy pass for every changed project and affected consumer.
5. Pytest passes for every changed project and affected integration surface.
6. Relevant workspace validation and real public-surface behavior pass.
7. Generated outputs are owner-driven and idempotent.
8. Beads contains exact commands, exit codes, decisive output, blockers, and remaining scope.

Project-scoped gates are iteration evidence, not substitutes for the final global Ruff,
format, and Pyrefly baseline. No task closes with red imports, broken generation,
uncollected tests, unvalidated WIP, or a workaround masking the defect.

### Fix-Forward Worktree Law

- The active worktree root is the execution root; never assume `/home/marlonsc/flext` is the mutation target when
  another worktree was selected.
- Preserve all existing root and submodule WIP. Never reset, restore, checkout, clean, stash, or overwrite unknown
  changes.
- Re-read mutable files before editing and commit only explicit owned paths when Git authority is granted.
- Generated files change only through their canonical generator, config, schema, policy, or template owner.
- Status is a checkpoint, not a stopping condition. Continue until the intent card's observable stop condition holds or
  one precise operator decision is required.

For the lane contract that governs light-worker execution, see
[`docs/ways-of-working/worker-lane-contract.md`](docs/ways-of-working/worker-lane-contract.md).

<!-- BEGIN BEADS INTEGRATION v:1 profile:full hash:19cc25d9 -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other
tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Dolt-powered version control with native sync
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update <id> --claim --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task atomically**: `bd update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Quality

- Use `--acceptance` and `--design` fields when creating issues
- Use `--validate` to check description completeness

### Lifecycle

- `bd defer <id>` / `bd supersede <id>` for issue management
- `bd stale` / `bd orphans` / `bd lint` for hygiene
- `bd human <id>` to flag for human decisions
- `bd formula list` / `bd mol pour <name>` for structured workflows

### Sync

bd stores issue history in Dolt:

- Each write auto-commits to Dolt history
- Use `bd dolt push`/`bd dolt pull` for remote sync
- Do not treat `.beads/issues.jsonl` as the sync protocol

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote;
`.beads/issues.jsonl` is a passive export. See <https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md>
for details and anti-patterns.

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator
instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync
  unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless
  active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit,
  and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and
orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:

   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status

   ```

5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**

- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.

<!-- END BEADS INTEGRATION -->

## Overview

FLEXT is a **multi-package Python 3.13 workspace** (git superproject + 31 `flext-*` git submodules) for enterprise data
integration, platform tooling, and operational connectors. Every package follows one canonical Clean-Architecture shape
built on `flext-core`. Branch `0.12.0-dev`; forward baseline `0.13.0`.

## Structure

```text
flext/                     # superproject: workspace manager + governance + docs
├── src/flext/             # flext-workspace CLI (thin orchestrator over flext-cli) — AUTO-GENERATED facets
├── config/                # workspace.yaml topology SSOT (codegen/conform input; never overwrite)
├── docs/architecture/adr/ # ADR-001..010 — architectural decisions (see below)
├── Makefile + *.mk        # root verb dispatcher (all work runs from here)
├── flext-core/            # foundation: c/t/p/m/u + r/e/x/h/d/s facades (every pkg depends on it)
├── flext-infra/           # build automation, codegen, enforcement (tooling; not a runtime dep)
├── flext-tests/           # shared test infra (tm/tv/tt fixtures)
├── flext-cli|api|auth|web|grpc|observability|plugin|meltano/  # platform capabilities
├── flext-ldap|ldif|db-oracle|oracle-wms|oracle-oic|quality/   # domain libraries
└── flext-{tap,target,dbt}-*/ # Singer ecosystem: 5 taps, 5 targets, 4 dbt (built on flext-meltano)
```

Each submodule is an **independent git repo**. This root `AGENTS.md` is the canonical SSOT; submodule `AGENTS.md` files
point here and add only domain-specific notes.

### How each submodule references this root (two working modes)

Each submodule's `AGENTS.md` links back to this file. Which link to follow depends on how the package is checked out:

- **Workspace mode** (submodule sits inside this superproject): read the sibling **[`../AGENTS.md`](../AGENTS.md)** —
  the working copy on your current branch.
- **Standalone / independent mode** (the package was cloned on its own, imported as a dependency, or vendored — no
    parent workspace exists, so `../AGENTS.md` does not resolve): read the **raw file on GitHub on the same
  branch/release** the project is on:

```text
  <https://raw.githubusercontent.com/flext-sh/flext/><branch-or-tag>/AGENTS.md
  # current working line:
  <https://raw.githubusercontent.com/flext-sh/flext/0.12.0-dev/AGENTS.md>
```

  Always pin `<branch-or-tag>` to the SAME branch/release the package is built from
(e.g. `0.12.0-dev`, or the release tag), never `main`/`master` — the governance law is versioned with the code.

Precedence is unchanged in both modes: this root law + the AI-HUB managed Universal Agent Law block override
submodule-local notes; the submodule file only *adds* domain specifics.

## Where to Look

| Task | Location | Notes |
| ------ | ---------- | ------- |
| Foundation facades / result / DI | `flext-core/src/flext_core/` | `c,t,p,m,u` + `r,e,x,h,d,s`; every pkg's base |
| Build/codegen/enforcement | `flext-infra/src/flext_infra/` | drives `make build WHAT=artifacts`, conform, lint rules |
| Test fixtures & builders | `flext-tests/src/flext_tests/` | `tm,tv,tt`; unified `conftest.py` pattern |
| Architectural decisions | `docs/architecture/adr/` | ADR-005 (config SSOT), ADR-006 (thin drivers), ADR-010 (codegen standardization) |
| Workspace topology | `config/workspace.yaml` | member list, codegen input (hand-written SSOT) |
| A Singer connector | `flext-{tap,target,dbt}-<domain>/` | thin driver over `flext-meltano` bases (ADR-006) |

## Build & Test

**All commands run from the active workspace/worktree root**, never from inside a submodule
(the root dispatcher forwards to each project). Use `make`, never bare `uv`/`ruff`/`pyrefly`/`mypy`/`pyright`/`pytest`.

```bash
# Environment (creates .venv, uv sync --all-packages, installs hooks)
make boot

# Whole-workspace quality gates (blocking in CI)
make check                              # all gates
make check CHECK_GATES=lint,format,pyrefly,mypy,pyright
make check CHECK_GATES=lint,format,pyrefly,mypy,pyright

# Tests / validation (advisory in CI)
make test
make check WHAT=all

# Scope a single submodule with PROJECT=
make check PROJECT=flext-core
make check WHAT=mypy PROJECT=flext-ldif
make test  PROJECT=flext-cli
make boot  PROJECT=flext-meltano

# Regenerate auto-generated facets (after touching codegen sources)
make build WHAT=artifacts
```

**Pinned toolchain** (`.default-python-packages`): Ruff `0.15.22`, mypy `2.3.0`, Pyright `1.1.411`, Pyrefly `1.1.1`.
Python strictly `>=3.13,<3.14`.

**Gotchas:** mypy is memory-capped (`MYPY_MEMORY_LIMIT_MB=6144`, 600s) — never run mypy uncapped, it can blow up RAM;
override with `make check WHAT=mypy MYPY_MEMORY_LIMIT_MB=8192`. Docs CI needs
`uv sync --all-packages --all-groups --all-extras` for dev tools.

## Inviolable Delivery Governance

These rules are mandatory for every FLEXT task. They strengthen the universal
law; no project-local instruction, Bead note, historical plan, agent, or
concurrent work may weaken them.

### Healthy environment is a completion condition

- Never close, defer as complete, hand off as complete, commit as complete, or
  claim success while the affected project is broken or left in unowned WIP.
  A task remains `in_progress` until it is fixed forward or blocked by an
  explicit external dependency recorded in its Bead.
- Before closing an implementation task, manually exercise the changed public
  surface: Make/CLI for workspace behavior, a minimal import/driver for a
  library, or the applicable service/UI surface. Static gates alone do not
  satisfy completion.
- Validate after the final edit, not merely before it. Any post-validation
  edit invalidates prior green evidence.
- Do not lower coverage, suppress diagnostics, skip gates, or replace root
  Make commands with direct tools to obtain a green result. Fix forward.

### Required Python quality gates

Run every command from the active workspace/worktree root using `make` only.

1. **Global environment gates, after every implementation task:**

   ```bash
   make check CHECK_GATES=lint,pyrefly

   ```

   Ruff and Pyrefly must be healthy for the workspace. Existing debt is not a
   reason to close new work: either resolve it in the owning Bead or keep the
   current task open with a precise, linked blocker.
2. **Changed-scope gates, after every implementation task:**

   ```bash
   make check PROJECT=<affected-project> CHECK_GATES=pyright,mypy
   make test PROJECT=<affected-project>
   ```

   Use the narrowest supported root-Make target first, then widen to the
   affected project when package boundaries, generated files, shared fixtures,
   configuration, or public facades changed.
3. **Final task gate:** repeat the global Ruff/Pyrefly command and all
   changed-scope Pyright, mypy, and pytest commands after the final change.
   Record command, cwd, exit code, and decisive output in the owning Bead.

If a required gate cannot run because the environment itself is broken, stop
.the task, preserve the worktree, create or update one narrow Bead for the
environment failure, and do not report the implementation as complete.

### Tests must validate config and settings changes (P0)

Tests are consumers of the config/settings SSOT, not frozen copies of it.
Any expected value owned by config or settings (versions, paths, URLs, verbs,
profiles, allowed lists, timeouts) must be read from the same source production
uses or proven through a generator round-trip.

- A test that breaks on a legitimate config change is a test defect.
- Golden files and snapshots may pin structure only; they are regenerated via
the canonical make verb when config-driven values change.
- This rule applies to unit, integration, and e2e tests, plus markdown examples
and docstring snippets validated by the pytest plugin.

See `docs/standards/testing.md` and `docs/standards/development.md` for the
detailed contract.

### State ownership and handoff

- Claim the live Bead before mutations. Beads are the sole task tracker;
  `.beads/issues.jsonl` is never edited by hand.
- Re-read `bd show <id> --json`, `git status`, and relevant submodule status
  before a handoff or closure. Existing changes are provenance: do not reset,
  restore, clean, stash, normalize, or silently include them.
- Use explicit-path atomic commits only when the user authorizes commits.
  Never use `git add -A`, amend, force-push, or push without explicit
  authorization.
- Handoffs must name changed paths, unresolved paths, exact validation status,
  manual-QA result, active Bead, and the next root-Make command. A handoff is
  not permission to leave an otherwise fixable broken environment behind.

## Architecture Overview

**Facade layering (strict order `c -> t -> p -> m -> u`)** composed via MRO from `flext-core`:

- `c` constants · `t` typings · `p` protocols · `m` models (Pydantic-2) · `u` utilities
- Operational: `r` FlextResult · `e` FlextExceptions · `x` FlextMixins · `h` FlextHandlers · `d` FlextDecorators · `s`
  FlextService
- Forward imports (higher→lower) may be runtime; **reverse imports are `TYPE_CHECKING`-only**. `c` never imports `m` at
  runtime.
- Each package exposes exactly one public `api.py` (thin MRO facade) + optional `cli.py`; internals live under
  `_constants/_typings/_protocols/_models/_utilities`.

**Config/settings are the layer-0 SSOT** consumed BY the facades (ADR-005). Access is single-form only:

```python
from <namespace> import config, settings   # e.g. from flext_core import config, settings
config.<Namespace>.*      settings.<Namespace>.*
```

Config = business rules (`config/*.yaml`, validated); settings = env/CLI-tunable knobs. Facades never hardcode values
the SSOT holds. Config/settings modules import only stdlib/pydantic/upstream base — never a project facade (zero-cycle).

**Dependency direction:** `flext-core` ← everything. `flext-cli` owns CLI domains
(Toml/Yaml/Csv/Json/Cli/Tui/Run/Dag/Templates/Workflow). Singer connectors are thin drivers over `flext-meltano`
(ADR-006). `flext-infra` is build/tooling — reached via its CLI + pytest plugin, **never imported at runtime**.

## Conventions & Patterns

- **`**init**.py`, `constants.py`, `models.py`, etc. facet roots are AUTO-GENERATED**
    (`# AUTO-GENERATED FILE — Regenerate with: make build WHAT=artifacts`). Never hand-edit; change the codegen source in `flext-infra`
  - run `make build WHAT=artifacts`.
- **Root `pyproject.toml` `[MANAGED]` sections** are generated by `flext_infra.deps.modernizer` — edit generator policy
  then `make build WHAT=artifacts`, never by hand.
- **Declaration layers are pure data:** models/protocols/constants/typings/settings/config carry ZERO methods
  (only Pydantic Field/validators/computed_field). Behavior lives only in `u`/services/`api`/`base`/`cli`.
- **Pydantic-2-way only** for owned payloads (`model_validate` in, `model_dump` out). No
  `dict`/`TypedDict`/`dataclass`/`NamedTuple`/`m.Dict` as a data contract.
- **Typing:** never `Any`/`object`/concrete-class annotations; type via `t.*` aliases and `p.*` protocols; `T | None`
  (never `Optional`). A model is never a type.
- **No compat surface:** no shims, legacy branches, dual old+new paths, loose helpers, or suppression
  (`# type: ignore`/`# noqa`) without documented justification. Remove superseded code the same cycle.
- **English-only** in all code, comments, docstrings, log strings, and `.j2` templates.
- **Tests** (`flext-tests`): behavior-only through public facades, NO mocks/`patch`, one unified `conftest.py`, typed
  fixtures in `tests/fixtures/`, layout `tests/{unit,integration,e2e}/`, thin single nested `Tests<Unit>` class.
- **Multi-agent tree:** fix-forward only, never `git reset/checkout/restore/clean/stash` shared work; commit by
  explicit paths (never `git add -A`); coordinate via beads (`bd`).
- **≤200 logical LOC per module**; net-negative LOC on refactors.
- Toolchain: `uv` + `.venv` only, always via `make`.

<!-- AIHUB-WORKSPACE-PROVIDERS-BEGIN -->
## Workspace providers

These routes are generated from provider-owned manifests.

- flext: read `.agents/skills/flext-context-routing/SKILL.md` first.
<!-- AIHUB-WORKSPACE-PROVIDERS-END -->
