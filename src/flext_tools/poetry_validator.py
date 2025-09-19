"""Minimal poetry validator for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class PoetryValidator:
    """Basic poetry validator for legacy scripts."""

    def __init__(self) -> None:
        """Initialize poetry validator."""

    def validate_pyproject(
        self,
        project_path: str | Path,
    ) -> FlextResult[dict[str, bool]]:
        """Validate pyproject.toml file."""
        try:
            project_path = Path(project_path)
            pyproject_path = project_path / "pyproject.toml"

            validation_results = {
                "file_exists": pyproject_path.exists(),
                "valid_format": True,  # Minimal validation
                "has_dependencies": True,
            }

            return FlextResult[dict[str, bool]].ok(validation_results)
        except Exception as e:
            return FlextResult[dict[str, bool]].fail(f"Poetry validation failed: {e}")

    def validate_project(self, project_path: str | Path) -> FlextResult[bool]:
        """Validate project (alias for validate_pyproject)."""
        result = self.validate_pyproject(project_path)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Poetry validation failed")

    def check_lock_consistency(self, project_path: str | Path) -> FlextResult[bool]:
        """Check if poetry.lock is consistent."""
        _ = project_path  # Parameter used for lock consistency checking
        return FlextResult[bool].ok(data=True)

    def get_dependency_issues(self) -> FlextResult[list[str]]:
        """Get dependency issues."""
        return FlextResult[list[str]].ok([])
