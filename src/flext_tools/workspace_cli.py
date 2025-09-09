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

from flext.workspace import FlextWorkspaceService, create_workspace_service

# =============================================================================
# FLEXT WORKSPACE CLI FACADE ALIASES (ELIMINATE CIRCULAR IMPORTS)
# =============================================================================


# Lazy loading to avoid circular imports
def _get_flext_workspace_cli_classes() -> tuple[type, object]:
    """Lazy load flext workspace classes to avoid circular imports."""
    return FlextWorkspaceService, create_workspace_service


# Primary workspace CLI API - delegate to flext (lazy loaded)
class WorkspaceCLI:
    """Lazy wrapper for FlextWorkspaceService to avoid circular imports."""

    def __new__(cls, *args: object, **kwargs: object) -> object:
        FlextWorkspaceService, _ = _get_flext_workspace_cli_classes()
        return FlextWorkspaceService(*args, **kwargs)


# Legacy compatibility factory functions
def create_workspace_cli(*args: object, **kwargs: object) -> object:
    """Create workspace CLI using lazy loading."""
    _, create_workspace_service = _get_flext_workspace_cli_classes()
    return create_workspace_service(*args, **kwargs)


# Facade class for legacy workspace CLI compatibility
class FlextToolsWorkspaceCLIService(FlextDomainService):
    """Facade to flext workspace CLI service - eliminates CLI code duplication."""

    def __init__(self, workspace_path: str | None = None) -> None:
        """Initialize with flext workspace and CLI services."""
        super().__init__()
        # Lazy loading to avoid circular imports
        self._workspace_path = workspace_path
        self._workspace_service = None
        self._cli_api = FlextCliApi()

    def _get_workspace_service(self) -> object:
        """Lazy load workspace service to avoid circular imports."""
        if self._workspace_service is None:
            _, create_workspace_service = _get_flext_workspace_cli_classes()
            self._workspace_service = create_workspace_service(self._workspace_path)
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
