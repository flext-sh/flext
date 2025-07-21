"""DBT Oracle Adapter specific type definitions - Maximum flext-core integration.

This module provides DBT Oracle Adapter specific type definitions using flext-core as
the foundation. All common Oracle types are inherited from flext-core to ensure
consistency and eliminate code duplication across Oracle projects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal, TypedDict

from pydantic import Field, StringConstraints

# Import ALL Oracle types from flext-core (our single source of truth)

if TYPE_CHECKING:
    from collections.abc import Callable

    from flext_core.domain.typedefs import (
        OracleArraySize,
        OracleColumnName,
        # Configuration types
        OracleConnectionTimeout,
        OracleFetchSize,
        # Core Oracle types
        OracleHost,
        OracleIdentifier,
        OraclePassword,
        OraclePort,
        OracleQueryTimeout,
        OracleSchema,
        OracleServiceName,
        OracleSID,
        OracleTableName,
        OracleUsername,
        PositiveInt,
    )

# ==============================================================================
# DBT-SPECIFIC TYPES - Only types unique to DBT adapter operations
# ==============================================================================

# DBT Adapter and Connection Types
DBTAdapterType = Literal["oracle"]
DBTConnectionType = Literal["oracle"]
DBTProfileType = Literal["oracle"]

# DBT Materialization Types
DBTMaterialization = Literal["table", "view", "incremental", "snapshot", "ephemeral"]
DBTIncrementalStrategy = Literal["append", "merge", "delete+insert"]
DBTSnapshotStrategy = Literal["timestamp", "check"]

# DBT Thread and Execution Types
DBTThreadCount = Annotated[int, Field(ge=1, le=16, description="Number of DBT threads")]
DBTTargetName = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
        min_length=1,
        max_length=64,
        description="DBT target name",
    ),
]

# DBT Quoting and Identifier Management
DBTQuotePolicy = Literal["always", "never", "when_needed"]
DBTCaseSensitivity = Literal["preserve", "upper", "lower"]


class DBTIdentifierQuoting(TypedDict):
    """DBT identifier quoting configuration."""

    database: bool
    schema: bool
    identifier: bool


# DBT Model Configuration
class DBTModelConfig(TypedDict):
    """DBT model configuration."""

    materialized: DBTMaterialization
    unique_key: str | list[str] | None
    incremental_strategy: DBTIncrementalStrategy | None
    on_schema_change: Literal[
        "ignore",
        "fail",
        "append_new_columns",
        "sync_all_columns",
    ]
    full_refresh: bool
    persist_docs: dict[str, bool]
    pre_hook: str | list[str] | None
    post_hook: str | list[str] | None


# DBT Snapshot Configuration
class DBTSnapshotConfig(TypedDict):
    """DBT snapshot configuration."""

    strategy: DBTSnapshotStrategy
    unique_key: str | list[str]
    updated_at: str | None
    check_cols: list[str] | Literal["all"] | None
    invalidate_hard_deletes: bool
    target_schema: OracleSchema
    target_database: str | None


# Oracle-specific DBT Types
DBTOracleHint = Annotated[
    str,
    StringConstraints(
        pattern=r"^/\*\+.*\*/$",
        description="Oracle SQL hint in /*+ hint */ format for DBT queries",
    ),
]

DBTOracleTablespace = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=30,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_$#]*$",
        description="Oracle tablespace name",
    ),
]


# DBT Connection Profile Types
class DBTOracleProfile(TypedDict):
    """DBT Oracle connection profile."""

    type: DBTConnectionType
    host: OracleHost
    port: OraclePort
    user: OracleUsername
    password: OraclePassword
    service_name: OracleServiceName | None
    sid: OracleSID | None
    schema: OracleSchema
    database: str | None
    threads: DBTThreadCount
    keepalives_idle: int
    search_path: str | None
    sslmode: Literal["disable", "allow", "prefer", "require"]
    connection_timeout: OracleConnectionTimeout
    query_timeout: OracleQueryTimeout
    retry_on_database_errors: bool
    retry_all: bool


# DBT Catalog and Metadata Types
class DBTCatalogTable(TypedDict):
    """DBT catalog table metadata."""

    type: Literal["table", "view", "materialized_view"]
    schema: OracleSchema
    name: OracleTableName
    database: str | None
    comment: str | None
    owner: OracleUsername | None


class DBTCatalogColumn(TypedDict):
    """DBT catalog column metadata."""

    type: str
    index: int
    name: OracleColumnName
    comment: str | None


class DBTRelation(TypedDict):
    """DBT relation configuration."""

    database: str | None
    schema: OracleSchema
    identifier: OracleIdentifier
    type: Literal["table", "view", "external", "cte"]


# DBT Compilation and Execution Types
class DBTCompilerConfig(TypedDict):
    """DBT compiler configuration."""

    quote_policy: DBTIdentifierQuoting
    case_sensitivity: DBTCaseSensitivity
    dispatch_list: list[str]
    generate_docs: bool
    query_comment: str | None


class DBTMacroContext(TypedDict):
    """DBT macro execution context."""

    adapter: Any
    model: dict[str, Any]
    config: dict[str, Any]
    var: Callable[[str, Any], Any]
    ref: Callable[[str], Any]
    source: Callable[[str, str], Any]
    this: Any
    target: dict[str, Any]


# DBT Error and Logging Types
DBTErrorType = Literal[
    "compilation",
    "runtime",
    "validation",
    "connection",
    "dependency",
    "parsing",
]

DBTLogLevel = Literal["DEBUG", "INFO", "WARN", "ERROR"]


class DBTLogMessage(TypedDict):
    """DBT log message structure."""

    timestamp: str
    level: DBTLogLevel
    logger_name: str
    message: str
    extra: dict[str, Any]


# DBT Performance and Monitoring Types
class DBTExecutionStats(TypedDict):
    """DBT execution statistics."""

    node_id: str
    node_name: str
    resource_type: str
    status: Literal["success", "error", "skipped"]
    execution_time: float
    rows_affected: int | None
    bytes_processed: int | None
    query_id: str | None


class DBTRunResult(TypedDict):
    """DBT run result information."""

    unique_id: str
    error: str | None
    status: Literal["success", "error", "skipped", "fail"]
    execution_time: float
    thread_id: str
    timing: list[dict[str, Any]]
    adapter_response: dict[str, Any]
    message: str | None
    failures: int


# ==============================================================================
# COMPOSITE CONFIGURATION TYPES - For maximum code reduction
# ==============================================================================


# Complete DBT Oracle Configuration (combines all settings)
class DBTOracleCompleteConfig(TypedDict):
    """Complete DBT Oracle configuration."""

    type: DBTConnectionType
    host: OracleHost
    port: OraclePort
    user: OracleUsername
    password: OraclePassword
    service_name: OracleServiceName | None
    sid: OracleSID | None
    schema: OracleSchema
    database: str | None
    threads: DBTThreadCount
    connection_timeout: OracleConnectionTimeout
    query_timeout: OracleQueryTimeout
    keepalives_idle: int
    retry_on_database_errors: bool
    retry_all: bool
    quoting: DBTIdentifierQuoting
    case_sensitivity: DBTCaseSensitivity
    quote_policy: DBTQuotePolicy
    use_hints: bool
    default_tablespace: DBTOracleTablespace | None
    parallel_degree: PositiveInt | None
    enable_parallel_ddl: bool
    enable_parallel_dml: bool
    fetch_size: OracleFetchSize
    array_size: OracleArraySize
    connection_pool_size: PositiveInt
    log_level: DBTLogLevel
    enable_sql_logging: bool
    enable_timing: bool
    enable_row_counts: bool


# Environment-specific DBT Configuration
class DBTEnvironmentConfig(TypedDict):
    """Environment-specific DBT configuration."""

    development: DBTOracleCompleteConfig
    staging: DBTOracleCompleteConfig
    production: DBTOracleCompleteConfig


# DBT Project Configuration
class DBTProjectConfig(TypedDict):
    """DBT project configuration."""

    name: str
    version: str
    profile: str
    model_paths: list[str]
    analysis_paths: list[str]
    test_paths: list[str]
    seed_paths: list[str]
    macro_paths: list[str]
    snapshot_paths: list[str]
    docs_paths: list[str]
    target_path: str
    clean_targets: list[str]
    models: dict[str, Any]
    snapshots: dict[str, Any]
    seeds: dict[str, Any]
    vars: dict[str, Any]
