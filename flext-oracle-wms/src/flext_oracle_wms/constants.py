"""Oracle WMS constants and types.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Centralized constants for Oracle WMS integrations using flext-core standards.
"""

from __future__ import annotations

from typing import Final, Literal

# Import flext-core constants
from flext_core.domain.constants import ConfigDefaults

# ==============================================================================
# ORACLE WMS API CONSTANTS
# ==============================================================================


class OracleWMSDefaults:
    """Oracle WMS-specific default values."""

    # API Configuration
    DEFAULT_API_VERSION: Final = "v10"
    DEFAULT_AUTH_METHOD: Final = "basic"

    # Performance settings aligned with flext-core
    DEFAULT_PAGE_SIZE: Final = ConfigDefaults.DEFAULT_PAGE_SIZE
    MAX_PAGE_SIZE: Final = ConfigDefaults.MAX_PAGE_SIZE
    DEFAULT_TIMEOUT: Final = ConfigDefaults.DEFAULT_HTTP_TIMEOUT
    DEFAULT_RETRIES: Final = ConfigDefaults.DEFAULT_HTTP_RETRIES
    DEFAULT_BATCH_SIZE: Final = ConfigDefaults.DEFAULT_BATCH_SIZE

    # WMS-specific limits
    MAX_ENTITIES_PER_REQUEST: Final = 50
    MAX_FILTER_CONDITIONS: Final = 10
    MAX_ORDERING_FIELDS: Final = 5

    # Rate limiting
    DEFAULT_RATE_LIMIT_RPM: Final = 60
    MIN_REQUEST_DELAY: Final = 0.1

    # Schema flattening
    DEFAULT_FLATTEN_ENABLED: Final = True
    DEFAULT_FLATTEN_MAX_DEPTH: Final = 5
    FLATTEN_SEPARATOR: Final = "__"


class OracleWMSEntityTypes:
    """Oracle WMS entity types."""

    ALLOCATION: Final = "allocation"
    ORDER_HDR: Final = "order_hdr"
    ORDER_DTL: Final = "order_dtl"
    INVENTORY: Final = "inventory"
    LOCATION: Final = "location"
    ITEM: Final = "item"
    SHIPMENT: Final = "shipment"
    RECEIPT: Final = "receipt"
    TASK: Final = "task"
    WAVE: Final = "wave"

    # All supported entities
    ALL_ENTITIES: Final = [
        ALLOCATION,
        ORDER_HDR,
        ORDER_DTL,
        INVENTORY,
        LOCATION,
        ITEM,
        SHIPMENT,
        RECEIPT,
        TASK,
        WAVE,
    ]


class OracleWMSFilterOperators:
    """Oracle WMS filter operators."""

    EQ: Final = "eq"
    NEQ: Final = "neq"
    GT: Final = "gt"
    GTE: Final = "gte"
    LT: Final = "lt"
    LTE: Final = "lte"
    IN: Final = "in"
    NIN: Final = "nin"
    LIKE: Final = "like"

    ALL_OPERATORS: Final = [EQ, NEQ, GT, GTE, LT, LTE, IN, NIN, LIKE]


class OracleWMSPageModes:
    """Oracle WMS pagination modes."""

    API: Final = "api"
    SEQUENCED: Final = "sequenced"

    ALL_MODES: Final = [API, SEQUENCED]
    DEFAULT: Final = API


class OracleWMSWriteModes:
    """Oracle WMS write modes for targets."""

    INSERT: Final = "insert"
    UPDATE: Final = "update"
    UPSERT: Final = "upsert"

    ALL_MODES: Final = [INSERT, UPDATE, UPSERT]
    DEFAULT: Final = INSERT


# ==============================================================================
# TYPE LITERALS
# ==============================================================================

# Entity type literal
OracleWMSEntityType = Literal[
    "allocation",
    "order_hdr",
    "order_dtl",
    "inventory",
    "location",
    "item",
    "shipment",
    "receipt",
    "task",
    "wave",
]

# Filter operator literal
OracleWMSFilterOperator = Literal[
    "eq",
    "neq",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "nin",
    "like",
]

# Page mode literal
OracleWMSPageMode = Literal["api", "sequenced"]

# Write mode literal
OracleWMSWriteMode = Literal["insert", "update", "upsert"]

# Authentication method literal
OracleWMSAuthMethod = Literal["basic", "oauth2"]


# ==============================================================================
# ERROR MESSAGES
# ==============================================================================


class OracleWMSErrorMessages:
    """Oracle WMS-specific error messages."""

    # Connection errors
    CONNECTION_FAILED: Final = "Failed to connect to Oracle WMS API"
    AUTHENTICATION_FAILED: Final = "Oracle WMS authentication failed"
    API_ERROR: Final = "Oracle WMS API error"
    TIMEOUT_ERROR: Final = "Oracle WMS API request timeout"

    # Entity errors
    ENTITY_NOT_FOUND: Final = "Oracle WMS entity not found"
    INVALID_ENTITY_TYPE: Final = "Invalid Oracle WMS entity type"
    ENTITY_DISCOVERY_FAILED: Final = "Oracle WMS entity discovery failed"

    # Schema errors
    SCHEMA_GENERATION_FAILED: Final = "Oracle WMS schema generation failed"
    FLATTENING_FAILED: Final = "Schema flattening failed"
    DEFLATTENING_FAILED: Final = "Schema deflattening failed"

    # Filter errors
    INVALID_FILTER_OPERATOR: Final = "Invalid filter operator"
    INVALID_FILTER_VALUE: Final = "Invalid filter value"
    TOO_MANY_FILTERS: Final = "Too many filter conditions"

    # Data errors
    INVALID_RECORD_FORMAT: Final = "Invalid record format"
    BATCH_WRITE_FAILED: Final = "Batch write to Oracle WMS failed"
    RATE_LIMIT_EXCEEDED: Final = "Oracle WMS rate limit exceeded"


# ==============================================================================
# SUCCESS MESSAGES
# ==============================================================================


class OracleWMSSuccessMessages:
    """Oracle WMS-specific success messages."""

    # Connection
    CONNECTION_SUCCESS: Final = "Connected to Oracle WMS API successfully"
    AUTHENTICATION_SUCCESS: Final = "Oracle WMS authentication successful"

    # Discovery
    ENTITY_DISCOVERY_SUCCESS: Final = "Oracle WMS entity discovery completed"
    SCHEMA_GENERATION_SUCCESS: Final = "Oracle WMS schema generation completed"

    # Data operations
    DATA_EXTRACTION_SUCCESS: Final = "Oracle WMS data extraction completed"
    DATA_LOAD_SUCCESS: Final = "Oracle WMS data load completed"
    BATCH_WRITE_SUCCESS: Final = "Batch write to Oracle WMS completed"


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "OracleWMSAuthMethod",
    # Constants
    "OracleWMSDefaults",
    # Type literals
    "OracleWMSEntityType",
    "OracleWMSEntityTypes",
    # Messages
    "OracleWMSErrorMessages",
    "OracleWMSFilterOperator",
    "OracleWMSFilterOperators",
    "OracleWMSPageMode",
    "OracleWMSPageModes",
    "OracleWMSSuccessMessages",
    "OracleWMSWriteMode",
    "OracleWMSWriteModes",
]
