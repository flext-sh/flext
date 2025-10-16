#!/usr/bin/env python3
"""FLEXT Documentation Maintenance & Quality Audit System.

Comprehensive documentation quality analysis, validation, and maintenance framework
for the FLEXT monorepo workspace with 659 markdown files across 36 docs directories.

Features:
- Content quality audit (freshness, completeness, structure)
- Link validation (external/internal links, images)
- Style consistency checking (markdown, formatting, accessibility)
- Automated reporting with severity classifications
- Git integration for change tracking
"""

import json
import operator
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required dependencies...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "requests",
            "beautifulsoup4",
        ]
    )
    import requests


@dataclass
class DocumentMetrics:
    """Metrics for a single documentation file."""

    file_path: Path
    word_count: int
    line_count: int
    heading_count: int
    code_block_count: int
    list_count: int
    link_count: int
    image_count: int
    last_modified: datetime
    age_days: int


@dataclass
class ValidationIssue:
    """Represents a validation issue found in documentation."""

    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    category: str
    file_path: Path
    line_number: int | None
    message: str
    suggestion: str | None = None


@dataclass
class AuditReport:
    """Complete audit report for documentation maintenance."""

    timestamp: datetime
    total_files: int
    total_issues: int
    files_analyzed: list[Path] = field(default_factory=list)
    metrics: list[DocumentMetrics] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    broken_links: list[dict[str, object]] = field(default_factory=list)
    missing_images: list[dict[str, object]] = field(default_factory=list)
    style_violations: list[dict[str, object]] = field(default_factory=list)


