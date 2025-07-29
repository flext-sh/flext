#!/usr/bin/env python3
"""Common utilities for FLEXT scripts."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


def discover_projects(
    workspace_root: Path,
    projects_filter: Sequence[str] | None = None,
) -> list[Path]:
    """Discover FLEXT projects in workspace.

    Args:
        workspace_root: Root directory of workspace
        projects_filter: Optional list of project names to include

    Returns:
        List of project paths sorted by name

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
