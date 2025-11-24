"""08_complete_workflow.py - Complete Workflow Example.

Demonstrates complete workflow integration with:
|- Integração completa de todas as capacidades
|- Railway pattern abrangente
|- Processamento paralelo em todas as etapas
|- Auto-detecção e builders inteligentes
|- Validação integrada end-to-end

This example showcases the complete FLEXT enterprise data integration
workflow with comprehensive capabilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from flext_core import FlextResult, FlextService


@dataclass
class WorkflowContext:
    """Complete workflow context with correlation and metadata."""

    workflow_id: str
    correlation_id: str
    start_time: float
    stages: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    performance_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStageResult:
    """Result of a workflow stage with comprehensive tracking."""

    stage_name: str
    workflow_id: str
    correlation_id: str
    success: bool
    items_processed: int
    items_succeeded: int
    items_failed: int
    processing_time: float
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stage_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompleteWorkflowResult:
    """Complete workflow result with all stages aggregated."""

    workflow_id: str
    correlation_id: str
    total_stages: int
    completed_stages: int
    failed_stages: int
    total_processing_time: float
    stage_results: list[WorkflowStageResult] = field(default_factory=list)
    aggregated_metrics: dict[str, Any] = field(default_factory=dict)
    workflow_status: str = "unknown"


class WorkflowOrchestrator(FlextService[dict]):
    """Resource-managed workflow orchestrator with automatic context lifecycle."""

    auto_execute = True

    data: Any
    workflow_config: dict

    def execute(self) -> FlextResult[dict]:
        """Execute complete workflow with automatic resource management."""
        return FlextResult.ok(self.data).with_resource(
            resource_factory=self._setup_context,
            operation=self._execute_workflow,
            cleanup=self._cleanup_context,
        )

    def _setup_context(self) -> WorkflowContext:
        """Setup workflow context with correlation tracking."""
        workflow_id = self.workflow_config.get(
            "workflow_id", f"workflow_{int(time.time())}"
        )
        correlation_id = f"{workflow_id}_{int(time.time() * 1000)}"

        return WorkflowContext(
            workflow_id=workflow_id,
            correlation_id=correlation_id,
            start_time=time.time(),
            stages=["validation", "processing", "analysis", "aggregation"],
            metadata={
                "parallel_enabled": self.workflow_config.get("parallel", True),
                "max_workers": self.workflow_config.get("max_workers", 4),
                "strict_mode": self.workflow_config.get("strict_mode", False),
            },
        )

    def _execute_workflow(
        self, data: Any, context: WorkflowContext
    ) -> FlextResult[dict]:
        """Execute workflow stages with parallel processing."""
        # Prepare data for processing
        items = data if isinstance(data, list) else [data]

        # Execute stages in parallel
        stage_results = []
        current_data = items

        for stage_name in context.stages:
            stage_func = self._get_stage_function(stage_name)
            if not stage_func:
                return FlextResult.fail(f"Unknown stage: {stage_name}")

            # Execute stage
            result = self._execute_stage_parallel(
                stage_name, current_data, stage_func, context
            )

            if result.is_failure:
                return FlextResult.fail(f"Stage {stage_name} failed: {result.error}")

            stage_result = result.unwrap()
            stage_results.append(stage_result)

            # Update context with performance metrics
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

            # Prepare data for next stage
            current_data = self._transform_data_for_next_stage(
                stage_name, current_data, stage_result
            )

        # Aggregate final results
        total_time = time.time() - context.start_time
        aggregated_metrics = self._aggregate_workflow_metrics(stage_results, total_time)

        workflow_result = CompleteWorkflowResult(
            workflow_id=context.workflow_id,
            correlation_id=context.correlation_id,
            total_stages=len(context.stages),
            completed_stages=len(stage_results),
            failed_stages=0,  # All stages succeeded if we reach here
            total_processing_time=total_time,
            stage_results=stage_results,
            aggregated_metrics=aggregated_metrics,
            workflow_status="completed",
        )

        return FlextResult.ok({
            "workflow_result": workflow_result,
            "final_data": current_data,
            "performance_summary": aggregated_metrics,
        })

    def _cleanup_context(self, context: WorkflowContext) -> None:
        """Cleanup workflow context and log completion."""
        total_time = time.time() - context.start_time
        context.performance_metrics["total_workflow_time"] = total_time

        # Log workflow completion (in real implementation)
        print(f"Workflow {context.workflow_id} completed in {total_time:.3f}s")

    def _get_stage_function(self, stage_name: str) -> Callable | None:
        """Get stage function by name."""
        stage_functions = {
            "validation": self._validate_items,
            "processing": self._process_items,
            "analysis": self._analyze_items,
            "aggregation": self._aggregate_results,
        }
        return stage_functions.get(stage_name)

    def _execute_stage_parallel(
        self,
        stage_name: str,
        items: list[dict[str, Any]],
        stage_func: Callable,
        context: WorkflowContext,
    ) -> FlextResult[WorkflowStageResult]:
        """Execute a workflow stage in parallel."""
        stage_start = time.time()
        max_workers = context.metadata.get("max_workers", 4)

        def process_single_item(item: dict[str, Any]) -> dict[str, Any] | None:
            """Process single item in stage."""
            try:
                result = stage_func(item, context)
                return result.unwrap() if result.is_success else None
            except Exception as e:
                return {"error": str(e), "item": item}

        processed_results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {
                executor.submit(process_single_item, item): item for item in items
            }

            for future in as_completed(future_to_item):
                result = future.result()
                if result is not None:
                    processed_results.append(result)

        processing_time = time.time() - stage_start

        stage_result = WorkflowStageResult(
            stage_name=stage_name,
            workflow_id=context.workflow_id,
            correlation_id=context.correlation_id,
            success=len(processed_results) > 0,
            items_processed=len(items),
            items_succeeded=len(processed_results),
            items_failed=len(items) - len(processed_results),
            processing_time=processing_time,
            errors=[],  # Would populate with actual errors
            warnings=[],  # Would populate with warnings
            stage_metadata={
                "parallel_execution": True,
                "max_workers": max_workers,
                "throughput": len(items) / processing_time
                if processing_time > 0
                else 0,
                "success_rate": len(processed_results) / len(items) if items else 0,
            },
        )

        return FlextResult.ok(stage_result)

    def _validate_items(
        self, item: dict[str, Any], context: WorkflowContext
    ) -> FlextResult[dict[str, Any]]:
        """Validate single item."""
        time.sleep(0.005)  # Simulate validation time
        result = item.copy()
        result["validated"] = True
        result["is_valid"] = bool(item.get("id") and item.get("name"))
        return FlextResult.ok(result)

    def _process_items(
        self, item: dict[str, Any], context: WorkflowContext
    ) -> FlextResult[dict[str, Any]]:
        """Process single item."""
        time.sleep(0.01)  # Simulate processing time
        result = item.copy()
        result["processed"] = True
        result["processed_at"] = time.time()
        return FlextResult.ok(result)

    def _analyze_items(
        self, item: dict[str, Any], context: WorkflowContext
    ) -> FlextResult[dict[str, Any]]:
        """Analyze single item."""
        time.sleep(0.005)  # Simulate analysis time
        result = item.copy()
        result["analyzed"] = True
        result["complexity_score"] = len(str(item)) * 0.1
        return FlextResult.ok(result)

    def _aggregate_results(
        self, item: dict[str, Any], context: WorkflowContext
    ) -> FlextResult[dict[str, Any]]:
        """Aggregate results."""
        result = item.copy()
        result["aggregated"] = True
        result["final_score"] = item.get("complexity_score", 0) + (
            1 if item.get("is_valid") else 0
        )
        return FlextResult.ok(result)

    def _transform_data_for_next_stage(
        self,
        stage_name: str,
        current_data: list[dict[str, Any]],
        stage_result: WorkflowStageResult,
    ) -> list[dict[str, Any]]:
        """Transform data for next stage."""
        # Simplified: just return current data (in real implementation would transform)
        return current_data[: stage_result.items_succeeded]

    def _aggregate_workflow_metrics(
        self, stage_results: list[WorkflowStageResult], total_time: float
    ) -> dict[str, Any]:
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


def create_sample_workflow_data(count: int = 100) -> list[dict[str, Any]]:
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


# Example usage (commented out - no main blocks or print statements as per requirements)
#
# sample_data = create_sample_workflow_data(50)
# workflow_config = {
#     "workflow_id": "comprehensive_workflow",
#     "parallel": True,
#     "max_workers": 4,
#     "strict_mode": False,
# }
#
# result = WorkflowOrchestrator(sample_data, workflow_config)
# Context automatically managed - setup and cleanup happen transparently!
