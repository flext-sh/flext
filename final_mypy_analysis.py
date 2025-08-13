#!/usr/bin/env python3
"""Final Comprehensive MyPy Error Analysis for FLEXT Ecosystem.

This script correctly parses MyPy's multiline error format to provide
accurate error categorization and actionable recommendations.
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
class FinalProjectAnalysis:
    """Final analysis results for a single project."""

    name: str
    path: str
    total_errors: int
    error_codes: dict[str, int]
    error_messages: dict[str, list[str]]  # Sample messages per error code
    error_files: dict[str, int]  # Errors per file
    has_src: bool
    has_pyproject: bool
    analysis_successful: bool
    analysis_time: float


class FinalMyPyAnalyzer:
    """Final comprehensive MyPy analyzer with correct multiline parsing."""

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

            result = subprocess.run(  # noqa: S603 - Internal development tool
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

    def parse_mypy_output_multiline(self, mypy_output: str) -> tuple[dict[str, int], dict[str, list[str]], dict[str, int]]:
        """Parse MyPy's multiline output format correctly."""
        error_codes = defaultdict(int)
        error_messages = defaultdict(list)
        error_files = defaultdict(int)

        if not mypy_output:
            return dict(error_codes), dict(error_messages), dict(error_files)

        lines = mypy_output.strip().split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for error lines in format: filename:line:col: error: message
            if ": error:" in line and ":" in line:
                # Extract file name
                file_part = line.split(":")[0]
                if file_part:
                    file_name = Path(file_part).name
                    error_files[file_name] += 1

                # Look for error code on this line or next few lines
                error_code = None
                error_message = line

                # Check current line for [error-code]
                if "[" in line and line.endswith("]"):
                    bracket_start = line.rfind("[")
                    bracket_end = line.rfind("]")
                    if bracket_start != -1 and bracket_end != -1 and bracket_start < bracket_end:
                        error_code = line[bracket_start + 1:bracket_end]

                # If no code on current line, check next line
                if error_code is None and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if "[" in next_line and next_line.strip().endswith("]"):
                        bracket_start = next_line.rfind("[")
                        bracket_end = next_line.rfind("]")
                        if bracket_start != -1 and bracket_end != -1 and bracket_start < bracket_end:
                            error_code = next_line[bracket_start + 1:bracket_end]
                            # Combine the error message with the code line
                            error_message = f"{line} {next_line.strip()}"
                            i += 1  # Skip the next line since we processed it

                # If still no code, check if next line continues the error
                if error_code is None and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Look for continued error messages that end with [code]
                    if (not next_line.startswith("src/") and
                        not next_line.startswith("/") and
                        "[" in next_line and next_line.strip().endswith("]")):
                        bracket_start = next_line.rfind("[")
                        bracket_end = next_line.rfind("]")
                        if bracket_start != -1 and bracket_end != -1 and bracket_start < bracket_end:
                            error_code = next_line[bracket_start + 1:bracket_end]
                            error_message = f"{line} {next_line.strip()}"
                            i += 1  # Skip the next line since we processed it

                # Assign error code (default if not found)
                if error_code is None:
                    error_code = "no-error-code"

                # Count the error
                error_codes[error_code] += 1

                # Store sample error message (limit to 3 per type)
                if len(error_messages[error_code]) < 3:
                    # Clean up the error message
                    clean_message = error_message.replace(str(self.base_path), "")
                    error_messages[error_code].append(clean_message)

            i += 1

        return dict(error_codes), dict(error_messages), dict(error_files)

    def analyze_project(self, project_path: Path) -> FinalProjectAnalysis:
        """Analyze a single project with correct multiline parsing."""
        mypy_output, success, analysis_time = self.run_mypy_analysis(project_path)
        error_codes, error_messages, error_files = self.parse_mypy_output_multiline(mypy_output)

        total_errors = sum(error_codes.values())

        if total_errors == 0:
            pass
        else:
            max(error_codes.items(), key=operator.itemgetter(1)) if error_codes else ("unknown", 0)

        return FinalProjectAnalysis(
            name=project_path.name,
            path=str(project_path),
            total_errors=total_errors,
            error_codes=error_codes,
            error_messages=error_messages,
            error_files=error_files,
            has_src=(project_path / "src").exists(),
            has_pyproject=(project_path / "pyproject.toml").exists(),
            analysis_successful=success,
            analysis_time=analysis_time,
        )

    def run_final_analysis(self) -> list[FinalProjectAnalysis]:
        """Run final comprehensive analysis on all projects."""
        projects = self.get_python_projects()

        analyses = []
        for project in projects:
            analysis = self.analyze_project(project)
            analyses.append(analysis)

        return analyses

    def print_executive_report(self, analyses: list[FinalProjectAnalysis]) -> None:
        """Print executive summary report with actionable insights."""
        total_projects = len(analyses)
        total_errors = sum(a.total_errors for a in analyses)
        zero_error_projects = sum(1 for a in analyses if a.total_errors == 0)
        (zero_error_projects / total_projects * 100) if total_projects > 0 else 0

        # Aggregate all error codes
        all_error_codes = Counter()
        for analysis in analyses:
            for code, count in analysis.error_codes.items():
                all_error_codes[code] += count

        zero_projects = [a for a in analyses if a.total_errors == 0]
        for analysis in zero_projects:
            pass

        for _i, (error_code, count) in enumerate(all_error_codes.most_common(10), 1):
            (count / total_errors * 100) if total_errors > 0 else 0
            sum(1 for a in analyses if error_code in a.error_codes)

        # Group by error severity
        critical_projects = [a for a in analyses if a.total_errors >= 80]
        high_projects = [a for a in analyses if 30 <= a.total_errors < 80]
        medium_projects = [a for a in analyses if 10 <= a.total_errors < 30]
        low_projects = [a for a in analyses if 1 <= a.total_errors < 10]

        if critical_projects:
            for project in sorted(critical_projects, key=lambda x: x.total_errors, reverse=True):
                max(project.error_codes.items(), key=operator.itemgetter(1))[0] if project.error_codes else "N/A"

        if high_projects:
            for project in sorted(high_projects, key=lambda x: x.total_errors, reverse=True):
                max(project.error_codes.items(), key=operator.itemgetter(1))[0] if project.error_codes else "N/A"

        if medium_projects:
            for project in sorted(medium_projects, key=lambda x: x.total_errors, reverse=True):
                max(project.error_codes.items(), key=operator.itemgetter(1))[0] if project.error_codes else "N/A"

        if low_projects:
            for project in sorted(low_projects, key=lambda x: x.total_errors, reverse=True):
                pass

        # Sample error messages for top error types
        for error_code, count in all_error_codes.most_common(5):

            # Find sample messages from projects
            sample_messages = []
            for analysis in analyses:
                if error_code in analysis.error_messages:
                    sample_messages.extend(analysis.error_messages[error_code][:2])
                    if len(sample_messages) >= 3:
                        break

            for _i, message in enumerate(sample_messages[:3], 1):
                # Clean and truncate message
                clean_msg = message.replace("/home/marlonsc/flext/", "").replace("\n", " ")
                if len(clean_msg) > 80:
                    clean_msg = clean_msg[:77] + "..."

        all_error_codes.most_common(1)[0] if all_error_codes else ("none", 0)

        ", ".join([a.name for a in zero_projects[:5]])

        critical_hours = len(critical_projects) * 4
        high_hours = len(high_projects) * 2
        medium_hours = len(medium_projects) * 1
        low_hours = len(low_projects) * 0.5
        critical_hours + high_hours + medium_hours + low_hours

    def save_comprehensive_report(self, analyses: list[FinalProjectAnalysis], filename: str = "final_mypy_ecosystem_analysis.json") -> None:
        """Save comprehensive analysis report."""
        output_file = self.base_path / filename

        # Calculate ecosystem-wide statistics
        total_errors = sum(a.total_errors for a in analyses)
        all_error_codes = Counter()
        for analysis in analyses:
            for code, count in analysis.error_codes.items():
                all_error_codes[code] += count

        report_data = {
            "executive_summary": {
                "total_projects": len(analyses),
                "projects_with_zero_errors": sum(1 for a in analyses if a.total_errors == 0),
                "total_errors": total_errors,
                "success_rate": (sum(1 for a in analyses if a.total_errors == 0) / len(analyses) * 100) if analyses else 0,
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "top_error_types": dict(all_error_codes.most_common(10)),
            },
            "strategic_priorities": {
                "critical": [{"name": a.name, "errors": a.total_errors} for a in analyses if a.total_errors >= 80],
                "high": [{"name": a.name, "errors": a.total_errors} for a in analyses if 30 <= a.total_errors < 80],
                "medium": [{"name": a.name, "errors": a.total_errors} for a in analyses if 10 <= a.total_errors < 30],
                "low": [{"name": a.name, "errors": a.total_errors} for a in analyses if 1 <= a.total_errors < 10],
            },
            "success_stories": [a.name for a in analyses if a.total_errors == 0],
            "detailed_projects": [
                {
                    "name": a.name,
                    "path": a.path,
                    "total_errors": a.total_errors,
                    "error_codes": a.error_codes,
                    "error_messages": a.error_messages,
                    "error_files": a.error_files,
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
    analyzer = FinalMyPyAnalyzer()

    try:
        analyses = analyzer.run_final_analysis()
        analyzer.print_executive_report(analyses)
        analyzer.save_comprehensive_report(analyses)

        return 0

    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main())
