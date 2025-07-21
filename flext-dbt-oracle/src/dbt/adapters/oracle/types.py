"""Oracle DBT adapter types using flext-core standards.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Ultra-modern Python 3.13 types for DBT Oracle adapter with MAXIMUM flext-core
integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    # Define DBT-specific types not available in flext-core
    from typing import Annotated

    # Import available flext-core types and define missing ones
    from pydantic import Field, StringConstraints

    # Define missing types for DBT Oracle adapter
    NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
    DBTDatabaseName = Annotated[str, StringConstraints(min_length=1, max_length=128)]
    DBTSchemaName = Annotated[str, StringConstraints(min_length=1, max_length=128)]
    DBTTableName = Annotated[str, StringConstraints(min_length=1, max_length=128)]
    DBTMaterialization = Literal["table", "view", "incremental", "ephemeral"]
    Port = Annotated[int, Field(ge=1, le=65535)]
    PositiveInt = Annotated[int, Field(gt=0)]
    TimeoutSeconds = Annotated[int, Field(ge=1, le=3600)]

# ==============================================================================
# DBT ORACLE ADAPTER TYPES - Python 3.13 Enhanced
# ==============================================================================


class DBTOracleCredentials(TypedDict):
    """DBT Oracle credentials configuration using flext-core types."""

    # Connection parameters
    type: str  # Always "oracle"
    host: NonEmptyStr
    port: Port
    username: NonEmptyStr
    password: NonEmptyStr

    # Oracle-specific connection
    service_name: NonEmptyStr | None
    sid: NonEmptyStr | None
    protocol: str  # "tcp" or "tcps"

    # DBT schema configuration
    database: DBTDatabaseName
    schema: DBTSchemaName

    # Optional settings
    search_path: str | None
    nls_lang: str | None
    nls_date_format: str


class DBTOracleConnectionConfig(TypedDict):
    """DBT Oracle connection configuration using flext-core types."""

    # Connection pool settings
    pool_min_size: PositiveInt
    pool_max_size: PositiveInt
    pool_increment: PositiveInt

    # Timeout settings
    query_timeout: TimeoutSeconds
    connect_timeout: TimeoutSeconds

    # Performance settings
    fetch_size: PositiveInt
    retry_attempts: PositiveInt
    retry_delay: float

    # SSL settings
    ssl_server_dn_match: bool


class DBTOracleModelConfig(TypedDict):
    """DBT Oracle model configuration using flext-core types."""

    # Model identification
    name: DBTTableName
    schema: DBTSchemaName
    database: DBTDatabaseName

    # Materialization settings
    materialized: DBTMaterialization

    # Oracle-specific model settings
    table_type: str | None  # "HEAP", "IOT", etc.
    compression: str | None  # "BASIC", "OLTP", "QUERY", etc.
    parallel: PositiveInt | None

    # Incremental model settings
    unique_key: str | list[str] | None
    incremental_strategy: str | None  # "append", "merge", "delete+insert"

    # Partitioning Oracle-specific settings
    partition_by: str | None
    partition_type: str | None  # "RANGE", "LIST", "HASH"

    # Performance tuning
    indexes: list[str] | None
    grants: dict[str, list[str]] | None


class DBTOracleRelationConfig(TypedDict):
    """DBT Oracle relation configuration using flext-core types."""

    # Relation identification
    database: DBTDatabaseName
    schema: DBTSchemaName
    identifier: DBTTableName
    type: str  # "table", "view", "snapshot"

    # Oracle-specific relation metadata
    owner: str
    table_space: str | None
    created: datetime | None
    last_analyzed: datetime | None

    # Statistics
    num_rows: int | None
    blocks: int | None
    avg_row_len: int | None


class DBTOracleExecutionResult(TypedDict):
    """DBT Oracle execution result using flext-core types."""

    # Execution metadata
    sql: str
    execution_time_ms: float
    rows_affected: int

    # Oracle-specific execution info
    elapsed_time: float
    cpu_time: float | None
    logical_reads: int | None
    physical_reads: int | None

    # Error information
    success: bool
    error_message: str | None
    oracle_error_code: str | None


class DBTOracleSchemaInfo(TypedDict):
    """DBT Oracle schema information using flext-core types."""

    # Schema identification
    schema_name: DBTSchemaName
    owner: str

    # Schema metadata
    created: datetime
    default_tablespace: str | None
    temporary_tablespace: str | None

    # Privileges and settings
    profile: str | None
    account_status: str
    lock_date: datetime | None
    expiry_date: datetime | None


class DBTOracleColumnInfo(TypedDict):
    """DBT Oracle column information using flext-core types."""

    # Column identification
    column_name: str
    table_name: DBTTableName
    owner: str

    # Data type information
    data_type: str
    data_length: int | None
    data_precision: int | None
    data_scale: int | None

    # Column properties
    nullable: bool
    column_id: int
    default_value: str | None

    # Statistics
    num_distinct: int | None
    low_value: str | None
    high_value: str | None
    density: float | None

    # DBT-specific metadata
    description: str | None
    tests: list[str] | None


class DBTOracleTableInfo(TypedDict):
    """DBT Oracle table information using flext-core types."""

    # Table identification
    table_name: DBTTableName
    owner: str
    tablespace_name: str | None

    # Table metadata
    status: str  # "VALID", "UNUSABLE"
    num_rows: int | None
    blocks: int | None
    empty_blocks: int | None
    avg_space: int | None
    chain_cnt: int | None
    avg_row_len: int | None

    # Timing information
    created: datetime
    last_analyzed: datetime | None

    # Oracle-specific features
    compression: str | None  # "ENABLED", "DISABLED"
    compress_for: str | None  # "BASIC", "OLTP", "QUERY HIGH", etc.
    partitioned: bool
    temporary: bool
    cluster_name: str | None


class DBTOracleIndexInfo(TypedDict):
    """DBT Oracle index information using flext-core types."""

    # Index identification
    index_name: str
    table_name: DBTTableName
    owner: str

    # Index properties
    index_type: str  # "NORMAL", "BITMAP", "FUNCTION-BASED", etc.
    uniqueness: str  # "UNIQUE", "NONUNIQUE"
    status: str  # "VALID", "UNUSABLE"

    # Performance metadata
    num_rows: int | None
    leaf_blocks: int | None
    distinct_keys: int | None
    avg_leaf_blocks_per_key: float | None
    clustering_factor: int | None

    # Index columns
    columns: list[str]
    column_positions: list[int]
    descend_flags: list[str]  # "ASC", "DESC"


class DBTOracleCompilationResult(TypedDict):
    """DBT Oracle compilation result using flext-core types."""

    # Compiled SQL
    compiled_sql: str
    wrapped_sql: str | None

    # Model metadata
    model_name: str
    materialization: DBTMaterialization
    schema: DBTSchemaName

    # Compilation metadata
    compilation_time_ms: float
    dependencies: list[str]
    refs: list[str]
    sources: list[str]

    # Oracle-specific compilation info
    bind_variables: dict[str, str] | None
    hints: list[str] | None
    parallel_degree: PositiveInt | None


class DBTOracleTestResult(TypedDict):
    """DBT Oracle test result using flext-core types."""

    # Test identification
    test_name: str
    model_name: str
    test_type: str  # "not_null", "unique", "accepted_values", etc.

    # Test execution
    status: str  # "pass", "fail", "error", "skip"
    failures: int
    message: str | None

    # Timing
    execution_time_ms: float

    # Oracle-specific test metadata
    sql_query: str
    row_count_checked: int
    constraint_violated: str | None


# ==============================================================================
# TYPE EXPORTS - All types are already defined above
# ==============================================================================

# All DBT Oracle types are available for import directly from the classes above
# No type aliases needed as the classes are self-contained
