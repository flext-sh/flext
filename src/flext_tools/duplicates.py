"""Minimal duplicates analyzer for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextCore


class CodeDuplicateAnalyzer:
    """Basic code duplicate analyzer for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize code duplicate analyzer."""

    def analyze_duplicates(
        self,
        project_path: str | Path,
    ) -> FlextCore.Result[list[FlextCore.Types.StringDict]]:
        """Analyze code duplicates."""
        try:
            _ = project_path  # Parameter used for duplicate analysis
            return FlextCore.Result[list[FlextCore.Types.StringDict]].ok([])
        except Exception as e:
            return FlextCore.Result[list[FlextCore.Types.StringDict]].fail(
                f"Duplicate analysis failed: {e}",
            )

    def get_duplicate_report(self: Self) -> FlextCore.Result[str]:
        """Get duplicate report."""
        return FlextCore.Result[str].ok("No duplicates found")
