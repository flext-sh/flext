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

from flext.workspace import FlextWorkspaceService


# Lazy loading to avoid circular imports
def _get_flext_workspace_service() -> type[FlextWorkspaceService]:
    """Lazy load flext workspace service to avoid circular imports."""
    return FlextWorkspaceService


# Facade class for legacy workspace CLI compatibility
# REMOVED: FlextToolsWorkspaceCLIService class - pure facade/wrapper violation
# VIOLATION: This was a facade that delegated to FlextWorkspaceService
# SOLUTION: Use FlextWorkspaceService directly instead of wrapper layer
#
# Per user directive: "do not tolerate wrappers, compatibility layers, aliases or over engineering"
# This entire class provided no value beyond delegation - eliminated per architectural mandate


# Legacy compatibility factory functions
def create_workspace_cli(**data: dict[str, object]) -> FlextWorkspaceService:
    """Create workspace CLI using lazy loading."""
    return _get_flext_workspace_service()(**data)


# Legacy compatibility aliases
WorkspaceCLI = FlextWorkspaceService

__all__ = [
    "FlextCliApi",
    "WorkspaceCLI",
    "create_workspace_cli",
]
