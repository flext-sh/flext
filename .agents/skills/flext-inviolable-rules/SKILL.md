---
name: flext-inviolable-rules
description: "Enforce FLEXT's fail-closed task-completion rules: healthy environment, required root-Make quality gates, manual QA, Bead evidence, and no broken WIP."
---

# FLEXT Inviolable Rules

## Before mutation

1. Read root `AGENTS.md` and `bd show <id> --json`.
2. Inspect `git status` at the root and affected submodule. Treat all existing
   changes as provenance owned by someone unless the live Bead proves yours.
3. Identify the public surface to manually exercise and the exact root-Make
   gates that will prove the task complete.

## Mandatory completion gate

After the final implementation change, from `/home/marlonsc/flext` run:

```bash
make check CHECK_GATES=lint,pyrefly
make check PROJECT=<affected-project> CHECK_GATES=pyright,mypy
make test PROJECT=<affected-project>
```

Use supported narrower Make targets first where appropriate, but never use a
narrow command to evade a failing required project gate. Widen validation when
the change crosses packages, generated files, fixtures, configuration, or
public facades. Never invoke bare `pytest`, `ruff`, `pyrefly`, `pyright`,
`mypy`, or `uv` as a bypass.

## Fail closed

- A non-zero required gate means the task remains open.
- Do not reduce coverage, add a suppression, skip a test, or call a baseline
  failure harmless without current command evidence and an owning linked Bead.
- If the environment is broken, fix it forward in the task or create one
  narrow `discovered-from` blocker; do not close the implementation as done.
- If an automated adjustment (sync, codegen, auto-fix, upstream merge) is
  part of the task, validate it through the same root-Make gates and record
  evidence in the Bead before closing.
- Manually use the changed public surface. Record the observed behavior,
  command, cwd, exit code, and decisive output in the Bead.
- A test pinned to a config-owned value that breaks on a legitimate
  config/settings change is a TEST DEFECT, never a reason to freeze config:
  fix the test to read the SSOT or the generator round-trip (P0 —
  cosmos-main-hr9e). This applies to all test tiers, markdown examples, and
  docstring snippets validated by the pytest plugin.

## Continuous green checkpoints

- Keep checkpoints short and complete. After every state-changing stage, append
  the current status, orientation, owned paths, remaining scope, and exact
  command evidence to the Bead; never defer Beads metadata or evidence until
  handoff.
- Resolve ordinary uncertainty from evidence and continue. Do not accumulate
  hypothesis loops or leave completed, validated work only in the local tree.
- A checkpoint is green only after every applicable canonical root-Make gate
  passes with zero lint errors and its manual public-surface check is recorded.
  Never commit or push a red, partial, or incompletely evidenced checkpoint.
- When push authority exists, stage explicit owned paths, commit the completed
  green checkpoint, and immediately fast-forward push the worker branch. Workers
  never rebase, force-push, merge, or promote main; reviewed promotion belongs to
  the orchestrator.
- Send the orchestrator a concise progress heartbeat at least every five minutes
  while work remains active, naming the stage, latest evidence, next action, and
  any changed risk or blocker. Reporting never pauses execution.
- Before any critical decision, stop, record the pending decision, options, and
  consequences in the Bead, and ask the operator one precise confirmation
  question. The minimum critical set is destructive or irreversible action,
  competing public-contract or architecture outcomes, security or privacy,
  production/release/main promotion, authority conflict, and material scope or
  acceptance change. Never infer critical intent.

## Handoff and landing

Before a handoff, report the active Bead, changed paths, preserved concurrent
paths, manual-QA outcome, full required gate results, and the next exact
root-Make command. Without push authority, stop before committing or pushing and
record the blocker. With authority, do not hand off completed local WIP: land the
green checkpoint through an explicit-path commit and immediate fast-forward push,
then append the commit SHA and push evidence to the Bead.
