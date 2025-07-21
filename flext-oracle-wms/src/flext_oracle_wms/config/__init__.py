"""Oracle WMS Configuration Package - flext-core integrated configuration system.

This package provides comprehensive configuration management for Oracle WMS integrations
using flext-core standards and modern Python 3.13 type system.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import the actual OracleWMSConfig class from the parent module
from flext_oracle_wms.config.types import (
    # Environment configurations
    DevOracleWMSConfig,
    # Complete configuration
    FlextOracleWMSConfig,
    # Core Oracle WMS configuration types
    OracleWMSConfiguration,
    OracleWMSConnectionConfiguration,
    OracleWMSEntityConfiguration,
    OracleWMSFilterConfiguration,
    OracleWMSMonitoringConfiguration,
    OracleWMSPerformanceConfiguration,
    OracleWMSSchemaConfiguration,
    OracleWMSTapConfiguration,
    OracleWMSTargetConfiguration,
    OracleWMSTargetFullConfiguration,
    ProdOracleWMSConfig,
    TestOracleWMSConfig,
)
from flext_oracle_wms.config_module import OracleWMSConfig

__all__ = [
    "DevOracleWMSConfig",
    "FlextOracleWMSConfig",
    "OracleWMSConfig",  # Actual class from config_module.py
    "OracleWMSConfiguration",
    "OracleWMSConnectionConfiguration",
    "OracleWMSEntityConfiguration",
    "OracleWMSFilterConfiguration",
    "OracleWMSMonitoringConfiguration",
    "OracleWMSPerformanceConfiguration",
    "OracleWMSSchemaConfiguration",
    "OracleWMSTapConfiguration",
    "OracleWMSTargetConfiguration",
    "OracleWMSTargetFullConfiguration",
    "ProdOracleWMSConfig",
    "TestOracleWMSConfig",
]
