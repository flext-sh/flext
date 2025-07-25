"""PEP8 compliance tests for FLEXT workspace."""
import json
import operator
import subprocess
from typing import Any

import pytest

from .base import BaseQualityAnalyzer


class PEP8Analyzer(BaseQualityAnalyzer):
    """Analyzer for PEP8 compliance using ruff."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext") -> None:
        super().__init__(workspace_root, "pep8")

    def run_analysis(self) -> dict[str, Any]:
        """Run PEP8 analysis using ruff."""
        python_files = self.find_python_files()
        results = {
            "timestamp": self.timestamp,
            "workspace_root": str(self.workspace_root),
            "test_type": self.test_type,
            "total_files": len(python_files),
            "violations": [],
            "summary": {"errors": 0, "warnings": 0, "info": 0},
            "compliant_files": [],
            "non_compliant_files": [],
            "recommendations": [],
        }
        if not python_files:
            return results
        for file_path in python_files:
            try:
                cmd = ["ruff", "check", str(file_path), "--output-format=json"]
                result = subprocess.run(
                    cmd, check=False, capture_output=True, text=True,
                )
                if result.returncode == 0:
                    compliant_files = results["compliant_files"]
                    if isinstance(compliant_files, list):
                        compliant_files.append(str(file_path))
                else:
                    non_compliant_files = results["non_compliant_files"]
                    if isinstance(non_compliant_files, list):
                        non_compliant_files.append(str(file_path))
                    # Parse ruff output
                    try:
                        ruff_output = json.loads(result.stdout) if result.stdout else []
                        for violation in ruff_output:
                            violation_data = {
                                "file": str(file_path),
                                "line": violation.get("location", {}).get("row", 0),
                                "column": violation.get("location", {}).get(
                                    "column", 0,
                                ),
                                "rule": violation.get("code", ""),
                                "message": violation.get("message", ""),
                                "severity": self._get_severity(
                                    violation.get("code", ""),
                                ),
                            }
                            violations = results["violations"]
                            if isinstance(violations, list):
                                violations.append(violation_data)
                            # Count by severity
                            severity = violation_data["severity"]
                            summary = results["summary"]
                            if isinstance(summary, dict):
                                if severity in summary:
                                    summary[severity] += 1
                                else:
                                    summary[severity] = 1
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                violations = results["violations"]
                if isinstance(violations, list):
                    violations.append(
                        {
                            "file": str(file_path),
                            "error": f"Analysis failed: {e!s}",
                            "severity": "error",
                        },
                    )
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)
        return results

    def _get_severity(self, code: str) -> str:
        """Determine severity based on ruff code."""
        if not code:
            return "info"
        # Error codes (E)
        if code.startswith("E"):
            return "errors"
        # Warning codes (W)
        if code.startswith("W"):
            return "warnings"
        # All others are info
        return "info"

    def _generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate PEP8 recommendations."""
        recommendations = []
        total_errors = results["summary"].get("errors", 0)
        total_warnings = results["summary"].get("warnings", 0)
        total_files = results["total_files"]
        compliant_files = len(results["compliant_files"])
        if total_files > 0:
            compliance_rate = (compliant_files / total_files) * 100
            if compliance_rate < 70:
                recommendations.append(
                    "🚨 Critical: PEP8 compliance is below 70%. Run 'ruff check --fix' to auto-fix issues.",
                )
            elif compliance_rate < 90:
                recommendations.append(
                    "⚠️ Warning: PEP8 compliance could be improved. Consider running 'ruff check --fix'.",
                )
            else:
                recommendations.append("✅ Good: PEP8 compliance is satisfactory.")
        if total_errors > 0:
            recommendations.append(f"🔴 Fix {total_errors} PEP8 errors immediately.")
        if total_warnings > 0:
            recommendations.append(
                f"🟡 Address {total_warnings} PEP8 warnings when possible.",
            )
        # Top violation types
        violation_types: dict[str, int] = {}
        for violation in results["violations"]:
            rule = violation.get("rule", "unknown")
            violation_types[rule] = violation_types.get(rule, 0) + 1
        if violation_types:
            top_violations = sorted(
                violation_types.items(), key=operator.itemgetter(1), reverse=True,
            )[:3]
            recommendations.append(
                f"📊 Most common violations: {', '.join([f'{rule}({count})' for rule, count in top_violations])}",
            )
        return recommendations

    def generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate PEP8 markdown report."""
        total_files = report_data.get("total_files", 0)
        compliant_files = len(report_data.get("compliant_files", []))
        compliance_rate = (
            (compliant_files / total_files * 100) if total_files > 0 else 0
        )
        report = f"""# PEP8 Compliance Report - FLEXT Workspace
