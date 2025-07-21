"""Oracle WMS Filtering Package - Advanced filtering capabilities.

This package provides comprehensive filtering capabilities for Oracle WMS integrations
with support for all required operators and pagination modes.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_oracle_wms.filtering.advanced import (
    # Filter structures
    FilterCondition,
    FilterGroup,
    FilterQuery,
    FilterResult,
    # Core filtering classes
    OracleWMSAdvancedFilter,
    # Factory functions
    create_advanced_filter,
    # Convenience functions
    filter_by_id_range,
    filter_by_modification_time,
)

__all__ = [
    "FilterCondition",
    "FilterGroup",
    "FilterQuery",
    "FilterResult",
    "OracleWMSAdvancedFilter",
    "create_advanced_filter",
    "filter_by_id_range",
    "filter_by_modification_time",
]
