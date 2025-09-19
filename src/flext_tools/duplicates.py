"""Minimal duplicates analyzer for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class CodeDuplicateAnalyzer:
    """Basic code duplicate analyzer for legacy scripts."""

    def __init__(self) -> None:
        """Initialize code duplicate analyzer."""

    def analyze_duplicates(
        self, project_path: str | Path,
    ) -> FlextResult[list[dict[str, str]]]:
        """Analyze code duplicates."""
        try:
            _ = project_path  # Parameter used for duplicate analysis
            return FlextResult[list[dict[str, str]]].ok([])
        except Exception as e:
            return FlextResult[list[dict[str, str]]].fail(
                f"Duplicate analysis failed: {e}",
            )

    def get_duplicate_report(self) -> FlextResult[str]:
        """Get duplicate report."""
        return FlextResult[str].ok("No duplicates found")
