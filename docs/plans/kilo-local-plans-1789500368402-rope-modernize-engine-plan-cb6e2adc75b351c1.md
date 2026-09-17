# Rope Modernize Engine — Exterminate ast/libcst/re, One CLI, ai_hub Pilot

## Objective

Re-platform the FLEXT modernization stack onto **rope + parameterized YAML rules + `make mod` (ast-grep/sed)** only. Exterminate every Python-side `ast`, `libcst`, and `re`-based engine in `flext-infra`. All adjustments run through **one CLI** (`flext-infra codegen conform`) with per-component toggles and dry-run. Pilot on `~/ai-hub`. Every cycle lands 100% green: ruff, pyrefly, pytest collection — nothing half-done. Keep beartype runtime in flext-core untouched.

## Ground truth (verified this session)

- Current state: flext-core collection **2683 tests / 0 errors**; circular-import class and `result.py` twin-class runtime defect already fixed (board `board_8032fb78`).
- Extermination inventory in `flext-infra/src/flext_infra`: **8 libcst files** (`codegen/_lazy_init_import_alignment.py`, `_utilities/{qualified_names,compatibility_alias_cst,private_import_cst,class_nesting_cst,class_nesting_references}.py`, `transformers/mro_remover.py`, `refactor/project_alias_migrator.py`) + **37 `import ast` files** (transformers/, detectors/, fixers/, gates/, \_utilities/, codegen/).
- Rope foundation already exists: `_utilities/_rope/project.py`, `rope_structure.py`, `rope_imports.py`, `rope_source.py`, `fixers/rope_fixer.py`.
- One-CLI anchor exists: `m.Infra.CodegenConformRequest` (`_models/_config/artifact.py:417`) with `root` / `what` / `scope` / `mode` — **`mode=CHECK` is already dry-run**, `mode=APPLY` is atomic apply via `CodegenFilePlan` (before-state + desired bytes, transaction-owned). Route: `services/cli_routes_codegen.py:67` (`codegen conform`).
- `make mod` is canonical (root `Makefile:736` → `RUN_PUBLIC,mod`) — ast-grep + sed. **Keep.**
- Beartype runtime in flext-core (`_beartype_bootstrap`, `beartype_engine`) — **Keep.**
- Enforcement catalog: 79 rules across 6 source kinds (beartype, code_smell, flext_infra_detector, flext_tests_validator, ruff, runtime_warning) — this is the parameterized rules-as-data pattern to extend; policy rows live in `flext-infra/config/*.yaml` (there is no `config/rules/` dir today; new policy files go under `flext-infra/config/` following `tooling.yaml` conventions).
- Layer SSOT: `flext-infra/config/tooling.yaml` `lazy-init` block (`import-layer-order`, `reverse-import-mode: type_checking`, `forward-import-form: relative_dot`) — already alias-repaired this session.

## Root rules (non-negotiable)

1. **Three instruments only**: rope (semantic refactor/rewrite), `make mod` (declarative ast-grep YAML + sed codemods), parameterized config YAML rows (detection/policy). Python `ast`/`libcst`/`re` engines are exterminated, never wrapped — consumers rewired to the three instruments.
2. **One CLI**: `flext-infra codegen conform`. Extend `CodegenConformRequest` with `components: frozenset[CodegenConformComponent]` (typed enum; default = config-owned from `tooling.yaml`, never hardcoded). `mode=CHECK` = dry-run; `mode=APPLY` = atomic apply. No parallel CLIs, no ad-hoc scripts — migrated or deleted.
3. **Import-alignment law** (same phase, re-platformed to rope): forward import → relative-dot in place; reverse import unused at runtime → merged single `if TYPE_CHECKING:` block (add `from typing import TYPE_CHECKING` if absent); reverse import runtime-needed → **phase fails** with module+symbol diagnostic (blocking beats generating runtime-broken output — operator law). Idempotent: second run is a no-op. Output must be ruff/pyrefly-clean by construction.
4. **Fix-forward adopt**: concurrent agents share the board; never stash/revert; adopt overlapping work; `rm -f .git/index.lock` on stale locks.
5. Per-cycle gates integral: `make fix` → `make fmt` → `make check` → `make test` at workspace root; pytest collection per touched project. A task is done only when its slice is green.

## Phase 1 — this cycle (integral, lands green)

