"""FLEXT Workspace Service - Single Responsibility Service.

Unified workspace service using flext-core exclusively with proper separation of concerns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""
from typing import Protocol, Self, runtime_checkable


from __future__ import annotations

from pathlib import Path

from flext_core import (, FlextTypes
    FlextContainer,
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextService,
    FlextTypes,
)


class FlextWorkspaceService(FlextService[str]):
    """Unified workspace service using flext-core utilities exclusively.

    Eliminates ALL wrapper methods and SOLID violations, using flext-core
    utilities directly without abstraction layers. Uses SOURCE OF TRUTH
    principle for all workspace operations and metadata loading.

    ANTI-DUPLICATION: NO local implementations - uses flext-core extensively.
    DOMAIN SEPARATION: Workspace operations only, NO CLI or tools functionality.

    SOLID Principles Applied:
        - Single Responsibility: Workspace management only
        - Open/Closed: Extensible through flext-core patterns
        - Dependency Inversion: Uses FlextContainer for dependencies
        - Interface Segregation: Focused workspace interface
    """

    def __init__(self, **_data: dict[str, object]) -> None:
        """Initialize workspace service with flext-core patterns."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._workspace_root = Path.cwd()

    @runtime_checkable
    class ProjectDiscoveryServiceProtocol(Protocol):
        """Protocol for project discovery services."""

        def discover_projects(
            self, workspace_root: Path
        ) -> FlextResult[list[FlextModels.Project]]:
            """Discover projects in workspace."""
            ...

    @runtime_checkable
    class WorkspaceValidatorProtocol(Protocol):
        """Protocol for workspace validation services."""

        def validate_workspace_path(self, path: str) -> FlextResult[str]:
            """Validate workspace path."""
            ...

    class _ProjectDiscoveryService:
        """Nested project discovery service."""

        def __init__(self, manager: FlextWorkspaceService) -> None:
            self._manager = manager

        def discover_projects(
            self, workspace_root: Path
        ) -> FlextResult[list[FlextModels.Project]]:
            """Discover all projects in workspace with type detection."""
            try:
                projects: list[FlextModels.Project] = []
                for project_dir in workspace_root.iterdir():
                    if not project_dir.is_dir() or project_dir.name.startswith("."):
                        continue

                    project_info_result: FlextResult[FlextModels.Project] = self._analyze_project(project_dir)
                    if project_info_result.is_success:
                        projects.append(project_info_result.unwrap())

                return FlextResult[list[FlextModels.Project]].ok(projects)

            except Exception as e:
                error = f"Project discovery failed: {e}"
                # Use manager's public logging interface
                logger = FlextLogger(__name__)
                logger.exception(error)
                return FlextResult[list[FlextModels.Project]].fail(error)

        def _analyze_project(
            self, project_path: Path
        ) -> FlextResult[FlextModels.Project]:
            """Analyze individual project for type and characteristics."""
            try:
                # Detect project type using FlextTypes.Project.ProjectType
                project_type: FlextTypes.Project.ProjectType = "application"
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

                project_info = FlextModels.Project(
                    name=project_path.name,
                    organization_id="default",
                    repository_path=str(project_path),
                    is_test_project=has_tests,
                    test_framework="pytest" if has_tests else None,
                    project_type=project_type,
                    domain_events=[],
                )

                return FlextResult[FlextModels.Project].ok(project_info)

            except Exception as e:
                error = f"Project analysis failed for {project_path.name}: {e}"
                return FlextResult[FlextModels.Project].fail(error)

    class _WorkspaceValidator:
        """Nested workspace validation service."""

        def __init__(self, manager: FlextWorkspaceService) -> None:
            self._manager = manager

        def validate_workspace_path(self, path: str) -> FlextResult[str]:
            """Validate workspace path."""
            try:
                workspace_path = Path(path)
                if not workspace_path.exists():
                    return FlextResult[str].fail(
                        f"Workspace path does not exist: {path}"
                    )
                if not workspace_path.is_dir():
                    return FlextResult[str].fail(
                        f"Workspace path is not a directory: {path}"
                    )
                return FlextResult[str].ok(str(workspace_path.resolve()))
            except Exception as e:
                return FlextResult[str].fail(f"Workspace path validation failed: {e}")

    def create_project_discovery(self: Self) -> _ProjectDiscoveryService:
        """Create project discovery service."""
        return self._ProjectDiscoveryService(self)

    def create_workspace_validator(self: Self) -> _WorkspaceValidator:
        """Create workspace validator service."""
        return self._WorkspaceValidator(self)

    def discover_workspace_projects(
        self, workspace_root: str | None = None
    ) -> FlextResult[list[FlextModels.Project]]:
        """Discover all projects in the workspace."""
        discovery_service = self.create_project_discovery()
        workspace_path = (
            Path(workspace_root) if workspace_root else self._workspace_root
        )
        return discovery_service.discover_projects(workspace_path)

    def validate_workspace_path(self, path: str) -> FlextResult[str]:
        """Validate workspace path."""
        validator = self.create_workspace_validator()
        return validator.validate_workspace_path(path)

    def get_workspace_info(
        self, workspace_root: str | None = None
    ) -> FlextResult[dict[str, object]]:
        """Get comprehensive workspace information."""
        try:
            workspace_path = (
                Path(workspace_root) if workspace_root else self._workspace_root
            )

            # Discover projects
            projects_result: FlextResult[list[FlextModels.Project]] = self.discover_workspace_projects(str(workspace_path))
            if projects_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to discover projects: {projects_result.error}"
                )

            projects = projects_result.unwrap()
            project_names = [p.name for p in projects]

            # Calculate total size (mock for now)
            total_size_mb = len(projects) * 10.5  # Mock calculation

            workspace_info: dict[str, object] = {
                "name": workspace_path.name,
                "path": str(workspace_path),
                "project_count": len(projects),
                "total_size_mb": total_size_mb,
                "projects": project_names,
                "status": "ready",
            }

            return FlextResult[dict[str, object]].ok(workspace_info)

        except Exception as e:
            error = f"Failed to get workspace info: {e}"
            self._logger.exception(error)
            return FlextResult[dict[str, object]].fail(error)

    def execute(self: Self) -> FlextResult[str]:
        """Execute workspace service - required by FlextService abstract method."""
        try:
            workspace_info_result: FlextResult[dict[str, object]] = self.get_workspace_info()
            if workspace_info_result.is_failure:
                return FlextResult[str].fail(
                    f"Workspace service execution failed: {workspace_info_result.error}"
                )

            workspace_info = workspace_info_result.unwrap()
            return FlextResult[str].ok(
                f"Workspace service ready: {workspace_info['name']} ({workspace_info['project_count']} projects)"
            )

        except Exception as e:
            error = f"Workspace service execution failed: {e}"
            self._logger.exception(error)
            return FlextResult[str].fail(error)


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
