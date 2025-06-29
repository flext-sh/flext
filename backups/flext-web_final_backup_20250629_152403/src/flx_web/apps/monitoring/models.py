"""Enterprise monitoring Django models for data persistence.

Models for storing and tracking monitoring data including:
- Business metrics history
- Security violation logs
- Error pattern tracking
- Health check results
- Alert management
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class BusinessMetricType(models.TextChoices):
    """Business metric type choices matching core monitoring system."""

    PIPELINE_PERFORMANCE = "pipeline_performance", "Pipeline Performance"
    RESOURCE_UTILIZATION = "resource_utilization", "Resource Utilization"
    PLUGIN_EFFICIENCY = "plugin_efficiency", "Plugin Efficiency"
    USER_ACTIVITY = "user_activity", "User Activity"
    SYSTEM_RELIABILITY = "system_reliability", "System Reliability"


class AlertSeverity(models.TextChoices):
    """Alert severity levels matching core monitoring system."""

    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class SecurityThreatLevel(models.TextChoices):
    """Security threat levels matching security validation system."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class ErrorSeverity(models.TextChoices):
    """Error severity levels matching error pattern system."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class BusinessMetricHistory(models.Model):
    """Historical business metrics for trend analysis and reporting."""

    name = models.CharField(max_length=100, db_index=True)
    metric_type = models.CharField(
        max_length=50,
        choices=BusinessMetricType.choices,
        db_index=True,
    )
    current_value = models.FloatField()
    previous_value = models.FloatField(null=True, blank=True)
    trend_direction = models.CharField(max_length=20, default="stable")
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["name", "-timestamp"]),
            models.Index(fields=["metric_type", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.name}: {self.current_value} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

    @property
    def trend_percentage(self) -> float | None:
        """Calculate trend percentage change."""
        if self.previous_value is None or self.previous_value == 0:
            return None
        return ((self.current_value - self.previous_value) / self.previous_value) * 100


class SecurityViolationLog(models.Model):
    """Security violation logs for compliance and monitoring."""

    violation_id = models.CharField(max_length=100, unique=True, db_index=True)
    threat_level = models.CharField(
        max_length=20,
        choices=SecurityThreatLevel.choices,
        db_index=True,
    )
    validation_type = models.CharField(max_length=50, db_index=True)
    description = models.TextField()
    source_ip = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=200, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    payload = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    blocked = models.BooleanField(default=True)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["threat_level", "-timestamp"]),
            models.Index(fields=["validation_type", "-timestamp"]),
            models.Index(fields=["source_ip", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"Security Violation: {self.validation_type} ({self.threat_level}) - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class ErrorPatternLog(models.Model):
    """Error pattern tracking for system reliability monitoring."""

    pattern_id = models.CharField(max_length=100, db_index=True)
    error_signature = models.CharField(max_length=500, db_index=True)
    error_message = models.TextField()
    category = models.CharField(max_length=50, db_index=True)
    severity = models.CharField(
        max_length=20,
        choices=ErrorSeverity.choices,
        db_index=True,
    )
    occurrence_count = models.PositiveIntegerField(default=1)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now, db_index=True)
    recovery_action = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["category", "-last_seen"]),
            models.Index(fields=["severity", "-last_seen"]),
            models.Index(fields=["pattern_id", "-last_seen"]),
        ]

    def __str__(self) -> str:
        return f"Error Pattern: {self.category} ({self.severity}) - {self.occurrence_count} occurrences"


class SystemHealthCheck(models.Model):
    """System health check results for monitoring system components."""

    component_name = models.CharField(max_length=100, db_index=True)
    healthy = models.BooleanField(db_index=True)
    message = models.TextField()
    metadata = models.JSONField(default=dict)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["component_name", "-timestamp"]),
            models.Index(fields=["healthy", "-timestamp"]),
        ]

    def __str__(self) -> str:
        status = "Healthy" if self.healthy else "Unhealthy"
        return f"{self.component_name}: {status} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class MonitoringAlert(models.Model):
    """Enterprise monitoring alerts across all systems."""

    alert_id = models.CharField(max_length=100, unique=True, db_index=True)
    alert_type = models.CharField(
        max_length=50,
        db_index=True,
    )  # business_metric, error_pattern, security_violation
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices,
        db_index=True,
    )
    source_system = models.CharField(
        max_length=50,
        db_index=True,
    )  # business_metrics, error_patterns, security_validation

    # Alert status tracking
    active = models.BooleanField(default=True, db_index=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_alerts",
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    # Alert resolution
    resolved = models.BooleanField(default=False, db_index=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional metadata
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["severity", "active", "-created_at"]),
            models.Index(fields=["alert_type", "active", "-created_at"]),
            models.Index(fields=["source_system", "active", "-created_at"]),
            models.Index(fields=["resolved", "-created_at"]),
        ]

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"{self.title} ({self.severity}) - {status}"

    def acknowledge(self, user: User) -> None:
        """Acknowledge the alert."""
        self.acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save(
            update_fields=[
                "acknowledged",
                "acknowledged_by",
                "acknowledged_at",
                "updated_at",
            ],
        )

    def resolve(self, user: User, notes: str | None = None) -> None:
        """Resolve the alert."""
        self.resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.active = False
        if notes:
            self.resolution_notes = notes
        self.save(
            update_fields=[
                "resolved",
                "resolved_by",
                "resolved_at",
                "active",
                "resolution_notes",
                "updated_at",
            ],
        )


class MonitoringDashboardConfig(models.Model):
    """Configuration settings for monitoring dashboard per user."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="monitoring_config",
    )

    # Dashboard preferences
    refresh_interval_seconds = models.PositiveIntegerField(default=30)
    show_business_metrics = models.BooleanField(default=True)
    show_security_violations = models.BooleanField(default=True)
    show_error_patterns = models.BooleanField(default=True)
    show_health_status = models.BooleanField(default=True)

    # Alert preferences
    email_alerts = models.BooleanField(default=True)
    alert_severity_threshold = models.CharField(
        max_length=20,
        choices=AlertSeverity.choices,
        default=AlertSeverity.WARNING,
    )

    # Display preferences
    metrics_chart_type = models.CharField(
        max_length=20,
        default="line",
    )  # line, bar, area
    time_range_hours = models.PositiveIntegerField(default=24)  # Default 24 hour view

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Monitoring Config for {self.user.username}"
