"""DBT Oracle Adapter Constants - Maximum flext-core integration with zero duplication.

This module provides DBT Oracle adapter specific constants using flext-core patterns.
All Oracle DB constants are inherited from flext-core to ensure consistency
and eliminate code duplication across Oracle projects.
"""

from __future__ import annotations

from typing import ClassVar, Final

# Import all shared Oracle constants from flext-core


# Define Oracle-specific constants locally
class OracleDBConstants:
    """Oracle database constants."""

    DEFAULT_PORT: Final = 1521
    DEFAULT_SERVICE_NAME: Final = "XE"
    DEFAULT_SCHEMA: Final = "SYSTEM"
    DEFAULT_ENCODING: Final = "utf-8"
    DEFAULT_PROTOCOL: Final = "tcp"
    DEFAULT_TIMEOUT: Final = 30


class OracleDefaults:
    """Oracle default values."""

    CONNECTION_TIMEOUT: Final = 30
    DEFAULT_CONNECT_TIMEOUT: Final = 30
    QUERY_TIMEOUT: Final = 300
    POOL_SIZE: Final = 5
    POOL_MAX_OVERFLOW: Final = 10
    BATCH_SIZE: Final = 1000


class OracleLimits:
    """Oracle limits and constraints."""

    MAX_IDENTIFIER_LENGTH: Final = 128
    MAX_VARCHAR_LENGTH: Final = 4000
    MAX_BATCH_SIZE: Final = 10000
    MIN_BATCH_SIZE: Final = 1


class DBTOracleConstants:
    """DBT Oracle adapter constants."""

    DEFAULT_BATCH_SIZE: Final = 1000
    MAX_BATCH_SIZE: Final = 10000
    DEFAULT_SCHEMA: Final = "DBT"
    DEFAULT_THREADS: Final = 4
    DEFAULT_DBT_TIMEOUT: Final = 300


