# Lean Critical-Path Plan — Checkpoint 0.12.0 (cycle-green)

> Created 2026-09-09 18:50 UTC from live session learnings. Supersedes the
> "violation-zero" reading of Phase A. Grounded in saved acceptance
> `closeout.checkpoint_0_12_0`: residual violations are accepted at 0.12.0
> provided flext-infra and its verbs run complete cycles.

## Context (verified this session)

- flext-infra published at `459ddf9c4` on `origin/0.12.0-dev`; PRs #665/#666
  merged; lane work (eb5aee3cf, 2ac58f5503) integrated no-ff.
- Superproject integration base pushed at `c424043b85`; 32 gitlinks synced;
  `make gen` fleet 32/32 conform (exit 0).
- `make gen` on the tip: 1432 findings. Census (full gate log):
  - namespace 1388 (NS-STRUCT-001=309, -002=170, CONTRACT-001=160,
    -003=117, -004=77, ...; top files: rope_analysis.py 31, promoted/base.py 21,
    census.py 15) — pre-existing debt exposed by newly-activated gates
    (owner bead `flext-hkz4p`), NOT a regression.
  - runtime-census 292 usages — same class of pre-existing debt.
  - loc-cap 5 (config.py 3679, conform.py 2879, rope_analysis.py 1709,
    test_codegen_conform.py 1474, codegen.py 1124).
  - duplication 24 (clone codemod yml rules), silent-failure 6, mypy 1,
    lint 7 (ALREADY FIXED in working tree: ISC004 ×5 + PT011).
- Beads already reduced 559 → 479 this session (81 SUPERSEDED, zero
  live descendants, evidence recorded in `flext-y3qpq.4`).
- 30 semver member lanes (`flext-1wjg1.16.1/.2/.4/.6–.33`) all repeat the
  same per-member step (pin → regen → PR → gates).

## Strategy: cycle-green first, debt re-parented, one fleet regen

### Fase A0 — Record dispositions (docs + beads, do first)

1. Append the lean-strategy section to
   `.kilo/plans/1788961161018-flext-012-checkpoint-status.md`
   (dispositions + automation policy; text drafted in this plan's
   "Fase A1/A2" sections).
2. `bd update flext-1wjg1.16.34` and `bd update flext-h2ffh` with the
   disposition: cycle-breakers = duplication 24 + silent-failure 6 + mypy 1
   (lint 7 already fixed); accepted-residual = namespace 1388 +
   runtime-census 292 + loc-cap 5 → 0.20 (`flext-ik359`); grounding =
   `closeout.checkpoint_0_12_0`; census already posted in `flext-hkz4p`.
3. Update the CSV `beads-reval250909.csv` summary row with the new
   disposition.

### Fase A1 — Cycle-breakers now (~31 mechanical items)

1. duplication 24: delete the clone yml rules (`ban-json-loads-paired-validate`
   clone of `ban-model-rebuild`; `ban-serialize-as-any-flag` clone of
   `require-future-annotations`; `fstring-fail-missing-exception-review-test`
   clone); extend the one owner, rewire consumers. Zero-residue deletion.
2. silent-failure 6: rewrite broad-except/sentinel branches at
   `network.py:33`, `docs_serve_e2e_tests.py:57`, `census_tests.py:34`,
   `test_project_gitignore_patterns.py:90`, `test_project_mise_tools.py:57`,
   `test_main_cli.py:210` — propagate via `r.fail`, no sentinels.
3. mypy 1: remove/justify the unreachable statement at
   `qualified_names.py:52` (root cause: dead branch → delete).
4. Fast iteration: run the wrapped CLI
   `flext_infra check run --gates duplication,silent-failure --projects .`
   per wave; full `make gen` only at wave boundary for evidence.
5. Close `flext-h2ffh` / `flext-1wjg1.16.34` with gate evidence; record
   accepted-residual in `flext-hkz4p` (census already posted).

### Fase A2 — Accepted-residual → backlog (NOT release blockers)

- namespace 1388 + runtime-census 292 + loc-cap 5: re-parent to the 0.20
  program under `flext-ik359`. Execution there uses:
  - `make mod` (canonical codemod: ast-grep + rope +
    private-import cutover) for mechanical classes (renames, nesting,
    private-import rewires) — never hand-edit generated surfaces; fix the
    generator, regen.
  - `code-review` skill (manual, per wave diff) + `scope-nav` for
    reference tracing when rewiring consumers.
  - Read-only subagents for per-rule census; central hand for edits.

### Fase B — ONE fleet regen replaces the 30 lanes

1. With A1 landed and pushed, run `make gen` fleet-wide (already
   proven 32/32 conform), then root `make fmt/fix/check/test`.
2. Close the 30 member lanes (`flext-1wjg1.16.1/.2/.4/.6–.33`) as
   SUPERSEDED by the bulk regen (evidence: gen commit + root gates);
   keep owner `flext-1wjg1.16`.
3. Net: −30 in_progress beads, zero code written per member.

### Fase C — Version, publish, accept

1. `make release-plan/version/tag/build`.
2. `make publication INDEX=Y` (trusted publishing OIDC).
3. Clean-install verification from PyPI in a fresh env.
4. Close `flext-1wjg1.11/.12/.13/.14`, `flext-y3qpq.5/.6` with merged SHA +
   artifact digests + runtime evidence. Residual debt documented in the
   acceptance beads per `closeout.checkpoint_0_12_0`.

### Fase D — Tracker shows only the critical path

- Re-parent post-release epics to `flext-ik359`: `wkii`(58), `wshr`(51),
  `2wjm`(23), `jbfz`, `p57t`, `mbowt`, `dz4ib`, `vjj1s`, `00ka`, `43ng`,
  `6s34`, `he00`, `now1`, `s5zp`, `0kl7`, `buxn`, `ehid`, `7akn`, `j47u`,
  `wgwh`, `d421`, `i6nq`, `hsiu`, plus the A2 residual beads.
- Continue the reval250909 CSV sweep incrementally after release.

## Efficiency levers (learnings encoded)

| Lever | Effect |
|---|---|
| `closeout.checkpoint_0_12_0` acceptance | Phase A shrinks from 1432 fixes to ~31 |
| One fleet regen | −30 lanes, no per-member PR cycles |
| Wrapped CLI per-gate iteration | seconds instead of 310 s per loop |
| Generator-first on generated surfaces | one fix kills N violations |
| `make mod` for mechanical classes | bulk renames without hand-edits |
| code-review skill per wave | catches regressions before landing |
| Backlog re-parenting | active board = ~10 release beads |

## Validation

- A1: `make gen` — duplication/silent-failure/mypy/lint = 0;
  residual = namespace + runtime-census + loc-cap only, documented.
- B: `make gen` 32/32 conform + root cycle evidence.
- C: `make publication INDEX=Y` success + clean-install import
  proof + digests in acceptance beads.
- Every closure carries command, cwd, exit code, decisive output.

## Execution notes

- Plan Mode blocked the doc/bead mutations this session (permissions); A0
  must be executed by the implementation agent first.
- Working tree already carries the lint fixes (ISC004 ×5 + PT011) in
  `flext-infra` tests — land them with the A1 wave commit.
- Check tip is the published base `459ddf9c4` (`origin/0.12.0-dev`); A1
  commits go through the canonical cycle then push to the integration base.

## Out of scope (explicit)

- Zero-ing the namespace 1388 / runtime-census 292 before 0.12.0
  (accepted-residual; lives in the 0.20 program).
- Any hand-edit of AUTO-GENERATED surfaces (facets, `[MANAGED]`).
- New lanes per member (superseded by the bulk regen).
