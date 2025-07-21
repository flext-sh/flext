"""Oracle WMS Singer SDK Package - Strict compliance with mandatory capabilities.

This package provides Singer SDK strict compliance for Oracle WMS integrations
with mandatory flattening/deflattening capabilities as required.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_oracle_wms.singer.flattening import (
    DeflatteningResult,
    # Result types
    FlatteningResult,
    OracleWMSDeflattener,
    # Core flattening/deflattening classes
    OracleWMSFlattener,
    create_deflattener,
    # Factory functions
    create_flattener,
    deflattened_wms_record,
    # Convenience functions
    flatten_wms_record,
)

__all__ = [
    "DeflatteningResult",
    "FlatteningResult",
    "OracleWMSDeflattener",
    "OracleWMSFlattener",
    "create_deflattener",
    "create_flattener",
    "deflattened_wms_record",
    "flatten_wms_record",
]