class DBTOracleAdapterConstants:
    """DBT Oracle Adapter specific constants following flext-core patterns."""

    # ==============================================================================
    # DBT ADAPTER TYPE AND VERSION
    # ==============================================================================

    ADAPTER_TYPE: Final = "oracle"
    DBT_VERSION_MIN: Final = "1.6.0"
    DBT_VERSION_MAX: Final = "1.8.x"
    DBT_VERSION_RECOMMENDED: Final = "1.8.0"

    # ==============================================================================
    # ORACLE CONNECTION - Use flext-core Oracle constants exclusively
    # ==============================================================================

    # Port and Protocol
    DEFAULT_PORT: Final = OracleDBConstants.DEFAULT_PORT
    DEFAULT_SERVICE_NAME: Final = OracleDBConstants.DEFAULT_SERVICE_NAME
    DEFAULT_PROTOCOL: Final = OracleDBConstants.DEFAULT_PROTOCOL
    PROTOCOL_TCP: Final = "tcp"
    PROTOCOL_TCPS: Final = "tcps"
    VALID_PROTOCOLS: ClassVar[set[str]] = {PROTOCOL_TCP, PROTOCOL_TCPS}

    # Timeouts
    DEFAULT_TIMEOUT: Final = OracleDBConstants.DEFAULT_TIMEOUT
    DEFAULT_CONNECT_TIMEOUT: Final = OracleDefaults.CONNECTION_TIMEOUT
    DEFAULT_QUERY_TIMEOUT: Final = DBTOracleConstants.DEFAULT_DBT_TIMEOUT
    MAX_TIMEOUT: Final = 600

    # ==============================================================================
    # DBT MATERIALIZATIONS - Standard DBT materializations
    # ==============================================================================

    MATERIALIZATION_TABLE: Final = "table"
    MATERIALIZATION_VIEW: Final = "view"
    MATERIALIZATION_INCREMENTAL: Final = "incremental"
    MATERIALIZATION_SNAPSHOT: Final = "snapshot"
    MATERIALIZATION_EPHEMERAL: Final = "ephemeral"
    DEFAULT_MATERIALIZATION: Final = "table"
    VALID_MATERIALIZATIONS: ClassVar[set[str]] = {
        MATERIALIZATION_TABLE,
        MATERIALIZATION_VIEW,
        MATERIALIZATION_INCREMENTAL,
        MATERIALIZATION_SNAPSHOT,
        MATERIALIZATION_EPHEMERAL,
    }

    # ==============================================================================
    # DBT PERFORMANCE - Use flext-core DBT Oracle constants
    # ==============================================================================

    # Thread management
    DEFAULT_THREADS: Final = DBTOracleConstants.DEFAULT_THREADS
    MAX_THREADS: Final = 16
    MIN_THREADS: Final = 1

    # Connection pooling for DBT
    DEFAULT_POOL_MIN_SIZE: Final = DBTOracleConstants.DEFAULT_THREADS
    DEFAULT_POOL_MAX_SIZE: Final = DBTOracleConstants.DEFAULT_THREADS * 2
    MAX_POOL_SIZE: Final = 50
    MIN_POOL_SIZE: Final = 1
    DEFAULT_POOL_INCREMENT: Final = 1
    MAX_POOL_INCREMENT: Final = 10

    # Fetch settings
    DEFAULT_FETCH_SIZE: Final = 1000
    DEFAULT_ARRAY_SIZE: Final = 100
    MAX_FETCH_SIZE: Final = 10000

    # ==============================================================================
    # DBT INCREMENTAL STRATEGIES - Oracle specific incremental patterns
    # ==============================================================================

    INCREMENTAL_STRATEGY_APPEND: Final = "append"
    INCREMENTAL_STRATEGY_MERGE: Final = "merge"
    INCREMENTAL_STRATEGY_DELETE_INSERT: Final = "delete+insert"
    DEFAULT_INCREMENTAL_STRATEGY: Final = INCREMENTAL_STRATEGY_MERGE
    VALID_INCREMENTAL_STRATEGIES: ClassVar[set[str]] = {
        INCREMENTAL_STRATEGY_APPEND,
        INCREMENTAL_STRATEGY_MERGE,
        INCREMENTAL_STRATEGY_DELETE_INSERT,
    }

    # ==============================================================================
    # DBT SNAPSHOT STRATEGIES - Standard DBT snapshot patterns
    # ==============================================================================

    SNAPSHOT_STRATEGY_TIMESTAMP: Final = "timestamp"
    SNAPSHOT_STRATEGY_CHECK: Final = "check"
    DEFAULT_SNAPSHOT_STRATEGY: Final = SNAPSHOT_STRATEGY_TIMESTAMP
    VALID_SNAPSHOT_STRATEGIES: ClassVar[set[str]] = {
        SNAPSHOT_STRATEGY_TIMESTAMP,
        SNAPSHOT_STRATEGY_CHECK,
    }

    # ==============================================================================
    # ORACLE SCHEMA AND QUOTING - Oracle identifier rules
    # ==============================================================================

    # Schema defaults
    DEFAULT_SCHEMA: Final = "dbt_user"
    DEFAULT_DATABASE: Final = None  # Oracle doesn't use database concept like other DBs

    # Quoting rules
    QUOTE_CHARACTER: Final = '"'
    QUOTE_POLICY_WHEN_NEEDED: Final = "when_needed"
    QUOTE_POLICY_ALWAYS: Final = "always"
    QUOTE_POLICY_NEVER: Final = "never"
    DEFAULT_QUOTE_POLICY: Final = QUOTE_POLICY_WHEN_NEEDED

    # Case handling
    CASE_SENSITIVITY_PRESERVE: Final = "preserve"
    CASE_SENSITIVITY_UPPER: Final = "upper"
    CASE_SENSITIVITY_LOWER: Final = "lower"
    DEFAULT_CASE_SENSITIVITY: Final = CASE_SENSITIVITY_PRESERVE

    # ==============================================================================
    # ORACLE DATA TYPES - Singer to Oracle type mapping
    # ==============================================================================

    # String types
    DEFAULT_STRING_TYPE: Final = "VARCHAR2(4000)"
    LONG_STRING_TYPE: Final = "CLOB"
    MAX_VARCHAR2_LENGTH: Final = OracleLimits.MAX_VARCHAR_LENGTH

    # Numeric types
    DEFAULT_INTEGER_TYPE: Final = "NUMBER(38,0)"
    DEFAULT_DECIMAL_TYPE: Final = "NUMBER(38,10)"
    DEFAULT_FLOAT_TYPE: Final = "BINARY_DOUBLE"

    # Boolean type (Oracle doesn't have native boolean)
    BOOLEAN_TYPE: Final = "NUMBER(1,0)"

    # Date/Time types
    DEFAULT_DATE_TYPE: Final = "DATE"
    DEFAULT_DATETIME_TYPE: Final = "TIMESTAMP(6)"
    DEFAULT_TIMESTAMP_TYPE: Final = "TIMESTAMP(6)"
    DEFAULT_NLS_DATE_FORMAT: Final = "YYYY-MM-DD HH24:MI:SS"
    DEFAULT_NLS_TIMESTAMP_FORMAT: Final = "YYYY-MM-DD HH24:MI:SS.FF6"

    # JSON and complex types
    JSON_TYPE: Final = "CLOB"
    ARRAY_TYPE: Final = "CLOB"

    # ==============================================================================
    # DBT HOOKS AND OPERATIONS - Standard DBT patterns
    # ==============================================================================

    SUPPORTS_PRE_HOOK: Final = True
    SUPPORTS_POST_HOOK: Final = True
    SUPPORTS_OPERATIONS: Final = True
    DEFAULT_HOOK_TRANSACTION: Final = "transaction"

    # ==============================================================================
    # ERROR HANDLING AND RETRY - Use flext-core patterns
    # ==============================================================================

    # Connection retry for DBT
    DEFAULT_RETRY_ATTEMPTS: Final = 3
    DEFAULT_RETRY_DELAY: Final = 1

    # DBT specific retryable errors
    RETRYABLE_ERRORS: ClassVar[set[str]] = {
        "ORA-00028",  # your session has been killed
        "ORA-00060",  # deadlock detected
        "ORA-01012",  # not logged on
        "ORA-03113",  # end-of-file on communication channel
        "ORA-03114",  # not connected to ORACLE
        "ORA-12170",  # TNS:Connect timeout occurred
    }

    # ==============================================================================
    # SSL AND SECURITY - Standard Oracle SSL modes
    # ==============================================================================

    SSL_MODE_DISABLE: Final = "disable"
    SSL_MODE_ALLOW: Final = "allow"
    SSL_MODE_PREFER: Final = "prefer"
    SSL_MODE_REQUIRE: Final = "require"
    DEFAULT_SSL_MODE: Final = SSL_MODE_PREFER
    DEFAULT_SSL_SERVER_DN_MATCH: Final = True
    DEFAULT_SSL_CLIENT_AUTH: Final = False
    VALID_SSL_MODES: ClassVar[set[str]] = {
        SSL_MODE_DISABLE,
        SSL_MODE_ALLOW,
        SSL_MODE_PREFER,
        SSL_MODE_REQUIRE,
    }

    # ==============================================================================
    # DBT LOGGING AND MONITORING
    # ==============================================================================

    DEFAULT_LOG_LEVEL: Final = "INFO"
    VALID_LOG_LEVELS: ClassVar[set[str]] = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }
    DEFAULT_SQL_LOGGING: Final = False
    DEFAULT_INCLUDE_TIMING: Final = True
    DEFAULT_INCLUDE_ROW_COUNTS: Final = True

    # ==============================================================================
    # DBT CATALOG AND METADATA - Oracle data dictionary integration
    # ==============================================================================

    SUPPORTS_TABLE_COMMENTS: Final = True
    SUPPORTS_COLUMN_COMMENTS: Final = True
    SUPPORTS_DATA_LINEAGE: Final = True
    SUPPORTS_CATALOG_INTEGRATION: Final = True

    # Oracle data dictionary views
    DBA_TABLES_VIEW: Final = "DBA_TABLES"
    ALL_TABLES_VIEW: Final = "ALL_TABLES"
    USER_TABLES_VIEW: Final = "USER_TABLES"
    DBA_TAB_COLUMNS_VIEW: Final = "DBA_TAB_COLUMNS"
    ALL_TAB_COLUMNS_VIEW: Final = "ALL_TAB_COLUMNS"
    USER_TAB_COLUMNS_VIEW: Final = "USER_TAB_COLUMNS"
