#!/usr/bin/env python3
"""Common utilities for FLEXT scripts."""

from __future__ import annotations

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
          >>> core_projects = discover_projects(
          ...     workspace, ["flext-core", "flext-api"]
          ... )
          >>> print([p.name for p in core_projects])
          ['flext-api', 'flext-core']

    Note:
          The following directories are automatically ignored:
          - client-a-oud-mig (legacy service)
          - client-b-meltano-native (specialized service)
          - flexcore (Go service)
          - System directories (.git, .venv, __pycache__)



    Args:
      workspace_root (Path): Description.
      projects_filter (Sequence[str] | None): Description.

    Returns:
      list[Path]: Description.

    """  # Projects to ignore (these are services, not libraries)
    ignore_list = {"client-a-oud-mig", "client-b-meltano-native", "flexcore"}

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
