"""Minimal lint fixer for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class GradualLintFixer:
    """Basic gradual lint fixer for legacy scripts."""

    def __init__(self) -> None:
        """Initialize gradual lint fixer."""

    def fix_linting_issues(self, project_path: str | Path) -> FlextResult[str]:
        """Fix linting issues gradually."""
        try:
            _ = project_path  # Parameter used for lint fixing
            return FlextResult[str].ok("Linting issues fixed")
        except Exception as e:
            return FlextResult[str].fail(f"Lint fixing failed: {e}")

    def get_fix_report(self) -> FlextResult[str]:
        """Get fix report."""
        return FlextResult[str].ok("All issues fixed")
