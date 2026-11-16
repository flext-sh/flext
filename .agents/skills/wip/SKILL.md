---
name: wip
description: Operate the governed WIP, worktree, branch, PR, and sweep lifecycle through ai-hub wip (never flext-infra).
---

# WIP & Worktree Lifecycle (`ai-hub wip`) — SOP-FLEXT-001 v3

`ai-hub` owns 100% of runtime, workspace, worktree, Beads, Gas City (`gc`), rigs, PR
lifecycle, and sweep operations. `flext-infra` is strictly static (`gen`, `fmt`, `fix`,
`mod`, `check`, `tests`) and never knows about `ai-hub`.

## 1. Fix → Forward → Adopt → Collaborate

Work happens in the project rig on its integration branch. A lane worktree is for a mass
refactor, a dangerous adjustment or isolated validation only; it lives at the documented
`<rig>/worktrees/<bead-id>` path (the Gas City formula path when dispatch owns the lane)
and is retired after its merge.

```bash
# 1. Claim the bead; the claim is the only writer of its declared scope
ai-hub wip claim --bead <id> --path <path>

# 2. One command: claim, scope and lane
ai-hub wip start --claim --bead <id> --path <path>

# 3. Fix & Forward (static gates)
make gen && make fmt && make fix && make mod && make check CHECK_PHASE=primary && make tests
make tests-full   # complete applicable population; harness gates NOT EXECUTED

# 4. Collaborate & Land
ai-hub wip save --bead <id>
ai-hub wip check --bead <id>
ai-hub wip ship --bead <id>
ai-hub wip approve --bead <id>
ai-hub wip land --bead <id>
ai-hub wip clean --bead <id>
```

## 2. Canonical `ai-hub wip` Commands

- `ai-hub wip status [--workspace PATH] [--json]` — hierarchy, git and sync state
- `ai-hub wip doctor [--workspace PATH] [--json]` — validate workspace resolution
- `ai-hub wip claim --bead ID [--path PATH ...] [--reason TEXT]` — claim and declare the
  authorized scope; idempotent; refuses closed, foreign, conflicting or escaping scopes
- `ai-hub wip start --bead ID [--claim] [--path PATH ...] [--branch NAME]` — preflight and
  create the lane; with `--claim` the claim runs before the scope gate
- `ai-hub wip next --bead ID` — next permitted action from observed lane facts
- `ai-hub wip cancel --bead ID --reason TEXT` — close the lane PR, preserving content
- `ai-hub wip sweep [--apply] [--align] [--idle-minutes N] [--json]` — preserve local work
  and retire idle worktrees (mutates only with `--apply`; never removes active or
  `.gc/worktrees`)

## 3. RCA & PR Readiness Rules

1. **RCA mandate**: reproduce through `make check`/`make tests`; fix at the canonical
   owner (no suppressions, fallbacks, shims or mocked owners).
2. **Item deadlines**: 2 s ordinary, 20 s slow. A case that cannot fit the ordinary budget
   is declared at the slow tier from measurement; a budget is never raised to hide a
   regression.
3. **PR readiness**: `make gen`/`fmt`/`fix` no-op, `CHECK_PHASE=primary make check` exit 0,
   `make tests` green, `make tests-full` green over the complete applicable population
   with harness gates reported NOT EXECUTED; the merged revision is re-proven at its real
   entry point.
4. **Merge**: one subject per PR, merge commit; the ADR-0038 administrative landing is the
   integration-branch approval, with green required checks as the gate.
5. **Boundary**: never use `flext-infra` or the Makefile for workspace sync, worktree
   cleanup, PR validation or RCA capture.
6. **Contracts**: `docs/guides/wip-session-workflow.md` and `docs/worktrees.md` in
   `ai-hub` own the full lifecycle and placement rules.
