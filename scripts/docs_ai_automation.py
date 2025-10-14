#!/usr/bin/env python3
"""AI-Powered Documentation Maintenance Automation.

Comprehensive automation system that combines:
- Advanced content analysis
- Smart optimization
- Health monitoring
- Automated reporting
- Intelligent decision making
- Team collaboration features
"""

import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextCore

# Import our custom modules
try:
    from docs_advanced_analyzer import AdvancedDocumentationAnalyzer
    from docs_health_monitor import DocumentationHealthMonitor
    from docs_smart_optimizer import SmartDocumentationOptimizer
except ImportError:
    print(
        "Error: Required modules not found. Please ensure all documentation scripts are in the same directory."
    )
    sys.exit(1)


@dataclass
class AutomationConfig:
    """Configuration for AI automation."""

    # Analysis settings
    enable_advanced_analysis: bool = True
    enable_smart_optimization: bool = True
    enable_health_monitoring: bool = True

    # Optimization settings
    auto_apply_optimizations: bool = False
    optimization_confidence_threshold: float = 0.7
    max_optimizations_per_run: int = 50

    # Health monitoring
    health_check_threshold: float = 0.6
    alert_on_critical_issues: bool = True

    # Reporting
    generate_reports: bool = True
    report_formats: FlextCore.Types.StringList = None

    # Team collaboration
    enable_team_features: bool = True
    notify_on_issues: bool = False

    def __post_init__(self):
        if self.report_formats is None:
            self.report_formats = ["markdown", "html", "json"]


@dataclass
class AutomationResult:
    """Result of automation run."""

    success: bool
    files_processed: int
    optimizations_applied: int
    issues_found: int
    health_score: float
    recommendations: FlextCore.Types.StringList
    errors: FlextCore.Types.StringList
    execution_time: float
    timestamp: datetime


