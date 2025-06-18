"""Pipeline REDACTED_LDAP_BIND_PASSWORD configuration."""

from django.contrib import REDACTED_LDAP_BIND_PASSWORD

from .models import Execution, Pipeline, Plugin


@REDACTED_LDAP_BIND_PASSWORD.register(Pipeline)
class PipelineAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Pipeline REDACTED_LDAP_BIND_PASSWORD."""

    list_display = [
        "name",
        "extractor",
        "loader",
        "is_active",
        "last_run",
        "last_status",
    ]
    list_filter = ["is_active", "last_status", "created_at"]
    search_fields = ["name", "description", "extractor", "loader"]
    readonly_fields = ["id", "created_at", "updated_at", "last_run", "last_status"]

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
    """Execution REDACTED_LDAP_BIND_PASSWORD."""

    list_display = [
        "pipeline",
        "status",
        "started_at",
        "duration_seconds",
        "records_processed",
    ]
    list_filter = ["status", "started_at", "pipeline"]
    search_fields = ["pipeline__name", "error_message"]
    readonly_fields = ["id", "started_at", "finished_at", "duration_seconds"]

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


@REDACTED_LDAP_BIND_PASSWORD.register(Plugin)
class PluginAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Plugin REDACTED_LDAP_BIND_PASSWORD."""

    list_display = ["name", "type", "variant", "version", "installed"]
    list_filter = ["type", "installed"]
    search_fields = ["name", "description"]
    readonly_fields = ["installed_at"]

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
