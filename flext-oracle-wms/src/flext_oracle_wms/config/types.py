"""Oracle WMS Configuration Types - Unified typing system using flext-core.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

This module imports from the unified typing system in flext-core and defines
Oracle WMS-specific configuration types using modern Python 3.13 patterns.
"""

from __future__ import annotations

from typing import Annotated, Literal, TypedDict

# Import ALL types from unified core typing system - eliminate duplication
from flext_core.domain.shared_types import (
    URL,
    ApiKey,
    BatchSize,
    ConfigurationKey,
    ConfigurationValue,
    CpuPercent,
    DatabaseName,
    DatabaseURL,
    DirPath,
    DiskMB,
    DurationSeconds,
    EntityId,
    Environment,
    FileName,
    FilePath,
    FileSize,
    Json,
    JsonDict,
    JsonList,
    JsonSchema,
    LogLevel,
    MemoryMB,
    NonEmptyStr,
    NonNegativeInt,
    OracleWMSAuthMethod,
    OracleWMSEntityType,
    OracleWMSFilterOperator,
    OracleWMSPageMode,
    OracleWMSWriteMode,
    Password,
    Port,
    PositiveInt,
    ProjectName,
    RetryCount,
    RetryDelay,
    ServiceResult,
    SingerBookmark,
    SingerCatalog,
    SingerRecordCount,
    SingerSchemaName,
    SingerState,
    SingerStreamName,
    TimeoutSeconds,
    TimestampISO,
    Token,
    Username,
    Version,
    WMSCompanyCode,
    WMSFacilityCode,
    WMSFieldMapping,
    WMSFieldName,
    WMSItemID,
    WMSLocationID,
    WMSOrderNumber,
)
from pydantic import Field

# ==============================================================================
# ORACLE WMS SPECIFIC TYPE ALIASES - Building on unified types
# ==============================================================================

# Oracle WMS filters (complex type not in core)
type WMSFilters = dict[WMSFieldName, dict[OracleWMSFilterOperator, str | list[str]]]

# ==============================================================================
# ORACLE WMS CONFIGURATION-SPECIFIC TYPES - Using unified types as foundation
# ==============================================================================

# Oracle WMS API configuration types (aliases from unified types for clarity)
type OracleWMSApiUrl = URL
type OracleWMSApiPort = Port
type OracleWMSApiTimeout = TimeoutSeconds
type OracleWMSApiVersion = Annotated[
    str,
    Field(min_length=1, max_length=10, description="Oracle WMS API version"),
]

# Oracle WMS authentication configuration types (aliases)
type OracleWMSUsername = Username
type OracleWMSPassword = Password
type OracleWMSToken = Token
type OracleWMSApiKey = ApiKey

# Oracle WMS connection configuration types (aliases)
type OracleWMSConnectionTimeout = TimeoutSeconds
type OracleWMSConnectionRetries = RetryCount
type OracleWMSConnectionRetryDelay = RetryDelay

# Oracle WMS batch configuration types (aliases)
type OracleWMSBatchSize = BatchSize
type OracleWMSBatchTimeout = TimeoutSeconds
type OracleWMSBatchRetries = RetryCount

# Oracle WMS pagination configuration types
type OracleWMSPageSize = Annotated[
    int,
    Field(ge=1, le=10000, description="Oracle WMS page size"),
]
type OracleWMSPageOffset = Annotated[
    int,
    Field(ge=0, description="Oracle WMS page offset"),
]

# Oracle WMS schema configuration types
type OracleWMSSchemaTimeout = TimeoutSeconds
type OracleWMSSchemaRetries = RetryCount
type OracleWMSSchemaDiscovery = Annotated[
    bool,
    Field(description="Enable Oracle WMS schema discovery"),
]

# Oracle WMS flattening configuration types
type OracleWMSFlattenEnabled = Annotated[
    bool,
    Field(description="Enable Oracle WMS data flattening"),
]
type OracleWMSFlattenMaxDepth = Annotated[
    int,
    Field(ge=1, le=10, description="Maximum flattening depth"),
]
type OracleWMSFlattenSeparator = Annotated[
    str,
    Field(min_length=1, max_length=10, description="Flattening separator"),
]

