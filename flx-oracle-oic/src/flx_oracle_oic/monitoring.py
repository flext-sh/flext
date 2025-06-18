"""Comprehensive monitoring system for Oracle Integration Cloud.

This module provides:
- Performance monitoring and metrics collection
- Health checks for OIC services and integrations
- Real-time monitoring of integration status
- SLA monitoring and alerting
- Resource utilization tracking
- Error tracking and analysis
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

from flx.core.logging import get_logger  # type: ignore[import-untyped]

from .constants import STATUS_ACTIVE, STATUS_INACTIVE

if TYPE_CHECKING:
    from .adapter import OracleOicHttpAdapter


logger = get_logger(__name__)


class HealthStatus(StrEnum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AlertSeverity(StrEnum):
    """Alert severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class MetricValue:
    """Represents a single metric measurement."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Represents a health check result."""

    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Represents a monitoring alert."""

    id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: datetime | None = None
    details: dict[str, Any] = field(default_factory=dict)


class MonitoringConfig(BaseModel):
    """Configuration for the monitoring system."""

    # Health check intervals (in seconds)
    health_check_interval: int = Field(
        default=60,
        ge=10,
        description="Interval between health checks",
    )
    integration_check_interval: int = Field(
        default=300,
        ge=60,
        description="Interval between integration checks",
    )

    # Thresholds
    response_time_threshold: float = Field(
        default=5.0,
        ge=0.1,
        description="Response time threshold in seconds",
    )
    error_rate_threshold: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Error rate threshold (0-1)",
    )

    # Retention periods (in hours)
    metrics_retention_hours: int = Field(
        default=168,
        ge=1,
        description="Metrics retention period (default: 7 days)",
    )
    alerts_retention_hours: int = Field(
        default=720,
        ge=1,
        description="Alerts retention period (default: 30 days)",
    )

    # Feature flags
    enable_detailed_metrics: bool = Field(
        default=True,
        description="Enable detailed metrics collection",
    )
    enable_sla_monitoring: bool = Field(
        default=True,
        description="Enable SLA monitoring",
    )
    enable_alerting: bool = Field(default=True, description="Enable alerting system")


class PerformanceMetrics:
    """Collects and manages performance metrics."""

    def __init__(self, config: MonitoringConfig) -> None:
        self.config = config
        self._metrics: list[MetricValue] = []
        self._response_times: list[float] = []
        self._error_counts: dict[str, int] = {}
        self._success_counts: dict[str, int] = {}

    def record_response_time(
        self,
        operation: str,
        response_time: float,
        *,
        success: bool = True,
    ) -> None:
        """Record response time for an operation."""
        now = datetime.now(UTC)

        # Record the metric
        metric = MetricValue(
            name="response_time",
            value=response_time,
            unit="seconds",
            timestamp=now,
            labels={"operation": operation, "success": str(success)},
        )
        self._metrics.append(metric)

        # Track for statistics
        self._response_times.append(response_time)

        # Track success/error counts
        if success:
            self._success_counts[operation] = self._success_counts.get(operation, 0) + 1
        else:
            self._error_counts[operation] = self._error_counts.get(operation, 0) + 1

        # Clean old metrics
        self._cleanup_old_metrics()

    def record_custom_metric(
        self,
        name: str,
        value: float,
        unit: str,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Record a custom metric."""
        metric = MetricValue(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(UTC),
            labels=labels or {},
        )
        self._metrics.append(metric)
        self._cleanup_old_metrics()

    def get_average_response_time(
        self,
        operation: str | None = None,
        minutes: int = 60,
    ) -> float:
        """Get average response time for the last N minutes."""
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)

        relevant_metrics = [
            m
            for m in self._metrics
            if m.name == "response_time"
            and m.timestamp >= cutoff
            and (operation is None or m.labels.get("operation") == operation)
        ]

        if not relevant_metrics:
            return 0.0

        return sum(m.value for m in relevant_metrics) / len(relevant_metrics)

    def get_error_rate(self, operation: str | None = None, minutes: int = 60) -> float:
        """Get error rate for the last N minutes."""
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)

        success_metrics = [
            m
            for m in self._metrics
            if m.name == "response_time"
            and m.timestamp >= cutoff
            and m.labels.get("success") == "True"
            and (operation is None or m.labels.get("operation") == operation)
        ]

        error_metrics = [
            m
            for m in self._metrics
            if m.name == "response_time"
            and m.timestamp >= cutoff
            and m.labels.get("success") == "False"
            and (operation is None or m.labels.get("operation") == operation)
        ]

        total = len(success_metrics) + len(error_metrics)
        if total == 0:
            return 0.0

        return len(error_metrics) / total

    def get_throughput(self, operation: str | None = None, minutes: int = 60) -> float:
        """Get throughput (requests per minute) for the last N minutes."""
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)

        relevant_metrics = [
            m
            for m in self._metrics
            if m.name == "response_time"
            and m.timestamp >= cutoff
            and (operation is None or m.labels.get("operation") == operation)
        ]

        return len(relevant_metrics) / minutes

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get a summary of all metrics."""
        return {
            "total_metrics": len(self._metrics),
            "avg_response_time_1h": self.get_average_response_time(minutes=60),
            "avg_response_time_24h": self.get_average_response_time(minutes=1440),
            "error_rate_1h": self.get_error_rate(minutes=60),
            "error_rate_24h": self.get_error_rate(minutes=1440),
            "throughput_1h": self.get_throughput(minutes=60),
            "throughput_24h": self.get_throughput(minutes=1440),
            "operations": list(
                {
                    m.labels.get("operation", "")
                    for m in self._metrics
                    if m.labels.get("operation")
                },
            ),
        }

    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics based on retention policy."""
        cutoff = datetime.now(UTC) - timedelta(
            hours=self.config.metrics_retention_hours,
        )
        self._metrics = [m for m in self._metrics if m.timestamp >= cutoff]


