#!/usr/bin/env python3
"""Dependency Management Module

Analyzes and standardizes dependencies across all workspace projects.
Based on scripts/utilities/dependency_analysis.py and standardize_dependencies.py functionality.
"""

import re
import shutil
import tomllib
from pathlib import Path
from typing import Any

import tomli_w
from rich.console import Console
from rich.table import Table

from .base import CustomFixModule, Issue


class DependencyManagementModule(CustomFixModule):
    """Module for analyzing and standardizing dependencies across workspace."""

    name = "dependency_management"
    description = "Analyzes and standardizes dependencies across workspace projects"

    # Standard dependency versions (enterprise-compatible)
    STANDARD_VERSIONS = {
        # Core Python
        "python": "^3.13",
        # Core framework dependencies
        "pydantic": "^2.11.5",
        "pydantic-settings": "^2.9.1",
        "sqlalchemy": "^2.0.36",
        "fastapi": "^0.115.6",
        "uvicorn": "^0.32.1",
        "httpx": "^0.28.1",
        "anyio": "^4.9.0",
        # Database
        "cx-oracle": "^8.3.0",
        "oracledb": "^2.5.0",
        "alembic": "^1.14.0",
        "aiosqlite": "^0.21.0",
        # Authentication & Security
        "PyJWT": "^2.10.1",
        "cryptography": "^43.0.0",
        "authlib": "^1.3.0",
        # CLI & UI
        "click": "^8.2.1",
        "typer": "^0.15.1",
        "rich": "^14.0.0",
        "fire": "^0.7.0",
        # Data processing
        "pandas": "^2.2.3",
        "pyarrow": "^18.1.0",
        "openpyxl": "^3.1.5",
        "tabulate": "^0.9.0",
        "lxml": "^5.3.0",
        # Configuration & environment
        "python-dotenv": "^1.0.1",
        "pyyaml": "^6.0.2",
        "toml": "^0.10.2",
        "tomli": "^2.2.1",
        "tomli-w": "^1.1.0",
        # Async & concurrency
        "asyncio": "*",
        "aiohttp": "^3.11.10",
        "aiofiles": "^24.1.0",
        # Logging & monitoring
        "structlog": "^24.4.0",
        "loguru": "^0.7.2",
        # Testing
        "pytest": "^8.4.0",
        "pytest-cov": "^6.1.1",
        "pytest-mock": "^3.14.0",
        "pytest-asyncio": "^0.24.0",
        # Code quality
        "mypy": "^1.16.0",
        "ruff": "^0.11.13",
        "black": "^25.1.0",
        "isort": "^6.0.1",
        "bandit": "^1.8.0",
        # Singer SDK specific
        "singer-sdk": "^0.40.0",
        "requests": "^2.32.3",
        "backoff": "^2.2.1",
        # Type stubs
        "types-requests": "^2.32.0",
        "types-PyYAML": "^6.0.12",
    }

    # Required development dependencies
    REQUIRED_DEV_DEPS = {
        "pytest": "^8.4.0",
        "pytest-cov": "^6.1.1",
        "pytest-mock": "^3.14.0",
        "pytest-asyncio": "^0.24.0",
        "mypy": "^1.16.0",
        "ruff": "^0.11.13",
        "black": "^25.1.0",
        "isort": "^6.0.1",
        "pre-commit": "^4.2.0",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.projects: dict[str, dict[str, Any]] = {}
        self.all_dependencies: dict[str, dict[str, str]] = {}
        self.version_conflicts: list[dict[str, Any]] = []
        self.missing_dependencies: list[dict[str, Any]] = []

    def find_pyproject_files(self, workspace_path: Path) -> list[Path]:
        """Find all pyproject.toml files in workspace."""
        pyproject_files: list = []

        # Look for pyproject.toml files in all subdirectories
        for pyproject_path in workspace_path.rglob("pyproject.toml"):
            # Skip cache and venv directories
            if any(
                part.startswith(".")
                and part in {".venv", ".mypy_cache", ".pytest_cache"}
                for part in pyproject_path.parts
            ):
                continue
            pyproject_files.append(pyproject_path)

        return pyproject_files

    def parse_version_spec(self, version_spec: str) -> tuple[str, str]:
        """Parse version specification to extract operator and version."""
        if isinstance(version_spec, dict):
            # Handle local path dependencies
            return "path", version_spec.get("path", "")

        version_str = str(version_spec)

        # Handle complex version specs like "^3.13,<3.15"
        if "," in version_str:
            parts = version_str.split(",")
            main_spec = parts[0].strip()
            main_spec = version_str.strip()

        # Extract operator and version
        match = re.match(r"([~^>=<!]*)(.*)", main_spec)
        if match:
            operator, version = match.groups()
            return operator or "==", version.strip()

        return "==", version_str

    def analyze_dependencies(self, workspace_path: Path) -> dict[str, Any]:
        """Analyze all dependencies across projects."""
        pyproject_files = self.find_pyproject_files(workspace_path)

        for pyproject_path in pyproject_files:
            project_name = pyproject_path.parent.name

            try:
                with open(pyproject_path, "rb") as f:
                    config = tomllib.load(f)

                self.projects[project_name] = {"path": pyproject_path, "config": config}

                # Extract dependencies
                poetry_config = config.get("tool", {}).get("poetry", {})
                dependencies = poetry_config.get("dependencies", {})

                # Extract dev dependencies
                dev_deps: dict = {}
                groups = poetry_config.get("group", {})
                if "dev" in groups:
                    dev_deps = groups["dev"].get("dependencies", {})

                all_deps = {**dependencies, **dev_deps}

                for dep_name, dep_version in all_deps.items():
                    if dep_name == "python":
                        continue

                    if dep_name not in self.all_dependencies:
                        self.all_dependencies[dep_name] = {}

                    self.all_dependencies[dep_name][project_name] = str(dep_version)

            except Exception as e:
                if self.verbose:
                    self.console.print(
                        f"[red]Error parsing {pyproject_path}: {e}[/red]",
                    )

        # Analyze conflicts
        self._analyze_version_conflicts()
        self._analyze_missing_dependencies()

        return {
            "projects": len(self.projects),
            "dependencies": len(self.all_dependencies),
            "conflicts": len(self.version_conflicts),
            "missing": len(self.missing_dependencies),
        }

    def _analyze_version_conflicts(self) -> None:
        """Analyze version conflicts across projects."""
        for dep_name, project_versions in self.all_dependencies.items():
            if len(project_versions) <= 1:
                continue

            # Check for version conflicts
            versions = set(project_versions.values())
            if len(versions) > 1:
                self.version_conflicts.append(
                    {
                        "dependency": dep_name,
                        "versions": dict(project_versions),
                        "standard_version": self.STANDARD_VERSIONS.get(dep_name),
                    },
                )

    def _analyze_missing_dependencies(self) -> None:
        """Analyze missing required dependencies."""
        for project_name, project_data in self.projects.items():
            config = project_data["config"]
            poetry_config = config.get("tool", {}).get("poetry", {})

            # Check dev dependencies
            groups = poetry_config.get("group", {})
            dev_deps = groups.get("dev", {}).get("dependencies", {}) if groups else {}

            for req_dep, req_version in self.REQUIRED_DEV_DEPS.items():
                if req_dep not in dev_deps:
                    self.missing_dependencies.append(
                        {
                            "project": project_name,
                            "dependency": req_dep,
                            "required_version": req_version,
                            "type": "dev",
                        },
                    )

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze individual pyproject.toml for dependency issues."""
        issues: list = []

        if file_path.name == "pyproject.toml":
            try:
                with open(file_path, "rb") as f:
                    config = tomllib.load(f)

                poetry_config = config.get("tool", {}).get("poetry", {})
                dependencies = poetry_config.get("dependencies", {})

                # Check for version conflicts with standards
                for dep_name, dep_version in dependencies.items():
                    if dep_name == "python":
                        continue

                    standard_version = self.STANDARD_VERSIONS.get(dep_name)
                    if standard_version and str(dep_version) != standard_version:
                        issues.append(
                            Issue(
                                line=1,
                                column=1,
                                code="DEP001",
                                message=f"Dependency {dep_name} version {dep_version} conflicts with standard {standard_version}",
                                suggestion=f"Update to standard version: {standard_version}",
                            ),
                        )

                # Check for missing required dev dependencies
                groups = poetry_config.get("group", {})
                dev_deps = (
                    groups.get("dev", {}).get("dependencies", {}) if groups else {}
                )

                for req_dep, req_version in self.REQUIRED_DEV_DEPS.items():
                    if req_dep not in dev_deps:
                        issues.append(
                            Issue(
                                line=1,
                                column=1,
                                code="DEP002",
                                message=f"Missing required dev dependency: {req_dep}",
                                suggestion=f'Add dev dependency: {req_dep} = "{req_version}"',
                            ),
                        )

            except Exception as e:
                issues.append(
                    Issue(
                        line=1,
                        column=1,
                        code="DEP003",
                        message=f"Failed to analyze dependencies: {e}",
                        suggestion="Check pyproject.toml format and syntax",
                    ),
                )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply dependency fixes (handled at workspace level)."""
        return content

    def standardize_dependencies(self, workspace_path: Path = None) -> bool:
        """Standardize dependencies across all projects."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Standardizing dependencies in: {workspace_path}[/blue]",
            )

        # Analyze current state
        analysis = self.analyze_dependencies(workspace_path)

        if self.verbose:
            self.console.print(
                f"[green]Found {analysis['projects']} projects with {
                    analysis['dependencies']
                } unique dependencies[/green]",
            )
            if analysis["conflicts"] > 0:
                self.console.print(
                    f"[yellow]Detected {
                        analysis['conflicts']
                    } version conflicts[/yellow]",
                )
            if analysis["missing"] > 0:
                self.console.print(
                    f"[yellow]Found {
                        analysis['missing']
                    } missing required dependencies[/yellow]",
                )

        # Show conflicts
        if self.version_conflicts and self.verbose:
            self._show_conflicts_table()

        # Apply standardization
        standardized_count = 0
        for _project_name, project_data in self.projects.items():
            if self._standardize_project(project_data):
                standardized_count += 1

        if self.verbose:
            action = "Would standardize" if self.dry_run else "Standardized"
            self.console.print(
                f"[bold green]{action} {standardized_count} projects[/bold green]",
            )

        return True

    def _show_conflicts_table(self) -> None:
        """Show dependency conflicts in a table."""
        table = Table(title="Dependency Version Conflicts")
        table.add_column("Dependency", style="cyan")
        table.add_column("Projects", style="yellow")
        table.add_column("Standard Version", style="green")

        for conflict in self.version_conflicts:
            dep_name = conflict["dependency"]
            versions = conflict["versions"]
            standard = conflict.get("standard_version", "N/A")

            project_versions: list = []
            for project, version in versions.items():
                project_versions.append(f"{project}: {version}")

            table.add_row(dep_name, "\n".join(project_versions), standard)

        self.console.print(table)

    def _standardize_project(self, project_data: dict[str, Any]) -> bool:
        """Standardize a single project's dependencies."""
        pyproject_path = project_data["path"]
        config = project_data["config"].copy()

        changes_made: list = []

        # Update dependencies
        poetry_config = config.setdefault("tool", {}).setdefault("poetry", {})
        dependencies = poetry_config.setdefault("dependencies", {})

        for dep_name, dep_version in dependencies.items():
            if dep_name == "python":
                continue

            standard_version = self.STANDARD_VERSIONS.get(dep_name)
            if standard_version and str(dep_version) != standard_version:
                dependencies[dep_name] = standard_version
                changes_made.append(
                    f"Updated {dep_name}: {dep_version} → {standard_version}",
                )

        # Add missing dev dependencies
        groups = poetry_config.setdefault("group", {})
        dev_group = groups.setdefault("dev", {})
        dev_deps = dev_group.setdefault("dependencies", {})

        for req_dep, req_version in self.REQUIRED_DEV_DEPS.items():
            if req_dep not in dev_deps:
                dev_deps[req_dep] = req_version
                changes_made.append(f"Added dev dependency: {req_dep} = {req_version}")

        if not changes_made:
            if self.verbose:
                project_name = pyproject_path.parent.name
                self.console.print(
                    f"[green]✅ {project_name} already standardized[/green]",
                )
            return True

        if self.dry_run:
            if self.verbose:
                project_name = pyproject_path.parent.name
                self.console.print(
                    f"[cyan][DRY RUN] Would apply changes to {project_name}:[/cyan]",
                )
                for change in changes_made:
                    self.console.print(f"[cyan]  - {change}[/cyan]")
            return True

        if self.interactive:
            project_name = pyproject_path.parent.name
            self.console.print(f"[yellow]Proposed changes for {project_name}:[/yellow]")
            for change in changes_made:
                self.console.print(f"[yellow]  - {change}[/yellow]")

            from rich.prompt import Confirm

            if not Confirm.ask("Apply these changes?"):
                self.console.print("[red]Standardization cancelled[/red]")
                return False

        # Write updated configuration
        try:
            # Create backup
            backup_path = pyproject_path.with_suffix(".toml.backup")
            shutil.copy2(pyproject_path, backup_path)

            # Write updated file
            with open(pyproject_path, "wb") as f:
                tomli_w.dump(config, f)

            if self.verbose:
                project_name = pyproject_path.parent.name
                self.console.print(f"[green]✅ Standardized {project_name}[/green]")
                for change in changes_made:
                    self.console.print(f"[green]  ✓ {change}[/green]")

            return True

        except Exception as e:
            if self.verbose:
                project_name = pyproject_path.parent.name
                self.console.print(
                    f"[red]❌ Failed to standardize {project_name}: {e}[/red]",
                )
            return False

    def run_workspace_standardization(self, workspace_path: Path = None) -> bool:
        """Run dependency standardization across the entire workspace."""
        return self.standardize_dependencies(workspace_path)
