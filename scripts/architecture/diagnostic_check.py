#!/usr/bin/env python3
"""FLEXT Architecture Diagnostic Tool.

Comprehensive diagnostic tool for FLEXT workspace architecture validation.
"""

import contextlib
import io
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import pytest
from flext_core import FlextLogger

# Ruff will be called via subprocess
from mypy import api as mypy_api

logger = FlextLogger(__name__)

# Constants for return codes
SUCCESS_CODE = 0
MAKEFILE_TARGET_NOT_FOUND = 2
COMMAND_FAILED = 1

# Status constants (not passwords, just status indicators)
STATUS_PASS = "✅ PASS"  # nosec B105
STATUS_FAIL = "❌ FAIL"  # nosec B105
STATUS_NO_TARGET = "⚠️  NO_TARGET"  # nosec B105
STATUS_SKIP = "SKIP"  # nosec B105


@dataclass
class ProjectStatus:
    """Project status."""

    name: str
    level: int
    has_makefile: bool
    has_pyproject: bool
    lint_status: str = STATUS_SKIP
    mypy_status: str = STATUS_SKIP
    test_status: str = STATUS_SKIP
    poetry_install: str = STATUS_SKIP
    errors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize post-creation setup for ProjectStatus."""


class FlextDiagnostic:
    """Flext diagnostic tool."""

    def __init__(self, workspace_root: str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.results: dict[str, ProjectStatus] = {}

        # Define layer hierarchy
        self.project_levels = {
            # LEVEL 1 - BASE
            "flext-core": 1,
            # LEVEL 2 - INTERMEDIATE
            "flext-cli": 2,
            "flext-observability": 2,
            "flext-grpc": 2,
            "flext-web": 2,
            "flext-api": 2,
            "flext-auth": 2,
            # LEVEL 3 - TECHNICAL BASES
            "flext-meltano": 3,
            "flext-ldif": 3,
            "flext-ldap": 3,
            "flext-db-oracle": 3,
            "flext-oracle-wms": 3,
            "flext-oracle-oic-ext": 3,
            # LEVEL 4 - MELTANO PLUGINS
            "flext-tap-oracle": 4,
            "flext-tap-ldap": 4,
            "flext-tap-ldif": 4,
            "flext-tap-oracle-wms": 4,
            "flext-tap-oracle-oic": 4,
            "flext-target-oracle": 4,
            "flext-target-ldap": 4,
            "flext-target-ldif": 4,
            "flext-target-oracle-wms": 4,
            "flext-target-oracle-oic": 4,
            "flext-dbt-oracle": 4,
            "flext-dbt-ldap": 4,
            "flext-dbt-ldif": 4,
            "flext-dbt-oracle-wms": 4,
            "flext-plugin": 4,
            # LEVEL 6 - SPECIFIC PROJECTS
            "client-a-oud-mig": 6,
            "client-b-meltano-native": 6,
        }

    def _run_lint(self, project_path: Path) -> tuple[int, str, str]:
        """Run Ruff lint using subprocess."""
        try:
            result = subprocess.run(
                ["ruff", "check", "."],
                check=False,
                capture_output=True,
                text=True,
                cwd=project_path,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", f"Ruff execution failed: {e}"

    def _run_mypy(self, project_path: Path) -> tuple[int, str, str]:
        """Run MyPy using its Python API in-process."""
        try:
            # Analyze the project directory
            stdout, stderr, exit_status = mypy_api.run([str(project_path)])
            return int(exit_status), stdout, stderr
        except Exception as e:
            return 1, "", f"MyPy execution failed: {e}"

    def _run_tests(self, project_path: Path) -> tuple[int, str, str]:
        """Run pytest in-process and capture output."""
        try:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                # Run tests within project path
                code = pytest.main([str(project_path)])
            return int(code), stdout.getvalue(), stderr.getvalue()
        except Exception as e:
            return 1, "", f"Pytest execution failed: {e}"

    def _run_poetry_install(self) -> tuple[int, str, str]:
        """Attempt Poetry install using subprocess."""
        try:
            result = subprocess.run(
                ["poetry", "install", "--no-interaction"],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", f"Poetry install failed: {e}"

    def check_project(self, project_name: str) -> ProjectStatus:
        """Check status of a project."""
        project_path = self.workspace_root / project_name

        if not project_path.exists():
            return ProjectStatus(
                name=project_name,
                level=self.project_levels.get(project_name, 0),
                has_makefile=False,
                has_pyproject=False,
                errors=["Project not found"],
            )

        status = ProjectStatus(
            name=project_name,
            level=self.project_levels.get(project_name, 0),
            has_makefile=(project_path / "Makefile").exists(),
            has_pyproject=(project_path / "pyproject.toml").exists(),
        )

        # Check Makefile
        if status.has_makefile:
            # Check lint
            rc, stdout, stderr = self._run_lint(project_path)
            if rc == SUCCESS_CODE:
                status.lint_status = STATUS_PASS
            else:
                status.lint_status = STATUS_FAIL
                status.errors.append(f"Lint: {stderr.strip()}")

            # Check mypy
            rc, stdout, stderr = self._run_mypy(project_path)
            if rc == SUCCESS_CODE:
                status.mypy_status = STATUS_PASS
            else:
                status.mypy_status = STATUS_FAIL
                status.errors.append(f"MyPy: {stderr.strip()}")

            # Check tests
            rc, stdout, stderr = self._run_tests(project_path)
            if rc == SUCCESS_CODE:
                status.test_status = STATUS_PASS
            else:
                status.test_status = STATUS_FAIL
                status.errors.append(f"Tests: {stderr.strip()}")

        # Check Poetry install
        if status.has_pyproject:
            rc, _stdout, stderr = self._run_poetry_install()
            if rc == 0:
                status.poetry_install = "✅ PASS"
            else:
                status.poetry_install = "❌ FAIL"
                status.errors.append(
                    f"Poetry: {stderr.strip()}"
                    if stderr
                    else "Poetry install failed via API",
                )

        return status

    def check_architecture_violations(self) -> dict[str, list[str]]:
        """Check architecture violations."""
        violations: dict[str, list[str]] = {}

        # Check flext-core (should not have specific imports)
        core_path = self.workspace_root / "flext-core" / "src"
        if core_path.exists():
            violations["flext-core"] = []

            # Search problematic imports by scanning files directly
            keywords = ["meltano", "oracle", "ldap", "singer", "client-a", "client-b"]
            for file_path in core_path.rglob("*.py"):
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for keyword in keywords:
                    if keyword in content:
                        violations["flext-core"].append(
                            f"Import {keyword}: {file_path}",
                        )

        return violations

    def run_full_diagnostic(self) -> dict[str, object]:
        """Run full diagnostic."""
        # Check all projects
        for project_name in self.project_levels:
            status = self.check_project(project_name)
            self.results[project_name] = status

            # Check architecture violations
        violations = self.check_architecture_violations()

        # Generate report
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "workspace_root": str(self.workspace_root),
            "projects": {
                name: {
                    "level": status.level,
                    "has_makefile": status.has_makefile,
                    "has_pyproject": status.has_pyproject,
                    "lint_status": status.lint_status,
                    "mypy_status": status.mypy_status,
                    "test_status": status.test_status,
                    "poetry_install": status.poetry_install,
                    "errors": status.errors,
                }
                for name, status in self.results.items()
            },
            "architecture_violations": violations,
            "summary": self.generate_summary(),
        }

    def generate_summary(self) -> dict[str, object]:
        """Generate summary."""
        total_projects = len(self.results)
        projects_with_makefile = sum(1 for s in self.results.values() if s.has_makefile)
        projects_with_pyproject = sum(
            1 for s in self.results.values() if s.has_pyproject
        )

        lint_passed = sum(
            1 for s in self.results.values() if s.lint_status == "✅ PASS"
        )
        mypy_passed = sum(
            1 for s in self.results.values() if s.mypy_status == "✅ PASS"
        )
        tests_passed = sum(
            1 for s in self.results.values() if s.test_status == "✅ PASS"
        )
        poetry_passed = sum(
            1 for s in self.results.values() if s.poetry_install == "✅ PASS"
        )

        projects_with_errors = sum(1 for s in self.results.values() if s.errors)

        return {
            "total_projects": total_projects,
            "projects_with_makefile": projects_with_makefile,
            "projects_with_pyproject": projects_with_pyproject,
            "lint_passed": lint_passed,
            "mypy_passed": mypy_passed,
            "tests_passed": tests_passed,
            "poetry_passed": poetry_passed,
            "projects_with_errors": projects_with_errors,
        }

    def print_report(self, report: dict[str, object]) -> None:
        """Print formatted report."""
        # Summary
        summary_obj = report["summary"]
        if not isinstance(summary_obj, dict):
            return

        # Project details

        for level in range(1, 7):
            projects_obj = report["projects"]
            if not isinstance(projects_obj, dict):
                continue
            level_projects = [
                (name, data)
                for name, data in projects_obj.items()
                if isinstance(data, dict) and data.get("level") == level
            ]

            if level_projects:
                {
                    1: "NÍVEL 1 - BASE",
                    2: "NÍVEL 2 - INTERMEDIÁRIA",
                    3: "NÍVEL 3 - BASES TECNOLÓGICAS",
                    4: "NÍVEL 4 - PLUGINS MELTANO",
                    5: "NÍVEL 5 - WORKSPACE",
                    6: "NÍVEL 6 - PROJETOS ESPECÍFICOS",
                }.get(level, f"NÍVEL {level}")

                for _name, data in level_projects:
                    if isinstance(data, dict):
                        status_icons = [
                            str(data.get("lint_status", "UNKNOWN")),
                            str(data.get("mypy_status", "UNKNOWN")),
                            str(data.get("test_status", "UNKNOWN")),
                            str(data.get("poetry_install", "UNKNOWN")),
                        ]
                        status_line = " | ".join(status_icons)

                    errors = data.get("errors", [])
                    if isinstance(errors, list) and errors:
                        for _error in errors[:2]:  # Show only first 2 errors
                            pass

        # Architecture violations
        violations_obj = report.get("architecture_violations", {})
        if isinstance(violations_obj, dict) and violations_obj:
            for violations in violations_obj.values():
                if isinstance(violations, list):
                    for _violation in violations:
                        pass


def main() -> None:
    """Main function."""
    diagnostic = FlextDiagnostic()
    report = diagnostic.run_full_diagnostic()
    diagnostic.print_report(report)

    # Save report in JSON
    report_file = "scripts/architecture/diagnostic_report.json"
    Path(report_file).parent.mkdir(parents=True, exist_ok=True)

    with Path(report_file).open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Return exit code based on errors
    summary_obj = report.get("summary", {})
    if isinstance(summary_obj, dict):
        projects_with_errors = summary_obj.get("projects_with_errors", 0)
        if (
            isinstance(projects_with_errors, (int, str))
            and int(projects_with_errors) > 0
        ):
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
