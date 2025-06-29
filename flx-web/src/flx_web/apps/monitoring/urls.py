"""Enterprise monitoring URL configuration.

URL patterns for comprehensive enterprise monitoring interface including:
- Main monitoring dashboard
- Real-time API endpoints for metrics
- Security monitoring interfaces
- Error pattern analysis endpoints
- Health status monitoring
"""

from django.urls import path

from flx_web import views

app_name = "monitoring"

urlpatterns = [
    # Main monitoring dashboard
    path("", views.MonitoringDashboardView.as_view(), name="dashboard"),
    # API endpoints for real-time data
    path(
        "api/business-metrics/",
        views.BusinessMetricsAPIView.as_view(),
        name="api_business_metrics",
    ),
    path(
        "api/security/",
        views.SecurityMonitoringAPIView.as_view(),
        name="api_security_monitoring",
    ),
    path(
        "api/error-patterns/",
        views.ErrorPatternsAPIView.as_view(),
        name="api_error_patterns",
    ),
    path("api/health/", views.HealthStatusAPIView.as_view(), name="api_health_status"),
    path("api/alerts/", views.AlertsAPIView.as_view(), name="api_alerts"),
    path(
        "api/stats/",
        views.MonitoringStatsAPIView.as_view(),
        name="api_monitoring_stats",
    ),
]
