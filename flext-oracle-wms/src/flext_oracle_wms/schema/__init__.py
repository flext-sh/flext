"""Oracle WMS Schema Package - Dynamic schema processing capabilities.

This package provides dynamic schema discovery and processing capabilities
for Oracle WMS integrations.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_oracle_wms.schema.dynamic import (
    # Core schema classes
    DynamicSchemaProcessor,
    EntityProcessingResult,
    # Result types
    SchemaDiscoveryResult,
    # Factory functions
    create_dynamic_schema_processor,
    # Convenience functions
    discover_entity_schemas,
    process_entity_with_schema,
)

__all__ = [
    "DynamicSchemaProcessor",
    "EntityProcessingResult",
    "SchemaDiscoveryResult",
    "create_dynamic_schema_processor",
    "discover_entity_schemas",
    "process_entity_with_schema",
]
