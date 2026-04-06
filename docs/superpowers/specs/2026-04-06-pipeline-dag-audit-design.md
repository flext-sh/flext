# Pipeline DAG Engine & Cross-Library Audit

**Date**: 2026-04-06
**Scope**: flext-infra, flext-cli, flext-core, flext-tests
**Approach**: Top-Down — DAG engine first, then pipeline migration, then cleanup

---

## Context

flext-infra's processing pipelines (codegen, check, refactor, release) execute stages sequentially without shared state, caching, or dependency tracking. Each stage independently rediscovers projects, violation reconciliation uses brittle line-number keys, and return values are partially discarded. Additionally, `flext_infra/_utilities/io.py` duplicates JSON/SHA256 logic already in flext-cli.

This design addresses all issues via a reusable DAG pipeline engine in flext-cli, followed by migration of flext-infra pipelines and elimination of code duplication.

---

## Phase 1: DAG Pipeline Engine in flext-cli

### 1.1 Protocols (`p.Cli.*`)

```python
@runtime_checkable
class PipelineStage(Protocol):
    """Contract for a pipeline stage handler."""

    def __call__(
        self, ctx: p.Cli.PipelineStageContext
    ) -> r[m.Cli.PipelineStageResult]: ...


@runtime_checkable
class PipelineStageContext(Protocol):
    """Contract for stage execution context."""

    workspace_root: Path
    shared: t.MutableContainerMapping
    config: t.ContainerMapping


@runtime_checkable
class PipelineExecutor(Protocol):
    """Contract for pipeline execution engine."""

    def execute(
        self,
        stages: Sequence[m.Cli.PipelineStageSpec],
        context: p.Cli.PipelineStageContext,
        *,
        fail_fast: bool = True,
    ) -> r[m.Cli.PipelineResult]: ...
```

### 1.2 Types (`t.Cli.*`)

```python
type PipelineHandler = Callable[
    [p.Cli.PipelineStageContext], r[m.Cli.PipelineStageResult]
]
type PipelineSkipPredicate = Callable[[p.Cli.PipelineStageContext], bool]
type PipelineStageStatus = Literal["ok", "skipped", "failed"]
```

### 1.3 Models (`m.Cli.*`) — flat namespace

```python
class PipelineStageSpec(FlextModels.ContractModel):
    """Declarative stage definition with dependency tracking."""

    stage_id: str
    depends_on: frozenset[str] = frozenset()
    handler: t.Cli.PipelineHandler
    skip_if: t.Cli.PipelineSkipPredicate | None = None
    retry: t.RetryCount = 0


class PipelineStageResult(FlextModels.ContractModel):
    """What a stage produces."""

    stage_id: str
    status: t.Cli.PipelineStageStatus
    output: t.ContainerMapping
    duration_ms: float


class PipelineResult(FlextModels.ContractModel):
    """Full pipeline execution result."""

    stages: Sequence[m.Cli.PipelineStageResult]
    total_duration_ms: float

    @property
    def ok(self) -> bool:
        return all(s.status != "failed" for s in self.stages)

    @property
    def failed_stages(self) -> Sequence[m.Cli.PipelineStageResult]:
        return [s for s in self.stages if s.status == "failed"]
```

### 1.4 Constants (`c.Cli.Pipeline.*`)

```python
class Pipeline:
    DEFAULT_RETRY: t.RetryCount = 0
    DEFAULT_FAIL_FAST: bool = True
    MAX_RETRY: t.RetryCount = 3
```

### 1.5 Utilities (`u.Cli.execute_pipeline`)

```python
@staticmethod
def execute_pipeline(
    stages: Sequence[m.Cli.PipelineStageSpec],
    context: p.Cli.PipelineStageContext,
    *,
    fail_fast: bool = c.Cli.Pipeline.DEFAULT_FAIL_FAST,
    logger: p.Logger | None = None,
) -> r[m.Cli.PipelineResult]:
    """Execute stages in topological order via graphlib.TopologicalSorter."""
```

**Implementation details:**
1. Build `graphlib.TopologicalSorter` from `stages` + `depends_on`
2. Execute in topological order (sequential — parallel-ready via `prepare()`/`done()` API)
3. Each stage receives `StageContext` with `shared` dict containing prior stage outputs
4. `skip_if` predicate checked before execution; skipped stages produce `status="skipped"`
5. Failed stages short-circuit if `fail_fast=True`, otherwise accumulate
6. Retry: on failure, retry up to `stage.retry` times before marking failed
7. All results structured-logged via `FlextLogger`
8. Returns `r[PipelineResult]` — railway-oriented, composable

