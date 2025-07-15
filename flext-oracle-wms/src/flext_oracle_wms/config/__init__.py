"""Oracle WMS Configuration Package - flext-core integrated configuration system.

This package provides comprehensive configuration management for Oracle WMS integrations
using flext-core standards and modern Python 3.13 type system.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

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

# Create alias for backward compatibility
OracleWMSConfig = OracleWMSConfiguration

__all__ = [
    "DevOracleWMSConfig",
    "FlextOracleWMSConfig",
    "OracleWMSConfig",  # Alias for backward compatibility
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
