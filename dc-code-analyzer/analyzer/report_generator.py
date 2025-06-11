"""Web-based report generator for Django Code Analyzer."""

from __future__ import annotations

import io
import logging
from typing import Any

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa

from .models import (
    AnalysisReport,
    AnalysisSession,
    DeadCodeIssue,
    DuplicateCodeBlock,
    FileAnalysis,
    QualityMetrics,
    SecurityIssue,
)

logger = logging.getLogger(__name__)


class WebReportGenerator:
    """Web-based report generator for analysis results."""

    def __init__(self, session: AnalysisSession):
        self.session = session
        self.flx_project = session.flx_project

    def generate_summary_report(self, format: str = "html") -> AnalysisReport:
        """Generate a summary report."""
        try:
            # Get quality metrics
            quality_metrics = getattr(self.session, "quality_metrics", None)
            if not quality_metrics:
                content = self._generate_no_metrics_content()
            else:
                content = self._generate_summary_content(quality_metrics)

            # Convert to requested format
            if format == "html":
                final_content = self._render_html_template("summary", content)
            elif format == "markdown":
                final_content = self._render_markdown_template("summary", content)
            elif format == "pdf":
                final_content = self._render_pdf_template("summary", content)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Save report
            report = AnalysisReport.objects.create(
                session=self.session,
                name=f"Summary Report - {self.flx_project.name}",
                report_type="summary",
                format=format,
                content=final_content,
            )

            logger.info(f"Generated summary report in {format} format")
            return report

        except Exception as e:
            logger.exception(f"Failed to generate summary report: {e}")
            raise

    def generate_detailed_report(self, format: str = "html") -> AnalysisReport:
        """Generate a detailed analysis report."""
        try:
            content = self._generate_detailed_content()

            # Convert to requested format
            if format == "html":
                final_content = self._render_html_template("detailed", content)
            elif format == "markdown":
                final_content = self._render_markdown_template("detailed", content)
            elif format == "pdf":
                final_content = self._render_pdf_template("detailed", content)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Save report
            report = AnalysisReport.objects.create(
                session=self.session,
                name=f"Detailed Report - {self.flx_project.name}",
                report_type="detailed",
                format=format,
                content=final_content,
            )

            logger.info(f"Generated detailed report in {format} format")
            return report

        except Exception as e:
            logger.exception(f"Failed to generate detailed report: {e}")
            raise

    def generate_security_report(self, format: str = "html") -> AnalysisReport:
        """Generate a security-focused report."""
        try:
            content = self._generate_security_content()

            # Convert to requested format
            if format == "html":
                final_content = self._render_html_template("security", content)
            elif format == "markdown":
                final_content = self._render_markdown_template("security", content)
            elif format == "pdf":
                final_content = self._render_pdf_template("security", content)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Save report
            report = AnalysisReport.objects.create(
                session=self.session,
                name=f"Security Report - {self.flx_project.name}",
                report_type="security",
                format=format,
                content=final_content,
            )

            logger.info(f"Generated security report in {format} format")
            return report

        except Exception as e:
            logger.exception(f"Failed to generate security report: {e}")
            raise

    def _generate_summary_content(
        self,
        quality_metrics: QualityMetrics,
    ) -> dict[str, Any]:
        """Generate content for summary report."""
        # File analysis data
        file_analyses = FileAnalysis.objects.filter(session=self.session)

        # Issue counts
        security_issues = SecurityIssue.objects.filter(session=self.session)
        dead_code_issues = DeadCodeIssue.objects.filter(session=self.session)
        duplicate_blocks = DuplicateCodeBlock.objects.filter(session=self.session)

        # Top complex files
        complex_files = file_analyses.order_by("-complexity_score")[:5]

        return {
            "project_name": self.flx_project.name,
            "session": self.session,
            "generated_at": timezone.now(),
            "quality_metrics": quality_metrics,
            "file_count": file_analyses.count(),
            "total_lines": quality_metrics.total_lines,
            "security_issues_count": security_issues.count(),
            "dead_code_issues_count": dead_code_issues.count(),
            "duplicate_blocks_count": duplicate_blocks.count(),
            "complex_files": complex_files,
            "grade_color": self._get_grade_color(quality_metrics.overall_score),
        }

    def _generate_detailed_content(self) -> dict[str, Any]:
        """Generate content for detailed report."""
        # Get all analysis data
        file_analyses = FileAnalysis.objects.filter(session=self.session)
        security_issues = SecurityIssue.objects.filter(session=self.session).order_by(
            "-severity",
            "-confidence",
        )
        dead_code_issues = DeadCodeIssue.objects.filter(session=self.session).order_by(
            "-confidence",
        )
        duplicate_blocks = DuplicateCodeBlock.objects.filter(
            session=self.session,
        ).order_by("-similarity_score")
        quality_metrics = getattr(self.session, "quality_metrics", None)

        # Calculate file statistics
        file_stats = {
            "largest_files": file_analyses.order_by("-lines_of_code")[:10],
            "most_complex": file_analyses.order_by("-complexity_score")[:10],
            "least_maintainable": file_analyses.order_by("maintainability_score")[:10],
        }

        return {
            "project_name": self.flx_project.name,
            "session": self.session,
            "generated_at": timezone.now(),
            "quality_metrics": quality_metrics,
            "file_analyses": file_analyses,
            "file_stats": file_stats,
            "security_issues": security_issues[:20],  # Top 20
            "dead_code_issues": dead_code_issues[:20],  # Top 20
            "duplicate_blocks": duplicate_blocks[:10],  # Top 10
            "security_summary": self._get_security_summary(security_issues),
            "complexity_distribution": self._get_complexity_distribution(file_analyses),
        }

    def _generate_security_content(self) -> dict[str, Any]:
        """Generate content for security report."""
        security_issues = SecurityIssue.objects.filter(session=self.session)

        # Group by severity
        issues_by_severity = {
            "CRITICAL": security_issues.filter(severity="CRITICAL"),
            "HIGH": security_issues.filter(severity="HIGH"),
            "MEDIUM": security_issues.filter(severity="MEDIUM"),
            "LOW": security_issues.filter(severity="LOW"),
        }

        # Group by issue type
        issues_by_type: dict[str, list[Any]] = {}
        for issue in security_issues:
            if issue.issue_type not in issues_by_type:
                issues_by_type[issue.issue_type] = []
            issues_by_type[issue.issue_type].append(issue)

        return {
            "project_name": self.flx_project.name,
            "session": self.session,
            "generated_at": timezone.now(),
            "total_issues": security_issues.count(),
            "issues_by_severity": issues_by_severity,
            "issues_by_type": issues_by_type,
            "severity_counts": {
                severity: issues.count()
                for severity, issues in issues_by_severity.items()
            },
            "recommendations": self._generate_security_recommendations(security_issues),
        }

    def _generate_no_metrics_content(self) -> dict[str, Any]:
        """Generate content when no quality metrics are available."""
        return {
            "project_name": self.flx_project.name,
            "session": self.session,
            "generated_at": timezone.now(),
            "error_message": "Analysis is not yet complete or failed to generate quality metrics.",
        }

    def _render_html_template(self, report_type: str, content: dict[str, Any]) -> str:
        """Render HTML template for report."""
        template_name = f"reports/{report_type}_report.html"

        # Use a base template if specific template doesn't exist
        try:
            template = get_template(template_name)
        except Exception:
            template = get_template("reports/base_report.html")
            content["report_type"] = report_type

        return template.render(content)

    def _render_markdown_template(
        self,
        report_type: str,
        content: dict[str, Any],
    ) -> str:
        """Render Markdown template for report."""
        template_name = f"reports/{report_type}_report.md"

        # Use a base template if specific template doesn't exist
        try:
            template = get_template(template_name)
        except Exception:
            # Generate basic markdown
            return self._generate_basic_markdown(report_type, content)

        return template.render(content)

    def _render_pdf_template(self, report_type: str, content: dict[str, Any]) -> str:
        """Render PDF template for report."""
        # First render as HTML
        html_content = self._render_html_template(report_type, content)

        # Convert to PDF
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result)

        if not pdf.err:
            return result.getvalue().decode("latin1")  # Store as string
        raise Exception("PDF generation failed")

    def _generate_basic_markdown(
        self,
        report_type: str,
        content: dict[str, Any],
    ) -> str:
        """Generate basic Markdown when template is not available."""
        md_content = f"""# {report_type.title()} Report

**Project:** {content.get('project_name', 'Unknown')}
**Generated:** {content.get('generated_at', timezone.now()).strftime('%Y-%m-%d %H:%M:%S')}

---

"""

        if "quality_metrics" in content and content["quality_metrics"]:
            qm = content["quality_metrics"]
            md_content += f"""## Quality Overview

- **Overall Score:** {qm.overall_score:.1f}/100 ({getattr(content.get('session'), 'quality_grade', 'N/A')})
- **Total Files:** {qm.total_files}
- **Total Lines:** {qm.total_lines:,}
- **Security Issues:** {qm.security_issues_count}
- **Dead Code Items:** {qm.dead_code_items_count}

## Score Breakdown

- **Complexity:** {qm.complexity_score:.1f}/100
- **Security:** {qm.security_score:.1f}/100
- **Maintainability:** {qm.maintainability_score:.1f}/100
- **Documentation:** {qm.documentation_score:.1f}/100
- **Duplication:** {qm.duplication_score:.1f}/100

"""

        if "error_message" in content:
            md_content += f"""## Error

{content['error_message']}
"""

        return md_content

    def _get_grade_color(self, score: float) -> str:
        """Get color class for grade display."""
        if score >= 90:
            return "success"
        if score >= 75:
            return "warning"
        if score >= 60:
            return "info"
        return "danger"

    def _get_security_summary(self, security_issues) -> dict[str, int]:
        """Get security issues summary."""
        summary = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in security_issues:
            summary[issue.severity] = summary.get(issue.severity, 0) + 1
        return summary

    def _get_complexity_distribution(self, file_analyses) -> dict[str, int]:
        """Get complexity distribution."""
        distribution = {"low": 0, "medium": 0, "high": 0, "very_high": 0}

        for file_analysis in file_analyses:
            complexity = file_analysis.complexity_score
            if complexity <= 5:
                distribution["low"] += 1
            elif complexity <= 10:
                distribution["medium"] += 1
            elif complexity <= 20:
                distribution["high"] += 1
            else:
                distribution["very_high"] += 1

        return distribution

    def _generate_security_recommendations(self, security_issues) -> list[str]:
        """Generate security recommendations."""
        recommendations = []

        # Group by issue type
        issue_types = {}
        for issue in security_issues:
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = 0
            issue_types[issue.issue_type] += 1

        # Generate recommendations based on most common issues
        sorted_types = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)

        for issue_type, count in sorted_types[:5]:  # Top 5 issue types
            recommendations.append(
                f"Address {count} instances of {issue_type} throughout the codebase",
            )

        return recommendations


def create_download_response(report: AnalysisReport) -> HttpResponse:
    """Create HTTP response for report download."""
    if report.format == "pdf":
        response = HttpResponse(
            report.content.encode("latin1"),
            content_type="application/pdf",
        )
        filename = f"{report.name.replace(' ', '_')}.pdf"
    elif report.format == "markdown":
        response = HttpResponse(report.content, content_type="text/markdown")
        filename = f"{report.name.replace(' ', '_')}.md"
    else:  # HTML
        response = HttpResponse(report.content, content_type="text/html")
        filename = f"{report.name.replace(' ', '_')}.html"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Update download count
    report.download_count += 1
    report.save()

    return response
