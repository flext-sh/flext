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
    MutableSequence,
    Sequence,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import StrEnum, unique
from typing import Annotated, ClassVar

from examples import m, p, r, t, u


class CompleteWorkflowExample:
    """Complete workflow example demonstrating FLEXT enterprise data integration capabilities."""

    type ProcessingDict = t.JsonMapping
    type WorkflowContent = t.JsonMapping

    class WorkflowData(m.BaseModel):
        """Data container for workflow processing."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
            extra="allow",
        )
        content: t.JsonMapping = u.Field(default_factory=dict)

    @unique
    class Stage(StrEnum):
        """Processing stage enumeration."""

        VALIDATION = "validation"
        PROCESSING = "processing"
        ANALYSIS = "analysis"
        AGGREGATION = "aggregation"

    class WorkflowContext(m.BaseModel):
        """Complete workflow context with correlation and metadata."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True
        )

        workflow_id: str = u.Field(description="Unique workflow identifier")
        correlation_id: str = u.Field(description="Correlation ID for tracking")
        start_time: float = u.Field(description="Workflow start timestamp")
        stages: t.StrSequence = u.Field(
            default_factory=lambda: [
                "validation",
                "processing",
                "analysis",
                "aggregation",
            ],
            description="List of workflow stages to execute",
        )
        metadata: t.JsonMapping = u.Field(
            default_factory=dict,
            description="Workflow metadata key-value pairs",
        )
        performance_metrics: t.MutableJsonMapping = u.Field(
            default_factory=dict,
            description="Performance metrics collected during workflow execution",
        )

    class WorkflowStageResult(m.BaseModel):
        """Result of a workflow stage with comprehensive tracking."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True
        )

        stage_name: str = u.Field(description="Name of the workflow stage")
        workflow_id: str = u.Field(description="Associated workflow ID")
        correlation_id: str = u.Field(description="Correlation ID for tracking")
        success: bool = u.Field(description="Whether the stage succeeded")
        items_processed: int = u.Field(description="Total items processed in stage")
        items_succeeded: int = u.Field(description="Items that succeeded")
        items_failed: int = u.Field(description="Items that failed")
        processing_time: float = u.Field(description="Time taken to process stage")
        errors: t.StrSequence = u.Field(
            default_factory=list,
            description="List of errors encountered",
        )
        warnings: t.StrSequence = u.Field(
            default_factory=list,
            description="List of warnings encountered",
        )
        stage_metadata: t.JsonMapping = u.Field(
            default_factory=dict,
            description="Stage-specific metadata",
        )

    class CompleteWorkflowResult(m.BaseModel):
        """Complete workflow result with all stages aggregated."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True
        )

        workflow_id: str = u.Field(description="Unique workflow identifier")
        correlation_id: str = u.Field(description="Correlation ID for tracking")
        total_stages: int = u.Field(description="Total number of stages")
        completed_stages: int = u.Field(description="Number of completed stages")
        failed_stages: int = u.Field(description="Number of failed stages")
        total_processing_time: float = u.Field(
            description="Total workflow processing time",
        )
        stage_results: Sequence[CompleteWorkflowExample.WorkflowStageResult] = u.Field(
            default_factory=list,
            description="Results from each workflow stage",
        )
        aggregated_metrics: t.JsonMapping = u.Field(
            default_factory=dict,
            description="Aggregated metrics across all stages",
        )
        workflow_status: Annotated[
            str,
            u.Field(
                description="Overall workflow status",
            ),
        ] = "unknown"

    class WorkflowOrchestrator(m.BaseModel):
        """Resource-managed workflow orchestrator with automatic context lifecycle."""

        auto_execute: bool = True
        data: Sequence[CompleteWorkflowExample.ProcessingDict] = u.Field(
            default_factory=tuple,
        )
        workflow_settings: t.ScalarMapping = u.Field(
            default_factory=dict,
        )

        def execute(self) -> p.Result[CompleteWorkflowExample.WorkflowData]:
            """Execute complete workflow with automatic resource management."""
            context = self._setup_context()
            try:
                return self._execute_workflow(self.data, context)
            finally:
                self._cleanup_context(context)

        def _aggregate_results(
            self,
            item: CompleteWorkflowExample.ProcessingDict,
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> p.Result[CompleteWorkflowExample.WorkflowData]:
            """Aggregate results."""
            complexity_score_raw = item.get("complexity_score", 0)
            complexity_score = (
                float(complexity_score_raw)
                if isinstance(complexity_score_raw, (int, float))
                else 0.0
            )
            final_score = complexity_score + (
                1 if bool(item.get("valid", False)) else 0
            )
            content_payload: CompleteWorkflowExample.WorkflowContent = {
                **self._process_stage(
                    item,
                    0,
                    "aggregated",
                    True,
                    lambda _i: {"final_score": final_score},
                    context=context,
                ),
            }
            workflow_data = CompleteWorkflowExample.WorkflowData.model_validate(
                {"content": content_payload},
            )
            return r.ok(workflow_data)

        def _aggregate_workflow_metrics(
            self,
            stage_results: Sequence[CompleteWorkflowExample.WorkflowStageResult],
            total_time: float,
        ) -> Mapping[str, t.Numeric]:
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
            item: CompleteWorkflowExample.ProcessingDict,
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> p.Result[CompleteWorkflowExample.WorkflowData]:
            """Analyze single item."""
            content_payload: CompleteWorkflowExample.WorkflowContent = {
                **self._process_stage(
                    item,
                    0.005,
                    "analyzed",
                    True,
                    lambda _i: {"complexity_score": len(str(item)) * 0.1},
                    context=context,
                ),
            }
            workflow_data = CompleteWorkflowExample.WorkflowData.model_validate(
                {"content": content_payload},
            )
            return r.ok(workflow_data)

        def _cleanup_context(
            self,
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> None:
            """Cleanup workflow context and log completion."""
            total_time = time.time() - context.start_time
            context.performance_metrics["total_workflow_time"] = total_time
            print(f"Workflow {context.workflow_id} completed in {total_time:.3f}s")

        def _execute_stage_parallel(
            self,
            stage_name: str,
            items: Sequence[CompleteWorkflowExample.ProcessingDict],
            stage_func: Callable[
                [
                    CompleteWorkflowExample.ProcessingDict,
                    CompleteWorkflowExample.WorkflowContext,
                ],
                p.Result[CompleteWorkflowExample.WorkflowData],
            ],
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> p.Result[CompleteWorkflowExample.WorkflowStageResult]:
            """Execute a workflow stage in parallel."""
            stage_start = time.time()
            max_workers_raw = context.metadata.get("max_workers", 4)
            max_workers = (
                int(max_workers_raw)
                if isinstance(max_workers_raw, (bool, int, float, str))
                else 4
            )

            def process_single_item(
                item: CompleteWorkflowExample.ProcessingDict,
            ) -> CompleteWorkflowExample.ProcessingDict | None:
                try:
                    result = stage_func(item, context)
                    workflow_data = result.map_or(None)
                    return (
                        {**workflow_data.content}
                        if isinstance(
                            workflow_data, CompleteWorkflowExample.WorkflowData
                        )
                        else workflow_data
                    )
                except Exception as e:
                    err: CompleteWorkflowExample.ProcessingDict = {
                        "error": str(e),
                        "item": str(item),
                    }
                    return err

            processed_results: MutableSequence[
                CompleteWorkflowExample.ProcessingDict
            ] = []
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
            data: Sequence[CompleteWorkflowExample.ProcessingDict],
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> p.Result[CompleteWorkflowExample.WorkflowData]:
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
                    return r[CompleteWorkflowExample.WorkflowData].fail(
                        f"Unknown stage: {stage_name}",
                    )
                result = self._execute_stage_parallel(
                    stage_name,
                    current_data,
                    stage_func,
                    context,
                )
                if result.failure:
                    return r[CompleteWorkflowExample.WorkflowData].fail(
                        f"Stage {stage_name} failed: {result.error}",
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
                stage_results,
                total_time,
            )
            aggregated_metrics_payload: t.MutableJsonMapping = {}
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
            perf_summary_raw: t.MutableJsonMapping = {}
            for key, value in aggregated_metrics.items():
                perf_summary_raw[key] = value
            summary: CompleteWorkflowExample.ProcessingDict = (
                t.json_mapping_adapter().validate_python({
                    "workflow_id": workflow_result.workflow_id,
                    "workflow_status": workflow_result.workflow_status,
                    "total_stages": workflow_result.total_stages,
                    "completed_stages": workflow_result.completed_stages,
                    "total_processing_time": workflow_result.total_processing_time,
                    "performance_summary": perf_summary_raw,
                })
            )
            summary_content: CompleteWorkflowExample.WorkflowContent = {**summary}
            workflow_data = CompleteWorkflowExample.WorkflowData.model_validate(
                {"content": summary_content},
            )
            return r.ok(workflow_data)

        def _process_items(
            self,
            item: CompleteWorkflowExample.ProcessingDict,
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> p.Result[CompleteWorkflowExample.WorkflowData]:
            """Process single item."""
            content_payload: CompleteWorkflowExample.WorkflowContent = {
                **self._process_stage(
                    item,
                    0.01,
                    "processed",
                    True,
                    lambda _i: {"processed_at": time.time()},
                    context=context,
                ),
            }
            workflow_data = CompleteWorkflowExample.WorkflowData.model_validate(
                {"content": content_payload},
            )
            return r.ok(workflow_data)

        def _process_stage(
            self,
            item: CompleteWorkflowExample.ProcessingDict,
            sleep_time: float,
            add_field: str,
            value: t.Primitives,
            extra_logic: Callable[
                [CompleteWorkflowExample.ProcessingDict],
                t.JsonMapping,
            ]
            | None = None,
            context: CompleteWorkflowExample.WorkflowContext | None = None,
        ) -> CompleteWorkflowExample.ProcessingDict:
            """Generic stage processing helper."""
            time.sleep(sleep_time)
            result: t.MutableJsonMapping = {
                **item,
            }
            result[add_field] = value
            if context is not None:
                result["workflow_context"] = {
                    "workflow_id": context.workflow_id,
                    "correlation_id": context.correlation_id,
                }
            if extra_logic:
                result.update(extra_logic(item))
            return result

        def _setup_context(self) -> CompleteWorkflowExample.WorkflowContext:
            """Setup workflow context with correlation tracking."""
            workflow_id = str(
                self.workflow_settings.get(
                    "workflow_id", f"workflow_{int(time.time())}"
                ),
            )
            correlation_id = f"{workflow_id}_{int(time.time() * 1000)}"
            return CompleteWorkflowExample.WorkflowContext(
                workflow_id=workflow_id,
                correlation_id=correlation_id,
                start_time=time.time(),
                metadata={
                    "parallel_enabled": bool(
                        self.workflow_settings.get("parallel", True),
                    ),
                    "max_workers": int(
                        str(self.workflow_settings.get("max_workers", 4))
                    ),
                    "strict_mode": bool(
                        self.workflow_settings.get("strict_mode", False)
                    ),
                },
            )

        def _validate_items(
            self,
            item: CompleteWorkflowExample.ProcessingDict,
            context: CompleteWorkflowExample.WorkflowContext,
        ) -> p.Result[CompleteWorkflowExample.WorkflowData]:
            """Validate single item."""
            content_payload: CompleteWorkflowExample.WorkflowContent = {
                **self._process_stage(
                    item,
                    0.005,
                    "validated",
                    True,
                    lambda _i: {"valid": bool(item.get("id") and item.get("name"))},
                    context=context,
                ),
            }
            workflow_data = CompleteWorkflowExample.WorkflowData.model_validate(
                {"content": content_payload},
            )
            return r.ok(workflow_data)

    @staticmethod
    def create_sample_workflow_data(
        count: int = 100,
    ) -> Sequence[CompleteWorkflowExample.ProcessingDict]:
        """Create sample data for workflow testing."""
        result: MutableSequence[CompleteWorkflowExample.ProcessingDict] = []
        for i in range(count):
            attrs: t.MutableJsonMapping = {
                "objectClass": "person,organizationalPerson",
                "cn": f"user{i}",
                "sn": f"User{i}",
            }
            item: CompleteWorkflowExample.ProcessingDict = (
                t.json_mapping_adapter().validate_python({
                    "id": f"item_{i}",
                    "dn": f"cn=user{i},ou=users,dc=example,dc=com",
                    "name": f"User {i}",
                    "attributes": attrs,
                    "timestamp": time.time() + i,
                })
            )
            result.append(item)
        return result

    @staticmethod
    def run_example() -> None:
        """Run the complete workflow example."""
        sample_data: Sequence[CompleteWorkflowExample.ProcessingDict] = (
            CompleteWorkflowExample.create_sample_workflow_data(50)
        )
        workflow_settings: t.ScalarMapping = {
            "workflow_id": "comprehensive_workflow",
            "parallel": True,
            "max_workers": 4,
            "strict_mode": False,
        }
        orchestrator = CompleteWorkflowExample.WorkflowOrchestrator()
        orchestrator.data = sample_data
        orchestrator.workflow_settings = workflow_settings
        result = orchestrator.execute()
        if result.success:
            print("Workflow completed successfully")
        else:
            print(f"Workflow failed: {result.error}")
