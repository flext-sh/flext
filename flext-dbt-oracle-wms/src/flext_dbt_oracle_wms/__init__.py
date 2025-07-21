"""FLEXT DBT Oracle WMS Package - Oracle WMS data transformation with DBT.

This package provides comprehensive DBT integration for Oracle WMS (Warehouse
Management System)
data transformation using flext-core standards and modern Python 3.13 type system.

IMPORTANT: This package is for Oracle WMS API integration, NOT Oracle Database.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_dbt_oracle_wms.config.types import (
    # Core DBT Oracle WMS configuration types
    DBTOracleWMSConfiguration,
    FlextDBTOracleWMSConfig,
)
from flext_dbt_oracle_wms.constants import (
    # Oracle WMS DBT constants
    DBTOracleWMSDefaults,
    DBTOracleWMSDocumentationTypes,
    DBTOracleWMSEntityTypes,
    DBTOracleWMSMacroTypes,
    DBTOracleWMSMaterializations,
    DBTOracleWMSTestTypes,
)
from flext_dbt_oracle_wms.domain.types import (
    # Domain objects
    DBTOracleWMSAnalysis,
    DBTOracleWMSAnalysisConfiguration,
    DBTOracleWMSCompilation,
    DBTOracleWMSCompilationConfiguration,
    DBTOracleWMSDocumentation,
    DBTOracleWMSDocumentationConfiguration,
    DBTOracleWMSExecution,
    DBTOracleWMSExecutionConfiguration,
    DBTOracleWMSMacro,
    DBTOracleWMSMacroConfiguration,
    DBTOracleWMSModel,
    # Configuration TypedDicts
    DBTOracleWMSModelConfiguration,
    DBTOracleWMSProject,
    DBTOracleWMSProjectConfiguration,
    DBTOracleWMSSnapshot,
    DBTOracleWMSSnapshotConfiguration,
    DBTOracleWMSSource,
    DBTOracleWMSSourceConfiguration,
    DBTOracleWMSTest,
    DBTOracleWMSTestConfiguration,
)

__version__ = "2.0.0"

__all__ = [
    "DBTOracleWMSAnalysis",
    "DBTOracleWMSAnalysisConfiguration",
    "DBTOracleWMSCompilation",
    "DBTOracleWMSCompilationConfiguration",
    "DBTOracleWMSConfiguration",
    "DBTOracleWMSDefaults",
    "DBTOracleWMSDocumentation",
    "DBTOracleWMSDocumentationConfiguration",
    "DBTOracleWMSDocumentationTypes",
    "DBTOracleWMSEntityTypes",
    "DBTOracleWMSExecution",
    "DBTOracleWMSExecutionConfiguration",
    "DBTOracleWMSMacro",
    "DBTOracleWMSMacroConfiguration",
    "DBTOracleWMSMacroTypes",
    "DBTOracleWMSMaterializations",
    "DBTOracleWMSModel",
    "DBTOracleWMSModelConfiguration",
    "DBTOracleWMSProject",
    "DBTOracleWMSProjectConfiguration",
    "DBTOracleWMSSnapshot",
    "DBTOracleWMSSnapshotConfiguration",
    "DBTOracleWMSSource",
    "DBTOracleWMSSourceConfiguration",
    "DBTOracleWMSTest",
    "DBTOracleWMSTestConfiguration",
    "DBTOracleWMSTestTypes",
    "FlextDBTOracleWMSConfig",
]
