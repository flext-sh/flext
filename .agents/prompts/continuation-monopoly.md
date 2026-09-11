# Continuation Prompt: FLEXT Fix-Forward Monopoly

You are taking exclusive execution ownership of `/home/marlonsc/flext` until
the assigned work reaches a demonstrably healthy end state. You may coordinate
read-only research, but no other actor may mutate overlapping FLEXT paths while
you own the task. Preserve all pre-existing work as provenance; do not reset,
restore, clean, stash, rebase, normalize branches, or rewrite history.

Read, in order:

1. `/home/marlonsc/.agents/AGENTS.md`
2. `/home/marlonsc/.agents/UNIVERSAL_CORE.md`
3. `/home/marlonsc/flext/AGENTS.md`
4. `/home/marlonsc/flext/.agents/skills/flext-law/SKILL.md`
5. `/home/marlonsc/.agents/skills/inviolable-rules/SKILL.md`
6. `/home/marlonsc/.agents/skills/make-check/SKILL.md`
7. `/home/marlonsc/.agents/skills/verification-loop/SKILL.md`
<!-- Why: cutover to exact global generic skills after the local flext-inviolable-rules removal (mro-1o6t.1.1) -->

## Operating contract

- Work only on `0.12.0-dev`; `0.20.0-dev` is read-only comparison evidence.
- Use Beads as the sole work tracker. Start with `bd ready --json`, inspect
  `bd show <id> --json`, claim the selected Bead, and record evidence there.
- Use only root `make` commands for FLEXT validation. Never use direct tool
  commands to bypass the project dispatcher.
- Keep the implementation focused on the assigned live Bead. Do not perform
  branch equalization, broad fixture cleanup, bulk Bead changes, archive
  restoration, or governance migration unless the live Bead explicitly owns it.
- Archives and `agentes-legacy` are evidence only. Do not copy or activate
  their contents without an explicit current governing decision.

## Non-negotiable healthy-task rule

The project must not be left broken or in unowned WIP at the end of any task.
After the final code/configuration edit, and before marking a Bead complete,
you must prove all of the following from `/home/marlonsc/flext`:

```bash
make check CHECK_GATES=lint,pyrefly
make check PROJECT=<affected-project> CHECK_GATES=pyright,mypy
make test PROJECT=<affected-project>
```

Run supported targeted Make tests first, then the required project-level gates.
If the change crosses packages, generated files, fixtures, configuration, or
public facades, widen the scope. Manually use the changed public surface
(Make/CLI for workspace behavior, import/driver for libraries, or live service
surface where applicable).

A required non-zero result is a blocker, not a successful handoff. Fix it
forward, rerun every invalidated gate, or create one narrow linked Bead for a
genuine external blocker and leave the current Bead in progress. Never lower
coverage, skip gates, suppress diagnostics, or classify a failure as baseline
without fresh reproducible evidence and an owner.

## Required final report

Do not finish until you can report: active/closed Bead IDs; changed and
preserved paths; manual-QA behavior; global Ruff/Pyrefly result; affected-scope
Pyright, mypy, and pytest results; remaining external blockers; and the final
root plus affected-submodule Git status. Commit or push only with explicit user
authorization and explicit pathspecs.
