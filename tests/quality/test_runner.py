"""Test runner for all quality tests - generates consolidated report."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest

from .test_dry import DRYAnalyzer
from .test_kiss import KISSAnalyzer
from .test_lint import LintAnalyzer
from .test_mypy import MyPyAnalyzer
from .test_pep8 import PEP8Analyzer
from .test_solid import SOLIDAnalyzer

# Report will be saved to a non-tracked location
REPORT_DIR = Path("/tmp/flext_quality_reports")
REPORT_DIR.mkdir(exist_ok=True)


class QualityTestRunner:
    """Runner for all quality tests with consolidated reporting."""

    def __init__(self, workspace_root: str = "/home/marlonsc/flext") -> None:
        self.workspace_root = workspace_root
        self.timestamp = datetime.now().isoformat()
        self.analyzers = {
            "pep8": PEP8Analyzer(workspace_root),
            "dry": DRYAnalyzer(workspace_root),
            "lint": LintAnalyzer(workspace_root),
            "mypy": MyPyAnalyzer(workspace_root),
            "solid": SOLIDAnalyzer(workspace_root),
            "kiss": KISSAnalyzer(workspace_root),
        }

    def run_all_tests(self) -> dict[str, Any]:
        """Run all quality tests and generate consolidated report."""
        consolidated_results = {
            "timestamp": self.timestamp,
            "workspace_root": self.workspace_root,
            "test_results": {},
            "overall_summary": {},
            "consolidated_recommendations": [],
            "quality_score": 0,
        }

        # Run all analyzers
        for test_name, analyzer in self.analyzers.items():
            try:
                results = analyzer.run_analysis()
                test_results = consolidated_results["test_results"]
                if isinstance(test_results, dict):
                    test_results[test_name] = results

                # Save individual report
                analyzer.save_report(results, "json")
                analyzer.save_report(results, "markdown")

            except Exception as e:
                test_results = consolidated_results["test_results"]
                if isinstance(test_results, dict):
                    test_results[test_name] = {
                        "error": str(e),
                        "timestamp": self.timestamp,
                    }

        # Generate consolidated summary
        test_results = consolidated_results["test_results"]
        if isinstance(test_results, dict):
            consolidated_results["overall_summary"] = self._generate_overall_summary(
                test_results
            )

            # Generate consolidated recommendations
            consolidated_results["consolidated_recommendations"] = (
                self._generate_consolidated_recommendations(test_results)
            )

            # Calculate overall quality score
            consolidated_results["quality_score"] = self._calculate_quality_score(
                test_results
            )

        return consolidated_results

    def _generate_overall_summary(self, test_results: dict[str, Any]) -> dict[str, Any]:
        """Generate overall summary from all test results."""
        summary = {
            "total_files_analyzed": 0,
            "total_issues": 0,
            "tests_completed": 0,
            "tests_failed": 0,
            "compliance_rates": {},
            "top_issues": [],
            "quality_metrics": {},
        }

        for test_name, results in test_results.items():
            if "error" in results:
                summary["tests_failed"] += 1
                continue

            summary["tests_completed"] += 1

            # Get file count (use maximum to avoid double counting)
            file_count = results.get("total_files", 0)
            total_files_analyzed = summary["total_files_analyzed"]
            if isinstance(total_files_analyzed, int):
                summary["total_files_analyzed"] = max(total_files_analyzed, file_count)

            # Extract compliance rates and metrics
            if test_name == "pep8":
                total_files = results.get("total_files", 0)
                compliant_files = len(results.get("compliant_files", []))
                if total_files > 0:
                    compliance_rates = summary["compliance_rates"]
                    if isinstance(compliance_rates, dict):
                        compliance_rates["pep8"] = (compliant_files / total_files) * 100

                total_issues = summary["total_issues"]
                if isinstance(total_issues, int):
                    summary["total_issues"] = total_issues + len(
                        results.get("violations", [])
                    )

                quality_metrics = summary["quality_metrics"]
                if isinstance(quality_metrics, dict):
                    quality_metrics["pep8_violations"] = len(
                        results.get("violations", [])
                    )

            elif test_name == "dry":
                compliance_rates = summary["compliance_rates"]
                if isinstance(compliance_rates, dict):
                    compliance_rates["dry"] = 100 - results.get("summary", {}).get(
                        "similarity_score", 0
                    )

                total_issues = summary["total_issues"]
                if isinstance(total_issues, int):
                    summary["total_issues"] = total_issues + results.get(
                        "summary", {}
                    ).get("total_duplicates", 0)

                quality_metrics = summary["quality_metrics"]
                if isinstance(quality_metrics, dict):
                    quality_metrics["dry_duplicates"] = results.get("summary", {}).get(
                        "total_duplicates", 0
                    )

            elif test_name == "lint":
                compliance_rates = summary["compliance_rates"]
                if isinstance(compliance_rates, dict):
                    compliance_rates["lint"] = results.get("summary", {}).get(
                        "clean_rate", 0
                    )

                total_issues = summary["total_issues"]
                if isinstance(total_issues, int):
                    summary["total_issues"] = total_issues + results.get(
                        "summary", {}
                    ).get("total_issues", 0)

                quality_metrics = summary["quality_metrics"]
                if isinstance(quality_metrics, dict):
                    quality_metrics["lint_issues"] = results.get("summary", {}).get(
                        "total_issues", 0
                    )

            elif test_name == "mypy":
                compliance_rates = summary["compliance_rates"]
                if isinstance(compliance_rates, dict):
                    compliance_rates["mypy"] = results.get("summary", {}).get(
                        "clean_rate", 0
                    )

                total_issues = summary["total_issues"]
                if isinstance(total_issues, int):
                    summary["total_issues"] = total_issues + results.get(
                        "summary", {}
                    ).get("total_errors", 0)

                quality_metrics = summary["quality_metrics"]
                if isinstance(quality_metrics, dict):
                    quality_metrics["mypy_errors"] = results.get("summary", {}).get(
                        "total_errors", 0
                    )
                    quality_metrics["typing_coverage"] = results.get("summary", {}).get(
                        "typing_coverage", 0
                    )

            elif test_name == "solid":
                compliance_rates = summary["compliance_rates"]
                if isinstance(compliance_rates, dict):
                    compliance_rates["solid"] = results.get("summary", {}).get(
                        "average_score", 0
                    )

                total_issues = summary["total_issues"]
                if isinstance(total_issues, int):
                    summary["total_issues"] = total_issues + results.get(
                        "summary", {}
                    ).get("total_violations", 0)

                quality_metrics = summary["quality_metrics"]
                if isinstance(quality_metrics, dict):
                    quality_metrics["solid_violations"] = results.get(
                        "summary", {}
                    ).get("total_violations", 0)

            elif test_name == "kiss":
                compliance_rates = summary["compliance_rates"]
                if isinstance(compliance_rates, dict):
                    compliance_rates["kiss"] = results.get("summary", {}).get(
                        "simplicity_score", 0
                    )

                total_issues = summary["total_issues"]
                if isinstance(total_issues, int):
                    summary["total_issues"] = total_issues + results.get(
                        "summary", {}
                    ).get("total_issues", 0)

                quality_metrics = summary["quality_metrics"]
                if isinstance(quality_metrics, dict):
                    quality_metrics["kiss_issues"] = results.get("summary", {}).get(
                        "total_issues", 0
                    )
                    quality_metrics["average_complexity"] = results.get(
                        "summary", {}
                    ).get("average_complexity", 0)

        return summary

    def _generate_consolidated_recommendations(
        self, test_results: dict[str, Any]
    ) -> list[str]:
        """Generate consolidated recommendations from all tests."""
        recommendations = []

        # Priority recommendations based on critical issues
        critical_issues = []

        for test_name, results in test_results.items():
            if "error" in results:
                continue

            test_recommendations = results.get("recommendations", [])

            # Add test-specific recommendations
            for rec in test_recommendations:
                if "🚨" in rec or "Critical" in rec:
                    critical_issues.append(f"[{test_name.upper()}] {rec}")
                else:
                    recommendations.append(f"[{test_name.upper()}] {rec}")

        # Put critical issues first
        final_recommendations = critical_issues + recommendations

        # Add overall recommendations
        overall_summary = self._generate_overall_summary(test_results)

        if overall_summary["tests_failed"] > 0:
            final_recommendations.insert(
                0,
                f"🔧 {overall_summary['tests_failed']} quality tests failed - check tool availability",
            )

        total_issues = overall_summary["total_issues"]
        if total_issues > 100:
            final_recommendations.insert(
                0, f"🚨 Critical: {total_issues} total issues found across all tests"
            )
        elif total_issues > 50:
            final_recommendations.insert(
                0, f"⚠️ Warning: {total_issues} issues found - prioritize fixes"
            )

        # Compliance-based recommendations
        compliance_rates = overall_summary["compliance_rates"]
        low_compliance = [test for test, rate in compliance_rates.items() if rate < 60]

        if low_compliance:
            final_recommendations.insert(
                0,
                f"📊 Low compliance in: {', '.join(low_compliance)} - requires immediate attention",
            )

        return final_recommendations[:20]  # Limit to top 20 recommendations

    def _calculate_quality_score(self, test_results: dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)."""
        weights = {
            "pep8": 15,  # Style compliance
            "dry": 20,  # Code duplication
            "lint": 20,  # General linting
            "mypy": 15,  # Type checking
            "solid": 15,  # Architecture
            "kiss": 15,  # Simplicity
        }

        total_weight = 0
        weighted_score = 0

        for test_name, results in test_results.items():
            if "error" in results:
                continue

            weight = weights.get(test_name, 10)
            total_weight += weight

            # Calculate individual test score
            if test_name == "pep8":
                total_files = results.get("total_files", 0)
                compliant_files = len(results.get("compliant_files", []))
                score = (compliant_files / total_files * 100) if total_files > 0 else 0

            elif test_name == "dry":
                # Invert similarity score (lower is better)
                similarity_score = results.get("summary", {}).get("similarity_score", 0)
                score = max(0, 100 - similarity_score)

            elif test_name in {"lint", "mypy"}:
                score = results.get("summary", {}).get("clean_rate", 0)

            elif test_name == "solid":
                score = results.get("summary", {}).get("average_score", 0)

            elif test_name == "kiss":
                score = results.get("summary", {}).get("simplicity_score", 0)

            else:
                score = 50  # Default

            weighted_score += score * weight

        if total_weight > 0:
            return weighted_score / total_weight

        return 0

    def save_consolidated_report(
        self, consolidated_results: dict[str, Any], format: str = "json"
    ) -> Path:
        """Save consolidated report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            report_file = REPORT_DIR / f"flext_quality_consolidated_{timestamp}.json"
            with open(report_file, "w") as f:
                json.dump(consolidated_results, f, indent=2, default=str)

        elif format == "markdown":
            report_file = REPORT_DIR / f"flext_quality_consolidated_{timestamp}.md"
            with open(report_file, "w") as f:
                f.write(self._generate_consolidated_markdown(consolidated_results))

        return report_file

    def _generate_consolidated_markdown(self, results: dict[str, Any]) -> str:
        """Generate consolidated markdown report."""
        overall_summary = results.get("overall_summary", {})
        quality_score = results.get("quality_score", 0)

        # Determine quality grade
        if quality_score >= 90:
            grade = "A (Excellent)"
        elif quality_score >= 80:
            grade = "B (Good)"
        elif quality_score >= 70:
            grade = "C (Acceptable)"
        elif quality_score >= 60:
            grade = "D (Needs Work)"
        else:
            grade = "F (Critical)"

        report = f"""# FLEXT Workspace - Comprehensive Quality Report

