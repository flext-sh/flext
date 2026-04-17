# flext-infra: Safe Execution, Mixin Cleanup & Dead Code Removal

**Date:** 2026-04-06
**Scope:** flext-infra refactoring — zero new abstractions, maximum reuse, fail fast

## Context

flext-infra has accumulated refactoring debt:

- 32 flat mixins with no hierarchy, field conflicts (`dry_run` inverted semantics), and 3 unused
- 30+ pass-through wrappers in docs services (logic moved to `u.Infra` but stubs left behind)
- 8 dead helpers in doc generator, 2 dead fixer methods
- Git-stash-based safety manager, disconnected from quality gates
- Imperative 12-step namespace enforcer pipeline (should be declarative)
- No automatic rollback when transforms cause quality regressions

This spec addresses all of these through pure refactoring of existing code.

## Principles

1. **Zero backward compat** — delete old code, migrate consumers inline
2. **Fail fast** — no fallbacks, no try/except generic, crash with clear message
3. **Maximum c/t/p/m/u reuse** — new concepts go into the MRO chains
4. **Declarative orchestration** — pipelines as data, not imperative code
5. **Refactoring only** — move, rename, eliminate. New code = absolute minimum

---

## 1. Dead Code Removal (215+ LOC)

### 1.1 Unused Mixins (delete)

| Mixin                | File                | LOC | Action                                                   |
| -------------------- | ------------------- | --- | -------------------------------------------------------- |
| `ErrorDetailMixin`   | `_models/mixins.py` | 4   | Delete (0 uses)                                          |
| `CurrentImportMixin` | `_models/mixins.py` | 4   | Delete (0 uses, inline field in ImportViolationBase)   |
| `FacadeNameMixin`    | `_models/mixins.py` | 7   | Delete (inline `facade_name: str = ""` into 2 consumers) |

### 1.2 Dead Doc Generator Helpers (delete)

File: `docs/generator.py` — 8 methods with 0 references:

- `_generate_root_docs()`, `_generate_project_guides()`, `_generate_project_mkdocs()`
- `_project_guide_content()`, `_sanitize_internal_anchor_links()`, `_update_toc()`
- `_write_if_needed()`, `_project_files()`, `_root_files()`

**Action:** Delete all 8. ~75 LOC removed.

### 1.3 Dead Doc Fixer Helpers (delete)

File: `docs/fixer.py`:

- `_maybe_fix_link()` (0 refs) — delete
- `_update_toc()` (0 refs) — delete

### 1.4 Doc Validator backward-compat alias (delete)

File: `docs/validator.py`:

- `validate_docs()` (labeled "backward-compat alias" in docstring, 0 external refs) — delete

---

## 2. Pass-Through Wrapper Elimination (30+ methods)

### 2.1 Doc Auditor — 11 pure delegations to `u.Infra`

File: `docs/auditor.py`, lines 36-122

Every method is:

```python
@staticmethod
def normalize_link(target: str) -> str:
    return u.Infra.docs_normalize_link(target)
```

**Action:** Delete all 11 methods. Update call sites to call `u.Infra.*` directly.

Methods: `normalize_link`, `should_skip_target`, `is_external`, `to_markdown`,
`broken_link_issues`, `stale_symbol_issues`, `scope_boundary_issues`,
`generated_ownership_issues`, `public_docstring_issues`

### 2.2 Doc Validator — 2 pass-throughs

- `_has_adr_reference()` — inline at call site
- `_maybe_write_todo()` — inline at call site

### 2.3 Doc Builder — 2 pass-throughs

- `_run_mkdocs()` — inline at call site
- `_write_reports()` — inline at call site

### 2.4 Module-level `main =` aliases

7 files export `main = ClassName.method` at module level for old import paths.
**Action:** Remove all. Callers use `__main__.py` or direct class method.

Files: `check/workspace_check.py`, `deps/extra_paths.py`, `deps/fix_pyrefly_settings.py`,
`deps/path_sync.py`, `deps/modernizer.py`, `deps/internal_sync.py`, `deps/detector.py`,
`workspace/sync.py`

### 2.5 Duplicate `_resolve_workspace_root()`