**Generated:** {report_data.get("timestamp", "Unknown")}
**Workspace:** {report_data.get("workspace_root", "Unknown")}
## Executive Summary
- **Total Files Analyzed:** {total_files}
- **Compliant Files:** {compliant_files}
- **Non-compliant Files:** {len(report_data.get("non_compliant_files", []))}
- **Compliance Rate:** {compliance_rate:.1f}%
- **Total Violations:** {len(report_data.get("violations", []))}
- **Errors:** {report_data.get("summary", {}).get("errors", 0)}
- **Warnings:** {report_data.get("summary", {}).get("warnings", 0)}
## Recommendations
"""
        for recommendation in report_data.get("recommendations", []):
            report += f"- {recommendation}\n"
        # Top violations
        violation_types: dict[str, int] = {}
        for violation in report_data.get("violations", []):
            rule = violation.get("rule", "unknown")
            violation_types[rule] = violation_types.get(rule, 0) + 1
        if violation_types:
            report += "\n## Top Violation Types\n\n"
            top_violations = sorted(
                violation_types.items(), key=operator.itemgetter(1), reverse=True,
            )[:10]
            for rule, count in top_violations:
                report += f"- **{rule}:** {count} occurrences\n"
        # Non-compliant files
        if report_data.get("non_compliant_files"):
            report += "\n## Non-compliant Files\n\n"
            for file_path in report_data.get("non_compliant_files", []):
                file_violations = [
                    v
                    for v in report_data.get("violations", [])
                    if v.get("file") == file_path
                ]
                report += f"- **{file_path}:** {len(file_violations)} violations\n"
        return report


class TestPEP8Compliance:
    """Test suite for PEP8 compliance."""

    @pytest.fixture(scope="class")
    def analyzer(self) -> object:
        """Create PEP8 analyzer instance."""
        return PEP8Analyzer()

    @pytest.fixture(scope="class")
    def analysis_results(self, analyzer: Any) -> dict[str, Any]:
        """Run PEP8 analysis once for all tests."""
        return analyzer.run_analysis()

    def test_pep8_files_found(self, analysis_results: dict[str, Any]) -> None:
        """Test that Python files are found for analysis."""
        assert analysis_results["total_files"] > 0, (
            "No Python files found for PEP8 analysis"
        )

    def test_pep8_compliance_rate(self, analysis_results: dict[str, Any]) -> None:
        """Test PEP8 compliance rate is acceptable."""
        total_files = analysis_results["total_files"]
        compliant_files = len(analysis_results["compliant_files"])
        if total_files > 0:
            compliance_rate = (compliant_files / total_files) * 100
            assert compliance_rate >= 60, (
                f"PEP8 compliance rate {compliance_rate:.1f}% is below 60%"
            )

    def test_pep8_has_compliant_files(self, analysis_results: dict[str, Any]) -> None:
        """Test that there are some PEP8 compliant files."""
        assert len(analysis_results["compliant_files"]) > 0, (
            "No PEP8 compliant files found"
        )

    def test_pep8_error_threshold(self, analysis_results: dict[str, Any]) -> None:
        """Test that PEP8 errors are within acceptable limits."""
        total_errors = analysis_results["summary"].get("errors", 0)
        total_files = analysis_results["total_files"]
        if total_files > 0:
            error_rate = total_errors / total_files
            assert error_rate < 5.0, (
                f"PEP8 error rate {error_rate:.1f} per file is too high"
            )

    def test_generate_pep8_reports(self, analyzer: Any, analysis_results: dict[str, Any]) -> None:
        """Test PEP8 report generation."""
        # Generate reports
        json_report = analyzer.save_report(analysis_results, "json")
        md_report = analyzer.save_report(analysis_results, "markdown")
        # Verify reports exist
        assert json_report.exists(), "PEP8 JSON report was not created"
        assert md_report.exists(), "PEP8 Markdown report was not created"
        # Verify report content
        with open(json_report, encoding="utf-8") as f:
            report_data = json.load(f)
        assert "violations" in report_data
        assert "summary" in report_data
        assert "recommendations" in report_data
        # Print summary
        total_files = analysis_results["total_files"]
        compliant_files = len(analysis_results["compliant_files"])
        (compliant_files / total_files * 100) if total_files > 0 else 0


if __name__ == "__main__":
    # Run PEP8 analysis directly
    analyzer = PEP8Analyzer()
    results = analyzer.run_analysis()
    json_report = analyzer.save_report(results, "json")
    md_report = analyzer.save_report(results, "markdown")
    # Print summary
    total_files = results["total_files"]
    compliant_files = len(results["compliant_files"])
    compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
