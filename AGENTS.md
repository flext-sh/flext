<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

1. Truth: never claim done/green/resolved without command, exit code, decisive output.
2. Root cause: no bypass, fallback, shim, suppression, stub, hardcode, or old+new coexistence.
3. Beads first: claim/update bead before file write, shell, or multi-step work; update after every repo-state change.
4. Research first: inspect code, docs, canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. Owner first: use the project's declared facades/primitives; do not reimplement them locally.
6. Gate discipline: if a gate blocks, stop and escalate with the exact command/edit; never route around it.
7. Landing: native gates, commit, fast-forward push, bead evidence.
8. Divergence: FF push rejected → integrate by cooperation: `git merge --no-ff` the integration base into your lane, resolve conflicts, revalidate, land. Never rebase or force-push a shared branch; never discard another actor's work.
9. Escalation: impossible rule → exact error. Rule conflict → present both with numbers. Unclear → one targeted question. Never guess.
10. Precedence: NEWEST > OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default. Adjust lower/older to higher/newer. Doubt → ASK USER FIRST.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# Project Instructions for AI Agents



## Canonical Governance Composition

The newest operator instruction has highest authority. Below it, FLEXT composes
four non-competing layers:

| Layer | Canonical owner | Permitted content |
| --- | --- | --- |
| Global | `~/.agents/UNIVERSAL_CORE.md` and global `inviolable-rules`, `make-check`, and `verification-loop` skills | universal conduct, execution safety, command selection, evidence, and completion |
| FLEXT | this root file and `.agents/skills/flext-law/SKILL.md` | FLEXT architecture, imports, MRO/lazy exports, workspace Make control plane, generation, and fleet boundaries |
| Scope | the nearest member or standalone `AGENTS.md` | only narrower domain facts, public surfaces, and explicit exclusions |
| Execution | the active Bead | current intent, ownership, dependencies, phase, evidence, and stop condition |

AI Hub distributes and validates managed projections; it does not become the
authority for global or FLEXT law. The local provider exposes the exact
branch-matched `.agents/skills/flext-law/SKILL.md`. A scoped file may strengthen
its parents but may not copy, weaken, rename, or replace them.

Before FLEXT work, follow `.agents/commands/flext-law.md`. Missing, ambiguous,
or branch-mismatched authority fails closed; never fall back to `main`, a
historical branch, another worktree, or a same-named catalog entry.

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

Composition is identical in both modes: global authority → this branch-matched
root and its local `flext-law` → the member's scope-only delta → the active
Bead. AI Hub only projects the managed sections. A member file adds domain
specifics and exclusions; it never copies or replaces either parent.

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

### Bootstrap contract (blocking)

A fresh `git clone` followed by `make setup` MUST exit 0 with no manual `git
submodule` step and leave the tree byte-clean. `make setup` provisions an
absent governed gitlink and attaches a detached HEAD to its declared branch,
but never writes to a present, on-branch checkout.

**Evidence rule — a completion claim is void without it.** Any change touching
`Makefile`, the `flext-infra` `.j2` templates, `.gitmodules`, `custom.mk`,
`pyproject.toml`, `uv.lock`, or `.beads/` is proven ONLY by:

```bash
git clone <origin-url> /tmp/verify && cd /tmp/verify/flext
make setup            # exit 0
git status --short    # empty
```

Run it against a clone of **origin**, never your own working copy. Evidence
from an unpushed tree is not evidence: the artifact the operator receives is
what `origin` serves, so validating local edits and reporting "done" is a
false completion (rule 1 truth-with-evidence, rule 22 finish-to-Done).
Commit and push BEFORE claiming the work lands.

**Warnings are failures.** A verb that exits 0 while printing `WARNING`,
`warning:`, or a remediation hint is not green. Fix the warning at its owner
or record it in the Bead with the exact command and output — never let it
scroll by. A dirty tree after a provisioning verb is likewise a defect, not
an acceptable leftover to hand to the next session.

**Generated surfaces have owners.** `Makefile`, `pyproject.toml` `[MANAGED]`
sections, `.beads/config.yaml`, `ci/`, and `.github/workflows/` carry
`@flext-managed` / `@flext-ssot` headers. Change the SSOT and regenerate
through `make gen`; never hand-write a projection, and never let a foreign
tool (e.g. `bd init`) rewrite one.

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
