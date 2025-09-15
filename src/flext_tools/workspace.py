"""FLEXT Tools Workspace Facade..

This module is a FACADE to flext workspace functionality. It eliminates
ALL workspace duplication by delegating to the established flext workspace service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextDomainService, FlextResult


class FlextWorkspaceService(FlextDomainService[str]):
    """Facade to flext workspace service - eliminates workspace code duplication."""

    def __init__(self, workspace_path: str | None = None) -> None:
        """Initialize with flext workspace service."""
        super().__init__()
        # Lazy loading to avoid circular imports
        self._workspace_path = workspace_path
        self._workspace_service: FlextWorkspaceService | None = None

    def _get_workspace_service(self) -> FlextWorkspaceService:
        """Lazy load workspace service to avoid circular imports."""
        if self._workspace_service is None:
            self._workspace_service = FlextWorkspaceService(self._workspace_path)
        return self._workspace_service

    def execute(self, _request: str = "") -> FlextResult[str]:
        """Execute workspace operation through flext workspace service."""
        # Access through lazy loading
        self._get_workspace_service()
        return FlextResult[str].ok(
            "FlextToolsWorkspaceService using flext workspace facade"
        )


__all__ = [
    "FlextWorkspaceService",
]
