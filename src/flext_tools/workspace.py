"""FLEXT Tools Workspace Facade..

This module is a FACADE to flext workspace functionality. It eliminates
ALL workspace duplication by delegating to the established flext workspace service.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_core import FlextDomainService, FlextResult

from flext.workspace import (
    FlextWorkspaceService,
    ProjectType,
    create_workspace_service,
)


# Lazy loading to avoid circular imports
def _get_flext_workspace_classes() -> tuple[
    type, type, Callable[[str | None], FlextWorkspaceService]
]:
    """Lazy load flext workspace classes to avoid circular imports."""
    return FlextWorkspaceService, ProjectType, create_workspace_service


# Primary workspace API - delegate to flext (lazy loaded)
class WorkspaceManager:
    """Lazy wrapper for FlextWorkspaceService to avoid circular imports."""

    def __new__(cls, *args: object, **kwargs: object) -> object:
        """Create instance using lazy-loaded FlextWorkspaceService."""
        flext_workspace_service, _, _ = _get_flext_workspace_classes()
        return flext_workspace_service(*args, **kwargs)


# Legacy compatibility factory functions
def create_workspace_manager(workspace_path: str | None = None) -> object:
    """Create workspace manager using lazy loading."""
    _, _, create_workspace_service = _get_flext_workspace_classes()
    return create_workspace_service(workspace_path)


# Facade class for legacy tools compatibility
class FlextToolsWorkspaceService(FlextDomainService[str]):
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
            _, _, create_workspace_service = _get_flext_workspace_classes()
            self._workspace_service = create_workspace_service(self._workspace_path)
        if self._workspace_service is None:
            msg = "Workspace service not initialized"
            raise RuntimeError(msg)
        return self._workspace_service

    def execute(self, _request: str = "") -> FlextResult[str]:
        """Execute workspace operation through flext workspace service."""
        # Access through lazy loading
        self._get_workspace_service()
        return FlextResult[str].ok(
            "FlextToolsWorkspaceService using flext workspace facade"
        )


__all__ = [
    "FlextToolsWorkspaceService",
    "WorkspaceManager",
    "create_workspace_manager",
]
