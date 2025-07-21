"""Type definitions for Oracle WMS integrations.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Centralized type definitions for Oracle WMS operations using flext-core standards.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, Any, TypedDict

# Import flext-core types
from flext_core.domain.types import (
    WMSEntityName,  # Use centralized WMSEntityName from flext-core
)
from pydantic import Field, StringConstraints

# Import Oracle WMS constants
from flext_oracle_wms.constants import (
    OracleWMSFilterOperator,
)

# Define positive/non-negative integer types for WMS
PositiveInt = Annotated[int, Field(gt=0)]
NonNegativeInt = Annotated[int, Field(ge=0)]

if TYPE_CHECKING:
    from datetime import datetime

    from flext_oracle_wms.constants import (
        OracleWMSAuthMethod,
        OracleWMSEntityType,
        OracleWMSPageMode,
        OracleWMSWriteMode,
    )

# ==============================================================================
# ORACLE WMS SPECIFIC TYPES
# ==============================================================================

# WMS Identifiers - using centralized WMSEntityName from flext-core

WMSCompanyCode = Annotated[
    str,
    StringConstraints(
        pattern=r"^[A-Z0-9*]{1,10}$",
        min_length=1,
        max_length=10,
    ),
]

WMSFacilityCode = Annotated[
    str,
    StringConstraints(
        pattern=r"^[A-Z0-9*]{1,10}$",
        min_length=1,
        max_length=10,
    ),
]

WMSItemID = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=50,
    ),
]

WMSLocationID = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=50,
    ),
]

WMSOrderNumber = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=50,
    ),
]

# WMS Field Mappings
WMSFieldName = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z][a-z0-9_]*$",
        min_length=1,
        max_length=128,
    ),
]

WMSFieldMapping = dict[WMSFieldName, WMSFieldName]

# Filter Types
WMSFilterValue = str | int | float | bool | list[Any]
WMSFilterCondition = dict[WMSFieldName, WMSFilterValue]
WMSFilters = dict[OracleWMSFilterOperator, WMSFilterCondition]

# Pagination Types
WMSPageToken = Annotated[str, Field(description="WMS pagination token")]
WMSPageSize = Annotated[PositiveInt, Field(ge=1, le=10000)]
WMSOffset = Annotated[NonNegativeInt, Field(ge=0)]

# Schema Types
WMSSchemaProperty = dict[str, Any]
WMSSchema = dict[str, WMSSchemaProperty]
WMSFlattenedSchema = dict[str, Any]

# Record Types
WMSRecord = dict[str, Any]
WMSRecordBatch = list[WMSRecord]
WMSFlattenedRecord = dict[str, Any]

# Response Types
WMSAPIResponse = dict[str, Any]
WMSEntityData = list[WMSRecord]


# ==============================================================================
# TYPED DICTS FOR STRUCTURED DATA
# ==============================================================================


class WMSConnectionInfo(TypedDict):
    """WMS connection information."""

    base_url: str
    api_version: str
    auth_method: OracleWMSAuthMethod
    username: str
    company_code: str
    facility_code: str


class WMSEntityInfo(TypedDict):
    """WMS entity information."""

    entity_name: OracleWMSEntityType
    display_name: str
    description: str
    primary_key: str
    replication_key: str | None
    schema: WMSSchema


class WMSStreamConfig(TypedDict):
    """WMS stream configuration."""

    entity_name: OracleWMSEntityType
    selected: bool
    replication_method: str
    replication_key: str | None
    filters: WMSFilters | None
    field_selection: list[str] | None


class WMSPaginationInfo(TypedDict):
    """WMS pagination information."""

    page_mode: OracleWMSPageMode
    page_size: int
    current_page: int
    total_pages: int | None
    has_next: bool
    next_token: str | None


class WMSRateLimitInfo(TypedDict):
    """WMS rate limiting information."""

    enabled: bool
    max_requests_per_minute: int
    current_requests: int
    reset_time: datetime
    delay_next_request: float


class WMSBatchInfo(TypedDict):
    """WMS batch processing information."""

    batch_size: int
    total_records: int
    processed_records: int
    failed_records: int
    current_batch: int
    total_batches: int


class WMSValidationResult(TypedDict):
    """WMS validation result."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    entity_name: str | None
    record_count: int