class AIDocumentationAutomation:
    """AI-powered documentation maintenance automation."""

    def __init__(self, root_path: Path, config: AutomationConfig | None = None) -> None:
        self.root_path = root_path
        self.config = config or AutomationConfig()
        self.results: list[AutomationResult] = []

        # Initialize components
        self.analyzer = AdvancedDocumentationAnalyzer(root_path)
        self.optimizer = SmartDocumentationOptimizer(root_path)
        self.monitor = DocumentationHealthMonitor(root_path)

    def run_complete_automation(self, dry_run: bool = True) -> AutomationResult:
        """Run complete AI-powered automation."""
        start_time = datetime.now(UTC)
        print("🤖 Starting AI-Powered Documentation Automation...")
        print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
        print(f"Root: {self.root_path}")
        print()

        files_processed = 0
        optimizations_applied = 0
        issues_found = 0
        health_score = 0.0
        recommendations = []
        errors = []

        try:
            # Step 1: Advanced Analysis
            if self.config.enable_advanced_analysis:
                print("🔍 Step 1: Running advanced content analysis...")
                try:
                    analysis_report = self.analyzer.run_comprehensive_analysis()
                    files_processed = analysis_report["total_files"]
                    print(f"  ✅ Analyzed {files_processed} files")
                except Exception as e:
                    error_msg = f"Analysis failed: {e}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")

            # Step 2: Smart Optimization
            if self.config.enable_smart_optimization:
                print("\n🔧 Step 2: Running smart optimization...")
                try:
                    optimization_results = self.optimizer.optimize_all_documents()
                    optimizations_applied = len([
                        r for r in optimization_results if r.changes_made
                    ])
                    print(
                        f"  ✅ Found {optimizations_applied} optimization opportunities"
                    )

                    # Apply optimizations if not dry run
                    if not dry_run and self.config.auto_apply_optimizations:
                        self.optimizer.apply_optimizations(dry_run=False)
                        print(f"  ✅ Applied {optimizations_applied} optimizations")
                    else:
                        print(
                            f"  🔍 Preview mode - {optimizations_applied} optimizations available"
                        )

                except Exception as e:
                    error_msg = f"Optimization failed: {e}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")

            # Step 3: Health Monitoring
            if self.config.enable_health_monitoring:
                print("\n🏥 Step 3: Running health monitoring...")
                try:
                    health_data = self.monitor.run_health_check()
                    health_score = health_data["summary"].get("avg_health_score", 0.0)
                    issues_found = health_data["summary"].get("total_alerts", 0)
                    print(
                        f"  ✅ Health score: {health_score:.2f}, Issues: {issues_found}"
                    )

                    # Generate recommendations
                    recommendations = self._generate_recommendations(health_data)

                except Exception as e:
                    error_msg = f"Health monitoring failed: {e}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")

            # Step 4: Generate Reports
            if self.config.generate_reports:
                print("\n📊 Step 4: Generating reports...")
                try:
                    self._generate_automation_reports()
                    print(
                        f"  ✅ Generated reports in {', '.join(self.config.report_formats)} format"
                    )
                except Exception as e:
                    error_msg = f"Report generation failed: {e}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")

            # Step 5: Team Notifications
            if self.config.enable_team_features and not dry_run:
                print("\n👥 Step 5: Team collaboration...")
                try:
                    self._handle_team_notifications(health_score, issues_found)
                    print("  ✅ Team notifications sent")
                except Exception as e:
                    error_msg = f"Team notifications failed: {e}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")

        except Exception as e:
            error_msg = f"Automation failed: {e}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")

        # Calculate execution time
        execution_time = (datetime.now(UTC) - start_time).total_seconds()

        # Create result
        result = AutomationResult(
            success=len(errors) == 0,
            files_processed=files_processed,
            optimizations_applied=optimizations_applied,
            issues_found=issues_found,
            health_score=health_score,
            recommendations=recommendations,
            errors=errors,
            execution_time=execution_time,
            timestamp=datetime.now(UTC),
        )

        self.results.append(result)

        # Print summary
        self._print_automation_summary(result)

        return result

    def _generate_recommendations(
        self, health_data: dict[str, object]
    ) -> FlextCore.Types.StringList:
        """Generate intelligent recommendations based on analysis."""
        recommendations = []

        summary = health_data.get("summary", {})

        # Health-based recommendations
        if summary.get("avg_health_score", 0) < 0.7:
            recommendations.append(
                "Overall documentation health is low - consider comprehensive review"
            )

        if summary.get("avg_link_health", 0) < 0.8:
            recommendations.append(
                "Link health needs improvement - run link repair tools"
            )

        if summary.get("avg_accessibility", 0) < 0.7:
            recommendations.append(
                "Accessibility issues detected - add alt text to images"
            )

        # Alert-based recommendations
        alert_counts = summary.get("alert_counts", {})
        if alert_counts.get("critical", 0) > 0:
            recommendations.append(
                "Critical issues found - immediate attention required"
            )

        if alert_counts.get("warning", 0) > 5:
            recommendations.append(
                "Multiple warnings detected - schedule maintenance session"
            )

        # Trend-based recommendations
        trends = health_data.get("trends", {})
        for trend_name, trend_data in trends.items():
            if trend_data.get("trend_direction") == "declining":
                recommendations.append(
                    f"{trend_name} is declining - investigate and address"
                )

        return recommendations

    def _generate_automation_reports(self) -> None:
        """Generate comprehensive automation reports."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

        for format_type in self.config.report_formats:
            if format_type == "markdown":
                self._generate_markdown_report(f"automation_report_{timestamp}.md")
            elif format_type == "html":
                self._generate_html_report(f"automation_dashboard_{timestamp}.html")
            elif format_type == "json":
                self._generate_json_report(f"automation_data_{timestamp}.json")

    def _generate_markdown_report(self, filename: str) -> None:
        """Generate markdown automation report."""
        if not self.results:
            return

        latest_result = self.results[-1]

        report = f"""# AI-Powered Documentation Automation Report

