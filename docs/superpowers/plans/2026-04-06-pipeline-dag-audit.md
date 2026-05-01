# Pipeline DAG Engine & Cross-Library Audit — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable DAG pipeline engine in flext-cli, migrate flext-infra pipelines to use it, and eliminate code duplication across the FLEXT monorepo.

**Architecture:** `graphlib.TopologicalSorter`-backed engine exposed via `u.Cli.execute_pipeline()` with typed protocols (`p.Cli.*`), models (`m.Cli.*`), and constants (`c.Cli.*`). flext-infra pipelines (codegen, check, release) become declarative stage DAGs. Dead code in `io.py` removed.

**Tech Stack:** Python 3.13, graphlib (stdlib), Pydantic v2, flext MRO facade pattern

**Spec:** `docs/superpowers/specs/2026-04-06-pipeline-dag-audit-design.md`

---

## File Structure

### New files (flext-cli)

| File                                             | Responsibility                                                                                 |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| `flext-cli/src/flext_cli/_protocols/pipeline.py` | Pipeline protocols (PipelineStage, PipelineStageContext, PipelineExecutor)                     |
| `flext-cli/src/flext_cli/_typings/pipeline.py`   | Pipeline type aliases (PipelineHandler, PipelineSkipPredicate, PipelineStageStatus)            |
| `flext-cli/src/flext_cli/models/pipeline.py`    | Pipeline models (PipelineStageSpec, PipelineStageResult, PipelineResult, PipelineStageContext) |
| `flext-cli/src/flext_cli/_constants/pipeline.py` | Pipeline constants (Pipeline.DEFAULT_FAIL_FAST, MAX_RETRY)                                     |
| `flext-cli/src/flext_cli/_utilities/pipeline.py` | Pipeline engine (execute_pipeline,_run_stage,_build_sorter)                                    |
| `flext-cli/tests/unit/test_pipeline.py`          | Pipeline engine unit tests                                                                     |

### Modified files (flext-cli)

| File                                   | Change                                   |
| -------------------------------------- | ---------------------------------------- |
| `flext-cli/src/flext_cli/protocols.py` | Add FlextCliProtocolsPipeline to Cli MRO |
| `flext-cli/src/flext_cli/typings.py`   | Add FlextCliTypesPipeline to Cli MRO     |
| `flext-cli/src/flext_cli/models.py`    | Add FlextCliModelsPipeline to Cli MRO    |
| `flext-cli/src/flext_cli/constants.py` | Add FlextCliConstantsPipeline to Cli MRO |
| `flext-cli/src/flext_cli/utilities.py` | Add FlextCliUtilitiesPipeline to Cli MRO |

### Deleted files (flext-infra)

| File                                           | Reason                                             |
| ---------------------------------------------- | -------------------------------------------------- |
| `flext-infra/src/flext_infra/_utilities/io.py` | Dead code — all callers use `u.Cli.json_*` already |

### Modified files (flext-infra)

| File                                                          | Change                                                    |
| ------------------------------------------------------------- | --------------------------------------------------------- |
| `flext-infra/src/flext_infra/utilities.py`                    | Remove FlextInfraUtilitiesIo from Infra MRO               |
| `flext-infra/src/flext_infra/_utilities/__init__.py`          | Remove io.py lazy import                                  |
| `flext-infra/src/flext_infra/__init__.py`                     | Remove FlextInfraUtilitiesIo re-export                    |
| `flext-infra/tests/unit/io/test_infra_json_io.py`             | Delete or redirect tests to u.Cli.json_*                  |
| `flext-infra/tests/unit/validate/basemk_validator_tests.py`   | Change `u.Infra.sha256_file` → `u.Cli.sha256_file`        |
| `flext-infra/src/flext_infra/services/pipeline.py`            | Rewrite to use DAG engine                                 |
| `flext-infra/src/flext_infra/codegen/fixer.py`                | Extract stages as handlers, use ViolationKey, add logging |
| `flext-infra/src/flext_infra/check/workspace_check.py`        | Fresh GateContext per project                             |
| `flext-infra/src/flext_infra/check/_workspace_check_gates.py` | Add structured logging                                    |
| `flext-infra/src/flext_infra/release/orchestrator.py`         | Convert phases to DAG stages                              |
| `flext-infra/src/flext_infra/models/codegen.py`              | Add ViolationKey model                                    |

---

## PHASE 1: DAG Pipeline Engine in flext-cli

### Task 1: Create Pipeline Protocols

**Files:**

- Create: `flext-cli/src/flext_cli/_protocols/pipeline.py`

- [ ] **Step 1: Create protocol definitions**

```python
"""Pipeline protocol contracts for DAG-based stage execution."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_core import r, p

if TYPE_CHECKING:
    from flext_cli import m, t


class FlextCliProtocolsPipeline:
    """Pipeline protocol namespace."""

    @runtime_checkable
    class PipelineStageContext(Protocol):
        """Contract for stage execution context — carries shared state between stages."""

        @property
        def workspace_root(self) -> Path:
            """Workspace root directory."""
            ...

        @property
        def shared(self) -> t.MutableJsonMapping:
            """Mutable shared state between stages — stages write outputs here."""
            ...

        @property
        def settings(self) -> t.JsonMapping:
            """Immutable configuration for the pipeline run."""
            ...

    @runtime_checkable
    class PipelineStage(Protocol):
        """Contract for a callable pipeline stage handler."""

        def __call__(
            self,
            ctx: FlextCliProtocolsPipeline.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            """Execute stage and return typed result."""
            ...

    @runtime_checkable
    class PipelineExecutor(Protocol):
        """Contract for pipeline execution engine."""

        def execute(
            self,
            stages: t.SequenceOf[m.Cli.PipelineStageSpec],
            context: FlextCliProtocolsPipeline.PipelineStageContext,
            *,
            fail_fast: bool = True,
        ) -> p.Result[m.Cli.PipelineResult]:
            """Execute stages in dependency order."""
            ...


__all__: list[str] = ["FlextCliProtocolsPipeline"]
```

