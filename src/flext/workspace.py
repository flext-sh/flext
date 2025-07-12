"""Workspace management for FLEXT multi-project setup."""

import os
import sys
from pathlib import Path


class WorkspaceManager:
    """Manages the FLEXT workspace with multiple projects."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize WorkspaceManager with workspace root."""
        self.workspace_root = workspace_root or Path.cwd()
        self.projects = self._discover_projects()

    def _discover_projects(self) -> list[Path]:
        """Discover all FLEXT projects in the workspace."""
        projects = []
        for item in self.workspace_root.iterdir():
            if item.is_dir() and item.name.startswith("flext-"):
                pyproject = item / "pyproject.toml"
                if pyproject.exists():
                    projects.append(item)
        return projects

    def get_project_info(self, project_name: str) -> dict[str, str] | None:
        """Get information about a specific project."""
        for project_path in self.projects:
            if project_path.name == project_name:
                return {
                    "name": project_path.name,
                    "path": str(project_path),
                    "type": "flext-module",
                }
        return None

    def list_projects(self) -> list[str]:
        """List all projects in the workspace."""
        return [project.name for project in self.projects]

    def get_project_dependencies(self, project_name: str) -> list[str]:
        """Get dependencies for a specific project."""
        # This would analyze pyproject.toml files
        # For now, return empty list
        return []

    def validate_workspace(self) -> bool:
        """Validate the workspace structure."""
        # Check if this is a valid FLEXT workspace
        if not (self.workspace_root / "pyproject.toml").exists():
            return False

        # Check if at least one FLEXT project exists
        return len(self.projects) > 0

    def setup_environment(self) -> None:
        """Setup workspace environment variables."""
        os.environ["FLEXT_WORKSPACE_ROOT"] = str(self.workspace_root)

        # Add workspace to Python path
        workspace_src = self.workspace_root / "src"
        if workspace_src.exists():
            sys.path.insert(0, str(workspace_src))
