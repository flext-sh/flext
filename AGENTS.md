<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

1. Truth: never claim done/green/resolved without command, exit code, decisive output.
2. Root cause: no bypass, fallback, shim, suppression, stub, hardcode, or old+new coexistence.
3. Beads first: claim/update bead before file write, shell, or multi-step work; update after every repo-state change.
4. Research first: inspect code, docs, canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. Owner first: use the project's declared facades/primitives; do not reimplement them locally.
6. Gate discipline: if a gate blocks, stop and escalate with the exact command/edit; never route around it.
7. Landing: native gates, commit, fast-forward push, bead evidence.
8. Push rejection: FF push rejected on divergence → stop; no autonomous rebase/force-push; escalate with git error + local vs remote SHAs.
9. Escalation: impossible rule → exact error. Rule conflict → present both with numbers. Unclear → one targeted question. Never guess.
10. Precedence: NEWEST > OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default. Adjust lower/older to higher/newer. Doubt → ASK USER FIRST.
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
make work WHAT=status PROJECT=flext-infra BEAD=<id>
make work WHAT=start PROJECT=flext-infra BEAD=<id> KIND=feature NAME=<slug> APPLY=Y
make work WHAT=land PROJECT=flext-infra BEAD=<id> APPLY=Y
make work WHAT=finish PROJECT=flext-infra BEAD=<id> APPLY=Y
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

- Deduplicate via MRO / `m`; atomic consumer updates with direct uses and no compatibility shims; keep Ruff + Pyrefly clean after every edit.
- Fix known failures; Make verbs must be idempotent; prefer standardized shape over transitional forms.
- Land fixes in upstream `flext-infra` codegen/config overlays on the workspace line, not local workarounds.
- Adopt, validate, commit, and push together; finish WIP through merge on the active DEV line (`0.12.0-dev`) unless the operator asks to promote to `main`; absorb fast-forward/merge fallout; remaining lint/test failures stay owned until green; do not invent blockers or re-confirm settled facts.
- Do mutating fleet work in a `make work` worktree on a dedicated branch; keep the primary flext checkout on `0.12.0-dev` clean.
- Prefer lean, structured AGENTS.md that cross-links skills and docs over long prose.
- Keep pre-commit inline and enforceable before commit/push; do not skip hooks to land work.
- Maximize flext-core/cli/infra/tests facades and declarative enforcers (tach, import-linter, rope, ast-grep) via SSOT rules — never reimplement local equivalents or custom validators.
- In result internals, ban regressive lazy imports of concrete `FlextResult`; type against abstract `p.Result`.
- Structure large programs as beads epic → sub-epics → per-phase enforcement and validation beads before any code phase.

## Learned Workspace Facts

- Branch / version / GitHub defaults live in one workspace overlay; `make setup` follows that line for all members.
- Workspace and member checkouts stay on `0.12.0-dev` unless the operator names another line.
- `flext-infra` defaults via project/workspace `config/` overlays — not forked defaults.
- Provisioning adjusts and never destroys dirty work; no `git checkout` / `git reset` in setup or member sync.
- `make gen WHAT=apply APPLY=Y` must be idempotent (following `make gen` reports no drift).
- `flext-infra` codegen owns fleet CI and hook projections; remove duplicate custom CI and regenerate consumers from its config/templates.
- CI policy: draft PRs run no CI; integration pushes (`dev`/`develop`/`0.12.0-dev`) run blocking ubuntu `CI` only; `ci-matrix` is projected only for workspace-root/standalone and auto-runs only on push to `main` (plus optional `workflow_dispatch`); workspace-member projects must not receive or auto-run `ci-matrix` (`codegen.yaml` profiles exclude them; `make gen WHAT=apply APPLY=Y` prunes orphan member copies); CodeQL default setup is a GitHub repo setting outside Jinja; other branches skip.
- Agent/skill surfaces on governed branches must be real files, not symlinks; `config.AiHub.paths.ai_hub` materializes them per its application config.
- Project markdown docs centralize under `docs/` (root keeps only standardized files); `.agents/*` and `data/*` are special; external-docs follow `docs/reference/` patterns; validate via `make check` markdown gates and flext-infra docs generation.
- Lane lifecycle is the `make work` verb (beads, worktrees, gh/PR, gitflow) owned by flext-infra Makefile/codegen on `0.12.0-dev`; AI Hub consumes the same surface without duplicating gitflow.
- Default `make test` is testmon-incremental fleet-wide; coverage stays out of default CI (`CI=Y` skips cov); GitHub Actions testmon cache warms until green, then renews only on success within quota.
- Enforcement split: flext-core runtime (beartype rules), flext-infra static engines, flext-tests pytest automation harness (`tm`/`tv`/`tt`) for all projects.

<!-- AIHUB-WORKSPACE-PROVIDERS-BEGIN -->
## Workspace providers

These routes are generated from provider-owned manifests.

- flext: read `.agents/skills/flext-context-routing/SKILL.md` first.
<!-- AIHUB-WORKSPACE-PROVIDERS-END -->