# Oracle WMS filtering configuration types
type OracleWMSFilterEnabled = Annotated[
    bool,
    Field(description="Enable Oracle WMS filtering"),
]
type OracleWMSFilterMaxConditions = Annotated[
    int,
    Field(ge=1, le=100, description="Maximum filter conditions"),
]

# Oracle WMS rate limiting configuration types
type OracleWMSRateLimitEnabled = Annotated[
    bool,
    Field(description="Enable Oracle WMS rate limiting"),
]
type OracleWMSRateLimitRPM = Annotated[
    int,
    Field(ge=1, le=10000, description="Requests per minute limit"),
]
type OracleWMSRateLimitDelay = Annotated[
    float,
    Field(ge=0.0, le=60.0, description="Minimum delay between requests"),
]

# Oracle WMS monitoring configuration types
type OracleWMSMonitoringEnabled = Annotated[
    bool,
    Field(description="Enable Oracle WMS monitoring"),
]
type OracleWMSMonitoringInterval = Annotated[
    int,
    Field(ge=1, le=3600, description="Monitoring interval in seconds"),
]
type OracleWMSHealthCheckEnabled = Annotated[
    bool,
    Field(description="Enable Oracle WMS health checks"),
]
type OracleWMSHealthCheckInterval = Annotated[
    int,
    Field(ge=1, le=3600, description="Health check interval in seconds"),
]

# ==============================================================================
# ORACLE WMS CONNECTION CONFIGURATION TYPEDDICTS
# ==============================================================================


class OracleWMSConnectionConfig(TypedDict):
    """Oracle WMS connection configuration structure using flext-core types."""

    # Connection identification
    connection_name: NonEmptyStr
    environment: Environment

    # API configuration
    base_url: OracleWMSApiUrl
    api_version: OracleWMSApiVersion
    api_port: OracleWMSApiPort | None
    api_timeout: OracleWMSApiTimeout

    # Authentication configuration
    auth_method: OracleWMSAuthMethod
    username: OracleWMSUsername
    password: OracleWMSPassword | None
    token: OracleWMSToken | None
    api_key: OracleWMSApiKey | None

    # Company and facility configuration
    company_code: WMSCompanyCode
    facility_code: WMSFacilityCode

    # Connection settings
    connection_timeout: OracleWMSConnectionTimeout
    connection_retries: OracleWMSConnectionRetries
    connection_retry_delay: OracleWMSConnectionRetryDelay

    # SSL/TLS configuration
    ssl_enabled: bool
    ssl_verify: bool
    ssl_cert_path: FilePath | None
    ssl_key_path: FilePath | None

    # Proxy configuration
    proxy_enabled: bool
    proxy_url: URL | None
    proxy_username: Username | None
    proxy_password: Password | None

    # Keep-alive configuration
    keep_alive: bool
    keep_alive_timeout: TimeoutSeconds
    connection_pool_size: PositiveInt


class OracleWMSEntityConfig(TypedDict):
    """Oracle WMS entity configuration structure using flext-core types."""

    # Entity identification
    entity_name: OracleWMSEntityType
    entity_enabled: bool
    entity_priority: PositiveInt

    # Entity replication configuration
    replication_method: Literal["FULL_TABLE", "INCREMENTAL", "LOG_BASED"]
    replication_key: WMSFieldName | None
    replication_key_value: str | None
    primary_key: WMSFieldName

    # Entity selection configuration
    selected_fields: list[WMSFieldName] | None
    excluded_fields: list[WMSFieldName] | None
    field_mappings: WMSFieldMapping | None

    # Entity filtering configuration
    filters: WMSFilters | None
    filter_enabled: bool
    dynamic_filters: bool

    # Entity schema configuration
    schema_discovery: bool
    schema_validation: bool
    schema_evolution: bool
    schema_cache_ttl: TimeoutSeconds

    # Entity pagination configuration
    page_mode: OracleWMSPageMode
    page_size: OracleWMSPageSize
    max_pages: PositiveInt | None

    # Entity transformation configuration
    flatten_enabled: bool
    flatten_max_depth: int
    flatten_separator: str
    deflattening_enabled: bool


