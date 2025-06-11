"""Django app configuration for analyzer."""

from __future__ import annotations

from django.apps import AppConfig


class AnalyzerConfig(AppConfig):
    """Configuration for the analyzer app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "analyzer"
    verbose_name = "Code Analyzer"

    def ready(self) -> None:
        """Initialize the app when Django starts."""
        from . import signals  # noqa: F401
