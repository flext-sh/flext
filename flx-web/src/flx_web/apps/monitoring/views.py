"""Enterprise monitoring views with real-time metrics and alerting.

Comprehensive monitoring interface providing:
- Real-time business metrics visualization
- Security violation monitoring
- Error pattern analysis and recovery tracking
- Performance monitoring and alerting
- Health status dashboard with component details
"""

from __future__ import annotations

import asyncio
import functools
import operator
from datetime import UTC, datetime
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.generic import TemplateView
from flx_core.config.domain_config import get_config
from flx_core.security.advanced_validation import AdvancedSecurityValidator
from flx_observability.health import HealthChecker
from flx_observability.metrics import MetricsCollector
from flx_observability.monitoring.business_metrics import EnterpriseBusinessMetrics
from flx_observability.monitoring.error_patterns import ProductionErrorHandler

# Python 3.13 type aliases for monitoring domain
type MonitoringStats = dict[str, int | float | list[dict[str, Any]]]
type AlertData = dict[str, str | int | float]
type SecurityStats = dict[str, int | dict[str, Any]]
type HealthData = dict[str, bool | dict[str, Any]]


class EnterpriseMonitoringService:
    """Unified monitoring service integrating all enterprise monitoring systems.

    Consolidates business metrics, error patterns, security validation,
    and health monitoring into a single coherent monitoring interface.
    """

    def __init__(self) -> None:
        """Initialize enterprise monitoring service with all components."""
        self.config = get_config()
        self.metrics_collector = MetricsCollector()
        self.business_metrics = EnterpriseBusinessMetrics(self.metrics_collector)
        self.error_handler = ProductionErrorHandler()
        self.health_monitor = HealthChecker()
        self.security_validator = AdvancedSecurityValidator()

    async def get_comprehensive_monitoring_data(self) -> dict[str, Any]:
        """Get complete monitoring data from all enterprise systems.

        Returns
        -------
            dict[str, Any]: Comprehensive monitoring data including:
                - business_metrics: Business intelligence metrics
                - error_patterns: Error analysis and recovery patterns
                - security_stats: Security validation statistics
                - health_status: System health monitoring data
                - alerts: Active alerts across all systems

        """
        try:
            # Collect data from all monitoring systems in parallel
            business_data = await self._get_business_metrics_data()
            error_data = await self._get_error_patterns_data()
            security_data = await self._get_security_stats_data()
            health_data = await self._get_health_status_data()

            # Consolidate alerts from all systems
            all_alerts = await self._consolidate_alerts()

            return {
                "business_metrics": business_data,
                "error_patterns": error_data,
                "security_stats": security_data,
                "health_status": health_data,
                "alerts": all_alerts,
                "timestamp": datetime.now(UTC).isoformat(),
                "status": "healthy" if len(all_alerts) == 0 else "degraded",
            }

        except Exception as e:
            return {
                "error": f"Failed to collect monitoring data: {e}",
                "timestamp": datetime.now(UTC).isoformat(),
                "status": "error",
            }

    async def _get_business_metrics_data(self) -> dict[str, Any]:
        """Get business metrics data with trend analysis."""
        metrics = await self.business_metrics.collect_business_metrics()

        # Group metrics by type for dashboard display
        metrics_by_type = {}
        for metric in metrics:
            metric_type = metric.metric_type.value
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []

            metrics_by_type[metric_type].append(
                {
                    "name": metric.name,
                    "current_value": metric.current_value,
                    "previous_value": metric.previous_value,
                    "trend_direction": metric.trend_direction,
                    "trend_percentage": metric.trend_percentage,
                    "metadata": metric.metadata,
                    "timestamp": metric.timestamp.isoformat(),
                },
            )

        return {
            "metrics_by_type": metrics_by_type,
            "summary": self.business_metrics.get_metrics_summary(),
            "active_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "metric_value": alert.metric_value,
                    "threshold": alert.threshold,
                    "timestamp": alert.timestamp.isoformat(),
                }
                for alert in self.business_metrics.get_active_alerts()
            ],
        }

    async def _get_error_patterns_data(self) -> dict[str, Any]:
        """Get error patterns analysis data."""
        error_stats = self.error_handler.get_error_statistics()
        recent_violations = self.error_handler.get_recent_violations(limit=20)

        return {
            "statistics": error_stats,
            "recent_violations": [
                {
                    "pattern_id": str(violation.pattern_id),
                    "error_signature": violation.error_signature[
                        :100
                    ],  # Truncate for display
                    "category": violation.category.value,
                    "severity": violation.severity.value,
                    "occurrence_count": violation.occurrence_count,
                    "recovery_action": violation.recovery_action.value,
                    "last_seen": violation.last_seen.isoformat(),
                }
                for violation in recent_violations
            ],
        }

    async def _get_security_stats_data(self) -> dict[str, Any]:
        """Get security validation statistics."""
        security_stats = self.security_validator.get_security_statistics()
        recent_violations = self.security_validator.get_recent_violations(limit=15)

        return {
            "statistics": security_stats,
            "recent_violations": [
                {
                    "violation_id": violation.violation_id,
                    "threat_level": violation.threat_level.value,
                    "validation_type": violation.validation_type.value,
                    "description": violation.violation_description,
                    "source_ip": violation.source_ip,
                    "user_id": violation.user_id,
                    "timestamp": violation.timestamp.isoformat(),
                    "blocked": violation.blocked,
                }
                for violation in recent_violations
            ],
        }

    async def _get_health_status_data(self) -> dict[str, Any]:
        """Get comprehensive health status data."""
        try:
            health_status = await self.health_monitor.check_health()

            return {
                "overall_healthy": health_status["status"] == "healthy",
                "components": {
                    component["name"]: {
                        "healthy": (
                            component["status"].value == "healthy"
                            if hasattr(component["status"], "value")
                            else component["status"] == "healthy"
                        ),
                        "message": component["message"],
                        "metadata": component["metadata"],
                        "details": component.get("details", {}),
                    }
                    for component in health_status["components"]
                },
                "timestamp": health_status["timestamp"],
            }
        except Exception:
            return {
                "overall_healthy": False,
                "components": {},
                "error": "Health monitoring unavailable",
                "timestamp": datetime.now(UTC).isoformat(),
            }

    async def _consolidate_alerts(self) -> list[dict[str, Any]]:
        """Consolidate alerts from all monitoring systems."""
        # Business metric alerts
        alerts = [
            {
                "type": "business_metric",
                "id": alert.alert_id,
                "title": alert.title,
                "severity": alert.severity.value,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "source": "business_metrics",
            }
            for alert in self.business_metrics.get_active_alerts()
        ]

        # Error pattern alerts (high severity patterns)
        alerts.extend(
            {
                "type": "error_pattern",
                "id": str(violation.pattern_id),
                "title": f"Error Pattern: {violation.category.value.title()}",
                "severity": violation.severity.value,
                "description": f"Pattern detected {violation.occurrence_count} times",
                "timestamp": violation.last_seen.isoformat(),
                "source": "error_patterns",
            }
            for violation in self.error_handler.get_recent_violations(limit=5)
            if violation.severity.value in {"high", "critical"}
        )

        # Security violation alerts
        alerts.extend(
            {
                "type": "security_violation",
                "id": violation.violation_id,
                "title": f"Security: {violation.validation_type.value.replace('_', ' ').title()}",
                "severity": violation.threat_level.value,
                "description": violation.violation_description,
                "timestamp": violation.timestamp.isoformat(),
                "source": "security_validation",
            }
            for violation in self.security_validator.get_recent_violations(limit=5)
            if violation.threat_level.value in {"high", "critical"}
        )

        # Sort alerts by timestamp (most recent first)
        alerts.sort(key=operator.itemgetter("timestamp"), reverse=True)

        return alerts[:20]  # Return top 20 alerts


