#!/usr/bin/env python3
"""Project Validation Module

Validates project compliance with enterprise standards.
Based on scripts/validate_pyproject_compliance.py functionality.
"""

import tomllib
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from .base import CustomFixModule, Issue


class ProjectValidationModule(CustomFixModule):
    """Module for validating project compliance with enterprise standards."""

    name = "project_validation"
    description = "Validates project compliance with enterprise standards"

    # Enterprise standards - ZERO TOLERANCE
    REQUIRED_PYTHON_VERSION = "^3.13"
    REQUIRED_BUILD_SYSTEM = {
        "requires": ["poetry-core>=2.1.3"],
        "build-backend": "poetry.core.masonry.api"
    }
    MINIMUM_COVERAGE = 90
    REQUIRED_LINE_LENGTH = 88

    # Required development dependencies (minimum versions)
    REQUIRED_DEV_DEPS = {
        "pytest": "^8.4.0",
        "pytest-cov": "^6.1.1",
        "black": "^25.1.0",
        "ruff": "^0.11.13",
        "mypy": "^1.16.0",
        "isort": "^6.0.1",
    }

    # Required core dependencies for enterprise projects
    REQUIRED_CORE_DEPS = {
        "pydantic": "^2.11.5",
        "structlog": "^24.4.0",
        "python-dotenv": "^1.0.1",
        "typing-extensions": "^4.12.2",
    }

    # Critical tool configurations
    REQUIRED_BLACK_CONFIG = {
        "line-length": 88,
        "target-version": ["py313"],
    }

    REQUIRED_RUFF_CONFIG = {
        "target-version": "py313",
        "line-length": 88,
        "src": ["src", "tests"],
    }

    REQUIRED_MYPY_CONFIG = {
        "python_version": "3.13",
        "strict": True,
        "warn_return_any": True,
        "warn_unused_configs": True,
        "warn_redundant_casts": True,
        "warn_unused_ignores": True,
        "show_error_codes": True,
        "pretty": True,
    }

    REQUIRED_PYTEST_CONFIG = {
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
    }

    REQUIRED_COVERAGE_CONFIG = {
        "run": {
            "source": ["src"],
            "branch": True,
            "omit": [
                "*/tests/*",
                "*/test_*",
                "*/__main__.py",
                "*/conftest.py",
            ],
        },
        "report": {
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
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.validation_results: dict[str, dict[str, Any]] = {}

    def find_projects(self, workspace_path: Path) -> list[Path]:
        """Find all projects with pyproject.toml."""
        projects: list = []

        for pyproject_file in workspace_path.rglob("pyproject.toml"):
            # Skip cache and venv directories
            if any(
                part.startswith(".")
                and part in {".venv", ".mypy_cache", ".pytest_cache"}
                for part in pyproject_file.parts
            ):
                continue
            projects.append(pyproject_file.parent)

        return projects

    def validate_project_structure(self, project_path: Path) -> list[str]:
        """Validate basic project structure."""
        issues: list = []

        # Required files
        required_files = [
            "pyproject.toml",
            "README.md",
            ".gitignore"
        ]

        for file_name in required_files:
            if not (project_path / file_name).exists():
                issues.append(f"Missing required file: {file_name}")

        # Required directories
        required_dirs = ["src", "tests"]
        for dir_name in required_dirs:
            if not (project_path / dir_name).exists():
                issues.append(f"Missing required directory: {dir_name}")

        # Check for __init__.py in src
        src_dir = project_path / "src"
        if src_dir.exists():
            if not any(src_dir.rglob("__init__.py")):
                issues.append("No __init__.py files found in src/ directory")

        return issues

    def validate_pyproject_toml(self, project_path: Path) -> list[str]:
        """Validate pyproject.toml compliance."""
        issues: list = []
        pyproject_file = project_path / "pyproject.toml"

        if not pyproject_file.exists():
            return ["pyproject.toml file not found"]

        try:
            with open(pyproject_file, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            return [f"Failed to parse pyproject.toml: {e}"]

        # Validate build system
        build_system = config.get("build-system", {})
        if build_system != self.REQUIRED_BUILD_SYSTEM:
            issues.append(
                "Build system configuration does not match enterprise standard")

        # Validate poetry configuration
        poetry_config = config.get("tool", {}).get("poetry", {})
        if not poetry_config:
            issues.append("Poetry configuration missing")
            return issues

        # Check Python version
        dependencies = poetry_config.get("dependencies", {})
        python_version = dependencies.get("python")
        if not python_version or not python_version.startswith("^3.13"):
            issues.append(
                f"Python version {python_version} does not meet requirement: {
                    self.REQUIRED_PYTHON_VERSION}")

        # Check required core dependencies
        for dep, required_version in self.REQUIRED_CORE_DEPS.items():
            if dep not in dependencies:
                issues.append(f"Missing required core dependency: {dep}")
                current_version = dependencies[dep]
                if not self._version_compatible(
                        current_version, required_version):
                    issues.append(
                        f"Dependency {dep} version {current_version} does not meet requirement: {required_version}")

        # Check development dependencies
        groups = poetry_config.get("group", {})
        dev_deps = groups.get(
            "dev",
            {}).get(
            "dependencies",
            {}) if groups else {}

        for dep, required_version in self.REQUIRED_DEV_DEPS.items():
            if dep not in dev_deps:
                issues.append(f"Missing required dev dependency: {dep}")
                current_version = dev_deps[dep]
                if not self._version_compatible(
                        current_version, required_version):
                    issues.append(
                        f"Dev dependency {dep} version {current_version} does not meet requirement: {required_version}")

        # Validate tool configurations
        tool_config = config.get("tool", {})

        # Black configuration
        black_config = tool_config.get("black", {})
        for key, value in self.REQUIRED_BLACK_CONFIG.items():
            if black_config.get(key) != value:
                issues.append(
                    f"Black configuration {key} does not match enterprise standard")

        # Ruff configuration
        ruff_config = tool_config.get("ruff", {})
        for key, value in self.REQUIRED_RUFF_CONFIG.items():
            if ruff_config.get(key) != value:
                issues.append(
                    f"Ruff configuration {key} does not match enterprise standard")

        # MyPy configuration
        mypy_config = tool_config.get("mypy", {})
        for key, value in self.REQUIRED_MYPY_CONFIG.items():
            if mypy_config.get(key) != value:
                issues.append(
                    f"MyPy configuration {key} does not match enterprise standard")

        # Pytest configuration
        pytest_config = tool_config.get("pytest", {}).get("ini_options", {})
        for key, value in self.REQUIRED_PYTEST_CONFIG.items():
            if pytest_config.get(key) != value:
                issues.append(
                    f"Pytest configuration {key} does not match enterprise standard")

        # Coverage configuration
        coverage_config = tool_config.get("coverage", {})
        for section, expected_config in self.REQUIRED_COVERAGE_CONFIG.items():
            current_section = coverage_config.get(section, {})
            for key, value in expected_config.items():
                if current_section.get(key) != value:
                    issues.append(
                        f"Coverage {section}.{key} does not match enterprise standard")

        return issues

    def _version_compatible(self, current: str, required: str) -> bool:
        """Check if current version is compatible with required version."""
        # Simplified version compatibility check
        # In a real implementation, you'd use packaging.version

        # Handle exact matches
        if current == required:
            return True

        # Handle caret versions (^1.0.0 allows >=1.0.0, <2.0.0)
        if required.startswith("^") and current.startswith("^"):
            req_version = required[1:]
            cur_version = current[1:]
            return cur_version >= req_version

        return False

    def validate_code_quality(self, project_path: Path) -> list[str]:
        """Validate code quality standards."""
        issues: list = []

        # Check for common anti-patterns in source code
        src_dir = project_path / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")

                    # Check for print statements in production code
                    if "print(" in content and not str(
                            py_file).endswith("__main__.py"):
                        issues.append(
                            f"Print statements found in production code: {
                                py_file.relative_to(project_path)}")

                    # Check for TODO/FIXME comments
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        if "TODO" in line.upper() or "FIXME" in line.upper():
                            issues.append(
                                f"TODO/FIXME comment found: {py_file.relative_to(project_path)}:{i}")

                    # Check for long lines (basic check)
                    for i, line in enumerate(lines, 1):
                        if len(line) > 120:  # More lenient than Black's 88 for now
                            issues.append(
                                f"Line too long ({
                                    len(line)} chars): {
                                    py_file.relative_to(project_path)}:{i}")

                except Exception:
                    continue

        return issues

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze individual project files for compliance issues."""
        issues: list = []

        if file_path.name == "pyproject.toml":
            project_path = file_path.parent

            # Validate project structure
            structure_issues = self.validate_project_structure(project_path)
            for issue_msg in structure_issues:
                issues.append(
                    Issue(
                        line=1,
                        column=1,
                        code="PROJ_STRUCT001",
                        message=issue_msg,
                        suggestion="Ensure project follows enterprise structure standards"))

            # Validate pyproject.toml
            pyproject_issues = self.validate_pyproject_toml(project_path)
            for issue_msg in pyproject_issues:
                issues.append(
                    Issue(
                        line=1,
                        column=1,
                        code="PROJ_CONFIG001",
                        message=issue_msg,
                        suggestion="Update configuration to match enterprise standards"))

            # Validate code quality
            quality_issues = self.validate_code_quality(project_path)
            for issue_msg in quality_issues:
                issues.append(
                    Issue(
                        line=1,
                        column=1,
                        code="PROJ_QUALITY001",
                        message=issue_msg,
                        suggestion="Fix code quality issues to meet enterprise standards"))

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply basic validation fixes (most fixes require manual intervention)."""
        # Most validation issues require manual configuration changes
        # This module focuses on detection rather than automatic fixing
        return content

    def validate_workspace(
            self, workspace_path: Path = None) -> dict[str, Any]:
        """Validate all projects in the workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Validating workspace: {workspace_path}[/blue]")

        projects = self.find_projects(workspace_path)

        if self.verbose:
            self.console.print(
                f"[green]Found {
                    len(projects)} projects to validate[/green]")

        validation_results = {
            "total_projects": len(projects),
            "compliant_projects": 0,
            "non_compliant_projects": 0,
            "total_issues": 0,
            "project_results": {}
        }

        for project_path in projects:
            project_name = project_path.name

            if self.verbose:
                self.console.print(
                    f"[yellow]Validating {project_name}[/yellow]")

            project_issues = {
                "structure": self.validate_project_structure(project_path),
                "pyproject": self.validate_pyproject_toml(project_path),
                "code_quality": self.validate_code_quality(project_path)
            }

            total_project_issues = sum(len(issues)
                                       for issues in project_issues.values())

            if total_project_issues == 0:
                validation_results["compliant_projects"] += 1
                if self.verbose:
                    self.console.print(
                        f"[green]✅ {project_name} is compliant[/green]")
                validation_results["non_compliant_projects"] += 1
                validation_results["total_issues"] += total_project_issues
                if self.verbose:
                    self.console.print(
                        f"[red]❌ {project_name} has {total_project_issues} issues[/red]")

            validation_results["project_results"][project_name] = {
                "compliant": total_project_issues == 0,
                "issues": project_issues,
                "total_issues": total_project_issues
            }

            self.validation_results[project_name] = validation_results["project_results"][project_name]

        # Show summary
        if self.verbose:
            self._show_validation_summary(validation_results)

        return validation_results

    def _show_validation_summary(self, results: dict[str, Any]) -> None:
        """Show validation summary table."""
        table = Table(title="Project Validation Summary")
        table.add_column("Project", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Structure Issues", justify="right")
        table.add_column("Config Issues", justify="right")
        table.add_column("Quality Issues", justify="right")
        table.add_column("Total Issues", justify="right")

        for project_name, project_result in results["project_results"].items():
            status = "✅ COMPLIANT" if project_result["compliant"] else "❌ NON-COMPLIANT"

            structure_count = len(project_result["issues"]["structure"])
            pyproject_count = len(project_result["issues"]["pyproject"])
            quality_count = len(project_result["issues"]["code_quality"])
            total_count = project_result["total_issues"]

            table.add_row(
                project_name,
                status,
                str(structure_count),
                str(pyproject_count),
                str(quality_count),
                str(total_count)
            )

        self.console.print(table)

        # Overall summary
        compliance_rate = (
            results["compliant_projects"] /
            results["total_projects"] *
            100) if results["total_projects"] > 0 else 0

        summary_text = (
            f"Total Projects: {results['total_projects']}\n"
            f"Compliant: {results['compliant_projects']}\n"
            f"Non-Compliant: {results['non_compliant_projects']}\n"
            f"Compliance Rate: {compliance_rate:.1f}%\n"
            f"Total Issues: {results['total_issues']}"
        )

        panel_style = "green" if compliance_rate == 100 else "yellow" if compliance_rate >= 80 else "red"

        from rich.panel import Panel
        self.console.print(
            Panel(
                summary_text,
                title="Validation Results",
                border_style=panel_style))

    def run_workspace_validation(self, workspace_path: Path = None) -> bool:
        """Run validation across the entire workspace."""
        results = self.validate_workspace(workspace_path)
        return results["non_compliant_projects"] == 0
