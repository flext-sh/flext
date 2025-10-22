#!/usr/bin/env python3
"""Pydantic v2 compliance monitoring and reporting dashboard.

Generates comprehensive compliance reports and tracks ecosystem-wide adoption.

Usage:
    # Generate compliance report for current project
    python monitor_pydantic_v2_compliance.py

    # Generate detailed report with timestamps
    python monitor_pydantic_v2_compliance.py --detailed

    # Generate HTML report
    python monitor_pydantic_v2_compliance.py --format=html --output=report.html

    # Run audit across all projects
    python monitor_pydantic_v2_compliance.py --all-projects

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar


@dataclass
class ComplianceMetrics:
    """Compliance metrics for a project."""

    project_name: str
    timestamp: str
    status: str  # PASS, WARNING, FAIL
    total_files: int = 0
    total_violations: int = 0
    critical_violations: int = 0
    high_violations: int = 0
    medium_violations: int = 0
    pydantic_v2_patterns: int = 0
    pydantic_v1_patterns: int = 0
    compliance_percentage: float = 0.0
    recommendations: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        """Format metrics for display."""
        return f"{self.project_name}: {self.status} ({self.compliance_percentage:.1f}%)"


@dataclass
class DashboardReport:
    """Dashboard compliance report."""

    generated_at: str
    total_projects: int = 0
    compliant_projects: int = 0
    warning_projects: int = 0
    failed_projects: int = 0
    ecosystem_compliance: float = 0.0
    metrics: list[ComplianceMetrics] = field(default_factory=list)
    critical_issues: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class PydanticV2Monitor:
    """Monitors Pydantic v2 compliance across FLEXT ecosystem."""

    FLEXT_PROJECTS: ClassVar[list[str]] = [
        "flext-core",
        "flext-api",
        "flext-auth",
        "flext-cli",
        "flext-ldif",
        "flext-ldap",
        "flext-web",
        "flext-meltano",
        "flext-observability",
        "flext-quality",
        "flext-grpc",
        "flext-plugin",
        "flext-tap-ldap",
        "flext-tap-ldif",
        "flext-tap-oracle",
        "flext-tap-oracle-oic",
        "flext-tap-oracle-wms",
        "flext-target-ldap",
        "flext-target-ldif",
        "flext-target-oracle",
        "flext-target-oracle-oic",
        "flext-target-oracle-wms",
        "flext-dbt-ldap",
        "flext-dbt-ldif",
        "flext-dbt-oracle",
        "flext-dbt-oracle-wms",
        "flext-db-oracle",
        "client-a-oud-mig",
        "client-b-meltano-native",
    ]

    def __init__(self, workspace_root: str | None = None) -> None:
        """Initialize monitor."""
        self.workspace_root = Path(workspace_root or ".").resolve()
        self.report = DashboardReport(generated_at=datetime.now().isoformat())

    def generate_report(
        self, all_projects: bool = False, detailed: bool = False
    ) -> DashboardReport:
        """Generate compliance report."""
        projects = self.FLEXT_PROJECTS if all_projects else [self.workspace_root.name]

        for project_name in projects:
            project_path = (
                self.workspace_root / project_name
                if all_projects
                else self.workspace_root
            )

            if not project_path.exists():
                continue

            metrics = self._audit_project(project_path, project_name)
            if metrics:
                self.report.metrics.append(metrics)

        # Calculate ecosystem metrics
        self._calculate_ecosystem_metrics()

        return self.report

    def _audit_project(
        self, project_path: Path, project_name: str
    ) -> ComplianceMetrics | None:
        """Audit a single project."""
        src_path = project_path / "src"
        if not src_path.exists():
            return None

        # Collect Python files
        py_files = list(src_path.rglob("*.py"))
        if not py_files:
            return None

        metrics = ComplianceMetrics(
            project_name=project_name,
            timestamp=datetime.now().isoformat(),
            status="PASS",
            total_files=len(py_files),
        )

        # Scan files
        for py_file in py_files:
            self._scan_file(py_file, metrics)

        # Calculate compliance percentage
        if metrics.total_files > 0:
            compliant_files = metrics.total_files - (
                metrics.critical_violations + metrics.high_violations
            )
            metrics.compliance_percentage = (
                compliant_files / metrics.total_files
            ) * 100

        # Determine status
        if metrics.critical_violations > 0:
            metrics.status = "FAIL"
        elif metrics.high_violations > 0 or metrics.medium_violations > 0:
            metrics.status = "WARNING"
        else:
            metrics.status = "PASS"

        return metrics

    def _scan_file(self, py_file: Path, metrics: ComplianceMetrics) -> None:
        """Scan a single file for Pydantic v2 compliance."""
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            return

        lines = content.split("\n")

        # Critical patterns
        critical_patterns = {
            r"class\s+\w+.*:\s*\n\s*class\s+Config": "class Config",
            r"\.dict\(": ".dict()",
            r"parse_obj\(": "parse_obj()",
            r"@validator\(": "@validator",
            r"@root_validator": "@root_validator",
        }

        for pattern in critical_patterns:
            for line in lines:
                if re.search(pattern, line):
                    metrics.critical_violations += 1
                    metrics.pydantic_v1_patterns += 1

        # Pydantic v2 patterns (positive indicators)
        v2_patterns = {
            r"model_dump\(": "model_dump()",
            r"model_validate\(": "model_validate()",
            r"@field_validator": "@field_validator",
            r"ConfigDict": "ConfigDict",
        }

        for pattern in v2_patterns:
            for line in lines:
                if re.search(pattern, line):
                    metrics.pydantic_v2_patterns += 1

    def _calculate_ecosystem_metrics(self) -> None:
        """Calculate ecosystem-wide metrics."""
        if not self.report.metrics:
            return

        total = len(self.report.metrics)
        self.report.total_projects = total
        self.report.compliant_projects = sum(
            1 for m in self.report.metrics if m.status == "PASS"
        )
        self.report.warning_projects = sum(
            1 for m in self.report.metrics if m.status == "WARNING"
        )
        self.report.failed_projects = sum(
            1 for m in self.report.metrics if m.status == "FAIL"
        )

        if total > 0:
            self.report.ecosystem_compliance = (
                self.report.compliant_projects / total
            ) * 100

        # Identify critical issues
        for metrics in self.report.metrics:
            if metrics.status == "FAIL":
                self.report.critical_issues.append({
                    "project": metrics.project_name,
                    "violations": metrics.critical_violations,
                    "patterns": metrics.pydantic_v1_patterns,
                })

        # Add recommendations
        if self.report.failed_projects > 0:
            self.report.recommendations.append(
                f"Fix {self.report.failed_projects} project(s) with critical violations"
            )

        if self.report.warning_projects > 0:
            self.report.recommendations.append(
                f"Address {self.report.warning_projects} project(s) with warnings"
            )

    def generate_html_report(self) -> str:
        """Generate HTML report."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>FLEXT Pydantic v2 Compliance Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007acc;
            padding-bottom: 10px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        .metric {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #007acc;
        }
        .metric-label {
            color: #666;
            margin-top: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th {
            background-color: #007acc;
            color: white;
            padding: 12px;
            text-align: left;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        .pass {
            color: #28a745;
            font-weight: bold;
        }
        .warning {
            color: #ffc107;
            font-weight: bold;
        }
        .fail {
            color: #dc3545;
            font-weight: bold;
        }
        .progress {
            width: 100%;
            height: 20px;
            background-color: #eee;
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background-color: #28a745;
            transition: width 0.3s;
        }
        .progress-bar.warning {
            background-color: #ffc107;
        }
        .progress-bar.fail {
            background-color: #dc3545;
        }
        .timestamp {
            color: #999;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>🔍 FLEXT Pydantic v2 Compliance Dashboard</h1>

    <div class="summary">
        <div class="metric">
            <div class="metric-value">"""
        html += str(self.report.total_projects)
        html += """</div>
            <div class="metric-label">Total Projects</div>
        </div>
        <div class="metric">
            <div class="metric-value pass">"""
        html += str(self.report.compliant_projects)
        html += """</div>
            <div class="metric-label">Compliant ✅</div>
        </div>
        <div class="metric">
            <div class="metric-value warning">"""
        html += str(self.report.warning_projects)
        html += """</div>
            <div class="metric-label">Warnings ⚠️</div>
        </div>
        <div class="metric">
            <div class="metric-value fail">"""
        html += str(self.report.failed_projects)
        html += """</div>
            <div class="metric-label">Failed ❌</div>
        </div>
    </div>

    <h2>Ecosystem Compliance: """
        html += f"{self.report.ecosystem_compliance:.1f}%"
        html += """</h2>
    <div class="progress">
        <div class="progress-bar" style="width: """
        html += f"{self.report.ecosystem_compliance}%"
        html += """"></div>
    </div>

    <h2>Project Status</h2>
    <table>
        <thead>
            <tr>
                <th>Project</th>
                <th>Status</th>
                <th>Compliance</th>
                <th>Files</th>
                <th>Violations</th>
            </tr>
        </thead>
        <tbody>
"""
        for metrics in sorted(
            self.report.metrics, key=lambda m: m.compliance_percentage
        ):
            status_class = metrics.status.lower()
            html += f"""            <tr>
                <td><strong>{metrics.project_name}</strong></td>
                <td class="{status_class}">{metrics.status}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar {status_class}" style="width: {metrics.compliance_percentage:.1f}%"></div>
                    </div>
                    {metrics.compliance_percentage:.1f}%
                </td>
                <td>{metrics.total_files}</td>
                <td>{metrics.total_violations}</td>
            </tr>
"""
        html += """        </tbody>
    </table>

    <div class="timestamp">
        Report generated: """
        html += self.report.generated_at
        html += """
    </div>
</body>
</html>
"""
        return html

    def generate_markdown_report(self) -> str:
        """Generate Markdown report."""
        md = f"""# 🔍 FLEXT Pydantic v2 Compliance Dashboard

**Generated**: {self.report.generated_at}

## 📊 Summary

| Metric | Value |
|--------|-------|
| Total Projects | {self.report.total_projects} |
| Compliant ✅ | {self.report.compliant_projects} |
| Warnings ⚠️ | {self.report.warning_projects} |
| Failed ❌ | {self.report.failed_projects} |
| Ecosystem Compliance | {self.report.ecosystem_compliance:.1f}% |

## 📈 Project Status

| Project | Status | Compliance | Files | Violations |
|---------|--------|-----------|-------|-----------|
"""
        for metrics in sorted(
            self.report.metrics, key=lambda m: m.compliance_percentage
        ):
            status_emoji = {
                "PASS": "✅",
                "WARNING": "⚠️",
                "FAIL": "❌",
            }.get(metrics.status, "❓")

            md += f"| {metrics.project_name} | {status_emoji} {metrics.status} | {metrics.compliance_percentage:.1f}% | {metrics.total_files} | {metrics.total_violations} |\n"

        if self.report.critical_issues:
            md += "\n## 🔴 Critical Issues\n\n"
            for issue in self.report.critical_issues:
                md += f"- **{issue['project']}**: {issue['violations']} critical violations\n"

        if self.report.recommendations:
            md += "\n## 💡 Recommendations\n\n"
            for rec in self.report.recommendations:
                md += f"- {rec}\n"

        return md


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pydantic v2 compliance monitoring and reporting"
    )
    parser.add_argument(
        "--all-projects",
        action="store_true",
        help="Audit all FLEXT projects",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Include detailed metrics",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "html", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        help="Output file (default: stdout)",
    )
    args = parser.parse_args()

    monitor = PydanticV2Monitor()
    report = monitor.generate_report(
        all_projects=args.all_projects, detailed=args.detailed
    )

    # Generate output based on format
    if args.format == "json":
        output = json.dumps(asdict(report), indent=2)
    elif args.format == "html":
        output = monitor.generate_html_report()
    elif args.format == "markdown":
        output = monitor.generate_markdown_report()
    else:  # text
        output = f"""
FLEXT Pydantic v2 Compliance Dashboard
=====================================
Generated: {report.generated_at}

Summary:
--------
Total Projects: {report.total_projects}
Compliant: {report.compliant_projects}
Warnings: {report.warning_projects}
Failed: {report.failed_projects}
Ecosystem Compliance: {report.ecosystem_compliance:.1f}%

Project Status:
---------------
"""
        for metrics in sorted(report.metrics, key=lambda m: m.compliance_percentage):
            status_emoji = {
                "PASS": "✅",
                "WARNING": "⚠️",
                "FAIL": "❌",
            }.get(metrics.status, "❓")
            output += f"{status_emoji} {metrics.project_name}: {metrics.status} ({metrics.compliance_percentage:.1f}%)\n"

    # Output result
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output)

    return 0 if report.failed_projects == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
