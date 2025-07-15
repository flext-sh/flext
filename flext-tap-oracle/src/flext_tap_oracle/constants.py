"""Oracle Tap Constants - Maximum flext-core integration with zero duplication.

This module provides Oracle Tap specific constants using flext-core patterns.
All Oracle DB constants are inherited from flext-core to ensure consistency
and eliminate code duplication across Oracle projects.
"""

from __future__ import annotations

from typing import ClassVar, Final

# Import all shared Oracle constants from flext-core
from flext_core.domain.constants import (
    ConnectionProtocols,
    OracleDBConstants,
    OracleDefaults,
    OracleLimits,
    SingerOracleConstants,
    SSLModes,
    StandardLogLevels,
)


class OracleTapConstants:
    """Oracle Tap specific constants following flext-core patterns."""

    # ==============================================================================
    # CONNECTION TYPES - Tap specific
    # ==============================================================================

    CONNECTION_TYPE_DATABASE: Final = "database"
    VALID_CONNECTION_TYPES: ClassVar[set[str]] = {CONNECTION_TYPE_DATABASE}

    # ==============================================================================
    # REPLICATION METHODS - Singer spec compliant
    # ==============================================================================

    REPLICATION_METHOD_FULL_TABLE: Final = "FULL_TABLE"
    REPLICATION_METHOD_INCREMENTAL: Final = "INCREMENTAL"
    VALID_REPLICATION_METHODS: ClassVar[set[str]] = {
        REPLICATION_METHOD_FULL_TABLE,
        REPLICATION_METHOD_INCREMENTAL,
    }

    # ==============================================================================
    # SSL MODES - Use flext-core consolidated SSL modes
    # ==============================================================================

    SSL_MODE_DISABLE: Final = SSLModes.DISABLE
    SSL_MODE_ALLOW: Final = SSLModes.ALLOW
    SSL_MODE_PREFER: Final = SSLModes.PREFER
    SSL_MODE_REQUIRE: Final = SSLModes.REQUIRE
    VALID_SSL_MODES: ClassVar[set[str]] = set(SSLModes.ALL)

    # ==============================================================================
    # ORACLE CONNECTION - Use flext-core Oracle constants exclusively
    # ==============================================================================

    # Port and Protocol
    DEFAULT_PORT: Final = OracleDBConstants.DEFAULT_PORT
    DEFAULT_PROTOCOL: Final = OracleDBConstants.DEFAULT_PROTOCOL
    VALID_PROTOCOLS: ClassVar[set[str]] = set(ConnectionProtocols.ALL)

    # Timeouts
    DEFAULT_TIMEOUT: Final = OracleDBConstants.DEFAULT_TIMEOUT
    DEFAULT_CONNECT_TIMEOUT: Final = OracleDefaults.DEFAULT_CONNECT_TIMEOUT
    DEFAULT_QUERY_TIMEOUT: Final = OracleDefaults.DEFAULT_QUERY_TIMEOUT

    # ==============================================================================
    # PERFORMANCE - Use Singer Oracle constants from flext-core
    # ==============================================================================

    # Batch sizes
    DEFAULT_BATCH_SIZE: Final = SingerOracleConstants.DEFAULT_BATCH_SIZE
    MAX_BATCH_SIZE: Final = SingerOracleConstants.MAX_BATCH_SIZE
    MIN_BATCH_SIZE: Final = SingerOracleConstants.MIN_BATCH_SIZE
    OPTIMAL_BATCH_SIZE: Final = SingerOracleConstants.OPTIMAL_BATCH_SIZE

    # Parallel processing
    DEFAULT_PARALLEL_STREAMS: Final = SingerOracleConstants.MIN_PARALLEL_STREAMS
    MAX_PARALLEL_STREAMS: Final = SingerOracleConstants.MAX_PARALLEL_STREAMS
    OPTIMAL_PARALLEL_STREAMS: Final = SingerOracleConstants.OPTIMAL_PARALLEL_STREAMS

    # Connection pooling
    DEFAULT_POOL_SIZE: Final = SingerOracleConstants.DEFAULT_CONNECTION_POOL_SIZE
    MAX_POOL_SIZE: Final = SingerOracleConstants.MAX_CONNECTION_POOL_SIZE
    MIN_POOL_SIZE: Final = SingerOracleConstants.MIN_CONNECTION_POOL_SIZE

    # Discovery
    DEFAULT_DISCOVERY_BATCH_SIZE: Final = (
        SingerOracleConstants.DEFAULT_DISCOVERY_BATCH_SIZE
    )
    MAX_DISCOVERY_TIMEOUT: Final = SingerOracleConstants.MAX_DISCOVERY_TIMEOUT

    # State management
    DEFAULT_STATE_INTERVAL: Final = SingerOracleConstants.DEFAULT_STATE_INTERVAL
    STATE_MESSAGE_VERSION: Final = SingerOracleConstants.STATE_MESSAGE_VERSION

    # ==============================================================================
    # ORACLE FETCH SETTINGS - Use Oracle DB constants from flext-core
    # ==============================================================================

    DEFAULT_FETCH_SIZE: Final = OracleDBConstants.DEFAULT_FETCH_SIZE
    DEFAULT_ARRAY_SIZE: Final = OracleDBConstants.DEFAULT_ARRAY_SIZE
    MAX_FETCH_SIZE: Final = OracleLimits.MAX_FETCH_SIZE
    MAX_ARRAY_SIZE: Final = 10000  # Standard Oracle array processing limit

    # ==============================================================================
    # CIRCUIT BREAKER - Use flext-core patterns
    # ==============================================================================

    CIRCUIT_BREAKER_FAILURE_THRESHOLD: Final = (
        OracleDefaults.DEFAULT_CIRCUIT_BREAKER_FAILURES
    )
    CIRCUIT_BREAKER_TIMEOUT: Final = OracleDefaults.DEFAULT_CIRCUIT_BREAKER_TIMEOUT

    # ==============================================================================
    # SCHEMA FLATTENING - Tap specific settings
    # ==============================================================================

    DEFAULT_FLATTENING_ENABLED: Final = False
    DEFAULT_FLATTENING_MAX_DEPTH: Final = 5
    DEFAULT_FLATTENING_SEPARATOR: Final = "__"
    MAX_FLATTENING_DEPTH: Final = 10
    VALID_FLATTENING_SEPARATORS: ClassVar[set[str]] = {"__", "_", "-", "."}

    # ==============================================================================
    # LOG LEVELS - Use flext-core consolidated log levels
    # ==============================================================================

    DEFAULT_LOG_LEVEL: Final = StandardLogLevels.DEFAULT
    VALID_LOG_LEVELS: ClassVar[set[str]] = set(StandardLogLevels.ALL)
