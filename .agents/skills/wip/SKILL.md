---
name: wip
description: Operate the governed WIP, worktree, branch, PR, and sweep lifecycle through ai-hub wip (never flext-infra).
---

# WIP & Worktree Lifecycle (`ai-hub wip`) — SOP-FLEXT-001 v2

`ai-hub` owns 100% of runtime, workspace, worktree, Beads, Gas City (`gc`), rigs, PR lifecycle, and sweep operations. `flext-infra` is strictly static (`gen`, `fmt`, `fix`, `mod`, `check`, `tests`) and never knows about `ai-hub`.

## 1. Fix → Forward → Adopt → Collaborate

```bash
# 1. Start / Adopt dedicated lane worktree (zero WIP in primary checkout)
ai-hub wip start --bead <id>

# 2. Fix & Forward (static gates inside lane worktree)
make gen && make fmt && make fix && make mod && make check CHECK_PHASE=primary && make tests

# 3. Collaborate & Land
ai-hub wip save --bead <id>
ai-hub wip check --bead <id>
ai-hub wip ship --bead <id>
ai-hub wip approve --bead <id>
ai-hub wip land --bead <id>
ai-hub wip clean --bead <id>
```

## 2. Canonical `ai-hub wip` Commands

- `ai-hub wip status [--workspace PATH] [--json]` — Hierarchy, git, and sync state
- `ai-hub wip doctor [--workspace PATH] [--json]` — Validate workspace resolution
- `ai-hub wip next --bead ID` — Next permitted action from observed lane facts
- `ai-hub wip cancel --bead ID --reason TEXT` — Close lane PR, preserving branch content
- `ai-hub wip sweep [--apply] [--align] [--idle-minutes N] [--json]` — Preserve local work & retire idle worktrees (`--apply` required to mutate; never removes active or `.gc/worktrees`)

## 3. RCA & PR Readiness Rules

1. **RCA Mandate**: Reproduce via `make check` / `make tests` first; fix at the canonical owner only (zero `# type: ignore`, lint suppressions, fallbacks, shims, or mocked owners).
2. **PR Readiness**: `make check CHECK_PHASE=primary` exit 0, `make tests` exit 0 (<20s incremental, <120s full), generator idempotence (`make gen && make check` green, `fmt`/`fix` no-op).
3. **Boundary**: Never use `flext-infra` or `Makefile` for workspace sync, worktree cleanup, PR validation, or RCA capture.
4. **Full Contract**: `docs/guides/wip-session-workflow.md` in `ai-hub`.
