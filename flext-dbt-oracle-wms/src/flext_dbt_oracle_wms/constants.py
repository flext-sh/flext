"""FLEXT DBT Oracle WMS Constants - Simplified version.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final


# DBT Oracle WMS Entity Types
class DBTOracleWMSEntityTypes:
    """Oracle WMS entity types for DBT models."""

    ALLOCATION: Final[str] = "allocation"
    ORDER_HDR: Final[str] = "order_hdr"
    ORDER_DTL: Final[str] = "order_dtl"
    INVENTORY: Final[str] = "inventory"
    LOCATION: Final[str] = "location"
    ITEM: Final[str] = "item"
    SHIPMENT: Final[str] = "shipment"
    RECEIPT: Final[str] = "receipt"
    TASK: Final[str] = "task"
    WAVE: Final[str] = "wave"


# DBT Materialization Types
class DBTOracleWMSMaterializations:
    """DBT materialization types for Oracle WMS."""

    TABLE: Final[str] = "table"
    VIEW: Final[str] = "view"
    INCREMENTAL: Final[str] = "incremental"
    SNAPSHOT: Final[str] = "snapshot"
    EPHEMERAL: Final[str] = "ephemeral"


# DBT Test Types
class DBTOracleWMSTestTypes:
    """DBT test types for Oracle WMS."""

    UNIQUE: Final[str] = "unique"
    NOT_NULL: Final[str] = "not_null"
    RELATIONSHIPS: Final[str] = "relationships"
    ACCEPTED_VALUES: Final[str] = "accepted_values"
    DATA_QUALITY: Final[str] = "data_quality"


# DBT Macro Types
class DBTOracleWMSMacroTypes:
    """DBT macro types for Oracle WMS."""

    UTILITY: Final[str] = "utility"
    TRANSFORMATION: Final[str] = "transformation"
    AUDIT: Final[str] = "audit"
    ORACLE_SPECIFIC: Final[str] = "oracle_specific"


# DBT Documentation Types
class DBTOracleWMSDocumentationTypes:
    """DBT documentation types for Oracle WMS."""

    MODEL: Final[str] = "model"
    SOURCE: Final[str] = "source"
    MACRO: Final[str] = "macro"
    ANALYSIS: Final[str] = "analysis"


# DBT Defaults
class DBTOracleWMSDefaults:
    """Default values for DBT Oracle WMS."""

    PROJECT_NAME: Final[str] = "flext_dbt_oracle_wms"
    VERSION: Final[str] = "2.0.0"
    PROFILE: Final[str] = "flext_oracle_wms"
    SCHEMA_PREFIX: Final[str] = "wms"
    BATCH_SIZE: Final[int] = 1000
    INCREMENTAL_LOOKBACK_DAYS: Final[int] = 7
    DATA_QUALITY_THRESHOLD: Final[float] = 0.95


# Core WMS Constants
class WMSConstants:
    """Core WMS constants for Oracle integration."""

    # Entity levels
    HIGH_LEVEL: Final[str] = "high"
    MEDIUM_LEVEL: Final[str] = "medium"
    LOW_LEVEL: Final[str] = "low"

    # Processing status
    PENDING: Final[str] = "pending"
    PROCESSING: Final[str] = "processing"
    COMPLETED: Final[str] = "completed"
    FAILED: Final[str] = "failed"

    # Validation modes
    STRICT_VALIDATION: Final[str] = "strict"
    NORMAL_VALIDATION: Final[str] = "normal"
    RELAXED_VALIDATION: Final[str] = "relaxed"


# Export commonly used constants
__all__ = [
    "DBTOracleWMSDefaults",
    "DBTOracleWMSDocumentationTypes",
    "DBTOracleWMSEntityTypes",
    "DBTOracleWMSMacroTypes",
    "DBTOracleWMSMaterializations",
    "DBTOracleWMSTestTypes",
    "WMSConstants",
]
