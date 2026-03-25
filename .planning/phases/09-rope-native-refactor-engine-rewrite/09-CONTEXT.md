# Phase 9: Rope-native refactor engine rewrite - Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Rewrite the `flext_infra` refactor engine so that semantic cross-file operations (rename,
find-occurrences, symbol propagation) use rope as the backend, while syntax-level
transformations stay on LibCST. Simplicity is the primary constraint: flext-infra must
not grow in complexity — rope is used as a library to simplify existing LibCST code, not
as an additional layer on top of it.

</domain>

<decisions>
## Implementation Decisions

### Replacement strategy
- **D-01:** Hybrid approach — rope for cross-file semantic ops, LibCST for syntax-level pattern edits
- **D-02:** Rope must SIMPLIFY existing code, not add layers. Where rope makes a LibCST transformer simpler, use it. Never add rope complexity to stay "pure LibCST."
- **D-03:** No "rope abstraction layer" — rope is used directly as a Python library where it helps

### Scope — which transformers migrate
- **D-04:** Rope-native in Phase 9: `symbol_propagator.py`, `mro_reference_rewriter.py`, `nested_class_propagation.py` — these are the only ones doing cross-file name resolution
- **D-05:** All other transformers stay LibCST — but MUST be reviewed and simplified where rope APIs can reduce their complexity (e.g. `rope.find_occurrences` replacing hand-rolled grep logic inside LibCST transformers)
- **D-06:** `mro_remover.py` and `mro_private_inline.py` — NO rope pre-check. Keep them as-is LibCST, simple.
- **D-07:** Import transformers (`import_modernizer`, `import_normalizer`, `import_bypass_remover`, `tier0_import_fixer`, `lazy_import_fixer`) — stay LibCST, simplify if possible
- **D-08:** Typing transformers (`typing_annotation_replacer`, `typing_unifier`) — stay LibCST, simplify if possible
- **D-09:** Structural transformers (`class_reconstructor`, `alias_remover`, `deprecated_remover`, `unused_model_remover`) — stay LibCST, simplify if possible

### Engine integration — how rope ops plug in
- **D-10:** Rope ops as pre/post hooks on `FlextInfraRefactorEngine`, NOT as new rule types
- **D-11:** No `FlextInfraRopeRefactorRule` subtype — rope is not part of the rule system
- **D-12:** No YAML schema changes — rope hooks are registered programmatically in the engine
- **D-13:** Existing `make refactor` CLI interface unchanged
- **D-14:** Hooks run once per project (rope's execution model), not per file

### Project isolation
- **D-15:** Single monorepo-rooted `rope.base.project.Project("/home/marlonsc/flext")` instance
- **D-16:** All 33 `flext-*/src` directories in `source_folders`
- **D-17:** `ignored_resources` must exclude: `.venv`, `*.pyc`, `dist/`, `__pycache__`, `.mypy_cache`, `.git`
- **D-18:** `save_objectdb = False` — avoid stale cache across sessions
- **D-19:** Single Project shared across all rope hook invocations in one engine run

### Simplicity constraint (critical)
- **D-20:** Every change must make flext-infra simpler or equal in complexity — never more complex
- **D-21:** If using rope in a transformer makes it more complex, don't use rope there
- **D-22:** Target: reduce total LOC in `transformers/` and `refactor/` after Phase 9

</decisions>

<specifics>
## Specific Ideas

- "manter flext-infra o mais simples possivel" — simplicity is the primary constraint, not completeness of rope adoption
- Rope is used as a Python library to simplify existing code, not as a framework to restructure around
- The 3 migrated transformers (`symbol_propagator`, `mro_reference_rewriter`, `nested_class_propagation`) should become shorter and clearer after migration, not just "rope-flavored"

</specifics>

<canonical_refs>
## Canonical References

### Existing engine and transformer code
- `flext-infra/src/flext_infra/refactor/engine.py` — current orchestration engine; hooks go here
- `flext-infra/src/flext_infra/transformers/symbol_propagator.py` — migrates to rope-native
- `flext-infra/src/flext_infra/transformers/mro_reference_rewriter.py` — migrates to rope-native
- `flext-infra/src/flext_infra/transformers/nested_class_propagation.py` — migrates to rope-native
- `flext-infra/src/flext_infra/refactor/_base_rule.py` — rule base class; NOT changing
- `flext-infra/src/flext_infra/rules/` — YAML rule configs; NOT changing

### Architecture
- `AGENTS.md` — MRO namespace composition rules, strict typing requirements
- `flext-infra/pyproject.toml` — confirms `rope>=1.14.0` already declared as dep

### No external specs
No ADRs or design docs exist for this phase — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `FlextInfraRefactorEngine` — add pre/post hook registration points here; all rope logic enters via hooks
- `rope.base.project.Project` — already declared dep, zero current usage in production code
- `rope.refactor.rename.Rename` — for cross-file symbol rename (replaces `QualifiedNameProvider` grep)
- `rope.find_occurrences` — for finding all usages without a full rename (simplifies hand-rolled grep in transformers)

### Established Patterns
- All transformers follow `FlextInfraRefactorRule` with `apply(tree, file_path)` — rope hooks bypass this (per-project, not per-file)
- `r[T]` result types for all fallible operations — rope hook methods must return `r[T]`
- MRO namespace: `FlextInfraRefactor*` facade pattern stays intact
- Zero ruff/pyrefly/pyright errors required after every change

### Integration Points
- `FlextInfraRefactorEngine.refactor_project()` — pre-hook runs before CST pass, post-hook after; both receive the project `Path`
- `.venv` exclusion critical — rope will index the entire venv if not excluded via `ignored_resources`

</code_context>

<deferred>
## Deferred Ideas

- Parallel engine (`FlextInfraRopeEngine`) — not needed, hooks are sufficient for Phase 9 scope
- `FlextInfraRopeRefactorRule` subtype — deferred; not warranted unless rope rules grow to dominate
- Rope pre-check for `mro_remover`/`mro_private_inline` — deferred, only if false positives observed in production runs
- Lazy project pool (LRU) — deferred; only relevant if memory profiling shows a problem
- `engine: rope` YAML discriminator — deferred with parallel engine

</deferred>

---

*Phase: 09-rope-native-refactor-engine-rewrite*
*Context gathered: 2026-03-25*
