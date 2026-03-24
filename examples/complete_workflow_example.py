"""08_complete_workflow.py - Complete Workflow Example.

Demonstrates complete workflow integration with:
- Integração completa de todas as capacidades
- Railway pattern abrangente
- Processamento paralelo em todas as etapas
- Auto-detecção e builders inteligentes
- Validação integrada end-to-end

This example showcases the complete FLEXT enterprise data integration
workflow with comprehensive capabilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import (
    Callable,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum, unique
from typing import ClassVar

from flext_core import r
from pydantic import BaseModel, ConfigDict, Field

from flext import t

type WorkflowScalar = Decimal | bool | bytes | date | datetime | float | int | str
type WorkflowValue = WorkflowScalar | t.StrSequence | Mapping[str, WorkflowScalar]

ProcessingDict = Mapping[str, WorkflowValue]
WorkflowContent = Mapping[str, WorkflowValue]


def _new_workflow_content() -> WorkflowContent:
    return {}


def _new_workflow_config() -> Mapping[str, t.Scalar | float]:
    return {}


class WorkflowData(BaseModel):
    """Data container for workflow processing."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        arbitrary_types_allowed=True, extra="allow"
    )
    content: WorkflowContent = Field(default_factory=_new_workflow_content)


def _new_str_list() -> MutableSequence[str]:
    return []


def _new_scalar_dict() -> MutableMapping[str, WorkflowScalar]:
    return {}


def _new_stage_metadata_dict() -> MutableMapping[str, float | int | bool]:
    return {}


def _new_performance_metrics_dict() -> MutableMapping[
    str, float | int | Mapping[str, float | int]
]:
    return {}


def _new_stage_result_list() -> MutableSequence[
    CompleteWorkflowExample.WorkflowStageResult
]:
    return []


def _new_aggregated_metrics_dict() -> MutableMapping[
    str, Decimal | bool | bytes | float | int | str
]:
    return {}