3+ files have identical one-liner delegating to `u.Infra.resolve_workspace_root_or_cwd()`.
**Action:** Inline at call sites. Delete the wrappers.

---

## 3. Mixin Hierarchy Refactoring (32 → ~15 mixins)

### 3.1 New Hierarchy

```
BaseMixin(ContractModel)
    workspace: str = "."
    verbose: bool = False
    workspace_path → computed property
    split_csv_values() → static
    resolve_optional_path() → static

ProjectMixin(BaseMixin)
    projects: t.StrSequence | None = None
    fail_fast: bool = True    # fail fast default
    project_names → computed property (CSV normalization)

ReadMixin(ProjectMixin)
    check: bool = False
    output_dir: str | None = None
    report: str | None = None
    json_output: str | None = None
    output_dir_path → computed property
    report_path → computed property
    json_output_path → computed property

WriteMixin(ProjectMixin)
    apply: bool = False
    diff: bool = False
    rollback: bool = True
    gates: str = c.Infra.SafeExecution.DEFAULT_GATES
    execution_mode → computed property (resolves to c.Infra.ExecutionMode)
```

### 3.2 Deletion Map

| Old Mixin                                   | Action     | Replacement                          |
| ------------------------------------------- | ---------- | ------------------------------------ |
| `CliInputBase`                              | **Delete** | `WriteMixin` (has workspace + apply) |
| `CheckMixin`                                | **Delete** | u.Field in `ReadMixin`               |
| `VerboseMixin`                              | **Delete** | u.Field in `BaseMixin`               |
| `DryRunFalseMixin`                          | **Delete** | `apply=False` default in WriteMixin  |
| `DryRunTrueMixin`                           | **Delete** | `apply=False` default in WriteMixin  |
| `ProjectSelectionMixin`                     | **Delete** | `ProjectMixin`                       |
| `OutputDirMixin`                            | **Delete** | u.Field in `ReadMixin`               |
| `OutputDirPathMixin`                        | **Delete** | u.Field in `ReadMixin`               |
| `JsonOutputPathMixin`                       | **Delete** | u.Field in `ReadMixin`               |
| `ReportPathMixin`                           | **Delete** | u.Field in `ReadMixin`               |
| `ErrorDetailMixin`                          | **Delete** | Dead code                            |
| `CurrentImportMixin`                        | **Delete** | Dead code, inline field            |
| `FacadeNameMixin`                           | **Delete** | Inline field in 2 consumers        |
| `FailFastMixin`                             | **Delete** | u.Field in `ProjectMixin`            |
| `ProjectNamesOptionalMixin`                 | **Keep**   | Domain-specific (release models)     |
| `ProjectNamesListMixin`                     | **Keep**   | Domain-specific (release models)     |
| All others (Release*, Github*, File*, etc.) | **Keep**   | Domain-specific, standalone          |

### 3.3 Consumer Migration

All 26+ CLI input models in `cli_inputs_ops.py` and `cli_inputs_codegen.py` are migrated:

**Before:**

```python
class RefactorNamespaceEnforceInput(ProjectSelectionMixin, CliInputBase): ...
```

**After:**

```python
class RefactorNamespaceEnforceInput(WriteMixin): ...
```

**Before:**

```python
class DocsAuditInput(
    CheckMixin, OutputDirMixin, ProjectSelectionMixin, CliInputBase
): ...
```

**After:**

```python
class DocsAuditInput(ReadMixin): ...
```

Each model that does writes → `WriteMixin`. Each read-only → `ReadMixin`.

### 3.4 `dry_run` Conflict Resolution

Today: `DryRunFalseMixin.dry_run = False` vs `DryRunTrueMixin.dry_run = True` (inverted semantics).

Resolution: **Delete both.** `WriteMixin.apply = False` is the single source of truth.
`dry_run` becomes a computed property:

```python
@u.computed_field
@property
def dry_run(self) -> bool:
    return not self.apply
```

Any code checking `params.dry_run` continues to work. Any code checking `params.apply` continues to work. One field, one truth.

---

## 4. c/t/p/m/u Chain Additions

### 4.1 c.Infra — `FlextInfraConstantsBase`