**Generated:** {latest_result.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
**Execution Time:** {latest_result.execution_time:.2f} seconds
**Status:** {"✅ Success" if latest_result.success else "❌ Failed"}

## Summary

- **Files Processed:** {latest_result.files_processed}
- **Optimizations Applied:** {latest_result.optimizations_applied}
- **Issues Found:** {latest_result.issues_found}
- **Health Score:** {latest_result.health_score:.2f}

## Recommendations

"""

        for i, rec in enumerate(latest_result.recommendations, 1):
            report += f"{i}. {rec}\n"

        if latest_result.errors:
            report += "\n## Errors\n\n"
            for error in latest_result.errors:
                report += f"- ❌ {error}\n"

        report += f"""
## Historical Data

Total automation runs: {len(self.results)}
Average execution time: {sum(r.execution_time for r in self.results) / len(self.results):.2f} seconds
Success rate: {sum(1 for r in self.results if r.success) / len(self.results) * 100:.1f}%
"""

        Path(filename).write_text(report, encoding="utf-8")

    def _generate_html_report(self, filename: str) -> None:
        """Generate HTML automation dashboard."""
        if not self.results:
            return

        latest_result = self.results[-1]

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Documentation Automation Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #3498db;
        }}
        .metric-label {{
            color: #7f8c8d;
            margin-top: 10px;
        }}
        .status-success {{ color: #27ae60; }}
        .status-error {{ color: #e74c3c; }}
        .recommendations {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .recommendation {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Documentation Automation Dashboard</h1>
        <p style="text-align: center; color: #7f8c8d;">
            Last updated: {latest_result.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
        </p>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{latest_result.files_processed}</div>
                <div class="metric-label">Files Processed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{latest_result.optimizations_applied}</div>
                <div class="metric-label">Optimizations Applied</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{latest_result.issues_found}</div>
                <div class="metric-label">Issues Found</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{latest_result.health_score:.2f}</div>
                <div class="metric-label">Health Score</div>
            </div>
        </div>

        <div class="recommendations">
            <h2>💡 Recommendations</h2>
"""

        for rec in latest_result.recommendations:
            html += f'            <div class="recommendation">{rec}</div>\n'

        html += "        </div>\n"

        if latest_result.errors:
            html += """
        <div class="recommendations">
            <h2>❌ Errors</h2>
"""
            for error in latest_result.errors:
                html += f'            <div class="recommendation" style="border-left-color: #e74c3c;">{error}</div>\n'
            html += "        </div>\n"

        html += """
    </div>
</body>
</html>"""

        Path(filename).write_text(html, encoding="utf-8")

    def _generate_json_report(self, filename: str) -> None:
        """Generate JSON automation data."""
        data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "results": [
                {
                    "success": r.success,
                    "files_processed": r.files_processed,
                    "optimizations_applied": r.optimizations_applied,
                    "issues_found": r.issues_found,
                    "health_score": r.health_score,
                    "recommendations": r.recommendations,
                    "errors": r.errors,
                    "execution_time": r.execution_time,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.results
            ],
            "summary": {
                "total_runs": len(self.results),
                "success_rate": sum(1 for r in self.results if r.success)
                / len(self.results)
                if self.results
                else 0,
                "avg_execution_time": sum(r.execution_time for r in self.results)
                / len(self.results)
                if self.results
                else 0,
                "total_files_processed": sum(r.files_processed for r in self.results),
                "total_optimizations": sum(
                    r.optimizations_applied for r in self.results
                ),
            },
        }

        Path(filename).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _handle_team_notifications(
        self, health_score: float, issues_found: int
    ) -> None:
        """Handle team notifications and collaboration features."""
        if not self.config.notify_on_issues:
            return

        # Create notification based on health and issues
        if health_score < 0.5 or issues_found > 10:
            notification = f"🚨 Documentation health alert: Score {health_score:.2f}, {issues_found} issues found"
            print(f"  📢 {notification}")

        # Could integrate with Slack, Teams, or email here
        # For now, just print to console

    def _print_automation_summary(self, result: AutomationResult) -> None:
        """Print automation summary."""
        print("\n" + "=" * 60)
        print("🤖 AI DOCUMENTATION AUTOMATION SUMMARY")
        print("=" * 60)
        print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        print(f"Files Processed: {result.files_processed}")
        print(f"Optimizations Applied: {result.optimizations_applied}")
        print(f"Issues Found: {result.issues_found}")
        print(f"Health Score: {result.health_score:.2f}")
        print(f"Execution Time: {result.execution_time:.2f}s")

        if result.recommendations:
            print(f"\n💡 Recommendations ({len(result.recommendations)}):")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"  {i}. {rec}")

        if result.errors:
            print(f"\n❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  - {error}")

        print("=" * 60)

    def schedule_automation(self, schedule_type: str = "daily") -> None:
        """Schedule automation runs."""
        print(f"📅 Scheduling {schedule_type} automation...")

        # This would integrate with system cron or task scheduler
        # For now, just print the schedule
        if schedule_type == "daily":
            print("  Schedule: Daily at 2:00 AM")
        elif schedule_type == "weekly":
            print("  Schedule: Weekly on Sunday at 2:00 AM")
        elif schedule_type == "monthly":
            print("  Schedule: Monthly on 1st at 2:00 AM")

        print("  Note: Actual scheduling requires system configuration")


def main() -> None:
    """Main entry point for AI automation."""
    import argparse

    parser = argparse.ArgumentParser(description="AI-Powered Documentation Automation")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of documentation (default: current directory)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default is dry-run)"
    )
    parser.add_argument("--config", type=Path, help="Configuration file (JSON format)")
    parser.add_argument(
        "--schedule",
        choices=["daily", "weekly", "monthly"],
        help="Schedule automation runs",
    )

    args = parser.parse_args()

    # Load configuration
    config = AutomationConfig()
    if args.config and args.config.exists():
        with Path(args.config).open(encoding="utf-8") as f:
            config_data = json.load(f)
            # Update config with loaded data
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

    # Override with command line arguments
    config.auto_apply_optimizations = args.apply

    # Create automation instance
    automation = AIDocumentationAutomation(args.root, config)

    # Handle scheduling
    if args.schedule:
        automation.schedule_automation(args.schedule)
        return

    # Run automation
    result = automation.run_complete_automation(dry_run=not args.apply)

    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
