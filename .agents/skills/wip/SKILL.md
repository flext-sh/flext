---
name: wip
description: >
  Operate the governed WIP, worktree, branch, PR, and sweep lifecycle through
  ai-hub wip (never flext-infra). USE FOR: claiming beads, starting lanes,
  saving, checking, shipping, approving, landing, cleaning work, sweeping idle
  worktrees, RCA and PR readiness. DO NOT USE FOR: static gates (gen/fmt/fix/mod/
  check/tests), code edits, or workspace sync outside ai-hub wip.
license: MIT
metadata:
  version: "3.0"
---

# WIP & Worktree Lifecycle (`ai-hub wip`)

`ai-hub` owns runtime, workspace, worktree, Beads, Gas City, rigs, PR lifecycle,
and sweep. `flext-infra` is static only (`gen`, `fmt`, `fix`, `mod`, `check`,
`tests`).

## Quick start

1. `ai-hub wip claim --bead <id> --path <path>`
2. `ai-hub wip start --claim --bead <id> --path <path>`
3. Static gates: `make check && make check formatting && make check repair && make mod && make check
   CHECK_PHASE=primary && make tests && make tests-full`
4. `ai-hub wip save --bead <id>` then `check`, `ship`, `approve`, `land`, `clean`

## Key rules

- One Bead, one branch, one worktree, one PR.
- Fix at cause; no suppressions, fallbacks, shims, or mocked owners.
- Merge commit; ADR-0038 administrative landing is integration approval.
- Never use flext-infra or Make for workspace sync, cleanup, PR validation, or RCA.

## References

- Commands: [references/commands.md](references/commands.md)
- Readiness: [references/readiness.md](references/readiness.md)
