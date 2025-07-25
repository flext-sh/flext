"""Lint compliance tests using ruff for FLEXT workspace."""

import json
import operator
import subprocess
from collections import defaultdict
from typing import Any

import pytest

from .base import BaseQualityAnalyzer


class LintAnalyzer(BaseQualityAnalyzer):
    """Analyzer for lint compliance using ruff."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext") -> None:
        super().__init__(workspace_root, "lint")

    def run_analysis(self) -> dict[str, Any]:
        """Run lint analysis using ruff."""
        python_files = self.find_python_files()

        # Use explicit typing for defaultdict fields
        issue_categories: defaultdict[str, int] = defaultdict(int)
        rule_violations: defaultdict[str, int] = defaultdict(int)
        severity_counts: defaultdict[str, int] = defaultdict(int)

        results = {
            "timestamp": self.timestamp,
            "workspace_root": str(self.workspace_root),
            "test_type": self.test_type,
            "total_files": len(python_files),
            "clean_files": [],
            "files_with_issues": [],
            "issue_categories": issue_categories,
            "rule_violations": rule_violations,
            "severity_counts": severity_counts,
            "summary": {
                "total_issues": 0,
                "clean_rate": 0,
                "most_common_rule": "",
                "most_problematic_file": "",
            },
            "recommendations": [],
        }

        if not python_files:
            return results

        max_issues_file = ""
        max_issues_count = 0

        for file_path in python_files:
            try:
                cmd = ["ruff", "check", str(file_path), "--output-format=json"]
                result = subprocess.run(
                    cmd, check=False, capture_output=True, text=True,
                )

                if result.returncode == 0:
                    clean_files = results["clean_files"]
                    if isinstance(clean_files, list):
                        clean_files.append(str(file_path))
                else:
                    file_issues = []
                    try:
                        ruff_output = json.loads(result.stdout) if result.stdout else []
                        for issue in ruff_output:
                            rule_code = issue.get("code", "")
                            severity = self._determine_severity(rule_code)

                            issue_data = {
                                "line": issue.get("location", {}).get("row", 0),
                                "column": issue.get("location", {}).get("column", 0),
                                "rule": rule_code,
                                "message": issue.get("message", ""),
                                "severity": severity,
                                "category": self._get_category(rule_code),
                            }
                            file_issues.append(issue_data)

                            # Update counters
                            rule_violations[rule_code] += 1
                            issue_categories[issue_data["category"]] += 1
                            severity_counts[severity] += 1
                            summary_dict = results["summary"]
                            if isinstance(summary_dict, dict):
                                summary_dict["total_issues"] += 1

                    except json.JSONDecodeError:
                        # Fallback parsing if JSON fails
                        if result.stdout:
                            lines = result.stdout.strip().split("\n")
                            for line in lines:
                                if ":" in line and any(
                                    code in line for code in ["E", "W", "F", "C", "N"]
                                ):
                                    file_issues.append(
                                        {
                                            "line": 0,
                                            "column": 0,
                                            "rule": "PARSE_ERROR",
                                            "message": line.strip(),
                                            "severity": "error",
                                            "category": "parsing",
                                        },
                                    )
                                    summary = results["summary"]
                                    if isinstance(summary, dict):
                                        summary["total_issues"] += 1

                    if file_issues:
                        files_with_issues = results["files_with_issues"]
                        if isinstance(files_with_issues, list):
                            files_with_issues.append(
                                {
                                    "file": str(file_path),
                                    "issues": file_issues,
                                    "count": len(file_issues),
                                },
                            )

                        # Track most problematic file
                        if len(file_issues) > max_issues_count:
                            max_issues_count = len(file_issues)
                            max_issues_file = str(file_path)

            except Exception as e:
                # Expected error handling
                # Record analysis failure
                files_with_issues = results["files_with_issues"]
                if isinstance(files_with_issues, list):
                    files_with_issues.append(
                        {
                            "file": str(file_path),
                            "issues": [
                                {
                                    "line": 0,
                                    "column": 0,
                                    "rule": "ANALYSIS_ERROR",
                                    "message": f"Analysis failed: {e!s}",
                                    "severity": "error",
                                    "category": "system",
                                },
                            ],
                            "count": 1,
                        },
                    )
                summary_dict = results["summary"]
                if isinstance(summary_dict, dict):
                    summary_dict["total_issues"] += 1

        # Calculate summary statistics
        total_files = results["total_files"]
        clean_files = results["clean_files"]
        summary_dict = results["summary"]
        if isinstance(total_files, int) and total_files > 0 and isinstance(clean_files, list) and isinstance(summary_dict, dict):
            summary_dict["clean_rate"] = (len(clean_files) / total_files) * 100

        # Find most common rule violation
        if rule_violations and isinstance(summary_dict, dict):
            most_common_rule = max(
                rule_violations.items(), key=operator.itemgetter(1),
            )
            summary_dict["most_common_rule"] = (
                f"{most_common_rule[0]} ({most_common_rule[1]} times)"
            )

        if isinstance(summary_dict, dict):
            summary_dict["most_problematic_file"] = max_issues_file

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def _determine_severity(self, rule_code: str) -> str:
        """Determine severity based on rule code."""
        if not rule_code:
            return "info"

        # Error codes
        if rule_code.startswith(("E", "F")):
            return "error"
        # Warning codes
        if rule_code.startswith(("W", "C")):
            return "warning"
        # Style/convention codes
        if rule_code.startswith(("N", "D")):
            return "style"
        return "info"

    def _get_category(self, rule_code: str) -> str:
        """Get category based on rule code."""
        if not rule_code:
            return "unknown"

        # Map rule prefixes to categories
        category_map = {
            "E": "errors",
            "W": "warnings",
            "F": "pyflakes",
            "C": "complexity",
            "N": "naming",
            "D": "docstring",
            "S": "security",
            "B": "bugbear",
            "A": "builtins",
            "I": "imports",
            "UP": "upgrades",
            "YTT": "typing",
            "ANN": "annotations",
            "BLE": "blind-except",
            "FBT": "boolean-trap",
            "COM": "commas",
            "DTZ": "datetime",
            "EM": "error-msg",
            "EXE": "executable",
            "ICN": "import-conventions",
            "INP": "implicit-namespace",
            "PIE": "pie",
            "PYI": "pyi",
            "PT": "pytest",
            "Q": "quotes",
            "RSE": "raise",
            "RET": "return",
            "SIM": "simplify",
            "TCH": "type-checking",
            "ARG": "unused-arguments",
            "PTH": "pathlib",
            "ERA": "eradicate",
            "PD": "pandas",
            "PGH": "pygrep",
            "PL": "pylint",
            "TRY": "tryceratops",
            "FLY": "flynt",
            "NPY": "numpy",
            "RUF": "ruff",
        }

        for prefix, category in category_map.items():
            if rule_code.startswith(prefix):
                return category

        return "other"

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate lint recommendations."""
        recommendations = []

        total_issues = results["summary"]["total_issues"]
        clean_rate = results["summary"]["clean_rate"]
        results["total_files"]

        # Overall assessment
        if clean_rate >= 90:
            recommendations.append("✅ Excellent: High lint compliance rate!")
        elif clean_rate >= 70:
            recommendations.append(
                "👍 Good: Decent lint compliance, but room for improvement.",
            )
        elif clean_rate >= 50:
            recommendations.append("⚠️ Warning: Lint compliance needs attention.")
        else:
            recommendations.append(
                "🚨 Critical: Poor lint compliance requires immediate action.",
            )

        # Auto-fix suggestion
        if total_issues > 0:
            recommendations.append(
                "🔧 Run 'ruff check --fix' to automatically fix many issues.",
            )

        # Rule-specific recommendations
        if results["rule_violations"]:
            top_rules = sorted(
                results["rule_violations"].items(), key=operator.itemgetter(1), reverse=True,
            )[:3]
            rule_list = ", ".join([f"{rule}({count})" for rule, count in top_rules])
            recommendations.append(f"📊 Most common violations: {rule_list}")

        # Severity-based recommendations
        error_count = results["severity_counts"].get("error", 0)
        warning_count = results["severity_counts"].get("warning", 0)

        if error_count > 0:
            recommendations.append(
                f"🔴 Fix {error_count} error-level issues immediately.",
            )

        if warning_count > 0:
            recommendations.append(
                f"🟡 Address {warning_count} warning-level issues when possible.",
            )

        # File-specific recommendations
        if results["summary"]["most_problematic_file"]:
            recommendations.append(
                f"🎯 Focus on: {results['summary']['most_problematic_file']} (most issues)",
            )

        # Category-specific recommendations
        if results["issue_categories"]:
            top_categories = sorted(
                results["issue_categories"].items(), key=operator.itemgetter(1), reverse=True,
            )[:2]
            for category, count in top_categories:
                if count > 10:
                    recommendations.append(
                        f"📈 High {category} violations ({count}) - review coding standards.",
                    )

        return recommendations

    def generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate lint markdown report."""
        total_files = report_data.get("total_files", 0)
        clean_files = len(report_data.get("clean_files", []))
        clean_rate = report_data.get("summary", {}).get("clean_rate", 0)
        total_issues = report_data.get("summary", {}).get("total_issues", 0)

        report = f"""# Lint Compliance Report - FLEXT Workspace

