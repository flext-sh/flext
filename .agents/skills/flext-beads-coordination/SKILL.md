---
name: flext-beads-coordination
description: 'Use this skill to coordinate parallel FLEXT work through Beads-first
  task ownership, evidence ledgers, delegation contracts, and native gate landing.
  DO NOT USE FOR: questions unrelated to FLEXT coordination, single-agent local
  edits that already have an active bead, or architecture design from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Beads Coordination

**UTILITY SKILL**

## USE FOR

- Coordinating multi-agent FLEXT work across root and submodule repositories.
- Creating or reviewing file ownership matrices before writes.
- Delegating implementation, research, or review work that must preserve AI Hub law.
- Landing verified work with bead evidence, explicit pathspecs, commit, and fast-forward push.

## DO NOT USE FOR

- questions unrelated to FLEXT coordination.
- single-agent local edits that already have an active bead and no delegation.
- creating projects or architecture from scratch.

## Workflow

1. Run `bd ready` or inspect the named bead, then claim the bead before substantive edits.
2. Record target, impact, risk, and disjoint file ownership in the bead before writes.
3. For delegated work, include the Supreme Rule, Supreme Law, R18, and exact validation commands in the delegation contract.
4. Keep every worker scoped to its owned files; read-only audits may inspect broadly, but verbose findings go under `.beads/artifacts/<bead-id>/`.
5. After each edit batch, run the affected import smoke, `ruff --no-fix`, typecheck, and scoped tests before continuing.
6. Record command, exit code, and decisive output in the bead as evidence.
7. Land only verified work with explicit pathspecs, one logical commit, fast-forward push, and final bead evidence.

## Critical rules

- Beads is the sole plan and execution ledger; never edit `.beads/*.jsonl` by hand.
- Fix root causes only; no bypasses, suppressions, compatibility wrappers, stubs, or hardcoded coexistence paths.
- Preserve continuous-green: import and collection must not break between edit batches.
- Use bare commands such as `uv run`, `make`, `ruff`, `pyrefly`, `pytest`, and `bd`; never use `.venv/bin/...`.
- Accept other agents' work as current state; do not use rollback/reset/restore/stash/clean/revert flows.
- Commit with explicit pathspecs and push only after native gates are green.

## Example

**Input:** coordinate two agents changing `flext-infra` and root skills.
**Output:** claim the bead, declare ownership per path, validate each batch, and record evidence before commit/push.

## Troubleshooting

- Missing bead -> stop and create or claim the correct bead before editing.
- Overlapping ownership -> resolve the ownership matrix in the bead before writes.
- Red gate -> diagnose the root cause, record exact command/output, and continue only after the same surface is green.
