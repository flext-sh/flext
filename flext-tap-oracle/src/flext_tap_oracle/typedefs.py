"""Oracle Tap specific type definitions - Maximum flext-core integration.

This module provides Oracle Tap specific type definitions using flext-core as the
foundation. All common Oracle types are inherited from flext-core to ensure
consistency and eliminate code duplication across Oracle projects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, TypedDict

from pydantic import StringConstraints

# Import ALL Oracle types from flext-core (our single source of truth)

if TYPE_CHECKING:
    from flext_core.domain.typedefs import (
        NonEmptyStr,
        OracleArraySize,
        OracleFetchSize,
        # Core Oracle types
        OracleHost,
        OraclePassword,
        OraclePort,
        OracleQueryTimeout,
        OracleSchema,
        OracleServiceName,
        OracleSID,
        OracleUsername,
        PositiveInt,
        # Singer Oracle types
        SingerBatchSize,
        SingerMaxRecords,
        SingerParallelStreams,
        SingerReplicationMethod,
        SingerStateInterval,
        TimeoutSeconds,
    )

# ==============================================================================
# TAP-SPECIFIC TYPES - Only types unique to tap operations
# ==============================================================================

# Discovery and Schema Detection Types
TapDiscoveryMode = Literal["automatic", "manual", "catalog_only"]
TapTablePattern = Annotated[
    str,
    StringConstraints(
        min_length=1, max_length=128, description="SQL LIKE pattern for table discovery"
    ),
]
TapSchemaPattern = Annotated[
    str,
    StringConstraints(
        min_length=1, max_length=64, description="SQL LIKE pattern for schema discovery"
    ),
]


# Stream Selection Types
class TapStreamSelection(TypedDict):
    selected: bool
    replication_method: SingerReplicationMethod
    replication_key: str | None
    key_properties: list[str]
    forced_replication_method: SingerReplicationMethod | None


class TapCatalogEntry(TypedDict):
    tap_stream_id: str
    stream: str
    table_name: str
    schema: dict[str, any]
    metadata: list[dict[str, any]]


# Incremental Replication Types
TapBookmarkType = Literal["timestamp", "integer", "date", "datetime"]
TapBookmarkValue = str | int | float  # Can be various types depending on column


class TapStateMessage(TypedDict):
    bookmarks: dict[str, dict[str, TapBookmarkValue]]
    currently_syncing: str | None


# Connection Pool Types (Tap-specific configuration)
class TapConnectionPoolConfig(TypedDict):
    size: PositiveInt
    max_overflow: PositiveInt
    timeout: TimeoutSeconds
    recycle: TimeoutSeconds
    pre_ping: bool


# Performance Tuning Types
TapPerformanceProfile = Literal["development", "staging", "production", "high_volume"]


class TapCircuitBreakerConfig(TypedDict):
    failure_threshold: PositiveInt
    timeout: TimeoutSeconds
    expected_exception: type[Exception] | None


# Schema Flattening Types (Tap-specific feature)
class TapFlatteningConfig(TypedDict):
    enabled: bool
    max_depth: PositiveInt
    separator: NonEmptyStr
    preserve_arrays: bool
    flatten_objects: bool


# Oracle Query Optimization Types
TapQueryHint = Annotated[
    str,
    StringConstraints(
        pattern=r"^/\*\+.*\*/$", description="Oracle SQL hint in /*+ hint */ format"
    ),
]


class TapQueryOptimization(TypedDict):
    use_hints: bool
    hints: list[TapQueryHint]
    parallel_degree: PositiveInt | None
    use_index: str | None


# Column Metadata for Discovery
class TapColumnMetadata(TypedDict):
    column_name: str
    data_type: str
    is_nullable: bool
    column_default: str | None
    character_maximum_length: int | None
    numeric_precision: int | None
    numeric_scale: int | None
    is_primary_key: bool
    is_foreign_key: bool


class TapTableMetadata(TypedDict):
    table_name: str
    schema_name: str
    table_type: Literal["TABLE", "VIEW", "MATERIALIZED VIEW"]
    row_count: int | None
    columns: list[TapColumnMetadata]
    primary_keys: list[str]
    foreign_keys: list[dict[str, str]]


# ==============================================================================
# COMPOSITE CONFIGURATION TYPES - For maximum code reduction
# ==============================================================================


# Complete Tap Configuration (combines all settings)
class TapOracleCompleteConfig(TypedDict):
    host: OracleHost
    port: OraclePort
    service_name: OracleServiceName | None
    sid: OracleSID | None
    username: OracleUsername
    password: OraclePassword
    schema: OracleSchema | None
    batch_size: SingerBatchSize
    max_parallel_streams: SingerParallelStreams
    connection_pool_size: PositiveInt
    query_timeout: OracleQueryTimeout
    fetch_size: OracleFetchSize
    array_size: OracleArraySize
    discovery_mode: TapDiscoveryMode
    table_pattern: TapTablePattern | None
    schema_pattern: TapSchemaPattern | None
    replication_method: SingerReplicationMethod
    max_records: SingerMaxRecords
    state_interval: SingerStateInterval
    flattening: TapFlatteningConfig
    circuit_breaker: TapCircuitBreakerConfig
    performance_profile: TapPerformanceProfile
    query_optimization: TapQueryOptimization
    log_level: str
    enable_sql_logging: bool
    enable_metrics: bool


# Environment-specific Configuration
class TapEnvironmentConfig(TypedDict):
    development: TapOracleCompleteConfig
    staging: TapOracleCompleteConfig
    production: TapOracleCompleteConfig
