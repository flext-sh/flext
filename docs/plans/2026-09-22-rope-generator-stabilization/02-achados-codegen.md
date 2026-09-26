# Findings — Codegen engine, templates and governing ADRs

<!-- TOC START -->

- [1. Engine location and surfaces](#1-engine-location-and-surfaces)
- [2. What make gen generates today (facts, not intent)](#2-what-make-gen-generates-today-facts-not-intent)
- [3. Governing law (the "earlier decision")](#3-governing-law-the-earlier-decision)
- [4. make mod machinery](#4-make-mod-machinery)
- [5. SSOT surfaces the generator must derive from](#5-ssot-surfaces-the-generator-must-derive-from)
- [6. Engine state in the worktree copy](#6-engine-state-in-the-worktree-copy)

<!-- TOC END -->

Date: 2026-09-22. Sources: live read-only inspection of
`/home/marlonsc/flext/flext-infra` (main checkout, near origin tip) and the worktree
copy, `config/codegen.yaml`, template tree, representative member `flext-ldif`, and ADRs
010/014/016/017/018.

## 1. Engine location and surfaces

- Engine root: `flext-infra/src/flext_infra/codegen/`. Key modules: `conform.py` +
  `_conform/` (conformance pipeline, `execute.py::_validate_managed_fixed_point`),
  `codegen_transaction.py` (transactional publication, `commit_locked`),
  `lazy_init_planner.py` + `_lazy_init_planner_*.py` (aliases/cache/children/collision/
  exports/parents/public*root),
  `_lazy_init_generation*.py`, `mise*artifacts.py` + `_mise_artifacts/**.py`
  (staging/publication/recovery/verification — the transactional artifact
  publication with rollback), `protocol*models.py`, `scaffolder.py`,
  `project_new.py`, `pipeline.py`, `layout*.py`, `fixer*.py`, `version_file.py`.
- Templates: `flext-infra/src/flext_infra/templates/` — `project/base/**` (per-project
  templates), `bootstrap/` (mise), plus root templates `lazy_init_root.py.j2`,
  `module_skeleton.py.j2`, `static_package_init.py.j2`, `version_file.py.j2`, mkdocs.

## 2. What `make gen` generates today (facts, not intent)

- `config/codegen.yaml` (2,161 lines; sections: toolchain, make, artifacts, layout,
  managed_files, scaffold, templates) declares template entries for EVERY target facet:
  `api.py`, `cli.py`, `__main__.py`, `base.py`, `models.py`, `typings.py`,
  `protocols.py`, `constants.py`, `utilities.py`, `_config.py`, `_settings.py`,
  `py.typed`, `services/ping.py`, `config/{ns}.yaml`, and internal parts
  `_models/{ping,config,settings}.py`, `_constants/{config,settings}.py`,
  `_protocols/{config,ping,settings}.py`, `_typings/base.py`.
- ALL facet entries carry `overwrite: false` → scaffold-once semantics. The body then
  evolves by hand; gen does not re-project it.
- Measured reality in a clean member (`flext-ldif`): only `__init__.py` files (root,
  family dirs, `servers/*`) and `__version__.py` carry the `AUTO-GENERATED` marker. The
  public facets (`constants.py`, `typings.py`, `protocols.py`, `models.py`,
  `utilities.py`, `base.py`, `api.py`, `cli.py`, `_settings.py`, `_config.py`) are
  hand-written today.
- Therefore the requested expansion = absorb existing facet bodies into the internal
  sources (`_constants/`, `_typings/`, `_protocols/`, `_models/`, `_utilities/`) and
  turn the public facets into COMPLETE generated projections (generation mark,
  docstring, future import, imports, public composition, aliases, singletons, trailing
  `__all__`), with names/bases/dependencies/exports derived from the SSOT
  (`config/workspace.yaml`, `config/*.yaml`, `config/exports.yaml`) and dependency
  contracts.

## 3. Governing law (the "earlier decision")

- **ADR-018 — Generator Declarations Law** (operator law 2026-09-20, epic
  `flext-0in0k`): a facade letter belongs to the module that declares it in its explicit
  `__all__`; `__init__.py` propagates, never declares; internal tiers derive from
  folders (no lists); the generator propagates, never compensates; violations are fixed
  at the source; deriving beats listing; every hack's permission dies in the same commit
  as the hack.
- **ADR-014 — Family Part Shape + Rope Codemod Rules** (§3b rope-in-gen): ONE engine,
  two modes (`codegen init` strict/total and `conform`); `make gen` is the ONLY writer
  of generated projections — hand-written split output is adoption input, never
  authority; render = `f(SSOT, templates, PINS)` (any environment input reaching the
  render is a P0 engine defect); strict/total init (union of sibling `__all__`,
  `GEN-W001` missing `__all__`, `GEN-E001` stale export fails loud); transactional loop
  per repository (CAS snapshot → one Rope project → one transactional publish → single
  receipt; mid-publication failure reverse-applies only its own effects); three
  instruments only — rope (semantic), `make mod` (ast-grep YAML + parameterized
  sed-by-list), config rows (detection/policy); Python rewrite engines (`re`/`ast`/
  `libcst`/`tokenize`) exterminated in favor of those instruments.
- **ADR-016 — Settings/Config Singleton Contract** (PROPOSED, execution assigned):
  singleton lifecycle owned exclusively by classmethods (`fetch_global`,
  `update_global`, `reset_for_testing`, `clone`); `__new__` must not intercept pydantic
  construction; `clone`/`fetch_global(overrides=...)` validate entirely inside
  `singleton_disabled()`; module-level `settings`/`config` aliases must resolve to the
  same identity the classmethods serve; one migration cycle transports ALL alias sites.
  This is the basis of the requested global config-vs-settings separation fix.
- **ADR-010** (codegen standardization) and **ADR-017** (parametrized rule surfaces,
  single `mod` modernize verb; rules as data under `config/rules/{mod,ast,rope}/`).

## 4. `make mod` machinery

- Superproject `custom.mk` adds verb `codemod RULE=<csv> [APPLY=Y]` over
  `codemod/rules/refactor/apply_renames.py` — generic CSV-driven rename engine
  (`old,new` header; longest-old-first; pass 1 `ast-grep run -p <old> -r <new>` via
  `u.Cli.run_raw`; pass 2 word-boundary regex over ALL text files for comments,
  docstrings, toml/md; idempotent because domain-first names never re-match). Existing
  CSVs: `cacophony.csv`, `cli-prefixes.csv`, `infra-dedup.csv`. This content is
  byte-identical to origin commit `9a8f437e31` and already staged in the worktree.
- Structural moves/identity/references/inheritance/collisions: Rope primitives
  (`FlextInfraUtilitiesRopeRuntime`, `_utilities/rope_class_move.py`,
  `_utilities/namespace_moves.py`) applied through the shared change cycle
  (`backup_files → transform → validate → cleanup | rollback`) inside the `make mod`
  circuit (`FlextInfraCodemodBatchApply` beside `FlextInfraCodemodSemanticApply`).

## 5. SSOT surfaces the generator must derive from

- `config/workspace.yaml` (root, hand-written topology SSOT v3, consumed by
  `flext-infra codegen conform`; never overwritten) — repository + project identity
  (package_name/class_stem/namespace/alias/environment_prefix) and the 31-member list.
- `config/exports.yaml` (root public-exports SSOT; scan-as-validator: manifest must
  EQUAL static scan; single-letter aliases are runtime machinery and stay OUT).
- `flext-infra/config/codegen.yaml` + `tooling.yaml` (toolchain and policy);
  `config/{ns}.yaml` per package for runtime config namespaces.

## 6. Engine state in the worktree copy

- Worktree `flext-infra`: clean tree, 5 ahead / 8 behind origin, branch
  `recovery/rope-automation-20260921`, 4 stashes preserving earlier WIP; its no-ff
  integration merge against `34b5262e5` was already concluded before this plan
  (flext-infra is NOT among the 17 members still holding `MERGE_HEAD`).
- Post-handoff improvements present in source (declaration/publication separation,
  relative-import resolution, Rope resource identity) but not yet proven by the
  canonical gate; known residue: unused `Annotated` import in `codegen/lazy_init.py`.
