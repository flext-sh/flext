"""Monitoring automation module for PyAuto enterprise workspace.

This module handles automated monitoring, alerting, performance tracking,
and system health visualization across all projects.
"""

import json
import subprocess
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
import yaml
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from .base import CustomFixModule, Issue, Severity

console = Console()


class MonitoringAutomationModule(CustomFixModule):
    """Module for automating monitoring and alerting tasks."""

    name = "monitoring_automation"
    description = "Automated monitoring, alerting, and performance tracking"

    def __init__(
        self,
        dry_run: bool = True,
        interactive: bool = False,
        verbose: bool = False,
    ):
        """Initialize monitoring automation module.

        Args:
            dry_run: If True, only simulate operations
            interactive: If True, prompt for confirmations
            verbose: If True, show detailed output
        """
        super().__init__(dry_run, interactive, verbose)
        self.metrics: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.alerts: list[dict[str, Any]] = []
        self.thresholds: dict[str, Any] = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
        }

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze monitoring configuration files.

        Args:
            file_path: Path to file being analyzed
            content: File content

        Returns:
            List of monitoring-related issues found
        """
        issues: list = []

        # Check monitoring configuration files
        if file_path.name in ["monitoring.yaml", "monitoring.yml", "alerts.yaml"]:
            issues.extend(self._analyze_monitoring_config(file_path, content))
        elif file_path.name == "prometheus.yml":
            issues.extend(self._analyze_prometheus_config(file_path, content))
        elif file_path.name == "grafana.json":
            issues.extend(self._analyze_grafana_dashboard(file_path, content))
        elif "logging" in file_path.name and file_path.suffix in [
            ".yaml",
            ".yml",
            ".json",
        ]:
            issues.extend(self._analyze_logging_config(file_path, content))

        return issues

    def _analyze_monitoring_config(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze monitoring configuration."""
        issues: list = []
        try:
            config = yaml.safe_load(content)

            # Check for required monitoring fields
            if "metrics" not in config:
                issues.append(
                    Issue(
                        severity=Severity.HIGH,
                        message="Missing metrics configuration",
                        file_path=file_path,
                        line=None,
                        fix_description="Add metrics collection configuration",
                    ),
                )

            if "alerts" not in config:
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        message="Missing alerts configuration",
                        file_path=file_path,
                        line=None,
                        fix_description="Add alert rules configuration",
                    ),
                )

            # Check alert rules
            if "alerts" in config:
                for alert in config["alerts"]:
                    if "threshold" not in alert:
                        issues.append(
                            Issue(
                                severity=Severity.MEDIUM,
                                message=f"Alert '{
                                    alert.get('name', 'unknown')
                                }' missing threshold",
                                file_path=file_path,
                                line=None,
                                fix_description="Add threshold value to alert rule",
                            ),
                        )

                    if "action" not in alert:
                        issues.append(
                            Issue(
                                severity=Severity.LOW,
                                message=f"Alert '{
                                    alert.get('name', 'unknown')
                                }' missing action",
                                file_path=file_path,
                                line=None,
                                fix_description="Define action for alert (email, webhook, etc)",
                            ),
                        )
        except yaml.YAMLError as e:
            issues.append(
                Issue(
                    severity=Severity.HIGH,
                    message=f"Invalid YAML in monitoring config: {e}",
                    file_path=file_path,
                    line=None,
                    fix_description="Fix YAML syntax errors",
                ),
            )

        return issues

    def _analyze_prometheus_config(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze Prometheus configuration."""
        issues: list = []
        try:
            config = yaml.safe_load(content)

            # Check scrape configs
            if "scrape_configs" not in config:
                issues.append(
                    Issue(
                        severity=Severity.HIGH,
                        message="Missing scrape_configs in Prometheus config",
                        file_path=file_path,
                        line=None,
                        fix_description="Add scrape configurations",
                    ),
                )
                for job in config["scrape_configs"]:
                    if "job_name" not in job:
                        issues.append(
                            Issue(
                                severity=Severity.HIGH,
                                message="Scrape job missing job_name",
                                file_path=file_path,
                                line=None,
                                fix_description="Add job_name to scrape configuration",
                            ),
                        )

                    if (
                        "static_configs" not in job
                        and "kubernetes_sd_configs" not in job
                    ):
                        issues.append(
                            Issue(
                                severity=Severity.MEDIUM,
                                message=f"Job '{
                                    job.get('job_name', 'unknown')
                                }' missing target configuration",
                                file_path=file_path,
                                line=None,
                                fix_description="Add static_configs or service discovery",
                            ),
                        )
        except yaml.YAMLError as e:
            issues.append(
                Issue(
                    severity=Severity.HIGH,
                    message=f"Invalid YAML in Prometheus config: {e}",
                    file_path=file_path,
                    line=None,
                    fix_description="Fix YAML syntax errors",
                ),
            )

        return issues

    def _analyze_grafana_dashboard(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze Grafana dashboard configuration."""
        issues: list = []
        try:
            dashboard = json.loads(content)

            # Check for required dashboard fields
            if "panels" not in dashboard:
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        message="Dashboard missing panels",
                        file_path=file_path,
                        line=None,
                        fix_description="Add visualization panels to dashboard",
                    ),
                )

            if "templating" not in dashboard:
                issues.append(
                    Issue(
                        severity=Severity.LOW,
                        message="Dashboard missing templating variables",
                        file_path=file_path,
                        line=None,
                        fix_description="Add template variables for flexibility",
                    ),
                )

            # Check panels
            if "panels" in dashboard:
                for i, panel in enumerate(dashboard["panels"]):
                    if "datasource" not in panel:
                        issues.append(
                            Issue(
                                severity=Severity.HIGH,
                                message=f"Panel {i} missing datasource",
                                file_path=file_path,
                                line=None,
                                fix_description="Configure datasource for panel",
                            ),
                        )
        except json.JSONDecodeError as e:
            issues.append(
                Issue(
                    severity=Severity.HIGH,
                    message=f"Invalid JSON in Grafana dashboard: {e}",
                    file_path=file_path,
                    line=None,
                    fix_description="Fix JSON syntax errors",
                ),
            )

        return issues

    def _analyze_logging_config(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze logging configuration."""
        issues: list = []

        if file_path.suffix == ".json":
            try:
                config = json.loads(content)
            except json.JSONDecodeError:
                issues.append(
                    Issue(
                        severity=Severity.HIGH,
                        message="Invalid JSON in logging config",
                        file_path=file_path,
                        line=None,
                        fix_description="Fix JSON syntax errors",
                    ),
                )
                return issues
            try:
                config = yaml.safe_load(content)
            except yaml.YAMLError:
                issues.append(
                    Issue(
                        severity=Severity.HIGH,
                        message="Invalid YAML in logging config",
                        file_path=file_path,
                        line=None,
                        fix_description="Fix YAML syntax errors",
                    ),
                )
                return issues

        # Check logging levels
        if "level" not in config and "root" not in config:
            issues.append(
                Issue(
                    severity=Severity.MEDIUM,
                    message="No root logging level configured",
                    file_path=file_path,
                    line=None,
                    fix_description="Set root logging level",
                ),
            )

        # Check handlers
        if "handlers" not in config:
            issues.append(
                Issue(
                    severity=Severity.MEDIUM,
                    message="No logging handlers configured",
                    file_path=file_path,
                    line=None,
                    fix_description="Configure logging handlers (console, file, etc)",
                ),
            )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply monitoring-related fixes to content.

        Args:
            content: Original file content
            issues: List of issues to fix

        Returns:
            Fixed content
        """
        # Monitoring configs typically require manual configuration
        return content

    def collect_metrics(self, project_path: Path) -> dict[str, Any]:
        """Collect system and application metrics.

        Args:
            project_path: Path to project directory

        Returns:
            Dictionary of collected metrics
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "project": project_path.name,
            "system": self._collect_system_metrics(),
            "application": self._collect_application_metrics(project_path),
        }

        # Store metrics
        self.metrics[project_path.name].append(metrics)

        # Check thresholds and generate alerts
        self._check_thresholds(metrics)

        return metrics

    def _collect_system_metrics(self) -> dict[str, Any]:
        """Collect system-level metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available_gb": psutil.virtual_memory().available / (1024**3),
                "total_gb": psutil.virtual_memory().total / (1024**3),
            },
            "disk": {
                "percent": psutil.disk_usage("/").percent,
                "free_gb": psutil.disk_usage("/").free / (1024**3),
                "total_gb": psutil.disk_usage("/").total / (1024**3),
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
            },
        }

    def _collect_application_metrics(self, project_path: Path) -> dict[str, Any]:
        """Collect application-specific metrics."""
        metrics = {
            "status": "unknown",
            "response_time_ms": None,
            "error_count": 0,
            "request_count": 0,
        }

        # Check if project has metrics endpoint
        metrics_script = project_path / "scripts" / "collect_metrics.py"
        if metrics_script.exists():
            try:
                result = subprocess.run(
                    ["python", str(metrics_script)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0:
                    metrics.update(json.loads(result.stdout))
            except Exception:
                pass

        # Simulate metrics for demo
        import random

        metrics["status"] = "healthy"
        metrics["response_time_ms"] = random.randint(50, 500)
        metrics["error_count"] = random.randint(0, 10)
        metrics["request_count"] = random.randint(100, 1000)

        return metrics

    def _check_thresholds(self, metrics: dict[str, Any]) -> None:
        """Check metrics against thresholds and generate alerts."""
        # Check system metrics
        system = metrics["system"]
        if system["cpu_percent"] > self.thresholds["cpu_percent"]:
            self._create_alert(
                severity="high",
                metric="cpu_percent",
                value=system["cpu_percent"],
                threshold=self.thresholds["cpu_percent"],
                project=metrics["project"],
            )

        if system["memory"]["percent"] > self.thresholds["memory_percent"]:
            self._create_alert(
                severity="high",
                metric="memory_percent",
                value=system["memory"]["percent"],
                threshold=self.thresholds["memory_percent"],
                project=metrics["project"],
            )

        if system["disk"]["percent"] > self.thresholds["disk_percent"]:
            self._create_alert(
                severity="medium",
                metric="disk_percent",
                value=system["disk"]["percent"],
                threshold=self.thresholds["disk_percent"],
                project=metrics["project"],
            )

        # Check application metrics
        app = metrics["application"]
        if (
            app["response_time_ms"]
            and app["response_time_ms"] > self.thresholds["response_time_ms"]
        ):
            self._create_alert(
                severity="medium",
                metric="response_time_ms",
                value=app["response_time_ms"],
                threshold=self.thresholds["response_time_ms"],
                project=metrics["project"],
            )

        if app["request_count"] > 0:
            error_rate = (app["error_count"] / app["request_count"]) * 100
            if error_rate > self.thresholds["error_rate_percent"]:
                self._create_alert(
                    severity="high",
                    metric="error_rate_percent",
                    value=error_rate,
                    threshold=self.thresholds["error_rate_percent"],
                    project=metrics["project"],
                )

    def _create_alert(
        self,
        severity: str,
        metric: str,
        value: float,
        threshold: float,
        project: str,
    ) -> None:
        """Create an alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "project": project,
            "message": f"{metric} exceeded threshold: {value:.2f} > {threshold:.2f}",
        }
        self.alerts.append(alert)

        if not self.dry_run:
            # Send actual alert (email, webhook, etc)
            if severity == "high":
                console.print(
                    f"[red]⚠ HIGH ALERT: {alert['message']} for {project}[/red]",
                )
                console.print(
                    f"[yellow]⚠ ALERT: {alert['message']} for {project}[/yellow]",
                )

    def start_monitoring_dashboard(self, projects: list[Path]) -> None:
        """Start live monitoring dashboard.

        Args:
            projects: List of project paths to monitor
        """

        def generate_dashboard() -> Layout:
            """Generate dashboard layout."""
            layout = Layout()

            # Create main sections
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body"),
                Layout(name="footer", size=4),
            )

            # Header
            layout["header"].update(
                Panel(
                    f"[bold cyan]PyAuto Monitoring Dashboard[/bold cyan] - {
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }",
                    border_style="cyan",
                ),
            )

            # Body - split into metrics and alerts
            layout["body"].split_row(
                Layout(name="metrics", ratio=2),
                Layout(name="alerts", ratio=1),
            )

            # Metrics table
            metrics_table = Table(title="System Metrics")
            metrics_table.add_column("Project", style="cyan")
            metrics_table.add_column("CPU %", style="green")
            metrics_table.add_column("Memory %", style="yellow")
            metrics_table.add_column("Response Time", style="blue")
            metrics_table.add_column("Status", style="magenta")

            for project in projects[:5]:  # Show top 5
                # Get latest metrics
                if self.metrics.get(project.name):
                    latest = self.metrics[project.name][-1]
                    cpu = latest["system"]["cpu_percent"]
                    mem = latest["system"]["memory"]["percent"]
                    resp_time = latest["application"]["response_time_ms"] or 0
                    status = latest["application"]["status"]

                    # Color code based on thresholds
                    cpu_style = "red" if cpu > 80 else "yellow" if cpu > 60 else "green"
                    mem_style = "red" if mem > 85 else "yellow" if mem > 70 else "green"

                    metrics_table.add_row(
                        project.name[:20],
                        f"[{cpu_style}]{cpu:.1f}[/{cpu_style}]",
                        f"[{mem_style}]{mem:.1f}[/{mem_style}]",
                        f"{resp_time}ms",
                        "[green]✓[/green]" if status == "healthy" else "[red]✗[/red]",
                    )

            layout["metrics"].update(
                Panel(metrics_table, title="Live Metrics", border_style="green"),
            )

            # Alerts panel
            alerts_text = ""
            recent_alerts = self.alerts[-10:]  # Show last 10 alerts
            for alert in reversed(recent_alerts):
                time_str = datetime.fromisoformat(alert["timestamp"]).strftime(
                    "%H:%M:%S",
                )
                severity_color = "red" if alert["severity"] == "high" else "yellow"
                alerts_text += f"[{severity_color}]{time_str} - {alert['message']}[/{severity_color}]\n"

            if not alerts_text:
                alerts_text = "[green]No active alerts[/green]"

            layout["alerts"].update(
                Panel(alerts_text, title="Recent Alerts", border_style="yellow"),
            )

            # Footer - resource usage
            layout["footer"].update(
                Panel(
                    self._get_resource_usage_text(),
                    title="Resource Usage",
                    border_style="blue",
                ),
            )

            return layout

        # Run live dashboard
        with Live(generate_dashboard(), refresh_per_second=1, console=console) as live:
            try:
                while True:
                    # Collect metrics for all projects
                    for project in projects:
                        self.collect_metrics(project)

                    # Update display
                    live.update(generate_dashboard())

                    # Wait before next update
                    time.sleep(5)
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped by user[/yellow]")

    def _get_resource_usage_text(self) -> str:
        """Get formatted resource usage text."""
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Create progress bars
        cpu_bar = self._create_usage_bar(cpu, 100, "CPU")
        mem_bar = self._create_usage_bar(mem.percent, 100, "Memory")
        disk_bar = self._create_usage_bar(disk.percent, 100, "Disk")

        return f"{cpu_bar}\n{mem_bar}\n{disk_bar}"

    def _create_usage_bar(self, value: float, max_value: float, label: str) -> str:
        """Create a usage bar visualization."""
        percent = (value / max_value) * 100
        bar_length = 40
        filled_length = int(bar_length * percent / 100)

        # Color based on usage
        if percent > 85:
            color = "red"
        elif percent > 70:
            color = "yellow"
            color = "green"

        bar = f"[{color}]{'█' * filled_length}[/{color}]" + "░" * (
            bar_length - filled_length
        )
        return f"{label:8} {bar} {percent:5.1f}%"

    def generate_monitoring_report(self) -> None:
        """Generate monitoring summary report."""
        console.print("\n[bold cyan]Monitoring Summary Report[/bold cyan]")

        # System overview
        table = Table(title="System Health Overview")
        table.add_column("Metric", style="cyan")
        table.add_column("Current", style="green")
        table.add_column("Threshold", style="yellow")
        table.add_column("Status", style="magenta")

        # Get current system metrics
        sys_metrics = self._collect_system_metrics()

        # Add rows
        cpu_status = (
            "✓" if sys_metrics["cpu_percent"] < self.thresholds["cpu_percent"] else "✗"
        )
        table.add_row(
            "CPU Usage",
            f"{sys_metrics['cpu_percent']:.1f}%",
            f"{self.thresholds['cpu_percent']:.0f}%",
            f"[{'green' if cpu_status == '✓' else 'red'}]{cpu_status}[/]",
        )

        mem_status = (
            "✓"
            if sys_metrics["memory"]["percent"] < self.thresholds["memory_percent"]
            else "✗"
        )
        table.add_row(
            "Memory Usage",
            f"{sys_metrics['memory']['percent']:.1f}%",
            f"{self.thresholds['memory_percent']:.0f}%",
            f"[{'green' if mem_status == '✓' else 'red'}]{mem_status}[/]",
        )

        disk_status = (
            "✓"
            if sys_metrics["disk"]["percent"] < self.thresholds["disk_percent"]
            else "✗"
        )
        table.add_row(
            "Disk Usage",
            f"{sys_metrics['disk']['percent']:.1f}%",
            f"{self.thresholds['disk_percent']:.0f}%",
            f"[{'green' if disk_status == '✓' else 'red'}]{disk_status}[/]",
        )

        console.print(table)

        # Alert summary
        if self.alerts:
            console.print(f"\n[yellow]Total Alerts: {len(self.alerts)}[/yellow]")
            high_alerts = sum(1 for a in self.alerts if a["severity"] == "high")
            med_alerts = sum(1 for a in self.alerts if a["severity"] == "medium")
            console.print(f"  [red]High: {high_alerts}[/red]")
            console.print(f"  [yellow]Medium: {med_alerts}[/yellow]")
            console.print("\n[green]No alerts generated[/green]")
