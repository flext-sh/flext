#!/usr/bin/env python3
"""Common utilities for FLEXT scripts - Facade for flext-core patterns.

ANTI-DUPLICATION ENFORCEMENT: Uses flext-core exclusively, NO local implementations.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

# Use flext-core exclusively - NO LOCAL IMPLEMENTATIONS
from flext_core import FlextLogger, FlextWorkspace

logger = FlextLogger(__name__)


def discover_projects(
    workspace_root: Path,
    projects_filter: Sequence[str] | None = None,
) -> list[Path]:
    """Discover FLEXT projects using flext-core workspace management.

    DELEGATES to flext-core FlextWorkspace - NO local implementation.
    """
    try:
        # Use flext-core workspace discovery
        workspace = FlextWorkspace.create(str(workspace_root))
        result = workspace.list_projects()

        if result.is_failure:
            logger.error(f"Project discovery failed: {result.error}")
            return []

        project_names = result.value
        project_paths = []

        for name in project_names:
            project_path = workspace_root / name
            if project_path.exists():
                # Apply filter if provided
                if projects_filter is None or name in projects_filter:
                    project_paths.append(project_path)

        return project_paths

    except Exception as e:
        logger.exception(f"Failed to discover projects: {e}")
        return []


def get_workspace_root() -> Path:
    """Get workspace root using flext-core discovery."""
    try:
        workspace = FlextWorkspace.discover()
        return Path(workspace.workspace_root)
    except Exception as e:
        logger.exception(f"Failed to discover workspace root: {e}")
        return Path.cwd()