class HealthMonitor:
    """Monitors health of OIC services and integrations."""

    def __init__(
        self,
        config: MonitoringConfig,
        adapter: Optional["OracleOicHttpAdapter"] = None,
    ) -> None:
        self.config = config
        self.adapter = adapter
        self._health_checks: list[HealthCheck] = []
        self._last_check_time: datetime | None = None

    async def check_oic_health(self) -> HealthCheck:
        """Check overall OIC instance health."""
        start_time = time.time()

        try:
            if not self.adapter:
                return HealthCheck(
                    name="oic_instance",
                    status=HealthStatus.UNKNOWN,
                    message="No adapter available for health check",
                    timestamp=datetime.now(UTC),
                    response_time=0.0,
                )

            # Try to get integrations to test connectivity
            integrations = await self.adapter.get_integrations(limit=1)
            response_time = time.time() - start_time

            if response_time > self.config.response_time_threshold:
                status = HealthStatus.DEGRADED
                message = f"Slow response time: {response_time:.2f}s"
            else:
                status = HealthStatus.HEALTHY
                message = "OIC instance is healthy"

            health_check = HealthCheck(
                name="oic_instance",
                status=status,
                message=message,
                timestamp=datetime.now(UTC),
                response_time=response_time,
                details={
                    "integrations_count": len(integrations),
                    "base_url": (
                        self.adapter.config.base_url
                        if hasattr(self.adapter, "config")
                        else "unknown"
                    ),
                },
            )

        except Exception as e:
            response_time = time.time() - start_time
            health_check = HealthCheck(
                name="oic_instance",
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {e!s}",
                timestamp=datetime.now(UTC),
                response_time=response_time,
                details={"error": str(e)},
            )

        self._health_checks.append(health_check)
        self._cleanup_old_health_checks()
        return health_check

    async def check_authentication_health(self) -> HealthCheck:
        """Check authentication system health."""
        start_time = time.time()

        try:
            if not self.adapter:
                return HealthCheck(
                    name="authentication",
                    status=HealthStatus.UNKNOWN,
                    message="No adapter available for auth check",
                    timestamp=datetime.now(UTC),
                    response_time=0.0,
                )

            # Try to authenticate
            auth_result = await self.adapter.authenticate()
            response_time = time.time() - start_time

            if auth_result.get("authenticated"):
                status = HealthStatus.HEALTHY
                message = "Authentication is working"
                details = {
                    "strategy": auth_result.get("strategy", "unknown"),
                    "token_expires_at": auth_result.get("expires_at"),
                }
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Authentication failed: {auth_result.get('error', 'unknown error')}"
                details = {"error": auth_result.get("error")}

            health_check = HealthCheck(
                name="authentication",
                status=status,
                message=message,
                timestamp=datetime.now(UTC),
                response_time=response_time,
                details=details,
            )

        except Exception as e:
            response_time = time.time() - start_time
            health_check = HealthCheck(
                name="authentication",
                status=HealthStatus.UNHEALTHY,
                message=f"Auth health check failed: {e!s}",
                timestamp=datetime.now(UTC),
                response_time=response_time,
                details={"error": str(e)},
            )

        self._health_checks.append(health_check)
        self._cleanup_old_health_checks()
        return health_check

    async def check_integration_health(self, integration_id: str) -> HealthCheck:
        """Check health of a specific integration."""
        start_time = time.time()

        try:
            if not self.adapter:
                return HealthCheck(
                    name=f"integration_{integration_id}",
                    status=HealthStatus.UNKNOWN,
                    message="No adapter available for integration check",
                    timestamp=datetime.now(UTC),
                    response_time=0.0,
                )

            # Get integration details
            integration = await self.adapter.get_integration(integration_id)
            response_time = time.time() - start_time

            if not integration:
                status = HealthStatus.UNHEALTHY
                message = f"Integration {integration_id} not found"
                details = {"error": "Integration not found"}
            else:
                integration_status = integration.get("status", "UNKNOWN").upper()
                if integration_status == STATUS_ACTIVE:
                    status = HealthStatus.HEALTHY
                    message = f"Integration {integration_id} is active"
                elif integration_status == STATUS_INACTIVE:
                    status = HealthStatus.DEGRADED
                    message = f"Integration {integration_id} is inactive"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = (
                        f"Integration {integration_id} status: {integration_status}"
                    )

                details = {
                    "integration_status": integration_status,
                    "name": integration.get("name"),
                    "version": integration.get("version"),
                    "last_updated": integration.get("lastUpdated"),
                }

            health_check = HealthCheck(
                name=f"integration_{integration_id}",
                status=status,
                message=message,
                timestamp=datetime.now(UTC),
                response_time=response_time,
                details=details,
            )

        except Exception as e:
            response_time = time.time() - start_time
            health_check = HealthCheck(
                name=f"integration_{integration_id}",
                status=HealthStatus.UNHEALTHY,
                message=f"Integration health check failed: {e!s}",
                timestamp=datetime.now(UTC),
                response_time=response_time,
                details={"error": str(e)},
            )

        self._health_checks.append(health_check)
        self._cleanup_old_health_checks()
        return health_check

    async def run_comprehensive_health_check(self) -> list[HealthCheck]:
        """Run all health checks."""
        results = []

        # OIC instance health
        results.append(await self.check_oic_health())

        # Authentication health
        results.append(await self.check_authentication_health())

        # Get integrations and check their health
        if self.adapter:
            try:
                integrations = await self.adapter.get_integrations(limit=10)
                for integration in integrations:
                    integration_id = integration.get("id")
                    if integration_id:
                        results.append(
                            await self.check_integration_health(integration_id),
                        )
            except Exception as e:
                logger.exception("Failed to get integrations for health check: %s", e)

        self._last_check_time = datetime.now(UTC)
        return results

    def get_overall_health_status(self) -> HealthStatus:
        """Get overall health status based on recent checks."""
        if not self._health_checks:
            return HealthStatus.UNKNOWN

        # Get recent health checks (last 10 minutes)
        cutoff = datetime.now(UTC) - timedelta(minutes=10)
        recent_checks = [hc for hc in self._health_checks if hc.timestamp >= cutoff]

        if not recent_checks:
            return HealthStatus.UNKNOWN

        # Determine overall status
        statuses = [hc.status for hc in recent_checks]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        if HealthStatus.HEALTHY in statuses:
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN

    def get_health_summary(self) -> dict[str, Any]:
        """Get health monitoring summary."""
        overall_status = self.get_overall_health_status()

        # Count recent checks by status
        cutoff = datetime.now(UTC) - timedelta(hours=1)
        recent_checks = [hc for hc in self._health_checks if hc.timestamp >= cutoff]

        status_counts = {}
        for status in HealthStatus:
            status_counts[status.value] = len(
                [hc for hc in recent_checks if hc.status == status],
            )

        return {
            "overall_status": overall_status.value,
            "last_check_time": (
                self._last_check_time.isoformat() if self._last_check_time else None
            ),
            "total_checks_1h": len(recent_checks),
            "status_counts_1h": status_counts,
            "recent_checks": [
                {
                    "name": hc.name,
                    "status": hc.status.value,
                    "message": hc.message,
                    "timestamp": hc.timestamp.isoformat(),
                    "response_time": hc.response_time,
                }
                for hc in recent_checks[-10:]  # Last 10 checks
            ],
        }

    def _cleanup_old_health_checks(self) -> None:
        """Clean up old health checks."""
        cutoff = datetime.now(UTC) - timedelta(hours=24)  # Keep 24 hours
        self._health_checks = [
            hc for hc in self._health_checks if hc.timestamp >= cutoff
        ]