class OracleWMSSchemaConfig(TypedDict):
    """Oracle WMS schema configuration structure using flext-core types."""

    # Schema discovery configuration
    discovery_enabled: OracleWMSSchemaDiscovery
    discovery_timeout: OracleWMSSchemaTimeout
    discovery_retries: OracleWMSSchemaRetries
    discovery_cache_ttl: TimeoutSeconds

    # Schema validation configuration
    validation_enabled: bool
    validation_strict: bool
    validation_timeout: TimeoutSeconds
    validation_retries: RetryCount

    # Schema evolution configuration
    evolution_enabled: bool
    evolution_strategy: Literal["strict", "permissive", "auto"]
    evolution_backup: bool
    evolution_rollback: bool

    # Schema flattening configuration
    flattening_enabled: OracleWMSFlattenEnabled
    flattening_max_depth: OracleWMSFlattenMaxDepth
    flattening_separator: OracleWMSFlattenSeparator
    flattening_preserve_types: bool

    # Schema deflattening configuration
    deflattening_enabled: bool
    deflattening_strategy: Literal["strict", "permissive", "auto"]
    deflattening_validation: bool
    deflattening_cache: bool

    # Schema caching configuration
    cache_enabled: bool
    cache_ttl: TimeoutSeconds
    cache_max_size: PositiveInt
    cache_compression: bool


class OracleWMSPerformanceConfig(TypedDict):
    """Oracle WMS performance configuration structure using flext-core types."""

    # Batch processing configuration
    batch_enabled: bool
    batch_size: OracleWMSBatchSize
    batch_timeout: OracleWMSBatchTimeout
    batch_retries: OracleWMSBatchRetries
    batch_parallelism: PositiveInt

    # Pagination configuration
    pagination_enabled: bool
    pagination_mode: OracleWMSPageMode
    pagination_size: OracleWMSPageSize
    pagination_offset: OracleWMSPageOffset
    pagination_max_pages: PositiveInt | None

    # Rate limiting configuration
    rate_limit_enabled: OracleWMSRateLimitEnabled
    rate_limit_rpm: OracleWMSRateLimitRPM
    rate_limit_delay: OracleWMSRateLimitDelay
    rate_limit_burst: PositiveInt

    # Timeout configuration
    request_timeout: TimeoutSeconds
    connection_timeout: TimeoutSeconds
    read_timeout: TimeoutSeconds
    write_timeout: TimeoutSeconds

    # Retry configuration
    retry_enabled: bool
    retry_count: RetryCount
    retry_delay: RetryDelay
    retry_exponential_backoff: bool
    retry_max_delay: TimeoutSeconds

    # Concurrency configuration
    concurrency_enabled: bool
    concurrency_max_workers: PositiveInt
    concurrency_queue_size: PositiveInt
    concurrency_timeout: TimeoutSeconds

    # Memory configuration
    memory_limit: MemoryMB | None
    memory_buffer_size: MemoryMB
    memory_gc_threshold: PositiveInt

    # Disk configuration
    disk_limit: DiskMB | None
    disk_cache_enabled: bool
    disk_cache_path: DirPath | None
    disk_cache_ttl: TimeoutSeconds


class OracleWMSFilterConfig(TypedDict):
    """Oracle WMS filter configuration structure using flext-core types."""

    # Filter general configuration
    filter_enabled: OracleWMSFilterEnabled
    filter_max_conditions: OracleWMSFilterMaxConditions
    filter_validation: bool
    filter_optimization: bool

    # Filter operators configuration
    supported_operators: list[OracleWMSFilterOperator]
    default_operator: OracleWMSFilterOperator
    case_sensitive: bool
    null_handling: Literal["ignore", "include", "exclude"]

    # Filter fields configuration
    filterable_fields: list[WMSFieldName] | None
    non_filterable_fields: list[WMSFieldName] | None
    field_type_validation: bool
    field_range_validation: bool

    # Filter performance configuration
    filter_indexing: bool
    filter_caching: bool
    filter_cache_ttl: TimeoutSeconds
    filter_parallel_processing: bool

    # Filter transformation configuration
    filter_normalization: bool
    filter_standardization: bool
    filter_encoding: str
    filter_locale: str

    # Filter logging configuration
    filter_logging: bool
    filter_log_level: LogLevel
    filter_log_file: FilePath | None
    filter_audit_trail: bool


