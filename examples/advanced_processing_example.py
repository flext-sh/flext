"""AdvancedProcessingExample - Advanced FLEXT Processing Example.

This module provides an advanced example demonstrating FLEXT's parallel processing
and pipeline capabilities for enterprise data integration. It showcases batch
processing, parallel validation, and comprehensive analysis with performance metrics.

Scope: Demonstration of advanced processing patterns including ThreadPoolExecutor
usage, pipeline execution, and result aggregation with modern FLEXT APIs.

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
from decimal import Decimal
from enum import StrEnum, unique
from typing import ClassVar

from flext_core import r, t
from pydantic import BaseModel, ConfigDict, Field

type DataPrimitive = str | int | float | bool | bytes | Decimal
type DataValue = DataPrimitive | Sequence[DataValue] | Mapping[str, DataValue]

ItemDict = Mapping[str, DataValue]
StageOperation = Callable[[Mapping[str, DataValue]], r["PipelineStageData"]]


def _new_data_value_map() -> Mapping[str, DataValue]:
    return {}


class PipelineStageData(BaseModel):
    """Data container for pipeline stage processing."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
    )

    class PipelinePayload(BaseModel):
        """Pipeline payload container."""

        model_config: ClassVar[ConfigDict] = ConfigDict(
            arbitrary_types_allowed=True,
            extra="allow",
        )

        values: Mapping[str, DataValue] = Field(default_factory=_new_data_value_map)

    data: PipelinePayload = Field(
        default_factory=lambda: PipelineStageData.PipelinePayload(values={}),
    )


def _new_str_list() -> MutableSequence[str]:
    return []


def _new_scalar_dict() -> MutableMapping[str, DataPrimitive]:
    return {}


