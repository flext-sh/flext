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
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import StrEnum

from flext import FlextResult, FlextService

ItemDict = dict[str, str | int | float | bool]


class AdvancedProcessingExample:
    """Advanced processing example demonstrating FLEXT parallel capabilities."""

    class Stage(StrEnum):
        """Processing stage enumeration."""

        VALIDATE = "validate"
        PROCESS = "process"
        ANALYZE = "analyze"

    @dataclass
    class ProcessingResult:
        """Result of processing operation with metrics."""

        operation_id: str
        items_processed: int
        items_succeeded: int
        items_failed: int
        processing_time: float
        errors: list[str] = field(default_factory=list)
        metadata: dict[str, str | int | float | bool] = field(default_factory=dict)

    @dataclass
    class ValidationResult:
        """Result of validation operation."""

        item_id: str
        is_valid: bool
        violations: list[str] = field(default_factory=list)
        warnings: list[str] = field(default_factory=list)
        validation_time: float = 0.0

    class ProcessingPipeline(
        FlextService[
            dict[
                str,
                list[ItemDict]
                | list["AdvancedProcessingExample.ValidationResult"]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ]
        ],
    ):
        """Declarative processing pipeline with automatic parallel execution."""

        auto_execute = True

        items: list[ItemDict]
        stages: list[str]

        def execute(
            self,
        ) -> FlextResult[
            dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ]
        ]:
            """Execute processing pipeline using declarative stages."""
            stage_functions: dict[
                str,
                Callable[
                    [
                        dict[
                            str,
                            list[ItemDict]
                            | list[AdvancedProcessingExample.ValidationResult]
                            | int
                            | float
                            | dict[
                                str,
                                int
                                | float
                                | dict[int, int]
                                | list[float]
                                | dict[str, int | float],
                            ],
                        ],
                    ],
                    FlextResult[
                        dict[
                            str,
                            list[ItemDict]
                            | list[AdvancedProcessingExample.ValidationResult]
                            | int
                            | float
                            | dict[
                                str,
                                int
                                | float
                                | dict[int, int]
                                | list[float]
                                | dict[str, int | float],
                            ],
                        ]
                    ],
                ],
            ] = {
                "validate": self._validate_batch,
                "process": self._process_parallel,
                "analyze": self._analyze_results,
            }

            operations: list[
                Callable[
                    [
                        dict[
                            str,
                            list[ItemDict]
                            | list[AdvancedProcessingExample.ValidationResult]
                            | int
                            | float
                            | dict[
                                str,
                                int
                                | float
                                | dict[int, int]
                                | list[float]
                                | dict[str, int | float],
                            ],
                        ],
                    ],
                    FlextResult[
                        dict[
                            str,
                            list[ItemDict]
                            | list[AdvancedProcessingExample.ValidationResult]
                            | int
                            | float
                            | dict[
                                str,
                                int
                                | float
                                | dict[int, int]
                                | list[float]
                                | dict[str, int | float],
                            ],
                        ]
                    ],
                ]
            ] = []
            for stage in self.stages:
                stage_func = stage_functions.get(stage)
                if stage_func:
                    operations.append(stage_func)
                else:
                    return FlextResult.fail(f"Unknown stage: {stage}")

            current_data: dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ] = {"items": self.items}

            for operation in operations:
                result = operation(current_data)
                if result.is_failure:
                    return result
                unwrapped = result.value
                if isinstance(unwrapped, dict):
                    current_data = unwrapped

            return FlextResult.ok(current_data)

        def _validate_batch(
            self,
            data: dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ],
        ) -> FlextResult[
            dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ]
        ]:
            """Validate batch of items."""
            items_data = data.get("items", [])
            if not isinstance(items_data, list):
                return FlextResult.fail("Invalid items data")

            validation_results: list[AdvancedProcessingExample.ValidationResult] = []
            items_to_validate: list[ItemDict] = [
                item
                for item in items_data
                if isinstance(item, dict)
                and not isinstance(item, AdvancedProcessingExample.ValidationResult)
            ]

            for item in items_to_validate:
                result = self._validate_single_item(item)
                if result.is_success:
                    validation_results.append(result.value)
                else:
                    return FlextResult.fail(f"Validation failed: {result.error}")

            result_data: dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ] = {
                **data,
                "validation_results": validation_results,
                "valid_count": sum(1 for r in validation_results if r.is_valid),
                "invalid_count": sum(1 for r in validation_results if not r.is_valid),
            }
            return FlextResult.ok(result_data)

        def _process_parallel(
            self,
            data: dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ],
        ) -> FlextResult[
            dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ]
        ]:
            """Process items in parallel."""
            items_data = data.get("items", [])
            if not isinstance(items_data, list):
                return FlextResult.fail("Invalid items data")

            start_time = time.time()

            def process_single_item(item: ItemDict) -> ItemDict | None:
                """Process a single item."""
                try:
                    time.sleep(0.01)
                    result = item.copy()
                    result["processed"] = True
                    result["processing_timestamp"] = time.time()
                    return result
                except Exception:
                    return None

            processed_items: list[ItemDict] = []
            items_to_process: list[ItemDict] = [
                item
                for item in items_data
                if isinstance(item, dict)
                and not isinstance(item, AdvancedProcessingExample.ValidationResult)
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

            result_data: dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ] = {
                **data,
                "processed_items": processed_items,
                "processing_time": processing_time,
                "success_rate": len(processed_items) / len(items_data)
                if items_data
                else 0,
            }
            return FlextResult.ok(result_data)

        def _analyze_results(
            self,
            data: dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ],
        ) -> FlextResult[
            dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ]
        ]:
            """Analyze processing results."""
            processed_items_data = data.get("processed_items", [])
            processed_items = (
                processed_items_data if isinstance(processed_items_data, list) else []
            )

            validation_results_data = data.get("validation_results", [])
            validation_results = (
                validation_results_data
                if isinstance(validation_results_data, list)
                else []
            )

            field_counts: dict[int, int] = {}
            complexity_scores: list[float] = []
            items_to_analyze: list[ItemDict] = [
                item
                for item in processed_items
                if isinstance(item, dict)
                and not isinstance(item, AdvancedProcessingExample.ValidationResult)
            ]

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

            validation_summary: dict[str, int | float] = {
                "total_validated": len(validation_results),
                "valid_items": sum(
                    1
                    for r in validation_results
                    if isinstance(r, AdvancedProcessingExample.ValidationResult)
                    and r.is_valid
                ),
                "total_violations": sum(
                    len(r.violations)
                    for r in validation_results
                    if isinstance(r, AdvancedProcessingExample.ValidationResult)
                ),
                "total_warnings": sum(
                    len(r.warnings)
                    for r in validation_results
                    if isinstance(r, AdvancedProcessingExample.ValidationResult)
                ),
            }
            analysis: dict[
                str,
                int | float | dict[int, int] | list[float] | dict[str, int | float],
            ] = {
                "total_processed": len(items_to_analyze),
                "field_distribution": field_counts,
                "avg_complexity": sum(complexity_scores) / len(complexity_scores)
                if complexity_scores
                else 0,
                "validation_summary": validation_summary,
                "processing_efficiency": processing_efficiency * 100,
            }

            result_data: dict[
                str,
                list[ItemDict]
                | list[AdvancedProcessingExample.ValidationResult]
                | int
                | float
                | dict[
                    str,
                    int | float | dict[int, int] | list[float] | dict[str, int | float],
                ],
            ] = {
                **data,
                "analysis": analysis,
            }
            return FlextResult.ok(result_data)

        def _validate_single_item(
            self, item: ItemDict,
        ) -> FlextResult[AdvancedProcessingExample.ValidationResult]:
            """Validate a single item."""
            start_time = time.time()
            violations: list[str] = []
            warnings: list[str] = []

            item_id = item.get("id")
            if not item_id or not isinstance(item_id, str):
                violations.append("Missing or invalid id field")

            name = item.get("name")
            if not name or not isinstance(name, str):
                violations.append("Missing or invalid name field")

            value = item.get("value", "")
            if isinstance(value, str) and len(value) > 100:
                warnings.append("Value field is very long")

            return FlextResult.ok(
                AdvancedProcessingExample.ValidationResult(
                    item_id=str(item_id) if item_id else "unknown",
                    is_valid=len(violations) == 0,
                    violations=violations,
                    warnings=warnings,
                    validation_time=time.time() - start_time,
                ),
            )

    @staticmethod
    def create_sample_items(count: int = 100) -> list[ItemDict]:
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


# Example usage (commented out - no main blocks or print statements as per requirements)
# sample_items = AdvancedProcessingExample.create_sample_items(100)
# result = AdvancedProcessingExample.ProcessingPipeline(sample_items, ["validate", "process", "analyze"])
# Result is dict directly - pipeline executed automatically!