class OracleWMSMonitoringConfig(TypedDict):
    """Oracle WMS monitoring configuration structure using flext-core types."""

    # Monitoring general configuration
    monitoring_enabled: OracleWMSMonitoringEnabled
    monitoring_interval: OracleWMSMonitoringInterval
    monitoring_timeout: TimeoutSeconds
    monitoring_retries: RetryCount

    # Health check configuration
    health_check_enabled: OracleWMSHealthCheckEnabled
    health_check_interval: OracleWMSHealthCheckInterval
    health_check_timeout: TimeoutSeconds
    health_check_retries: RetryCount

    # Metrics configuration
    metrics_enabled: bool
    metrics_collection_interval: PositiveInt
    metrics_retention_period: PositiveInt
    metrics_export_enabled: bool
    metrics_export_format: Literal["json", "csv", "parquet"]

    # Alerting configuration
    alerting_enabled: bool
    alerting_channels: list[str]
    alerting_severity_levels: list[str]
    alerting_rate_limit: PositiveInt

    # Logging configuration
    logging_enabled: bool
    logging_level: LogLevel
    logging_file: FilePath | None
    logging_rotation: bool
    logging_retention_days: PositiveInt

    # Performance monitoring configuration
    performance_monitoring: bool
    performance_thresholds: dict[str, float]
    performance_alerting: bool
    performance_optimization: bool

    # Resource monitoring configuration
    resource_monitoring: bool
    resource_thresholds: dict[str, float]
    resource_alerting: bool
    resource_limits_enforcement: bool


class OracleWMSTargetConfig(TypedDict):
    """Oracle WMS target configuration structure using flext-core types."""

    # Target identification
    target_name: NonEmptyStr
    target_type: Literal["oracle_wms"]
    target_version: Version

    # Target write configuration
    write_mode: OracleWMSWriteMode
    write_batch_size: BatchSize
    write_timeout: TimeoutSeconds
    write_retries: RetryCount

    # Target validation configuration
    validation_enabled: bool
    validation_strict: bool
    validation_timeout: TimeoutSeconds
    validation_on_error: Literal["skip", "stop", "continue"]

    # Target transformation configuration
    transform_enabled: bool
    transform_mappings: WMSFieldMapping | None
    transform_validation: bool
    transform_rollback: bool

    # Target conflict resolution configuration
    conflict_resolution: Literal["ignore", "update", "error"]
    conflict_detection: bool
    conflict_logging: bool
    conflict_notification: bool

    # Target performance configuration
    performance_mode: Literal["speed", "accuracy", "balanced"]
    performance_parallel: bool
    performance_buffer_size: PositiveInt
    performance_compression: bool

    # Target monitoring configuration
    monitoring_enabled: bool
    monitoring_interval: PositiveInt
    monitoring_metrics: list[str]
    monitoring_alerting: bool

    # Target backup configuration
    backup_enabled: bool
    backup_strategy: Literal["full", "incremental", "differential"]
    backup_retention: PositiveInt
    backup_compression: bool


# ==============================================================================
# ORACLE WMS SINGER TAP CONFIGURATION TYPEDDICTS
# ==============================================================================


class OracleWMSTapConfig(TypedDict):
    """Oracle WMS tap configuration structure using flext-core types."""

    # Tap identification
    tap_name: NonEmptyStr
    tap_type: Literal["tap-oracle-wms"]
    tap_version: Version

    # Tap connection configuration
    connection: OracleWMSConnectionConfig

    # Tap entities configuration
    entities: dict[str, OracleWMSEntityConfig]
    entities_selection: list[OracleWMSEntityType]
    entities_exclusion: list[OracleWMSEntityType]

    # Tap schema configuration
    schema: OracleWMSSchemaConfig

    # Tap performance configuration
    performance: OracleWMSPerformanceConfig

    # Tap filtering configuration
    filters: OracleWMSFilterConfig

    # Tap monitoring configuration
    monitoring: OracleWMSMonitoringConfig

    # Tap Singer configuration
    singer_catalog: SingerCatalog | None
    singer_state: SingerState | None
    singer_bookmarks: dict[str, SingerBookmark]
    singer_properties: dict[str, dict[str, str]]

    # Tap advanced configuration
    advanced_features: dict[str, bool]
    advanced_settings: dict[str, str]
    advanced_tuning: dict[str, float]


