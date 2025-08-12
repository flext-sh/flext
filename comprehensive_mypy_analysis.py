#!/usr/bin/env python3
"""Comprehensive MyPy Error Analysis for FLEXT Ecosystem.

This script performs MyPy analysis across all FLEXT projects and generates
a detailed report with statistics, error categorization, and recommendations.
"""

import json
import operator
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectAnalysis:
    """Analysis results for a single project."""

    name: str
    path: str
    total_errors: int
    error_categories: dict[str, int]
    error_details: list[str]
    has_src: bool
    has_pyproject: bool
    analysis_successful: bool
    analysis_time: float


@dataclass
class EcosystemReport:
    """Comprehensive ecosystem analysis report."""

    total_projects: int
    analyzed_projects: int
    projects_with_zero_errors: int
    total_errors: int
    project_analyses: list[ProjectAnalysis]
    top_error_types: dict[str, int]
    most_problematic_projects: list[tuple[str, int]]
    success_rate: float
    analysis_timestamp: str


class MyPyEcosystemAnalyzer:
    """Comprehensive MyPy analyzer for FLEXT ecosystem."""

    def __init__(self, base_path: str = "/home/marlonsc/flext") -> None:
        self.base_path = Path(base_path)
        self.flext_core_path = self.base_path / "flext-core"
        # Updated pattern to handle MyPy's multi-line error format
        self.error_pattern = re.compile(r".*:(\d+):\d*:\s*error:\s*(.*?)\s*\[([^\]]+)\].*")

    def get_python_projects(self) -> list[Path]:
        """Find all flext-* projects with src/ and pyproject.toml."""
        projects = [item for item in self.base_path.iterdir() if item.is_dir() and
                item.name.startswith("flext-") and
                (item / "src").exists() and
                (item / "pyproject.toml").exists()]
        return sorted(projects)

    def setup_environment(self, project_path: Path) -> dict[str, str]:
        """Setup environment variables for MyPy analysis."""
        env = os.environ.copy()

        # Add flext-core to PYTHONPATH for dependency resolution
        pythonpath_components = [
            str(self.flext_core_path / "src"),
            str(project_path / "src"),
        ]

        if "PYTHONPATH" in env:
            pythonpath_components.append(env["PYTHONPATH"])

        env["PYTHONPATH"] = ":".join(pythonpath_components)
        return env

    def run_mypy_analysis(self, project_path: Path) -> tuple[list[str], bool, float]:
        """Run MyPy analysis on a project."""
        start_time = time.time()

        try:
            env = self.setup_environment(project_path)

            cmd = [
                "python", "-m", "mypy",
                "src",
                "--show-error-codes",
                "--no-error-summary",
                "--show-absolute-path",
            ]

            result = subprocess.run(
                cmd,
                check=False, cwd=project_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout per project
            )

            analysis_time = time.time() - start_time

            if result.returncode == 0:
                return [], True, analysis_time
            error_lines = [line for line in result.stdout.split("\n") if line.strip()]
            return error_lines, True, analysis_time

        except subprocess.TimeoutExpired:
            return ["MyPy analysis timed out"], False, time.time() - start_time
        except Exception as e:
            return [f"MyPy analysis failed: {e}"], False, time.time() - start_time

    def categorize_errors(self, error_lines: list[str]) -> dict[str, int]:
        """Categorize MyPy errors by type."""
        categories = defaultdict(int)

        for line in error_lines:
            # Handle multi-line format and extract error codes
            if ": error:" in line and "[" in line and "]" in line:
                # Extract error code between brackets
                start_bracket = line.rfind("[")
                end_bracket = line.rfind("]")
                if start_bracket != -1 and end_bracket != -1 and start_bracket < end_bracket:
                    error_code = line[start_bracket + 1:end_bracket]
                    categories[error_code] += 1
                else:
                    categories["parse-error"] += 1
            elif ": error:" in line:
                # Error without code
                categories["no-error-code"] += 1

        return dict(categories)

    def analyze_project(self, project_path: Path) -> ProjectAnalysis:
        """Analyze a single project."""
        error_lines, success, analysis_time = self.run_mypy_analysis(project_path)
        error_categories = self.categorize_errors(error_lines)
        total_errors = sum(error_categories.values())

        if total_errors == 0:
            pass

        return ProjectAnalysis(
            name=project_path.name,
            path=str(project_path),
            total_errors=total_errors,
            error_categories=error_categories,
            error_details=error_lines[:50],  # Limit to first 50 errors
            has_src=(project_path / "src").exists(),
            has_pyproject=(project_path / "pyproject.toml").exists(),
            analysis_successful=success,
            analysis_time=analysis_time,
        )

    def generate_ecosystem_report(self, analyses: list[ProjectAnalysis]) -> EcosystemReport:
        """Generate comprehensive ecosystem report."""
        total_projects = len(analyses)
        analyzed_projects = sum(1 for a in analyses if a.analysis_successful)
        projects_with_zero_errors = sum(1 for a in analyses if a.total_errors == 0)
        total_errors = sum(a.total_errors for a in analyses)

        # Aggregate error types across all projects
        all_error_types = Counter()
        for analysis in analyses:
            for error_type, count in analysis.error_categories.items():
                all_error_types[error_type] += count

        # Most problematic projects
        most_problematic = sorted(
            [(a.name, a.total_errors) for a in analyses],
            key=operator.itemgetter(1),
            reverse=True,
        )[:10]

        success_rate = (projects_with_zero_errors / total_projects * 100) if total_projects > 0 else 0

        return EcosystemReport(
            total_projects=total_projects,
            analyzed_projects=analyzed_projects,
            projects_with_zero_errors=projects_with_zero_errors,
            total_errors=total_errors,
            project_analyses=analyses,
            top_error_types=dict(all_error_types.most_common(15)),
            most_problematic_projects=most_problematic,
            success_rate=success_rate,
            analysis_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def print_detailed_report(self, report: EcosystemReport) -> None:
        """Print comprehensive analysis report."""
        for _i, (_name, errors) in enumerate(report.most_problematic_projects, 1):
            if errors > 0:
                pass

        zero_error_projects = [a.name for a in report.project_analyses if a.total_errors == 0]
        if zero_error_projects:
            for _project in zero_error_projects:
                pass

        for _i, (_error_type, _count) in enumerate(report.top_error_types.items(), 1):
            pass

        for analysis in sorted(report.project_analyses, key=lambda a: a.total_errors, reverse=True):

            if analysis.total_errors > 0 and analysis.error_categories:
                # Show top 5 error types for this project
                top_errors = sorted(analysis.error_categories.items(), key=operator.itemgetter(1), reverse=True)[:5]
                for _error_type, _count in top_errors:
                    pass

    def save_json_report(self, report: EcosystemReport, filename: str = "mypy_ecosystem_analysis.json") -> None:
        """Save detailed report as JSON."""
        output_file = self.base_path / filename

        # Convert report to JSON-serializable format
        report_data = {
            "metadata": {
                "total_projects": report.total_projects,
                "analyzed_projects": report.analyzed_projects,
                "projects_with_zero_errors": report.projects_with_zero_errors,
                "total_errors": report.total_errors,
                "success_rate": report.success_rate,
                "analysis_timestamp": report.analysis_timestamp,
            },
            "top_error_types": report.top_error_types,
            "most_problematic_projects": report.most_problematic_projects,
            "projects": [
                {
                    "name": a.name,
                    "path": a.path,
                    "total_errors": a.total_errors,
                    "error_categories": a.error_categories,
                    "analysis_successful": a.analysis_successful,
                    "analysis_time": a.analysis_time,
                }
                for a in report.project_analyses
            ],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def run_comprehensive_analysis(self) -> EcosystemReport:
        """Run comprehensive MyPy analysis across entire ecosystem."""
        projects = self.get_python_projects()

        analyses = []
        for project in projects:
            analysis = self.analyze_project(project)
            analyses.append(analysis)

        return self.generate_ecosystem_report(analyses)


def main() -> int | None:
    """Main entry point."""
    analyzer = MyPyEcosystemAnalyzer()

    try:
        report = analyzer.run_comprehensive_analysis()
        analyzer.print_detailed_report(report)
        analyzer.save_json_report(report)

        return 0

    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())