- [ ] **Step 2: Wire into protocols facade**

Edit `flext-cli/src/flext_cli/protocols.py`:

```python
# Add import
from flext_cli import (
    FlextCliProtocolsBase,
    FlextCliProtocolsDomain,
    FlextCliProtocolsPipeline,
)


# Update Cli inner class MRO
class Cli(FlextCliProtocolsPipeline, FlextCliProtocolsDomain, FlextCliProtocolsBase):
    """Unified CLI protocol namespace."""
```

- [ ] **Step 3: Run linter**

Run: `cd /home/marlonsc/flext/flext-cli && ruff check src/flext_cli/_protocols/pipeline.py src/flext_cli/protocols.py`
Expected: 0 errors

- [ ] **Step 4: Commit**

```bash
git add flext-cli/src/flext_cli/_protocols/pipeline.py flext-cli/src/flext_cli/protocols.py
git commit -m "feat(flext-cli): add pipeline protocol contracts (p.Cli.PipelineStage, PipelineStageContext, PipelineExecutor)"
```

---

### Task 2: Create Pipeline Type Aliases

**Files:**

- Create: `flext-cli/src/flext_cli/_typings/pipeline.py`

- [ ] **Step 1: Create type alias definitions**

```python
"""Pipeline type aliases for DAG engine."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from typing import TYPE_CHECKING, Literal

from flext_core import r, p

if TYPE_CHECKING:
    from flext_cli import m, p


class FlextCliTypesPipeline:
    """Pipeline type aliases namespace."""

    type PipelineStageStatus = Literal["ok", "skipped", "failed"]
    type PipelineHandler = Callable[
        [p.Cli.PipelineStageContext],
        r[m.Cli.PipelineStageResult],
    ]
    type PipelineSkipPredicate = Callable[[p.Cli.PipelineStageContext], bool]


__all__: list[str] = ["FlextCliTypesPipeline"]
```

- [ ] **Step 2: Wire into typings facade**

Edit `flext-cli/src/flext_cli/typings.py`:

```python
# Add import
from flext_cli import FlextCliTypesBase, FlextCliTypesDomain, FlextCliTypesPipeline


# Update Cli inner class MRO
class Cli(FlextCliTypesPipeline, FlextCliTypesDomain, FlextCliTypesBase):
    """CLI types namespace for cross-project access."""

    YAMLError: type[Exception] = _YamlError
```

- [ ] **Step 3: Run linter**

Run: `cd /home/marlonsc/flext/flext-cli && ruff check src/flext_cli/_typings/pipeline.py src/flext_cli/typings.py`
Expected: 0 errors

- [ ] **Step 4: Commit**

```bash
git add flext-cli/src/flext_cli/_typings/pipeline.py flext-cli/src/flext_cli/typings.py
git commit -m "feat(flext-cli): add pipeline type aliases (t.Cli.PipelineHandler, PipelineSkipPredicate, PipelineStageStatus)"
```

---

### Task 3: Create Pipeline Constants

**Files:**

- Create: `flext-cli/src/flext_cli/_constants/pipeline.py`

- [ ] **Step 1: Create constant definitions**

```python
"""Pipeline execution constants."""

from __future__ import annotations

from typing import Final

from flext_core import t


class FlextCliConstantsPipeline:
    """Pipeline execution constants namespace."""

    class Pipeline:
        """DAG pipeline engine defaults."""

        DEFAULT_FAIL_FAST: Final[bool] = True
        DEFAULT_RETRY: Final[t.RetryCount] = 0
        MAX_RETRY: Final[t.RetryCount] = 3
        STAGE_TIMEOUT_SECONDS: Final[int] = 600


__all__: list[str] = ["FlextCliConstantsPipeline"]
```

- [ ] **Step 2: Wire into constants facade**

Edit `flext-cli/src/flext_cli/constants.py`:

```python
# Add import
from flext_cli import (
    FlextCliConstantsBase,
    FlextCliConstantsSettings,
    FlextCliConstantsEnums,
    FlextCliConstantsPipeline,
)


# Update Cli inner class MRO
class Cli(
    FlextCliConstantsPipeline,
    FlextCliConstantsBase,
    FlextCliConstantsEnums,
    FlextCliConstantsSettings,
):
    """CLI related constants."""
```

- [ ] **Step 3: Run linter**

Run: `cd /home/marlonsc/flext/flext-cli && ruff check src/flext_cli/_constants/pipeline.py src/flext_cli/constants.py`
Expected: 0 errors

- [ ] **Step 4: Commit**

```bash
git add flext-cli/src/flext_cli/_constants/pipeline.py flext-cli/src/flext_cli/constants.py
git commit -m "feat(flext-cli): add pipeline constants (c.Cli.Pipeline.DEFAULT_FAIL_FAST, MAX_RETRY)"
```

---

### Task 4: Create Pipeline Models

**Files:**

- Create: `flext-cli/src/flext_cli/models/pipeline.py`

- [ ] **Step 1: Create model definitions**

