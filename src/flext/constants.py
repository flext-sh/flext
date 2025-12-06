"""Constants for flext package.

This module provides centralized constants for the flext package,
inheriting from FlextCliConstants and extending with workspace-specific values.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_cli import FlextCliConstants


class FlextConstants(FlextCliConstants):
    """Centralized constants for flext package."""

    class Workspace:
        """Workspace-specific constants."""

        NAME: Final[str] = "flext"
        ENV_PREFIX: Final[str] = "FLEXT"


# Alias for convenience
c = FlextConstants
