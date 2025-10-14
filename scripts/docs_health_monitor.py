#!/usr/bin/env python3
"""Documentation Health Monitor & Dashboard.

Real-time documentation health monitoring with:
- Health scoring and trending
- Automated alerts and notifications
- Performance metrics tracking
- Quality trend analysis
- Team productivity insights
- Documentation ROI metrics
"""

import json
import statistics
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from flext_core import FlextCore

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required dependencies...")
    import subprocess

    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "requests",
        "beautifulsoup4",
    ])


@dataclass
class HealthMetric:
    """Individual health metric."""

    name: str
    value: float
    target: float
    status: str  # 'excellent', 'good', 'warning', 'critical'
    trend: str  # 'improving', 'stable', 'declining'
    last_updated: datetime


@dataclass
class HealthScore:
    """Overall health score for documentation."""

    overall_score: float
    content_quality: float
    structure_quality: float
    link_health: float
    accessibility_score: float
    freshness_score: float
    completeness_score: float
    maintainability_score: float
    timestamp: datetime


@dataclass
class Alert:
    """Health alert."""

    severity: str  # 'info', 'warning', 'critical'
    category: str
    message: str
    file_path: Path | None
    recommendation: str
    timestamp: datetime


@dataclass
class TrendData:
    """Trend analysis data."""

    metric_name: str
    values: FlextCore.Types.FloatList
    timestamps: list[datetime]
    trend_direction: str
    trend_strength: float
    forecast: float | None