```python
"""Pipeline Pydantic domain models for DAG execution."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Annotated, ClassVar

from pydantic import ConfigDict, u.Field

from flext_cli import c, t
from flext_core import FlextModels


class FlextCliModelsPipeline:
    """Pipeline models namespace — flat in m.Cli.*."""

    class PipelineStageContext(FlextModels.ContractModel):
        """Accumulated state passed between pipeline stages."""

        model_config: ClassVar[m.ConfigDict] = ConfigDict(
            extra="forbid",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        workspace_root: Annotated[
            Path,
            u.Field(description="Workspace root directory"),
        ]
        shared: Annotated[
            MutableMapping[str, object],
            u.Field(
                default_factory=lambda: MappingProxyType({}), description="Mutable shared state between stages"
            ),
        ]
        settings: Annotated[
            t.MappingKV[str, object],
            u.Field(
                default_factory=lambda: MappingProxyType({}), description="Immutable pipeline configuration"
            ),
        ]

    class PipelineStageSpec(FlextModels.ContractModel):
        """Declarative stage definition with dependency tracking."""

        model_config: ClassVar[m.ConfigDict] = ConfigDict(
            extra="forbid",
            arbitrary_types_allowed=True,
        )

        stage_id: Annotated[
            str,
            u.Field(description="Unique stage identifier"),
        ]
        depends_on: Annotated[
            frozenset[str],
            u.Field(default=frozenset(), description="Stage IDs this stage depends on"),
        ]
        handler: Annotated[
            t.Cli.PipelineHandler,
            u.Field(description="Callable that executes the stage"),
        ]
        skip_if: Annotated[
            t.Cli.PipelineSkipPredicate | None,
            u.Field(default=None, description="Predicate — skip stage if returns True"),
        ]
        retry: Annotated[
            t.RetryCount,
            u.Field(
                default=c.Cli.Pipeline.DEFAULT_RETRY,
                description="Number of retries on failure",
            ),
        ]

    class PipelineStageResult(FlextModels.ContractModel):
        """What a stage produces after execution."""

        model_config: ClassVar[m.ConfigDict] = ConfigDict(extra="forbid")

        stage_id: Annotated[str, u.Field(description="Stage that produced this result")]
        status: Annotated[
            t.Cli.PipelineStageStatus,
            u.Field(description="Execution outcome"),
        ]
        output: Annotated[
            t.MappingKV[str, object],
            u.Field(default_factory=lambda: MappingProxyType({}), description="Stage output payload"),
        ]
        duration_ms: Annotated[
            float,
            u.Field(default=0.0, description="Execution duration in milliseconds"),
        ]
        error: Annotated[
            str | None,
            u.Field(default=None, description="Error message if failed"),
        ]

    class PipelineResult(FlextModels.ContractModel):
        """Full pipeline execution result — aggregated from all stages."""

        model_config: ClassVar[m.ConfigDict] = ConfigDict(extra="forbid")

        stages: Annotated[
            t.SequenceOf[FlextCliModelsPipeline.PipelineStageResult],
            u.Field(
                default_factory=list, description="Results from all executed stages"
            ),
        ]
        total_duration_ms: Annotated[
            float,
            u.Field(default=0.0, description="Total pipeline execution time"),
        ]

        @property
        def ok(self) -> bool:
            """True if no stage failed."""
            return all(s.status != "failed" for s in self.stages)

        @property
        def failed_stages(self) -> t.SequenceOf[FlextCliModelsPipeline.PipelineStageResult]:
            """Return only failed stage results."""
            return [s for s in self.stages if s.status == "failed"]

        @property
        def skipped_stages(
            self,
        ) -> t.SequenceOf[FlextCliModelsPipeline.PipelineStageResult]:
            """Return only skipped stage results."""
            return [s for s in self.stages if s.status == "skipped"]


__all__: list[str] = ["FlextCliModelsPipeline"]
```

- [ ] **Step 2: Wire into models facade**

Edit `flext-cli/src/flext_cli/models.py`:

```python
# Add import
from flext_cli import FlextCliModelsBase, FlextCliModelsPipeline


# Update Cli inner class MRO
class Cli(FlextCliModelsPipeline, FlextCliModelsBase):
    """CLI project namespace."""
```

- [ ] **Step 3: Run linter**

Run: `cd /home/marlonsc/flext/flext-cli && ruff check src/flext_cli/models/pipeline.py src/flext_cli/models.py`
Expected: 0 errors

- [ ] **Step 4: Commit**

```bash
git add flext-cli/src/flext_cli/models/pipeline.py flext-cli/src/flext_cli/models.py
git commit -m "feat(flext-cli): add pipeline models (m.Cli.PipelineStageSpec, PipelineStageResult, PipelineResult, PipelineStageContext)"
```

---

### Task 5: Write Pipeline Engine Tests (TDD)

**Files:**

