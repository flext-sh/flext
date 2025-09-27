"""Conflict analysis utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tools.utilities import FlextToolsUtilities


class ConflictAnalyzer(FlextToolsUtilities.ConflictAnalyzer):
    """Conflict analysis utilities."""

    def __init__(self) -> None:
        """Initialize ConflictAnalyzer."""
        super().__init__()


__all__ = [
    "ConflictAnalyzer",
]