class DocumentationHealthMonitor:
    """Real-time documentation health monitoring system."""

    def __init__(
        self, root_path: Path, config: dict[str, object] | None = None
    ) -> None:
        self.root_path = root_path
        self.config = config or self._default_config()
        self.health_scores: list[HealthScore] = []
        self.alerts: list[Alert] = []
        self.trends: dict[str, TrendData] = {}
        self.metrics_history: dict[str, list[tuple[datetime, float]]] = {}

    def _default_config(self) -> dict[str, object]:
        """Default configuration for health monitoring."""
        return {
            "health_thresholds": {
                "excellent": 0.9,
                "good": 0.7,
                "warning": 0.5,
                "critical": 0.3,
            },
            "alert_thresholds": {
                "link_health": 0.8,
                "accessibility": 0.7,
                "freshness_days": 90,
                "completeness": 0.6,
            },
            "trend_analysis": {"min_data_points": 5, "trend_window_days": 30},
            "monitoring": {
                "enable_real_time": True,
                "check_interval_minutes": 60,
                "enable_alerts": True,
                "enable_trends": True,
            },
        }

    def calculate_health_score(self, file_path: Path, content: str) -> HealthScore:
        """Calculate comprehensive health score for a document."""
        # Content quality metrics
        word_count = len(content.split())
        sentence_count = len([s for s in content.split(".") if s.strip()])
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Readability score (simplified Flesch-Kincaid)
        readability_score = max(0, 100 - (avg_sentence_length * 1.5))

        # Structure quality
        headings = len([
            line for line in content.split("\n") if line.strip().startswith("#")
        ])
        lists = len([
            line
            for line in content.split("\n")
            if line.strip().startswith(("-", "*", "+"))
        ])
        code_blocks = len([
            line for line in content.split("\n") if line.strip().startswith("```")
        ])

        structure_score = min(
            1.0, (headings + lists + code_blocks) / max(word_count / 100, 1)
        )

        # Link health
        links = self._extract_links(content)
        broken_links = self._check_broken_links(file_path, links)
        link_health = 1.0 - (broken_links / max(len(links), 1))

        # Accessibility score
        images = self._extract_images(content)
        images_with_alt = len([
            img for img in images if img.get("alt_text", "").strip()
        ])
        accessibility_score = images_with_alt / max(len(images), 1) if images else 1.0

        # Freshness score
        file_age_days = (
            datetime.now(UTC) - datetime.fromtimestamp(file_path.stat().st_mtime)
        ).days
        freshness_score = max(0, 1.0 - (file_age_days / 365))

        # Completeness score
        completeness_score = min(1.0, word_count / 500)  # Assume 500 words is complete

        # Maintainability score (based on structure and organization)
        maintainability_score = (
            structure_score * 0.4
            + (1.0 - (len(content.split("\n")) / 1000))
            * 0.3  # Penalize very long files
            + (1.0 - (len(content) / 10000)) * 0.3  # Penalize very long content
        )

        # Overall score (weighted average)
        overall_score = (
            readability_score / 100 * 0.2
            + structure_score * 0.2
            + link_health * 0.2
            + accessibility_score * 0.15
            + freshness_score * 0.1
            + completeness_score * 0.1
            + maintainability_score * 0.05
        )

        return HealthScore(
            overall_score=overall_score,
            content_quality=readability_score / 100,
            structure_quality=structure_score,
            link_health=link_health,
            accessibility_score=accessibility_score,
            freshness_score=freshness_score,
            completeness_score=completeness_score,
            maintainability_score=maintainability_score,
            timestamp=datetime.now(UTC),
        )

    def _extract_links(self, content: str) -> list[dict[str, str]]:
        """Extract all links from content."""
        import re

        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        return [
            {
                "text": match.group(1),
                "url": match.group(2),
                "line": content[: match.start()].count("\n") + 1,
            }
            for match in re.finditer(link_pattern, content)
        ]

    def _extract_images(self, content: str) -> list[dict[str, str]]:
        """Extract all images from content."""
        import re

        image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

        return [
            {
                "alt_text": match.group(1),
                "url": match.group(2),
                "line": content[: match.start()].count("\n") + 1,
            }
            for match in re.finditer(image_pattern, content)
        ]

    def _check_broken_links(self, file_path: Path, links: list[dict[str, str]]) -> int:
        """Check for broken links."""
        broken_count = 0

        for link in links:
            url = link["url"]

            # Skip external links
            if url.startswith(("http://", "https://")):
                continue

            # Check internal links
            if url.startswith(("./", "../")):
                target_path = file_path.parent / url
            else:
                target_path = self.root_path / url.lstrip("/")

            if not target_path.exists():
                broken_count += 1

        return broken_count

    def generate_alerts(
        self, health_score: HealthScore, file_path: Path
    ) -> list[Alert]:
        """Generate health alerts based on score."""
        alerts = []
        thresholds = self.config["alert_thresholds"]

        # Link health alert
        if health_score.link_health < thresholds["link_health"]:
            alerts.append(
                Alert(
                    severity="warning",
                    category="link_health",
                    message=f"Low link health: {health_score.link_health:.2f}",
                    file_path=file_path,
                    recommendation="Fix broken links to improve navigation",
                    timestamp=datetime.now(UTC),
                )
            )

        # Accessibility alert
        if health_score.accessibility_score < thresholds["accessibility"]:
            alerts.append(
                Alert(
                    severity="warning",
                    category="accessibility",
                    message=f"Poor accessibility: {health_score.accessibility_score:.2f}",
                    file_path=file_path,
                    recommendation="Add alt text to images for better accessibility",
                    timestamp=datetime.now(UTC),
                )
            )

        # Freshness alert
        if health_score.freshness_score < 0.5:  # More than 6 months old
            alerts.append(
                Alert(
                    severity="info",
                    category="freshness",
                    message="Document appears stale",
                    file_path=file_path,
                    recommendation="Review and update content",
                    timestamp=datetime.now(UTC),
                )
            )

        # Completeness alert
        if health_score.completeness_score < thresholds["completeness"]:
            alerts.append(
                Alert(
                    severity="info",
                    category="completeness",
                    message="Document may be incomplete",
                    file_path=file_path,
                    recommendation="Add more content to improve completeness",
                    timestamp=datetime.now(UTC),
                )
            )

        # Critical health alert
        if health_score.overall_score < self.config["health_thresholds"]["critical"]:
            alerts.append(
                Alert(
                    severity="critical",
                    category="overall_health",
                    message=f"Critical health score: {health_score.overall_score:.2f}",
                    file_path=file_path,
                    recommendation="Immediate attention required",
                    timestamp=datetime.now(UTC),
                )
            )

        return alerts

    def analyze_trends(self) -> dict[str, TrendData]:
        """Analyze trends in health metrics."""
        trends = {}

        for metric_name, history in self.metrics_history.items():
            if len(history) < self.config["trend_analysis"]["min_data_points"]:
                continue

            # Extract values and timestamps
            values = [value for _, value in history]
            timestamps = [ts for ts, _ in history]

            # Calculate trend direction
            if len(values) >= 2:
                trend_direction = "improving" if values[-1] > values[0] else "declining"
                trend_strength = abs(values[-1] - values[0]) / max(values[0], 0.001)
            else:
                trend_direction = "stable"
                trend_strength = 0.0

            # Simple forecast (linear extrapolation)
            forecast = None
            if len(values) >= 2:
                slope = (values[-1] - values[0]) / len(values)
                forecast = values[-1] + slope

            trends[metric_name] = TrendData(
                metric_name=metric_name,
                values=values,
                timestamps=timestamps,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                forecast=forecast,
            )

        return trends

    def update_metrics_history(self, health_score: HealthScore) -> None:
        """Update metrics history for trend analysis."""
        timestamp = health_score.timestamp

        metrics = {
            "overall_score": health_score.overall_score,
            "content_quality": health_score.content_quality,
            "structure_quality": health_score.structure_quality,
            "link_health": health_score.link_health,
            "accessibility_score": health_score.accessibility_score,
            "freshness_score": health_score.freshness_score,
            "completeness_score": health_score.completeness_score,
            "maintainability_score": health_score.maintainability_score,
        }

        for metric_name, value in metrics.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []

            self.metrics_history[metric_name].append((timestamp, value))

            # Keep only recent history
            cutoff_date = timestamp - timedelta(
                days=self.config["trend_analysis"]["trend_window_days"]
            )
            self.metrics_history[metric_name] = [
                (ts, val)
                for ts, val in self.metrics_history[metric_name]
                if ts >= cutoff_date
            ]

    def run_health_check(self) -> dict[str, object]:
        """Run comprehensive health check."""
        print("🏥 Running Documentation Health Check...")

        markdown_files = list(self.root_path.rglob("*.md"))
        print(f"Found {len(markdown_files)} markdown files")

        health_scores = []
        all_alerts = []

        for idx, file_path in enumerate(markdown_files, 1):
            print(
                f"[{idx}/{len(markdown_files)}] Checking: {file_path.relative_to(self.root_path)}"
            )

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                health_score = self.calculate_health_score(file_path, content)
                health_scores.append(health_score)

                # Generate alerts
                alerts = self.generate_alerts(health_score, file_path)
                all_alerts.extend(alerts)

                # Update metrics history
                self.update_metrics_history(health_score)

            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")

        # Analyze trends
        if self.config["monitoring"]["enable_trends"]:
            self.trends = self.analyze_trends()

        # Store results
        self.health_scores = health_scores
        self.alerts = all_alerts

        # Generate summary
        summary = self._generate_health_summary(health_scores, all_alerts)

        print("\n✅ Health check complete!")
        print(f"  - Files checked: {len(health_scores)}")
        print(f"  - Alerts generated: {len(all_alerts)}")
        print(f"  - Average health score: {summary['avg_health_score']:.2f}")

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "health_scores": health_scores,
            "alerts": all_alerts,
            "trends": self.trends,
            "summary": summary,
        }

    def _generate_health_summary(
        self, health_scores: list[HealthScore], alerts: list[Alert]
    ) -> dict[str, object]:
        """Generate health summary statistics."""
        if not health_scores:
            return {}

        # Calculate averages
        avg_health_score = statistics.mean([hs.overall_score for hs in health_scores])
        avg_content_quality = statistics.mean([
            hs.content_quality for hs in health_scores
        ])
        avg_structure_quality = statistics.mean([
            hs.structure_quality for hs in health_scores
        ])
        avg_link_health = statistics.mean([hs.link_health for hs in health_scores])
        avg_accessibility = statistics.mean([
            hs.accessibility_score for hs in health_scores
        ])
        avg_freshness = statistics.mean([hs.freshness_score for hs in health_scores])
        avg_completeness = statistics.mean([
            hs.completeness_score for hs in health_scores
        ])
        avg_maintainability = statistics.mean([
            hs.maintainability_score for hs in health_scores
        ])

        # Count alerts by severity
        alert_counts = {
            "critical": len([a for a in alerts if a.severity == "critical"]),
            "warning": len([a for a in alerts if a.severity == "warning"]),
            "info": len([a for a in alerts if a.severity == "info"]),
        }

        # Health distribution
        health_distribution = {
            "excellent": len([hs for hs in health_scores if hs.overall_score >= 0.9]),
            "good": len([hs for hs in health_scores if 0.7 <= hs.overall_score < 0.9]),
            "warning": len([
                hs for hs in health_scores if 0.5 <= hs.overall_score < 0.7
            ]),
            "critical": len([hs for hs in health_scores if hs.overall_score < 0.5]),
        }

        return {
            "avg_health_score": avg_health_score,
            "avg_content_quality": avg_content_quality,
            "avg_structure_quality": avg_structure_quality,
            "avg_link_health": avg_link_health,
            "avg_accessibility": avg_accessibility,
            "avg_freshness": avg_freshness,
            "avg_completeness": avg_completeness,
            "avg_maintainability": avg_maintainability,
            "alert_counts": alert_counts,
            "health_distribution": health_distribution,
            "total_files": len(health_scores),
            "total_alerts": len(alerts),
        }

    def generate_health_dashboard(self) -> str:
        """Generate HTML health dashboard."""
        if not self.health_scores:
            return "<html><body><h1>No health data available</h1></body></html>"

        summary = self._generate_health_summary(self.health_scores, self.alerts)

        # Generate HTML dashboard
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLEXT Documentation Health Dashboard</title>
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
        .health-distribution {{
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
        }}
        .health-category {{
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
        }}
        .excellent {{ background: #27ae60; }}
        .good {{ background: #3498db; }}
        .warning {{ background: #f39c12; }}
        .critical {{ background: #e74c3c; }}
        .alerts-section {{
            margin: 30px 0;
        }}
        .alert {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 5px solid;
        }}
        .alert-critical {{ background: #fdf2f2; border-color: #e74c3c; }}
        .alert-warning {{ background: #fef9e7; border-color: #f39c12; }}
        .alert-info {{ background: #e8f4fd; border-color: #3498db; }}
        .trends-section {{
            margin: 30px 0;
        }}
        .trend-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            margin: 5px 0;
            border-radius: 5px;
        }}
        .trend-improving {{ color: #27ae60; }}
        .trend-declining {{ color: #e74c3c; }}
        .trend-stable {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 FLEXT Documentation Health Dashboard</h1>
        <p style="text-align: center; color: #7f8c8d;">
            Last updated: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}
        </p>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{summary["avg_health_score"]:.2f}</div>
                <div class="metric-label">Overall Health Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary["total_files"]}</div>
                <div class="metric-label">Total Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary["total_alerts"]}</div>
                <div class="metric-label">Total Alerts</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{summary["avg_link_health"]:.2f}</div>
                <div class="metric-label">Link Health</div>
            </div>
        </div>

        <div class="health-distribution">
            <div class="health-category excellent">
                <div style="font-size: 2em;">{summary["health_distribution"]["excellent"]}</div>
                <div>Excellent</div>
            </div>
            <div class="health-category good">
                <div style="font-size: 2em;">{summary["health_distribution"]["good"]}</div>
                <div>Good</div>
            </div>
            <div class="health-category warning">
                <div style="font-size: 2em;">{summary["health_distribution"]["warning"]}</div>
                <div>Warning</div>
            </div>
            <div class="health-category critical">
                <div style="font-size: 2em;">{summary["health_distribution"]["critical"]}</div>
                <div>Critical</div>
            </div>
        </div>

        <div class="alerts-section">
            <h2>🚨 Recent Alerts</h2>
"""

        # Add alerts
        for alert in self.alerts[:10]:  # Show first 10 alerts
            severity_class = f"alert-{alert.severity}"
            file_name = alert.file_path.name if alert.file_path else "Unknown"
            html += f"""
            <div class="alert {severity_class}">
                <strong>{alert.severity.upper()}</strong> - {alert.message}
                <br><small>File: {file_name} | {alert.recommendation}</small>
            </div>
"""

        html += """
        </div>

        <div class="trends-section">
            <h2>📈 Trends</h2>
"""

        # Add trends
        for metric_name, trend in self.trends.items():
            trend_class = f"trend-{trend.trend_direction}"
            html += f"""
            <div class="trend-item">
                <span>{metric_name.replace("_", " ").title()}</span>
                <span class="{trend_class}">
                    {trend.trend_direction.title()}
                    ({trend.trend_strength:.2f})
                </span>
            </div>
"""

        html += """
        </div>
    </div>
</body>
</html>"""

        return html

    def save_health_data(self, output_path: Path) -> None:
        """Save health data to file."""
        health_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "health_scores": [
                {
                    "file_path": str(
                        hs.overall_score
                    ),  # Simplified for JSON serialization
                    "overall_score": hs.overall_score,
                    "content_quality": hs.content_quality,
                    "structure_quality": hs.structure_quality,
                    "link_health": hs.link_health,
                    "accessibility_score": hs.accessibility_score,
                    "freshness_score": hs.freshness_score,
                    "completeness_score": hs.completeness_score,
                    "maintainability_score": hs.maintainability_score,
                    "timestamp": hs.timestamp.isoformat(),
                }
                for hs in self.health_scores
            ],
            "alerts": [
                {
                    "severity": alert.severity,
                    "category": alert.category,
                    "message": alert.message,
                    "file_path": str(alert.file_path) if alert.file_path else None,
                    "recommendation": alert.recommendation,
                    "timestamp": alert.timestamp.isoformat(),
                }
                for alert in self.alerts
            ],
            "trends": {
                name: {
                    "metric_name": trend.metric_name,
                    "values": trend.values,
                    "timestamps": [ts.isoformat() for ts in trend.timestamps],
                    "trend_direction": trend.trend_direction,
                    "trend_strength": trend.trend_strength,
                    "forecast": trend.forecast,
                }
                for name, trend in self.trends.items()
            },
            "summary": self._generate_health_summary(self.health_scores, self.alerts),
        }

        output_path.write_text(json.dumps(health_data, indent=2), encoding="utf-8")


def main() -> None:
    """Main entry point for health monitoring."""
    import argparse

    parser = argparse.ArgumentParser(description="Documentation Health Monitor")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of documentation (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("health_dashboard.html"),
        help="Output file for health dashboard",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("health_data.json"),
        help="Output file for health data",
    )
    parser.add_argument(
        "--format", choices=["html", "json"], default="html", help="Output format"
    )

    args = parser.parse_args()

    # Run health check
    monitor = DocumentationHealthMonitor(args.root)
    health_data = monitor.run_health_check()

    # Generate dashboard
    if args.format == "html":
        dashboard = monitor.generate_health_dashboard()
        args.output.write_text(dashboard, encoding="utf-8")
        print(f"\n📊 Health dashboard saved to: {args.output}")
    else:
        # Save as JSON
        args.output.write_text(json.dumps(health_data, indent=2), encoding="utf-8")
        print(f"\n📊 Health data saved to: {args.output}")

    # Save detailed data
    monitor.save_health_data(args.data)
    print(f"📊 Detailed health data saved to: {args.data}")


if __name__ == "__main__":
    main()
