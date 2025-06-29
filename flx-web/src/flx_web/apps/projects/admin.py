"""FLX Projects Django Admin Configuration - Enterprise Administration.

This module configures Django REDACTED_LDAP_BIND_PASSWORD interface for enterprise project management,
providing comprehensive REDACTED_LDAP_BIND_PASSWORDistrative capabilities for production environments.

Author: Datacosmos
Date: 2025-06-22
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django.contrib import REDACTED_LDAP_BIND_PASSWORD
from django.utils.html import format_html

from flx_web.models import (
    MeltanoProject,
    ProjectDeployment,
    ProjectMembership,
    ProjectTemplate,
)

if TYPE_CHECKING:
    from django.forms import ModelForm
    from django.http import HttpRequest


@REDACTED_LDAP_BIND_PASSWORD.register(ProjectTemplate)
class ProjectTemplateAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Django REDACTED_LDAP_BIND_PASSWORD configuration for ProjectTemplate model.

    Provides comprehensive template management with enterprise features
    including versioning, category filtering, and template validation.
    """

    list_display: ClassVar[list[str]] = [
        "name",
        "category",
        "version",
        "is_active",
        "created_at",
        "created_by",
    ]
    list_filter: ClassVar[list[str]] = ["category", "is_active", "created_at"]
    search_fields: ClassVar[list[str]] = ["name", "description", "category"]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "description", "category", "version", "is_active")},
        ),
        (
            "Template Configuration",
            {
                "fields": (
                    "config_template",
                    "plugins_template",
                    "environments_template",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("id", "created_at", "updated_at", "created_by"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(
        self,
        request: HttpRequest,
        obj: ProjectTemplate,
        form: ModelForm,
        *,
        change: bool,
    ) -> None:
        """Save template with current user as creator for new templates."""
        if not change:  # Creating new template
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ProjectMembershipInline(REDACTED_LDAP_BIND_PASSWORD.TabularInline):
    r"""ProjectMembershipInline - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    extra (ClassVar[int]): Atributo da classe.
    readonly_fields (ClassVar[list[str]]): Atributo da classe.

    Methods:
    save_model(): Salva dados

    Examples:
    Uso típico da classe:

    ```python
    instance = ProjectMembershipInline()\n    result = instance.method()
    ```

    See Also:
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Inline REDACTED_LDAP_BIND_PASSWORD for project memberships."""

    model = ProjectMembership
    extra: ClassVar[int] = 0
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "created_by"]

    def save_model(
        self,
        request: HttpRequest,
        obj: ProjectMembership,
        form: ModelForm,
        *,
        change: bool,
    ) -> None:
        """Save membership with current user as creator for new memberships."""
        if not change:  # Creating new membership
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ProjectDeploymentInline(REDACTED_LDAP_BIND_PASSWORD.TabularInline):
    r"""ProjectDeploymentInline - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    extra (ClassVar[int]): Atributo da classe.
    readonly_fields (ClassVar[list[str]]): Atributo da classe.
    fields (ClassVar[list[str]]): Atributo da classe.

    Methods:
    duration_display(): Método específico da classe

    Examples:
    Uso típico da classe:

    ```python
    instance = ProjectDeploymentInline()\n    result = instance.method()
    ```

    See Also:
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Inline REDACTED_LDAP_BIND_PASSWORD for project deployments."""

    model = ProjectDeployment
    extra: ClassVar[int] = 0
    readonly_fields: ClassVar[list[str]] = [
        "id",
        "started_at",
        "completed_at",
        "duration_display",
        "deployed_by",
    ]
    fields: ClassVar[list[str]] = [
        "environment",
        "version",
        "status",
        "duration_display",
        "deployed_by",
    ]

    def duration_display(self, obj: ProjectDeployment) -> str:
        """Display deployment duration in human-readable format."""
        if obj.duration_seconds is not None:
            minutes, seconds = divmod(obj.duration_seconds, 60)
            return f"{minutes}m {seconds}s"
        return "N/A"

    duration_display.short_description = "Duration"


@REDACTED_LDAP_BIND_PASSWORD.register(MeltanoProject)
class MeltanoProjectAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Django REDACTED_LDAP_BIND_PASSWORD configuration for MeltanoProject model.

    Provides comprehensive project management with enterprise features
    including team management, deployment tracking, and project statistics.
    """

    list_display: ClassVar[list[str]] = [
        "display_name",
        "name",
        "status_badge",
        "owner",
        "total_pipelines",
        "total_plugins",
        "last_deployed_at",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = [
        "status",
        "default_environment",
        "created_at",
        "template",
    ]
    search_fields: ClassVar[list[str]] = [
        "name",
        "display_name",
        "description",
        "owner__username",
    ]
    readonly_fields: ClassVar[list[str]] = [
        "id",
        "created_at",
        "updated_at",
        "last_deployed_at",
        "total_pipelines",
        "total_plugins",
        "last_execution_count",
    ]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "display_name", "description", "status", "template")},
        ),
        (
            "Configuration",
            {
                "fields": (
                    "meltano_version",
                    "project_path",
                    "repository_url",
                    "default_environment",
                ),
            },
        ),
        ("Team Management", {"fields": ("owner",)}),
        (
            "Environment Configuration",
            {"fields": ("environments",), "classes": ("collapse",)},
        ),
        (
            "Statistics",
            {
                "fields": ("total_pipelines", "total_plugins", "last_execution_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("id", "created_at", "updated_at", "last_deployed_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines: ClassVar[list[type[REDACTED_LDAP_BIND_PASSWORD.TabularInline]]] = [
        ProjectMembershipInline,
        ProjectDeploymentInline,
    ]

    def status_badge(self, obj: MeltanoProject) -> str:
        """Display project status with color-coded badge."""
        color_map = {
            "draft": "gray",
            "active": "green",
            "paused": "orange",
            "archived": "blue",
            "deleted": "red",
        }
        color = color_map.get(obj.status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def save_model(
        self,
        request: HttpRequest,
        obj: MeltanoProject,
        form: ModelForm,
        *,
        change: bool,
    ) -> None:
        """Save project with current user as owner for new projects."""
        if not change:  # Creating new project
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@REDACTED_LDAP_BIND_PASSWORD.register(ProjectMembership)
class ProjectMembershipAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Django REDACTED_LDAP_BIND_PASSWORD configuration for ProjectMembership model.

    Provides team membership management with role-based access control
    and comprehensive audit trails for security compliance.
    """

    list_display: ClassVar[list[str]] = [
        "user",
        "project",
        "role",
        "created_at",
        "created_by",
    ]
    list_filter: ClassVar[list[str]] = ["role", "created_at", "project__status"]
    search_fields: ClassVar[list[str]] = [
        "user__username",
        "user__email",
        "project__name",
        "project__display_name",
    ]
    readonly_fields: ClassVar[list[str]] = ["id", "created_at", "created_by"]

    fieldsets = (
        ("Membership Details", {"fields": ("project", "user", "role")}),
        (
            "Metadata",
            {"fields": ("id", "created_at", "created_by"), "classes": ("collapse",)},
        ),
    )

    def save_model(
        self,
        request: HttpRequest,
        obj: ProjectMembership,
        form: ModelForm,
        *,
        change: bool,
    ) -> None:
        """Save membership with current user as creator for new memberships."""
        if not change:  # Creating new membership
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@REDACTED_LDAP_BIND_PASSWORD.register(ProjectDeployment)
class ProjectDeploymentAdmin(REDACTED_LDAP_BIND_PASSWORD.ModelAdmin):
    """Django REDACTED_LDAP_BIND_PASSWORD configuration for ProjectDeployment model.

    Provides deployment tracking and management with comprehensive
    audit trails and deployment history for enterprise compliance.
    """

    list_display: ClassVar[list[str]] = [
        "project",
        "environment",
        "version",
        "status_badge",
        "deployed_by",
        "started_at",
        "duration_display",
    ]
    list_filter: ClassVar[list[str]] = ["status", "environment", "started_at"]
    search_fields: ClassVar[list[str]] = [
        "project__name",
        "project__display_name",
        "version",
        "commit_hash",
        "branch_name",
    ]
    readonly_fields: ClassVar[list[str]] = [
        "id",
        "started_at",
        "completed_at",
        "duration_display",
        "deployed_by",
    ]

    fieldsets = (
        (
            "Deployment Information",
            {"fields": ("project", "environment", "version", "status")},
        ),
        ("Source Code", {"fields": ("commit_hash", "branch_name")}),
        ("Configuration", {"fields": ("deployment_config",), "classes": ("collapse",)}),
        (
            "Logs and Errors",
            {"fields": ("deployment_logs", "error_message"), "classes": ("collapse",)},
        ),
        (
            "Metadata",
            {
                "fields": (
                    "id",
                    "started_at",
                    "completed_at",
                    "duration_display",
                    "deployed_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def status_badge(self, obj: ProjectDeployment) -> str:
        """Display deployment status with color-coded badge."""
        color_map = {
            "pending": "orange",
            "in_progress": "blue",
            "success": "green",
            "failed": "red",
            "rolled_back": "purple",
        }
        color = color_map.get(obj.status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def duration_display(self, obj: ProjectDeployment) -> str:
        """Display deployment duration in human-readable format."""
        if obj.duration_seconds is not None:
            minutes, seconds = divmod(obj.duration_seconds, 60)
            return f"{minutes}m {seconds}s"
        return "N/A"

    duration_display.short_description = "Duration"

    def save_model(
        self,
        request: HttpRequest,
        obj: ProjectDeployment,
        form: ModelForm,
        *,
        change: bool,
    ) -> None:
        """Save deployment with current user as deployer for new deployments."""
        if not change:  # Creating new deployment
            obj.deployed_by = request.user
        super().save_model(request, obj, form, change)
