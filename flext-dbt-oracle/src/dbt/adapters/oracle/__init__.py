"""FLEXT DBT Oracle Adapter - Modern Oracle Database Integration for DBT.

This adapter provides enterprise-grade Oracle database integration for DBT using
flext-infrastructure.databases.flext-db-oracle as the foundation, ensuring zero code
duplication and maximum
reliability for data transformation workflows.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from __future__ import annotations

from dbt.adapters.oracle.config import (
    DBTOracleConfig,
    DBTOracleSettings,
    OracleCredentialsConfig,
)
from dbt.adapters.oracle.connections import OracleConnectionManager
from dbt.adapters.oracle.constants import DBTOracleAdapterConstants
from dbt.adapters.oracle.impl import OracleAdapter
from dbt.adapters.oracle.types import (
    DBTOracleColumnInfo,
    DBTOracleCompilationResult,
    DBTOracleConnectionConfig,
    DBTOracleCredentials,
    DBTOracleExecutionResult,
    DBTOracleIndexInfo,
    DBTOracleModelConfig,
    DBTOracleRelationConfig,
    DBTOracleSchemaInfo,
    DBTOracleTableInfo,
    DBTOracleTestResult,
)

# Version information
__version__ = "1.0.0"
__author__ = "FLEXT Team"
__email__ = "team@flext.sh"

# Public API - following DBT adapter conventions
__all__ = [
    # Configuration classes
    "DBTOracleAdapterConstants",
    # Type definitions
    "DBTOracleColumnInfo",
    "DBTOracleCompilationResult",
    "DBTOracleConfig",
    "DBTOracleConnectionConfig",
    "DBTOracleCredentials",
    "DBTOracleExecutionResult",
    "DBTOracleIndexInfo",
    "DBTOracleModelConfig",
    "DBTOracleRelationConfig",
    "DBTOracleSchemaInfo",
    "DBTOracleSettings",
    "DBTOracleTableInfo",
    "DBTOracleTestResult",
    # Core adapter classes
    "OracleAdapter",
    "OracleConnectionManager",
    "OracleCredentialsConfig",
    # Metadata
    "__author__",
    "__email__",
    "__version__",
]
