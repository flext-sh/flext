#!/usr/bin/env python3
"""Detailed MyPy Error Analysis for FLEXT Ecosystem.

This script performs detailed MyPy analysis across all FLEXT projects with
proper error code categorization and specific error pattern analysis.
"""

import json
import operator
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DetailedProjectAnalysis:
    """Detailed analysis results for a single project."""

    name: str
    path: str
    total_errors: int
    error_codes: dict[str, int]
    sample_errors: list[str]  # First few errors of each type
    error_files: dict[str, int]  # Errors per file
    has_src: bool
    has_pyproject: bool
    analysis_successful: bool
    analysis_time: float


class DetailedMyPyAnalyzer:
    """Detailed MyPy analyzer with better error categorization."""

    def __init__(self, base_path: str = "/home/marlonsc/flext") -> None:
        self.base_path = Path(base_path)
        self.flext_core_path = self.base_path / "flext-core"

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

    def run_mypy_analysis(self, project_path: Path) -> tuple[str, bool, float]:
        """Run MyPy analysis and return complete output."""
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
                timeout=120,  # 2 minute timeout
            )

            analysis_time = time.time() - start_time

            if result.returncode == 0:
                return "", True, analysis_time
            return result.stdout, True, analysis_time

        except subprocess.TimeoutExpired:
            return f"MyPy analysis timed out for {project_path.name}", False, time.time() - start_time
        except Exception as e:
            return f"MyPy analysis failed: {e}", False, time.time() - start_time

    def parse_mypy_output(self, mypy_output: str) -> tuple[dict[str, int], dict[str, int], list[str]]:
        """Parse MyPy output to extract error codes, file counts, and samples."""
        error_codes = defaultdict(int)
        error_files = defaultdict(int)
        sample_errors = []

        lines = mypy_output.strip().split("\n") if mypy_output else []

        for line in lines:
            if ": error:" in line:
                # Extract error code if present
                if "[" in line and "]" in line:
                    # Find the last occurrence of [error-code]
                    bracket_start = line.rfind("[")
                    bracket_end = line.rfind("]")

                    if bracket_start != -1 and bracket_end != -1 and bracket_start < bracket_end:
                        error_code = line[bracket_start + 1:bracket_end]
                        error_codes[error_code] += 1

                        # Store sample errors (first 3 of each type)
                        if error_codes[error_code] <= 3:
                            sample_errors.append(f"[{error_code}] {line}")
                    else:
                        error_codes["no-code"] += 1
                        if error_codes["no-code"] <= 3:
                            sample_errors.append(f"[no-code] {line}")
                else:
                    error_codes["no-brackets"] += 1
                    if error_codes["no-brackets"] <= 3:
                        sample_errors.append(f"[no-brackets] {line}")

                # Extract file name for file-based counting
                if ":" in line:
                    file_part = line.split(":")[0]
                    if file_part:
                        file_name = Path(file_part).name
                        error_files[file_name] += 1

        return dict(error_codes), dict(error_files), sample_errors

    def analyze_project(self, project_path: Path) -> DetailedProjectAnalysis:
        """Analyze a single project with detailed error breakdown."""
        mypy_output, success, analysis_time = self.run_mypy_analysis(project_path)
        error_codes, error_files, sample_errors = self.parse_mypy_output(mypy_output)

        total_errors = sum(error_codes.values())

        if total_errors == 0:
            pass
        else:
            max(error_codes.items(), key=operator.itemgetter(1)) if error_codes else ("unknown", 0)

        return DetailedProjectAnalysis(
            name=project_path.name,
            path=str(project_path),
            total_errors=total_errors,
            error_codes=error_codes,
            sample_errors=sample_errors[:15],  # Limit samples
            error_files=error_files,
            has_src=(project_path / "src").exists(),
            has_pyproject=(project_path / "pyproject.toml").exists(),
            analysis_successful=success,
            analysis_time=analysis_time,
        )

    def run_detailed_analysis(self) -> list[DetailedProjectAnalysis]:
        """Run detailed analysis on all projects."""
        projects = self.get_python_projects()

        analyses = []
        for project in projects:
            analysis = self.analyze_project(project)
            analyses.append(analysis)

        return analyses

    def print_comprehensive_report(self, analyses: list[DetailedProjectAnalysis]) -> None:
        """Print detailed comprehensive report."""
        total_projects = len(analyses)
        total_errors = sum(a.total_errors for a in analyses)
        zero_error_projects = sum(1 for a in analyses if a.total_errors == 0)
        (zero_error_projects / total_projects * 100) if total_projects > 0 else 0

        # Aggregate all error codes
        all_error_codes = Counter()
        for analysis in analyses:
            for code, count in analysis.error_codes.items():
                all_error_codes[code] += count

        problematic = sorted(analyses, key=lambda x: x.total_errors, reverse=True)[:10]
        for analysis in problematic:
            if analysis.total_errors > 0:
                max(analysis.error_codes.items(), key=operator.itemgetter(1))[0] if analysis.error_codes else "N/A"

        zero_projects = [a.name for a in analyses if a.total_errors == 0]
        if zero_projects:
            for project in zero_projects:
                pass

        for _i, (error_code, count) in enumerate(all_error_codes.most_common(15), 1):
            (count / total_errors * 100) if total_errors > 0 else 0

        for analysis in sorted(analyses, key=lambda x: x.total_errors, reverse=True):

            if analysis.total_errors > 0:
                # Show error breakdown
                for error_code, count in sorted(analysis.error_codes.items(), key=operator.itemgetter(1), reverse=True)[:5]:
                    pass

                # Show most problematic files
                if analysis.error_files:
                    top_files = sorted(analysis.error_files.items(), key=operator.itemgetter(1), reverse=True)[:3]
                    for _file_name, _error_count in top_files:
                        pass

        # Priority recommendations

        # Group projects by error count for strategy
        high_priority = [a for a in analyses if a.total_errors >= 50]
        medium_priority = [a for a in analyses if 10 <= a.total_errors < 50]
        low_priority = [a for a in analyses if 1 <= a.total_errors < 10]

        for project in high_priority:
            max(project.error_codes.items(), key=operator.itemgetter(1))[0] if project.error_codes else "N/A"

        for project in medium_priority:
            max(project.error_codes.items(), key=operator.itemgetter(1))[0] if project.error_codes else "N/A"

        for project in low_priority:
            pass

        # Systematic approach recommendations
        top_error_types = all_error_codes.most_common(5)

        for error_code, count in top_error_types:
            sum(1 for a in analyses if error_code in a.error_codes)

    def save_detailed_report(self, analyses: list[DetailedProjectAnalysis], filename: str = "detailed_mypy_ecosystem_report.json") -> None:
        """Save detailed analysis report."""
        output_file = self.base_path / filename

        # Calculate ecosystem-wide statistics
        total_errors = sum(a.total_errors for a in analyses)
        all_error_codes = Counter()
        for analysis in analyses:
            for code, count in analysis.error_codes.items():
                all_error_codes[code] += count

        report_data = {
            "metadata": {
                "total_projects": len(analyses),
                "projects_with_zero_errors": sum(1 for a in analyses if a.total_errors == 0),
                "total_errors": total_errors,
                "success_rate": (sum(1 for a in analyses if a.total_errors == 0) / len(analyses) * 100) if analyses else 0,
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "ecosystem_error_codes": dict(all_error_codes.most_common()),
            "projects": [
                {
                    "name": a.name,
                    "path": a.path,
                    "total_errors": a.total_errors,
                    "error_codes": a.error_codes,
                    "error_files": a.error_files,
                    "sample_errors": a.sample_errors,
                    "analysis_successful": a.analysis_successful,
                    "analysis_time": a.analysis_time,
                }
                for a in analyses
            ],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)


def main() -> int | None:
    """Main entry point."""
    analyzer = DetailedMyPyAnalyzer()

    try:
        analyses = analyzer.run_detailed_analysis()
        analyzer.print_comprehensive_report(analyses)
        analyzer.save_detailed_report(analyses)

        return 0

    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())
