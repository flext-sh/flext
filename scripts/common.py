#!/usr/bin/env python3
"""Common utilities for FLEXT scripts - Facade for flext-core patterns.

ANTI-DUPLICATION ENFORCEMENT: Uses flext-core exclusively, NO local implementations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flext_core import FlextCore

from flext import FlextWorkspaceService

logger = FlextCore.Logger(__name__)


def discover_projects(
    workspace_root: Path,
    projects_filter: Sequence[str] | None = None,
) -> list[Path]:
    """Discover FLEXT projects using flext-core workspace management.

    DELEGATES to flext-core FlextWorkspaceService - NO local implementation.
    """
    try:
        # Use flext-core workspace discovery
        workspace_service = FlextWorkspaceService()
        result = workspace_service.discover_workspace_projects(str(workspace_root))

        if result.is_failure:
            logger.error(f"Project discovery failed: {result.error}")
            return []

        project_infos = result.unwrap()
        project_paths: list[Path] = []
        for project_info in project_infos:
            if project_info.repository_path:
                project_path = Path(project_info.repository_path)
                if project_path.exists() and (
                    projects_filter is None or project_info.name in projects_filter
                ):
                    project_paths.append(project_path)

        return project_paths

    except Exception:
        logger.exception("Failed to discover projects")
        return []


def get_workspace_root() -> Path:
    """Get workspace root using flext-core discovery."""
    try:
        # Use current working directory as workspace root
        return Path.cwd()
    except Exception:
        logger.exception("Failed to discover workspace root")
        return Path.cwd()