@functools.lru_cache(maxsize=1)
def get_monitoring_service() -> EnterpriseMonitoringService:
    """Get singleton monitoring service instance.

    Returns
    -------
        EnterpriseMonitoringService: Configured monitoring service instance.

    """
    return EnterpriseMonitoringService()


class MonitoringDashboardView(LoginRequiredMixin, TemplateView):
    """Main monitoring dashboard providing comprehensive enterprise monitoring.

    Features:
        - Real-time business metrics visualization
        - Security violation monitoring and alerting
        - Error pattern analysis and recovery tracking
        - System health monitoring with component details
        - Consolidated alerting across all monitoring systems
    """

    template_name = "monitoring/dashboard.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Get monitoring dashboard context data.

        Returns
        -------
            dict[str, Any]: Context data including comprehensive monitoring data.

        """
        context = super().get_context_data(**kwargs)

        # Get comprehensive monitoring data
        monitoring_service = get_monitoring_service()
        monitoring_data = asyncio.run(
            monitoring_service.get_comprehensive_monitoring_data(),
        )

        context.update(monitoring_data)

        return context


class BusinessMetricsAPIView(LoginRequiredMixin, View):
    """API endpoint for real-time business metrics data."""

    def get(
        self, _request: HttpRequest, *_args: object, **_kwargs: object
    ) -> JsonResponse:
        """Get current business metrics data.

        Returns
        -------
            JsonResponse: Business metrics data or error information.

        """
        try:
            monitoring_service = get_monitoring_service()
            business_data = asyncio.run(monitoring_service._get_business_metrics_data())

            return JsonResponse(
                {
                    "status": "success",
                    "data": business_data,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                status=500,
            )


class SecurityMonitoringAPIView(LoginRequiredMixin, View):
    """API endpoint for real-time security monitoring data."""

    def get(
        self, _request: HttpRequest, *_args: object, **_kwargs: object
    ) -> JsonResponse:
        """Get current security monitoring data.

        Returns
        -------
            JsonResponse: Security monitoring data or error information.

        """
        try:
            monitoring_service = get_monitoring_service()
            security_data = asyncio.run(monitoring_service._get_security_stats_data())

            return JsonResponse(
                {
                    "status": "success",
                    "data": security_data,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                status=500,
            )


class ErrorPatternsAPIView(LoginRequiredMixin, View):
    """API endpoint for error patterns and recovery data."""

    def get(
        self, _request: HttpRequest, *_args: object, **_kwargs: object
    ) -> JsonResponse:
        """Get current error patterns data.

        Returns
        -------
            JsonResponse: Error patterns data or error information.

        """
        try:
            monitoring_service = get_monitoring_service()
            error_data = asyncio.run(monitoring_service._get_error_patterns_data())

            return JsonResponse(
                {
                    "status": "success",
                    "data": error_data,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                status=500,
            )


class HealthStatusAPIView(LoginRequiredMixin, View):
    """API endpoint for comprehensive health status monitoring."""

    def get(
        self, _request: HttpRequest, *_args: object, **_kwargs: object
    ) -> JsonResponse:
        """Get current health status data.

        Returns
        -------
            JsonResponse: Health status data or error information.

        """
        try:
            monitoring_service = get_monitoring_service()
            health_data = asyncio.run(monitoring_service._get_health_status_data())

            return JsonResponse(
                {
                    "status": "success",
                    "data": health_data,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                status=500,
            )


class AlertsAPIView(LoginRequiredMixin, View):
    """API endpoint for consolidated alerts across all monitoring systems."""

    def get(
        self, _request: HttpRequest, *_args: object, **_kwargs: object
    ) -> JsonResponse:
        """Get current consolidated alerts.

        Returns
        -------
            JsonResponse: Consolidated alerts data or error information.

        """
        try:
            monitoring_service = get_monitoring_service()
            alerts = asyncio.run(monitoring_service._consolidate_alerts())

            return JsonResponse(
                {
                    "status": "success",
                    "data": {
                        "alerts": alerts,
                        "count": len(alerts),
                        "critical_count": len(
                            [a for a in alerts if a["severity"] == "critical"],
                        ),
                        "high_count": len(
                            [a for a in alerts if a["severity"] == "high"],
                        ),
                    },
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                status=500,
            )


class MonitoringStatsAPIView(LoginRequiredMixin, View):
    """API endpoint for comprehensive monitoring statistics."""

    def get(
        self, _request: HttpRequest, *_args: object, **_kwargs: object
    ) -> JsonResponse:
        """Get comprehensive monitoring statistics.

        Returns
        -------
            JsonResponse: Monitoring statistics or error information.

        """
        try:
            monitoring_service = get_monitoring_service()
            monitoring_data = asyncio.run(
                monitoring_service.get_comprehensive_monitoring_data(),
            )

            # Calculate summary statistics
            stats = {
                "business_metrics_count": len(
                    monitoring_data.get("business_metrics", {}).get(
                        "metrics_by_type",
                        {},
                    ),
                ),
                "active_alerts_count": len(monitoring_data.get("alerts", [])),
                "security_violations_count": monitoring_data.get("security_stats", {})
                .get("statistics", {})
                .get("total_violations", 0),
                "error_patterns_count": monitoring_data.get("error_patterns", {})
                .get("statistics", {})
                .get("summary", {})
                .get("total_error_patterns", 0),
                "health_status": (
                    "healthy"
                    if monitoring_data.get("health_status", {}).get(
                        "overall_healthy",
                        False,
                    )
                    else "degraded"
                ),
                "last_updated": monitoring_data.get("timestamp"),
            }

            return JsonResponse(
                {
                    "status": "success",
                    "data": stats,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                status=500,
            )