```python
class SafeExecution:
    """Constants for safe execution pipeline."""

    DEFAULT_GATES: Final[str] = "lint,pyrefly"
    BAK_SUFFIX: Final[str] = ".bak"


class ExecutionMode(StrEnum):
    DRY_RUN = "dry-run"
    CHECK_ONLY = "check-only"
    APPLY_SAFE = "apply-safe"
    APPLY_FORCE = "apply-force"
```

### 4.2 m.Infra — `FlextInfraModelsBase`

```python
class SafeExecutionResult(ContractModel):
    """Result of a safe execution pipeline run."""

    mode: c.Infra.ExecutionMode
    files_backed_up: t.StrSequence
    gate_results: Sequence[m.Infra.GateResult]
    rolled_back: bool


class TransformStep(ContractModel):
    """Declarative step for enforcement pipeline."""

    detector: NonEmptyStr
    transformer: NonEmptyStr
    gates: str = c.Infra.SafeExecution.DEFAULT_GATES
```

### 4.3 p.Infra — `FlextInfraProtocolsBase`

```python
@runtime_checkable
class SafeTransformer(Protocol):
    def transform(self, files: Sequence[Path]) -> p.Result[Sequence[Path]]: ...


@runtime_checkable
class SafeValidator(Protocol):
    def validate(
        self, files: Sequence[Path], project_dir: Path
    ) -> p.Result[m.Infra.GateResult]: ...
```

---

## 5. Safe Execution — Refactored `u.Infra.Safety`

Refactor existing `_utilities/safety.py` from git-stash to .bak:

```python
class FlextInfraUtilitiesSafety:
    @staticmethod
    def backup_files(files: Sequence[Path]) -> Sequence[Path]:
        """Copy each file to .bak. Fail fast on any error."""

    @staticmethod
    def restore_files(bak_files: Sequence[Path]) -> None:
        """Move .bak back to original. Fail fast."""

    @staticmethod
    def cleanup_backups(bak_files: Sequence[Path]) -> None:
        """Remove .bak files after successful validation."""

    @staticmethod
    def execute_safely(
        files: Sequence[Path],
        transform: p.Infra.SafeTransformer,
        project_dir: Path,
        gates: str = c.Infra.SafeExecution.DEFAULT_GATES,
    ) -> m.Infra.SafeExecutionResult:
        """Pipeline: backup -> transform -> validate -> (cleanup | rollback).

        Fail fast: any step failure = immediate rollback + raise.
        """
```

### 5.1 Gate File-Targeted Check

Add `check_files()` to `FlextInfraGate` base class:

```python
def check_files(
    self,
    files: Sequence[Path],
    project_dir: Path,
    ctx: m.Infra.GateContext,
) -> m.Infra.GateExecution:
    """Check specific files instead of whole directory."""
```

For ruff/pyrefly: pass file paths directly to CLI tool. Same result as directory check but scoped.

---

## 6. Declarative Namespace Enforcer

Refactor `namespace_enforcer.py` from 12 imperative `_detect_and_apply()` calls to declarative pipeline:

```python
ENFORCEMENT_PIPELINE: Final[Sequence[m.Infra.TransformStep]] = [
    m.Infra.TransformStep(
        detector="namespace.loose_objects", transformer="FlextInfraLooseObjectFixer"
    ),
    m.Infra.TransformStep(
        detector="namespace.import_aliases", transformer="FlextInfraImportModernizer"
    ),
    m.Infra.TransformStep(
        detector="namespace.sources", transformer="FlextInfraNamespaceSourceFixer"
    ),
    m.Infra.TransformStep(
        detector="namespace.internal_imports",
        transformer="FlextInfraInternalImportFixer",
    ),
    m.Infra.TransformStep(
        detector="namespace.runtime_aliases", transformer="FlextInfraRuntimeAliasFixer"
    ),
    m.Infra.TransformStep(
        detector="typing.future_annotations",
        transformer="FlextInfraFutureAnnotationsFixer",
    ),
    m.Infra.TransformStep(
        detector="typing.manual_protocols", transformer="FlextInfraManualProtocolFixer"
    ),
    m.Infra.TransformStep(
        detector="typing.manual_aliases", transformer="FlextInfraManualTypingAliasFixer"
    ),
    m.Infra.TransformStep(
        detector="typing.compatibility_aliases",
        transformer="FlextInfraCompatibilityAliasFixer",
    ),
    m.Infra.TransformStep(
        detector="namespace.class_placement",
        transformer="FlextInfraClassPlacementFixer",
    ),
    m.Infra.TransformStep(
        detector="namespace.mro_completeness",
        transformer="FlextInfraMROCompletenessFixer",
    ),
    m.Infra.TransformStep(
        detector="imports.cyclic", transformer="FlextInfraCyclicImportFixer"
    ),
]
```