class AlertManager:
    """Manages monitoring alerts."""

    def __init__(self, config: MonitoringConfig) -> None:
        self.config = config
        self._alerts: list[Alert] = []
        self._alert_counter = 0

    def create_alert(
        self,
        name: str,
        severity: AlertSeverity,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> Alert:
        """Create a new alert."""
        self._alert_counter += 1
        alert = Alert(
            id=f"alert_{self._alert_counter}",
            name=name,
            severity=severity,
            message=message,
            timestamp=datetime.now(UTC),
            details=details or {},
        )

        self._alerts.append(alert)
        self._cleanup_old_alerts()

        logger.warning("Alert created: %s - %s", name, message)
        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self._alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolution_time = datetime.now(UTC)
                logger.info("Alert resolved: %s", alert.name)
                return True
        return False

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[Alert]:
        """Get active alerts, optionally filtered by severity."""
        alerts = [a for a in self._alerts if not a.resolved]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def get_alerts_summary(self) -> dict[str, Any]:
        """Get alerts summary."""
        active_alerts = self.get_active_alerts()

        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(
                [a for a in active_alerts if a.severity == severity],
            )

        return {
            "total_active_alerts": len(active_alerts),
            "severity_counts": severity_counts,
            "recent_alerts": [
                {
                    "id": a.id,
                    "name": a.name,
                    "severity": a.severity.value,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                    "resolved": a.resolved,
                }
                for a in self._alerts[-10:]  # Last 10 alerts
            ],
        }

    def _cleanup_old_alerts(self) -> None:
        """Clean up old alerts based on retention policy."""
        cutoff = datetime.now(UTC) - timedelta(hours=self.config.alerts_retention_hours)
        self._alerts = [a for a in self._alerts if a.timestamp >= cutoff]


class OICMonitor:
    """Main monitoring system for Oracle Integration Cloud."""

    def __init__(
        self,
        config: MonitoringConfig,
        adapter: Optional["OracleOicHttpAdapter"] = None,
    ) -> None:
        self.config = config
        self.adapter = adapter

        self.metrics = PerformanceMetrics(config)
        self.health_monitor = HealthMonitor(config, adapter)
        self.alert_manager = AlertManager(config)

        self._monitoring_task: asyncio.Task | None = None
        self._monitoring_enabled = False

    def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if self._monitoring_enabled:
            logger.warning("Monitoring is already running")
            return

        self._monitoring_enabled = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("OIC monitoring started")

    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        self._monitoring_enabled = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
        logger.info("OIC monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        last_health_check = datetime.now(UTC) - timedelta(hours=1)

        while self._monitoring_enabled:
            try:
                now = datetime.now(UTC)

                # Run health checks at configured interval
                if (
                    now - last_health_check
                ).total_seconds() >= self.config.health_check_interval:
                    await self._run_scheduled_health_checks()
                    last_health_check = now

                # Check for alerts based on metrics and health
                await self._check_for_alerts()

                # Wait before next iteration
                await asyncio.sleep(10)  # Check every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Error in monitoring loop: %s", e)
                await asyncio.sleep(30)  # Wait longer on error

    async def _run_scheduled_health_checks(self) -> None:
        """Run scheduled health checks."""
        try:
            health_checks = await self.health_monitor.run_comprehensive_health_check()

            # Record health check metrics
            for hc in health_checks:
                success = hc.status in {HealthStatus.HEALTHY, HealthStatus.DEGRADED}
                self.metrics.record_response_time(
                    operation=f"health_check_{hc.name}",
                    response_time=hc.response_time,
                    success=success,
                )

        except Exception as e:
            logger.exception("Failed to run scheduled health checks: %s", e)

    async def _check_for_alerts(self) -> None:
        """Check metrics and health for alert conditions."""
        if not self.config.enable_alerting:
            return

        try:
            # Check response time thresholds
            avg_response_time = self.metrics.get_average_response_time(minutes=5)
            if avg_response_time > self.config.response_time_threshold:
                self.alert_manager.create_alert(
                    name="high_response_time",
                    severity=AlertSeverity.HIGH,
                    message=(
                        f"Average response time {avg_response_time:.2f}s exceeds threshold "
                        f"{self.config.response_time_threshold}s"
                    ),
                    details={
                        "avg_response_time": avg_response_time,
                        "threshold": self.config.response_time_threshold,
                    },
                )

            # Check error rate thresholds
            error_rate = self.metrics.get_error_rate(minutes=5)
            if error_rate > self.config.error_rate_threshold:
                self.alert_manager.create_alert(
                    name="high_error_rate",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Error rate {error_rate:.2%} exceeds threshold {self.config.error_rate_threshold:.2%}",
                    details={
                        "error_rate": error_rate,
                        "threshold": self.config.error_rate_threshold,
                    },
                )

            # Check overall health status
            overall_health = self.health_monitor.get_overall_health_status()
            if overall_health == HealthStatus.UNHEALTHY:
                self.alert_manager.create_alert(
                    name="system_unhealthy",
                    severity=AlertSeverity.CRITICAL,
                    message="OIC system is unhealthy",
                    details={"health_status": overall_health.value},
                )

        except Exception as e:
            logger.exception("Failed to check for alerts: %s", e)

    def get_monitoring_dashboard(self) -> dict[str, Any]:
        """Get comprehensive monitoring dashboard data."""
        return {
            "monitoring_enabled": self._monitoring_enabled,
            "config": {
                "health_check_interval": self.config.health_check_interval,
                "response_time_threshold": self.config.response_time_threshold,
                "error_rate_threshold": self.config.error_rate_threshold,
            },
            "metrics": self.metrics.get_metrics_summary(),
            "health": self.health_monitor.get_health_summary(),
            "alerts": self.alert_manager.get_alerts_summary(),
        }

    async def get_integration_monitoring_report(
        self,
        integration_id: str,
    ) -> dict[str, Any]:
        """Get detailed monitoring report for a specific integration."""
        # Get integration-specific metrics
        avg_response_time = self.metrics.get_average_response_time(
            operation=f"integration_{integration_id}",
        )
        error_rate = self.metrics.get_error_rate(
            operation=f"integration_{integration_id}",
        )
        throughput = self.metrics.get_throughput(
            operation=f"integration_{integration_id}",
        )

        # Get latest health check
        health_check = await self.health_monitor.check_integration_health(
            integration_id,
        )

        return {
            "integration_id": integration_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "health": {
                "status": health_check.status.value,
                "message": health_check.message,
                "response_time": health_check.response_time,
                "details": health_check.details,
            },
            "performance": {
                "avg_response_time_1h": avg_response_time,
                "error_rate_1h": error_rate,
                "throughput_1h": throughput,
            },
            "alerts": [
                {
                    "id": a.id,
                    "name": a.name,
                    "severity": a.severity.value,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in self.alert_manager.get_active_alerts()
                if integration_id in a.details.get("integration_id", "")
            ],
        }
