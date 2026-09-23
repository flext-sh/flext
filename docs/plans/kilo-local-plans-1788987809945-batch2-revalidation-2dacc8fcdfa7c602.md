# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md

<!-- TOC START -->

- [Goal](#goal)
- [Starting state (verified 2026-09-10)](#starting-state-verified-2026-09-10)
- [Tasks (ordered)](#tasks-ordered)
- [Rules applied](#rules-applied)
- [Validation](#validation)
- [Out of scope](#out-of-scope)

<!-- TOC END -->

(Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there

# Plan: Batch-2 bead revalidation (238 open beads → final aligned state)

## Goal

Finish the fleet bead hygiene program: every open bead revalidated against the
integration branch and worktrees, aligned to epics, and classified bugfix/hotfix with
standardized tags in descriptions. Final state: bz (bd ready) contains only real,
current, prioritized work.

## Starting state (verified 2026-09-10)

- 238 open beads: P0=8, P1=149, P2=55, P3=26; 122 with parent, 116 standalone.
- All tagged; batch-1 closed 7 beads, deferred 3 (flext-qb4y.8, flext-7akn, flext-sht2 →
  2026-10-01).
- Integration branch 0.12.0-dev tip f39e4b7b84; release worktree at flext-release-012/.

## Tasks (ordered)

1. **P0 verification round** — for each of the 8 P0 beads, run the exact
   reproduction/measurement on integration tip and either close with command evidence
   (exit code + decisive output) or downgrade/reprioritize with the finding. Known
   candidates: flext-5k9r7 (fix was reverted by 8ac1b2d5b2 — re-verify live), flext-cpkk
   (CI green hold), flext-y3qpq.5, flext-dipb.\*, flext-sikjh, flext-ozlu0.
2. **P1 batch fix-evidence sweep** — grep `git log` per remaining P1 bead ID (as done in
   batch-1); any bead whose ID appears in a landed, non-reverted fix commit → close with
   commit evidence; fix commit reverted → add note `reverted:<sha>` and keep open.
3. **Epic alignment** — review the 116 standalone beads; beads whose topic matches an
   existing epic root (flext-wkii, flext-y3qpq.2, flext-y3qpq.4, flext-mbowt,
   flext-i6nq, flext-wgwh) get `--parent` attached; genuine standalone bugfix/hotfix
   stay orphan and MUST have tags `kind:bugfix`/`kind:hotfix` in the description header,
   standardized format: `kind:bugfix | scope:<member>` as first description line.
4. **Description standardization** — append standardized classification line to each
   open bead description:
   `kind:<bugfix|hotfix|feature|refactor|task> scope:<owner/member> status:<open|deferred>`.
   No rewriting of original prose.
5. **Dependency cleanup** — for each open bead with dependencies: verify each dep exists
   and is open; closed/closed dep → remove the edge; blocked pairs that are actually
   independent → remove, so `bd ready` unblocks real work (this is the "destravar"
   requirement).
6. **Title normalization** — strip noise prefixes (`[bug]`, `(BUG)`, duplicated
   `flext-<scope>:` when body already names scope); keep one language per epic lane:
   descriptions in PT may stay, title in EN for gates/T0/RC lanes.
7. **Deferred reconciliation** — P3/deferred beads without evidence stay deferred to
   2026-10-01; any deferred bead with a stale defer value gets normalized.
8. **Final report** — counts by kind/priority/epic, list of closed beads with commit
   SHAs, list of deferred, list of reparented. Save to memory.

## Rules applied

- Root: `~/flext`, all mutations via `bd`; never hand-edit `.beads/issues.jsonl`.
- `make` verbs untouched: this plan is tracker-only; no source code writes.
- Evidence rule: every closure carries command/commit SHA as reason.
- Fix-forward: no defer-sweep of beads with recent interpreter evidence (batch-1 filter
  already proven: 51 of 54 stale had evidence).

## Validation

- `bd ready --json` count decreases monotonically; no dup closes.
- `bd lint / bd doctor` clean at end.
- Cross-check: 0 open beads with both `kind:bugfix` label and missing standardized
  description line.

## Out of scope

- Implementing any of the beads' actual fixes.
- Open-plan files/PRs beyond tracker state.
