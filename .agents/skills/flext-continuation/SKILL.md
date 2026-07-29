---
name: flext-continuation
description: Use when resuming interrupted FLEXT work tracked in Beads, after session compaction, tool failure, or handoff.
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Continuation

**PROCESS SKILL**

Resume interrupted FLEXT work from its single source of truth: the Bead ledger and its artifacts.

## Workflow

1. **Identify the active bead**
   - Context may name it; otherwise run `bd ready` or `bd list --status=in_progress`.
   - If none is active and the task clearly belongs to an existing bead, claim it with `bd claim <id>`.

2. **Load state**
   - `bd show <bead>` — read notes, acceptance criteria, dependencies, blockers.
   - Read the stored plan: either in `.beads/artifacts/<bead>/plan.md` or in the path referenced by the bead description.
   - Read the most recent artifact under `.beads/artifacts/<bead>/` if available.

3. **Validate current tree**
   - Before editing, run the narrowest gate that covers the touched lane.
   - Prefer `make check CHANGED_ONLY=1` for a quick baseline, or the per-file gates from `flext-quality-gates`.
   - Red = stop, record in bead, ask the operator.

4. **Execute the next unfinished step**
   - One step per cycle.
   - Prefer canonical commands (`make`, `ruff`, `pyrefly`, `pytest`) over one-off scripts.
   - Do **not** copy code inline from the prompt or from old bead notes. Re-derive from the canonical source.

5. **Record evidence in the bead**
   - Every command: `bd note <bead> "<command> exit <N>; <decisive output>"`.
   - Keep verbose logs on disk under `.beads/artifacts/<bead>/`; bead notes only store filepath + status.

6. **Gate before moving on**
   - After each edit batch (≤5 files): fresh import smoke + `ruff check` + `pyrefly check` + affected tests.
   - All green before the next batch.

7. **Handle blockers**
   - Stop. Do not bypass, stub, suppress, or guess.
   - Record exact command/output in the bead.
   - Ask the operator with clean options.

8. **Finish**
   - Final `make check` for affected projects.
   - Commit with explicit pathspecs; no `git add .`.
   - Fast-forward push.
   - `bd close <bead>` with evidence summary.

## Critical rules

- The bead and its artifacts are the SSOT. The prompt is only a trigger.
- Never recopy `AGENTS.md` into the bead note or prompt.
- Never include code blocks of replacement code in bead notes; point to the file/line instead.
- One logical change = one commit.
- Red gate = full stop and escalation.

## Red flags — STOP and escalate

- "The last agent already ran the gates."
- "I'll just apply this one fix without a bead."
- "The prompt told me to edit this file."
- "I'll dump the full log into the bead note."

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Copying old code blocks from the prompt | Read the current file and edit by principle |
| Skipping gates because "the last agent already ran them" | Re-run the narrowest gate now |
| Dumping full logs into bead notes | Write logs to `.beads/artifacts/<bead>/`; notes get filepath + status |
| `git add .` | Use explicit pathspecs for the active lane |
| Inventing steps not in the bead plan | Stay in the bead's accepted scope |

## Common mistakes

- **Believing the prompt over the bead.** The bead is the SSOT; re-read it every cycle.
- **Running broad validation first.** Start with the narrowest gate (`ruff check <file>`), then expand.
- **Forgetting to claim the bead.** An unclaimed bead is a coordination hazard.
- **Recording only success.** Failed commands must also be recorded with exit code and output.

## References

- `AGENTS.md` — universal law and FLEXT overlay
- `.agents/skills/flext-quality-gates/SKILL.md` — exact gate commands
- `.agents/skills/flext-development-workflow/SKILL.md` — make targets and CI
- `beads` (skill) — bead CLI usage
