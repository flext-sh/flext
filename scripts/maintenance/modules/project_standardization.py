#!/usr/bin/env python3
"""Project Standardization Module

Standardizes pyproject.toml configurations across all workspace projects.
Based on scripts/utilities/standardize_projects.py functionality.
"""

import shutil
from pathlib import Path
from typing import Any

import tomli
import tomli_w
from rich.console import Console

from .base import CustomFixModule, Issue


class ProjectStandardizationModule(CustomFixModule):
    """Module for standardizing project configurations."""

    name = "project_standardization"
    description = "Standardizes pyproject.toml configurations across workspace projects"

    # Standard configuration template
    STANDARD_CONFIG = {
        "build-system": {
            "requires": ["poetry-core>=2.1.3"],
            "build-backend": "poetry.core.masonry.api",
        },
        "tool": {
            "poetry": {
                "dependencies": {
                    "python": "^3.13",
                },
            },
            "black": {
                "line-length": 88,
                "target-version": ["py313"],
                "include": r"\.pyi?$",
            },
            "isort": {
                "profile": "black",
                "line_length": 88,
                "multi_line_output": 3,
                "include_trailing_comma": True,
                "force_grid_wrap": 0,
                "use_parentheses": True,
                "ensure_newline_before_comments": True,
            },
            "ruff": {
                "target-version": "py313",
                "line-length": 88,
                "src": ["src", "tests"],
            },
            "ruff.lint": {
                "select": [
                    "E", "W", "F", "I", "UP", "N", "B", "C4", "DTZ", "T10",
                    "ISC", "G", "PIE", "PT", "RET", "SIM", "ARG", "ERA",
                    "PGH", "PL", "TRY", "BLE", "COM",
                ],
                "ignore": [
                    "E501", "UP007", "BLE001", "G004", "DTZ007", "TRY003",
                    "PLR2004", "PLR0911", "PLR0912", "TRY401",
                ],
            },
            "ruff.lint.per-file-ignores": {
                "__init__.py": ["F401"],
                "tests/**/*.py": ["S101", "PLR2004", "TID252", "ARG", "FBT"],
                "scripts/**/*.py": ["T20", "S101", "PLR2004"],
            },
            "mypy": {
                "python_version": "3.13",
                "strict": True,
                "warn_return_any": True,
                "warn_unused_configs": True,
                "warn_redundant_casts": True,
                "warn_unused_ignores": True,
                "show_error_codes": True,
                "pretty": True,
            },
            "pytest.ini_options": {
                "minversion": "8.0",
                "addopts": [
                    "--strict-markers",
                    "--strict-config",
                    "--cov-report=term-missing",
                    "--cov-report=html:reports/coverage",
                    "--cov-report=xml",
                    "--junitxml=reports/junit.xml",
                ],
                "testpaths": ["tests"],
                "python_files": ["test_*.py", "*_test.py"],
                "python_functions": ["test_*"],
                "python_classes": ["Test*"],
                "markers": [
                    "slow: marks tests as slow",
                    "integration: marks tests as integration tests",
                    "unit: marks tests as unit tests",
                ],
            },
            "coverage.run": {
                "source": ["src"],
                "branch": True,
                "omit": [
                    "*/tests/*",
                    "*/test_*",
                    "*/__main__.py",
                    "*/conftest.py",
                ],
            },
            "coverage.report": {
                "exclude_lines": [
                    "pragma: no cover",
                    "def __repr__",
                    "raise AssertionError",
                    "raise NotImplementedError",
                    "if __name__ == .__main__.:",
                    "if TYPE_CHECKING:",
                    "@abstractmethod",
                ],
            },
        },
    }

    STANDARD_DEV_DEPENDENCIES = {
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
        self.backup_dir = Path.cwd() / ".standardization_backup"

    def find_projects(self, workspace_path: Path) -> list[Path]:
        """Find all projects with pyproject.toml."""
        projects: list = []
        seen_projects: set = set()

        for path in workspace_path.rglob("pyproject.toml"):
            # Ignore venv and cache directories
            if any(
                part.startswith(".")
                and part in {".venv", ".mypy_cache", ".pytest_cache"}
                for part in path.parts
            ):
                continue

            # Avoid duplicates based on project name
            project_path = path.parent
            if project_path.name not in seen_projects:
                projects.append(project_path)
                seen_projects.add(project_path.name)

        return projects

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze workspace for standardization opportunities."""
        issues: list = []

        if file_path.name == "pyproject.toml":
            try:
                with open(file_path, "rb") as f:
                    config = tomli.load(f)

                # Check if configuration needs standardization
                needs_update = False

                # Check build-system
                build_system = config.get("build-system", {})
                if build_system != self.STANDARD_CONFIG["build-system"]:
                    needs_update = True

                # Check tool configurations
                tool_config = config.get("tool", {})
                for tool, standard_config in self.STANDARD_CONFIG["tool"].items(
                ):
                    if tool == "poetry":
                        continue  # Handle poetry separately

                    if tool_config.get(tool) != standard_config:
                        needs_update = True
                        break

                # Check development dependencies
                poetry_config = tool_config.get("poetry", {})
                group_config = poetry_config.get("group", {})
                dev_config = group_config.get("dev", {})
                dev_deps = dev_config.get("dependencies", {})

                for dep, _version in self.STANDARD_DEV_DEPENDENCIES.items():
                    if dep not in dev_deps:
                        needs_update = True
                        break

                if needs_update:
                    issues.append(
                        Issue(
                            line=1,
                            column=1,
                            code="PROJ001",
                            message="Project configuration needs standardization",
                            suggestion="Apply standard PyAuto configuration template"))

            except Exception as e:
                issues.append(Issue(
                    line=1,
                    column=1,
                    code="PROJ002",
                    message=f"Failed to analyze pyproject.toml: {e}",
                    suggestion="Check file format and syntax"
                ))

        return issues

    def create_backup(self, project_path: Path) -> None:
        """Create backup of original pyproject.toml."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / project_path.name
        backup_path.mkdir(parents=True, exist_ok=True)

        source = project_path / "pyproject.toml"
        target = backup_path / "pyproject.toml"
        shutil.copy2(source, target)

    def merge_configs(
            self, current: dict[str, Any], project_path: Path) -> dict[str, Any]:
        """Merge current configuration with standards."""
        result = current.copy()

        # Update build-system
        result["build-system"] = self.STANDARD_CONFIG["build-system"]

        # Initialize tool section
        if "tool" not in result:
            result["tool"] = {}
        if "poetry" not in result["tool"]:
            result["tool"]["poetry"] = {}

        # Preserve project-specific Poetry metadata
        poetry_config = result["tool"]["poetry"]

        # Update python version in dependencies
        if "dependencies" in poetry_config:
            poetry_config["dependencies"]["python"] = "^3.13"

        # Add standard development dependencies
        if "group" not in poetry_config:
            poetry_config["group"] = {}
        if "dev" not in poetry_config["group"]:
            poetry_config["group"]["dev"] = {}
        if "dependencies" not in poetry_config["group"]["dev"]:
            poetry_config["group"]["dev"]["dependencies"] = {}

        # Merge dev dependencies
        dev_deps = poetry_config["group"]["dev"]["dependencies"]
        for dep, version in self.STANDARD_DEV_DEPENDENCIES.items():
            if dep not in dev_deps:
                dev_deps[dep] = version

        # Apply standard tool configurations
        for tool, config in self.STANDARD_CONFIG["tool"].items():
            if tool != "poetry":  # Poetry handled above
                result["tool"][tool] = config

        # Project-specific adjustments
        if "flx" in str(project_path):
            # FLX projects need stricter configurations
            result["tool"]["ruff"]["line-length"] = 120
            result["tool"]["mypy"]["strict"] = True

        return result

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply standardization fixes to pyproject.toml files."""
        # This method is called for individual files
        # For project standardization, we handle this at the workspace level
        return content

    def standardize_workspace(self, workspace_path: Path) -> bool:
        """Standardize all projects in the workspace."""
        if self.verbose:
            self.console.print(
                f"[blue]Standardizing workspace: {workspace_path}[/blue]")

        projects = self.find_projects(workspace_path)

        if self.verbose:
            self.console.print(
                f"[green]Found {
                    len(projects)} projects[/green]")

        success_count = 0

        for project_path in projects:
            try:
                if self.verbose:
                    self.console.print(
                        f"[yellow]Processing {
                            project_path.name}[/yellow]")

                # Create backup
                if not self.dry_run:
                    self.create_backup(project_path)

                # Load current configuration
                config_path = project_path / "pyproject.toml"
                with open(config_path, "rb") as f:
                    current_config = tomli.load(f)

                # Merge with standards
                standardized_config = self.merge_configs(
                    current_config, project_path)

                if self.dry_run:
                    if self.verbose:
                        self.console.print(
                            f"[cyan][DRY RUN] Would standardize {
                                project_path.name}[/cyan]")
                    # Save standardized configuration
                    with open(config_path, "wb") as f:
                        tomli_w.dump(standardized_config, f)

                    if self.verbose:
                        self.console.print(
                            f"[green]✅ Standardized {
                                project_path.name}[/green]")

                success_count += 1

            except Exception as e:
                if self.verbose:
                    self.console.print(
                        f"[red]❌ Failed to standardize {
                            project_path.name}: {e}[/red]")

        if self.verbose:
            action = "Would standardize" if self.dry_run else "Standardized"
            self.console.print(
                f"[bold green]{action} {success_count}/{len(projects)} projects[/bold green]")

        return success_count == len(projects)

    def run_workspace_standardization(
            self, workspace_path: Path = None) -> bool:
        """Run standardization across the entire workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        return self.standardize_workspace(workspace_path)
