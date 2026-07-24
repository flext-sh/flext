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

## Handoff and landing

Before a handoff, report the active Bead, changed paths, preserved concurrent
paths, manual-QA outcome, full required gate results, and the next exact
root-Make command. Do not commit or push without user authorization. If
authorized, stage explicit paths only and never include unrelated work.