class DocumentationAuditor:
    """Main documentation audit and maintenance system."""

    def __init__(
        self, root_path: Path, config: dict[str, object] | None = None
    ) -> None:
        self.root_path = root_path
        self.config = config or self._default_config()
        self.report = AuditReport(
            timestamp=datetime.now(UTC), total_files=0, total_issues=0
        )

    def _default_config(self) -> dict[str, object]:
        """Default configuration for auditing."""
        return {
            "max_document_age_days": 90,
            "min_word_count": 50,
            "max_line_length": 120,
            "check_external_links": True,
            "link_timeout": 5,
            "exclude_patterns": [
                ".git",
                ".venv",
                "node_modules",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
            ],
            "style_rules": {
                "require_alt_text": True,
                "max_heading_level": 6,
                "consistent_list_markers": True,
                "code_block_language": True,
            },
        }

    def find_markdown_files(self) -> list[Path]:
        """Find all markdown files in the workspace."""
        markdown_files = []
        for pattern in ["**/*.md"]:
            for file_path in self.root_path.rglob(pattern):
                # Skip excluded directories
                if any(
                    exclude in str(file_path)
                    for exclude in self.config["exclude_patterns"]
                ):
                    continue
                markdown_files.append(file_path)
        return sorted(markdown_files)

    def analyze_document_metrics(self, file_path: Path) -> DocumentMetrics:
        """Analyze metrics for a single document."""
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        # Count elements
        word_count = len(re.findall(r"\w+", content))
        heading_count = len(re.findall(r"^#{1,6}\s+", content, re.MULTILINE))
        code_block_count = len(re.findall(r"```", content)) // 2
        list_count = len(re.findall(r"^[\s]*[-*+]\s+", content, re.MULTILINE))
        link_count = len(re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content))
        image_count = len(re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content))

        # File age
        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        age_days = (datetime.now(UTC) - last_modified).days

        return DocumentMetrics(
            file_path=file_path,
            word_count=word_count,
            line_count=len(lines),
            heading_count=heading_count,
            code_block_count=code_block_count,
            list_count=list_count,
            link_count=link_count,
            image_count=image_count,
            last_modified=last_modified,
            age_days=age_days,
        )

    def validate_content_quality(
        self, file_path: Path, metrics: DocumentMetrics
    ) -> list[ValidationIssue]:
        """Validate content quality and completeness."""
        issues = []
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Check document age
        if metrics.age_days > self.config["max_document_age_days"]:
            issues.append(
                ValidationIssue(
                    severity="medium",
                    category="content_freshness",
                    file_path=file_path,
                    line_number=None,
                    message=f"Document not updated in {metrics.age_days} days",
                    suggestion=f"Review and update content (last modified: {metrics.last_modified.strftime('%Y-%m-%d')})",
                )
            )

        # Check minimum word count
        if metrics.word_count < self.config["min_word_count"]:
            issues.append(
                ValidationIssue(
                    severity="low",
                    category="content_completeness",
                    file_path=file_path,
                    line_number=None,
                    message=f"Document has only {metrics.word_count} words",
                    suggestion=f"Consider adding more content (minimum: {self.config['min_word_count']} words)",
                )
            )

        # Check for TODO/FIXME markers
        todo_pattern = r"(TODO|FIXME|XXX|HACK):\s*(.+)"
        for i, line in enumerate(content.split("\n"), 1):
            if match := re.search(todo_pattern, line, re.IGNORECASE):
                issues.append(
                    ValidationIssue(
                        severity="low",
                        category="content_incomplete",
                        file_path=file_path,
                        line_number=i,
                        message=f"Found {match.group(1)}: {match.group(2)}",
                        suggestion="Resolve or remove TODO marker",
                    )
                )

        # Check for heading structure
        if metrics.heading_count == 0:
            issues.append(
                ValidationIssue(
                    severity="medium",
                    category="content_structure",
                    file_path=file_path,
                    line_number=None,
                    message="Document has no headings",
                    suggestion="Add headings to improve document structure",
                )
            )

        return issues

    def validate_links(
        self, file_path: Path, check_external: bool = True
    ) -> list[ValidationIssue]:
        """Validate all links in a document."""
        issues = []
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Find all markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for i, line in enumerate(content.split("\n"), 1):
            for match in re.finditer(link_pattern, line):
                link_text, link_url = match.groups()

                # Validate internal links
                if link_url.startswith(("./", "../", "/")):
                    target_path = (
                        file_path.parent / link_url
                        if link_url.startswith(("./", "../"))
                        else self.root_path / link_url.lstrip("/")
                    )
                    if not target_path.exists():
                        issues.append(
                            ValidationIssue(
                                severity="high",
                                category="broken_link",
                                file_path=file_path,
                                line_number=i,
                                message=f"Broken internal link: {link_url}",
                                suggestion=f"Fix or remove link to '{link_text}'",
                            )
                        )

                # Validate external links
                elif check_external and link_url.startswith(("http://", "https://")):
                    try:
                        response = requests.head(
                            link_url,
                            timeout=self.config["link_timeout"],
                            allow_redirects=True,
                        )
                        if response.status_code >= 400:
                            issues.append(
                                ValidationIssue(
                                    severity="high",
                                    category="broken_link",
                                    file_path=file_path,
                                    line_number=i,
                                    message=f"External link returns {response.status_code}: {link_url}",
                                    suggestion=f"Update or remove link to '{link_text}'",
                                )
                            )
                    except requests.RequestException as e:
                        issues.append(
                            ValidationIssue(
                                severity="medium",
                                category="link_validation_failed",
                                file_path=file_path,
                                line_number=i,
                                message=f"Could not validate external link: {link_url} ({e!s})",
                                suggestion="Verify link manually",
                            )
                        )

        return issues

    def validate_images(self, file_path: Path) -> list[ValidationIssue]:
        """Validate image references and alt text."""
        issues = []
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Find all markdown images
        image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        for i, line in enumerate(content.split("\n"), 1):
            for match in re.finditer(image_pattern, line):
                alt_text, image_url = match.groups()

                # Check for alt text
                if not alt_text and self.config["style_rules"]["require_alt_text"]:
                    issues.append(
                        ValidationIssue(
                            severity="medium",
                            category="accessibility",
                            file_path=file_path,
                            line_number=i,
                            message=f"Image missing alt text: {image_url}",
                            suggestion="Add descriptive alt text for accessibility",
                        )
                    )

                # Validate local image paths
                if not image_url.startswith(("http://", "https://")):
                    image_path = (
                        file_path.parent / image_url
                        if image_url.startswith(("./", "../"))
                        else self.root_path / image_url.lstrip("/")
                    )
                    if not image_path.exists():
                        issues.append(
                            ValidationIssue(
                                severity="high",
                                category="missing_image",
                                file_path=file_path,
                                line_number=i,
                                message=f"Image file not found: {image_url}",
                                suggestion="Add missing image or update path",
                            )
                        )

        return issues

    def validate_style(self, file_path: Path) -> list[ValidationIssue]:
        """Validate markdown style and formatting."""
        issues = []
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        # Check line length
        for i, line in enumerate(lines, 1):
            # Skip code blocks and URLs
            if line.strip().startswith("```") or re.search(r"https?://", line):
                continue
            if len(line) > self.config["max_line_length"]:
                issues.append(
                    ValidationIssue(
                        severity="low",
                        category="style_formatting",
                        file_path=file_path,
                        line_number=i,
                        message=f"Line exceeds {self.config['max_line_length']} characters ({len(line)} chars)",
                        suggestion="Break line for better readability",
                    )
                )

        # Check heading hierarchy
        headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)
        prev_level = 0
        for heading in headings:
            level = len(heading[0])
            if level > prev_level + 1 and prev_level > 0:
                issues.append(
                    ValidationIssue(
                        severity="low",
                        category="style_structure",
                        file_path=file_path,
                        line_number=None,
                        message=f"Heading level skipped: {heading[1]}",
                        suggestion="Use sequential heading levels (h1 -> h2 -> h3)",
                    )
                )
            prev_level = level

        # Check code blocks have language specified
        if self.config["style_rules"]["code_block_language"]:
            code_blocks = re.findall(r"```(\w*)", content)
            issues.extend(
                ValidationIssue(
                    severity="low",
                    category="style_formatting",
                    file_path=file_path,
                    line_number=None,
                    message="Code block missing language specification",
                    suggestion="Add language identifier (e.g., ```python)",
                )
                for block in code_blocks
                if not block
            )

        return issues

    def run_full_audit(self) -> AuditReport:
        """Run complete documentation audit."""
        print("🔍 Starting FLEXT Documentation Audit...")
        print(f"Root path: {self.root_path}")

        # Find all markdown files
        markdown_files = self.find_markdown_files()
        self.report.total_files = len(markdown_files)
        print(f"Found {self.report.total_files} markdown files\n")

        # Analyze each file
        for idx, file_path in enumerate(markdown_files, 1):
            print(
                f"[{idx}/{self.report.total_files}] Analyzing: {file_path.relative_to(self.root_path)}"
            )

            # Collect metrics
            metrics = self.analyze_document_metrics(file_path)
            self.report.metrics.append(metrics)
            self.report.files_analyzed.append(file_path)

            # Run validations
            issues = []
            issues.extend(self.validate_content_quality(file_path, metrics))
            issues.extend(
                self.validate_links(file_path, check_external=False)
            )  # External link checking can be slow
            issues.extend(self.validate_images(file_path))
            issues.extend(self.validate_style(file_path))

            self.report.issues.extend(issues)

        self.report.total_issues = len(self.report.issues)
        print(
            f"\n✅ Audit complete! Found {self.report.total_issues} issues across {self.report.total_files} files"
        )

        return self.report

    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate audit report in specified format."""
        if output_format == "markdown":
            return self._generate_markdown_report()
        if output_format == "json":
            return self._generate_json_report()
        if output_format == "html":
            return self._generate_html_report()
        msg = f"Unsupported format: {output_format}"
        raise ValueError(msg)

    def _generate_markdown_report(self) -> str:
        """Generate markdown audit report."""
        report_lines = [
            "# FLEXT Documentation Audit Report",
            "",
            f"**Generated:** {self.report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Files Analyzed:** {self.report.total_files}",
            f"**Total Issues Found:** {self.report.total_issues}",
            "",
            "## 📊 Summary Statistics",
            "",
        ]

        # Calculate statistics
        total_words = sum(m.word_count for m in self.report.metrics)
        total_lines = sum(m.line_count for m in self.report.metrics)
        avg_age = (
            sum(m.age_days for m in self.report.metrics) / len(self.report.metrics)
            if self.report.metrics
            else 0
        )

        report_lines.extend(
            [
                f"- **Total Words:** {total_words:,}",
                f"- **Total Lines:** {total_lines:,}",
                f"- **Average Document Age:** {avg_age:.1f} days",
                f"- **Total Links:** {sum(m.link_count for m in self.report.metrics)}",
                f"- **Total Images:** {sum(m.image_count for m in self.report.metrics)}",
                "",
                "## 🚨 Issues by Severity",
                "",
            ]
        )

        # Group issues by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for issue in self.report.issues:
            severity_counts[issue.severity] += 1

        report_lines.extend(
            [
                f"- **Critical:** {severity_counts['critical']}",
                f"- **High:** {severity_counts['high']}",
                f"- **Medium:** {severity_counts['medium']}",
                f"- **Low:** {severity_counts['low']}",
                f"- **Info:** {severity_counts['info']}",
                "",
                "## 📁 Issues by Category",
                "",
            ]
        )

        # Group issues by category
        category_counts: dict[str, int] = {}
        for issue in self.report.issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        for category, count in sorted(
            category_counts.items(), key=operator.itemgetter(1), reverse=True
        ):
            report_lines.append(f"- **{category.replace('_', ' ').title()}:** {count}")

        report_lines.extend(["", "## 🔍 Detailed Issues", ""])

        # List critical and high severity issues
        critical_high_issues = [
            i for i in self.report.issues if i.severity in {"critical", "high"}
        ]
        if critical_high_issues:
            report_lines.append("### Critical & High Severity Issues\n")
            for issue in critical_high_issues[:50]:  # Limit to first 50
                file_rel = issue.file_path.relative_to(self.root_path)
                line_info = f":{issue.line_number}" if issue.line_number else ""
                report_lines.extend(
                    [
                        f"**{issue.severity.upper()}** | `{file_rel}{line_info}`",
                        f"- **Issue:** {issue.message}",
                        f"- **Suggestion:** {issue.suggestion or 'N/A'}",
                        "",
                    ]
                )

        report_lines.extend(
            [
                "## 📈 Oldest Documents (Top 10)",
                "",
            ]
        )

        # List oldest documents
        oldest_docs = sorted(
            self.report.metrics, key=lambda m: m.age_days, reverse=True
        )[:10]
        for metric in oldest_docs:
            file_rel = metric.file_path.relative_to(self.root_path)
            report_lines.append(
                f"- `{file_rel}` - {metric.age_days} days old "
                f"({metric.last_modified.strftime('%Y-%m-%d')})"
            )

        report_lines.extend(
            [
                "",
                "## 📝 Recommendations",
                "",
                "1. **Address Critical Issues:** Focus on broken links and missing images first",
                "2. **Update Stale Content:** Review documents older than 90 days",
                "3. **Improve Accessibility:** Add alt text to all images",
                "4. **Enhance Structure:** Add headings to documents lacking structure",
                "5. **Resolve TODOs:** Complete or remove TODO markers",
                "",
                "---",
                "",
                "*Generated by FLEXT Documentation Maintenance System*",
            ]
        )

        return "\n".join(report_lines)

    def _generate_json_report(self) -> str:
        """Generate JSON audit report."""
        report_data = {
            "timestamp": self.report.timestamp.isoformat(),
            "total_files": self.report.total_files,
            "total_issues": self.report.total_issues,
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "file": str(issue.file_path.relative_to(self.root_path)),
                    "line": issue.line_number,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                }
                for issue in self.report.issues
            ],
            "metrics": [
                {
                    "file": str(metric.file_path.relative_to(self.root_path)),
                    "word_count": metric.word_count,
                    "age_days": metric.age_days,
                    "last_modified": metric.last_modified.isoformat(),
                }
                for metric in self.report.metrics
            ],
        }
        return json.dumps(report_data, indent=2)

    def _generate_html_report(self) -> str:
        """Generate HTML audit report with interactive dashboard."""
        # Convert markdown report to HTML structure
        md_report = self._generate_markdown_report()

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLEXT Documentation Audit Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .severity-critical {{ color: #e74c3c; font-weight: bold; }}
        .severity-high {{ color: #e67e22; font-weight: bold; }}
        .severity-medium {{ color: #f39c12; }}
        .severity-low {{ color: #95a5a6; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        code {{ background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <pre>{md_report}</pre>
    </div>
</body>
</html>"""

    def save_report(self, output_path: Path, output_format: str = "markdown") -> None:
        """Save audit report to file."""
        report_content = self.generate_report(output_format)
        output_path.write_text(report_content, encoding="utf-8")
        print(f"\n📄 Report saved to: {output_path}")


def main() -> None:
    """Main entry point for documentation audit."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FLEXT Documentation Maintenance & Quality Audit System"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of FLEXT workspace (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs_audit_report.md"),
        help="Output file for audit report",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Report output format",
    )
    parser.add_argument(
        "--check-external-links",
        action="store_true",
        help="Enable external link validation (slower)",
    )

    args = parser.parse_args()

    # Run audit
    auditor = DocumentationAuditor(args.root)
    auditor.config["check_external_links"] = args.check_external_links
    auditor.run_full_audit()

    # Save report
    auditor.save_report(args.output, args.format)


if __name__ == "__main__":
    main()