class OracleWMSTargetFullConfig(TypedDict):
    """Oracle WMS target full configuration structure using flext-core types."""

    # Target identification
    target_name: NonEmptyStr
    target_type: Literal["target-oracle-wms"]
    target_version: Version

    # Target connection configuration
    connection: OracleWMSConnectionConfig

    # Target write configuration
    target: OracleWMSTargetConfig

    # Target schema configuration
    schema: OracleWMSSchemaConfig

    # Target performance configuration
    performance: OracleWMSPerformanceConfig

    # Target monitoring configuration
    monitoring: OracleWMSMonitoringConfig

    # Target Singer configuration
    singer_schema: JsonSchema | None
    singer_key_properties: list[str]
    singer_bookmark_properties: list[str]

    # Target advanced configuration
    advanced_features: dict[str, bool]
    advanced_settings: dict[str, str]
    advanced_tuning: dict[str, float]


# ==============================================================================
# COMPLETE ORACLE WMS CONFIGURATION
# ==============================================================================


class FlextOracleWMSConfig(TypedDict):
    """Complete FLEXT Oracle WMS configuration using flext-core types."""

    # Project information
    project_name: ProjectName
    project_version: Version
    environment: Environment

    # Core Oracle WMS configurations
    connection: OracleWMSConnectionConfig
    entities: dict[str, OracleWMSEntityConfig]
    schema: OracleWMSSchemaConfig
    performance: OracleWMSPerformanceConfig
    filters: OracleWMSFilterConfig
    monitoring: OracleWMSMonitoringConfig

    # Singer configurations
    tap_config: OracleWMSTapConfig
    target_config: OracleWMSTargetFullConfig

    # Global settings
    global_timeout: TimeoutSeconds
    global_retries: RetryCount
    global_log_level: LogLevel
    global_monitoring: bool

    # Feature flags
    features: dict[str, bool]

    # Advanced settings
    advanced: dict[str, str]


# ==============================================================================
# ENVIRONMENT-SPECIFIC CONFIGURATIONS
# ==============================================================================


class DevelopmentOracleWMSConfig(TypedDict):
    """Development environment Oracle WMS configuration."""

    debug: bool
    verbose_logging: bool
    fast_discovery: bool
    disable_validation: bool
    enable_debug_plugins: bool
    hot_reload: bool
    log_level: LogLevel
    monitoring_interval: int
    health_check_interval: int
    performance_mode: Literal["debug"]


class ProductionOracleWMSConfig(TypedDict):
    """Production environment Oracle WMS configuration."""

    debug: bool
    strict_validation: bool
    monitoring_enabled: bool
    health_checks_enabled: bool
    alerting_enabled: bool
    performance_optimization: bool
    log_level: LogLevel
    resource_limits_enforced: bool
    security_enabled: bool
    audit_logging: bool
    performance_mode: Literal["production"]


class TestingOracleWMSConfig(TypedDict):
    """Testing environment Oracle WMS configuration."""

    debug: bool
    test_mode: bool
    mock_enabled: bool
    disable_external_calls: bool
    in_memory_processing: bool
    fast_execution: bool
    predictable_behavior: bool
    simplified_validation: bool
    log_level: LogLevel
    disable_telemetry: bool
    performance_mode: Literal["test"]


# ==============================================================================
# TYPE ALIASES FOR MAXIMUM CODE REDUCTION
# ==============================================================================

# Configuration aggregates for simplified usage
type OracleWMSConfiguration = FlextOracleWMSConfig
type OracleWMSConnectionConfiguration = OracleWMSConnectionConfig
type OracleWMSEntityConfiguration = OracleWMSEntityConfig
type OracleWMSSchemaConfiguration = OracleWMSSchemaConfig

# Performance configurations
type OracleWMSPerformanceConfiguration = OracleWMSPerformanceConfig
type OracleWMSFilterConfiguration = OracleWMSFilterConfig
type OracleWMSMonitoringConfiguration = OracleWMSMonitoringConfig
type OracleWMSTargetConfiguration = OracleWMSTargetConfig

# Singer configurations
type OracleWMSTapConfiguration = OracleWMSTapConfig
type OracleWMSTargetFullConfiguration = OracleWMSTargetFullConfig

# Environment configurations
type DevOracleWMSConfig = DevelopmentOracleWMSConfig
type ProdOracleWMSConfig = ProductionOracleWMSConfig
type TestOracleWMSConfig = TestingOracleWMSConfig

