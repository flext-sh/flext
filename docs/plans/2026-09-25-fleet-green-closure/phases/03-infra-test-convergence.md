---
title: Phase 03 - flext-infra test convergence and integration
updated_at: 2026-09-25T17:27:00Z
status: active
---

# Phase 03: `flext-infra` test convergence and integration

## Entry state

- Worktree: `/home/marlonsc/fleet-closure-lanes/infra-convergence-20260925/flext-infra`
- Branch: `fix/infra-green-convergence-20260925`
- Local/published HEAD: `44b3381eaca295eeba280142572f62770a691381`
- Current fetched integration: `0f5d0cd7042caba1eca841e9678a2229606c0182`
- PR: <https://github.com/flext-sh/flext-infra/pull/861>, open draft, behind
- Authored convergence batch: dirty and deliberately uncommitted pending full test
  evidence
- Static lifecycle through `make check`: green
- Full `make test`: no valid result after the batch; prior invocation ended 130 by
  operator-requested handoff

## Owned behavior

This phase owns the repository-local catalog fixtures, layout context, Rope PEP 701
occurrence behavior, facade-source invalidation, CI candidate reuse, release fixtures,
Mise seed fixtures and pytest runner accounting/performance. It must preserve raw
exceptions, complete test accounting and public consumer behavior.

## Execution loop

1. Run `rtk make test` at the worktree root.
2. Read the complete report. Repair every failure/error/warning/skip at its canonical
   owner; do not raise timeouts, retry, suppress, mock the owner, or narrow collection.
3. After any mutation, repeat `make gen`, `make mod`, two `make gen` fixed-point runs,
   `make fix`, `make fmt`, `make check`, and full `make test` as affected by the change.
4. Run `rtk make build` only after the full test report is green.
5. Obtain independent review of the complete diff. Address every finding and rerun
   invalidated gates.
6. Commit explicit paths and push fast-forward. Because the PR is behind, integrate the
   current `origin/0.12.0-dev` using a no-ff merge, resolve by adoption, and rerun the
   complete lifecycle on the merged result.
7. Update PR 861 from draft, require non-skipped green CI/review, merge through the
   configured integration branch, then run post-merge proof at the exact integrated SHA.

## Stop condition

This phase completes only when `flext-infra` is integrated into `0.12.0-dev`, native
post-merge gates and required CI are green, the exact SHA is recorded in the canonical
Bead, PR 861 is closed by integration, and its manual worktree can be retired. Until
then the next phases remain blocked by this producer.
