<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

1. Truth: Never claim done, green, or resolved without command, exit code, and decisive output.
2. Root cause: No bypass, fallback, shim, suppression, stub, hardcode, or old+new coexistence.
3. Beads first: Claim or update the bead before any file write, shell command, or multi-step task sequence, and update it after each discrete step that changes repository state.
4. Research first: Inspect code, docs, and canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. FLEXT first (ai-hub Python): Use the project facades backed by flext-core and flext-cli; do not reimplement primitives locally.
6. Gate discipline: If a gate blocks, stop and escalate with the exact command/edit; never route around it.
7. Landing: Land verified work with native gates, commit, fast-forward push, and bead evidence.
8. Push rejection handling: If a fast-forward push is rejected because the remote has diverged, stop immediately, do not rebase or force-push autonomously, and escalate to the operator with the exact git error message and the local vs. remote commit SHAs.
9. Escalation clarity: If a rule is technically impossible to satisfy, stop and report the exact error. If two rules conflict, stop and present the conflict to the operator with the specific rule numbers. If a rule is unclear in context, ask a targeted clarification question before proceeding.
10. Precedence (UNIVERSAL, INVIOLABLE): NEWEST supersedes OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default behavior. On conflict, ADJUST the lower/older artifact (bead, plan, ADR, skill, doc) to match the higher/newer — never override the user or a higher/newer directive to fit a stale one. In ANY doubt, ASK THE USER FIRST — never guess.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# Project Instructions for AI Agents

## Authority

Newest operator instruction wins. Layers (non-competing):

| Layer | Owner | Content |
| --- | --- | --- |
| Global | `~/.agents/UNIVERSAL_CORE.md` + `inviolable-rules` / `make-check` / `verification-loop` | conduct, evidence, completion |
| FLEXT | this file + `.agents/skills/flext-law/SKILL.md` | architecture, Make, generation, fleet |
| Scope | nearest member `AGENTS.md` | domain facts / exclusions only |
| Execution | active Bead | intent, ownership, evidence, stop |

- Entry: `.agents/skills/flext-context-routing/SKILL.md` → `.agents/commands/flext-law.md`.
- Fail closed on missing/mismatched law; never fall back to `main` or another checkout.
- AI Hub projects managed sections; it is not Global/FLEXT authority.

Docs: [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) ·
[`docs/architecture/adr/`](docs/architecture/adr/) ·
[`docs/AI_HUB_CONSUMER.md`](docs/AI_HUB_CONSUMER.md)

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:f84d1039 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See <https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md> for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:

   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
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

Multi-package Python 3.13 workspace (superproject + 31 `flext-*` submodules) for data
integration and connectors. Clean Architecture on `flext-core`. Branch `0.12.0-dev`; forward `0.13.0`.

## Structure

```text
flext/                        # superproject: workspace + governance + docs
├── src/flext/                # workspace CLI (AUTO-GENERATED facets)
├── config/                   # workspace.yaml topology SSOT
├── docs/architecture/adr/    # ADR-001..010
├── Makefile + *.mk           # root verb dispatcher
├── flext-core/               # c/t/p/m/u + r/e/x/h/d/s
├── flext-infra/              # codegen/enforcement (not a runtime dep)
├── flext-tests/              # tm/tv/tt fixtures
├── flext-cli|api|auth|…      # platform
├── flext-ldap|ldif|…         # domain
└── flext-{tap,target,dbt}-*/ # Singer (via flext-meltano)
```

Root `AGENTS.md` is SSOT; each member repo adds a domain delta only.

| Mode | Law pointer |
| --- | --- |
| Workspace | sibling [`../AGENTS.md`](../AGENTS.md) |
| Standalone | raw GitHub `flext-sh/flext/<branch-or-tag>/AGENTS.md` (pin working line, never `main`) |

Composition: Global → this root + `flext-law` → member delta → Bead.

## Where to Look

| Task | Location | Notes |
| --- | --- | --- |
| Facades / result / DI | `flext-core/src/flext_core/` | `c,t,p,m,u` + `r,e,x,h,d,s` |
| Build / codegen | `flext-infra/src/flext_infra/` | `make build WHAT=artifacts` |
| Test fixtures | `flext-tests/src/flext_tests/` | `tm,tv,tt` |
| ADRs | `docs/architecture/adr/` | ADR-005 / 006 / 010 |
| Topology | `config/workspace.yaml` | hand-written SSOT |
| Singer connector | `flext-{tap,target,dbt}-<domain>/` | thin drivers (ADR-006) |

## Make

From workspace root only. Use `make`, never bare `uv`/`ruff`/`pyrefly`/`mypy`/`pyright`/`pytest`.

```bash
make setup
make check
make check CHECK_GATES=lint,format,pyrefly,mypy,pyright
make test
make check PROJECT=flext-core
make build WHAT=artifacts
```

- Toolchain: Python `>=3.13,<3.14`; pins in `.default-python-packages`.
- Mypy memory-capped (`MYPY_MEMORY_LIMIT_MB=6144`); never uncapped.
- Bootstrap evidence (Makefile / `.j2` / `.gitmodules` / `custom.mk` / `pyproject.toml` / `uv.lock` / `.beads`):
  clone **origin** → `make setup` exit 0 → `git status --short` empty.
- Warnings and dirty trees after provisioning are failures.
- Generated (`@flext-managed` / `@flext-ssot`): change SSOT, then `make gen` — never hand-edit projections.

## Architecture

- Facades MRO: `c → t → p → m → u`; ops `r,e,x,h,d,s`. Reverse imports
  `TYPE_CHECKING`-only. One public `api.py` (+ optional `cli.py`).
- Config/settings = layer-0 SSOT (ADR-005): `from <ns> import config, settings`
  — facades never hardcode SSOT values.
- Deps: everything → `flext-core`. Singer → `flext-meltano` (ADR-006).
  `flext-infra` via CLI/plugin only — never runtime import.
- Full law: `.agents/skills/flext-law/SKILL.md`.

## Conventions

- Facet roots AUTO-GENERATED — edit `flext-infra`, then `make build WHAT=artifacts`.
- Root `pyproject.toml` `[MANAGED]`: modernizer policy → `make build WHAT=artifacts`.
- Declaration layers: pure data (zero methods). Behavior in `u` / services / `api` / `cli`.
- Pydantic-2-way only; type via `t.*` / `p.*`; no `Any`; no compat shims; English-only.
- Tests (`flext-tests`): public facades, no mocks, unified `conftest.py`, `tests/{unit,integration,e2e}/`.
- Fix-forward git; scoped `git add` (never `-A`); track work with `bd`; ≤200 LOC/module; `uv` + `.venv` via `make`.

## Learned User Preferences

- Deduplicate via MRO / `m`; atomic consumer updates; keep Ruff + Pyrefly clean.
- Fix known failures; Make verbs must be idempotent; prefer standardized shape over transitional forms.
- Land fixes in upstream `flext-infra` on the workspace line, not local workarounds.

## Learned Workspace Facts

- Branch / version / GitHub defaults live in one workspace overlay; `make setup` follows that line for all members.
- `flext-infra` defaults via project/workspace `config/` overlays — not forked defaults.
- Provisioning adjusts and never destroys dirty work; no `git checkout` / `git reset` in setup or member sync.
- `make gen APPLY=Y` must be idempotent (following `make gen` reports no drift).

<!-- AIHUB-WORKSPACE-PROVIDERS-BEGIN -->
## Workspace providers

These routes are generated from provider-owned manifests.

- flext: read `.agents/skills/flext-context-routing/SKILL.md` first.
<!-- AIHUB-WORKSPACE-PROVIDERS-END -->
