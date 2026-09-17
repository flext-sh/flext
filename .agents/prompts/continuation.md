# Continuation Prompt: FLEXT Fix-Forward Monopoly

You are taking bounded execution ownership of the assigned Bead and paths until
the work reaches a demonstrably healthy end state. Coordinate thematic agents
through disjoint owners, re-read shared paths before mutation, and reconcile
overlap by fix-forward. Preserve all pre-existing work as provenance; do not
reset, restore, clean, stash, rebase, normalize branches, or rewrite history.

Read, in order:

1. `~/.agents/AGENTS.md`
2. `./AGENTS.md`
3. `.agents/skills/flext-law/SKILL.md`
4. `~/.agents/skills/project-wide/shell/make-check/SKILL.md`
5. `~/.agents/skills/agent-wide/verification/verification-loop/SKILL.md`

## Operating contract

- Work only on `0.12.0-dev`; `0.20.0-dev` is read-only comparison evidence.
- Use Gas City Beads as the sole work tracker. Run every tracker command as
  `direnv exec <repo> bd ...`: prime the context, inspect the selected Bead,
  claim it, and record evidence there.
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
you must prove all of the following from this workspace:

```bash
make setup
make gen
make mod
make gen
make gen
make fix
make fmt
make check
make test
make build
```

Every Python test selection retains the canonical testmon cache; never bypass,
clear, or replace it, including for an explicit full run. Manually use the changed public surface
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
