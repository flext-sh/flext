---
name: flext-development-workflow
description: >-
  Execute a FLEXT change from workspace-root Bead ownership through narrow
  feedback, native Make gates, and scoped landing. Use for bootstrap, command
  discovery, implementation flow, and CI-equivalent validation.
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Development Workflow

## Start

1. Resolve the workspace root and claim the active Bead there.
2. Record exact path ownership before writes.
3. Read `docs/GOVERNANCE.md`, then load only the skills selected by
   `flext-context-routing`.
4. Inspect the owning declaration/config and all affected consumers.
5. Record which docs, skills, agent instructions, and provider entries are
   impacted.

## Bootstrap and Discovery

```bash
make help
make boot
```

`make help` is the current command inventory. Do not preserve a stale alias or
external dispatcher name in documentation.

## Change Cycle

1. Make the smallest coherent root-cause change.
2. Remove the superseded path in the same cycle.
3. Run the narrowest read-only gate from `flext-quality-gates`.
4. For performance changes, capture a `cProfile` baseline and an optimized
   profile following `docs/standards/performance-profiling.md`.
5. Update every affected consumer atomically.
6. Update docs, skills, agents, and provider metadata when reality changed; if
   not, verify impacted surfaces remain current.
7. Append state and evidence to the root-workspace Bead.
8. Widen to the affected Make gate only after narrow feedback is green.

Tests validate public behavior but never define the contract or source of
truth.

## Current Make Verbs

```bash
make check PROJECT=<project> CHECK_GATES=<gates>
make test PROJECT=<project> MATCH=<expression>
make docs DOCS_PHASE=<generate|fix|audit|build|validate>
make val VALIDATE_SCOPE=workspace
make ship WHAT=<save|tag|push|pr|rel>
```

The root `Makefile` owns this surface. Verify `make help` whenever it changes.

## Landing

- Stage and commit only owned paths with explicit pathspecs.
- Preserve all unrelated staged and unstaged work.
- Push only fast-forward after scoped and native gates pass.
- Record commit SHA, push output, and remaining risk in the same Bead.
- On remote divergence, stop and report the exact rejection plus local and
  remote SHAs; never rebase or force-push autonomously.

## References

- [`flext-quality-gates`](../flext-quality-gates/SKILL.md)
- [`flext-beads-coordination`](../flext-beads-coordination/SKILL.md)
- [`docs/GOVERNANCE.md`](../../../docs/GOVERNANCE.md)
- [`ADR-007`](../../../docs/architecture/adr/007-worktree-transaction-performance.md)
- [`docs/standards/performance-profiling.md`](../../../docs/standards/performance-profiling.md)
