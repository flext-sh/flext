# RCA & PR Readiness Rules

1. **RCA mandate**: reproduce through `make check`/`make tests`; fix at the canonical
   owner (no suppressions, fallbacks, shims or mocked owners).
2. **Item deadlines**: 2 s ordinary, 20 s slow. A case that cannot fit the ordinary budget
   is declared at the slow tier from measurement; a budget is never raised to hide a
   regression.
3. **PR readiness**: `make gen`/`fmt`/`fix` no-op, `CHECK_PHASE=primary make check` exit 0,
   `make tests` green, `make tests-full` green over the complete applicable population
   with harness gates reported NOT EXECUTED; the merged revision is re-proven at its real
   entry point.
4. **Merge**: one subject per PR, merge commit; the ADR-0038 administrative landing is the
   integration-branch approval, with green required checks as the gate.
5. **Boundary**: never use `flext-infra` or the Makefile for workspace sync, worktree
   cleanup, PR validation or RCA capture.
6. **Contracts**: `docs/guides/wip-session-workflow.md` and `docs/worktrees.md` in
   `ai-hub` own the full lifecycle and placement rules.
