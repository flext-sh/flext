"""07_advanced_processing.py - Advanced Processing Example.

Demonstrates advanced processing capabilities with:
|- Corrected APIs (currently deprecated ones updated)
|- Parallel processing with ThreadPoolExecutor
|- Batch processing for heavy operations
|- Integrated processing pipeline
|- Parallel validation and analysis

This example showcases enterprise-grade data processing following
FLEXT architecture patterns with modern APIs.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from flext_core import FlextResult, FlextService


@dataclass
class ProcessingResult:
    """Result of processing operation with metrics."""

    operation_id: str
    items_processed: int
    items_succeeded: int
    items_failed: int
    processing_time: float
    errors: list[str]
    metadata: dict[str, Any]


@dataclass
class ValidationResult:
    """Result of validation operation."""

    item_id: str
    is_valid: bool
    violations: list[str]
    warnings: list[str]
    validation_time: float


class ProcessingPipeline(FlextService[dict]):
    """Declarative processing pipeline with automatic parallel execution."""

    auto_execute = True

    items: list[dict]
    stages: list[str]

    def execute(self) -> FlextResult[dict]:
        """Execute processing pipeline using declarative stages."""
        # Map stage names to functions
        stage_functions = {
            "validate": self._validate_batch,
            "process": self._process_parallel,
            "analyze": self._analyze_results,
        }

        # Build pipeline from requested stages
        operations = []
        for stage in self.stages:
            if stage in stage_functions:
                operations.append(stage_functions[stage])
            else:
                return FlextResult.fail(f"Unknown stage: {stage}")

        # Execute pipeline
        return FlextResult.pipeline(self.items, *operations)

    def _validate_batch(
        self, items: list[dict[str, Any]]
    ) -> FlextResult[dict[str, Any]]:
        """Validate batch of items."""
        validation_results = []

        for item in items:
            result = self._validate_single_item(item)
            if result.is_success:
                validation_results.append(result.unwrap())
            else:
                return FlextResult.fail(f"Validation failed: {result.error}")

        return FlextResult.ok({
            "items": items,
            "validation_results": validation_results,
            "valid_count": sum(1 for r in validation_results if r.is_valid),
            "invalid_count": sum(1 for r in validation_results if not r.is_valid),
        })

    def _process_parallel(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Process items in parallel."""
        items = data["items"]
        start_time = time.time()

        def process_single_item(item: dict[str, Any]) -> dict[str, Any] | None:
            """Process a single item."""
            try:
                # Simulate processing
                time.sleep(0.01)
                return {**item, "processed": True, "processing_timestamp": time.time()}
            except Exception:
                return None

        processed_items = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_item = {
                executor.submit(process_single_item, item): item for item in items
            }

            for future in as_completed(future_to_item):
                result = future.result()
                if result is not None:
                    processed_items.append(result)

        processing_time = time.time() - start_time

        return FlextResult.ok({
            **data,
            "processed_items": processed_items,
            "processing_time": processing_time,
            "success_rate": len(processed_items) / len(items) if items else 0,
        })

    def _analyze_results(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Analyze processing results."""
        processed_items = data.get("processed_items", [])
        validation_results = data.get("validation_results", [])

        # Aggregate analysis
        total_items = len(processed_items)
        field_counts = {}
        complexity_scores = []

        for item in processed_items:
            # Count fields
            field_count = len(item)
            field_counts[field_count] = field_counts.get(field_count, 0) + 1

            # Calculate complexity score
            complexity_scores.append(field_count * 0.1)

        analysis = {
            "total_processed": total_items,
            "field_distribution": field_counts,
            "avg_complexity": sum(complexity_scores) / len(complexity_scores)
            if complexity_scores
            else 0,
            "validation_summary": {
                "total_validated": len(validation_results),
                "valid_items": sum(1 for r in validation_results if r.is_valid),
                "total_violations": sum(len(r.violations) for r in validation_results),
                "total_warnings": sum(len(r.warnings) for r in validation_results),
            },
            "processing_efficiency": data.get("success_rate", 0) * 100,
        }

        return FlextResult.ok({
            **data,
            "analysis": analysis,
        })

    def _validate_single_item(
        self, item: dict[str, Any]
    ) -> FlextResult[ValidationResult]:
        """Validate a single item."""
        start_time = time.time()
        violations = []
        warnings = []

        if not item.get("id"):
            violations.append("Missing id field")
        if not item.get("name"):
            violations.append("Missing name field")
        if len(str(item.get("value", ""))) > 100:
            warnings.append("Value field is very long")

        result = ValidationResult(
            item_id=str(item.get("id", "unknown")),
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            validation_time=time.time() - start_time,
        )

        return FlextResult.ok(result)


def create_sample_items(count: int = 100) -> list[dict[str, Any]]:
    """Create sample items for testing."""
    return [
        {
            "id": f"item_{i}",
            "name": f"Sample Item {i}",
            "value": f"Data value {i}" * (i % 10 + 1),  # Variable length
            "category": f"category_{i % 5}",
            "timestamp": time.time() + i,
        }
        for i in range(count)
    ]


# Example usage (commented out - no main blocks or print statements as per requirements)
#
# sample_items = create_sample_items(100)
# result = ProcessingPipeline(sample_items, ["validate", "process", "analyze"])
# Result is dict directly - pipeline executed automatically!