**Generated:** {results.get("timestamp", "Unknown")}
**Workspace:** {results.get("workspace_root", "Unknown")}

## Executive Summary

- **Overall Quality Score:** {quality_score:.1f}/100 ({grade})
- **Total Files Analyzed:** {overall_summary.get("total_files_analyzed", 0)}
- **Total Issues Found:** {overall_summary.get("total_issues", 0)}
- **Tests Completed:** {overall_summary.get("tests_completed", 0)}/6
- **Tests Failed:** {overall_summary.get("tests_failed", 0)}/6

## Compliance Rates

"""

        compliance_rates = overall_summary.get("compliance_rates", {})
        for test_name, rate in compliance_rates.items():
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            report += f"- **{test_name.upper()}:** {rate:.1f}% {status}\n"

        report += "\n## Key Metrics\n\n"

        quality_metrics = overall_summary.get("quality_metrics", {})
        for metric, value in quality_metrics.items():
            report += f"- **{metric.replace('_', ' ').title()}:** {value}\n"

        report += "\n## Priority Recommendations\n\n"

        for i, recommendation in enumerate(
            results.get("consolidated_recommendations", [])[:10], 1
        ):
            report += f"{i}. {recommendation}\n"

        # Individual test summaries
        report += "\n## Individual Test Results\n\n"

        test_results = results.get("test_results", {})
        for test_name, test_data in test_results.items():
            if "error" in test_data:
                report += f"### {test_name.upper()} - ❌ FAILED\n\n"
                report += f"**Error:** {test_data['error']}\n\n"
            else:
                report += f"### {test_name.upper()} - ✅ COMPLETED\n\n"

                # Test-specific summary
                if test_name == "pep8":
                    total_files = test_data.get("total_files", 0)
                    compliant_files = len(test_data.get("compliant_files", []))
                    violations = len(test_data.get("violations", []))
                    report += f"- **Files:** {total_files}\n"
                    report += f"- **Compliant:** {compliant_files}\n"
                    report += f"- **Violations:** {violations}\n"

                elif test_name == "dry":
                    duplicates = test_data.get("summary", {}).get("total_duplicates", 0)
                    similarity = test_data.get("summary", {}).get("similarity_score", 0)
                    report += f"- **Duplicates:** {duplicates}\n"
                    report += f"- **Similarity Score:** {similarity:.1f}\n"

                elif test_name == "lint":
                    clean_rate = test_data.get("summary", {}).get("clean_rate", 0)
                    total_issues = test_data.get("summary", {}).get("total_issues", 0)
                    report += f"- **Clean Rate:** {clean_rate:.1f}%\n"
                    report += f"- **Total Issues:** {total_issues}\n"

                elif test_name == "mypy":
                    clean_rate = test_data.get("summary", {}).get("clean_rate", 0)
                    total_errors = test_data.get("summary", {}).get("total_errors", 0)
                    typing_coverage = test_data.get("summary", {}).get(
                        "typing_coverage", 0
                    )
                    report += f"- **Clean Rate:** {clean_rate:.1f}%\n"
                    report += f"- **Type Errors:** {total_errors}\n"
                    report += f"- **Typing Coverage:** {typing_coverage:.1f}%\n"

                elif test_name == "solid":
                    avg_score = test_data.get("summary", {}).get("average_score", 0)
                    violations = test_data.get("summary", {}).get("total_violations", 0)
                    report += f"- **Average Score:** {avg_score:.1f}/100\n"
                    report += f"- **Violations:** {violations}\n"

                elif test_name == "kiss":
                    simplicity_score = test_data.get("summary", {}).get(
                        "simplicity_score", 0
                    )
                    total_issues = test_data.get("summary", {}).get("total_issues", 0)
                    avg_complexity = test_data.get("summary", {}).get(
                        "average_complexity", 0
                    )
                    report += f"- **Simplicity Score:** {simplicity_score:.1f}/100\n"
                    report += f"- **Issues:** {total_issues}\n"
                    report += f"- **Avg Complexity:** {avg_complexity:.1f}\n"

                report += "\n"

        return report


class TestQualityRunner:
    """Test suite for quality test runner."""

    @pytest.fixture(scope="class")
    def runner(self):
        """Create quality test runner instance."""
        return QualityTestRunner()

    @pytest.fixture(scope="class")
    def consolidated_results(self, runner):
        """Run all quality tests once."""
        return runner.run_all_tests()

    def test_quality_tests_execution(self, consolidated_results) -> None:
        """Test that quality tests executed successfully."""
        assert "test_results" in consolidated_results
        assert "overall_summary" in consolidated_results
        assert "quality_score" in consolidated_results

        # At least some tests should complete
        completed_tests = consolidated_results["overall_summary"]["tests_completed"]
        assert completed_tests > 0, "No quality tests completed successfully"

    def test_quality_score_reasonable(self, consolidated_results) -> None:
        """Test that overall quality score is reasonable."""
        quality_score = consolidated_results["quality_score"]
        assert 0 <= quality_score <= 100, (
            f"Quality score {quality_score} is out of range"
        )

        # Should have some baseline quality
        assert quality_score >= 20, f"Quality score {quality_score} is critically low"

    def test_generate_consolidated_reports(self, runner, consolidated_results) -> None:
        """Test consolidated report generation."""
        # Generate reports
        json_report = runner.save_consolidated_report(consolidated_results, "json")
        md_report = runner.save_consolidated_report(consolidated_results, "markdown")

        # Verify reports exist
        assert json_report.exists(), "Consolidated JSON report was not created"
        assert md_report.exists(), "Consolidated Markdown report was not created"

        # Verify report content
        with open(json_report) as f:
            report_data = json.load(f)

        assert "test_results" in report_data
        assert "overall_summary" in report_data
        assert "consolidated_recommendations" in report_data
        assert "quality_score" in report_data

        # Print executive summary
        overall_summary = consolidated_results["overall_summary"]
        consolidated_results["quality_score"]

        # Print compliance rates
        for _test_name, _rate in overall_summary.get("compliance_rates", {}).items():
            pass


if __name__ == "__main__":
    # Run all quality tests
    runner = QualityTestRunner()
    results = runner.run_all_tests()

    # Generate consolidated reports
    json_report = runner.save_consolidated_report(results, "json")
    md_report = runner.save_consolidated_report(results, "markdown")

    # Print executive summary
    overall_summary = results["overall_summary"]
    quality_score = results["quality_score"]

    grade = (
        "A"
        if quality_score >= 90
        else "B"
        if quality_score >= 80
        else "C"
        if quality_score >= 70
        else "D"
        if quality_score >= 60
        else "F"
    )

    for rate in overall_summary.get("compliance_rates", {}).values():
        status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"

    for _i, _rec in enumerate(results.get("consolidated_recommendations", [])[:5], 1):
        pass
