"""Models for flext package.

This module provides centralized models for the flext package,
inheriting from FlextCliModels and extending with workspace-specific models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliModels


class FlextModels(FlextCliModels):
    """Centralized models for flext package."""

    # Add workspace-specific models here if needed


# Alias for convenience
m = FlextModels
