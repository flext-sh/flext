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

## Mandatory three-boundary completion gate

Any edit or automated adjustment (sync, codegen, auto-fix, or upstream merge) is
code and must remain an atomic in-lane correction. At each boundary, from the
applicable workspace root, run fresh canonical evidence:

```bash
make check CHECK_GATES=lint,format,pyrefly
make check PROJECT=<affected-project> CHECK_GATES=pyright,mypy
make test PROJECT=<affected-project>
```

The affected-project commands cover every changed project and affected
consumer. Each boundary also requires real public-surface QA and generator /
consumer idempotence when generated outputs are involved.

1. **Final worker lane:** after the final lane edit or automated adjustment.
2. **Updated worker lane:** before review, non-destructively merge the latest
   target HEAD into the lane, then rerun all gates and QA. This is worker
   pre-merge evidence.
3. **Original target:** after orchestrator integration, rerun all gates and QA
   on the target branch. This is post-integration evidence and cannot be claimed
   before integration.

Use supported narrower Make targets only as iteration evidence, never to evade a
required gate. Never invoke bare `pytest`, `ruff`, `pyrefly`, `pyright`, `mypy`,
or `uv` as a bypass.

## Fail closed

- A non-zero required gate means the task remains open.
- Inconclusive, timeout-without-verdict, zero-project, partial-scope, or
  stale-HEAD evidence is not green and blocks review or integration.
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

## Handoff and landing

Before a handoff, report the active Bead, changed paths, preserved concurrent
paths, manual-QA outcome, full required gate results, and the next exact
root-Make command. Do not commit or push without user authorization. If
authorized, stage explicit paths only and never include unrelated work.