class CompleteWorkflowExample:
    """Complete workflow example demonstrating FLEXT enterprise data integration capabilities."""

    @unique
    class Stage(StrEnum):
        """Processing stage enumeration."""

        VALIDATION = "validation"
        PROCESSING = "processing"
        ANALYSIS = "analysis"
        AGGREGATION = "aggregation"

    class WorkflowContext(BaseModel):
        """Complete workflow context with correlation and metadata."""

        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

        workflow_id: str = Field(description="Unique workflow identifier")
        correlation_id: str = Field(description="Correlation ID for tracking")
        start_time: float = Field(description="Workflow start timestamp")
        stages: t.StrSequence = Field(
            default_factory=lambda: [
                "validation",
                "processing",
                "analysis",
                "aggregation",
            ],
            description="List of workflow stages to execute",
        )
        metadata: Mapping[str, WorkflowScalar] = Field(
            default_factory=_new_scalar_dict,
            description="Workflow metadata key-value pairs",
        )
        performance_metrics: MutableMapping[
            str, float | int | Mapping[str, float | int]
        ] = Field(
            default_factory=_new_performance_metrics_dict,
            description="Performance metrics collected during workflow execution",
        )

    class WorkflowStageResult(BaseModel):
        """Result of a workflow stage with comprehensive tracking."""

        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

        stage_name: str = Field(description="Name of the workflow stage")
        workflow_id: str = Field(description="Associated workflow ID")
        correlation_id: str = Field(description="Correlation ID for tracking")
        success: bool = Field(description="Whether the stage succeeded")
        items_processed: int = Field(description="Total items processed in stage")
        items_succeeded: int = Field(description="Items that succeeded")
        items_failed: int = Field(description="Items that failed")
        processing_time: float = Field(description="Time taken to process stage")
        errors: t.StrSequence = Field(
            default_factory=_new_str_list,
            description="List of errors encountered",
        )
        warnings: t.StrSequence = Field(
            default_factory=_new_str_list,
            description="List of warnings encountered",
        )
        stage_metadata: Mapping[str, float | int | bool] = Field(
            default_factory=_new_stage_metadata_dict,
            description="Stage-specific metadata",
        )

    class CompleteWorkflowResult(BaseModel):
        """Complete workflow result with all stages aggregated."""

        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

        workflow_id: str = Field(description="Unique workflow identifier")
        correlation_id: str = Field(description="Correlation ID for tracking")
        total_stages: int = Field(description="Total number of stages")
        completed_stages: int = Field(description="Number of completed stages")
        failed_stages: int = Field(description="Number of failed stages")
        total_processing_time: float = Field(
            description="Total workflow processing time"
        )
        stage_results: Sequence[CompleteWorkflowExample.WorkflowStageResult] = Field(
            default_factory=_new_stage_result_list,
            description="Results from each workflow stage",
        )
        aggregated_metrics: Mapping[str, Decimal | bool | bytes | float | int | str] = (
            Field(
                default_factory=_new_aggregated_metrics_dict,
                description="Aggregated metrics across all stages",
            )
        )
        workflow_status: str = Field(
            default="unknown",
            description="Overall workflow status",
        )

    class WorkflowOrchestrator(BaseModel):
        """Resource-managed workflow orchestrator with automatic context lifecycle."""

        auto_execute: bool = True
        data: Sequence[ProcessingDict] = Field(default_factory=tuple)
        workflow_config: Mapping[str, t.Scalar | float] = Field(
            default_factory=_new_workflow_config
        )

        def execute(self) -> r[WorkflowData]:
            """Execute complete workflow with automatic resource management."""
            context = self._setup_context()
            try:
                return self._execute_workflow(self.data, context)
            finally:
                self._cleanup_context(context)

        def _aggregate_results(
            self,
            item: ProcessingDict,
            _context: CompleteWorkflowExample.WorkflowContext,
        ) -> r[WorkflowData]:
            """Aggregate results."""
            complexity_score_raw = item.get("complexity_score", 0)
            complexity_score = (
                float(complexity_score_raw)
                if isinstance(complexity_score_raw, (int, float))
                else 0.0
            )
            final_score = complexity_score + (
                1 if bool(item.get("is_valid", False)) else 0
            )
            content_payload: WorkflowContent = {
                **self._process_stage(
                    item,
                    0,
                    "aggregated",
                    True,
                    lambda _i: {"final_score": final_score},
                )
            }
            workflow_data = WorkflowData.model_validate({"content": content_payload})
            return r.ok(workflow_data)

        def _aggregate_workflow_metrics(
            self,
            stage_results: Sequence[CompleteWorkflowExample.WorkflowStageResult],
            total_time: float,
        ) -> Mapping[str, float | int]:
            """Aggregate metrics across all workflow stages."""
            if not stage_results:
                return {}
            total_items_processed = sum(r.items_processed for r in stage_results)
            total_items_succeeded = sum(r.items_succeeded for r in stage_results)
            total_processing_time = sum(r.processing_time for r in stage_results)
            return {
                "total_items_processed": total_items_processed,
                "total_items_succeeded": total_items_succeeded,
                "total_items_failed": total_items_processed - total_items_succeeded,
                "workflow_efficiency": total_items_succeeded / total_items_processed
                if total_items_processed > 0
                else 0,
                "average_stage_time": total_processing_time / len(stage_results)
                if stage_results
                else 0,
                "workflow_throughput": total_items_processed / total_time
                if total_time > 0
                else 0,
                "parallel_utilization": total_processing_time / total_time
                if total_time > 0
                else 0,
            }

        def _analyze_items(
            self,
            item: ProcessingDict,
            _context: CompleteWorkflowExample.WorkflowContext,
        ) -> r[WorkflowData]:
            """Analyze single item."""
            content_payload: WorkflowContent = {
                **self._process_stage(
                    item,
                    0.005,
                    "analyzed",
                    True,
                    lambda _i: {"complexity_score": len(str(item)) * 0.1},
                )
            }
            workflow_data = WorkflowData.model_validate({"content": content_payload})
            return r.ok(workflow_data)

        def _cleanup_context(
            self, context: CompleteWorkflowExample.WorkflowContext
        ) -> None:
            """Cleanup workflow context and log completion."""
            total_time = time.time() - context.start_time
            context.performance_metrics["total_workflow_time"] = total_time
            print(f"Workflow {context.workflow_id} completed in {total_time:.3f}s")

        def _execute_stage_parallel(
            self,
            stage_name: str,
            items: Sequence[ProcessingDict],
            stage_func: Callable[
                [ProcessingDict, CompleteWorkflowExample.WorkflowContext],
                r[WorkflowData],
            ],
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> r[CompleteWorkflowExample.WorkflowStageResult]:
            """Execute a workflow stage in parallel."""
            stage_start = time.time()
            max_workers_raw = context.metadata.get("max_workers", 4)
            max_workers = (
                int(max_workers_raw)
                if isinstance(max_workers_raw, (bool, int, float, str))
                else 4
            )

            def process_single_item(item: ProcessingDict) -> ProcessingDict | None:
                try:
                    result = stage_func(item, context)
                    workflow_data = result.map_or(None)
                    return (
                        {**workflow_data.content}
                        if isinstance(workflow_data, WorkflowData)
                        else workflow_data
                    )
                except Exception as e:
                    err: ProcessingDict = {"error": str(e), "item": str(item)}
                    return err

            processed_results: MutableSequence[ProcessingDict] = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_item = {
                    executor.submit(process_single_item, item): item for item in items
                }
                for future in as_completed(future_to_item):
                    result = future.result()
                    if result is not None:
                        processed_results.append(result)
            processing_time = time.time() - stage_start
            stage_result = CompleteWorkflowExample.WorkflowStageResult(
                stage_name=stage_name,
                workflow_id=context.workflow_id,
                correlation_id=context.correlation_id,
                success=len(processed_results) > 0,
                items_processed=len(items),
                items_succeeded=len(processed_results),
                items_failed=len(items) - len(processed_results),
                processing_time=processing_time,
                stage_metadata={
                    "parallel_execution": True,
                    "max_workers": max_workers,
                    "throughput": len(items) / processing_time
                    if processing_time > 0
                    else 0,
                    "success_rate": len(processed_results) / len(items) if items else 0,
                },
            )
            return r[CompleteWorkflowExample.WorkflowStageResult].ok(stage_result)

        def _execute_workflow(
            self,
            data: Sequence[ProcessingDict],
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> r[WorkflowData]:
            """Execute workflow stages with parallel processing."""
            items = data
            stage_results: MutableSequence[
                CompleteWorkflowExample.WorkflowStageResult
            ] = []
            current_data = items
            stage_functions = {
                "validation": self._validate_items,
                "processing": self._process_items,
                "analysis": self._analyze_items,
                "aggregation": self._aggregate_results,
            }
            for stage_name in context.stages:
                stage_func = stage_functions.get(stage_name)
                if not stage_func:
                    return r[WorkflowData].fail(f"Unknown stage: {stage_name}")
                result = self._execute_stage_parallel(
                    stage_name, current_data, stage_func, context
                )
                if result.is_failure:
                    return r[WorkflowData].fail(
                        f"Stage {stage_name} failed: {result.error}"
                    )
                stage_result = result.value
                stage_results.append(stage_result)
                context.performance_metrics[stage_name] = {
                    "processing_time": stage_result.processing_time,
                    "success_rate": stage_result.items_succeeded
                    / stage_result.items_processed
                    if stage_result.items_processed > 0
                    else 0,
                    "throughput": stage_result.items_processed
                    / stage_result.processing_time
                    if stage_result.processing_time > 0
                    else 0,
                }
                current_data = current_data[: stage_result.items_succeeded]
            total_time = time.time() - context.start_time
            aggregated_metrics = self._aggregate_workflow_metrics(
                stage_results, total_time
            )
            aggregated_metrics_payload: MutableMapping[
                str, Decimal | bool | bytes | float | int | str
            ] = {}
            for key, value in aggregated_metrics.items():
                aggregated_metrics_payload[key] = value

            workflow_result = (
                CompleteWorkflowExample.CompleteWorkflowResult.model_validate({
                    "workflow_id": context.workflow_id,
                    "correlation_id": context.correlation_id,
                    "total_stages": len(context.stages),
                    "completed_stages": len(stage_results),
                    "failed_stages": 0,
                    "total_processing_time": total_time,
                    "stage_results": stage_results,
                    "aggregated_metrics": aggregated_metrics_payload,
                    "workflow_status": "completed",
                })
            )
            perf_summary_raw: MutableMapping[str, WorkflowScalar] = {}
            for key, value in aggregated_metrics.items():
                perf_summary_raw[key] = value
            summary: ProcessingDict = {
                "workflow_id": workflow_result.workflow_id,
                "workflow_status": workflow_result.workflow_status,
                "total_stages": workflow_result.total_stages,
                "completed_stages": workflow_result.completed_stages,
                "total_processing_time": workflow_result.total_processing_time,
                "performance_summary": perf_summary_raw,
            }
            summary_content: WorkflowContent = {**summary}
            workflow_data = WorkflowData.model_validate({"content": summary_content})
            return r.ok(workflow_data)

        def _process_items(
            self,
            item: ProcessingDict,
            _context: CompleteWorkflowExample.WorkflowContext,
        ) -> r[WorkflowData]:
            """Process single item."""
            content_payload: WorkflowContent = {
                **self._process_stage(
                    item,
                    0.01,
                    "processed",
                    True,
                    lambda _i: {"processed_at": time.time()},
                )
            }
            workflow_data = WorkflowData.model_validate({"content": content_payload})
            return r.ok(workflow_data)

        def _process_stage(
            self,
            item: ProcessingDict,
            sleep_time: float,
            add_field: str,
            value: str | float | bool,
            extra_logic: Callable[[ProcessingDict], Mapping[str, WorkflowScalar]]
            | None = None,
        ) -> ProcessingDict:
            """Generic stage processing helper."""
            time.sleep(sleep_time)
            result: MutableMapping[
                str,
                WorkflowScalar | t.StrSequence | Mapping[str, WorkflowScalar],
            ] = {**item}
            result[add_field] = value
            if extra_logic:
                result.update(extra_logic(item))
            return result

        def _setup_context(self) -> CompleteWorkflowExample.WorkflowContext:
            """Setup workflow context with correlation tracking."""
            workflow_id = str(
                self.workflow_config.get("workflow_id", f"workflow_{int(time.time())}")
            )
            correlation_id = f"{workflow_id}_{int(time.time() * 1000)}"
            return CompleteWorkflowExample.WorkflowContext(
                workflow_id=workflow_id,
                correlation_id=correlation_id,
                start_time=time.time(),
                metadata={
                    "parallel_enabled": bool(
                        self.workflow_config.get("parallel", True)
                    ),
                    "max_workers": int(str(self.workflow_config.get("max_workers", 4))),
                    "strict_mode": bool(self.workflow_config.get("strict_mode", False)),
                },
            )

        def _validate_items(
            self,
            item: ProcessingDict,
            _context: CompleteWorkflowExample.WorkflowContext,
        ) -> r[WorkflowData]:
            """Validate single item."""
            content_payload: WorkflowContent = {
                **self._process_stage(
                    item,
                    0.005,
                    "validated",
                    True,
                    lambda _i: {"is_valid": bool(item.get("id") and item.get("name"))},
                )
            }
            workflow_data = WorkflowData.model_validate({"content": content_payload})
            return r.ok(workflow_data)

    @staticmethod
    def create_sample_workflow_data(count: int = 100) -> Sequence[ProcessingDict]:
        """Create sample data for workflow testing."""
        result: MutableSequence[ProcessingDict] = []
        for i in range(count):
            attrs: MutableMapping[str, WorkflowScalar] = {
                "objectClass": "person,organizationalPerson",
                "cn": f"user{i}",
                "sn": f"User{i}",
            }
            item: ProcessingDict = {
                "id": f"item_{i}",
                "dn": f"cn=user{i},ou=users,dc=example,dc=com",
                "name": f"User {i}",
                "attributes": attrs,
                "timestamp": time.time() + i,
            }
            result.append(item)
        return result

    @staticmethod
    def run_example() -> None:
        """Run the complete workflow example."""
        sample_data: Sequence[ProcessingDict] = (
            CompleteWorkflowExample.create_sample_workflow_data(50)
        )
        workflow_config: Mapping[str, t.Scalar | float] = {
            "workflow_id": "comprehensive_workflow",
            "parallel": True,
            "max_workers": 4,
            "strict_mode": False,
        }
        orchestrator = CompleteWorkflowExample.WorkflowOrchestrator()
        orchestrator.data = sample_data
        orchestrator.workflow_config = workflow_config
        result = orchestrator.execute()
        if result.is_success:
            print("Workflow completed successfully")
        else:
            print(f"Workflow failed: {result.error}")
