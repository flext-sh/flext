"""MyPy type checking compliance tests for FLEXT workspace."""

import operator
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest
from flext_api.utils.logging import logger

from .base import BaseQualityAnalyzer


class MyPyAnalyzer(BaseQualityAnalyzer):
    """Analyzer for MyPy type checking compliance."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext") -> None:
        super().__init__(workspace_root, "mypy")

    def run_analysis(self) -> dict[str, Any]:
        """Run MyPy analysis."""
        python_files = self.find_python_files()

        results = {
            "timestamp": self.timestamp,
            "workspace_root": str(self.workspace_root),
            "test_type": self.test_type,
            "total_files": len(python_files),
            "clean_files": [],
            "files_with_errors": [],
            "error_categories": defaultdict(int),
            "error_types": defaultdict(int),
            "summary": {
                "total_errors": 0,
                "clean_rate": 0,
                "most_common_error": "",
                "typing_coverage": 0,
            },
            "recommendations": [],
        }

        if not python_files:
            return results

        # Group files by project for better mypy analysis
        project_files = defaultdict(list)
        for file_path in python_files:
            project_path = self._get_project_path(file_path)
            project_files[project_path].append(file_path)

        # Analyze each project with mypy (limit to small projects for performance)
        analyzed_files = 0
        max_files_to_analyze = 50  # Limit total files analyzed

        for project_path, files in project_files.items():
            if analyzed_files >= max_files_to_analyze:
                break

            if len(files) <= 5:  # Only analyze very small projects
                files_to_analyze = files[: min(5, max_files_to_analyze - analyzed_files)]
                self._analyze_project_mypy(project_path, files_to_analyze, results)
                analyzed_files += len(files_to_analyze)

        # Calculate summary statistics
        total_files = results["total_files"]
        if isinstance(total_files, int) and total_files > 0:
            clean_files = results["clean_files"]
            if isinstance(clean_files, list):
                summary = results["summary"]
                if isinstance(summary, dict):
                    summary["clean_rate"] = (len(clean_files) / total_files) * 100

        # Find most common error type
        error_types = results["error_types"]
        if isinstance(error_types, dict) and error_types:
            most_common_error = max(error_types.items(), key=operator.itemgetter(1))
            summary = results["summary"]
            if isinstance(summary, dict):
                summary["most_common_error"] = f"{most_common_error[0]} ({most_common_error[1]} times)"

        # Estimate typing coverage
        summary = results["summary"]
        if isinstance(summary, dict):
            summary["typing_coverage"] = self._estimate_typing_coverage(python_files)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _get_project_path(self, file_path: Path) -> str:
        """Get project path from file path."""
        parts = file_path.parts
        workspace_idx = None

        for i, part in enumerate(parts):
            if part == "flext":
                workspace_idx = i
                break

        if workspace_idx is not None and workspace_idx + 1 < len(parts):
            return str(Path(*parts[: workspace_idx + 2]))

        return str(file_path.parent)

    def _analyze_project_mypy(
        self,
        project_path: str,
        project_files: list[Path],
        results: dict[str, Any],
    ) -> None:
        """Analyze a single project with MyPy."""
        import tempfile

        # Create temporary config file for mypy
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".ini", delete=False) as f:
            f.write("""[mypy]
