"""FLEXT Tools Workspace CLI Facade - ANTI-DUPLICATION flext-cli Integration.

CRITICAL: This module is a FACADE to flext workspace CLI functionality. It eliminates
ALL workspace CLI duplication by delegating to the established flext workspace service.

ZERO TOLERANCE ENFORCEMENT: NO local CLI implementations. ALL CLI functionality
MUST use flext-cli exclusively. NO Click/Rich direct imports allowed.

DOMAIN SEPARATION: CLI patterns belong to flext-cli domain, NOT flext-tools.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli import FlextCliApi
from flext_core import FlextDomainService, FlextResult

from flext.workspace import FlextWorkspaceService


# Lazy loading to avoid circular imports
def _get_flext_workspace_service() -> type[FlextWorkspaceService]:
    """Lazy load flext workspace service to avoid circular imports."""
    return FlextWorkspaceService


# Primary workspace CLI API - delegate to flext (lazy loaded)
class WorkspaceCLI:
    """Lazy wrapper for FlextWorkspaceService to avoid circular imports."""

    def __init__(self, workspace_path: str | None = None, **data: object) -> None:
        """Initialize workspace CLI with lazy loading."""
        self._workspace_path = workspace_path
        self._data = data
        self._service: FlextWorkspaceService | None = None

    def _get_service(self) -> FlextWorkspaceService:
        """Get the underlying workspace service."""
        if self._service is None:
            flext_workspace_service = _get_flext_workspace_service()
            self._service = flext_workspace_service(self._workspace_path, **self._data)
        return self._service

    def __getattr__(self, name: str) -> object:
        """Delegate attribute access to the underlying service."""
        return getattr(self._get_service(), name)


# Legacy compatibility factory functions
def create_workspace_cli(
    workspace_path: str | None = None, **data: object
) -> WorkspaceCLI:
    """Create workspace CLI using lazy loading."""
    return WorkspaceCLI(workspace_path, **data)


# Facade class for legacy workspace CLI compatibility
class FlextToolsWorkspaceCLIService(FlextDomainService[str]):
    """Facade to flext workspace CLI service - eliminates CLI code duplication."""

    def __init__(self, workspace_path: str | None = None) -> None:
        """Initialize with flext workspace and CLI services."""
        super().__init__()
        # Lazy loading to avoid circular imports
        self._workspace_path = workspace_path
        self._workspace_service: FlextWorkspaceService | None = None
        self._cli_api = FlextCliApi()

    def _get_workspace_service(self) -> FlextWorkspaceService:
        """Lazy load workspace service to avoid circular imports."""
        if self._workspace_service is None:
            flext_workspace_service = _get_flext_workspace_service()
            self._workspace_service = flext_workspace_service(self._workspace_path)
            # Additional safety check after initialization
            if self._workspace_service is None:
                msg = "Failed to initialize workspace service"
                raise RuntimeError(msg)
        return self._workspace_service

    def execute(self, _request: str = "") -> FlextResult[str]:
        """Execute workspace CLI operation through flext services."""
        # Access through lazy loading
        self._get_workspace_service()
        return FlextResult[str].ok("FlextToolsWorkspaceCLIService using flext facade")


__all__ = [
    "FlextCliApi",
    "FlextToolsWorkspaceCLIService",
    "WorkspaceCLI",
    "create_workspace_cli",
]
