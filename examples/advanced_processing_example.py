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
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Annotated, ClassVar

from examples import ExamplesStage, m, p, r, t, u

type DataValue = t.JsonValue
type ItemDict = t.JsonMapping
type StageOperation = Callable[[t.JsonMapping], r[PipelineStageData]]

MAX_VALUE_LENGTH = 100


def _new_data_value_map() -> t.JsonMapping:
    return {}


def _json_mapping_or_none(value: t.JsonValue) -> t.JsonMapping | None:
    if not isinstance(value, Mapping):
        return None
    return dict(value.items())


def _json_mapping_sequence(value: t.JsonValue) -> t.SequenceOf[t.JsonMapping]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    mappings: MutableSequence[t.JsonMapping] = []
    for item in value:
        mapping_item = _json_mapping_or_none(item)
        if mapping_item is not None:
            mappings.append(mapping_item)
    return tuple(mappings)


def _string_sequence(value: t.JsonValue) -> t.StrSequence:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    strings: MutableSequence[str] = []
    for item in value:
        if isinstance(item, str):
            strings.append(item)
    return tuple(strings)


class PipelineStageData(m.BaseModel):
    """Data container for pipeline stage processing."""

    model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
        arbitrary_types_allowed=True, extra="allow"
    )

    class PipelinePayload(m.BaseModel):
        """Pipeline payload container."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True, extra="allow"
        )

        values: t.JsonMapping = u.Field(default_factory=_new_data_value_map)

    data: PipelinePayload = u.Field(
        default_factory=lambda: PipelineStageData.PipelinePayload(values={})
    )


def _new_scalar_dict() -> t.MutableJsonMapping:
    return {}


class AdvancedProcessingExample:
    """Advanced processing example demonstrating FLEXT parallel capabilities."""

    Stage = ExamplesStage

    class ProcessingResult(m.BaseModel):
        """Result of processing operation with metrics."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True
        )

        operation_id: str = u.Field(description="Unique operation identifier")
        items_processed: int = u.Field(description="Total items processed")
        items_succeeded: int = u.Field(description="Items that succeeded")
        items_failed: int = u.Field(description="Items that failed")
        processing_time: float = u.Field(description="Time taken for processing")
        errors: t.StrSequence = u.Field(
            default_factory=tuple, description="List of errors encountered"
        )
        metadata: t.JsonMapping = u.Field(
            default_factory=_new_scalar_dict, description="Operation metadata"
        )

    class ValidationResult(m.BaseModel):
        """Result of validation operation."""

        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True
        )

        item_id: str = u.Field(description="Unique item identifier")
        valid: bool = u.Field(description="Whether the item is valid")
        violations: t.StrSequence = u.Field(
            default_factory=tuple, description="List of validation violations"
        )
        warnings: t.StrSequence = u.Field(
            default_factory=tuple, description="List of validation warnings"
        )
        validation_time: Annotated[
            float, u.Field(description="Time taken for validation")
        ] = 0.0

    class FlextLdifProcessingPipeline(m.BaseModel):
        """Declarative processing pipeline with automatic parallel execution."""

        auto_execute: bool = True
        items: t.SequenceOf[ItemDict]
        stages: t.StrSequence

        def execute(self) -> p.Result[PipelineStageData]:
            """Execute processing pipeline using declarative stages."""
            stage_functions: t.MappingKV[
                str, Callable[[t.JsonMapping], p.Result[PipelineStageData]]
            ] = {
                "validate": self._validate_batch,
                "process": self._process_parallel,
                "analyze": self._analyze_results,
            }
            operations: MutableSequence[
                Callable[[t.JsonMapping], p.Result[PipelineStageData]]
            ] = []
            for stage in self.stages:
                stage_func = stage_functions.get(stage)
                if stage_func:
                    operations.append(stage_func)
                else:
                    return r[PipelineStageData].fail(f"Unknown stage: {stage}")
            current_data: t.JsonMapping = t.json_mapping_adapter().validate_python({
                "items": self.items
            })
            for operation in operations:
                result = operation(current_data)
                if result.failure:
                    return result
                current_data = result.value.data.values
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": current_data
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _analyze_results(self, data: t.JsonMapping) -> p.Result[PipelineStageData]:
            """Analyze processing results."""
            processed_items = _json_mapping_sequence(data.get("processed_items", []))
            validation_results = _json_mapping_sequence(
                data.get("validation_results", [])
            )
            field_counts: MutableMapping[int, int] = {}
            complexity_scores: MutableSequence[float] = []
            items_to_analyze: t.SequenceOf[ItemDict] = processed_items
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
            validation_summary = {
                "total_validated": len(validation_results),
                "valid_items": sum(
                    1
                    for result_item in validation_results
                    if result_item.get("valid") is True
                ),
                "total_violations": sum(
                    len(_string_sequence(result_item.get("violations")))
                    for result_item in validation_results
                ),
                "total_warnings": sum(
                    len(_string_sequence(result_item.get("warnings")))
                    for result_item in validation_results
                ),
            }
            field_distribution: t.JsonMapping = {
                str(key): value for key, value in field_counts.items()
            }
            analysis: t.JsonMapping = t.json_mapping_adapter().validate_python({
                "total_processed": len(items_to_analyze),
                "field_distribution": field_distribution,
                "avg_complexity": sum(complexity_scores) / len(complexity_scores)
                if complexity_scores
                else 0,
                "validation_summary": validation_summary,
                "processing_efficiency": processing_efficiency * 100,
            })
            result_data: t.JsonMapping = t.json_mapping_adapter().validate_python({
                **data,
                "analysis": analysis,
            })
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": result_data
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _process_parallel(self, data: t.JsonMapping) -> p.Result[PipelineStageData]:
            """Process items in parallel."""
            items_to_process = _json_mapping_sequence(data.get("items", []))
            if not items_to_process:
                return r[PipelineStageData].fail("Invalid items data")
            start_time = time.time()

            def process_single_item(item: ItemDict) -> ItemDict:
                """Process a single item."""
                time.sleep(0.01)
                result: t.MutableJsonMapping = {**item}
                result["processed"] = True
                result["processing_timestamp"] = time.time()
                return result

            processed_items: MutableSequence[ItemDict] = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_item = {
                    executor.submit(process_single_item, item): item
                    for item in items_to_process
                }
                for future in as_completed(future_to_item):
                    processed_items.append(future.result())
            processing_time = time.time() - start_time
            result_data: t.JsonMapping = t.json_mapping_adapter().validate_python({
                **data,
                "processed_items": processed_items,
                "processing_time": processing_time,
                "success_rate": len(processed_items) / len(items_to_process)
                if items_to_process
                else 0,
            })
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": result_data
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _validate_batch(self, data: t.JsonMapping) -> p.Result[PipelineStageData]:
            """Validate batch of items."""
            items_to_validate = _json_mapping_sequence(data.get("items", []))
            if not items_to_validate:
                return r[PipelineStageData].fail("Invalid items data")
            validation_results: MutableSequence[
                AdvancedProcessingExample.ValidationResult
            ] = []
            for item in items_to_validate:
                result = self._validate_single_item(item)
                if result.success:
                    validation_results.append(result.value)
                else:
                    return r[PipelineStageData].fail(
                        f"Validation failed: {result.error}"
                    )
            result_data: t.JsonMapping = t.json_mapping_adapter().validate_python({
                **data,
                "validation_results": [
                    {
                        "item_id": validation.item_id,
                        "valid": validation.valid,
                        "violations": tuple(validation.violations),
                        "warnings": tuple(validation.warnings),
                        "validation_time": validation.validation_time,
                    }
                    for validation in validation_results
                ],
                "valid_count": sum(1 for r in validation_results if r.valid),
                "invalid_count": sum(1 for r in validation_results if not r.valid),
            })
            payload = PipelineStageData.PipelinePayload.model_validate({
                "values": result_data
            })
            return r[PipelineStageData].ok(PipelineStageData(data=payload))

        def _validate_single_item(
            self, item: ItemDict
        ) -> p.Result[AdvancedProcessingExample.ValidationResult]:
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
            if isinstance(value, str) and len(value) > MAX_VALUE_LENGTH:
                warnings.append("Value field is very long")
            return r[AdvancedProcessingExample.ValidationResult].ok(
                AdvancedProcessingExample.ValidationResult(
                    item_id=str(item_id) if item_id else "unknown",
                    valid=not violations,
                    violations=tuple(violations),
                    warnings=tuple(warnings),
                    validation_time=time.time() - start_time,
                )
            )

    @staticmethod
    def create_sample_items(count: int = 100) -> t.SequenceOf[ItemDict]:
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