### 1.6 Files to create/modify in flext-cli

| File | Action |
|------|--------|
| `src/flext_cli/_protocols/pipeline.py` | CREATE — Pipeline protocols |
| `src/flext_cli/_typings/pipeline.py` | CREATE — Pipeline type aliases |
| `src/flext_cli/_models/pipeline.py` | CREATE — Pipeline models |
| `src/flext_cli/_constants/pipeline.py` | CREATE — Pipeline constants |
| `src/flext_cli/_utilities/pipeline.py` | CREATE — Pipeline engine |
| `src/flext_cli/protocols.py` | MODIFY — Add PipelineMixin to MRO |
| `src/flext_cli/typings.py` | MODIFY — Add PipelineMixin to MRO |
| `src/flext_cli/models.py` | MODIFY — Add PipelineMixin to MRO |
| `src/flext_cli/constants.py` | MODIFY — Add PipelineMixin to MRO |
| `src/flext_cli/utilities.py` | MODIFY — Add PipelineMixin to MRO |
| `tests/unit/test_pipeline.py` | CREATE — Engine unit tests |

---

## Phase 2: io.py Absorption into flext-cli

### 2.1 Current state of `flext_infra/_utilities/io.py` (~220 lines)

| Method | Status | Action |
|--------|--------|--------|
| `sha256_content()` | Dead code (duplicate of `u.Cli.sha256_content`) | DELETE |
| `sha256_file()` | Dead code (duplicate of `u.Cli.sha256_file`) | DELETE |
| `read_json()` | 95% duplicate of `u.Cli.json_read()` | ABSORB into flext-cli |
| `write_json()` | 95% duplicate of `u.Cli.json_write()` | ABSORB into flext-cli |
| `parse()` | Thin wrapper | ABSORB or inline at call sites |
| `serialize()` | Thin wrapper | ABSORB or inline at call sites |

### 2.2 Plan

1. Extend `u.Cli.json_read()` / `u.Cli.json_write()` to accept optional `validator: Callable[[t.ContainerMapping], r[t.ContainerMapping]] | None` callback for domain-specific validation (the 5% variation)
2. Update all flext-infra callers from `u.Infra.read_json()` → `u.Cli.json_read()`
3. Delete `flext_infra/_utilities/io.py` entirely
4. Remove `FlextInfraUtilitiesIo` from `FlextInfraUtilities.Infra` MRO

### 2.3 Files to modify

| File | Action |
|------|--------|
| `flext-cli/src/flext_cli/_utilities/json.py` | MODIFY — Add validation callback params |
| `flext-infra/src/flext_infra/_utilities/io.py` | DELETE |
| `flext-infra/src/flext_infra/utilities.py` | MODIFY — Remove FlextInfraUtilitiesIo from MRO |
| All `u.Infra.read_json` callers | MODIFY — Switch to `u.Cli.json_read` |

---

## Phase 3: Migrate flext-infra Pipelines to DAG Engine

### 3.1 Codegen Pipeline (6 stages)

Convert `FlextInfraCodegenPipeline` to declare stages as `m.Cli.PipelineStageSpec` and execute via `u.Cli.execute_pipeline()`.

**Stage DAG:**
```
py_typed → census_before → scaffold → auto_fix → census_after → aggregate
```

**Key improvement**: Project discovery runs once in `StageContext.shared["projects"]`, all stages read from there.

### 3.2 Check Pipeline (gate execution)

Convert `FlextInfraWorkspaceChecker._run_project_loop()` to use DAG per project:
- Each gate becomes a stage
- Gates with `can_fix=True` get a `skip_if` based on `check_only` flag
- **Gate context isolation**: Fresh `GateContext` per project (fixes mutation risk)

### 3.3 Refactor Engine (12 rules)

Rules already execute sequentially per-file. **Optional**: Convert to per-file micro-pipeline only if rule interdependencies warrant it. Otherwise, keep sequential execution but wrap the outer per-project loop as a DAG stage within the codegen pipeline:
- The refactor engine itself becomes one DAG stage (`auto_fix`)
- Internal rule execution stays sequential (rules are order-dependent by design)
- Rule-level retry for transient Rope failures added within the stage handler
- Result propagation via `shared["changes"]` accumulator

### 3.4 Release Orchestrator (4 phases)

Already has explicit phases. Convert to DAG stages:
```
validate → version → build → publish
```

