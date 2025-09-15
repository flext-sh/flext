"""FLEXT Workspace - Legacy compatibility module.

This module provides backward compatibility for the old workspace structure.
All functionality has been moved to workspace_service.py and workspace_models.py
following the single-class-per-module principle.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext.project_types import ProjectType, WorkspaceStatus
from flext.workspace_models import FlextAdvancedWorkspaceModels
from flext.workspace_service import (
    FlextWorkspaceService,
    ProjectDiscoveryServiceProtocol,
    WorkspaceValidatorProtocol,
    create_workspace_service,
)

# Alias for test compatibility
FlextAdvancedWorkspaceService = FlextWorkspaceService

__all__ = [
    "FlextAdvancedWorkspaceModels",
    "FlextAdvancedWorkspaceService",  # Test compatibility alias
    "FlextWorkspaceService",
    "ProjectDiscoveryServiceProtocol",
    "ProjectType",
    "WorkspaceStatus",
    "WorkspaceValidatorProtocol",
    "create_workspace_service",
]
