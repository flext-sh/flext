#!/usr/bin/env python3
"""Testing Orchestration Module

Comprehensive test runner for all workspace projects.
Based on run_all_e2e_tests.py and other testing scripts functionality.
"""

import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .base import CustomFixModule, Issue


class TestingOrchestrationModule(CustomFixModule):
    """Module for orchestrating comprehensive testing across workspace."""

    name = "testing_orchestration"
    description = "Runs comprehensive testing across all workspace projects"

    # Test types and their priority order
    TEST_TYPES = {
        "unit": {"priority": 1, "pattern": "test_*.py", "timeout": 300},
        "integration": {
            "priority": 2,
            "pattern": "test_*integration*.py",
            "timeout": 600,
        },
        "e2e": {"priority": 3, "pattern": "test_*e2e*.py", "timeout": 1200},
        "acceptance": {
            "priority": 4,
            "pattern": "test_*acceptance*.py",
            "timeout": 1800,
        },
    }

    # Common test commands by project type
    TEST_COMMANDS = {
        "poetry": ["poetry", "run", "pytest"],
        "pip": [sys.executable, "-m", "pytest"],
        "tox": ["tox"],
        "make": ["make", "test"],
        "python": [sys.executable, "-m", "pytest"],
    }

    def __init__(
        self,
        test_types: list[str] | None = None,
        parallel_jobs: int = 4,
        coverage_threshold: float = 85.0,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.test_types = test_types or ["unit", "integration", "e2e"]
        self.parallel_jobs = parallel_jobs
        self.coverage_threshold = coverage_threshold
        self.test_results: dict[str, dict[str, any]] = {}

    def find_test_projects(self, workspace_path: Path) -> list[Path]:
        """Find all projects with test configurations."""
        projects: list = []

        for pyproject_file in workspace_path.rglob("pyproject.toml"):
            # Skip cache and venv directories
            if any(
                part.startswith(".")
                and part in {".venv", ".mypy_cache", ".pytest_cache"}
                for part in pyproject_file.parts
            ):
                continue

            project_path = pyproject_file.parent

            # Check if project has tests
            if self._has_tests(project_path):
                projects.append(project_path)

        return projects

    def _has_tests(self, project_path: Path) -> bool:
        """Check if project has test files."""
        test_patterns = ["tests/", "test/", "**/test_*.py", "**/tests.py", "test*.py"]

        for pattern in test_patterns:
            if list(project_path.glob(pattern)):
                return True

        return False

    def detect_test_runner(self, project_path: Path) -> str:
        """Detect the appropriate test runner for a project."""
        # Check for poetry
        if (project_path / "pyproject.toml").exists():
            return "poetry"

        # Check for tox
        if (project_path / "tox.ini").exists():
            return "tox"

        # Check for Makefile with test target
        makefile = project_path / "Makefile"
        if makefile.exists():
            content = makefile.read_text()
            if "test:" in content:
                return "make"

        # Check for requirements files
        if any(
            (project_path / req_file).exists()
            for req_file in ["requirements.txt", "requirements-dev.txt"]
        ):
            return "pip"

        # Default to python
        return "python"

    def run_project_tests(
        self,
        project_path: Path,
        test_type: str = "unit",
    ) -> dict[str, any]:
        """Run tests for a specific project."""
        project_name = project_path.name
        test_config = self.TEST_TYPES[test_type]

        result = {
            "project": project_name,
            "test_type": test_type,
            "success": False,
            "duration": 0.0,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "coverage": 0.0,
            "errors": [],
            "warnings": [],
        }

        start_time = time.time()

        try:
            # Detect test runner
            runner = self.detect_test_runner(project_path)

            # Prepare test command
            cmd = self._build_test_command(runner, project_path, test_type)

            if self.verbose:
                self.console.print(
                    f"[cyan]Running {test_type} tests in {project_name}: {
                        ' '.join(cmd)
                    }[/cyan]",
                )

            # Install dependencies first if using poetry
            if runner == "poetry":
                self._install_dependencies(project_path)

            # Run tests
            process_result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=test_config["timeout"],
                check=False,
            )

            result["duration"] = time.time() - start_time
            result["success"] = process_result.returncode == 0

            # Parse test output
            self._parse_test_output(
                process_result.stdout,
                process_result.stderr,
                result,
            )

            if not result["success"] and self.verbose:
                self.console.print(f"[red]Tests failed in {project_name}[/red]")
                if process_result.stderr:
                    result["errors"].append(process_result.stderr[:500])

        except subprocess.TimeoutExpired:
            result["duration"] = time.time() - start_time
            result["errors"].append(
                f"Tests timed out after {test_config['timeout']} seconds",
            )
            if self.verbose:
                self.console.print(f"[red]Tests timed out in {project_name}[/red]")

        except Exception as e:
            result["duration"] = time.time() - start_time
            result["errors"].append(str(e))
            if self.verbose:
                self.console.print(
                    f"[red]Error running tests in {project_name}: {e}[/red]",
                )

        return result

    def _build_test_command(
        self,
        runner: str,
        project_path: Path,
        test_type: str,
    ) -> list[str]:
        """Build test command based on runner and test type."""
        base_cmd = self.TEST_COMMANDS[runner].copy()

        if runner == "poetry":
            # Add pytest args for poetry
            base_cmd.extend(
                [
                    "--verbose",
                    "--tb=short",
                    "--cov=src",
                    "--cov-report=term-missing",
                    "--cov-report=xml",
                    f"--cov-fail-under={self.coverage_threshold}",
                ],
            )

            # Add test type specific patterns
            if test_type == "unit":
                base_cmd.extend(["-k", "not integration and not e2e"])
            elif test_type == "integration":
                base_cmd.extend(["-k", "integration"])
            elif test_type == "e2e":
                base_cmd.extend(["-k", "e2e"])

        elif runner == "python":
            base_cmd.extend(
                [
                    "--verbose",
                    "--tb=short",
                    "-x",  # Stop on first failure for faster feedback
                ],
            )

        return base_cmd

    def _install_dependencies(self, project_path: Path) -> bool:
        """Install project dependencies."""
        try:
            result = subprocess.run(
                ["poetry", "install", "--no-interaction"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _parse_test_output(
        self,
        stdout: str,
        stderr: str,
        result: dict[str, any],
    ) -> None:
        """Parse pytest output to extract test metrics."""
        output = stdout + stderr

        # Parse pytest summary line
        import re

        # Look for patterns like "5 passed, 2 failed in 10.23s"
        summary_pattern = r"(?:=+\s+)?(\d+)\s+(?:passed|failed|error|skipped)"
        matches = re.findall(summary_pattern, output, re.IGNORECASE)

        if matches:
            # Sum all test numbers (passed + failed + skipped)
            result["tests_run"] = sum(int(match) for match in matches)

        # Look for specific passed/failed counts
        passed_match = re.search(r"(\d+)\s+passed", output, re.IGNORECASE)
        if passed_match:
            result["tests_passed"] = int(passed_match.group(1))

        failed_match = re.search(r"(\d+)\s+failed", output, re.IGNORECASE)
        if failed_match:
            result["tests_failed"] = int(failed_match.group(1))

        # Parse coverage percentage
        coverage_pattern = r"TOTAL\s+\d+\s+\d+\s+(\d+)%"
        coverage_match = re.search(coverage_pattern, output)
        if coverage_match:
            result["coverage"] = float(coverage_match.group(1))

        # Extract warnings
        warning_pattern = r"(WARNING|WARN|warning).*"
        warnings = re.findall(warning_pattern, output, re.MULTILINE)
        result["warnings"].extend(warnings[:5])  # Limit to first 5 warnings

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze test files for common issues."""
        issues: list = []

        if file_path.name.startswith("test_") or "test" in str(file_path):
            lines = content.split("\n")

            # Check for common test issues
            has_imports = False
            has_tests = False

            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check for imports
                if line_stripped.startswith(("import ", "from ")):
                    has_imports = True

                # Check for test functions
                if line_stripped.startswith(("def test_", "async def test_")):
                    has_tests = True

                # Check for common anti-patterns
                if "print(" in line and "test_" in file_path.name:
                    issues.append(
                        Issue(
                            line=i,
                            column=1,
                            code="TEST001",
                            message="Test files should not contain print statements",
                            suggestion="Use logging or assertions instead",
                        ),
                    )

                if "sleep(" in line and "test_" in file_path.name:
                    issues.append(
                        Issue(
                            line=i,
                            column=1,
                            code="TEST002",
                            message="Avoid sleep() in tests - use proper async patterns or mocking",
                            suggestion="Use pytest fixtures or async testing patterns",
                        ),
                    )

            if not has_tests and file_path.name.startswith("test_"):
                issues.append(
                    Issue(
                        line=1,
                        column=1,
                        code="TEST003",
                        message="Test file contains no test functions",
                        suggestion="Add test functions starting with 'test_'",
                    ),
                )

            if not has_imports and has_tests:
                issues.append(
                    Issue(
                        line=1,
                        column=1,
                        code="TEST004",
                        message="Test file has no imports but contains tests",
                        suggestion="Import required testing modules (pytest, unittest, etc.)",
                    ),
                )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply basic test fixes."""
        lines = content.split("\n")

        for issue in issues:
            if issue.code == "TEST001":  # Remove print statements
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    if "print(" in line:
                        # Comment out print statements
                        lines[line_idx] = (
                            "# " + line + "  # TODO: Replace with proper logging"
                        )

        return "\n".join(lines)

    def run_comprehensive_tests(self, workspace_path: Path = None) -> dict[str, any]:
        """Run comprehensive testing across all projects."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Running comprehensive tests in: {workspace_path}[/blue]",
            )

        # Find all test projects
        projects = self.find_test_projects(workspace_path)

        if not projects:
            if self.verbose:
                self.console.print("[yellow]No test projects found[/yellow]")
            return {"projects": 0, "total_success": True}

        if self.verbose:
            self.console.print(
                f"[green]Found {len(projects)} projects with tests[/green]",
            )

        # Run tests for each project and test type
        all_results: list = []
        total_success = True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            for project_path in projects:
                project_name = project_path.name

                for test_type in self.test_types:
                    task = progress.add_task(
                        f"Running {test_type} tests in {project_name}...",
                        total=None,
                    )

                    if self.dry_run:
                        result = {
                            "project": project_name,
                            "test_type": test_type,
                            "success": True,
                            "duration": 0.0,
                            "dry_run": True,
                        }
                        progress.update(
                            task,
                            description=f"[DRY RUN] Would run {test_type} tests in {project_name}",
                        )
                        result = self.run_project_tests(project_path, test_type)

                        if result["success"]:
                            progress.update(
                                task,
                                description=f"✅ {test_type} tests in {project_name} - {result['tests_passed']} passed",
                            )
                            progress.update(
                                task,
                                description=f"❌ {test_type} tests in {project_name} - {len(result['errors'])} errors",
                            )
                            total_success = False

                    all_results.append(result)

                    # Store in instance for reporting
                    if project_name not in self.test_results:
                        self.test_results[project_name] = {}
                    self.test_results[project_name][test_type] = result

        # Generate summary
        if self.verbose:
            self._show_test_summary(all_results)

        return {
            "projects": len(projects),
            "test_types": len(self.test_types),
            "total_tests": len(all_results),
            "total_success": total_success,
            "results": all_results,
        }

    def _show_test_summary(self, results: list[dict[str, any]]) -> None:
        """Show comprehensive test summary."""
        # Overall summary table
        table = Table(title="Test Execution Summary")
        table.add_column("Project", style="cyan")
        table.add_column("Test Type", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Tests", justify="right")
        table.add_column("Coverage", justify="right")
        table.add_column("Duration", justify="right")

        total_tests = 0
        total_passed = 0
        total_duration = 0.0

        for result in results:
            if result.get("dry_run"):
                status = "🔍 DRY RUN"
                tests_info = "N/A"
                coverage_info = "N/A"
                duration_info = "N/A"
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                tests_info = f"{result['tests_passed']}/{result['tests_run']}"
                coverage_info = (
                    f"{result['coverage']:.1f}%" if result["coverage"] > 0 else "N/A"
                )
                duration_info = f"{result['duration']:.1f}s"

                total_tests += result["tests_run"]
                total_passed += result["tests_passed"]
                total_duration += result["duration"]

            table.add_row(
                result["project"],
                result["test_type"],
                status,
                tests_info,
                coverage_info,
                duration_info,
            )

        self.console.print(table)

        # Summary panel
        if not any(r.get("dry_run") for r in results):
            success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            summary_text = (
                f"Total Tests: {total_tests}\n"
                f"Passed: {total_passed}\n"
                f"Failed: {total_tests - total_passed}\n"
                f"Success Rate: {success_rate:.1f}%\n"
                f"Total Duration: {total_duration:.1f}s"
            )

            panel_style = (
                "green"
                if success_rate >= 95
                else "yellow"
                if success_rate >= 80
                else "red"
            )
            self.console.print(
                Panel(summary_text, title="Overall Results", border_style=panel_style),
            )

    def run_workspace_testing(self, workspace_path: Path = None) -> bool:
        """Run comprehensive testing across the entire workspace."""
        result = self.run_comprehensive_tests(workspace_path)
        return result["total_success"]
