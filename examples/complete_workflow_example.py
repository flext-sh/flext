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
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import StrEnum
from typing import override

from flext_core import FlextService, r, t
from pydantic import BaseModel, ConfigDict, Field

ItemType = dict[str, object]


def _new_str_list() -> list[str]:
    return []


def _new_scalar_dict() -> dict[str, t.Scalar]:
    return {}


def _new_stage_metadata_dict() -> dict[str, float | int | bool]:
    return {}


def _new_performance_metrics_dict() -> dict[str, float | int | dict[str, float | int]]:
    return {}


def _new_stage_result_list() -> list[CompleteWorkflowExample.WorkflowStageResult]:
    return []


def _new_aggregated_metrics_dict() -> dict[str, float | int]:
    return {}


def _to_float(value: object) -> float:
    """Coerce object to float; return 0.0 for non-numeric."""
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


class CompleteWorkflowExample:
    """Complete workflow example demonstrating FLEXT enterprise data integration capabilities."""

    class Stage(StrEnum):
        """Workflow stages enumeration."""

        VALIDATION = "validation"
        PROCESSING = "processing"
        ANALYSIS = "analysis"
        AGGREGATION = "aggregation"

    class WorkflowContext(BaseModel):
        """Complete workflow context with correlation and metadata."""

        model_config = ConfigDict(arbitrary_types_allowed=True)

        workflow_id: str = Field(description="Unique workflow identifier")
        correlation_id: str = Field(description="Correlation ID for tracking")
        start_time: float = Field(description="Workflow start timestamp")
        stages: list[str] = Field(
            default_factory=lambda: [
                "validation",
                "processing",
                "analysis",
                "aggregation",
            ],
            description="List of workflow stages to execute",
        )
        metadata: dict[str, t.Scalar] = Field(
            default_factory=_new_scalar_dict,
            description="Workflow metadata key-value pairs",
        )
        performance_metrics: dict[str, float | int | dict[str, float | int]] = Field(
            default_factory=_new_performance_metrics_dict,
            description="Performance metrics collected during workflow execution",
        )

    class WorkflowStageResult(BaseModel):
        """Result of a workflow stage with comprehensive tracking."""

        model_config = ConfigDict(arbitrary_types_allowed=True)

        stage_name: str = Field(description="Name of the workflow stage")
        workflow_id: str = Field(description="Associated workflow ID")
        correlation_id: str = Field(description="Correlation ID for tracking")
        success: bool = Field(description="Whether the stage succeeded")
        items_processed: int = Field(description="Total items processed in stage")
        items_succeeded: int = Field(description="Items that succeeded")
        items_failed: int = Field(description="Items that failed")
        processing_time: float = Field(description="Time taken to process stage")
        errors: list[str] = Field(
            default_factory=_new_str_list,
            description="List of errors encountered",
        )
        warnings: list[str] = Field(
            default_factory=_new_str_list,
            description="List of warnings encountered",
        )
        stage_metadata: dict[str, float | int | bool] = Field(
            default_factory=_new_stage_metadata_dict,
            description="Stage-specific metadata",
        )

    class CompleteWorkflowResult(BaseModel):
        """Complete workflow result with all stages aggregated."""

        model_config = ConfigDict(arbitrary_types_allowed=True)

        workflow_id: str = Field(description="Unique workflow identifier")
        correlation_id: str = Field(description="Correlation ID for tracking")
        total_stages: int = Field(description="Total number of stages")
        completed_stages: int = Field(description="Number of completed stages")
        failed_stages: int = Field(description="Number of failed stages")
        total_processing_time: float = Field(
            description="Total workflow processing time"
        )
        stage_results: list[CompleteWorkflowExample.WorkflowStageResult] = Field(
            default_factory=_new_stage_result_list,
            description="Results from each workflow stage",
        )
        aggregated_metrics: dict[str, float | int] = Field(
            default_factory=_new_aggregated_metrics_dict,
            description="Aggregated metrics across all stages",
        )
        workflow_status: str = Field(
            default="unknown",
            description="Overall workflow status",
        )

    class WorkflowOrchestrator(FlextService[dict[str, object]]):
        """Resource-managed workflow orchestrator with automatic context lifecycle."""

        auto_execute: bool = True
        data: list[ItemType]
        workflow_config: dict[str, str | int | bool | float]

        def __init__(self) -> None:
            """Initialize the workflow orchestrator."""
            super().__init__()
            self.data = []
            self.workflow_config = {}

        @override
        def execute(self) -> r[dict[str, object]]:
            """Execute complete workflow with automatic resource management."""
            context = self._setup_context()
            try:
                return self._execute_workflow(self.data, context)
            finally:
                self._cleanup_context(context)

        def _aggregate_results(
            self, item: ItemType, _context: CompleteWorkflowExample.WorkflowContext
        ) -> r[ItemType]:
            """Aggregate results."""
            return r[ItemType].ok(
                self._process_stage(
                    item,
                    0,
                    "aggregated",
                    True,
                    lambda _i: {
                        "final_score": _to_float(item.get("complexity_score", 0))
                        + (1 if bool(item.get("is_valid", False)) else 0)
                    },
                )
            )

        def _aggregate_workflow_metrics(
            self,
            stage_results: list[CompleteWorkflowExample.WorkflowStageResult],
            total_time: float,
        ) -> dict[str, float | int]:
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
            self, item: ItemType, _context: CompleteWorkflowExample.WorkflowContext
        ) -> r[ItemType]:
            """Analyze single item."""
            return r[ItemType].ok(
                self._process_stage(
                    item,
                    0.005,
                    "analyzed",
                    True,
                    lambda _i: {"complexity_score": len(str(item)) * 0.1},
                )
            )

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
            items: list[ItemType],
            stage_func: Callable[
                [ItemType, CompleteWorkflowExample.WorkflowContext], r[ItemType]
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

            def process_single_item(item: ItemType) -> ItemType | None:
                try:
                    result = stage_func(item, context)
                    return result.map_or(None)
                except Exception as e:
                    return {"error": str(e), "item": item}

            processed_results: list[ItemType] = []
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
            self, data: list[ItemType], context: CompleteWorkflowExample.WorkflowContext
        ) -> r[dict[str, object]]:
            """Execute workflow stages with parallel processing."""
            items = data
            stage_results: list[CompleteWorkflowExample.WorkflowStageResult] = []
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
                    return r[dict[str, object]].fail(f"Unknown stage: {stage_name}")
                result = self._execute_stage_parallel(
                    stage_name, current_data, stage_func, context
                )
                if result.is_failure:
                    return r[dict[str, object]].fail(
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
            workflow_result = CompleteWorkflowExample.CompleteWorkflowResult(
                workflow_id=context.workflow_id,
                correlation_id=context.correlation_id,
                total_stages=len(context.stages),
                completed_stages=len(stage_results),
                failed_stages=0,
                total_processing_time=total_time,
                stage_results=stage_results,
                aggregated_metrics=aggregated_metrics,
                workflow_status="completed",
            )
            return r[dict[str, object]].ok({
                "workflow_result": workflow_result,
                "final_data": current_data,
                "performance_summary": aggregated_metrics,
            })

        def _process_items(
            self, item: ItemType, _context: CompleteWorkflowExample.WorkflowContext
        ) -> r[ItemType]:
            """Process single item."""
            return r[ItemType].ok(
                self._process_stage(
                    item,
                    0.01,
                    "processed",
                    True,
                    lambda _i: {"processed_at": time.time()},
                )
            )

        def _process_stage(
            self,
            item: ItemType,
            sleep_time: float,
            add_field: str,
            value: str | float | bool,
            extra_logic: Callable[[ItemType], dict[str, t.Scalar]] | None = None,
        ) -> ItemType:
            """Generic stage processing helper."""
            time.sleep(sleep_time)
            result = item.copy()
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
                    "max_workers": int(self.workflow_config.get("max_workers", 4)),
                    "strict_mode": bool(self.workflow_config.get("strict_mode", False)),
                },
            )

        def _validate_items(
            self, item: ItemType, _context: CompleteWorkflowExample.WorkflowContext
        ) -> r[ItemType]:
            """Validate single item."""
            return r[ItemType].ok(
                self._process_stage(
                    item,
                    0.005,
                    "validated",
                    True,
                    lambda _i: {"is_valid": bool(item.get("id") and item.get("name"))},
                )
            )

    @staticmethod
    def create_sample_workflow_data(count: int = 100) -> list[ItemType]:
        """Create sample data for workflow testing."""
        return [
            {
                "id": f"item_{i}",
                "dn": f"cn=user{i},ou=users,dc=example,dc=com",
                "name": f"User {i}",
                "attributes": {
                    "objectClass": ["person", "organizationalPerson"],
                    "cn": f"user{i}",
                    "sn": f"User{i}",
                },
                "timestamp": time.time() + i,
            }
            for i in range(count)
        ]

    @staticmethod
    def run_example() -> None:
        """Run the complete workflow example."""
        sample_data: list[ItemType] = (
            CompleteWorkflowExample.create_sample_workflow_data(50)
        )
        workflow_config: dict[str, str | int | bool | float] = {
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
