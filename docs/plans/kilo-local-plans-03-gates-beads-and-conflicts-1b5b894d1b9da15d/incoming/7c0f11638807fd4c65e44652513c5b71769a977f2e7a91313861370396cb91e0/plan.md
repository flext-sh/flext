# Gates, Beads, and Resolved Conflicts

## Gate evidence ledger

| Evidence | Tree/time | Result | Planning consequence |
|---|---|---|---|
| flext-infra native `make test` | 2026-09-16 19:19 local report | 2,626 collected; exit 2; killed at 600 s (`raw_return_code=-15`) | Current red evidence. Start from report tracebacks before another blind full run. |
| Named conform failures | Same report | dependency-surface ownership; two ProjectNew fixed-point variants; existing-manifest tree convergence | First product/test classification slice. |
| surf-hornet targeted tests | Historical lane | 36/36 reported green | Scope evidence only, not suite or integration green. |
| surf-hornet fleet gen | Historical lane | First run published env files; serialized later run reported zero publications | Reprove on current Gas-City-only design and integrated SHA. |
| surf-hornet `make mod` / check | Historical lane | 64 detection-only / 0 actionable; 914 findings | Red; follow-up Beads required. |
| rope audit check report | Older rope tree | 852 findings; markdown/runtime-census/duplication red | Stale diagnostic, not current result. |
| native Claude session | 20:40Z–22:53Z | No complete flext-infra gate ladder | No flext-infra phase may be marked complete from this session. |

## Gas City conflict resolution

Two historical observations conflict:

1. surf-hornet reported healthy runtime publication on port 14499 and successful `direnv exec` smoke;
2. a later rope audit reported missing/unhealthy Dolt publication and intermittent MySQL timeout.

Resolution: neither report is timeless. Phase 0 must perform a live `direnv exec <rig> bd show <active-bead> --json` and city health proof. The latest operator correction is binding: **Gas City is the sole Beads engine**. No embedded/local alternate database may be created or selected.

## Tracker owner reconciliation

Re-read live records through Gas City before mutation; passive files are not authoritative.

| Intent | Candidate Beads | Provisional owner decision |
|---|---|---|
| Generator/enforcement stabilization | `flext-5fxu6.4` under `flext-5fxu6` / `flext-itpd1.1` | `flext-5fxu6.4` remains the primary technical owner unless live Bead says otherwise. |
| Journal/lock | `flext-dcge0`, `flext-fkfmu` | Elect one after live read; preserve the PIN-SHA/per-repo lock design and supersede the duplicate only after dependency transfer. |
| Invalid tests | `flext-9m4gc`, `flext-wjozx`, `flext-c4k44`, `flext-4v4tf` | Prefer `flext-c4k44` for flext-infra-local acceptance; keep one fleet parent only if scope is distinct. |
| Setup/toolchain | `flext-5k9r7` | Active dependency; do not duplicate. |
| Generation fixed point | `flext-3d8bv`, historical `flext-za816` | Reconcile current scope and status. |
| Namespace/test budget | `flext-z4ydq`, `flext-t9q8h` | Preserve as separate measurable budgets only if acceptance differs. |
| Native Claude new blocker | `flext-5fxu6.4.27` | Read live; built-in verb shadowing may precede later lifecycle proof. |

## Conflict decisions

1. **Main checkout vs rope lane:** the `_lazy_analysis` defect was observed in the main checkout but not in rope `flext-infra@469b26b4e`. Treat it as parallel WIP to adjudicate, not as a universal current defect.
2. **Static CRG vs runtime coverage:** CRG can miss dynamic dispatch (`tm.ok`, `transaction.state.*`). Graph gaps prioritize inspection but never authorize duplicate tests or production changes.
3. **Test expectation vs generated Make:** the template/runtime uses Mise-owned `override UV := ... exec -- uv`; the obsolete `UV ?= uv` expectation is invalid, subject to public generated-project runtime proof.
4. **Half-migrated conform:** `conform.py` remains runtime owner while `_conform/*` contains parallel/duplicated implementations. Do not patch both indefinitely. Centralize contracts, then complete one MRO cutover and delete the god copies.
5. **LOC gate:** the operator requires ≤200 logical LOC as the completion outcome. A temporary higher gate may exist only as an explicit migration stage; it is not acceptance and may not hide touched-module debt.

## Immediate next slice

1. Read current integration tips and current WIP; classify every hunk against this matrix.
2. Prove Gas City connectivity and reread the active/overlap Beads.
3. Confirm whether built-in Make verb shadowing and `_lazy_analysis` mismatch survive on the integration tip.
4. Adopt the smallest producer fix and run `make setup`; stop at its first causal failure.
5. After setup is green, prove gen fixed point before continuing to mod/fix/fmt/check/test/build.
