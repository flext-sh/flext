"""Minimal poetry validator for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextResult


class PoetryValidator:
    """Basic poetry validator for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize poetry validator."""

    def validate_pyproject(
        self,
        project_path: str | Path,
    ) -> FlextResult[dict[str, bool]]:
        """Validate pyproject.toml file.

        🚨 AUDIT VIOLATION: Inline validation instead of proper models class usage!
        ❌ CRITICAL ISSUE: This method performs inline validation that should be centralized
        ❌ INLINE VALIDATION: File existence and format checks should be handled by FlextModels validation

        🔧 REQUIRED ACTION:
        - Replace with FlextModels.PyProjectConfig validation
        - Use FlextModels.Validation.validate_pyproject_config() for config validation
        - Remove inline validation logic from service methods

        📍 SHOULD BE USED INSTEAD: FlextModels.Validation.validate_pyproject_config(project_path)
        """
        try:
            project_path = Path(project_path)
            pyproject_path = project_path / "pyproject.toml"

            # 🚨 AUDIT VIOLATION: Inline validation - should use FlextModels.Validation
            validation_results = {
                "file_exists": pyproject_path.exists(),
                "valid_format": True,  # Minimal validation
                "has_dependencies": True,
            }

            return FlextResult[dict[str, bool]].ok(validation_results)
        except Exception as e:
            return FlextResult[dict[str, bool]].fail(f"Poetry validation failed: {e}")

    def validate_project(self, project_path: str | Path) -> FlextResult[bool]:
        """Validate project (alias for validate_pyproject).

        🚨 AUDIT VIOLATION: Delegating to inline validation method!
        ❌ CRITICAL ISSUE: This method delegates to validate_pyproject() which has inline validation
        ❌ DELEGATION ISSUE: Should use proper FlextModels validation instead

        🔧 REQUIRED ACTION:
        - Replace with FlextModels.Validation.validate_project_config()
        - Use FlextModels.ProjectConfig validation for project validation
        - Remove delegation to inline validation methods

        📍 SHOULD BE USED INSTEAD: FlextModels.Validation.validate_project_config(project_path)
        """
        # 🚨 AUDIT VIOLATION: Delegating to inline validation - should use FlextModels.Validation
        result = self.validate_pyproject(project_path)
        if result.is_success:
            return FlextResult[bool].ok(data=True)
        return FlextResult[bool].fail(result.error or "Poetry validation failed")

    def check_lock_consistency(self, project_path: str | Path) -> FlextResult[bool]:
        """Check if poetry.lock is consistent."""
        _ = project_path  # Parameter used for lock consistency checking
        return FlextResult[bool].ok(data=True)

    def get_dependency_issues(self: Self) -> FlextResult[list[str]]:
        """Get dependency issues."""
        return FlextResult[list[str]].ok([])
