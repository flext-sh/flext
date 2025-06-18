"""Pipelines app configuration."""

from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    """Pipelines app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pipelines"
    verbose_name = "Pipelines"