- Create: `flext-cli/tests/unit/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

```python
"""Unit tests for the DAG pipeline engine."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from pathlib import Path

import pytest

from flext_cli import c, m, r, p, t, u


# ── Fixtures ────────────────────────────────────────────────────────


def _ok_handler(stage_id: str, output_key: str = "done") -> t.Cli.PipelineHandler:
    """Factory for a handler that succeeds and writes to shared."""

    def handler(ctx: m.Cli.PipelineStageContext) -> p.Result[m.Cli.PipelineStageResult]:
        ctx.shared[output_key] = stage_id
        return r[m.Cli.PipelineStageResult].ok(
            m.Cli.PipelineStageResult(
                stage_id=stage_id,
                status="ok",
                output={output_key: stage_id},
                duration_ms=1.0,
            ),
        )

    return handler


def _fail_handler(stage_id: str) -> t.Cli.PipelineHandler:
    """Factory for a handler that fails."""

    def handler(ctx: m.Cli.PipelineStageContext) -> p.Result[m.Cli.PipelineStageResult]:
        return r[m.Cli.PipelineStageResult].fail(f"{stage_id} failed")

    return handler


def _skip_always(_ctx: m.Cli.PipelineStageContext) -> bool:
    return True


def _make_ctx(tmp_path: Path) -> m.Cli.PipelineStageContext:
    return m.Cli.PipelineStageContext(workspace_root=tmp_path)


# ── Tests ───────────────────────────────────────────────────────────


class TestPipelineExecute:
    """Test u.Cli.execute_pipeline()."""

    def test_single_stage_ok(self, tmp_path: Path) -> None:
        """Single stage executes and returns ok."""
        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="alpha",
                handler=_ok_handler("alpha"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_success
        pipeline = result.value
        assert pipeline.ok
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0].stage_id == "alpha"
        assert pipeline.stages[0].status == "ok"

    def test_dependency_order(self, tmp_path: Path) -> None:
        """Stages execute in topological order — B depends on A."""
        execution_order: list[str] = []

        def tracking_handler(stage_id: str) -> t.Cli.PipelineHandler:
            def handler(
                ctx: m.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                execution_order.append(stage_id)
                return r[m.Cli.PipelineStageResult].ok(
                    m.Cli.PipelineStageResult(stage_id=stage_id, status="ok"),
                )

            return handler

        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=tracking_handler("b"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="a",
                handler=tracking_handler("a"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_success
        assert execution_order == ["a", "b"]

    def test_shared_state_propagation(self, tmp_path: Path) -> None:
        """Stage B can read what stage A wrote to shared."""
        received: dict[str, object] = {}

        def reader(
            ctx: m.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            received["from_a"] = ctx.shared.get("a_output")
            return r[m.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult(stage_id="b", status="ok"),
            )

        def writer(
            ctx: m.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            ctx.shared["a_output"] = "hello"
            return r[m.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult(stage_id="a", status="ok"),
            )

        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=writer),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=reader,
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_success
        assert received["from_a"] == "hello"

    def test_fail_fast_stops_on_failure(self, tmp_path: Path) -> None:
        """With fail_fast=True, pipeline stops after first failure."""
        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=_fail_handler("a")),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=_ok_handler("b"),
            ),
        ]
        result = u.Cli.execute_pipeline(
            stages,
            _make_ctx(tmp_path),
            fail_fast=True,
        )
        assert result.is_success  # Pipeline itself succeeds, result.ok is False
        pipeline = result.value
        assert not pipeline.ok
        assert len(pipeline.failed_stages) == 1
        assert pipeline.failed_stages[0].stage_id == "a"

    def test_skip_predicate(self, tmp_path: Path) -> None:
        """Stage with skip_if returning True is skipped."""
        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="skippable",
                handler=_ok_handler("skippable"),
                skip_if=_skip_always,
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_success
        pipeline = result.value
        assert pipeline.ok
        assert pipeline.stages[0].status == "skipped"

    def test_cycle_detection(self, tmp_path: Path) -> None:
        """Circular dependencies produce a failure result."""
        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="a",
                depends_on=frozenset({"b"}),
                handler=_ok_handler("a"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=_ok_handler("b"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_failure

    def test_retry_on_failure(self, tmp_path: Path) -> None:
        """Stage retries up to retry count before failing."""
        call_count = 0

        def flaky(
            ctx: m.Cli.PipelineStageContext,
        ) -> p.Result[m.Cli.PipelineStageResult]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return r[m.Cli.PipelineStageResult].fail("transient")
            return r[m.Cli.PipelineStageResult].ok(
                m.Cli.PipelineStageResult(stage_id="flaky", status="ok"),
            )

        stages = [
            m.Cli.PipelineStageSpec(
                stage_id="flaky",
                handler=flaky,
                retry=3,
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_success
        assert result.value.ok
        assert call_count == 3

    def test_empty_pipeline(self, tmp_path: Path) -> None:
        """Empty pipeline returns ok with no stages."""
        result = u.Cli.execute_pipeline([], _make_ctx(tmp_path))
        assert result.is_success
        assert result.value.ok
        assert len(result.value.stages) == 0

    def test_total_duration_tracked(self, tmp_path: Path) -> None:
        """Pipeline tracks total duration."""
        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=_ok_handler("a")),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_success
        assert result.value.total_duration_ms >= 0.0

    def test_diamond_dependency(self, tmp_path: Path) -> None:
        """Diamond DAG: A → B, A → C, B → D, C → D."""
        order: list[str] = []

        def track(sid: str) -> t.Cli.PipelineHandler:
            def h(
                ctx: m.Cli.PipelineStageContext,
            ) -> p.Result[m.Cli.PipelineStageResult]:
                order.append(sid)
                return r[m.Cli.PipelineStageResult].ok(
                    m.Cli.PipelineStageResult(stage_id=sid, status="ok"),
                )

            return h

        stages = [
            m.Cli.PipelineStageSpec(stage_id="a", handler=track("a")),
            m.Cli.PipelineStageSpec(
                stage_id="b",
                depends_on=frozenset({"a"}),
                handler=track("b"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="c",
                depends_on=frozenset({"a"}),
                handler=track("c"),
            ),
            m.Cli.PipelineStageSpec(
                stage_id="d",
                depends_on=frozenset({"b", "c"}),
                handler=track("d"),
            ),
        ]
        result = u.Cli.execute_pipeline(stages, _make_ctx(tmp_path))
        assert result.is_success
        assert order[0] == "a"
        assert order[-1] == "d"
        assert set(order[1:3]) == {"b", "c"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/marlonsc/flext/flext-cli && pytest tests/unit/test_pipeline.py -v --no-header 2>&1 | head -30`
Expected: FAIL — `execute_pipeline` not defined yet

- [ ] **Step 3: Commit test file**

```bash
git add flext-cli/tests/unit/test_pipeline.py
git commit -m "test(flext-cli): add pipeline engine unit tests (TDD red phase)"
```

---

### Task 6: Implement Pipeline Engine

**Files:**

- Create: `flext-cli/src/flext_cli/_utilities/pipeline.py`

- [ ] **Step 1: Implement the engine**

```python
"""DAG pipeline execution engine backed by graphlib.TopologicalSorter."""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from graphlib import CycleError, TopologicalSorter
from typing import ClassVar

from flext_cli import c, m, r, p, t


class FlextCliUtilitiesPipeline:
    """Pipeline execution utilities — exposed as u.Cli.execute_pipeline()."""

    _pipeline_logger: ClassVar[FlextLogger] = u.fetch_logger(__name__)

    @staticmethod
    def execute_pipeline(
        stages: t.SequenceOf[m.Cli.PipelineStageSpec],
        context: m.Cli.PipelineStageContext,
        *,
        fail_fast: bool = c.Cli.Pipeline.DEFAULT_FAIL_FAST,
        logger: FlextLogger | None = None,
    ) -> p.Result[m.Cli.PipelineResult]:
        """Execute pipeline stages in topological order.

        Uses graphlib.TopologicalSorter for dependency resolution.
        Stages share state via context.shared mutable mapping.
        """
        log = logger or FlextCliUtilitiesPipeline._pipeline_logger
        pipeline_start = time.monotonic()
        results: list[m.Cli.PipelineStageResult] = []

        if not stages:
            return r[m.Cli.PipelineResult].ok(
                m.Cli.PipelineResult(stages=[], total_duration_ms=0.0),
            )

        # Build stage lookup and dependency graph.
        stage_map: t.MappingKV[str, m.Cli.PipelineStageSpec] = {
            s.stage_id: s for s in stages
        }

        # Build TopologicalSorter graph.
        sorter: TopologicalSorter[str] = TopologicalSorter()
        for spec in stages:
            sorter.add(spec.stage_id, *spec.depends_on)

        try:
            order = tuple(sorter.static_order())
        except CycleError as exc:
            return r[m.Cli.PipelineResult].fail(
                f"pipeline cycle detected: {exc}",
            )

        failed = False
        for stage_id in order:
            spec = stage_map.get(stage_id)
            if spec is None:
                # Dependency referenced but not defined — skip silently.
                continue

            if failed and fail_fast:
                results.append(
                    m.Cli.PipelineStageResult(
                        stage_id=stage_id,
                        status="skipped",
                        error="skipped due to prior failure (fail_fast)",
                    ),
                )
                continue

            stage_result = FlextCliUtilitiesPipeline._run_stage(
                spec,
                context,
                log,
            )
            results.append(stage_result)

            if stage_result.status == "failed":
                failed = True

        total_ms = (time.monotonic() - pipeline_start) * 1000
        pipeline_result = m.Cli.PipelineResult(
            stages=results,
            total_duration_ms=total_ms,
        )

        log.info(
            "pipeline_complete",
            total_stages=len(results),
            failed=len(pipeline_result.failed_stages),
            skipped=len(pipeline_result.skipped_stages),
            duration_ms=round(total_ms, 2),
        )

        return r[m.Cli.PipelineResult].ok(pipeline_result)

    @staticmethod
    def _run_stage(
        spec: m.Cli.PipelineStageSpec,
        context: m.Cli.PipelineStageContext,
        log: FlextLogger,
    ) -> m.Cli.PipelineStageResult:
        """Execute a single stage with skip check and retry logic."""
        # Check skip predicate.
        if spec.skip_if is not None and spec.skip_if(context):
            log.debug("stage_skipped", stage_id=spec.stage_id, reason="skip_if")
            return m.Cli.PipelineStageResult(
                stage_id=spec.stage_id,
                status="skipped",
            )

        max_attempts = 1 + min(spec.retry, c.Cli.Pipeline.MAX_RETRY)
        last_error: str | None = None

        for attempt in range(1, max_attempts + 1):
            stage_start = time.monotonic()
            try:
                result = spec.handler(context)
            except Exception as exc:
                last_error = f"stage {spec.stage_id} raised: {exc}"
                log.warning(
                    "stage_exception",
                    stage_id=spec.stage_id,
                    attempt=attempt,
                    error=str(exc),
                )
                continue

            duration_ms = (time.monotonic() - stage_start) * 1000

            if result.is_success:
                stage_result = result.value
                # Override duration with measured value.
                return m.Cli.PipelineStageResult(
                    stage_id=stage_result.stage_id,
                    status=stage_result.status,
                    output=stage_result.output,
                    duration_ms=duration_ms,
                    error=stage_result.error,
                )

            last_error = result.error or f"stage {spec.stage_id} failed"
            log.debug(
                "stage_retry",
                stage_id=spec.stage_id,
                attempt=attempt,
                error=last_error,
            )

        # All attempts exhausted.
        log.warning(
            "stage_failed",
            stage_id=spec.stage_id,
            attempts=max_attempts,
            error=last_error,
        )
        return m.Cli.PipelineStageResult(
            stage_id=spec.stage_id,
            status="failed",
            error=last_error,
        )


__all__: list[str] = ["FlextCliUtilitiesPipeline"]
```

- [ ] **Step 2: Wire into utilities facade**

Edit `flext-cli/src/flext_cli/utilities.py`:

```python
# Add import
from flext_cli import (
    FlextCliUtilitiesBase,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesYaml,
)


# Update Cli inner class MRO
class Cli(
    FlextCliUtilitiesPipeline,
    FlextCliUtilitiesBase,
    FlextCliUtilitiesJson,
    FlextCliUtilitiesToml,
    FlextCliUtilitiesYaml,
):
    """Command line interface specific utilities."""
```

- [ ] **Step 3: Regenerate lazy init files**

Run: `cd /home/marlonsc/flext/flext-cli && make gen`
Expected: Auto-generated `__init__.py` files updated with new pipeline modules

- [ ] **Step 4: Run tests**

Run: `cd /home/marlonsc/flext/flext-cli && pytest tests/unit/test_pipeline.py -v --no-header`
Expected: ALL PASS (10 tests)

- [ ] **Step 5: Run full linter suite**

Run: `cd /home/marlonsc/flext/flext-cli && ruff check src/ && pyrefly check src/ tests/ && pyright src/`
Expected: 0 errors across all linters

- [ ] **Step 6: Commit**

```bash
git add flext-cli/src/flext_cli/_utilities/pipeline.py flext-cli/src/flext_cli/utilities.py
git add flext-cli/src/flext_cli/_protocols/__init__.py flext-cli/src/flext_cli/_typings/__init__.py
git add flext-cli/src/flext_cli/models/__init__.py flext-cli/src/flext_cli/_constants/__init__.py
git add flext-cli/src/flext_cli/_utilities/__init__.py
git commit -m "feat(flext-cli): implement DAG pipeline engine (u.Cli.execute_pipeline) with graphlib TopologicalSorter"
```

---

## PHASE 2: io.py Dead Code Removal

### Task 7: Delete io.py and Remove from MRO

**Key finding from audit:** All production callers use `u.Cli.json_read()`/`u.Cli.json_write()`/`u.Cli.json_parse()`/`u.Cli.sha256_*()` — the flext-cli versions. io.py methods (`read_json`, `write_json`, `parse`, `serialize`, `sha256_*`) have different names and zero production callers. Only test files reference them.

**Files:**

- Delete: `flext-infra/src/flext_infra/_utilities/io.py`
- Modify: `flext-infra/src/flext_infra/utilities.py`
- Modify: `flext-infra/src/flext_infra/_utilities/__init__.py`

- [ ] **Step 1: Remove FlextInfraUtilitiesIo from utilities facade MRO**

Edit `flext-infra/src/flext_infra/utilities.py` — remove `FlextInfraUtilitiesIo` from:

1. The import statement
2. The `Infra` inner class MRO bases

- [ ] **Step 2: Remove from `_utilities/__init__.py`**

Edit `flext-infra/src/flext_infra/_utilities/__init__.py` — remove:

1. The TYPE_CHECKING import of `FlextInfraUtilitiesIo`
2. The lazy import entry for `FlextInfraUtilitiesIo`
3. The `__all__` entry

- [ ] **Step 3: Remove from `__init__.py` re-export**

Edit `flext-infra/src/flext_infra/__init__.py` — remove:

1. The lazy import entry for `FlextInfraUtilitiesIo`
2. The `__all__` entry

- [ ] **Step 4: Delete io.py**

```bash
mv flext-infra/src/flext_infra/_utilities/io.py flext-infra/src/flext_infra/_utilities/io.py.bak
```

- [ ] **Step 5: Delete or update io test file**

```bash
mv flext-infra/tests/unit/io/test_infra_json_io.py flext-infra/tests/unit/io/test_infra_json_io.py.bak
```

- [ ] **Step 6: Fix basemk_validator test**

Edit `flext-infra/tests/unit/validate/basemk_validator_tests.py` line 135:

```python
# Before:
return u.Infra.sha256_file(path)
# After:
return u.Cli.sha256_file(path)
```

- [ ] **Step 7: Run linters + tests**

Run: `cd /home/marlonsc/flext/flext-infra && ruff check src/ && pyrefly check src/ tests/ && pytest tests/ -x --no-header -q`
Expected: 0 lint errors, all tests passing

- [ ] **Step 8: Commit**

```bash
git add flext-infra/src/flext_infra/utilities.py flext-infra/src/flext_infra/_utilities/__init__.py
git add flext-infra/src/flext_infra/__init__.py
git add flext-infra/tests/unit/validate/basemk_validator_tests.py
git commit -m "refactor(flext-infra): remove dead io.py — all callers already use u.Cli.json_*/sha256_*"
```

---

## PHASE 3: Migrate flext-infra Pipelines to DAG Engine

### Task 8: Migrate Codegen Pipeline to DAG

**Files:**

- Modify: `flext-infra/src/flext_infra/services/pipeline.py`

- [ ] **Step 1: Read current pipeline.py to understand exact structure**

Read: `flext-infra/src/flext_infra/services/pipeline.py`

- [ ] **Step 2: Refactor execute() to declare stages as DAG**

The current `execute()` method calls 6 stages sequentially. Refactor to:

1. Define stage handler functions that take `m.Cli.PipelineStageContext` and return `r[m.Cli.PipelineStageResult]`
2. Build `Sequence[m.Cli.PipelineStageSpec]` with correct `depends_on`
3. Call `u.Cli.execute_pipeline(stages, ctx)`
4. Extract final result from pipeline result

Key pattern for each handler:

```python
def _stage_py_typed(
    ctx: m.Cli.PipelineStageContext,
) -> p.Result[m.Cli.PipelineStageResult]:
    workspace = ctx.workspace_root
    # ... existing logic ...
    return r[m.Cli.PipelineStageResult].ok(
        m.Cli.PipelineStageResult(
            stage_id="py_typed",
            status="ok",
            output={"files_processed": count},
        ),
    )
```

Project discovery cached in `ctx.shared["projects"]` by first stage.

- [ ] **Step 3: Run tests**

Run: `cd /home/marlonsc/flext/flext-infra && pytest tests/ -x -k pipeline --no-header -q`
Expected: All pipeline tests pass

- [ ] **Step 4: Commit**

```bash
git add flext-infra/src/flext_infra/services/pipeline.py
git commit -m "refactor(flext-infra): migrate codegen pipeline to DAG engine (u.Cli.execute_pipeline)"
```

---

### Task 9: Fix Gate Context Isolation

**Files:**

- Modify: `flext-infra/src/flext_infra/check/_workspace_check_gates.py`

- [ ] **Step 1: Read current gates mixin**

Read: `flext-infra/src/flext_infra/check/_workspace_check_gates.py`

- [ ] **Step 2: Create fresh GateContext per project**

In `_run_single_project()`, create a new `GateContext` for each project instead of sharing one:

```python
def _run_single_project(
    self,
    project_name: str,
    index: int,
    total: int,
    resolved_gates: t.StrSequence,
    ctx: m.Infra.GateContext,
) -> m.Infra.ProjectResult | None:
    project_dir = self._workspace_root / project_name
    # Create isolated context per project.
    project_ctx = m.Infra.GateContext(
        workspace=ctx.workspace_root,
        reports_dir=ctx.reports_dir / project_name,
        apply_fixes=ctx.apply_fixes,
        check_only=ctx.check_only,
        fail_fast=ctx.fail_fast,
        ruff_args=ctx.ruff_args,
        pyright_args=ctx.pyright_args,
    )
    project_result = self._check_project_with_ctx(
        project_dir,
        resolved_gates,
        project_ctx,
    )
    return project_result
```

- [ ] **Step 3: Add structured logging per gate**

```python
self._pipeline_logger.debug(
    "gate_executed",
    project=project_name,
    gate=gate_id,
    passed=execution.result.passed,
    duration_ms=execution.result.duration_ms,
)
```

- [ ] **Step 4: Run tests**

Run: `cd /home/marlonsc/flext/flext-infra && pytest tests/ -x -k check --no-header -q`
Expected: All check tests pass

- [ ] **Step 5: Commit**

```bash
git add flext-infra/src/flext_infra/check/_workspace_check_gates.py
git commit -m "fix(flext-infra): isolate GateContext per project to prevent mutation leaks"
```

---

### Task 10: Migrate Release Orchestrator to DAG

**Files:**

- Modify: `flext-infra/src/flext_infra/release/orchestrator.py`

- [ ] **Step 1: Read current orchestrator**

Read: `flext-infra/src/flext_infra/release/orchestrator.py`

- [ ] **Step 2: Convert phase dispatch to DAG**

Replace the sequential `for phase in phases` loop with DAG stages:

```python
stages = [
    m.Cli.PipelineStageSpec(
        stage_id="validate",
        handler=lambda ctx: self._run_phase_validate(ctx),
    ),
    m.Cli.PipelineStageSpec(
        stage_id="version",
        depends_on=frozenset({"validate"}),
        handler=lambda ctx: self._run_phase_version(ctx),
    ),
    m.Cli.PipelineStageSpec(
        stage_id="build",
        depends_on=frozenset({"version"}),
        handler=lambda ctx: self._run_phase_build(ctx),
    ),
    m.Cli.PipelineStageSpec(
        stage_id="publish",
        depends_on=frozenset({"build"}),
        handler=lambda ctx: self._run_phase_publish(ctx),
    ),
]
# Filter to only requested phases.
requested = frozenset(phases)
active_stages = [s for s in stages if s.stage_id in requested]
result = u.Cli.execute_pipeline(active_stages, pipeline_ctx, fail_fast=True)
```

- [ ] **Step 3: Run tests**

Run: `cd /home/marlonsc/flext/flext-infra && pytest tests/ -x -k release --no-header -q`
Expected: All release tests pass

- [ ] **Step 4: Commit**

```bash
git add flext-infra/src/flext_infra/release/orchestrator.py
git commit -m "refactor(flext-infra): migrate release orchestrator to DAG pipeline engine"
```

---

## PHASE 4: Violation Reconciliation with Content Hash

### Task 11: Add ViolationKey Model

**Files:**

- Modify: `flext-infra/src/flext_infra/models/codegen.py`

- [ ] **Step 1: Read current codegen models**

Read: `flext-infra/src/flext_infra/models/codegen.py`

- [ ] **Step 2: Add ViolationKey model**

```python
class ViolationKey(FlextModels.ContractModel):
    """Content-stable violation identifier — resilient to line shifts."""

    model_config: ClassVar[m.ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    module: Annotated[str, u.Field(description="Module containing the violation")]
    rule: Annotated[str, u.Field(description="Rule that was violated")]
    content_hash: Annotated[
        str, u.Field(description="SHA256 of surrounding context lines")
    ]

    @staticmethod
    def from_violation(
        violation: FlextInfraModelsCodegen.CensusViolation,
        source_lines: t.StrSequence,
    ) -> FlextInfraModelsCodegen.ViolationKey:
        """Build key from violation and source context (±2 lines)."""
        ctx_start = max(0, violation.line - 2)
        ctx_end = min(len(source_lines), violation.line + 3)
        context = "\n".join(source_lines[ctx_start:ctx_end])
        return FlextInfraModelsCodegen.ViolationKey(
            module=violation.module,
            rule=violation.rule,
            content_hash=u.Cli.sha256_content(context),
        )
```

- [ ] **Step 3: Commit**

```bash
git add flext-infra/src/flext_infra/models/codegen.py
git commit -m "feat(flext-infra): add ViolationKey model with content-hash-based identification"
```

---

### Task 12: Integrate ViolationKey into Fixer

**Files:**

- Modify: `flext-infra/src/flext_infra/codegen/fixer.py`

- [ ] **Step 1: Read fixer.py violation key and reconciliation methods**

Read: `flext-infra/src/flext_infra/codegen/fixer.py` (focus on `_violation_key` and `_reconcile_namespace_violations`)

- [ ] **Step 2: Replace `_violation_key` with `ViolationKey.from_violation`**

In `_reconcile_namespace_violations()`, replace:

```python
# Before:
remaining_keys = {
    cls._violation_key(violation) for violation in remaining_result.unwrap_or(())
}
for violation in initial_violations:
    if violation.fixable and cls._violation_key(violation) not in remaining_keys:
        ctx.violations_fixed.append(violation)
    else:
        ctx.violations_skipped.append(violation)

# After:
source_lines = (
    project_path_file.read_text().splitlines() if project_path_file.exists() else []
)
remaining_keys = {
    m.Infra.ViolationKey.from_violation(v, source_lines)
    for v in remaining_result.unwrap_or(())
}
for violation in initial_violations:
    key = m.Infra.ViolationKey.from_violation(violation, source_lines)
    if violation.fixable and key not in remaining_keys:
        ctx.violations_fixed.append(violation)
    else:
        ctx.violations_skipped.append(violation)
```

- [ ] **Step 3: Remove old `_violation_key` static method**

Delete the old tuple-based method.

- [ ] **Step 4: Run tests**

Run: `cd /home/marlonsc/flext/flext-infra && pytest tests/ -x -k fixer --no-header -q`
Expected: All fixer tests pass

- [ ] **Step 5: Commit**

```bash
git add flext-infra/src/flext_infra/codegen/fixer.py
git commit -m "fix(flext-infra): replace brittle line-number violation keys with content-hash ViolationKey"
```

---

## PHASE 5: Structured Logging for Discarded Returns

### Task 13: Add Logging at Discard Points

**Files:**

- Modify: `flext-infra/src/flext_infra/codegen/fixer.py`
- Modify: `flext-infra/src/flext_infra/refactor/engine.py`

- [ ] **Step 1: Add logging to fixer.py MRO migration section**

At the point where MRO migration report fields are discarded (~line 124-143):

```python
log.info(
    "mro_migration_complete",
    project=project_path.name,
    migrations=len(report.migrations),
    rewrites=len(report.rewrites) if hasattr(report, "rewrites") else 0,
)
```

- [ ] **Step 2: Add logging to fixer.py namespace validator error**

At the point where namespace validator errors are silently skipped:

```python
if initial_violations_result.is_failure:
    log.warning(
        "namespace_validation_failed",
        project=project_path.name,
        error=initial_violations_result.error,
    )
    ctx.skip(...)
```

- [ ] **Step 3: Add logging to refactor engine no-op detection**

In refactor engine, when `success=True, modified=False`:

```python
if result.success and not result.modified:
    log.debug(
        "refactor_noop",
        file=str(result.file_path),
        rule=result.rule_id,
    )
```

- [ ] **Step 4: Run tests**

Run: `cd /home/marlonsc/flext/flext-infra && pytest tests/ -x --no-header -q`
Expected: All tests pass (logging is additive)

- [ ] **Step 5: Commit**

```bash
git add flext-infra/src/flext_infra/codegen/fixer.py flext-infra/src/flext_infra/refactor/engine.py
git commit -m "fix(flext-infra): add structured logging at return-value discard points"
```

---

## PHASE 6: SSOT Enforcement Tests

### Task 14: Create SSOT Duplicate Detection Test

**Files:**

- Create: `flext-infra/tests/unit/test_ssot_enforcement.py`

- [ ] **Step 1: Write parametrized SSOT test**

```python
"""SSOT enforcement: no duplicate utility implementations across the workspace."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parents[4]  # flext/ root