The enforcer iterates the list, running each step through `u.Infra.execute_safely()`.

---

## 7. Execution Order

### Wave 1: Dead Code Removal (no dependencies)

1. Delete 3 unused mixins
2. Delete 8 dead generator helpers + 2 dead fixer helpers
3. Delete backward-compat `validate_docs()` alias
4. Validate: `ruff check src/` + `pyrefly check src/`

### Wave 2: Pass-Through Wrapper Elimination

1. Inline 11 auditor delegations → call `u.Infra.*` directly
2. Inline 4 validator/builder pass-throughs
3. Remove 7 module-level `main =` aliases
4. Inline 3+ `_resolve_workspace_root()` duplicates
5. Validate: `ruff check src/` + `pyrefly check src/`

### Wave 3: c/t/p/m/u Additions

1. Add `c.Infra.SafeExecution` + `c.Infra.ExecutionMode` to `_constants/base.py`
2. Add `m.Infra.SafeExecutionResult` + `m.Infra.TransformStep` to `_models/base.py`
3. Add `p.Infra.SafeTransformer` + `p.Infra.SafeValidator` to `_protocols/base.py`
4. Validate: `ruff check src/` + `pyrefly check src/`

### Wave 4: Mixin Hierarchy

1. Rewrite `_models/mixins.py` — delete 14 mixins, create 4-class hierarchy
2. Migrate all 26+ CLI input models in `cli_inputs_ops.py` + `cli_inputs_codegen.py`
3. Migrate any domain models that used deleted mixins
4. Validate: `ruff check src/` + `pyrefly check src/` + run tests

### Wave 5: Safe Execution

1. Refactor `_utilities/safety.py` — git-stash → .bak
2. Add `check_files()` to `gates/_base_gate.py`
3. Validate: `ruff check src/` + `pyrefly check src/` + run safety tests

### Wave 6: Declarative Pipeline

1. Refactor `refactor/namespace_enforcer.py` — imperative → declarative
2. Update `refactor/_engine_helpers.py` to use `u.Infra.execute_safely()`
3. Validate: full `make check` + run enforcer tests

---

## 8. Verification

After each wave:

- `ruff check src/` — 0 errors
- `pyrefly check src/` — 0 errors

After Wave 4 (mixin migration):

- All CLI commands parse correctly (test with `--help`)
- `flext-infra refactor namespace-enforce --dry-run` works
- `flext-infra check ruff-lint --projects flext-core` works
- `flext-infra docs audit` works

After Wave 6 (full pipeline):

- `flext-infra refactor namespace-enforce --apply --projects flext-core` creates .bak, transforms, validates, cleans up
- Same command with intentionally broken transform → rollback occurs, .bak restored
- `flext-infra refactor namespace-enforce --apply --no-rollback` skips validation

## 9. Net LOC Impact

| Category              | Removed  | Added    | Net      |
| --------------------- | -------- | -------- | -------- |
| Dead code             | -95      | 0        | -95      |
| Pass-through wrappers | -120     | 0        | -120     |
| Module aliases        | -15      | 0        | -15      |
| Mixin consolidation   | -200     | +150     | -50      |
| c/t/p/m/u additions   | 0        | +60      | +60      |
| Safety refactor       | -80      | +60      | -20      |
| Declarative enforcer  | -100     | +40      | -60      |
| **Total**             | **-610** | **+310** | **-300** |

**Net result: ~300 LOC reduction** with safer execution, cleaner architecture, and zero complexity wrappers.