class AdvancedProcessingExample:
    """Advanced processing example demonstrating FLEXT parallel capabilities."""

    @unique
    class Stage(StrEnum):
        """Processing stage enumeration."""

        VALIDATE = "validate"
        PROCESS = "process"
        ANALYZE = "analyze"

    class ProcessingResult(BaseModel):
        """Result of processing operation with metrics."""

        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

        operation_id: str = Field(description="Unique operation identifier")
        items_processed: int = Field(description="Total items processed")
        items_succeeded: int = Field(description="Items that succeeded")
        items_failed: int = Field(description="Items that failed")
        processing_time: float = Field(description="Time taken for processing")
        errors: t.StrSequence = Field(
            default_factory=_new_str_list,
            description="List of errors encountered",
        )
        metadata: Mapping[str, DataPrimitive] = Field(
            default_factory=_new_scalar_dict,
            description="Operation metadata",
        )

    class ValidationResult(BaseModel):
        """Result of validation operation."""

        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

        item_id: str = Field(description="Unique item identifier")
        is_valid: bool = Field(description="Whether the item is valid")
        violations: t.StrSequence = Field(
            default_factory=_new_str_list,
            description="List of validation violations",
        )
        warnings: t.StrSequence = Field(
            default_factory=_new_str_list,
            description="List of validation warnings",
        )
        validation_time: float = Field(
            default=0.0,
            description="Time taken for validation",
        )

    class FlextLdifProcessingPipeline(BaseModel):
        """Declarative processing pipeline with automatic parallel execution."""

        auto_execute: bool = True
        items: Sequence[ItemDict]
        stages: t.StrSequence

        def execute(self) -> r[PipelineStageData]:
            """Execute processing pipeline using declarative stages."""
            stage_functions: Mapping[
                str,
                Callable[[Mapping[str, DataValue]], r[PipelineStageData]],
            ] = {
                "validate": self._validate_batch,
                "process": self._process_parallel,
                "analyze": self._analyze_results,
            }
            operations: MutableSequence[
                Callable[[Mapping[str, DataValue]], r[PipelineStageData]]
            ] = []
            for stage in self.stages:
                stage_func = stage_functions.get(stage)
                if stage_func:
                    operations.append(stage_func)
                else:
                    return r[PipelineStageData].fail(f"Unknown stage: {stage}")
            current_data: Mapping[str, DataValue] = {"items": self.items}
            for operation in operations:
                result = operation(current_data)
                if result.is_failure:
                    return result
                current_data = result.value.data.values
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": current_data,
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _analyze_results(
            self,
            data: Mapping[str, DataValue],
        ) -> r[PipelineStageData]:
            """Analyze processing results."""
            processed_items_data = data.get("processed_items", [])
            processed_items: MutableSequence[ItemDict] = (
                [{**item} for item in processed_items_data if isinstance(item, Mapping)]
                if isinstance(processed_items_data, Sequence)
                and not isinstance(processed_items_data, (str, bytes, bytearray))
                else []
            )
            validation_results_data = data.get("validation_results", [])
            validation_results: MutableSequence[Mapping[str, DataValue]] = (
                [item for item in validation_results_data if isinstance(item, Mapping)]
                if isinstance(validation_results_data, Sequence)
                and not isinstance(validation_results_data, (str, bytes, bytearray))
                else []
            )
            field_counts: MutableMapping[int, int] = {}
            complexity_scores: MutableSequence[float] = []
            items_to_analyze: Sequence[ItemDict] = processed_items
            for item in items_to_analyze:
                field_count = len(item)
                field_counts[field_count] = field_counts.get(field_count, 0) + 1
                complexity_scores.append(field_count * 0.1)
            success_rate_data = data.get("success_rate", 0)
            processing_efficiency = (
                float(success_rate_data)
                if isinstance(success_rate_data, (int, float))
                else 0.0
            )
            validation_summary: Mapping[str, int | float] = {
                "total_validated": len(validation_results),
                "valid_items": sum(
                    1 for r in validation_results if r.get("is_valid") is True
                ),
                "total_violations": sum(
                    len(violations)
                    for r in validation_results
                    for violations in [r.get("violations")]
                    if isinstance(violations, Sequence)
                ),
                "total_warnings": sum(
                    len(warnings)
                    for r in validation_results
                    for warnings in [r.get("warnings")]
                    if isinstance(warnings, Sequence)
                ),
            }
            field_distribution: Mapping[str, DataValue] = {
                str(key): value for key, value in field_counts.items()
            }
            analysis: Mapping[str, DataValue] = {
                "total_processed": len(items_to_analyze),
                "field_distribution": field_distribution,
                "avg_complexity": sum(complexity_scores) / len(complexity_scores)
                if complexity_scores
                else 0,
                "validation_summary": validation_summary,
                "processing_efficiency": processing_efficiency * 100,
            }
            result_data: Mapping[str, DataValue] = {
                **data,
                "analysis": analysis,
            }
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": result_data,
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _process_parallel(
            self,
            data: Mapping[str, DataValue],
        ) -> r[PipelineStageData]:
            """Process items in parallel."""
            items_data = data.get("items", [])
            if not isinstance(items_data, Sequence) or isinstance(
                items_data,
                (str, bytes, bytearray),
            ):
                return r[PipelineStageData].fail("Invalid items data")
            start_time = time.time()

            def process_single_item(item: ItemDict) -> ItemDict | None:
                """Process a single item."""
                try:
                    time.sleep(0.01)
                    result: MutableMapping[str, DataValue] = {**item}
                    result["processed"] = True
                    result["processing_timestamp"] = time.time()
                    return result
                except Exception:
                    return None

            processed_items: MutableSequence[ItemDict] = []
            items_to_process: Sequence[ItemDict] = [
                {**item}
                for item in items_data
                if isinstance(item, Mapping)
                and (not isinstance(item, AdvancedProcessingExample.ValidationResult))
            ]
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_item = {
                    executor.submit(process_single_item, item): item
                    for item in items_to_process
                }
                for future in as_completed(future_to_item):
                    result = future.result()
                    if result is not None:
                        processed_items.append(result)
            processing_time = time.time() - start_time
            result_data: Mapping[str, DataValue] = {
                **data,
                "processed_items": processed_items,
                "processing_time": processing_time,
                "success_rate": len(processed_items) / len(items_data)
                if items_data
                else 0,
            }
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": result_data,
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _validate_batch(
            self,
            data: Mapping[str, DataValue],
        ) -> r[PipelineStageData]:
            """Validate batch of items."""
            items_data = data.get("items", [])
            if not isinstance(items_data, Sequence) or isinstance(
                items_data,
                (str, bytes, bytearray),
            ):
                return r[PipelineStageData].fail("Invalid items data")
            validation_results: MutableSequence[
                AdvancedProcessingExample.ValidationResult
            ] = []
            items_to_validate: Sequence[ItemDict] = [
                {**item}
                for item in items_data
                if isinstance(item, Mapping)
                and (not isinstance(item, AdvancedProcessingExample.ValidationResult))
            ]
            for item in items_to_validate:
                result = self._validate_single_item(item)
                if result.is_success:
                    validation_results.append(result.value)
                else:
                    return r[PipelineStageData].fail(
                        f"Validation failed: {result.error}",
                    )
            result_data: Mapping[str, DataValue] = {
                **data,
                "validation_results": [
                    {
                        "item_id": validation.item_id,
                        "is_valid": validation.is_valid,
                        "violations": tuple(validation.violations),
                        "warnings": tuple(validation.warnings),
                        "validation_time": validation.validation_time,
                    }
                    for validation in validation_results
                ],
                "valid_count": sum(1 for r in validation_results if r.is_valid),
                "invalid_count": sum(1 for r in validation_results if not r.is_valid),
            }
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": result_data,
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _validate_single_item(
            self,
            item: ItemDict,
        ) -> r[AdvancedProcessingExample.ValidationResult]:
            """Validate a single item."""
            start_time = time.time()
            violations: MutableSequence[str] = []
            warnings: MutableSequence[str] = []
            item_id = item.get("id")
            if not item_id or not isinstance(item_id, str):
                violations.append("Missing or invalid id field")
            name = item.get("name")
            if not name or not isinstance(name, str):
                violations.append("Missing or invalid name field")
            value = item.get("value", "")
            if isinstance(value, str) and len(value) > 100:
                warnings.append("Value field is very long")
            return r[AdvancedProcessingExample.ValidationResult].ok(
                AdvancedProcessingExample.ValidationResult(
                    item_id=str(item_id) if item_id else "unknown",
                    is_valid=not violations,
                    violations=violations,
                    warnings=warnings,
                    validation_time=time.time() - start_time,
                ),
            )

    @staticmethod
    def create_sample_items(count: int = 100) -> Sequence[ItemDict]:
        """Create sample items for testing."""
        return [
            {
                "id": f"item_{i}",
                "name": f"Sample Item {i}",
                "value": f"Data value {i}" * (i % 10 + 1),
                "category": f"category_{i % 5}",
                "timestamp": time.time() + i,
            }
            for i in range(count)
        ]
