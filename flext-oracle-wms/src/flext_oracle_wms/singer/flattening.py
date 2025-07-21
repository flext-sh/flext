"""Oracle WMS Singer SDK Flattening/Deflattening Module - Mandatory capabilities.

This module provides MANDATORY flattening and deflattening capabilities for Oracle WMS
Singer SDK compliance as required by the user specifications.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from flext_core.domain.types import ServiceResult

from flext_oracle_wms.constants import OracleWMSDefaults, OracleWMSErrorMessages

if TYPE_CHECKING:
    from flext_oracle_wms.typedefs import (
        WMSFlattenedRecord,
        WMSFlattenedSchema,
        WMSRecord,
        WMSRecordBatch,
        WMSSchema,
    )


class FlatteningResult(TypedDict):
    """Result of flattening operation."""

    flattened_record: WMSFlattenedRecord
    original_schema: WMSSchema
    flattened_schema: WMSFlattenedSchema
    metadata: dict[str, Any]


class DeflatteningResult(TypedDict):
    """Result of deflattening operation."""

    original_record: WMSRecord
    restored_schema: WMSSchema
    metadata: dict[str, Any]


class OracleWMSFlattener:
    """Oracle WMS data flattener with mandatory capabilities."""

    def __init__(
        self,
        enabled: bool = OracleWMSDefaults.DEFAULT_FLATTEN_ENABLED,
        max_depth: int = OracleWMSDefaults.DEFAULT_FLATTEN_MAX_DEPTH,
        separator: str = OracleWMSDefaults.FLATTEN_SEPARATOR,
        preserve_types: bool = True,
        preserve_null_values: bool = True,
        preserve_empty_objects: bool = False,
        preserve_empty_arrays: bool = False,
    ) -> None:
        """Initialize flattener with configuration."""
        self.enabled = enabled
        self.max_depth = max_depth
        self.separator = separator
        self.preserve_types = preserve_types
        self.preserve_null_values = preserve_null_values
        self.preserve_empty_objects = preserve_empty_objects
        self.preserve_empty_arrays = preserve_empty_arrays

    def flatten_record(
        self,
        record: WMSRecord,
        schema: WMSSchema | None = None,
    ) -> ServiceResult[FlatteningResult]:
        """Flatten a WMS record with mandatory capabilities."""
        if not self.enabled:
            return ServiceResult.ok(
                FlatteningResult(
                    flattened_record=record,
                    original_schema=schema or {},
                    flattened_schema=schema or {},
                    metadata={"flattening_enabled": False},
                ),
            )

        try:
            flattened_record = self._flatten_object(record, prefix="", depth=0)

            # Generate flattened schema if original schema provided
            flattened_schema = {}
            if schema:
                flattened_schema = self._flatten_schema(schema)

            result = FlatteningResult(
                flattened_record=flattened_record,
                original_schema=schema or {},
                flattened_schema=flattened_schema,
                metadata={
                    "flattening_enabled": True,
                    "max_depth": self.max_depth,
                    "separator": self.separator,
                    "total_fields": len(flattened_record),
                    "original_fields": len(record),
                    "flattening_ratio": (
                        len(flattened_record) / len(record) if record else 0
                    ),
                },
            )

            return ServiceResult.ok(result)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.FLATTENING_FAILED}: {e}",
            )

    def flatten_batch(
        self,
        records: WMSRecordBatch,
        schema: WMSSchema | None = None,
    ) -> ServiceResult[list[FlatteningResult]]:
        """Flatten a batch of WMS records."""
        if not self.enabled:
            return ServiceResult.ok(
                [
                    FlatteningResult(
                        flattened_record=record,
                        original_schema=schema or {},
                        flattened_schema=schema or {},
                        metadata={"flattening_enabled": False},
                    )
                    for record in records
                ],
            )

        try:
            results: list[FlatteningResult] = []
            for record in records:
                flatten_result = self.flatten_record(record, schema)
                if not flatten_result.is_success:
                    return ServiceResult.fail(
                        f"{OracleWMSErrorMessages.FLATTENING_FAILED}: "
                        f"{flatten_result.error}",
                    )
                # Since we know it's successful, data is guaranteed to be not None
                if flatten_result.data is None:
                    return ServiceResult.fail(
                        f"{OracleWMSErrorMessages.FLATTENING_FAILED}: "
                        "Result data is None despite success status",
                    )
                results.append(flatten_result.data)

            return ServiceResult.ok(results)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.FLATTENING_FAILED}: {e}",
            )

    def _flatten_object(
        self,
        obj: Any,
        prefix: str = "",
        depth: int = 0,
    ) -> dict[str, Any]:
        """Recursively flatten an object."""
        if depth >= self.max_depth:
            return {prefix.rstrip(self.separator): obj}

        if not isinstance(obj, dict):
            return {prefix.rstrip(self.separator): obj}

        flattened = {}

        for key, value in obj.items():
            new_key = (
                f"{prefix}{key}" if not prefix else f"{prefix}{self.separator}{key}"
            )

            if isinstance(value, dict):
                if not value and not self.preserve_empty_objects:
                    continue
                flattened.update(
                    self._flatten_object(value, new_key + self.separator, depth + 1),
                )
            elif isinstance(value, list):
                if not value and not self.preserve_empty_arrays:
                    continue
                flattened.update(self._flatten_array(value, new_key, depth + 1))
            elif value is None and not self.preserve_null_values:
                continue
            else:
                flattened[new_key] = value

        return flattened

    def _flatten_array(
        self,
        arr: list[Any],
        prefix: str,
        depth: int,
    ) -> dict[str, Any]:
        """Flatten an array with indexed keys."""
        flattened = {}

        for i, item in enumerate(arr):
            indexed_key = f"{prefix}{self.separator}{i}"

            if isinstance(item, dict):
                flattened.update(
                    self._flatten_object(item, indexed_key + self.separator, depth),
                )
            elif isinstance(item, list):
                flattened.update(self._flatten_array(item, indexed_key, depth))
            else:
                flattened[indexed_key] = item

        return flattened

    def _flatten_schema(self, schema: WMSSchema) -> WMSFlattenedSchema:
        """Flatten a schema structure."""
        flattened_schema = {}

        for field_name, field_props in schema.items():
            if isinstance(field_props, dict) and "type" in field_props:
                if field_props["type"] == "object" and "properties" in field_props:
                    # Flatten nested object schema
                    nested_schema = self._flatten_schema(field_props["properties"])
                    for nested_field, nested_props in nested_schema.items():
                        flattened_key = f"{field_name}{self.separator}{nested_field}"
                        flattened_schema[flattened_key] = nested_props
                elif field_props["type"] == "array" and "items" in field_props:
                    # Handle array schema flattening
                    array_key = f"{field_name}{self.separator}*"
                    flattened_schema[array_key] = field_props["items"]
                else:
                    flattened_schema[field_name] = field_props
            else:
                flattened_schema[field_name] = field_props

        return flattened_schema


class OracleWMSDeflattener:
    """Oracle WMS data deflattener with mandatory capabilities."""

    def __init__(
        self,
        separator: str = OracleWMSDefaults.FLATTEN_SEPARATOR,
        restore_types: bool = True,
        validate_structure: bool = True,
        strict_mode: bool = False,
    ) -> None:
        """Initialize deflattener with configuration."""
        self.separator = separator
        self.restore_types = restore_types
        self.validate_structure = validate_structure
        self.strict_mode = strict_mode

    def deflattened_record(
        self,
        flattened_record: WMSFlattenedRecord,
        original_schema: WMSSchema | None = None,
    ) -> ServiceResult[DeflatteningResult]:
        """Deflattened a flattened WMS record."""
        try:
            original_record = self._deflattened_object(flattened_record)

            # Restore schema if provided
            restored_schema = original_schema or {}
            if original_schema:
                restored_schema = self._restore_schema(original_schema)

            # Validate structure if enabled
            if self.validate_structure and original_schema:
                validation_result = self._validate_restored_structure(
                    original_record,
                    restored_schema,
                )
                if not validation_result:
                    return ServiceResult.fail(
                        f"{OracleWMSErrorMessages.DEFLATTENING_FAILED}: "
                        "Restored structure doesn't match schema",
                    )

            result = DeflatteningResult(
                original_record=original_record,
                restored_schema=restored_schema,
                metadata={
                    "deflattening_enabled": True,
                    "separator": self.separator,
                    "total_restored_fields": len(original_record),
                    "original_flattened_fields": len(flattened_record),
                    "restoration_ratio": (
                        len(original_record) / len(flattened_record)
                        if flattened_record
                        else 0
                    ),
                },
            )

            return ServiceResult.ok(result)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.DEFLATTENING_FAILED}: {e}",
            )

    def deflattened_batch(
        self,
        flattened_records: list[WMSFlattenedRecord],
        original_schema: WMSSchema | None = None,
    ) -> ServiceResult[list[DeflatteningResult]]:
        """Deflattened a batch of flattened WMS records."""
        try:
            results: list[DeflatteningResult] = []
            for flattened_record in flattened_records:
                deflattened_result = self.deflattened_record(
                    flattened_record,
                    original_schema,
                )
                if not deflattened_result.is_success:
                    return ServiceResult.fail(
                        f"{OracleWMSErrorMessages.DEFLATTENING_FAILED}: "
                        f"{deflattened_result.error}",
                    )
                # Since we know it's successful, data is guaranteed to be not None
                if deflattened_result.data is None:
                    return ServiceResult.fail(
                        f"{OracleWMSErrorMessages.DEFLATTENING_FAILED}: "
                        "Result data is None despite success status",
                    )
                results.append(deflattened_result.data)

            return ServiceResult.ok(results)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.DEFLATTENING_FAILED}: {e}",
            )

    def _deflattened_object(self, flattened_obj: dict[str, Any]) -> dict[str, Any]:
        """Recursively deflattened a flattened object."""
        result: dict[str, Any] = {}

        for key, value in flattened_obj.items():
            self._set_nested_value(result, key, value)

        return result

    def _set_nested_value(self, obj: dict[str, Any], key: str, value: Any) -> None:
        """Set a nested value in an object using dot notation."""
        if self.separator not in key:
            obj[key] = value
            return

        keys = key.split(self.separator)
        current = obj

        for i, k in enumerate(keys[:-1]):
            # Handle array indices
            if k.isdigit():
                # Convert current level to array if needed
                parent_key = keys[i - 1] if i > 0 else None
                if parent_key and parent_key in current:
                    if not isinstance(current[parent_key], list):
                        current[parent_key] = []

                    # Extend array if needed
                    index = int(k)
                    while len(current[parent_key]) <= index:
                        current[parent_key].append({})

                    current = current[parent_key][index]
                else:
                    # This shouldn't happen in well-formed flattened data
                    if self.strict_mode:
                        msg = f"Invalid array index structure: {key}"
                        raise ValueError(msg)
                    continue
            else:
                if k not in current:
                    # Check if next key is a digit (array index)
                    if i + 1 < len(keys) - 1 and keys[i + 1].isdigit():
                        current[k] = []
                    else:
                        current[k] = {}
                current = current[k]

        # Set the final value
        final_key = keys[-1]
        if final_key.isdigit():
            # This is an array index - but current should be a dict here
            # The parent should have been set as an array in the loop above
            index = int(final_key)
            parent_key = keys[-2] if len(keys) > 1 else None
            if parent_key and parent_key in obj:
                parent_obj = obj
                for k in keys[:-2]:
                    parent_obj = parent_obj[k]
                if parent_key in parent_obj and isinstance(
                    parent_obj[parent_key],
                    list,
                ):
                    while len(parent_obj[parent_key]) <= index:
                        parent_obj[parent_key].append(None)
                    parent_obj[parent_key][index] = value
                else:
                    # Fallback: treat as regular field
                    current[final_key] = value
            else:
                current[final_key] = value
        else:
            current[final_key] = value

    def _restore_schema(self, flattened_schema: WMSFlattenedSchema) -> WMSSchema:
        """Restore original schema from flattened schema."""
        restored_schema: dict[str, Any] = {}

        for field_name, field_props in flattened_schema.items():
            if self.separator in field_name:
                # This is a nested field, restore its structure
                self._set_nested_schema_value(restored_schema, field_name, field_props)
            else:
                restored_schema[field_name] = field_props

        return restored_schema

    def _set_nested_schema_value(
        self,
        schema: dict[str, Any],
        field_path: str,
        field_props: Any,
    ) -> None:
        """Set nested schema value using field path."""
        keys = field_path.split(self.separator)
        current = schema

        for _i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {"type": "object", "properties": {}}

            if "properties" not in current[key]:
                current[key]["properties"] = {}

            current = current[key]["properties"]

        # Set the final field
        final_key = keys[-1]
        current[final_key] = field_props

    def _validate_restored_structure(
        self,
        restored_record: WMSRecord,
        original_schema: WMSSchema,
    ) -> bool:
        """Validate that restored record matches original schema."""
        try:
            # Basic structure validation
            for field_name, field_props in original_schema.items():
                if isinstance(field_props, dict) and "type" in field_props:
                    if (
                        field_props.get("required", False)
                        and field_name not in restored_record
                    ):
                        return False

                    if field_name in restored_record:
                        field_type = field_props["type"]
                        field_value = restored_record[field_name]

                        # Type validation
                        if (
                            field_type == "object" and not isinstance(field_value, dict)
                        ) or (
                            field_type == "array"
                            and not isinstance(
                                field_value,
                                list,
                            )
                        ):
                            return False
                        if (
                            (
                                field_type == "string"
                                and not isinstance(
                                    field_value,
                                    str,
                                )
                            )
                            or (
                                field_type == "number"
                                and not isinstance(
                                    field_value,
                                    (int, float),
                                )
                            )
                            or (
                                field_type == "boolean"
                                and not isinstance(
                                    field_value,
                                    bool,
                                )
                            )
                        ):
                            return False

            return True

        except Exception:
            return False


# Factory functions for easy instantiation
def create_flattener(
    enabled: bool = True,
    max_depth: int = 5,
    separator: str = "__",
    **kwargs: Any,
) -> OracleWMSFlattener:
    """Create a configured Oracle WMS flattener."""
    return OracleWMSFlattener(
        enabled=enabled,
        max_depth=max_depth,
        separator=separator,
        **kwargs,
    )


def create_deflattener(
    separator: str = "__",
    strict_mode: bool = False,
    **kwargs: Any,
) -> OracleWMSDeflattener:
    """Create a configured Oracle WMS deflattener."""
    return OracleWMSDeflattener(separator=separator, strict_mode=strict_mode, **kwargs)


# Convenience functions for direct usage
def flatten_wms_record(
    record: WMSRecord,
    schema: WMSSchema | None = None,
    **flattener_kwargs: Any,
) -> ServiceResult[FlatteningResult]:
    """Flatten a WMS record with default configuration."""
    flattener = create_flattener(**flattener_kwargs)
    return flattener.flatten_record(record, schema)


def deflattened_wms_record(
    flattened_record: WMSFlattenedRecord,
    original_schema: WMSSchema | None = None,
    **deflattener_kwargs: Any,
) -> ServiceResult[DeflatteningResult]:
    """Deflattened a WMS record with default configuration."""
    deflattener = create_deflattener(**deflattener_kwargs)
    return deflattener.deflattened_record(flattened_record, original_schema)


__all__ = [
    "DeflatteningResult",
    "FlatteningResult",
    "OracleWMSDeflattener",
    "OracleWMSFlattener",
    "create_deflattener",
    "create_flattener",
    "deflattened_wms_record",
    "flatten_wms_record",
]
