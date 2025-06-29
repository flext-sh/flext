"""Dashboard Django application configuration.

This module configures the dashboard application for the FLX Meltano Enterprise
web interface, providing pipeline monitoring and management capabilities.
"""

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Django application configuration for the FLX Dashboard.

    Configures the dashboard application that provides real-time monitoring,
    pipeline management, and analytics visualization for the FLX Meltano
    Enterprise platform.

    Features:
        - Real-time pipeline status monitoring
        - Execution history and logs
        - Performance metrics visualization
        - User activity tracking
        - System health monitoring

    Attributes
    ----------
        default_auto_field: Uses BigAutoField for primary keys
        name: Full Python path to the application
        verbose_name: Human-readable name for REDACTED_LDAP_BIND_PASSWORD interface

    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "flx_web.apps.dashboard"
    verbose_name = "Dashboard"
