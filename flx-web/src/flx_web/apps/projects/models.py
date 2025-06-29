"""FLX Web Projects - Django Models.

Enterprise project management models with comprehensive lifecycle tracking.
Supports multi-tenant project organization with role-based access control.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from django.contrib.auth.models import User
from django.db import models


class ProjectTemplate(models.Model):
    """Reusable project templates for consistent project initialization."""

    id: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name: models.CharField[str, str] = models.CharField(max_length=100, unique=True)
    description: models.TextField[str, str] = models.TextField(blank=True)
    template_config: models.JSONField[dict[str, Any], dict[str, Any]] = (
        models.JSONField(default=dict)
    )
    is_active: models.BooleanField[bool, bool] = models.BooleanField(default=True)
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        """Meta configuration for ProjectTemplate model."""

        db_table = "flx_project_templates"
        ordering = ["-created_at"]
        verbose_name = "Project Template"
        verbose_name_plural = "Project Templates"

    def __str__(self) -> str:
        """Return string representation of project template."""
        return self.name


class MeltanoProject(models.Model):
    """Enterprise Meltano project with comprehensive lifecycle management."""

    id: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name: models.CharField[str, str] = models.CharField(max_length=100, unique=True)
    description: models.TextField[str, str] = models.TextField(blank=True)
    project_root: models.CharField[str, str] = models.CharField(max_length=500)
    meltano_version: models.CharField[str, str] = models.CharField(
        max_length=20,
        default="latest",
    )
    environment: models.CharField[str, str] = models.CharField(
        max_length=50,
        default="dev",
    )
    is_active: models.BooleanField[bool, bool] = models.BooleanField(default=True)
    template: models.ForeignKey[ProjectTemplate | None, ProjectTemplate] = (
        models.ForeignKey(
            ProjectTemplate,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
        )
    )
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now=True,
    )
    created_by: models.ForeignKey[User, User] = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_projects",
    )

    class Meta:
        """Meta configuration for MeltanoProject model."""

        db_table = "flx_meltano_projects"
        ordering = ["-created_at"]
        verbose_name = "Meltano Project"
        verbose_name_plural = "Meltano Projects"

    def __str__(self) -> str:
        """Return string representation of meltano project."""
        return f"{self.name} ({self.environment})"


class ProjectMembership(models.Model):
    """Project team membership with role-based access control."""

    class Role(models.TextChoices):
        """Project role enumeration."""

        VIEWER = "viewer", "Viewer"
        DEVELOPER = "developer", "Developer"
        ADMIN = "REDACTED_LDAP_BIND_PASSWORD", "Admin"
        OWNER = "owner", "Owner"

    id: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    project: models.ForeignKey[MeltanoProject, MeltanoProject] = models.ForeignKey(
        MeltanoProject,
        on_delete=models.CASCADE,
    )
    user: models.ForeignKey[User, User] = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    role: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
    )
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True,
    )
    created_by: models.ForeignKey[User, User] = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="granted_memberships",
    )

    class Meta:
        """Meta configuration for ProjectMembership model."""

        db_table = "flx_project_memberships"
        unique_together = ["project", "user"]
        ordering = ["role", "user__username"]
        verbose_name = "Project Membership"
        verbose_name_plural = "Project Memberships"

    def __str__(self) -> str:
        """Return string representation of project membership."""
        return f"{self.user.username} - {self.project.name} ({self.role})"


class ProjectDeployment(models.Model):
    """Project deployment tracking for enterprise deployment management."""

    class DeploymentStatus(models.TextChoices):
        """Deployment status enumeration."""

        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        ROLLBACK = "rollback", "Rollback"

    id: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    project: models.ForeignKey[MeltanoProject, MeltanoProject] = models.ForeignKey(
        MeltanoProject,
        on_delete=models.CASCADE,
    )
    environment: models.CharField[str, str] = models.CharField(max_length=50)
    version: models.CharField[str, str] = models.CharField(max_length=20)
    status: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=DeploymentStatus.choices,
        default=DeploymentStatus.PENDING,
    )
    deployment_config: models.JSONField[dict[str, Any], dict[str, Any]] = (
        models.JSONField(default=dict)
    )
    started_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True,
    )
    completed_at: models.DateTimeField[datetime | None, datetime | None] = (
        models.DateTimeField(null=True, blank=True)
    )
    error_message: models.TextField[str, str] = models.TextField(blank=True)
    deployed_by: models.ForeignKey[User, User] = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )

    class Meta:
        """Meta configuration for ProjectDeployment model."""

        db_table = "flx_project_deployments"
        ordering = ["-started_at"]
        verbose_name = "Project Deployment"
        verbose_name_plural = "Project Deployments"
        indexes = [
            models.Index(fields=["project", "environment"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        """Return string representation of project deployment."""
        return f"{self.project.name} → {self.environment} (v{self.version})"

    def mark_success(self) -> None:
        """Mark deployment as successful."""
        self.status = self.DeploymentStatus.SUCCESS
        self.completed_at = datetime.now()
        self.save(update_fields=["status", "completed_at"])

    def mark_failed(self, error_message: str) -> None:
        """Mark deployment as failed with error message."""
        self.status = self.DeploymentStatus.FAILED
        self.completed_at = datetime.now()
        if error_message:
            self.error_message = error_message
        self.save(update_fields=["status", "completed_at", "error_message"])
