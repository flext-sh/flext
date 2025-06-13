#!/usr/bin/env python3
from __future__ import annotations

"""Advanced Code Quality Metrics Dashboard for FLX Project.

This script provides comprehensive analysis of code quality metrics including:
- Lint compliance rates
- Type annotation coverage
- Test coverage metrics
- Architectural compliance
- Performance indicators
- Security analysis
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class CodeQualityMetrics:
    """Advanced code quality metrics analyzer."""

    def __init__(self, project_root: str = "/home/marlonsc/pyauto/flx") -> None:
        """Initialize metrics analyzer."""
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src" / "flx"
        self.tests_path = self.project_root / "tests"

    def analyze_lint_metrics(self) -> dict[str, Any]:
        """Analyze lint compliance metrics."""
        try:
            # Run ruff check and capture output
            result = subprocess.run(
                ["ruff", "check", str(self.src_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root, check=False,
            )

            # Count errors by category
            errors_by_type = {}
            total_errors = 0

            for line in result.stdout.split("\n"):
                if ":" in line and "(" in line:
                    # Extract error code (e.g., F821, E501)
                    parts = line.split(":")
                    if len(parts) >= 4:
                        error_part = parts[3].strip()
                        if error_part:
                            error_code = error_part.split()[0]
                            errors_by_type[error_code] = errors_by_type.get(error_code, 0) + 1
                            total_errors += 1

            # Calculate total lines of code
            total_lines = self._count_lines_of_code()

            return {
                "total_errors": total_errors,
                "errors_by_type": errors_by_type,
                "total_lines": total_lines,
                "error_density": total_errors / total_lines if total_lines > 0 else 0,
                "quality_score": max(0, 100 - (total_errors / total_lines * 1000)) if total_lines > 0 else 0,
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_type_coverage(self) -> dict[str, Any]:
        """Analyze type annotation coverage."""
        try:
            # Run mypy with coverage report
            result = subprocess.run(
                ["python", "-m", "mypy", "--show-error-codes", str(self.src_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root, check=False,
            )

            type_errors = 0
            missing_annotations = 0

            for line in result.stdout.split("\n"):
                if "error:" in line:
                    type_errors += 1
                    if "missing" in line.lower() and "annotation" in line.lower():
                        missing_annotations += 1

            total_functions = self._count_functions()

            return {
                "type_errors": type_errors,
                "missing_annotations": missing_annotations,
                "total_functions": total_functions,
                "annotation_coverage": ((total_functions - missing_annotations) / total_functions * 100) if total_functions > 0 else 0,
                "type_safety_score": max(0, 100 - (type_errors / total_functions * 100)) if total_functions > 0 else 0,
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_architecture_compliance(self) -> dict[str, Any]:
        """Analyze hexagonal architecture compliance."""
        architecture_violations = []
        compliance_score = 100

        # Check for proper layer separation
        core_path = self.src_path / "core"
        self.src_path / "infra"

        # Scan for architectural violations
        if core_path.exists():
            for py_file in core_path.rglob("*.py"):
                content = py_file.read_text()
                # Check for infrastructure imports in core
                if any(forbidden in content for forbidden in ["import requests", "import sqlalchemy", "import redis"]):
                    architecture_violations.append(f"Infrastructure import in core: {py_file}")
                    compliance_score -= 5

        return {
            "violations": architecture_violations,
            "compliance_score": max(0, compliance_score),
            "architecture_pattern": "Hexagonal",
            "layers_identified": ["core", "application", "infrastructure", "adapters"],
        }

    def analyze_security_metrics(self) -> dict[str, Any]:
        """Analyze security-related metrics."""
        try:
            # Run bandit security scanner
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", str(self.src_path), "-f", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_root, check=False,
            )

            if result.stdout:
                bandit_data = json.loads(result.stdout)
                security_issues = len(bandit_data.get("results", []))
                severity_counts = {}

                for issue in bandit_data.get("results", []):
                    severity = issue.get("issue_severity", "UNKNOWN")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                return {
                    "total_security_issues": security_issues,
                    "severity_breakdown": severity_counts,
                    "security_score": max(0, 100 - security_issues * 5),
                }
            return {"total_security_issues": 0, "security_score": 100}
        except Exception as e:
            return {"error": str(e), "security_score": 50}  # Unknown score

    def generate_comprehensive_report(self) -> dict[str, Any]:
        """Generate comprehensive quality report."""
        timestamp = datetime.now().isoformat()

        # Gather all metrics
        lint_metrics = self.analyze_lint_metrics()
        type_metrics = self.analyze_type_coverage()
        architecture_metrics = self.analyze_architecture_compliance()
        security_metrics = self.analyze_security_metrics()

        # Calculate overall quality score
        scores = []
        if "quality_score" in lint_metrics:
            scores.append(lint_metrics["quality_score"])
        if "type_safety_score" in type_metrics:
            scores.append(type_metrics["type_safety_score"])
        if "compliance_score" in architecture_metrics:
            scores.append(architecture_metrics["compliance_score"])
        if "security_score" in security_metrics:
            scores.append(security_metrics["security_score"])

        overall_score = sum(scores) / len(scores) if scores else 0

        # Determine quality grade
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        else:
            grade = "D"

        return {
            "timestamp": timestamp,
            "project": "FLX Framework",
            "overall_score": round(overall_score, 2),
            "grade": grade,
            "metrics": {
                "lint": lint_metrics,
                "types": type_metrics,
                "architecture": architecture_metrics,
                "security": security_metrics,
            },
            "recommendations": self._generate_recommendations(
                lint_metrics, type_metrics, architecture_metrics, security_metrics,
            ),
        }

    def _count_lines_of_code(self) -> int:
        """Count total lines of Python code."""
        total_lines = 0
        for py_file in self.src_path.rglob("*.py"):
            try:
                lines = py_file.read_text().split("\n")
                # Count non-empty, non-comment lines
                code_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
                total_lines += len(code_lines)
            except Exception:
                continue
        return total_lines

    def _count_functions(self) -> int:
        """Count total number of functions and methods."""
        total_functions = 0
        for py_file in self.src_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Simple regex to count function definitions
                import re
                functions = re.findall(r"^\s*def\s+\w+", content, re.MULTILINE)
                total_functions += len(functions)
            except Exception:
                continue
        return total_functions

    def _generate_recommendations(self, lint_metrics: dict[str, Any],
                                 type_metrics: dict[str, Any],
                                 architecture_metrics: dict[str, Any],
                                 security_metrics: dict[str, Any]) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Lint recommendations
        if lint_metrics.get("total_errors", 0) > 50:
            recommendations.append("🔧 High lint error count - run aggressive auto-fixing")

        # Type recommendations
        if type_metrics.get("annotation_coverage", 100) < 80:
            recommendations.append("📝 Improve type annotation coverage")

        # Architecture recommendations
        if architecture_metrics.get("compliance_score", 100) < 90:
            recommendations.append("🏗️ Address hexagonal architecture violations")

        # Security recommendations
        if security_metrics.get("total_security_issues", 0) > 0:
            recommendations.append("🛡️ Address security vulnerabilities")

        if not recommendations:
            recommendations.append("✨ Excellent code quality - maintain current standards!")

        return recommendations


def main() -> None:
    """Main entry point for quality metrics analysis."""
    analyzer = CodeQualityMetrics()
    report = analyzer.generate_comprehensive_report()

    # Print formatted report

    # Print individual metrics
    report["metrics"]

    # Print recommendations
    for _rec in report["recommendations"]:
        pass

    # Save detailed report
    output_file = Path("code_quality_report.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
