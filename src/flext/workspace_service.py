"""FLEXT Workspace Service - Single Responsibility Service.

Unified workspace service using flext-core exclusively with proper separation of concerns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Self, runtime_checkable

from flext_core import FlextCore


class FlextWorkspaceService(FlextCore.Service[str]):
    """Unified workspace service using flext-core utilities exclusively.

    Eliminates ALL wrapper methods and SOLID violations, using flext-core
    utilities directly without abstraction layers. Uses SOURCE OF TRUTH
    principle for all workspace operations and metadata loading.

    ANTI-DUPLICATION: NO local implementations - uses flext-core extensively.
    DOMAIN SEPARATION: Workspace operations only, NO CLI or tools functionality.

    SOLID Principles Applied:
        - Single Responsibility: Workspace management only
        - Open/Closed: Extensible through flext-core patterns
        - Dependency Inversion: Uses FlextCore.Container for dependencies
        - Interface Segregation: Focused workspace interface
    """

    def __init__(self, **_data: FlextCore.Types.Dict) -> None:
        """Initialize workspace service with flext-core patterns."""
        super().__init__()
        self._logger = FlextCore.Logger(__name__)
        self._container = FlextCore.Container.get_global()
        self._workspace_root = Path.cwd()

    @runtime_checkable
    class ProjectDiscoveryServiceProtocol(Protocol):
        """Protocol for project discovery services."""

        def discover_projects(
            self, workspace_root: Path
        ) -> FlextCore.Result[list[FlextCore.Models.Project]]:
            """Discover projects in workspace."""
            ...

    @runtime_checkable
    class WorkspaceValidatorProtocol(Protocol):
        """Protocol for workspace validation services."""

        def validate_workspace_path(self, path: str) -> FlextCore.Result[str]:
            """Validate workspace path."""
            ...

    class _ProjectDiscoveryService:
        """Nested project discovery service."""

        def __init__(self, manager: FlextWorkspaceService) -> None:
            self._manager = manager

        def discover_projects(
            self, workspace_root: Path
        ) -> FlextCore.Result[list[FlextCore.Models.Project]]:
            """Discover all projects in workspace with type detection."""
            try:
                projects: list[FlextCore.Models.Project] = []
                for project_dir in workspace_root.iterdir():
                    if not project_dir.is_dir() or project_dir.name.startswith("."):
                        continue

                    project_info_result: FlextCore.Result[FlextCore.Models.Project] = (
                        self._analyze_project(project_dir)
                    )
                    if project_info_result.is_success:
                        projects.append(project_info_result.unwrap())

                return FlextCore.Result[list[FlextCore.Models.Project]].ok(projects)

            except Exception as e:
                error = f"Project discovery failed: {e}"
                # Use manager's public logging interface
                logger = FlextCore.Logger(__name__)
                logger.exception(error)
                return FlextCore.Result[list[FlextCore.Models.Project]].fail(error)

        def _analyze_project(
            self, project_path: Path
        ) -> FlextCore.Result[FlextCore.Models.Project]:
            """Analyze individual project for type and characteristics."""
            try:
                # Detect project type using FlextCore.Types.Project.ProjectType
                project_type: FlextCore.Types.Project.ProjectType = "application"
                has_pyproject = (project_path / "pyproject.toml").exists()
                has_go_mod = (project_path / "go.mod").exists()
                has_package_json = (project_path / "package.json").exists()

                if has_pyproject or (project_path / "setup.py").exists():
                    project_type = "PYTHON"
                elif has_go_mod:
                    project_type = "GO"
                elif has_package_json:
                    project_type = "JAVASCRIPT"

                # Count test files
                tests_dir = project_path / "tests"
                has_tests = tests_dir.exists()
                # Test count tracking removed as unused

                project_info = FlextCore.Models.Project(
                    name=project_path.name,
                    organization_id="default",
                    repository_path=str(project_path),
                    is_test_project=has_tests,
                    test_framework="pytest" if has_tests else None,
                    project_type=project_type,
                    domain_events=[],
                )

                return FlextCore.Result[FlextCore.Models.Project].ok(project_info)

            except Exception as e:
                error = f"Project analysis failed for {project_path.name}: {e}"
                return FlextCore.Result[FlextCore.Models.Project].fail(error)

    class _WorkspaceValidator:
        """Nested workspace validation service."""

        def __init__(self, manager: FlextWorkspaceService) -> None:
            self._manager = manager

        def validate_workspace_path(self, path: str) -> FlextCore.Result[str]:
            """Validate workspace path."""
            try:
                workspace_path = Path(path)
                if not workspace_path.exists():
                    return FlextCore.Result[str].fail(
                        f"Workspace path does not exist: {path}"
                    )
                if not workspace_path.is_dir():
                    return FlextCore.Result[str].fail(
                        f"Workspace path is not a directory: {path}"
                    )
                return FlextCore.Result[str].ok(str(workspace_path.resolve()))
            except Exception as e:
                return FlextCore.Result[str].fail(
                    f"Workspace path validation failed: {e}"
                )

    def create_project_discovery(self: Self) -> _ProjectDiscoveryService:
        """Create project discovery service."""
        return self._ProjectDiscoveryService(self)

    def create_workspace_validator(self: Self) -> _WorkspaceValidator:
        """Create workspace validator service."""
        return self._WorkspaceValidator(self)

    def discover_workspace_projects(
        self, workspace_root: str | None = None
    ) -> FlextCore.Result[list[FlextCore.Models.Project]]:
        """Discover all projects in the workspace."""
        discovery_service = self.create_project_discovery()
        workspace_path = (
            Path(workspace_root) if workspace_root else self._workspace_root
        )
        return discovery_service.discover_projects(workspace_path)

    def validate_workspace_path(self, path: str) -> FlextCore.Result[str]:
        """Validate workspace path."""
        validator = self.create_workspace_validator()
        return validator.validate_workspace_path(path)

    def get_workspace_info(
        self, workspace_root: str | None = None
    ) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Get comprehensive workspace information."""
        try:
            workspace_path = (
                Path(workspace_root) if workspace_root else self._workspace_root
            )

            # Discover projects
            projects_result: FlextCore.Result[list[FlextCore.Models.Project]] = (
                self.discover_workspace_projects(str(workspace_path))
            )
            if projects_result.is_failure:
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    f"Failed to discover projects: {projects_result.error}"
                )

            projects = projects_result.unwrap()
            project_names = [p.name for p in projects]

            # Calculate total size (mock for now)
            total_size_mb = len(projects) * 10.5  # Mock calculation

            workspace_info: FlextCore.Types.Dict = {
                "name": workspace_path.name,
                "path": str(workspace_path),
                "project_count": len(projects),
                "total_size_mb": total_size_mb,
                "projects": project_names,
                "status": "ready",
            }

            return FlextCore.Result[FlextCore.Types.Dict].ok(workspace_info)

        except Exception as e:
            error = f"Failed to get workspace info: {e}"
            self._logger.exception(error)
            return FlextCore.Result[FlextCore.Types.Dict].fail(error)

    def execute(self: Self) -> FlextCore.Result[str]:
        """Execute workspace service - required by FlextCore.Service abstract method."""
        try:
            workspace_info_result: FlextCore.Result[FlextCore.Types.Dict] = (
                self.get_workspace_info()
            )
            if workspace_info_result.is_failure:
                return FlextCore.Result[str].fail(
                    f"Workspace service execution failed: {workspace_info_result.error}"
                )

            workspace_info = workspace_info_result.unwrap()
            return FlextCore.Result[str].ok(
                f"Workspace service ready: {workspace_info['name']} ({workspace_info['project_count']} projects)"
            )

        except Exception as e:
            error = f"Workspace service execution failed: {e}"
            self._logger.exception(error)
            return FlextCore.Result[str].fail(error)


# LEGACY ALIASES ELIMINATED - Access protocols directly through service:
# Use: FlextWorkspaceService.ProjectDiscoveryServiceProtocol
# Use: FlextWorkspaceService.WorkspaceValidatorProtocol


# Factory function for creating service instances
def create_workspace_service() -> FlextWorkspaceService:
    """Create workspace service with flext-core patterns."""
    return FlextWorkspaceService()


__all__ = [
    "FlextWorkspaceService",
    "create_workspace_service",
]
