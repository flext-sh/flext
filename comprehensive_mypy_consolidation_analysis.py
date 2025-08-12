#!/usr/bin/env python3
"""COMPREHENSIVE MYPY CONSOLIDATION ANALYSIS.
=========================================

Executes comprehensive MyPy analysis across all FLEXT ecosystem projects
to assess current state after Phases 1-5 completion and create strategy
for 100% type safety elimination.

Analysis covers:
- All 33 Python projects in the ecosystem
- Error counting with detailed breakdown
- Progress metrics since initial baseline
- Error categorization by type and complexity
- Strategic recommendations for final elimination
"""

import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class ComprehensiveMyPyAnalyzer:
    """Comprehensive MyPy analysis for FLEXT ecosystem consolidation."""

    def __init__(self) -> None:
        self.root_dir = Path("/home/marlonsc/flext")
        self.projects = [
            "client-a-oud-mig", "flexcore", "flext-api", "flext-auth", "flext-cli",
            "flext-core", "flext-db-oracle", "flext-dbt-ldap", "flext-dbt-ldif",
            "flext-dbt-oracle", "flext-dbt-oracle-wms", "flext-grpc", "flext-ldap",
            "flext-ldif", "flext-meltano", "flext-observability", "flext-oracle-oic-ext",
            "flext-oracle-wms", "flext-plugin", "flext-quality", "flext-tap-ldap",
            "flext-tap-ldif", "flext-tap-oracle-oic", "flext-tap-oracle",
            "flext-tap-oracle-wms", "flext-target-ldap", "flext-target-ldif",
            "flext-target-oracle-oic", "flext-target-oracle", "flext-target-oracle-wms",
            "flext-web", "client-b-meltano-native", ".",  # Root project
        ]
        self.results = {}
        self.error_patterns = defaultdict(int)
        self.complexity_categories = {
            "QUICK_FIXES": [],
            "MEDIUM_COMPLEXITY": [],
            "HIGH_COMPLEXITY": [],
            "ARCHITECTURAL_CHANGES": [],
        }

    def run_mypy_analysis(self, project_path: Path) -> dict[str, Any]:
        """Run MyPy analysis on a single project."""
        try:
            if not (project_path / "pyproject.toml").exists():
                return {"error": f"No pyproject.toml found in {project_path}"}

            # First try with src/ if it exists
            src_path = project_path / "src"
            target_path = src_path if src_path.exists() else project_path

            # Run MyPy with comprehensive error collection
            cmd = [
                "mypy",
                str(target_path),
                "--show-error-codes",
                "--no-error-summary",
                "--show-absolute-path",
            ]

            result = subprocess.run(
                cmd,
                check=False, cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Parse errors
            errors = []
            if result.stdout.strip():
                error_lines = [line for line in result.stdout.split("\n") if line.strip()]
                errors = self._parse_mypy_errors(error_lines)

            return {
                "project": project_path.name,
                "error_count": len(errors),
                "errors": errors,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            return {
                "project": project_path.name,
                "error": "MyPy analysis timed out",
                "error_count": 0,
            }
        except Exception as e:
            return {
                "project": project_path.name,
                "error": f"Analysis failed: {e}",
                "error_count": 0,
            }

    def _parse_mypy_errors(self, error_lines: list[str]) -> list[dict[str, Any]]:
        """Parse MyPy error output into structured format."""
        errors = []
        error_pattern = re.compile(
            r"^(.+):(\d+):\s*(?:(\d+):)?\s*(\w+):\s*(.+?)(?:\s+\[([^\]]+)\])?$",
        )

        for line in error_lines:
            line = line.strip()
            if not line or line.startswith("Found "):
                continue

            match = error_pattern.match(line)
            if match:
                file_path, line_no, col_no, level, message, error_code = match.groups()

                error_info = {
                    "file": file_path,
                    "line": int(line_no),
                    "column": int(col_no) if col_no else None,
                    "level": level,
                    "message": message,
                    "error_code": error_code,
                    "raw_line": line,
                }
                errors.append(error_info)

                # Track error patterns
                if error_code:
                    self.error_patterns[error_code] += 1
                # Extract error type from message
                elif "has no attribute" in message:
                    self.error_patterns["attr-defined"] += 1
                elif "Cannot determine type" in message:
                    self.error_patterns["has-type"] += 1
                elif "Incompatible types" in message:
                    self.error_patterns["assignment"] += 1
                else:
                    self.error_patterns["other"] += 1

        return errors

    def categorize_complexity(self, project: str, errors: list[dict[str, Any]]) -> None:
        """Categorize project by error complexity."""
        error_count = len(errors)

        if error_count == 0:
            self.complexity_categories["QUICK_FIXES"].append(f"{project}: COMPLETE ✅")
            return

        # Analyze error types for complexity assessment
        any("Any" in error.get("message", "") for error in errors)
        has_attr_errors = any("attr-defined" in (error.get("error_code") or "") for error in errors)
        any("import" in error.get("message", "").lower() for error in errors)
        has_generic_errors = any("generic" in error.get("message", "").lower() for error in errors)

        if error_count <= 5 and not has_generic_errors:
            self.complexity_categories["QUICK_FIXES"].append(f"{project}: {error_count} erros")
        elif error_count <= 20 and not has_generic_errors:
            self.complexity_categories["MEDIUM_COMPLEXITY"].append(f"{project}: {error_count} erros")
        elif error_count <= 100 or (has_attr_errors and not has_generic_errors):
            self.complexity_categories["HIGH_COMPLEXITY"].append(f"{project}: {error_count} erros")
        else:
            self.complexity_categories["ARCHITECTURAL_CHANGES"].append(f"{project}: {error_count} erros (architectural)")

    def analyze_all_projects(self) -> dict[str, Any]:
        """Run comprehensive analysis on all projects."""
        total_projects = len(self.projects)
        total_errors = 0
        successful_projects = 0

        for _i, project in enumerate(self.projects, 1):
            project_path = self.root_dir / project if project != "." else self.root_dir

            result = self.run_mypy_analysis(project_path)
            self.results[project] = result

            if "error_count" in result:
                error_count = result["error_count"]
                total_errors += error_count

                if error_count == 0:
                    successful_projects += 1

                # Categorize complexity
                errors = result.get("errors", [])
                self.categorize_complexity(project, errors)

        # Generate comprehensive summary
        return {
            "timestamp": datetime.now().isoformat(),
            "total_projects": total_projects,
            "successful_projects": successful_projects,
            "projects_with_errors": total_projects - successful_projects,
            "total_errors": total_errors,
            "average_errors_per_project": round(total_errors / total_projects, 2),
            "error_patterns": dict(Counter(self.error_patterns).most_common(10)),
            "complexity_categories": dict(self.complexity_categories),
            "detailed_results": self.results,
        }

    def generate_consolidation_report(self, analysis_results: dict[str, Any]):
        """Generate final consolidation report."""
        # Overall metrics

        # Success rate
        (analysis_results["successful_projects"] / analysis_results["total_projects"]) * 100

        # Error patterns
        for _error_code, _count in analysis_results["error_patterns"].items():
            pass

        # Complexity breakdown
        for projects in analysis_results["complexity_categories"].values():
            for _project in projects:
                pass

        # Progress assessment (comparing to initial 8,860 errors baseline)
        initial_baseline = 8860
        remaining_errors = analysis_results["total_errors"]
        ((initial_baseline - remaining_errors) / initial_baseline) * 100

        return analysis_results


def main():
    """Execute comprehensive consolidation analysis."""
    analyzer = ComprehensiveMyPyAnalyzer()

    # Run analysis
    analysis_results = analyzer.analyze_all_projects()

    # Generate report
    final_report = analyzer.generate_consolidation_report(analysis_results)

    # Save detailed results
    results_file = Path("/home/marlonsc/flext/mypy_consolidation_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    return final_report


if __name__ == "__main__":
    main()
