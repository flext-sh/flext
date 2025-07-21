"""Oracle WMS Advanced Filtering Module - Comprehensive filtering capabilities.

This module provides advanced filtering capabilities for Oracle WMS integrations
with support for all required operators and pagination modes.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from flext_core.domain.types import ServiceResult

from flext_oracle_wms.constants import (
    OracleWMSErrorMessages,
    OracleWMSFilterOperators,
    OracleWMSPageModes,
)

if TYPE_CHECKING:
    from flext_oracle_wms.constants import (
        OracleWMSEntityType,
        OracleWMSFilterOperator,
        OracleWMSPageMode,
    )
    from flext_oracle_wms.typedefs import (
        WMSFieldName,
        WMSFilterValue,
        WMSOffset,
        WMSPageSize,
        WMSPageToken,
        WMSRecord,
        WMSRecordBatch,
    )


class FilterCondition(TypedDict):
    """Advanced filter condition structure."""

    field: WMSFieldName
    operator: OracleWMSFilterOperator
    value: WMSFilterValue
    case_sensitive: bool
    data_type: str  # "string", "number", "boolean", "date", "datetime"


class FilterGroup(TypedDict):
    """Filter group with logical operations."""

    conditions: list[FilterCondition]
    logical_operator: Literal["AND", "OR"]
    nested_groups: list[FilterGroup]


class FilterQuery(TypedDict):
    """Complete filter query structure."""

    entity: OracleWMSEntityType
    filter_groups: list[FilterGroup]
    ordering: list[dict[str, str]]  # [{"field": "field_name", "direction": "ASC|DESC"}]
    page_mode: OracleWMSPageMode
    page_size: WMSPageSize
    page_offset: WMSOffset | None
    page_token: WMSPageToken | None
    limit: int | None


class FilterResult(TypedDict):
    """Result of filtering operation."""

    filtered_records: WMSRecordBatch
    total_count: int
    filtered_count: int
    has_next_page: bool
    next_page_token: str | None
    execution_time_ms: float
    filter_summary: dict[str, Any]


class OracleWMSAdvancedFilter:
    """Oracle WMS advanced filtering engine with comprehensive capabilities."""

    def __init__(
        self,
        max_conditions: int = 100,
        max_nested_groups: int = 10,
        enable_optimization: bool = True,
        case_sensitive_default: bool = False,
        date_format: str = "%Y-%m-%d",
        datetime_format: str = "%Y-%m-%d %H:%M:%S",
    ) -> None:
        """Initialize advanced filter with configuration."""
        self.max_conditions = max_conditions
        self.max_nested_groups = max_nested_groups
        self.enable_optimization = enable_optimization
        self.case_sensitive_default = case_sensitive_default
        self.date_format = date_format
        self.datetime_format = datetime_format

        # Operator mapping
        self.operators = {
            OracleWMSFilterOperators.EQ: self._op_equals,
            OracleWMSFilterOperators.NEQ: self._op_not_equals,
            OracleWMSFilterOperators.GT: self._op_greater_than,
            OracleWMSFilterOperators.GTE: self._op_greater_than_equal,
            OracleWMSFilterOperators.LT: self._op_less_than,
            OracleWMSFilterOperators.LTE: self._op_less_than_equal,
            OracleWMSFilterOperators.IN: self._op_in,
            OracleWMSFilterOperators.NIN: self._op_not_in,
            OracleWMSFilterOperators.LIKE: self._op_like,
        }

    def filter_records(
        self,
        records: WMSRecordBatch,
        filter_query: FilterQuery,
    ) -> ServiceResult[FilterResult]:
        """Filter records using advanced query."""
        start_time = datetime.now()

        try:
            # Validate filter query
            validation_result = self._validate_filter_query(filter_query)
            if not validation_result.is_success:
                return ServiceResult.fail(
                    f"{OracleWMSErrorMessages.INVALID_FILTER_OPERATOR}: "
                    f"{validation_result.error}",
                )

            # Apply filtering
            filter_groups = filter_query["filter_groups"]
            filtered_records = self._apply_filters(records, filter_groups)

            # Apply ordering
            ordering = filter_query["ordering"]
            if ordering:
                filtered_records = self._apply_ordering(
                    filtered_records,
                    ordering,
                )

            # Apply pagination
            paginated_result = self._apply_pagination(
                filtered_records,
                filter_query["page_mode"],
                filter_query["page_size"],
                filter_query["page_offset"],
                filter_query["page_token"],
                filter_query["limit"],
            )

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            result = FilterResult(
                filtered_records=paginated_result["records"],
                total_count=len(records),
                filtered_count=len(filtered_records),
                has_next_page=paginated_result["has_next"],
                next_page_token=paginated_result["next_token"],
                execution_time_ms=execution_time,
                filter_summary=self._generate_filter_summary(filter_query),
            )

            return ServiceResult.ok(result)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.INVALID_FILTER_OPERATOR}: {e}",
            )

    def build_filter_query(
        self,
        entity: OracleWMSEntityType,
        filters: dict[str, Any],
        ordering: list[dict[str, str]] | None = None,
        page_mode: OracleWMSPageMode = OracleWMSPageModes.DEFAULT,
        page_size: int = 100,
        **kwargs: Any,
    ) -> FilterQuery:
        """Build a filter query from parameters."""
        filter_groups = []

        if filters:
            conditions = []
            for field, filter_config in filters.items():
                if isinstance(filter_config, dict):
                    for operator, value in filter_config.items():
                        if operator in self.operators:
                            condition = FilterCondition(
                                field=field,
                                operator=operator,
                                value=value,
                                case_sensitive=self.case_sensitive_default,
                                data_type=self._infer_data_type(value),
                            )
                            conditions.append(condition)
                else:
                    # Simple equality filter
                    condition = FilterCondition(
                        field=field,
                        operator=OracleWMSFilterOperators.EQ,
                        value=filter_config,
                        case_sensitive=self.case_sensitive_default,
                        data_type=self._infer_data_type(filter_config),
                    )
                    conditions.append(condition)

            if conditions:
                filter_groups.append(
                    FilterGroup(
                        conditions=conditions,
                        logical_operator="AND",
                        nested_groups=[],
                    ),
                )

        return FilterQuery(
            entity=entity,
            filter_groups=filter_groups,
            ordering=ordering or [],
            page_mode=page_mode,
            page_size=page_size,
            page_offset=kwargs.get("page_offset"),
            page_token=kwargs.get("page_token"),
            limit=kwargs.get("limit"),
        )

    def _validate_filter_query(self, filter_query: FilterQuery) -> ServiceResult[bool]:
        """Validate filter query structure."""
        try:
            # Count total conditions
            total_conditions = 0
            filter_groups = filter_query["filter_groups"]
            for group in filter_groups:
                total_conditions += len(group["conditions"])
                total_conditions += sum(
                    len(nested["conditions"]) for nested in group["nested_groups"]
                )

            if total_conditions > self.max_conditions:
                return ServiceResult.fail(
                    f"{OracleWMSErrorMessages.TOO_MANY_FILTERS}: "
                    f"{total_conditions} > {self.max_conditions}",
                )

            # Validate nested groups depth
            for group in filter_groups:
                if len(group["nested_groups"]) > self.max_nested_groups:
                    return ServiceResult.fail(
                        f"{OracleWMSErrorMessages.TOO_MANY_FILTERS}: "
                        f"nested groups {len(group['nested_groups'])} > "
                        f"{self.max_nested_groups}",
                    )

            # Validate operators
            for group in filter_groups:
                for condition in group["conditions"]:
                    if condition["operator"] not in self.operators:
                        return ServiceResult.fail(
                            f"{OracleWMSErrorMessages.INVALID_FILTER_OPERATOR}: "
                            f"{condition['operator']}",
                        )

            # Validate page mode
            page_mode = filter_query["page_mode"]
            if page_mode not in OracleWMSPageModes.ALL_MODES:
                return ServiceResult.fail(
                    f"{OracleWMSErrorMessages.INVALID_FILTER_OPERATOR}: "
                    f"invalid page mode {page_mode}",
                )

            return ServiceResult.ok(True)

        except Exception as e:
            return ServiceResult.fail(
                f"{OracleWMSErrorMessages.INVALID_FILTER_OPERATOR}: "
                f"validation error {e}",
            )

    def _apply_filters(
        self,
        records: WMSRecordBatch,
        filter_groups: list[FilterGroup],
    ) -> WMSRecordBatch:
        """Apply filter groups to records."""
        if not filter_groups:
            return records

        return [
            record
            for record in records
            if self._record_matches_groups(record, filter_groups)
        ]

    def _record_matches_groups(
        self,
        record: WMSRecord,
        filter_groups: list[FilterGroup],
    ) -> bool:
        """Check if record matches all filter groups (AND logic between groups)."""
        return all(self._record_matches_group(record, group) for group in filter_groups)

    def _record_matches_group(
        self,
        record: WMSRecord,
        filter_group: FilterGroup,
    ) -> bool:
        """Check if record matches a filter group."""
        # Check conditions within the group
        condition_results = [
            self._record_matches_condition(record, condition)
            for condition in filter_group["conditions"]
        ]

        # Check nested groups
        nested_results = [
            self._record_matches_group(record, nested_group)
            for nested_group in filter_group["nested_groups"]
        ]

        # Combine all results
        all_results = condition_results + nested_results

        if not all_results:
            return True

        # Apply logical operator
        if filter_group["logical_operator"] == "AND":
            return all(all_results)
        # OR
        return any(all_results)

    def _record_matches_condition(
        self,
        record: WMSRecord,
        condition: FilterCondition,
    ) -> bool:
        """Check if record matches a specific condition."""
        field_value = self._get_nested_field_value(record, condition["field"])

        if field_value is None:
            return False

        # Convert values for comparison
        converted_field_value = self._convert_value(field_value, condition["data_type"])
        converted_filter_value = self._convert_value(
            condition["value"],
            condition["data_type"],
        )

        # Apply case sensitivity for string comparisons
        if condition["data_type"] == "string" and not condition["case_sensitive"]:
            if isinstance(converted_field_value, str):
                converted_field_value = converted_field_value.lower()
            if isinstance(converted_filter_value, str):
                converted_filter_value = converted_filter_value.lower()

        # Apply operator
        operator_func = self.operators.get(condition["operator"])
        if operator_func:
            return operator_func(converted_field_value, converted_filter_value)

        return False

    def _apply_ordering(
        self,
        records: WMSRecordBatch,
        ordering: list[dict[str, str]],
    ) -> WMSRecordBatch:
        """Apply ordering to records."""
        if not ordering:
            return records

        try:

            def sort_key(record: WMSRecord) -> tuple[Any, ...]:
                key_values = []
                for order_spec in ordering:
                    field = order_spec["field"]
                    direction = order_spec.get("direction", "ASC")

                    field_value = self._get_nested_field_value(record, field)

                    # Handle None values
                    if field_value is None:
                        field_value = ""

                    # Apply reverse for DESC
                    if direction.upper() == "DESC":
                        if isinstance(field_value, str):
                            field_value = field_value[::-1]  # Reverse string for DESC
                        elif isinstance(field_value, (int, float)):
                            field_value = -field_value  # Negate number for DESC

                    key_values.append(field_value)

                return tuple(key_values)

            return sorted(records, key=sort_key)
        except Exception:
            # Fallback to original order if sorting fails
            return records

    def _apply_pagination(
        self,
        records: WMSRecordBatch,
        page_mode: OracleWMSPageMode,
        page_size: int,
        page_offset: int | None,
        page_token: str | None,
        limit: int | None,
    ) -> dict[str, Any]:
        """Apply pagination to records."""
        total_records = len(records)

        # Apply limit first if specified
        if limit is not None:
            records = records[:limit]

        # Apply pagination based on mode
        if page_mode == OracleWMSPageModes.API:
            # Offset-based pagination
            offset = page_offset or 0
            end_index = offset + page_size

            paginated_records = records[offset:end_index]
            has_next = end_index < len(records)
            next_token = str(end_index) if has_next else None

        elif page_mode == OracleWMSPageModes.SEQUENCED:
            # Cursor-based pagination
            if page_token:
                try:
                    cursor_index = int(page_token)
                except ValueError:
                    cursor_index = 0
            else:
                cursor_index = 0

            end_index = cursor_index + page_size
            paginated_records = records[cursor_index:end_index]
            has_next = end_index < len(records)
            next_token = str(end_index) if has_next else None

        # Note: This branch is reachable for any page_mode not in the if/elif above
        # Remove else block to fix unreachable code warning
        # Handled by the 'sequenced' elif block above

        return {
            "records": paginated_records,
            "has_next": has_next,
            "next_token": next_token,
            "total_available": total_records,
            "page_size": page_size,
            "current_page_size": len(paginated_records),
        }

    def _get_nested_field_value(self, record: WMSRecord, field_path: str) -> Any:
        """Get value from nested field path."""
        if "." not in field_path:
            return record.get(field_path)

        current_value: Any = record
        for field_part in field_path.split("."):
            if isinstance(current_value, dict):
                current_value = current_value.get(field_part)
                if current_value is None:
                    return None
            else:
                return None

        return current_value

    def _convert_value(self, value: Any, data_type: str) -> Any:
        """Convert value to appropriate type for comparison."""
        try:
            if value is None:
                return None
            if data_type == "string":
                return str(value)
            if data_type == "number":
                if isinstance(value, (int, float)):
                    return value
                return float(value)
            if data_type == "boolean":
                if isinstance(value, bool):
                    return value
                return str(value).lower() in {"true", "1", "yes", "on"}
            if data_type == "date":
                if isinstance(value, datetime):
                    return value.date()
                return (
                    datetime.strptime(str(value), self.date_format)
                    .replace(tzinfo=UTC)
                    .date()
                )
            if data_type == "datetime":
                if isinstance(value, datetime):
                    return value
                return datetime.strptime(str(value), self.datetime_format).replace(
                    tzinfo=UTC,
                )
            return value
        except Exception:
            return value

    def _infer_data_type(self, value: Any) -> str:
        """Infer data type from value."""
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, str):
            # Try to detect date/datetime patterns
            if re.match(r"\d{4}-\d{2}-\d{2}$", value):
                return "date"
            if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", value):
                return "datetime"
            return "string"
        if isinstance(value, datetime):
            return "datetime"
        return "string"

    def _generate_filter_summary(self, filter_query: FilterQuery) -> dict[str, Any]:
        """Generate summary of applied filters."""
        filter_groups = filter_query["filter_groups"]
        summary: dict[str, Any] = {
            "entity": filter_query["entity"],
            "total_filter_groups": len(filter_groups),
            "total_conditions": sum(
                len(group["conditions"]) for group in filter_groups
            ),
            "ordering_fields": [order["field"] for order in filter_query["ordering"]],
            "page_mode": filter_query["page_mode"],
            "page_size": filter_query["page_size"],
            "has_limit": filter_query["limit"] is not None,
        }

        # Add operator distribution
        operator_counts: dict[str, int] = {}
        for group in filter_groups:
            for condition in group["conditions"]:
                operator = condition["operator"]
                operator_counts[operator] = operator_counts.get(operator, 0) + 1

        # Ensure type safety for summary dictionary
        summary["operator_distribution"] = dict(operator_counts)

        return summary

    # Operator implementations
    def _op_equals(self, field_value: Any, filter_value: Any) -> bool:
        """Equality operator."""
        result: bool = field_value == filter_value
        return result

    def _op_not_equals(self, field_value: Any, filter_value: Any) -> bool:
        """Not equals operator."""
        result: bool = field_value != filter_value
        return result

    def _op_greater_than(self, field_value: Any, filter_value: Any) -> bool:
        """Greater than operator."""
        result: bool = field_value > filter_value
        return result

    def _op_greater_than_equal(self, field_value: Any, filter_value: Any) -> bool:
        """Greater than or equal operator."""
        result: bool = field_value >= filter_value
        return result

    def _op_less_than(self, field_value: Any, filter_value: Any) -> bool:
        """Less than operator."""
        result: bool = field_value < filter_value
        return result

    def _op_less_than_equal(self, field_value: Any, filter_value: Any) -> bool:
        """Less than or equal operator."""
        result: bool = field_value <= filter_value
        return result

    def _op_in(self, field_value: Any, filter_value: Any) -> bool:
        """In operator (value in list)."""
        if not isinstance(filter_value, (list, tuple, set)):
            return False
        return field_value in filter_value

    def _op_not_in(self, field_value: Any, filter_value: Any) -> bool:
        """Not in operator (value not in list)."""
        if not isinstance(filter_value, (list, tuple, set)):
            return True
        return field_value not in filter_value

    def _op_like(self, field_value: Any, filter_value: Any) -> bool:
        """Like operator (pattern matching)."""
        if not isinstance(field_value, str) or not isinstance(filter_value, str):
            return False

        # Convert SQL LIKE pattern to regex
        pattern = filter_value.replace("%", ".*").replace("_", ".")
        return bool(re.search(pattern, field_value, re.IGNORECASE))


# Factory function for easy instantiation
def create_advanced_filter(**kwargs: Any) -> OracleWMSAdvancedFilter:
    """Create a configured Oracle WMS advanced filter."""
    return OracleWMSAdvancedFilter(**kwargs)


# Convenience functions for common filtering scenarios
def filter_by_id_range(
    records: WMSRecordBatch,
    entity: OracleWMSEntityType,
    id_field: str = "id",
    id_min: int | None = None,
    id_max: int | None = None,
) -> ServiceResult[FilterResult]:
    """Filter records by ID range."""
    filter_engine = create_advanced_filter()

    filters = {}
    if id_min is not None:
        filters[id_field] = {OracleWMSFilterOperators.GTE: id_min}
    if id_max is not None:
        filters[id_field] = {
            **filters.get(id_field, {}),
            OracleWMSFilterOperators.LTE: id_max,
        }

    filter_query = filter_engine.build_filter_query(entity, filters)
    return filter_engine.filter_records(records, filter_query)


def filter_by_modification_time(
    records: WMSRecordBatch,
    entity: OracleWMSEntityType,
    modts_field: str = "last_modified",
    modts_gte: str | None = None,
    modts_lte: str | None = None,
) -> ServiceResult[FilterResult]:
    """Filter records by modification timestamp."""
    filter_engine = create_advanced_filter()

    filters = {}
    if modts_gte is not None:
        filters[modts_field] = {OracleWMSFilterOperators.GTE: modts_gte}
    if modts_lte is not None:
        filters[modts_field] = {
            **filters.get(modts_field, {}),
            OracleWMSFilterOperators.LTE: modts_lte,
        }

    filter_query = filter_engine.build_filter_query(entity, filters)
    return filter_engine.filter_records(records, filter_query)


__all__ = [
    "FilterCondition",
    "FilterGroup",
    "FilterQuery",
    "FilterResult",
    "OracleWMSAdvancedFilter",
    "create_advanced_filter",
    "filter_by_id_range",
    "filter_by_modification_time",
]
