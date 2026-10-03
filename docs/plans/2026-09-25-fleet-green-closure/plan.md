---
title: FLEXT fleet green closure execution plan
updated_at: 2026-09-25T17:27:00Z
status: active
---

# Execution plan

<!-- TOC START -->

- [Objective](#objective)
- [Accepted operator decisions](#accepted-operator-decisions)
- [Ordered phases](#ordered-phases)

<!-- TOC END -->

## Objective

Adopt every current FLEXT lane and fix all failures forward until the public behavior is
preserved, every repository's native gates and CI are green, changes are integrated
through `0.12.0-dev`, and the increment leaves no open PR, unpublished branch, unretired
worktree, or unresolved Bead in its declared scope.

## Accepted operator decisions

- Python 3.13 local aliases require explicit declaration-owner context. If that context
  is absent or cannot prove the declaration, the original error propagates unchanged.
- SonarCloud administrative issue/configuration work is outside this execution; no
  `SONAR_TOKEN` is required.
- Canonical environment recovery through the public `flext-infra` generator is
  authorized when a generated `.envrc` prevents `make gen` from starting. All normal
  diagnostics, generation and validation remain root Make operations.
- Divergence is integrated with `git pull --no-ff`/`git merge --no-ff`; preserve and
  adopt all work. Never rebase, reset, discard, stash shared WIP, or force-push an
  authorized lane.
- A defect discovered during the work is part of the work. Do not classify failures as
  pre-existing or defer them merely because another lane exposed them.
- Repository-local catalog behavior follows current `cosmos-gitops` `origin/develop`:
  the typed local `config/workspace.yaml` declaration is authoritative, standalone
  repositories declare an empty member set, and Git remains the physical-topology
  authority. Tests use arbitrary values and the public detector; they do not copy Cosmos
  literals.
- Commits and pushes are authorized. Deliver through reviewed PRs onto each configured
  integration branch and keep the branch green before integration.

## Ordered phases

1. Complete `flext-infra` test convergence, build, review, publication, integration and
   post-merge proof.
2. Regenerate and validate `flext-cli` with the integrated `flext-infra` generator;
   retain the atomic interruption fix and replace obsolete generated Mise surfaces.
3. Integrate current `flext-core` and repair the explicit owner-context alias contract;
   run the complete native lifecycle and land it.
4. Reconcile all remaining FLEXT repositories and lanes through the fleet topology,
   adopting every claimed, deferred or blocked item whose acceptance remains live.
5. Prove final fleet state: native gates and CI green, integration SHAs current, no open
   increment PRs or unpublished branches, tracker evidence closed, and manual worktrees
   retired.

Each repository completes setup, generation fixed point, modernization, fix, format,
check, full test and build through selector-free root Make verbs. A failed invocation is
repaired at its owner and repeated; it never authorizes a phase change.