# ==============================================================================
# EXPORT PUBLIC API
# ==============================================================================

# ==============================================================================
# EXPORTS - ALL ORACLE WMS TYPES
# ==============================================================================

__all__ = [
    # Core types re-exported from unified system
    "URL",
    "ApiKey",
    "BatchSize",
    "ConfigurationKey",
    "ConfigurationValue",
    "CpuPercent",
    "DatabaseName",
    "DatabaseURL",
    "DevOracleWMSConfig",
    # Environment configurations
    "DevelopmentOracleWMSConfig",
    "DirPath",
    "DiskMB",
    "DurationSeconds",
    "EntityId",
    "Environment",
    "FileName",
    "FilePath",
    "FileSize",
    "FlextOracleWMSConfig",
    "Json",
    "JsonDict",
    "JsonList",
    "JsonSchema",
    "LogLevel",
    "MemoryMB",
    "NonEmptyStr",
    "NonNegativeInt",
    "OracleWMSApiKey",
    "OracleWMSApiPort",
    "OracleWMSApiTimeout",
    "OracleWMSApiUrl",
    "OracleWMSApiVersion",
    "OracleWMSAuthMethod",
    "OracleWMSBatchRetries",
    "OracleWMSBatchSize",
    "OracleWMSBatchTimeout",
    # Type aliases
    "OracleWMSConfiguration",
    # Configuration structures
    "OracleWMSConnectionConfig",
    "OracleWMSConnectionConfiguration",
    "OracleWMSConnectionRetries",
    "OracleWMSConnectionRetryDelay",
    "OracleWMSConnectionTimeout",
    "OracleWMSEntityConfig",
    "OracleWMSEntityConfiguration",
    "OracleWMSEntityType",
    "OracleWMSFilterConfig",
    "OracleWMSFilterConfiguration",
    "OracleWMSFilterEnabled",
    "OracleWMSFilterMaxConditions",
    "OracleWMSFilterOperator",
    "OracleWMSFlattenEnabled",
    "OracleWMSFlattenMaxDepth",
    "OracleWMSFlattenSeparator",
    "OracleWMSHealthCheckEnabled",
    "OracleWMSHealthCheckInterval",
    "OracleWMSMonitoringConfig",
    "OracleWMSMonitoringConfiguration",
    "OracleWMSMonitoringEnabled",
    "OracleWMSMonitoringInterval",
    "OracleWMSPageMode",
    "OracleWMSPageOffset",
    "OracleWMSPageSize",
    "OracleWMSPassword",
    "OracleWMSPerformanceConfig",
    "OracleWMSPerformanceConfiguration",
    "OracleWMSRateLimitDelay",
    "OracleWMSRateLimitEnabled",
    "OracleWMSRateLimitRPM",
    "OracleWMSSchemaConfig",
    "OracleWMSSchemaConfiguration",
    "OracleWMSSchemaDiscovery",
    "OracleWMSSchemaRetries",
    "OracleWMSSchemaTimeout",
    "OracleWMSTapConfig",
    "OracleWMSTapConfiguration",
    "OracleWMSTargetConfig",
    "OracleWMSTargetConfiguration",
    "OracleWMSTargetFullConfig",
    "OracleWMSTargetFullConfiguration",
    "OracleWMSToken",
    "OracleWMSUsername",
    "OracleWMSWriteMode",
    "Password",
    "Port",
    "PositiveInt",
    "ProdOracleWMSConfig",
    "ProductionOracleWMSConfig",
    "ProjectName",
    "RetryCount",
    "RetryDelay",
    "ServiceResult",
    "SingerBookmark",
    "SingerCatalog",
    "SingerRecordCount",
    "SingerSchemaName",
    "SingerState",
    "SingerStreamName",
    "TestOracleWMSConfig",
    "TestingOracleWMSConfig",
    "TimeoutSeconds",
    "TimestampISO",
    "Token",
    "Username",
    "Version",
    "WMSCompanyCode",
    "WMSFacilityCode",
    "WMSFieldMapping",
    "WMSFieldName",
    # Oracle WMS specific types
    "WMSFilters",
    "WMSItemID",
    "WMSLocationID",
    "WMSOrderNumber",
]
