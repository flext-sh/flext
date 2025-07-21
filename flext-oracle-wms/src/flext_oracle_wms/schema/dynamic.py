"""Oracle WMS Dynamic Schema Processing Module - Dynamic schema and entity processing.

This module provides dynamic schema discovery and entity processing capabilities
for Oracle WMS integrations as required by the user specifications.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from collections.abc import Callable

from flext_core.domain.types import ServiceResult

from flext_oracle_wms.constants import (
    OracleWMSEntityTypes,
    OracleWMSErrorMessages,
)
from flext_oracle_wms.typedefs import (
    WMSDiscoveryResult,
    WMSEntityInfo,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from flext_oracle_wms.constants import OracleWMSEntityType
    from flext_oracle_wms.typedefs import (
        WMSConnectionInfo,
        WMSRecord,
        WMSRecordBatch,
        WMSSchema,
    )


class SchemaDiscoveryResult(TypedDict):
    """Result of schema discovery operation."""

    entity_name: str
    schema: WMSSchema
    sample_records: list[WMSRecord]
    field_analysis: dict[str, dict[str, Any]]
    schema_confidence: float
    discovered_at: datetime
    discovery_metadata: dict[str, Any]


class EntityProcessingResult(TypedDict):
    """Result of entity processing operation."""

    entity_name: str
    processed_records: WMSRecordBatch
    schema_validation_results: list[dict[str, Any]]
    type_conversions: dict[str, str]
    processing_stats: dict[str, Any]
    processing_metadata: dict[str, Any]


class DynamicSchemaProcessor:
    """Dynamic schema discovery and processing for Oracle WMS entities."""

    def __init__(
        self,
        sample_size: int = 1000,
        confidence_threshold: float = 0.8,
        enable_type_inference: bool = True,
        enable_schema_validation: bool = True,
        enable_field_analysis: bool = True,
        max_schema_depth: int = 10,
    ) -> None:
        """Initialize dynamic schema processor."""
        self.sample_size = sample_size
        self.confidence_threshold = confidence_threshold
        self.enable_type_inference = enable_type_inference
        self.enable_schema_validation = enable_schema_validation
        self.enable_field_analysis = enable_field_analysis
        self.max_schema_depth = max_schema_depth

        # Type inference mappings with proper typing
        self.type_patterns: dict[str, Callable[[Any], bool]] = {
            "string": lambda x: isinstance(x, str),
            "integer": lambda x: isinstance(x, int),
            "number": lambda x: isinstance(x, (int, float)),
            "boolean": lambda x: isinstance(x, bool),
            "array": lambda x: isinstance(x, list),
            "object": lambda x: isinstance(x, dict),
            "null": lambda x: x is None,
        }

    def discover_entity_schema(
        self,
        entity_name: OracleWMSEntityType,
        sample_records: WMSRecordBatch,
        existing_schema: WMSSchema | None = None,
    ) -> ServiceResult[SchemaDiscoveryResult]:
        """Discover schema for a WMS entity dynamically."""
        try:
            # Validate entity type
            if entity_name not in OracleWMSEntityTypes.ALL_ENTITIES:
                return ServiceResult.fail(
                    f"{OracleWMSErrorMessages.INVALID_ENTITY_TYPE}: {entity_name}",
                )

            # Limit sample size
            limited_sample = sample_records[: self.sample_size]

            if not limited_sample:
                return ServiceResult.fail(
                    f"{OracleWMSErrorMessages.ENTITY_NOT_FOUND}: {entity_name} "
                    "(sample_size: 0)",
                )

            # Discover schema
            discovered_schema = self._discover_schema_from_records(limited_sample)

            # Perform field analysis
            field_analysis = {}
            if self.enable_field_analysis:
                field_analysis = self._analyze_fields(limited_sample, discovered_schema)

            # Calculate schema confidence
            schema_confidence = self._calculate_schema_confidence(
                limited_sample,
                discovered_schema,
                field_analysis,
            )

            # Merge with existing schema if provided
            if existing_schema:
                discovered_schema = self._merge_schemas(
                    existing_schema,
                    discovered_schema,
                )

            result = SchemaDiscoveryResult(
                entity_name=entity_name,
                schema=discovered_schema,
                sample_records=limited_sample[:10],  # Return small sample for reference
                field_analysis=field_analysis,
                schema_confidence=schema_confidence,
                discovered_at=datetime.now(),
                discovery_metadata={
                    "sample_size": len(limited_sample),
                    "total_fields": len(discovered_schema),
                    "schema_depth": self._calculate_schema_depth(discovered_schema),
                    "type_inference_enabled": self.enable_type_inference,
                    "confidence_threshold": self.confidence_threshold,
                },
            )

            return ServiceResult.ok(result)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.SCHEMA_GENERATION_FAILED}: {e} "
                f"(entity: {entity_name})",
            )

    def process_entity_records(
        self,
        entity_name: OracleWMSEntityType,
        records: WMSRecordBatch,
        target_schema: WMSSchema,
        validate_schema: bool = True,
        convert_types: bool = True,
    ) -> ServiceResult[EntityProcessingResult]:
        """Process entity records against a target schema."""
        try:
            processed_records = []
            validation_results = []
            type_conversions = {}
            processing_stats = {
                "total_records": len(records),
                "processed_records": 0,
                "validation_errors": 0,
                "type_conversions": 0,
                "field_additions": 0,
                "field_removals": 0,
            }

            for i, record in enumerate(records):  # Validate record against schema
                if validate_schema:
                    validation_result = self._validate_record_against_schema(
                        record,
                        target_schema,
                    )
                    validation_results.append(
                        {
                            "record_index": i,
                            "valid": validation_result["valid"],
                            "errors": validation_result["errors"],
                            "warnings": validation_result["warnings"],
                        },
                    )

                    if not validation_result["valid"]:
                        processing_stats["validation_errors"] += 1

                # Convert types if enabled
                processed_record = record.copy()
                if convert_types:
                    processed_record, conversions = self._convert_record_types(
                        processed_record,
                        target_schema,
                    )
                    type_conversions.update(conversions)
                    processing_stats["type_conversions"] += len(conversions)

                # Add missing fields with defaults
                processed_record = self._add_missing_fields(
                    processed_record,
                    target_schema,
                )

                # Remove extra fields not in schema
                processed_record = self._remove_extra_fields(
                    processed_record,
                    target_schema,
                )

                processed_records.append(processed_record)
                processing_stats["processed_records"] += 1

        except Exception as e:
            return ServiceResult.fail(f"Error in operation: {e}")

        result = EntityProcessingResult(
            entity_name=entity_name,
            processed_records=processed_records,
            schema_validation_results=validation_results,
            type_conversions=type_conversions,
            processing_stats=processing_stats,
            processing_metadata={
                "target_schema_fields": len(target_schema),
                "validation_enabled": validate_schema,
                "type_conversion_enabled": convert_types,
                "processing_timestamp": datetime.now().isoformat(),
            },
        )

        return ServiceResult.ok(result)

    def discover_all_entities(
        self,
        entity_data: dict[str, WMSRecordBatch],
        connection_info: WMSConnectionInfo,
    ) -> ServiceResult[WMSDiscoveryResult]:
        """Discover schemas for all provided entities."""
        try:
            discovered_entities = []

            for entity_name, records in entity_data.items():
                if entity_name in OracleWMSEntityTypes.ALL_ENTITIES:
                    # Cast to the proper type for the discover_entity_schema method
                    validated_entity_name: OracleWMSEntityType = entity_name  # type: ignore[assignment]
                    discovery_result = self.discover_entity_schema(
                        validated_entity_name,
                        records,
                    )

                    if not discovery_result.is_success:
                        continue

                    schema_data = discovery_result.data
                    if schema_data is None:
                        return ServiceResult.fail(
                            f"{OracleWMSErrorMessages.SCHEMA_GENERATION_FAILED}: "
                            "Discovery result data is None",
                        )

                    # Create entity info
                    entity_info = WMSEntityInfo(
                        entity_name=validated_entity_name,
                        display_name=entity_name.replace("_", " ").title(),
                        description=f"Dynamically discovered {entity_name} entity",
                        primary_key=self._infer_primary_key(schema_data["schema"]),
                        replication_key=self._infer_replication_key(
                            schema_data["schema"],
                        ),
                        schema=schema_data["schema"],
                    )

                    discovered_entities.append(entity_info)

            result = WMSDiscoveryResult(
                entities=discovered_entities,
                total_entities=len(discovered_entities),
                discovery_time=datetime.now(),
                api_version=connection_info.get("api_version", "unknown"),
                connection_info=connection_info,
            )

            return ServiceResult.ok(result)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.ENTITY_DISCOVERY_FAILED}: {e}",
            )

    def _discover_schema_from_records(self, records: WMSRecordBatch) -> WMSSchema:
        """Discover schema from record samples."""
        schema: dict[str, Any] = {}

        for record in records:
            self._analyze_record_structure(record, schema, depth=0)

        # Finalize schema with type inference
        if self.enable_type_inference:
            schema = self._finalize_schema_types(schema, records)

        return schema

    def _analyze_record_structure(
        self,
        record: WMSRecord,
        schema: WMSSchema,
        depth: int = 0,
    ) -> None:
        """Analyze record structure recursively."""
        if depth > self.max_schema_depth:
            return

        for field_name, field_value in record.items():
            if field_name not in schema:
                schema[field_name] = {
                    "type": self._infer_field_type(field_value),
                    "seen_count": 0,
                    "null_count": 0,
                    "sample_values": [],
                }

            field_schema = schema[field_name]
            field_schema["seen_count"] += 1

            if field_value is None:
                field_schema["null_count"] += 1
            else:
                # Add sample values for analysis
                if len(field_schema["sample_values"]) < 10:
                    field_schema["sample_values"].append(field_value)

                # Handle nested objects
                if isinstance(field_value, dict) and depth < self.max_schema_depth:
                    if "properties" not in field_schema:
                        field_schema["properties"] = {}

                    self._analyze_record_structure(
                        field_value,
                        field_schema["properties"],
                        depth + 1,
                    )

                # Handle arrays
                elif isinstance(field_value, list) and field_value:
                    if "items" not in field_schema:
                        field_schema["items"] = {"type": "object", "properties": {}}

                    # Analyze array items
                    for item in field_value[:5]:  # Limit to first 5 items
                        if isinstance(item, dict):
                            self._analyze_record_structure(
                                item,
                                field_schema["items"]["properties"],
                                depth + 1,
                            )

    def _finalize_schema_types(
        self,
        schema: WMSSchema,
        records: WMSRecordBatch,
    ) -> WMSSchema:
        """Finalize schema types based on analysis."""
        finalized_schema = {}

        for field_name, field_info in schema.items():
            if isinstance(field_info, dict):
                finalized_field = {
                    "type": field_info.get("type", "string"),
                    "nullable": field_info.get("null_count", 0) > 0,
                    "confidence": self._calculate_field_confidence(field_info),
                }

                # Add format information
                if field_info.get("type") == "string":
                    format_info = self._infer_string_format(
                        field_info.get("sample_values", []),
                    )
                    if format_info:
                        finalized_field["format"] = format_info

                # Add constraints
                if field_info.get("type") in {"integer", "number"}:
                    numeric_info = self._infer_numeric_constraints(
                        field_info.get("sample_values", []),
                    )
                    finalized_field.update(numeric_info)

                # Handle nested properties
                if "properties" in field_info:
                    finalized_field["properties"] = self._finalize_schema_types(
                        field_info["properties"],
                        records,
                    )

                # Handle array items
                if "items" in field_info:
                    finalized_field["items"] = self._finalize_schema_types(
                        {"items": field_info["items"]},
                        records,
                    )["items"]

                finalized_schema[field_name] = finalized_field

        return finalized_schema

    def _infer_field_type(self, value: Any) -> str:
        """Infer field type from value."""
        if value is None:
            return "null"

        for type_name, type_check in self.type_patterns.items():
            try:
                check_result: bool = type_check(value)
                if check_result:
                    return type_name
            except Exception as e:
                logger.debug("Type pattern check failed for %s: %s", type_name, e)
                continue

        return "string"

    def _calculate_field_confidence(self, field_info: dict[str, Any]) -> float:
        """Calculate confidence score for a field."""
        seen_count = field_info.get("seen_count", 0)
        null_count = field_info.get("null_count", 0)

        if seen_count == 0:
            return 0.0

        # Base confidence on consistency
        consistency_score = float(seen_count - null_count) / float(seen_count)

        # Adjust based on sample size
        sample_size_factor = min(float(seen_count) / 100.0, 1.0)

        return consistency_score * sample_size_factor

    def _infer_string_format(self, sample_values: list[Any]) -> str | None:
        """Infer string format from sample values."""
        if not sample_values:
            return None

        # Check for common patterns
        import re

        # Email pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if all(re.match(email_pattern, str(v)) for v in sample_values[:5]):
            return "email"

        # Date pattern
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if all(re.match(date_pattern, str(v)) for v in sample_values[:5]):
            return "date"

        # DateTime pattern
        datetime_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        if all(re.match(datetime_pattern, str(v)) for v in sample_values[:5]):
            return "date-time"

        # UUID pattern
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        if all(re.match(uuid_pattern, str(v)) for v in sample_values[:5]):
            return "uuid"

        return None

    def _infer_numeric_constraints(self, sample_values: list[Any]) -> dict[str, Any]:
        """Infer numeric constraints from sample values."""
        constraints: dict[str, Any] = {}

        numeric_values = [v for v in sample_values if isinstance(v, (int, float))]

        if numeric_values:
            constraints["minimum"] = float(min(numeric_values))
            constraints["maximum"] = float(max(numeric_values))

            # Check if all values are integers
            if all(isinstance(v, int) for v in numeric_values):
                constraints["data_type"] = "integer"
            else:
                constraints["data_type"] = "number"

        return constraints

    def _analyze_fields(
        self,
        records: WMSRecordBatch,
        schema: WMSSchema,
    ) -> dict[str, dict[str, Any]]:
        """Analyze field patterns and statistics."""
        field_analysis = {}

        for field_name, field_schema in schema.items():
            analysis = {
                "field_name": field_name,
                "data_type": field_schema.get("type", "unknown"),
                "nullable": field_schema.get("nullable", False),
                "confidence": field_schema.get("confidence", 0.0),
                "unique_values": set(),
                "value_distribution": {},
                "missing_count": 0,
                "total_count": 0,
            }

            # Analyze field values across all records
            for record in records:
                analysis["total_count"] += 1

                if field_name in record:
                    value = record[field_name]
                    if value is not None:
                        analysis["unique_values"].add(str(value))

                        # Track value distribution
                        value_str = str(value)
                        analysis["value_distribution"][value_str] = (
                            analysis["value_distribution"].get(value_str, 0) + 1
                        )
                    else:
                        analysis["missing_count"] += 1
                else:
                    analysis["missing_count"] += 1

            # Calculate statistics
            analysis["unique_count"] = len(analysis["unique_values"])
            analysis["missing_rate"] = (
                analysis["missing_count"] / analysis["total_count"]
            )
            analysis["cardinality"] = analysis["unique_count"] / max(
                analysis["total_count"],
                1,
            )

            # Convert set to list for JSON serialization
            analysis["unique_values"] = list(analysis["unique_values"])[
                :100
            ]  # Limit size

            field_analysis[field_name] = analysis

        return field_analysis

    def _calculate_schema_confidence(
        self,
        records: WMSRecordBatch,
        schema: WMSSchema,
        field_analysis: dict[str, dict[str, Any]],
    ) -> float:
        """Calculate overall schema confidence."""
        if not schema or not records:
            return 0.0

        field_confidences = []

        for field_name, field_schema in schema.items():
            field_confidence = field_schema.get("confidence", 0.0)

            # Adjust confidence based on field analysis
            if field_name in field_analysis:
                analysis = field_analysis[field_name]

                # Penalize high missing rates
                missing_rate = analysis.get("missing_rate", 0.0)
                missing_penalty = 1.0 - missing_rate

                # Reward appropriate cardinality
                cardinality = analysis.get("cardinality", 0.0)
                cardinality_score = 1.0 - abs(
                    cardinality - 0.5,
                )  # Ideal is moderate cardinality

                field_confidence *= missing_penalty * cardinality_score

            field_confidences.append(field_confidence)

        # Overall confidence is average of field confidences
        overall_confidence = sum(field_confidences) / len(field_confidences)

        return min(overall_confidence, 1.0)

    def _calculate_schema_depth(self, schema: WMSSchema) -> int:
        """Calculate maximum depth of schema structure."""
        max_depth = 0

        for field_schema in schema.values():
            if isinstance(field_schema, dict):
                depth = 1

                if "properties" in field_schema:
                    depth += self._calculate_schema_depth(field_schema["properties"])

                max_depth = max(max_depth, depth)

        return max_depth

    def _merge_schemas(
        self,
        existing_schema: WMSSchema,
        new_schema: WMSSchema,
    ) -> WMSSchema:
        """Merge existing schema with newly discovered schema."""
        merged_schema = existing_schema.copy()

        for field_name, field_info in new_schema.items():
            if field_name not in merged_schema:
                merged_schema[field_name] = field_info
            else:
                # Merge field information
                existing_field = merged_schema[field_name]

                if isinstance(existing_field, dict) and isinstance(field_info, dict):
                    # Update confidence to higher value
                    existing_confidence = existing_field.get("confidence", 0.0)
                    new_confidence = field_info.get("confidence", 0.0)

                    if new_confidence > existing_confidence:
                        merged_schema[field_name] = field_info

                    # Merge nested properties
                    if "properties" in existing_field and "properties" in field_info:
                        merged_schema[field_name]["properties"] = self._merge_schemas(
                            existing_field["properties"],
                            field_info["properties"],
                        )

        return merged_schema

    def _validate_record_against_schema(
        self,
        record: WMSRecord,
        schema: WMSSchema,
    ) -> dict[str, Any]:
        """Validate a record against a schema."""
        validation_result: dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Check required fields
        for field_name, field_schema in schema.items():
            if isinstance(field_schema, dict):
                is_required = field_schema.get("required", False)
                is_nullable = field_schema.get("nullable", True)

                if is_required and field_name not in record:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Required field '{field_name}' is missing",
                    )

                if field_name in record:
                    field_value = record[field_name]

                    # Check null values
                    if field_value is None and not is_nullable:
                        validation_result["valid"] = False
                        validation_result["errors"].append(
                            f"Field '{field_name}' cannot be null",
                        )

                    # Check type
                    if field_value is not None:
                        expected_type = field_schema.get("type", "string")
                        actual_type = self._infer_field_type(field_value)

                        if actual_type != expected_type:
                            validation_result["warnings"].append(
                                f"Field '{field_name}' expected type '{expected_type}' "
                                f"but got '{actual_type}'",
                            )

        # Check for extra fields
        for field_name in record:
            if field_name not in schema:
                validation_result["warnings"].append(
                    f"Extra field '{field_name}' not in schema",
                )

        return validation_result

    def _convert_record_types(
        self,
        record: WMSRecord,
        schema: WMSSchema,
    ) -> tuple[WMSRecord, dict[str, str]]:
        """Convert record field types to match schema."""
        converted_record = record.copy()
        conversions = {}

        for field_name, field_schema in schema.items():
            if field_name in converted_record and isinstance(field_schema, dict):
                current_value = converted_record[field_name]
                target_type = field_schema.get("type", "string")

                if current_value is not None:
                    try:
                        converted_value = self._convert_value_to_type(
                            current_value,
                            target_type,
                        )
                        if converted_value != current_value:
                            converted_record[field_name] = converted_value
                            conversions[field_name] = (
                                f"{type(current_value).__name__} -> {target_type}"
                            )
                    except Exception as e:
                        # Keep original value if conversion fails
                        conversions[field_name] = f"conversion_failed: {e!s}"

        return converted_record, conversions

    def _convert_value_to_type(self, value: Any, target_type: str) -> Any:
        """Convert value to target type."""
        if target_type == "string":
            return str(value)
        if target_type == "integer":
            return int(float(value))
        if target_type == "number":
            return float(value)
        if target_type == "boolean":
            if isinstance(value, bool):
                return value
            return str(value).lower() in {"true", "1", "yes", "on"}
        if target_type == "array":
            if isinstance(value, list):
                return value
            return [value]
        if target_type == "object":
            if isinstance(value, dict):
                return value
            return {"value": value}
        return value

    def _add_missing_fields(self, record: WMSRecord, schema: WMSSchema) -> WMSRecord:
        """Add missing fields with default values."""
        updated_record = record.copy()

        for field_name, field_schema in schema.items():
            if field_name not in updated_record and isinstance(field_schema, dict):
                default_value = field_schema.get("default")
                if default_value is not None:
                    updated_record[field_name] = default_value
                elif field_schema.get("nullable", True):
                    updated_record[field_name] = None

        return updated_record

    def _remove_extra_fields(self, record: WMSRecord, schema: WMSSchema) -> WMSRecord:
        """Remove fields not present in schema."""
        return {
            field_name: field_value
            for field_name, field_value in record.items()
            if field_name in schema
        }

    def _infer_primary_key(self, schema: WMSSchema) -> str:
        """Infer primary key from schema."""
        # Common primary key field names
        primary_key_candidates = ["id", "uuid", "key", "primary_key", "pk"]

        for candidate in primary_key_candidates:
            if candidate in schema:
                return candidate

        # Look for fields with "id" in the name
        for field_name in schema:
            if "id" in field_name.lower():
                return field_name

        # Return first field as fallback
        return next(iter(schema.keys())) if schema else "id"

    def _infer_replication_key(self, schema: WMSSchema) -> str | None:
        """Infer replication key from schema."""
        # Common replication key field names
        replication_key_candidates = [
            "last_modified",
            "updated_at",
            "modification_date",
            "last_update",
            "timestamp",
            "modts",
        ]

        for candidate in replication_key_candidates:
            if candidate in schema:
                return candidate

        # Look for fields with time-related names
        for field_name in schema:
            if any(
                time_word in field_name.lower()
                for time_word in ["time", "date", "modified", "updated"]
            ):
                return field_name

        return None


# Factory function for easy instantiation
def create_dynamic_schema_processor(**kwargs: Any) -> DynamicSchemaProcessor:
    """Create a configured dynamic schema processor."""
    return DynamicSchemaProcessor(**kwargs)


# Convenience functions for common scenarios
def discover_entity_schemas(
    entities_data: dict[str, WMSRecordBatch],
    connection_info: WMSConnectionInfo,
    **processor_kwargs: Any,
) -> ServiceResult[WMSDiscoveryResult]:
    """Discover schemas for multiple entities."""
    processor = create_dynamic_schema_processor(**processor_kwargs)
    return processor.discover_all_entities(entities_data, connection_info)


def process_entity_with_schema(
    entity_name: OracleWMSEntityType,
    records: WMSRecordBatch,
    target_schema: WMSSchema,
    **processor_kwargs: Any,
) -> ServiceResult[EntityProcessingResult]:
    """Process entity records with schema validation."""
    processor = create_dynamic_schema_processor(**processor_kwargs)
    return processor.process_entity_records(entity_name, records, target_schema)


__all__ = [
    "DynamicSchemaProcessor",
    "EntityProcessingResult",
    "SchemaDiscoveryResult",
    "create_dynamic_schema_processor",
    "discover_entity_schemas",
    "process_entity_with_schema",
]
