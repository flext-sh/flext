"""Type definitions for flext package.

This module provides centralized type definitions for the flext package,
inheriting from FlextCliTypes and extending with workspace-specific types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeVar

from flext_cli import FlextCliTypes


class FlextTypes(FlextCliTypes):
    """Centralized type definitions for flext package."""

    # Add workspace-specific types here if needed


# TypeVars
T = TypeVar("T")

# Alias for convenience
t = FlextTypes
