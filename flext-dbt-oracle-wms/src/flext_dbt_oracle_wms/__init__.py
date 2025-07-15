"""FLEXT DBT Oracle WMS Package - Oracle WMS data transformation with DBT.

This package provides comprehensive DBT integration for Oracle WMS (Warehouse Management System)
data transformation using flext-core standards and modern Python 3.13 type system.

IMPORTANT: This package is for Oracle WMS API integration, NOT Oracle Database.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from flext_dbt_oracle_wms.config.types import (
    # Core DBT Oracle WMS configuration types
    DBTOracleWMSConfiguration,
    DBTOracleWMSMacroConfiguration,
    DBTOracleWMSModelConfiguration,
    DBTOracleWMSProfileConfiguration,
    DBTOracleWMSSourceConfiguration,
    DBTOracleWMSTestConfiguration,
    # Complete configuration
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
    DBTOracleWMSAnalysis,
    DBTOracleWMSCompilation,
    DBTOracleWMSDocumentation,
    DBTOracleWMSExecution,
    DBTOracleWMSMacro,
    DBTOracleWMSModel,
    DBTOracleWMSModelConfiguration,
    # Core DBT Oracle WMS domain types
    DBTOracleWMSProject,
    # Type aliases
    DBTOracleWMSProjectConfiguration,
    DBTOracleWMSSnapshot,
    DBTOracleWMSSource,
    DBTOracleWMSSourceConfiguration,
    DBTOracleWMSTest,
)

__version__ = "2.0.0"

__all__ = [
    "DBTOracleWMSAnalysis",
    "DBTOracleWMSCompilation",
    # Configuration types
    "DBTOracleWMSConfiguration",
    # Constants
    "DBTOracleWMSDefaults",
    "DBTOracleWMSDocumentation",
    "DBTOracleWMSDocumentationTypes",
    "DBTOracleWMSEntityTypes",
    "DBTOracleWMSExecution",
    "DBTOracleWMSMacro",
    "DBTOracleWMSMacroConfiguration",
    "DBTOracleWMSMacroTypes",
    "DBTOracleWMSMaterializations",
    "DBTOracleWMSModel",
    "DBTOracleWMSModelConfiguration",
    "DBTOracleWMSModelConfiguration",
    "DBTOracleWMSProfileConfiguration",
    # Domain types
    "DBTOracleWMSProject",
    # Type aliases
    "DBTOracleWMSProjectConfiguration",
    "DBTOracleWMSSnapshot",
    "DBTOracleWMSSource",
    "DBTOracleWMSSourceConfiguration",
    "DBTOracleWMSSourceConfiguration",
    "DBTOracleWMSTest",
    "DBTOracleWMSTestConfiguration",
    "DBTOracleWMSTestTypes",
    "FlextDBTOracleWMSConfig",
]
