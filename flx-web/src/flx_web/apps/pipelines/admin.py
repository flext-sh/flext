"""Django REDACTED_LDAP_BIND_PASSWORD configuration for pipeline models.

This module configures the Django REDACTED_LDAP_BIND_PASSWORD interface for managing pipelines,
executions, and plugins in the FLX Meltano Enterprise platform.
"""

from typing import ClassVar

from django.contrib import REDACTED_LDAP_BIND_PASSWORD

from flx_web.models import Execution, PipelineWeb, PluginWeb


@REDACTED_LDAP_BIND_PASSWORD.register(PipelineWeb)
class PipelineAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Django REDACTED_LDAP_BIND_PASSWORD configuration for Pipeline model.

    Provides a comprehensive REDACTED_LDAP_BIND_PASSWORD interface for managing data pipelines
    including creation, configuration, monitoring, and execution tracking.

    Features:
        - List view with key pipeline information
        - Filtering by status, activity, and dates
        - Search across pipeline names and components
        - Organized fieldsets for easy navigation
        - Read-only fields for computed values
    """

    list_display: ClassVar[list[str]] = [
        "name",
        "extractor",
        "loader",
        "is_active",
        "last_run",
        "last_status",
    ]
    list_filter: ClassVar[list[str]] = ["is_active", "last_status", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "description", "extractor", "loader"]
    readonly_fields: ClassVar[list[str]] = [
        "id",
        "created_at",
        "updated_at",
        "last_run",
        "last_status",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": ("id", "name", "description", "is_active"),
            },
        ),
        (
            "Pipeline Configuration",
            {
                "fields": ("extractor", "loader", "transform", "config", "schedule"),
            },
        ),
        (
            "Status",
            {
                "fields": ("last_run", "last_status"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
            },
        ),
    )


@REDACTED_LDAP_BIND_PASSWORD.register(Execution)
class ExecutionAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Django REDACTED_LDAP_BIND_PASSWORD configuration for Execution model.

    Provides detailed monitoring and management interface for pipeline
    executions, including status tracking, timing information, and
    error investigation capabilities.

    Features:
        - Execution status monitoring
        - Performance metrics (duration, records)
        - Error message search
        - Filtering by pipeline and status
        - Read-only computed fields
    """

    list_display: ClassVar[list[str]] = [
        "pipeline",
        "status",
        "started_at",
        "duration_seconds",
        "records_processed",
    ]
    list_filter: ClassVar[list[str]] = ["status", "started_at", "pipeline"]
    search_fields: ClassVar[list[str]] = ["pipeline__name", "error_message"]
    readonly_fields: ClassVar[list[str]] = [
        "id",
        "started_at",
        "finished_at",
        "duration_seconds",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": ("id", "pipeline", "status"),
            },
        ),
        (
            "Timing",
            {
                "fields": ("started_at", "finished_at", "duration_seconds"),
            },
        ),
        (
            "Results",
            {
                "fields": ("records_processed", "error_message"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("triggered_by", "full_refresh"),
            },
        ),
    )


@REDACTED_LDAP_BIND_PASSWORD.register(PluginWeb)
class PluginAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Django REDACTED_LDAP_BIND_PASSWORD configuration for Plugin model.

    Manages Meltano plugin registry with installation tracking,
    version management, and configuration settings for all types
    of plugins (extractors, loaders, transformers, etc).

    Features:
        - Plugin type categorization
        - Installation status tracking
        - Version and variant management
        - JSON configuration editor
        - Search by name and description
    """

    list_display: ClassVar[list[str]] = [
        "name",
        "type",
        "variant",
        "version",
        "installed",
    ]
    list_filter: ClassVar[list[str]] = ["type", "installed"]
    search_fields: ClassVar[list[str]] = ["name", "description"]
    readonly_fields: ClassVar[list[str]] = ["installed_at"]

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "type", "variant", "version", "description"),
            },
        ),
        (
            "Installation",
            {
                "fields": ("installed", "installed_at"),
            },
        ),
        (
            "Configuration",
            {
                "fields": ("settings",),
            },
        ),
    )
