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
from collections.abc import Callable, MutableMapping, MutableSequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Annotated, ClassVar

from examples import FlextRootExamplesConstants, m, p, t, u
from flext_core import r


class FlextRootAdvancedProcessingExample:
    """Advanced processing example demonstrating FLEXT parallel capabilities."""

    class _Constants:
        """Internal constants for advanced processing example."""

        MAX_VALUE_LENGTH: int = 100

    class ValidationResult(m.BaseModel):
        """Result of validation operation."""

        model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
            arbitrary_types_allowed=True,
        )

        item_id: str = u.Field(description="Unique item identifier")
        valid: bool = u.Field(description="Whether the item is valid")
        violations: t.StrSequence = u.Field(
            default_factory=tuple,
            description="List of validation violations",
        )
        warnings: t.StrSequence = u.Field(
            default_factory=tuple,
            description="List of validation warnings",
        )
        validation_time: Annotated[
            float,
            u.Field(description="Time taken for validation"),
        ] = 0.0

    class FlextLdifProcessingPipeline(m.BaseModel):
        """Declarative processing pipeline with automatic parallel execution."""

        auto_execute: bool = True
        items: t.SequenceOf[t.JsonMapping]
        stages: t.StrSequence
        max_workers: int = 4

        def execute(
            self,
        ) -> p.Result[t.JsonMapping]:
            """Execute processing pipeline using declarative stages.

            Returns:
                The resulting ``p.Result[t.JsonMapping]``.

            """
            stage_functions: t.MappingKV[
                str,
                Callable[
                    [t.JsonMapping],
                    p.Result[t.JsonMapping],
                ],
            ] = {
                "validate": self._validate_batch,
                "process": self._process_parallel,
                "analyze": self._analyze_results,
            }
            operations: MutableSequence[
                Callable[
                    [t.JsonMapping],
                    p.Result[t.JsonMapping],
                ]
            ] = []
            for stage in self.stages:
                stage_func = stage_functions.get(stage)
                if stage_func:
                    operations.append(stage_func)
                else:
                    return r[t.JsonMapping].fail(
                        f"Unknown stage: {stage}",
                    )
            current_data: t.JsonMapping = t.json_mapping_adapter().validate_python(
                self.model_dump(mode="json", include={"items"}),
            )
            for operation in operations:
                result = operation(current_data)
                if result.failure:
                    return result
                stage_data = FlextRootExamplesConstants.JsonMappingOrNoneHelper.extract(
                    result.value.get("data"),
                )
                if stage_data is None:
                    return r[t.JsonMapping].fail(
                        "Stage returned no data mapping",
                    )
                stage_values = (
                    FlextRootExamplesConstants.JsonMappingOrNoneHelper.extract(
                        stage_data.get("values"),
                    )
                )
                if stage_values is None:
                    return r[t.JsonMapping].fail(
                        "Stage returned no values mapping",
                    )
                current_data = stage_values
            result_data: t.JsonMapping = t.json_mapping_adapter().validate_python({
                "data": {"values": current_data},
            })
            return r[t.JsonMapping].ok(result_data)

        @staticmethod
        def _analyze_results(
            data: t.JsonMapping,
        ) -> p.Result[t.JsonMapping]:
            """Analyze processing results.

            Returns:
                The resulting ``p.Result[t.JsonMapping]``.

            """
            processed_items = (
                FlextRootExamplesConstants.JsonMappingSequenceHelper.extract(
                    data.get("processed_items", []),
                )
            )
            validation_results = (
                FlextRootExamplesConstants.JsonMappingSequenceHelper.extract(
                    data.get("validation_results", []),
                )
            )
            field_counts: MutableMapping[int, int] = {}
            complexity_scores: MutableSequence[float] = []
            items_to_analyze: t.SequenceOf[t.JsonMapping] = processed_items
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
                    len(
                        FlextRootExamplesConstants.StringSequenceHelper.extract(
                            result_item.get("violations"),
                        ),
                    )
                    for result_item in validation_results
                ),
                "total_warnings": sum(
                    len(
                        FlextRootExamplesConstants.StringSequenceHelper.extract(
                            result_item.get("warnings"),
                        ),
                    )
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
            return r[t.JsonMapping].ok(
                t.json_mapping_adapter().validate_python({
                    "data": {"values": result_data},
                }),
            )

        def _process_parallel(
            self,
            data: t.JsonMapping,
        ) -> p.Result[t.JsonMapping]:
            """Process items in parallel.

            Returns:
                The resulting ``p.Result[t.JsonMapping]``.

            """
            items_to_process = (
                FlextRootExamplesConstants.JsonMappingSequenceHelper.extract(
                    data.get("items", []),
                )
            )
            if not items_to_process:
                return r[t.JsonMapping].fail(
                    "Invalid items data",
                )
            start_time = time.time()

            def process_single_item(item: t.JsonMapping) -> t.JsonMapping:
                """Process a single item.

                Returns:
                    The resulting ``t.JsonMapping``.

                """
                result: t.MutableJsonMapping = {**item}
                result["processed"] = True
                result["processing_timestamp"] = time.time()
                return result

            processed_items: MutableSequence[t.JsonMapping] = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
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
            return r[t.JsonMapping].ok(
                t.json_mapping_adapter().validate_python({
                    "data": {"values": result_data},
                }),
            )

        def _validate_batch(
            self,
            data: t.JsonMapping,
        ) -> p.Result[t.JsonMapping]:
            """Validate batch of items.

            Returns:
                The resulting ``p.Result[t.JsonMapping]``.

            """
            items_to_validate = (
                FlextRootExamplesConstants.JsonMappingSequenceHelper.extract(
                    data.get("items", []),
                )
            )
            if not items_to_validate:
                return r[t.JsonMapping].fail(
                    "Invalid items data",
                )
            validation_results: MutableSequence[
                FlextRootAdvancedProcessingExample.ValidationResult
            ] = []
            for item in items_to_validate:
                result = self._validate_single_item(item)
                if result.success:
                    validation_results.append(result.value)
                else:
                    return r[t.JsonMapping].fail(
                        f"Validation failed: {result.error}",
                    )
            result_data: t.JsonMapping = t.json_mapping_adapter().validate_python({
                **data,
                "validation_results": [
                    validation.model_dump(mode="json")
                    for validation in validation_results
                ],
                "valid_count": sum(1 for r in validation_results if r.valid),
                "invalid_count": sum(1 for r in validation_results if not r.valid),
            })
            return r[t.JsonMapping].ok(
                t.json_mapping_adapter().validate_python({
                    "data": {"values": result_data},
                }),
            )

        @staticmethod
        def _validate_single_item(
            item: t.JsonMapping,
        ) -> p.Result[FlextRootAdvancedProcessingExample.ValidationResult]:
            """Validate a single item.

            Returns:
                The resulting
                    ``p.Result[FlextRootAdvancedProcessingExample.ValidationResult]``.

            """
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
            if (
                isinstance(value, str)
                and len(value)
                > FlextRootAdvancedProcessingExample._Constants.MAX_VALUE_LENGTH
            ):
                warnings.append("Value field is very long")
            return r[FlextRootAdvancedProcessingExample.ValidationResult].ok(
                FlextRootAdvancedProcessingExample.ValidationResult(
                    item_id=str(item_id) if item_id else "unknown",
                    valid=not violations,
                    violations=tuple(violations),
                    warnings=tuple(warnings),
                    validation_time=time.time() - start_time,
                ),
            )

    @staticmethod
    def create_sample_items(count: int = 100) -> t.SequenceOf[t.JsonMapping]:
        """Create sample items for testing.

        Returns:
            The resulting ``t.SequenceOf[t.JsonMapping]``.

        """
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