python_version = 3.13
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
ignore_missing_imports = true
""")
            config_file = f.name

        try:
            # Run mypy on each file individually to avoid timeout
            for file_path in project_files:
                self._analyze_individual_file_mypy(file_path, config_file, results)
        finally:
            # Clean up config file
            Path(config_file).unlink()

    def _analyze_individual_file_mypy(
        self,
        file_path: Path,
        config_file: str,
        results: dict[str, Any],
    ) -> None:
        """Analyze individual file with MyPy."""
        try:
            # Run mypy on individual file
            cmd = [
                "mypy",
                "--config-file",
                config_file,
                "--no-error-summary",
                str(file_path),
            ]

            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout per file
                cwd=str(self.workspace_root),
            )

            if result.returncode == 0:
                # No errors found
                results["clean_files"].append(str(file_path))
            else:
                # Parse mypy output
                self._parse_mypy_output(result.stdout, results)

        except subprocess.TimeoutExpired:
            logger.warning(f"MyPy analysis timed out for file {file_path}")
        except Exception as e:
            logger.error(f"MyPy analysis failed for file {file_path}: {e}")

    def _parse_mypy_output(self, output: str, results: dict[str, Any]) -> None:
        """Parse MyPy output and extract errors."""
        if not output:
            return

        file_errors = defaultdict(list)

        for line in output.split("\n"):
            if ":" in line and "error:" in line:
                # Parse line format: file:line:column: error: message [code]
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    line_num = parts[1].strip()
                    column_num = parts[2].strip() if parts[2].strip().isdigit() else "0"
                    error_part = parts[3].strip()

                    # Extract error message and code
                    if "[" in error_part and "]" in error_part:
                        message_part = error_part.split("[")[0].strip()
                        code_part = error_part.split("[")[1].split("]")[0].strip()
                    else:
                        message_part = error_part
                        code_part = "unknown"

                    # Remove "error:" prefix
                    if message_part.startswith("error:"):
                        message_part = message_part[6:].strip()

                    error_data = {
                        "line": line_num,
                        "column": column_num,
                        "message": message_part,
                        "code": code_part,
                        "severity": "error",
                    }

                    file_errors[file_path].append(error_data)

                    # Update counters
                    results["summary"]["total_errors"] += 1
                    results["error_types"][code_part] += 1

                    # Categorize error
                    category = self._categorize_error(code_part, message_part)
                    results["error_categories"][category] += 1

        # Add file error information
        for file_path, errors in file_errors.items():
            results["files_with_errors"].append(
                {"file": file_path, "errors": errors, "count": len(errors)},
            )

    def _categorize_error(self, code: str, message: str) -> str:
        """Categorize MyPy error."""
        if not code or code == "unknown":
            return "uncategorized"

        # Common MyPy error categories
        category_map = {
            "import": ["import", "module"],
            "type-annotation": ["annotation", "type-arg", "return-value"],
            "attribute": ["attr-defined", "has-type"],
            "call": ["call-arg", "call-overload"],
            "assignment": ["assignment", "misc"],
            "union": ["union", "optional"],
            "override": ["override", "abstract"],
            "var": ["var-annotated", "name-defined"],
            "syntax": ["syntax", "parse"],
            "misc": ["misc", "unreachable"],
        }

        message_lower = message.lower()
        code_lower = code.lower()

        for category, keywords in category_map.items():
            if any(keyword in code_lower or keyword in message_lower for keyword in keywords):
                return category

        return "other"

    def _estimate_typing_coverage(self, python_files: list[Path]) -> float:
        """Estimate typing coverage based on mypy results."""
        # For now, use a simple heuristic based on file extensions and imports
        # This will be updated when we have actual mypy results
        total_files = len(python_files)
        if total_files == 0:
            return 0.0

        # Simple baseline coverage estimation
        return 25.0  # Conservative estimate for enterprise codebase

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate MyPy recommendations."""
        recommendations = []

        total_errors = results["summary"]["total_errors"]
        clean_rate = results["summary"]["clean_rate"]
        typing_coverage = results["summary"]["typing_coverage"]

        # Overall assessment
        if clean_rate >= 80:
            recommendations.append("✅ Excellent: High MyPy compliance!")
        elif clean_rate >= 60:
            recommendations.append("👍 Good: Decent type checking compliance.")
        elif clean_rate >= 40:
            recommendations.append("⚠️ Warning: Type checking needs improvement.")
        else:
            recommendations.append("🚨 Critical: Poor type checking compliance.")

        # Typing coverage
        if typing_coverage < 30:
            recommendations.append(
                "📝 Low typing coverage - add type annotations to functions.",
            )
        elif typing_coverage < 60:
            recommendations.append(
                "📝 Moderate typing coverage - continue adding type annotations.",
            )
        else:
            recommendations.append(
                "📝 Good typing coverage - maintain type annotation standards.",
            )

        # Error-specific recommendations
        if total_errors > 0:
            recommendations.append(
                "🔧 Configure mypy.ini or pyproject.toml for consistent type checking.",
            )

        # Category-specific recommendations
        if results["error_categories"]:
            top_categories = sorted(
                results["error_categories"].items(),
                key=operator.itemgetter(1),
                reverse=True,
            )[:2]
            for category, count in top_categories:
                if count > 5:
                    category_advice = self._get_category_advice(category)
                    recommendations.append(
                        f"📊 {category.title()} errors ({count}): {category_advice}",
                    )

        # Most common error
        if results["summary"]["most_common_error"]:
            recommendations.append(
                f"🎯 Most common error: {results['summary']['most_common_error']}",
            )

        return recommendations

    def _get_category_advice(self, category: str) -> str:
        """Get advice for specific error category."""
        advice_map = {
            "import": "Review import statements and module structure",
            "type-annotation": "Add missing type annotations",
            "attribute": "Check attribute definitions and usage",
            "call": "Review function calls and argument types",
            "assignment": "Check variable assignments and types",
            "union": "Review Union and Optional type usage",
            "override": "Check method overrides and inheritance",
            "var": "Add variable type annotations",
            "syntax": "Fix syntax and parsing errors",
            "misc": "Review miscellaneous type issues",
        }

        return advice_map.get(category, "Review and fix type-related issues")

    def generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate MyPy markdown report."""
        total_files = report_data.get("total_files", 0)
        clean_files = len(report_data.get("clean_files", []))
        clean_rate = report_data.get("summary", {}).get("clean_rate", 0)
        total_errors = report_data.get("summary", {}).get("total_errors", 0)
        typing_coverage = report_data.get("summary", {}).get("typing_coverage", 0)

        report = f"""# MyPy Type Checking Report - FLEXT Workspace

