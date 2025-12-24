"""Constants for flext-core package.

This module provides centralized constants for the flext-core package.
No inheritance from higher domains - core is the foundation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final


class FlextConstants:
    """Centralized constants for flext-core package."""

    # =========================================================================
    # NAMESPACE: .Core - All core domain constants
    # =========================================================================

    class Core:
        """Core domain constants."""

        class Status:
            """Status constants."""

            OK: Final[str] = "ok"
            ERROR: Final[str] = "error"
            WARNING: Final[str] = "warning"

        class Workspace:
            """Workspace-specific constants."""

            NAME: Final[str] = "flext"
            ENV_PREFIX: Final[str] = "FLEXT"

    class Platform:
        """Platform-specific constants."""

        FLEXT_API_PORT: Final[int] = 8000
        DEFAULT_HOST: Final[str] = "localhost"


# Alias for convenience
c = FlextConstants
