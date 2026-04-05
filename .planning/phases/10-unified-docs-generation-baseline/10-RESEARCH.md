# Phase 10 Research — flext-infra Full Command Refactoring to flext-cli Pattern

## Scope Clarification

**NOT just docs** — ALL flext-infra command domains (excluding docs, handled by separate agent).

Target: Refactor all flext-infra commands to follow the modern flext-cli MRO service facade pattern with centralized rope library usage.

## Current Architecture Inventory

### Command Domains (11 total, docs excluded)

| Domain | LOC | Files | Service Classes | Has cli.py |
|--------|-----|-------|-----------------|------------|
| basemk | 397 | 4 | FlextInfraBaseMkTemplateEngine(s[str]), FlextInfraBaseMkGenerator(s[str]) | Yes |
| check | 768 | 6 | FlextInfraWorkspaceChecker(s[bool]), FlextInfraCheckServices | Yes (2) |
| codegen | 1,826 | 10 | LazyInit, Census, Scaffolder, Fixer, PyTyped, ConstantsQualityGate (all FlextInfraServiceBase[T]) | Yes |
| deps | 2,942 | 13 | FlextInfraDepsDetector, FlextInfraDepsModernizer, FlextInfraConfigFixer(s[bool]) + more | Yes |
| detectors | 1,799 | 16 | 12 detector classes (all FlextInfraScanFileMixin + p.Infra.Scanner) | No (library) |
| gates | 1,157 | 10 | 8 gate classes (all _base_gate pattern) | No (library) |
| github | 173 | 3 | FlextInfraGithubService | Yes |
| refactor | 7,572 | 34 | FlextInfraRefactorEngine, NamespaceEnforcer, MROResolver + many utilities | Yes |
| release | 688 | 4 | FlextInfraReleaseOrchestrator(s[bool]) via OrchestratorPhases mixin | Yes |
| rules | 993 | 7 | Rule definitions (library, no service classes) | No (library) |
| services | 325 | 4 | Pipeline, Consolidator, Deduplicator (codegen-related) | No |
| transformers | 3,244 | 25 | 15+ transformer classes (all FlextInfraRopeTransformer base) | No (library) |
| validate | 1,836 | 10 | Scanner, BasemkValidator, NamespaceValidator, SkillValidator + more | Yes |
| workspace | 1,674 | 8 | Orchestrator, Migrator, Detector, SyncService | Yes |

### Supporting Layers

| Layer | LOC | Files | Key Classes |
|-------|-----|-------|-------------|
| _utilities | 12,731 | 43 | 29 utility classes in MRO facade `FlextInfraUtilities.Infra` |
| _constants | 2,097 | 15 | Organized per domain (_constants/basemk.py, check.py, etc.) |
| _models | 5,353 | 22 | Organized per domain (_models/basemk.py, check.py, etc.) |
| _typings | varies | 4+ | Including _typings/rope.py with PEP 695 type aliases |
| _protocols | varies | 4+ | Including _protocols/rope.py with rope protocol contracts |

### Rope Centralization Status

**Already centralized in _utilities/rope*.py (7 files, ~1,730 LOC):**
- `rope_core.py` (286 LOC) — init_rope_project, RopeProject management
- `rope_analysis.py` (262 LOC) — class analysis, symbol resolution
- `rope_analysis_introspection.py` (178 LOC) — introspection helpers
- `rope_helpers.py` (329 LOC) — general rope helpers
- `rope_imports.py` (446 LOC) — import analysis via rope
- `rope_source.py` (229 LOC) — source code analysis via rope
- `rope.py` — MRO facade composing all above

**Direct rope type usage outside utilities (via t.Infra.RopeProject — CORRECT):**
- detectors/_base_detector.py — DetectorContext.rope_project field
- detectors/namespace_source_detector.py, cyclic_import_detector.py, loose_object_detector.py
- transformers/_base.py, tier0_import_fixer.py, alias_remover.py, mro_remover.py, etc.
- _protocols/rope.py — protocol definitions

**No direct `import rope.*` outside _utilities and _typings** — GOOD.

### CLI Architecture Gap

**Current (flext-infra/cli.py):**
- Manual dispatcher via `importlib.import_module` + string specs
- `_GROUP_REGISTRARS` and `_GROUP_RUNNERS` ClassVar dicts
- Each domain has its own `cli.py` with `FlextInfraCli<Domain>` class
- No MRO composition — groups are independently loaded

**Target (flext-cli pattern):**
- api.py MRO facade composing all service mixins
- base.py thin service base (~30 LOC)
- services/ directory with one mixin per concern
- CLI registration via Typer on the facade

### base.py Gap

**Current FlextInfraServiceBase (187 LOC):**
- Too many fields: config_type, config_overrides, initial_context, subproject, container_overrides, wire_modules, wire_packages, wire_classes, workspace_root, apply_changes, check_only
- Field validators
- Complex initialization

**Target FlextCliServiceBase (31 LOC):**
- Just settings access via property
- ABC enforcing execute()

### Key Patterns Already Correct

1. **Utilities via MRO**: `FlextInfraUtilities.Infra` composes 29 utility classes — ✅
2. **Constants organized**: `_constants/` per domain — ✅
3. **Models organized**: `_models/` per domain — ✅
4. **Rope types via t.Infra**: `t.Infra.RopeProject` etc. — ✅
5. **No direct rope imports outside _utilities/_typings** — ✅
6. **Detectors use scan mixin pattern** — ✅
7. **Transformers use FlextInfraRopeTransformer base** — ✅

## What Needs to Change

### 1. Create api.py MRO Facade
- New `FlextInfra` class composing domain service mixins
- Singleton pattern like FlextCli.get_instance()
- execute() returns r[T]

### 2. Simplify base.py
- Strip to ~30 LOC like FlextCliServiceBase
- Fields like workspace_root, apply_changes move to per-domain mixins or settings
- All service classes inherit from new thin base

### 3. Convert Command Domains to Service Mixins
- Each domain's main service class → mixin in services/
- Business logic → u.Infra.* utilities (most already there)
- CLI registration stays lazy but routes through facade

### 4. Ensure Thin Orchestrators
- Service methods: validate inputs → call u.Infra.* → return r[T]
- No inline business logic in service methods
- Constants via c.Infra.*, types via t.Infra.*, utilities via u.Infra.*

### 5. Library Domains Stay As-Is
- detectors/, gates/, rules/, transformers/ — these are libraries, not commands
- They already follow correct patterns (scan mixin, gate base, rule base)
- No changes needed unless they have anti-patterns

## Risk Assessment

- **refactor/ domain** (7,572 LOC) is the biggest risk — complex engine with rope integration
- **deps/ domain** (2,942 LOC) has many standalone service classes
- **codegen/ domain** has services/ subdirectory that may conflict with new pattern
- **base.py simplification** may break many service classes that depend on current fields

## Plan Breakdown Recommendation

Given the scope (~25K LOC across 11 domains), break into waves:
1. **Wave 1**: Foundation (api.py, base.py, settings) — must be first
2. **Wave 2**: Simple domains (basemk, github, release) — low LOC, few dependencies
3. **Wave 3**: Medium domains (check, validate, workspace) — moderate complexity
4. **Wave 4**: Complex domains (codegen, deps) — many service classes
5. **Wave 5**: Engine domain (refactor + its _utilities) — highest complexity, rope-heavy

Library domains (detectors, gates, rules, transformers) need no structural changes.
