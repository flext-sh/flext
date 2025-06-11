"""Django app configuration for dashboard."""

from __future__ import annotations

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Configuration for the dashboard app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"
    verbose_name = "Dashboard"