### 3.5 Files to modify in flext-infra

| File | Action |
|------|--------|
| `codegen/pipeline.py` | REWRITE — Use DAG engine |
| `codegen/fixer.py` | MODIFY — Extract sub-stages as handlers |
| `check/workspace_check.py` | MODIFY — Use DAG per project |
| `check/gates_mixin.py` | MODIFY — Gate context isolation |
| `refactor/engine.py` | MODIFY — Rule DAG per file |
| `release/orchestrator.py` | MODIFY — Phase DAG |

---

## Phase 4: Violation Reconciliation with Content Hash

### 4.1 New Model

```python
class ViolationKey(FlextModels.ContractModel):
    """Content-stable violation identifier."""

    module: str
    rule: str
    content_hash: str  # sha256 of ±2 lines context

    @staticmethod
    def from_violation(
        violation: m.Infra.Violation,
        source_lines: Sequence[str],
    ) -> m.Infra.ViolationKey:
        ctx_start = max(0, violation.line - 2)
        ctx_end = min(len(source_lines), violation.line + 3)
        context = "\n".join(source_lines[ctx_start:ctx_end])
        return m.Infra.ViolationKey(
            module=violation.module,
            rule=violation.rule,
            content_hash=u.Cli.sha256_content(context),
        )
```

### 4.2 Integration

Replace current `_violation_key()` in codegen fixer with `ViolationKey.from_violation()`. Reconciliation compares frozensets of `ViolationKey` instead of tuples with line numbers.

### 4.3 Files to modify

| File | Action |
|------|--------|
| `flext-infra/src/flext_infra/_models/codegen.py` | MODIFY — Add ViolationKey |
| `flext-infra/src/flext_infra/codegen/fixer.py` | MODIFY — Use ViolationKey |

---

## Phase 5: Structured Logging for Discarded Returns

Add `FlextLogger` calls at every point where return values are currently silently discarded:

| Location | What's discarded | Log level |
|----------|-----------------|-----------|
| Codegen fixer: MRO migration | `report.replacements_count`, `report.ordering` | INFO |
| Refactor engine | `success=True, modified=False` no-op | DEBUG |
| Namespace validator error | Full error on `is_failure` | WARNING |
| Gate execution | Per-project context state | DEBUG |

No interface changes. Purely additive.

### Files to modify

| File | Action |
|------|--------|
| `codegen/fixer.py` | MODIFY — Add logging at discard points |
| `refactor/engine.py` | MODIFY — Log no-op stages |
| `codegen/namespace_enforcer.py` | MODIFY — Log full errors |
| `check/gates_mixin.py` | MODIFY — Log per-project context |

---

## Phase 6: SSOT Enforcement (Category C)

### 6.1 CI Test

Parametrized test that validates no duplicate utility implementations across flext-core/flext-cli/flext-infra:

```python
@pytest.mark.parametrize(
    "method", ["sha256_content", "sha256_file", "json_read", "json_write"]
)
def test_no_duplicate_implementations(method: str) -> None:
    """Ensure each utility method has exactly one implementation (SSOT)."""
    ...
```

### 6.2 Namespace Enforcer Extension

Add rule to detect re-implemented utilities:
- Scan for methods in `_utilities/` that duplicate parent facade methods
- Report as violation with `severity=error`

---

## Execution Order

1. **Phase 1**: DAG engine in flext-cli (new code, no breaking changes)
2. **Phase 2**: io.py absorption (cleanup, small breaking change in flext-infra)
3. **Phase 3**: Pipeline migration (major refactor in flext-infra)
4. **Phase 4**: Violation key fix (contained change in codegen)
5. **Phase 5**: Logging additions (additive, no breaking changes)
6. **Phase 6**: SSOT enforcement tests (additive)

---

## Verification

### Per-phase gates
- `ruff check src/` — 0 errors
- `pyrefly check src/ tests/` — 0 errors
- `pyright src/` — 0 errors
- `mypy src/` — 0 errors
- `pytest tests/` — all passing

### End-to-end validation
1. Run `flext-infra codegen pipeline` on workspace → verify same output as before migration
2. Run `flext-infra check` on workspace → verify same gate results
3. Run `flext-infra refactor` on test project → verify same transformations
4. Verify no `io.py` references remain in flext-infra
5. Verify `u.Cli.execute_pipeline()` works from other flext projects (import test)

### Performance validation
- Compare pipeline duration before/after (expect improvement from cached project discovery)
- Verify project discovery runs exactly once per pipeline execution
