"""Utilities for flext-core package.

This module provides centralized utilities for the flext-core package.
Aggregates functions in flat class, uses constants, types, protocols, models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext.models import m


class FlextUtilities:
    """Centralized utilities for flext-core package."""

    # =========================================================================
    # NAMESPACE: .Core - All core domain utilities
    # =========================================================================

    class Core:
        """Core domain utilities."""

        @staticmethod
        def get_workspace_info() -> m.Core.WorkspaceInfo:
            """Get workspace information."""
            return m.Core.WorkspaceInfo()

        @staticmethod
        def validate_workspace_name(name: str) -> bool:
            """Validate workspace name."""
            return bool(name and name.strip())


# Alias for convenience
u = FlextUtilities
