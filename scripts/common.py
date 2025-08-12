#!/usr/bin/env python3
"""Common utilities for FLEXT scripts.

This module provides shared utilities and functions used across various
FLEXT automation, maintenance, and operational scripts. It implements
common patterns for project discovery, workspace management, and
script coordination.

Key Functions:
    - discover_projects: Discovers FLEXT projects in workspace
    - Project filtering and organization utilities
    - Workspace navigation and validation helpers

The utilities in this module follow FLEXT ecosystem patterns and
integrate with the broader FLEXT tooling infrastructure.

Example:
    Basic project discovery:

    >>> from pathlib import Path
    >>> from scripts.common import discover_projects
    >>>
    >>> workspace = Path("/path/to/flext")
    >>> projects = discover_projects(workspace)
    >>> print(f"Found {len(projects)} projects")
    >>>
    >>> # Filter specific projects
    >>> core_projects = discover_projects(workspace, ["flext-core", "flext-api"])
    >>> print(f"Core projects: {[p.name for p in core_projects]}")

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


def discover_projects(
    workspace_root: Path,
    projects_filter: Sequence[str] | None = None,
) -> list[Path]:
    """Discover FLEXT projects in workspace directory.

    Searches the workspace directory for valid FLEXT projects by looking for
    directories that contain a pyproject.toml file and are not in the ignore
    list. Projects are automatically filtered to exclude service directories
    and system directories.

    Args:
        workspace_root: Root directory of the FLEXT workspace to search.
        projects_filter: Optional sequence of project names to include.
                        If provided, only projects matching these names
                        will be returned. If None, all discovered projects
                        are returned.

    Returns:
        List of Path objects pointing to discovered project directories,
        sorted alphabetically by project name.

    Example:
        >>> from pathlib import Path
        >>> workspace = Path("/home/user/flext")
        >>>
        >>> # Discover all projects
        >>> all_projects = discover_projects(workspace)
        >>> print([p.name for p in all_projects])
        ['flext-api', 'flext-auth', 'flext-core', ...]
        >>>
        >>> # Filter specific projects
        >>> core_projects = discover_projects(workspace, ["flext-core", "flext-api"])
        >>> print([p.name for p in core_projects])
        ['flext-api', 'flext-core']

    Note:
        The following directories are automatically ignored:
        - algar-oud-mig (legacy service)
        - gruponos-meltano-native (specialized service)
        - flexcore (Go service)
        - System directories (.git, .venv, __pycache__)

    """
    # Projects to ignore (these are services, not libraries)
    ignore_list = {"algar-oud-mig", "gruponos-meltano-native", "flexcore"}

    # Find all directories with pyproject.toml
    all_projects = [
        item
        for item in workspace_root.iterdir()
        if item.is_dir()
        and (item / "pyproject.toml").exists()
        and item.name not in ignore_list
        and not any(skip in item.name for skip in [".git", ".venv", "__pycache__"])
    ]

    # Apply filter if provided
    if projects_filter:
        filtered_projects = [
            project for project in all_projects if project.name in projects_filter
        ]
        return sorted(filtered_projects, key=lambda p: p.name)

    return sorted(all_projects, key=lambda p: p.name)
