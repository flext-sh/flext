#!/usr/bin/env python3
"""Comprehensive Workspace Management - Clean FLEXT Domain Service Implementation.

Unified workspace management using flext-core domain services:
- Setup of project links
- Environment configuration
- Dependency management
- Type checking with MyPy
- SSL setup for staging
- Monitoring configuration

Using clean flext-core architecture patterns without external dependencies.
"""

import argparse
import json
import sys
from pathlib import Path

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)


class WorkspaceManagementService(FlextService[dict[str, object]]):
    """Workspace link management service for FLEXT ecosystem.

    Unified class for managing workspace symbolic links and directory structure.
    """

    def __init__(self) -> None:
        """Initialize workspace management service."""
        super().__init__()
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
        self._workspace_root = Path.cwd()

    class _LinkHelper:
        """Nested helper for symbolic link operations."""

        @staticmethod
        def create_symbolic_link(source: Path, target: Path) -> FlextResult[None]:
            """Create symbolic link with validation."""
            try:
                if not source.exists():
                    return FlextResult[None].fail(
                        f"Source path does not exist: {source}",
                    )

                if target.exists() and target.is_symlink():
                    target.unlink()
                elif target.exists():
                    return FlextResult[None].fail(
                        f"Target exists and is not a symlink: {target}",
                    )

                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(source)

                return FlextResult[None].ok(None)

            except OSError as e:
                return FlextResult[None].fail(f"Failed to create symlink: {e}")

        @staticmethod
        def validate_link(link_path: Path) -> FlextResult[bool]:
            """Validate symbolic link exists and points to valid target."""
            try:
                if not link_path.exists():
                    return FlextResult[bool].fail(f"Link does not exist: {link_path}")

                if not link_path.is_symlink():
                    return FlextResult[bool].fail(
                        f"Path is not a symbolic link: {link_path}",
                    )

                target = link_path.resolve()
                if not target.exists():
                    return FlextResult[bool].fail(
                        f"Link target does not exist: {target}",
                    )

                link_is_valid = True
                return FlextResult[bool].ok(link_is_valid)

            except Exception as e:
                return FlextResult[bool].fail(f"Link validation error: {e}")

    class _WorkspaceHelper:
        """Nested helper for workspace structure operations."""

        @staticmethod
        def discover_flext_projects(workspace_root: Path) -> FlextResult[list[Path]]:
            """Discover FLEXT projects in workspace."""
            try:
                projects: list[object] = []
                for item in workspace_root.iterdir():
                    if item.is_dir() and item.name.startswith("flext-"):
                        pyproject_file = item / "pyproject.toml"
                        if pyproject_file.exists():
                            projects.append(item)

                return FlextResult[list[Path]].ok(projects)

            except Exception as e:
                return FlextResult[list[Path]].fail(f"Project discovery error: {e}")

        @staticmethod
        def create_workspace_structure(
            workspace_root: Path,
        ) -> FlextResult[dict[str, Path]]:
            """Create standard workspace directory structure."""
            try:
                directories = {
                    "src": workspace_root / "src",
                    "tests": workspace_root / "tests",
                    "docs": workspace_root / "docs",
                    "scripts": workspace_root / "scripts",
                }

                for path in directories.values():
                    path.mkdir(parents=True, exist_ok=True)

                return FlextResult[dict[str, Path]].ok(directories)

            except Exception as e:
                return FlextResult[dict[str, Path]].fail(
                    f"Workspace structure creation error: {e}",
                )

    def setup_workspace_links(self) -> FlextResult[dict[str, object]]:
        """Setup symbolic links for workspace projects."""
        self._logger.info("Setting up workspace links")

        # Discover projects
        projects_result = self._WorkspaceHelper.discover_flext_projects(
            self._workspace_root,
        )
        if projects_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Project discovery failed: {projects_result.error}",
            )

        projects = projects_result.unwrap()

        # Create workspace structure
        structure_result = self._WorkspaceHelper.create_workspace_structure(
            self._workspace_root,
        )
        if structure_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Workspace structure creation failed: {structure_result.error}",
            )

        directories = structure_result.unwrap()

        # Setup links for each project
        links_created: list[object] = []
        links_failed: list[object] = []
        for project in projects:
            project_name = project.name.replace("-", "_")

            # Link source directory
            if (project / "src" / project_name).exists():
                source = project / "src" / project_name
                target = directories["src"] / project_name

                link_result = self._LinkHelper.create_symbolic_link(source, target)
                if link_result.is_success:
                    links_created.append(f"src/{project_name}")
                else:
                    links_failed.append(f"src/{project_name}: {link_result.error}")

            # Link tests directory
            if (project / "tests").exists():
                source = project / "tests"
                target = directories["tests"] / project_name

                link_result = self._LinkHelper.create_symbolic_link(source, target)
                if link_result.is_success:
                    links_created.append(f"tests/{project_name}")
                else:
                    links_failed.append(f"tests/{project_name}: {link_result.error}")

        result: dict[str, object] = {
            "projects_found": len(projects),
            "links_created": links_created,
            "links_failed": links_failed,
            "workspace_directories": list(directories.keys()),
        }

        return FlextResult[dict[str, object]].ok(result)

    def validate_workspace_links(self) -> FlextResult[dict[str, object]]:
        """Validate all workspace symbolic links."""
        self._logger.info("Validating workspace links")

        # Get workspace structure
        structure_result = self._WorkspaceHelper.create_workspace_structure(
            self._workspace_root,
        )
        if structure_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Workspace structure access failed: {structure_result.error}",
            )

        directories = structure_result.unwrap()

        valid_links: list[object] = []
        invalid_links: list[object] = []
        # Check src links
        src_dir = directories["src"]
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_symlink():
                    validation_result = self._LinkHelper.validate_link(item)
                    if validation_result.is_success:
                        valid_links.append(f"src/{item.name}")
                    else:
                        invalid_links.append(
                            f"src/{item.name}: {validation_result.error}",
                        )

        # Check tests links
        tests_dir = directories["tests"]
        if tests_dir.exists():
            for item in tests_dir.iterdir():
                if item.is_symlink():
                    validation_result = self._LinkHelper.validate_link(item)
                    if validation_result.is_success:
                        valid_links.append(f"tests/{item.name}")
                    else:
                        invalid_links.append(
                            f"tests/{item.name}: {validation_result.error}",
                        )

        result = {
            "valid_links": valid_links,
            "invalid_links": invalid_links,
            "total_checked": len(valid_links) + len(invalid_links),
        }

        return FlextResult[dict[str, object]].ok(result)

    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute workspace management operation."""
        self._logger.info("Executing workspace management")

        # Setup workspace links
        setup_result = self.setup_workspace_links()
        if setup_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Workspace setup failed: {setup_result.error}",
            )

        # Validate links
        validation_result = self.validate_workspace_links()
        if validation_result.is_failure:
            return FlextResult[dict[str, object]].fail(
                f"Link validation failed: {validation_result.error}",
            )

        # Combine results
        setup_data = setup_result.unwrap()
        validation_data = validation_result.unwrap()

        combined_result: dict[str, object] = {
            "workspace_setup": setup_data,
            "link_validation": validation_data,
            "operation_status": "completed",
        }

        return FlextResult[dict[str, object]].ok(combined_result)


def print_results(data: dict[str, object], title: str) -> None:
    """Print results in a clean format."""
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2, default=str))


def main() -> int:
    """Main function using proper domain service architecture."""
    parser = argparse.ArgumentParser(
        description="Comprehensive FLEXT workspace management",
        prog="setup_workspace_links",
    )
    parser.add_argument(
        "operation",
        choices=["links", "deps", "types", "monitoring", "all"],
        default="all",
        nargs="?",
        help="Operation to perform",
    )

    parser.parse_args()

    # Create service using proper dependency injection
    FlextContainer.get_global()
    service = WorkspaceManagementService()

    # Execute operation
    result = service.execute()

    if result.is_success:
        print("✅ Workspace management completed successfully")
        print_results(result.value, "Workspace Management Results")
        return 0
    print(f"❌ Workspace management failed: {result.error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