# Methods that must have exactly ONE implementation across the workspace.
SSOT_METHODS = [
    ("sha256_content", "flext_cli"),
    ("sha256_file", "flext_cli"),
    ("json_read", "flext_cli"),
    ("json_write", "flext_cli"),
    ("json_parse", "flext_cli"),
]


def _find_method_definitions(
    method_name: str,
    search_dirs: tuple[Path, ...],
) -> list[str]:
    """Find all static/class methods with exact name in _utilities/ dirs."""
    found: list[str] = []
    for search_dir in search_dirs:
        utils_dir = search_dir / "_utilities"
        if not utils_dir.exists():
            continue
        for py_file in utils_dir.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            try:
                tree = ast.parse(py_file.read_text())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    found.append(f"{py_file.relative_to(WORKSPACE)}")
    return found


@pytest.mark.parametrize(
    ("method", "canonical_package"),
    SSOT_METHODS,
    ids=[m for m, _ in SSOT_METHODS],
)
def test_no_duplicate_utility_implementations(
    method: str,
    canonical_package: str,
) -> None:
    """Each utility method must have exactly one implementation in its canonical package."""
    search_dirs = (
        WORKSPACE / "flext-core" / "src" / "flext_core",
        WORKSPACE / "flext-cli" / "src" / "flext_cli",
        WORKSPACE / "flext-infra" / "src" / "flext_infra",
    )
    definitions = _find_method_definitions(method, search_dirs)
    canonical_defs = [d for d in definitions if canonical_package in d]
    duplicate_defs = [d for d in definitions if canonical_package not in d]

    assert len(canonical_defs) >= 1, (
        f"{method} not found in canonical package {canonical_package}"
    )
    assert len(duplicate_defs) == 0, (
        f"{method} has duplicate implementations outside {canonical_package}: {duplicate_defs}"
    )