class WMSDiscoveryResult(TypedDict):
    """WMS discovery result."""

    entities: list[WMSEntityInfo]
    total_entities: int
    discovery_time: datetime
    api_version: str
    connection_info: WMSConnectionInfo


class WMSExecutionStats(TypedDict):
    """WMS execution statistics."""

    start_time: datetime
    end_time: datetime | None
    duration_seconds: float | None
    records_processed: int
    records_failed: int
    api_calls_made: int
    rate_limit_hits: int
    retries_attempted: int


class WMSErrorInfo(TypedDict):
    """WMS error information."""

    error_code: str
    error_message: str
    entity_name: str | None
    record_id: str | None
    timestamp: datetime
    retry_count: int
    recoverable: bool


# ==============================================================================
# CALLBACK TYPES
# ==============================================================================

type WMSProgressCallback = Callable[[int, int], None]  # (processed, total)
type WMSErrorCallback = Callable[[WMSErrorInfo], None]
type WMSValidationCallback = Callable[[WMSValidationResult], None]
type WMSDiscoveryCallback = Callable[[WMSDiscoveryResult], None]


# ==============================================================================
# CONFIGURATION TYPES
# ==============================================================================


class WMSFilterConfig(TypedDict, total=False):
    """WMS filter configuration."""

    enable_dynamic_filters: bool
    default_filters: WMSFilters
    filter_operators: list[OracleWMSFilterOperator]
    max_filter_conditions: int


class WMSSchemaConfig(TypedDict, total=False):
    """WMS schema configuration."""

    enable_flattening: bool
    flatten_max_depth: int
    flatten_separator: str
    enable_deflattening: bool
    preserve_original_schema: bool


class WMSPerformanceConfig(TypedDict, total=False):
    """WMS performance configuration."""

    page_size: int
    page_mode: OracleWMSPageMode
    timeout: float
    max_retries: int
    retry_delay: float
    enable_rate_limiting: bool
    max_requests_per_minute: int


class WMSTargetConfig(TypedDict, total=False):
    """WMS target configuration."""

    write_mode: OracleWMSWriteMode
    batch_size: int
    enable_validation: bool
    field_mappings: WMSFieldMapping
    conflict_resolution: str


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    # Response Types
    "WMSAPIResponse",
    "WMSBatchInfo",
    "WMSCompanyCode",
    # Typed Dicts
    "WMSConnectionInfo",
    "WMSDiscoveryCallback",
    "WMSDiscoveryResult",
    "WMSEntityData",
    "WMSEntityInfo",
    # WMS Specific Types
    "WMSEntityName",
    "WMSErrorCallback",
    "WMSErrorInfo",
    "WMSExecutionStats",
    "WMSFacilityCode",
    "WMSFieldMapping",
    "WMSFieldName",
    "WMSFilterCondition",
    # Configuration Types
    "WMSFilterConfig",
    # Filter Types
    "WMSFilterValue",
    "WMSFilters",
    "WMSFlattenedRecord",
    "WMSFlattenedSchema",
    "WMSItemID",
    "WMSLocationID",
    "WMSOffset",
    "WMSOrderNumber",
    "WMSPageSize",
    # Pagination Types
    "WMSPageToken",
    "WMSPaginationInfo",
    "WMSPerformanceConfig",
    # Callback Types
    "WMSProgressCallback",
    "WMSRateLimitInfo",
    # Record Types
    "WMSRecord",
    "WMSRecordBatch",
    "WMSSchema",
    "WMSSchemaConfig",
    # Schema Types
    "WMSSchemaProperty",
    "WMSStreamConfig",
    "WMSTargetConfig",
    "WMSValidationCallback",
    "WMSValidationResult",
]