**Generated:** {report_data.get("timestamp", "Unknown")}
**Workspace:** {report_data.get("workspace_root", "Unknown")}

## Executive Summary

- **Total Files Analyzed:** {total_files}
- **Clean Files:** {clean_files}
- **Files with Issues:** {len(report_data.get("files_with_issues", []))}
- **Clean Rate:** {clean_rate:.1f}%
- **Total Issues:** {total_issues}
- **Most Common Rule:** {report_data.get("summary", {}).get("most_common_rule", "N/A")}

## Severity Breakdown

"""

        severity_counts = report_data.get("severity_counts", {})
        for severity, count in sorted(
            severity_counts.items(), key=operator.itemgetter(1), reverse=True,
        ):
            report += f"- **{severity.title()}:** {count}\n"

        report += "\n## Recommendations\n\n"

        for recommendation in report_data.get("recommendations", []):
            report += f"- {recommendation}\n"

        # Top rule violations
        if report_data.get("rule_violations"):
            report += "\n## Top Rule Violations\n\n"
            top_rules = sorted(
                report_data["rule_violations"].items(), key=operator.itemgetter(1), reverse=True,
            )[:10]
            for rule, count in top_rules:
                report += f"- **{rule}:** {count} occurrences\n"

        # Issue categories
        if report_data.get("issue_categories"):
            report += "\n## Issue Categories\n\n"
            for category, count in sorted(
                report_data["issue_categories"].items(),
                key=operator.itemgetter(1),
                reverse=True,
            ):
                report += f"- **{category.title()}:** {count} issues\n"

        # Most problematic files
        if report_data.get("files_with_issues"):
            report += "\n## Most Problematic Files\n\n"
            problematic_files = sorted(
                report_data["files_with_issues"], key=operator.itemgetter("count"), reverse=True,
            )[:5]
            for file_info in problematic_files:
                report += f"- **{file_info['file']}:** {file_info['count']} issues\n"

        return report


class TestLintCompliance:
    """Test suite for lint compliance."""

    @pytest.fixture(scope="class")
    def analyzer(self) -> LintAnalyzer:
        """Create lint analyzer instance."""
        return LintAnalyzer()

    @pytest.fixture(scope="class")
    def analysis_results(self, analyzer: LintAnalyzer) -> dict[str, Any]:
        """Run lint analysis once for all tests."""
        return analyzer.run_analysis()

    def test_lint_files_found(self, analysis_results: dict[str, Any]) -> None:
        """Test that Python files are found for analysis."""
        assert analysis_results["total_files"] > 0, (
            "No Python files found for lint analysis"
        )

    def test_lint_clean_rate(self, analysis_results: dict[str, Any]) -> None:
        """Test that lint clean rate is acceptable."""
        clean_rate = analysis_results["summary"]["clean_rate"]
        assert clean_rate >= 50, f"Lint clean rate {clean_rate:.1f}% is below 50%"

    def test_lint_has_clean_files(self, analysis_results: dict[str, Any]) -> None:
        """Test that there are some lint-clean files."""
        assert len(analysis_results["clean_files"]) > 0, "No lint-clean files found"

    def test_lint_error_threshold(self, analysis_results: dict[str, Any]) -> None:
        """Test that lint errors are within acceptable limits."""
        error_count = analysis_results["severity_counts"].get("error", 0)
        total_files = analysis_results["total_files"]

        if total_files > 0:
            error_rate = error_count / total_files
            assert error_rate < 10.0, (
                f"Lint error rate {error_rate:.1f} per file is too high"
            )

    def test_lint_issue_distribution(self, analysis_results: dict[str, Any]) -> None:
        """Test that lint issues are not concentrated in a few files."""
        files_with_issues = analysis_results["files_with_issues"]

        if files_with_issues:
            # Check that no single file has more than 50% of total issues
            total_issues = analysis_results["summary"]["total_issues"]
            max_issues_in_file = max(
                file_info["count"] for file_info in files_with_issues
            )

            if total_issues > 0:
                concentration = (max_issues_in_file / total_issues) * 100
                assert concentration < 50, (
                    f"Too many issues concentrated in one file ({concentration:.1f}%)"
                )

    def test_generate_lint_reports(self, analyzer: LintAnalyzer, analysis_results: dict[str, Any]) -> None:
        """Test lint report generation."""
        # Generate reports
        json_report = analyzer.save_report(analysis_results, "json")
        md_report = analyzer.save_report(analysis_results, "markdown")

        # Verify reports exist
        assert json_report.exists(), "Lint JSON report was not created"
        assert md_report.exists(), "Lint Markdown report was not created"

        # Verify report content
        with open(json_report, encoding="utf-8") as f:
            report_data = json.load(f)

        assert "clean_files" in report_data
        assert "files_with_issues" in report_data
        assert "summary" in report_data
        assert "recommendations" in report_data

        # Print summary


if __name__ == "__main__":
    # Run lint analysis directly
    analyzer = LintAnalyzer()
    results = analyzer.run_analysis()

    json_report = analyzer.save_report(results, "json")
    md_report = analyzer.save_report(results, "markdown")

    # Print summary
