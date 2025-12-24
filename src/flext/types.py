"""Type definitions for flext-core package.

This module provides centralized type definitions for the flext-core package.
Uses constants for constant values, defines complex types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypeVar


class FlextTypes:
    """Centralized type definitions for flext-core package."""

    # =========================================================================
    # NAMESPACE: .Core - All core domain types
    # =========================================================================

    class Core:
        """Core domain types."""

        # JSON types
        type JsonPrimitive = str | int | float | bool | None
        type JsonValue = JsonPrimitive | Sequence[object] | Mapping[str, object]


# TypeVars
T = TypeVar("T")

# Alias for convenience
t = FlextTypes