```

- [ ] **Step 2: Run test**

Run: `cd /home/marlonsc/flext/flext-infra && pytest tests/unit/test_ssot_enforcement.py -v --no-header`
Expected: ALL PASS (5 tests) — confirms io.py deletion removed all duplicates

- [ ] **Step 3: Commit**

```bash
git add flext-infra/tests/unit/test_ssot_enforcement.py
git commit -m "test(flext-infra): add SSOT enforcement tests — detect duplicate utility implementations"
```

---

## Verification Checklist

After all tasks:

- [ ] **flext-cli linters**: `cd flext-cli && ruff check src/ && pyrefly check src/ tests/ && pyright src/ && mypy src/`
- [ ] **flext-cli tests**: `cd flext-cli && pytest tests/ -x -q`
- [ ] **flext-infra linters**: `cd flext-infra && ruff check src/ && pyrefly check src/ tests/ && pyright src/ && mypy src/`
- [ ] **flext-infra tests**: `cd flext-infra && pytest tests/ -x -q`
- [ ] **E2E**: `flext-infra codegen pipeline` produces same output as before
- [ ] **E2E**: `flext-infra check` produces same gate results
- [ ] **Import test**: `python -c "from flext_cli import u; print(u.Cli.execute_pipeline)"`
- [ ] **No io.py references**: `grep -r "FlextInfraUtilitiesIo" flext-infra/src/` returns nothing