1. **Rope spike (first, throwaway)**: verify installed rope API surface for the engine needs — `rope.refactor.importutils.module_imports.ModuleImports` (`get_imports`, `add_import`, `remove_import`), `rope.base.change` ChangeSet composition, `codeanalyze`/`worder` for TYPE_CHECKING-block insertion. If the API cannot express the alignment law, STOP and ask the operator before improvising.
2. **Re-platform `_lazy_init_import_alignment.py`**: delete the libcst visitor/rewriter entirely (`_ImportAlignmentVisitor`, `_rewrite_module`, `_rewrite_import`, helpers — no shims). New rope-native implementation: rope index (`FlextInfraRopeWorkspace`) already opened by the lazy-init phase; classify each project-internal import by layer from `config.Infra.tooling.lazy_init`; emit `CodegenFilePlan`s (same publication contract, same transaction/callback channel). Runtime-usage proof of reverse-imported symbols via rope scope analysis, not text search.
3. **One-CLI toggles**: add `CodegenConformComponent` enum + `components` field to `CodegenConformRequest` (defaults read from `tooling.yaml`, kebab-case aliases per session law); conform executor honors toggles by including/excluding phase plans; `mode=CHECK` prints per-component plan summaries (dry-run report), `mode=APPLY` writes atomically.
4. **Exterminate in-path libcst**: after step 2, `libcst` import count in `codegen/` must be 0; `_lazy_init_planner_collision.py` (ast) migrated to rope index in the same slice. Delete now-dead `libcst` usage from `flext-infra` dependencies only when count reaches 0 fleet-wide (Phase 2 boundary — dependency removal is NOT in Phase 1).
5. **Tests at the owner**: replace libcst-based engine tests with behavior-only rope-engine tests (forward realign, reverse→TYPE_CHECKING merge, runtime-needed→phase-fail diagnostic, idempotence double-run, multi-line import preservation). Run via `make test PROJECT=flext-infra`.
6. **Gates**: `make fix`, `make fmt`, `make check`, `make test` — zero ruff errors, zero pyrefly errors, full collection. Iterate to green; no suppression, no per-file-ignores.
7. **ai_hub pilot**: `flext-infra codegen conform --root ~/ai-hub --mode check` (dry-run) → review plan summary → `mode=apply` → rerun gates inside ai-hub (`make check`, `make test`) → second dry-run must produce empty plan (idempotence proof).
8. **Knowledge artifacts (same cycle)**: update `flext-infra/AGENTS.md` conventions + ADR-014 (codemod governance) with the three-instrument law; new ADR section or bead documenting the extermination decision; `bd` beads filed for Phase 2; board post with evidence (commands, exit codes, plan counts).

## Phase 2+ — filed as beads, executed in later cycles (each integral)

- Detectors (`detectors/*.py`, ast) → parameterized YAML rule rows + rope index queries.
- Transformers (`transformers/*.py`, ast) → ast-grep rule sets under `make mod` or rope refactors.
- Compat-alias apparatus (`_utilities/compatibility_alias*`, `refactor/project_alias_migrator.py`) → absorbed into the modernize engine (rope rename + ast-grep rules); the apparatus itself exterminated — it exists to kill aliases, so its function migrates and its body dies.
- `_utilities/*ast*`, `gates/{duplication,abstraction_boundary}.py` → rope-index/YAML-rule rewrites.
- Final: remove `libcst`/`ast`-only dependencies from `flext-infra` pyproject; `grep`-verified zero `import ast`/`import libcst` in fleet production code.

## Risks

- **Rope API gap** for TYPE_CHECKING insertion → spike is task 1; stop-and-ask if it cannot compose.
- **Behavior drift** vs the libcst engine → the libcst engine never implemented TYPE_CHECKING relocation (dead `direction` variable); rope engine implements the documented law, so tests pin the law, not the legacy bug.
- **Concurrent-agent races** on shared files (`result.py` was overwritten once) → board claim before edit; fix-forward; index.lock cleanup.
- **ai_hub is not a fleet member** → dry-run first (`mode=check`); pilot requires no onboarding because `root` is a free `Path` and discovery is rope-index-based; if ai-hub lacks FLEXT shape, stop and report rather than force.

## Out of scope (explicit)

- Exterminating ast/libcst outside `flext-infra` (flext-core beartype engine stays; other members follow in later beads).
- Changing beartype runtime rules or `make mod` mechanics.
- New CLI binaries (the one CLI is the existing `flext-infra` surface).
