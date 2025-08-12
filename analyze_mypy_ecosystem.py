#!/usr/bin/env python3
"""FLEXT Ecosystem MyPy Error Analysis Script.

Analyzes all Python projects in the FLEXT ecosystem for MyPy errors.
"""

import json
import operator
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class ProjectResult:
    """Structured result of a MyPy analysis run for one project.

    Captures project metadata, error counts per area (src/tests/examples),
    categorized error types, and a small set of sample error lines.
    """

    name: str
    path: str
    has_mypy_config: bool
    src_errors: int
    test_errors: int
    example_errors: int
    total_errors: int
    error_types: dict[str, int]
    sample_errors: list[str]
    success: bool
    error_message: str | None = None


class FlextMypyAnalyzer:
    """Analyze MyPy errors across all FLEXT Python projects in the monorepo."""

    PYTHON_PROJECTS: ClassVar[list[str]] = [
        # Core libraries
        "flext-core", "flext-api", "flext-auth", "flext-web", "flext-cli",

        # Infrastructure libraries
        "flext-db-oracle", "flext-ldap", "flext-ldif", "flext-oracle-wms",
        "flext-grpc", "flext-observability", "flext-meltano", "flext-plugin",
        "flext-quality",

        # Extensions
        "flext-oracle-oic-ext",

        # Singer Taps (5)
        "flext-tap-ldap", "flext-tap-ldif", "flext-tap-oracle",
        "flext-tap-oracle-oic", "flext-tap-oracle-wms",

        # Singer Targets (5)
        "flext-target-ldap", "flext-target-ldif", "flext-target-oracle",
        "flext-target-oracle-oic", "flext-target-oracle-wms",

        # DBT Projects (4)
        "flext-dbt-ldap", "flext-dbt-ldif", "flext-dbt-oracle", "flext-dbt-oracle-wms",

        # Legacy/Specialized
        "algar-oud-mig", "gruponos-meltano-native",
    ]

    ERROR_PATTERNS: ClassVar[dict[str, str]] = {
        "missing_imports": r"Cannot find implementation or library stub for module",
        "untyped_imports": r"Skipping analyzing .* untyped",
        "missing_return_type": r"Function is missing a return type annotation",
        "missing_parameter_type": r"Function is missing a type annotation for one or more arguments",
        "any_type": r"has type .*(Any|_SpecialForm).*",
        "attribute_error": r"has no attribute",
        "incompatible_types": r"Incompatible types in",
        "incompatible_return": r"Incompatible return value type",
        "incompatible_assignment": r"Incompatible types in assignment",
        "unused_ignore": r"Unused .* comment",
        "type_ignore": r"type: ignore",
        "call_error": r"Too (many|few) arguments|Unexpected keyword argument",
        "override_error": r"Signature.*incompatible with supertype",
        "name_defined": r"Name .* already defined",
        "unreachable_code": r"Statement is unreachable",
        "no_untyped_def": r"Function .* is untyped",
        "misc_error": r".*",  # Catch-all for other errors
    }

    def __init__(self, base_path: str = "/home/marlonsc/flext") -> None:
        """Initialize the analyzer.

        Args:
            base_path: Filesystem path to the monorepo root where projects live.

        """
        self.base_path = Path(base_path)
        self.results: list[ProjectResult] = []

    def analyze_project(self, project_name: str) -> ProjectResult:
        """Analyze a single project for MyPy errors."""
        project_path = self.base_path / project_name

        if not project_path.exists():
            return ProjectResult(
                name=project_name,
                path=str(project_path),
                has_mypy_config=False,
                src_errors=0,
                test_errors=0,
                example_errors=0,
                total_errors=0,
                error_types={},
                sample_errors=[],
                success=False,
                error_message=f"Project path does not exist: {project_path}",
            )

        # Check for MyPy configuration
        has_mypy_config = any([
            (project_path / "mypy.ini").exists(),
            (project_path / ".mypy.ini").exists(),
            (project_path / "setup.cfg").exists(),
            (project_path / "pyproject.toml").exists(),
        ])

        # Run MyPy on different directories
        src_errors, src_output = self._run_mypy(project_path, "src")
        test_errors, test_output = self._run_mypy(project_path, "tests")
        example_errors, example_output = self._run_mypy(project_path, "examples")

        # Combine all outputs
        all_output = f"{src_output}\n{test_output}\n{example_output}"

        # Analyze error types
        error_types = self._categorize_errors(all_output)

        # Get sample errors (first 10)
        sample_errors = self._extract_sample_errors(all_output)

        total_errors = src_errors + test_errors + example_errors

        return ProjectResult(
            name=project_name,
            path=str(project_path),
            has_mypy_config=has_mypy_config,
            src_errors=src_errors,
            test_errors=test_errors,
            example_errors=example_errors,
            total_errors=total_errors,
            error_types=error_types,
            sample_errors=sample_errors,
            success=True,
        )

    def _run_mypy(self, project_path: Path, subdir: str) -> tuple[int, str]:
        """Run MyPy on a specific subdirectory and return error count and output."""
        target_dir = project_path / subdir

        if not target_dir.exists():
            return 0, ""

        try:
            # Change to project directory to respect local config
            cmd = [
                "python", "-m", "mypy",
                str(subdir),
                "--show-error-codes",
                "--no-error-summary",
            ]

            result = subprocess.run(  # noqa: S603
                cmd,
                check=False, cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            # Count errors (lines that contain error indicators)
            error_lines = [
                line for line in result.stdout.split("\n")
                if ": error:" in line or ": warning:" in line
            ]

            return len(error_lines), result.stdout

        except subprocess.TimeoutExpired:
            return -1, f"MyPy timeout for {subdir}"
        except Exception as e:
            return -1, f"MyPy error for {subdir}: {e}"

    def _categorize_errors(self, output: str) -> dict[str, int]:
        """Categorize errors by pattern."""
        error_types = defaultdict(int)

        for line in output.split("\n"):
            if ": error:" in line or ": warning:" in line:
                categorized = False
                for category, pattern in self.ERROR_PATTERNS.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        error_types[category] += 1
                        categorized = True
                        break

                if not categorized:
                    error_types["uncategorized"] += 1

        return dict(error_types)

    def _extract_sample_errors(self, output: str, limit: int = 10) -> list[str]:
        """Extract sample error messages."""
        error_lines = [
            line.strip() for line in output.split("\n")
            if ": error:" in line or ": warning:" in line
        ]

        return error_lines[:limit]

    def analyze_all_projects(self) -> None:
        """Analyze all Python projects in the ecosystem."""
        for _i, project_name in enumerate(self.PYTHON_PROJECTS, 1):

            result = self.analyze_project(project_name)
            self.results.append(result)

            if result.success and result.total_errors > 0:
                pass

    def generate_report(self) -> dict:
        """Generate comprehensive analysis report."""
        successful_projects = [r for r in self.results if r.success]
        failed_projects = [r for r in self.results if not r.success]

        # Overall statistics
        total_errors = sum(r.total_errors for r in successful_projects)
        total_src_errors = sum(r.src_errors for r in successful_projects)
        total_test_errors = sum(r.test_errors for r in successful_projects)
        total_example_errors = sum(r.example_errors for r in successful_projects)

        # Error type aggregation
        all_error_types = defaultdict(int)
        for result in successful_projects:
            for error_type, count in result.error_types.items():
                all_error_types[error_type] += count

        # Project rankings
        projects_by_errors = sorted(
            successful_projects,
            key=lambda r: r.total_errors,
            reverse=True,
        )

        # Most problematic projects (top 10)
        most_problematic = projects_by_errors[:10]

        # Projects with no errors
        clean_projects = [r for r in successful_projects if r.total_errors == 0]

        # Projects with MyPy config
        projects_with_config = [r for r in successful_projects if r.has_mypy_config]

        return {
            "summary": {
                "total_projects_analyzed": len(self.PYTHON_PROJECTS),
                "successful_analyses": len(successful_projects),
                "failed_analyses": len(failed_projects),
                "total_errors": total_errors,
                "src_errors": total_src_errors,
                "test_errors": total_test_errors,
                "example_errors": total_example_errors,
                "clean_projects": len(clean_projects),
                "projects_with_config": len(projects_with_config),
            },
            "error_types": dict(sorted(all_error_types.items(), key=operator.itemgetter(1), reverse=True)),
            "most_problematic_projects": [
                {
                    "name": r.name,
                    "total_errors": r.total_errors,
                    "src_errors": r.src_errors,
                    "test_errors": r.test_errors,
                    "example_errors": r.example_errors,
                    "has_config": r.has_mypy_config,
                } for r in most_problematic
            ],
            "clean_projects": [r.name for r in clean_projects],
            "failed_projects": [
                {"name": r.name, "error": r.error_message}
                for r in failed_projects
            ],
            "detailed_results": [
                {
                    "name": r.name,
                    "path": r.path,
                    "has_mypy_config": r.has_mypy_config,
                    "errors": {
                        "src": r.src_errors,
                        "tests": r.test_errors,
                        "examples": r.example_errors,
                        "total": r.total_errors,
                    },
                    "error_types": r.error_types,
                    "sample_errors": r.sample_errors[:5],  # First 5 samples
                } for r in successful_projects
            ],
        }

    def print_executive_summary(self, report: dict) -> None:
        """Print executive summary of the analysis."""
        report["summary"]

        for _i, (_error_type, _count) in enumerate(list(report["error_types"].items())[:10], 1):
            pass

        for _i, project in enumerate(report["most_problematic_projects"][:10], 1):
            "📋" if project["has_config"] else "❌"

        if report["clean_projects"]:
            for _ in report["clean_projects"][:10]:  # Show first 10
                pass
            DISPLAY_LIMIT = 10
            if len(report["clean_projects"]) > DISPLAY_LIMIT:
                pass

        if report["failed_projects"]:
            for _ in report["failed_projects"]:
                pass


def main() -> None:
    """Main execution function."""
    analyzer = FlextMypyAnalyzer()

    # Run analysis
    analyzer.analyze_all_projects()

    # Generate report
    report = analyzer.generate_report()

    # Print executive summary
    analyzer.print_executive_summary(report)

    # Save detailed report
    report_path = "/home/marlonsc/flext/mypy_ecosystem_analysis.json"
    Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
