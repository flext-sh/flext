---
name: flext-beads-coordination
description: Use when coordinating parallel FLEXT agents through Beads. Covers claim order, ownership matrices, delegation law, evidence notes, validation commands, and fast-forward landing for shared worktrees.
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Beads Coordination

**PROCESS SKILL**

Coordinate parallel FLEXT work from the Beads ledger. Beads is the single source of truth for task state, ownership, blockers, evidence, and handoff notes.

## USE FOR

- Coordinating multiple agents or lanes in the FLEXT workspace.
- Claiming or resuming shared-worktree implementation beads.
- Defining file ownership before edits.
- Recording validation and landing evidence.

## DO NOT USE FOR

- Replacing `bd` with ad-hoc task files.
- Delegating without the universal law and exact validation commands.
- Editing files before ownership is claimed.
- Broad cleanup outside the active bead lane.

## Workflow

1. Run `bd ready` or `bd show <bead>` and select one active bead.
2. Claim the bead before edits with `bd update <bead> --claim`.
3. Record a disjoint ownership matrix in the bead before writes.
4. Read `AGENTS.md` and the scoped skills for the touched paths.
5. Validate the current lane before editing when the tree may already be red.
6. Edit one batch of at most five files.
7. Run fresh import smoke, `ruff check --no-fix`, `pyrefly check`, and the affected tests.
8. Append concise bead evidence with command, exit code, and decisive output.
9. Commit only active-lane files with explicit pathspecs.
10. Push fast-forward and record the SHA in the bead.

## Critical rules

- Beads is the only task and coordination ledger.
- Claim before editing and keep evidence current.
- Delegation propagates the universal law and exact validation commands.
- Disjoint file ownership is mandatory before writes.
- Validation evidence must include command, exit code, and decisive output.
- Red gates stop the lane until the root cause is fixed or escalated.

## Delegation Contract

Every delegated worker prompt must include:

- Supreme Rule: absolute truth with command evidence.
- Supreme Law: root-cause fixes only; no bypass, shim, fallback, suppression, stub, or hardcode.
- R18 continuous-green requirement.
- The bead ID and owned file paths.
- Exact validation commands the worker must run.
- Instruction to write verbose findings under `.beads/artifacts/<bead>/` and keep bead notes concise.

## Ownership Rules

- One lane owns a file for writes until it records handoff or closes the bead.
- Other agents may read broadly, but they must not edit outside their recorded lane.
- Interface changes require workspace-wide consumer discovery and same-batch consumer updates.
- Concurrent user or agent changes are accepted as current state and fixed forward.

## Git Rules

- Never use rollback, reset, restore, stash, clean, revert, or destructive checkout.
- Never use `git add .`.
- Use explicit pathspecs for `git add` and `git commit`.
- Push only after the native gates for the touched lane are green.
- If push is not fast-forward or ownership overlaps, stop and record the blocker.

## Validation

Use the narrowest decisive commands first:

```bash
ruff check --no-fix <paths>
pyrefly check <paths>
pytest <tests> -q --tb=short --no-cov
make check PROJECT=<project>
make test PROJECT=<project>
```

For docs and skills, also run the relevant repository validators when available, such as skill format checks, docs audits, or the project `make check` target that covers the changed paths.

## Evidence Template

Record concise bead notes:

```text
<scope> green. Commands: <command> exit 0 <decisive output>; <command> exit 0 <decisive output>. Commit <sha> pushed to origin/<branch>.
```

For failures:

```text
Blocked. Command: <command>. Exit: <code>. Decisive output: <root error>. Next clean action: <exact edit or command>.
```

## References

- `AGENTS.md`
- `.agents/skills/flext-continuation/SKILL.md`
- `.agents/skills/flext-development-workflow/SKILL.md`
- `.agents/skills/flext-quality-gates/SKILL.md`
