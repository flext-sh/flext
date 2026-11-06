# Campaign record 2026-11-05 — make check zero-defect (workspace-wide)

Lane: `upload-20261007` (workspace dev tip, umbrella + all 31 members).
Session: main ZCode session (make-check campaign), coordinated with the live writer.

## What the campaign found (root causes, proven)

1. **Checker-level defects (cured, on the tip):**
   - Root `[tool.pyright]` include listed the retired `flext-infra/scripts`
     (1 of 116 include entries + 1 stale `executionEnvironment` with
     `root = "flext-infra/scripts"`). pyright was invoked with a nonexistent
     path → error path → 541–600s+ runs → `timed_out=True` → `interrupted`
     → the workspace loop broke after the first project → 31 members
     `INCOMPLETE` → "quality check target accounting is incomplete".
   - The umbrella pyright analyzes 4,829 files in a measured **744s**, exceeding
     the gate's `TIMEOUT_LONG=600s`. Cured: new constant
     `TIMEOUT_UMBRELLA: ClassVar[int] = 1200` (`flext-infra/src/flext_infra/_constants/validate.py`)
     used by `gates/pyright.py`; the gate no longer kills the umbrella run.
2. **Hook/partition reality (new map):** pre-commit runs the CI=C partition
   (lint+format+markdown) over the whole governed tree; on the umbrella this
   exceeds the hook deadline (Error 124 observed) — root commits only flow in
   writer-wave windows until that deadline is repaired at its owner.
3. **Finding map (run of 16:26, run2 17:06):** ~2,200 findings: pyrefly 1,161
   (flekt-infra 768, flekt-ldif 160, flekt-api 48, flext-tests 48,
   observability 35, quality 30, root 14 = `p.Root.PipelineStageData` family),
   root slow-gates (codemod 440–448 with 278 ban-cyclic-import, mypy 66 —
   51 are examples/tests facade drift + 9 facade-composition: duplicate-base
   FlextApi* + rebind multi-type-assign), flekt-infra lint 170 (ALL ruff-fixable,
   cured by `make fix`+`make fmt` → lint 0), flekt-tests lint 1, markdown 1
   (cured), duplication 134 (generated template files, same-template
   conftest.py ×32 — needs operator-authorized exclusion), smells 14
   (generated lazy-binding facades — owner is the flekt-infra template), layout 1
   (`requirements-infra.txt` non-canonical root entry — cure: add
   `keep_root_files` override in flekt-infra config/codegen.yaml layout section;
   file is generated+consumed, do NOT delete).

## Landed on the tip (content-verified in HEAD)

- Root pyproject: stale `flext-infra/scripts` include entry + stale
  executionEnvironment removed (TOML valid; 115/115 include paths exist).
- flekt-infra: `TIMEOUT_UMBRELLA=1200` + pyright gate bound (in HEAD).
- flekt-infra: `make fix`+`make fmt` → lint 170→0 (in the tree, writer wave absorbs).
- Root: ADR-006 MD013 wrap (in the tree, writer wave absorbs).
- Members unification (script): **20 merge commits** on member tips
  (MERGED-OK); ANCESTOR branches skipped; dirty-collision merges recorded
  MERGE-FAILED/SKIPPED-WIP.
- Umbrella unification: 6 MERGED-OK (incl. `ws/submodule-0.12`,
  preserve snapshots); fix/*+land/* lanes BLOCKED by submodule gitlink
  conflicts — their member pointers diverge from the tip; resolution needs an
  operator ruling (take tip gitlinks vs take branch content per branch).

## Deferred with exact cures (next session queue)

1. pyrefly waves per project (agents were throttled by the harness concurrency
   limit twice; run per-project cure lanes: flekt-infra 768, flekt-ldif 160,
   api 48, tests 48, obs 35, quality 30, then the 1–10 tails).
2. Root facade duplicate-base (generated files — owner is the flekt-infra
   facade_members template; the writer's current WIP touches exactly that).
3. Root examples/tests facade drift (51 findings — update consumers to the
   current facade: `m.Root.PipelineStageData` exists at runtime; static
   resolvability of the composed namespaces is the open question).
4. duplication 134 → operator-authorized exclusion for template-rendered
   identical files (tooling.yaml is ruling-protected).
5. smells 14 → flekt-infra template cure (generated facade boilerplate).
6. layout 1 → add `keep_root_files: [requirements-infra.txt]` for the flext
   root in flekt-infra config/codegen.yaml `layout.project_overrides`
   (file is generated + consumed by Makefiles; do NOT delete).
7. Root commit-hook deadline (Error 124) → raise/repair at the hook owner so
   umbrella commits flow without writer-window dependence.
8. Conflicted fix/*+land/* umbrella lanes → operator ruling on gitlink
   conflicts, then re-merge with content resolution.
9. Register the campaign bead in the Gas City store (`gc bd create`) and
   re-run the automation partition (`make check CHECK_PHASE=primary`) as the
   standing watch signal.
