"""Pipelines Django application configuration.

This module configures the pipelines application for the FLX Meltano Enterprise
web interface, providing data pipeline CRUD operations and management.
"""

from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    """Django application configuration for Pipeline Management.

    Configures the pipelines application that handles data pipeline
    creation, configuration, execution, and monitoring within the
    FLX Meltano Enterprise platform.

    Features:
        - Pipeline CRUD operations (Create, Read, Update, Delete)
        - Pipeline configuration management
        - Execution scheduling and triggers
        - Integration with Meltano extractors and loaders
        - Pipeline versioning and history

    Attributes
    ----------
        default_auto_field: Uses BigAutoField for primary keys
        name: Full Python path to the application
        verbose_name: Human-readable name for REDACTED_LDAP_BIND_PASSWORD interface

    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "flx_web.apps.pipelines"
    verbose_name = "Pipelines"
