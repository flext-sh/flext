# ADR-037: `make check` Is the Single Gate

## Status

Accepted (operator, 2026-11-25). Implemented by flext-infra #2791 (`4bf12d062d`)
and the fixed-point convergence of `feat/check-converges`.

## Context

The common Make surface exposed `gen`, `fix`, `fmt` and `lock` beside `check`.
Agents ran them as a separate manual cycle before `check`, in varying orders,
and a lock could be rewritten by any of them. Two paths produced the same tree,
and CI could not tell a forgotten local step from a real defect.

## Decision

1. The common verbs are `setup`, `upg`, `mod`, `check`, `tests`, `tests-full`,
   `help`, `build` and `clean`. `gen`, `fix`, `fmt` and `lock` are not public.
2. Outside CI, `make check` (default `CHECK_PHASE=primary`) first converges
   gen → fix → fmt to a fixed point: passes repeat until the working tree stops
   changing, and a tree still moving after a bounded number of passes fails.
   Then the read-only gates run.
3. In CI (`GITHUB_ACTIONS` sets `CI := Y`), `make check` converges nothing; its
   gates are verify-only and fail when any byte would change.
4. Locks change only through `make upg`.
5. The host load queue applies only to the full forms (`check-full`, `mod-full`,
   `tests-full`).
6. Delivery order: fetch + `merge --no-ff` of the integration tip → `make check`
   → runtime validation → `make tests` → commit → PR → merge → release deploy.
   Work from another lane is adopted with `git cherry-pick -x`.
7. FLEXT consumes nothing from AI Hub for this cycle.

## Consequences

- One local command leaves the tree in its canonical state; CI proves it was run.
- Instructions naming `make gen`, `make fix`, `make fmt` or `make lock` are stale
  and are corrected at their owner.
- A non-converging generator or fixer surfaces as a failing `make check` instead of
  a silent oscillation.
