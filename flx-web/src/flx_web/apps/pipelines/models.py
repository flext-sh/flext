"""Django models for pipeline management.

This module defines the database models for managing data pipelines,
executions, and plugins in the FLX Meltano Enterprise platform.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, ClassVar

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

if TYPE_CHECKING:
    from datetime import datetime


class PipelineWeb(models.Model):
    """Data pipeline model for ETL/ELT operations.

    Represents a data pipeline configuration including extractor,
    loader, and optional transformer components. Supports scheduling,
    configuration management, and execution tracking.

    Attributes
    ----------
        id: UUID primary key
        name: Unique pipeline name
        description: Optional pipeline description
        extractor: Name of the data extractor plugin
        loader: Name of the data loader plugin
        transform: Optional transformer plugin name
        config: JSON configuration for pipeline components
        schedule: Cron expression for scheduled execution
        is_active: Whether pipeline is enabled
        last_run: Timestamp of last execution
        last_status: Status of last execution
        created_by: User who created the pipeline
        created_at: Creation timestamp
        updated_at: Last update timestamp

    """

    id: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name: models.CharField[str, str] = models.CharField(max_length=255, unique=True)
    description: models.TextField[str, str] = models.TextField(blank=True)

    # Pipeline components
    extractor: models.CharField[str, str] = models.CharField(max_length=255)
    loader: models.CharField[str, str] = models.CharField(max_length=255)
    transform: models.CharField[str, str] = models.CharField(max_length=255, blank=True)

    # Configuration
    config: models.JSONField[dict[str, Any], dict[str, Any]] = models.JSONField(
        default=dict,
        blank=True,
    )
    schedule: models.CharField[str, str] = models.CharField(
        max_length=100,
        blank=True,
        help_text="Cron expression",
    )

    # Status
    is_active: models.BooleanField[bool, bool] = models.BooleanField(default=True)
    last_run: models.DateTimeField[datetime | None, datetime | None] = (
        models.DateTimeField(null=True, blank=True)
    )
    last_status: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        blank=True,
    )

    # Metadata
    created_by: models.ForeignKey[User, User] = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="pipelines",
    )
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        """Django model metadata configuration."""

        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of pipeline."""
        return self.name

    def get_absolute_url(self) -> str:
        """Get the absolute URL for pipeline detail view.

        Returns the URL path for accessing this pipeline's detail page
        in the Django web interface.

        Returns
        -------
            str: URL path for pipeline detail view

        """
        return reverse("pipelines: detail", kwargs={"pk": self.pk})


class Execution(models.Model):
    """Pipeline execution tracking model.

    Records individual pipeline execution instances with status tracking,
    timing information, and execution results. Links to the parent pipeline
    and tracks who triggered the execution.

    Attributes
    ----------
        id: UUID primary key
        pipeline: Foreign key to parent Pipeline
        status: Current execution status (pending/running/success/failed/cancelled)
        started_at: Execution start timestamp
        finished_at: Execution completion timestamp
        duration_seconds: Total execution time in seconds
        records_processed: Number of records processed
        error_message: Error details if execution failed
        triggered_by: User who triggered the execution
        full_refresh: Whether this was a full refresh execution

    """

    id: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    pipeline: models.ForeignKey[PipelineWeb, PipelineWeb] = models.ForeignKey(
        PipelineWeb,
        on_delete=models.CASCADE,
        related_name="executions",
    )

    # Status
    status: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )

    # Timing
    started_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        default=timezone.now,
    )
    finished_at: models.DateTimeField[datetime | None, datetime | None] = (
        models.DateTimeField(null=True, blank=True)
    )
    duration_seconds: models.IntegerField[int | None, int | None] = models.IntegerField(
        null=True,
        blank=True,
    )

    # Results
    records_processed: models.IntegerField[int, int] = models.IntegerField(default=0)
    error_message: models.TextField[str, str] = models.TextField(blank=True)

    # Metadata
    triggered_by: models.ForeignKey[User | None, User] = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="triggered_executions",
    )
    full_refresh: models.BooleanField[bool, bool] = models.BooleanField(default=False)

    class Meta:
        """Django model metadata configuration."""

        ordering: ClassVar[list[str]] = ["-started_at"]

    def __str__(self) -> str:
        """Return string representation of execution."""
        return f"{self.pipeline.name} - {self.started_at}"

    @property
    def is_running(self) -> bool:
        """Check if execution is currently running.

        Returns whether this execution is in the 'running' status,
        indicating it is actively processing.

        Returns
        -------
            bool: True if execution is running, False otherwise

        """
        return self.status == "running"

    @property
    def is_finished(self) -> bool:
        """Check if execution has finished.

        Returns whether this execution has completed with any final
        status (success, failed, or cancelled).

        Returns
        -------
            bool: True if execution is finished, False otherwise

        """
        return self.status in {"success", "failed", "cancelled"}


class PluginWeb(models.Model):
    """Meltano plugin registry model.

    Tracks installed Meltano plugins including extractors, loaders,
    transformers, orchestrators, and utilities. Manages plugin
    configuration and installation status.

    Attributes
    ----------
        name: Plugin name (e.g., 'tap-postgres', 'target-snowflake')
        type: Plugin type (extractor/loader/transformer/orchestrator/utility)
        variant: Plugin variant (e.g., 'meltano', 'singer-io')
        version: Installed version
        description: Plugin description
        installed: Whether plugin is currently installed
        installed_at: Installation timestamp
        settings: JSON configuration for plugin settings

    """

    PLUGIN_TYPES: ClassVar[list[tuple[str, str]]] = [
        ("extractor", "Extractor"),
        ("loader", "Loader"),
        ("transformer", "Transformer"),
        ("orchestrator", "Orchestrator"),
        ("utility", "Utility"),
    ]

    name: models.CharField[str, str] = models.CharField(max_length=255)
    type: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=PLUGIN_TYPES,
    )
    variant: models.CharField[str, str] = models.CharField(max_length=255, blank=True)
    version: models.CharField[str, str] = models.CharField(max_length=50, blank=True)
    description: models.TextField[str, str] = models.TextField(blank=True)

    # Installation
    installed: models.BooleanField[bool, bool] = models.BooleanField(default=False)
    installed_at: models.DateTimeField[datetime | None, datetime | None] = (
        models.DateTimeField(null=True, blank=True)
    )

    # Configuration
    settings: models.JSONField[dict[str, Any], dict[str, Any]] = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        """Django model metadata configuration."""

        unique_together: ClassVar[list[list[str]]] = [["name", "type"]]
        ordering: ClassVar[list[str]] = ["type", "name"]

    def __str__(self) -> str:
        """Return string representation of plugin."""
        return f"{self.get_type_display()}: {self.name}"
