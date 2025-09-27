"""Path resolution and management utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tools.utilities import FlextToolsUtilities


class FlextPathService(FlextToolsUtilities.PathService):
    """Path resolution and management utilities."""

    def __init__(self) -> None:
        """Initialize FlextPathService."""
        super().__init__()

    @property
    def utility_helper(self) -> FlextToolsUtilities.PathService._UtilityHelper:
        """Get the utility helper instance."""
        return self._UtilityHelper()


__all__ = [
    "FlextPathService",
]