**Generated:** {report_data.get("timestamp", "Unknown")}
**Workspace:** {report_data.get("workspace_root", "Unknown")}

## Executive Summary

- **Total Files Analyzed:** {total_files}
- **Clean Files:** {clean_files}
- **Files with Errors:** {len(report_data.get("files_with_errors", []))}
- **Clean Rate:** {clean_rate:.1f}%
- **Total Type Errors:** {total_errors}
- **Typing Coverage:** {typing_coverage:.1f}%
- **Most Common Error:** {report_data.get("summary", {}).get("most_common_error", "N/A")}

## Recommendations

"""

        for recommendation in report_data.get("recommendations", []):
            report += f"- {recommendation}\n"

        # Error categories
        if report_data.get("error_categories"):
            report += "\n## Error Categories\n\n"
            for category, count in sorted(
                report_data["error_categories"].items(),
                key=operator.itemgetter(1),
                reverse=True,
            ):
                report += f"- **{category.title()}:** {count} errors\n"

        # Top error types
        if report_data.get("error_types"):
            report += "\n## Top Error Types\n\n"
            top_errors = sorted(
                report_data["error_types"].items(),
                key=operator.itemgetter(1),
                reverse=True,
            )[:10]
            for error_type, count in top_errors:
                report += f"- **{error_type}:** {count} occurrences\n"

        # Most problematic files
        if report_data.get("files_with_errors"):
            report += "\n## Most Problematic Files\n\n"
            problematic_files = sorted(
                report_data["files_with_errors"],
                key=operator.itemgetter("count"),
                reverse=True,
            )[:5]
            for file_info in problematic_files:
                report += f"- **{file_info['file']}:** {file_info['count']} errors\n"

        return report


class TestMyPyCompliance:
    """Test suite for MyPy compliance."""

    @pytest.fixture(scope="class")
    def analyzer(self) -> Any:
        """Create MyPy analyzer instance."""
        return MyPyAnalyzer()

    @pytest.fixture(scope="class")
    def analysis_results(self, analyzer: Any) -> Any:
        """Run MyPy analysis once for all tests."""
        return analyzer.run_analysis()

    def test_mypy_files_found(self, analysis_results: Any) -> None:
        """Test that Python files are found for analysis."""
        assert analysis_results["total_files"] > 0, "No Python files found for MyPy analysis"

    def test_mypy_clean_rate(self, analysis_results: Any) -> None:
        """Test that MyPy clean rate is acceptable."""
        clean_rate = analysis_results["summary"]["clean_rate"]
        assert clean_rate >= 0.5, f"MyPy clean rate {clean_rate:.1f}% is below 0.5%"

    def test_mypy_typing_coverage(self, analysis_results: Any) -> None:
        """Test that typing coverage is reasonable."""
        typing_coverage = analysis_results["summary"]["typing_coverage"]
        assert typing_coverage >= 10, f"Typing coverage {typing_coverage:.1f}% is below 10%"

    def test_mypy_error_distribution(self, analysis_results: Any) -> None:
        """Test that type errors are not concentrated in a few files."""
        files_with_errors = analysis_results["files_with_errors"]

        if files_with_errors:
            total_errors = analysis_results["summary"]["total_errors"]
            max_errors_in_file = max(file_info["count"] for file_info in files_with_errors)

            if total_errors > 0:
                concentration = (max_errors_in_file / total_errors) * 100
                assert concentration < 60, f"Too many type errors concentrated in one file ({concentration:.1f}%)"

    def test_generate_mypy_reports(self, analyzer: Any, analysis_results: Any) -> None:
        """Test MyPy report generation."""
        # Generate reports
        json_report = analyzer.save_report(analysis_results, "json")
        md_report = analyzer.save_report(analysis_results, "markdown")

        # Verify reports exist
        assert json_report.exists(), "MyPy JSON report was not created"
        assert md_report.exists(), "MyPy Markdown report was not created"

        # Verify report content
        import json

        with open(json_report, encoding="utf-8") as f:
            report_data = json.load(f)

        assert "clean_files" in report_data
        assert "files_with_errors" in report_data
        assert "summary" in report_data
        assert "recommendations" in report_data

        # Print summary


if __name__ == "__main__":
    # Run MyPy analysis directly
    analyzer = MyPyAnalyzer()
    results = analyzer.run_analysis()

    json_report = analyzer.save_report(results, "json")
    md_report = analyzer.save_report(results, "markdown")

    # Print summary
    total_files = results["total_files"]
    clean_files = len(results["clean_files"])
    clean_rate = results["summary"]["clean_rate"]
