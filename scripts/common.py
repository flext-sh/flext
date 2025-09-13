#!/usr/bin/env python3
"""Common utilities for FLEXT scripts - Facade for flext-core patterns.

ANTI-DUPLICATION ENFORCEMENT: Uses flext-core exclusively, NO local implementations.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

# Use flext-core exclusively - NO LOCAL IMPLEMENTATIONS
from flext_core import FlextLogger

from flext.workspace import FlextWorkspaceService

logger = FlextLogger(__name__)


def discover_projects(
    workspace_root: Path,
    projects_filter: Sequence[str] | None = None,
) -> list[Path]:
    """Discover FLEXT projects using flext-core workspace management.

    DELEGATES to flext-core FlextWorkspaceService - NO local implementation.
    """
    try:
        # Use flext-core workspace discovery
        workspace_service = FlextWorkspaceService(str(workspace_root))
        result = workspace_service.discover_projects()

        if result.is_failure:
            logger.error(f"Project discovery failed: {result.error}")
            return []

        project_infos = result.value
        project_paths = []

        for project_info in project_infos:
            project_path = Path(project_info["path"])
            if project_path.exists():
                # Apply filter if provided
                if projects_filter is None or project_info["name"] in projects_filter:
                    project_paths.append(project_path)

        return project_paths

    except Exception as e:
        logger.exception(f"Failed to discover projects: {e}")
        return []


def get_workspace_root() -> Path:
    """Get workspace root using flext-core discovery."""
    try:
        # Use current working directory as workspace root
        workspace_service = FlextWorkspaceService()
        return workspace_service._workspace_path
    except Exception as e:
        logger.exception(f"Failed to discover workspace root: {e}")
        return Path.cwd()
