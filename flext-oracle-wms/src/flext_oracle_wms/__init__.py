"""Enterprise Oracle WMS client library for FLEXT data integration platform.

This library provides comprehensive Oracle WMS integration capabilities with:
- Python 3.13 type safety and flext-core integration
- Mandatory flattening/deflattening capabilities for Singer SDK compliance
- Advanced filtering with all required operators
  (eq, neq, gt, gte, lt, lte, in, nin, like)
- Dynamic schema discovery and entity processing
- Pagination modes: "api" (offset-based) and "sequenced" (cursor-based)
- Complete Oracle WMS API integration (NOT Oracle Database)

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

__version__ = "2.0.0"

# Core Oracle WMS client and configuration
from flext_oracle_wms.client import OracleWMSClient
from flext_oracle_wms.config import (
    FlextOracleWMSConfig,
    OracleWMSConfiguration,
    OracleWMSConnectionConfiguration,
    OracleWMSEntityConfiguration,
    OracleWMSSchemaConfiguration,
)
from flext_oracle_wms.config_module import OracleWMSConfig as OracleWMSConfig_Class
from flext_oracle_wms.constants import (
    OracleWMSDefaults,
    OracleWMSEntityTypes,
    OracleWMSFilterOperators,
    OracleWMSPageModes,
    OracleWMSWriteModes,
)

# Advanced filtering capabilities
from flext_oracle_wms.filtering import (
    FilterQuery,
    FilterResult,
    OracleWMSAdvancedFilter,
    create_advanced_filter,
    filter_by_id_range,
    filter_by_modification_time,
)
from flext_oracle_wms.models import WMSDiscoveryResult, WMSEntity

# Dynamic schema processing
from flext_oracle_wms.schema import (
    DynamicSchemaProcessor,
    EntityProcessingResult,
    SchemaDiscoveryResult,
    create_dynamic_schema_processor,
    discover_entity_schemas,
    process_entity_with_schema,
)

# Singer SDK capabilities - MANDATORY flattening/deflattening
# Factory functions for easy instantiation
from flext_oracle_wms.singer import (
    DeflatteningResult,
    FlatteningResult,
    OracleWMSDeflattener,
    OracleWMSFlattener,
    create_deflattener,
    create_flattener,
    deflattened_wms_record,
    flatten_wms_record,
)

# Type definitions and constants
from flext_oracle_wms.typedefs import (
    WMSConnectionInfo,
    WMSEntityInfo,
    WMSFilterCondition,
    WMSFilters,
    WMSFlattenedRecord,
    WMSFlattenedSchema,
    WMSRecord,
    WMSRecordBatch,
    WMSSchema,
)

__all__ = [
    "DeflatteningResult",
    # Dynamic schema processing
    "DynamicSchemaProcessor",
    "EntityProcessingResult",
    "FilterQuery",
    "FilterResult",
    "FlatteningResult",
    "FlextOracleWMSConfig",
    # Advanced filtering
    "OracleWMSAdvancedFilter",
    # Core client and configuration
    "OracleWMSClient",
    "OracleWMSConfig_Class",
    "OracleWMSConfiguration",
    "OracleWMSConnectionConfiguration",
    "OracleWMSDefaults",
    "OracleWMSDeflattener",
    "OracleWMSEntityConfiguration",
    # Constants
    "OracleWMSEntityTypes",
    "OracleWMSFilterOperators",
    # Singer SDK capabilities (MANDATORY)
    "OracleWMSFlattener",
    "OracleWMSPageModes",
    "OracleWMSSchemaConfiguration",
    "OracleWMSWriteModes",
    "SchemaDiscoveryResult",
    "WMSConnectionInfo",
    "WMSDiscoveryResult",
    "WMSEntity",
    "WMSEntityInfo",
    "WMSFilterCondition",
    "WMSFilters",
    "WMSFlattenedRecord",
    "WMSFlattenedSchema",
    # Type definitions
    "WMSRecord",
    "WMSRecordBatch",
    "WMSSchema",
    "create_advanced_filter",
    "create_deflattener",
    "create_dynamic_schema_processor",
    "create_flattener",
    "deflattened_wms_record",
    "discover_entity_schemas",
    "filter_by_id_range",
    "filter_by_modification_time",
    "flatten_wms_record",
    "process_entity_with_schema",
]
