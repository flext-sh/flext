# FLEXT Continuation — Summary

## Purpose

This skill turns any "continue from where we left off" request into a disciplined, repeatable workflow. The prompt that triggered the skill is intentionally thin; the bead and its artifacts carry the actual plan.

## When to invoke

- The user says "continue", "resume", "retake", "finish", or similar.
- A bead is in progress and the next step is unclear from chat context.
- A session was interrupted by compaction, a tool failure, or a handoff.

## Ritual at a glance

1. `bd show <bead>` — load accepted plan and last evidence.
2. Read the plan file and latest artifact under `.beads/artifacts/<bead>/`.
3. Smoke-test the affected package(s) before editing.
4. Do the next unfinished step; one per cycle.
5. Gate: `ruff check` → `pyrefly check` → affected `pytest`/`make test`.
6. Record command + exit code + decisive output in the bead.
7. Repeat until the bead closes.

## Example template

Given bead `<bead-id>`:

1. **Load state**
   - `bd show <bead-id>`
   - Read plan at `.beads/artifacts/<bead-id>/plan.md` or path referenced by the bead.
   - Read latest artifact under `.beads/artifacts/<bead-id>/`.

2. **Validate tree before edits**
   - `make check CHANGED_ONLY=1`
   - Import smoke for affected packages.

3. **Next unfinished step**
   - Derive from the bead plan; do not copy from this file.
   - Re-derive implementation details from canonical source, not from old notes.

4. **Gate after each batch**
   - `ruff check <touched_file>`
   - `pyrefly check <touched_file>`
   - `make test PROJECT=<proj> MATCH=<pattern>`

5. **Record evidence**
   - `bd note <bead-id> "<command> exit <N>; <decisive output>"`
   - Store long outputs under `.beads/artifacts/<bead-id>/`.

6. **Finish**
   - Full validation across affected projects.
   - Commit with explicit pathspecs; no `git add .`.
   - Fast-forward push.
   - `bd close <bead-id>` with evidence summary.

## What not to put in the continuation prompt

- Full code blocks of replacement implementations.
- Recopied sections of `AGENTS.md`.
- Rigid numbered steps that ignore the current tree state.
- Hard-coded file paths or class names not validated against the live repo.

## Checklist

- [ ] Active bead identified and claimed.
- [ ] Plan and latest artifact read.
- [ ] Tree smoke-tested before edits.
- [ ] One step executed per cycle.
- [ ] Narrow gates run and green.
- [ ] Evidence recorded in bead with command + exit code + output.
- [ ] No code blocks dumped into bead notes.
