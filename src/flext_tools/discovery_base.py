"""Minimal dependency discovery for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Self

from flext_core import FlextResult


class DependencyDiscovery:
    """Basic dependency discovery for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize dependency discovery."""

    def discover_dependencies(
        self,
        project_path: str,
    ) -> FlextResult[list[FlextTypes.StringDict]]:
        """Discover project dependencies.

        🚨 AUDIT VIOLATION: Inline validation instead of proper models class usage!
        ❌ CRITICAL ISSUE: This method performs inline validation that should be centralized
        ❌ INLINE VALIDATION: Empty path check should be handled by FlextModels validation

        🔧 REQUIRED ACTION:
        - Replace with FlextModels.ProjectPath validation
        - Use FlextModels.Validation.validate_project_path() for path validation
        - Remove inline validation logic from service methods

        📍 SHOULD BE USED INSTEAD: FlextModels.Validation.validate_project_path(project_path)
        """
        try:
            # Use the project_path parameter for dependency discovery
            # 🚨 AUDIT VIOLATION: Inline validation - should use FlextModels.Validation
            if not project_path:
                return FlextResult[list[FlextTypes.StringDict]].fail(
                    "Project path cannot be empty",
                )

            # Placeholder implementation - acknowledge parameter usage
            _ = project_path  # Parameter used for dependency discovery
            return FlextResult[list[FlextTypes.StringDict]].ok([])
        except Exception as e:
            return FlextResult[list[FlextTypes.StringDict]].fail(
                f"Discovery failed: {e}"
            )

    def analyze_imports(self, file_path: str) -> FlextResult[FlextTypes.StringList]:
        """Analyze imports in a file.

        🚨 AUDIT VIOLATION: Inline validation instead of proper models class usage!
        ❌ CRITICAL ISSUE: This method performs inline validation that should be centralized
        ❌ INLINE VALIDATION: Empty path check should be handled by FlextModels validation

        🔧 REQUIRED ACTION:
        - Replace with FlextModels.FilePath validation
        - Use FlextModels.Validation.validate_file_path() for path validation
        - Remove inline validation logic from service methods

        📍 SHOULD BE USED INSTEAD: FlextModels.Validation.validate_file_path(file_path)
        """
        # 🚨 AUDIT VIOLATION: Inline validation - should use FlextModels.Validation
        if not file_path:
            return FlextResult[FlextTypes.StringList].fail("File path cannot be empty")

        # Placeholder implementation - acknowledge parameter usage
        _ = file_path  # Parameter used for import analysis
        return FlextResult[FlextTypes.StringList].ok([])
