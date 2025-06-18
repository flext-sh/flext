"""Pipeline models."""

import uuid

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Pipeline(models.Model):
    """Pipeline model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Pipeline components
    extractor = models.CharField(max_length=255)
    loader = models.CharField(max_length=255)
    transform = models.CharField(max_length=255, blank=True)

    # Configuration
    config = models.JSONField(default=dict, blank=True)
    schedule = models.CharField(max_length=100, blank=True, help_text="Cron expression")

    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(
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
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="pipelines"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("pipelines:detail", kwargs={"pk": self.pk})


class Execution(models.Model):
    """Pipeline execution model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, related_name="executions"
    )

    # Status
    status = models.CharField(
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
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    # Results
    records_processed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    # Metadata
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="triggered_executions",
    )
    full_refresh = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.pipeline.name} - {self.started_at}"

    @property
    def is_running(self):
        return self.status == "running"

    @property
    def is_finished(self):
        return self.status in ["success", "failed", "cancelled"]


class Plugin(models.Model):
    """Installed plugin model."""

    PLUGIN_TYPES = [
        ("extractor", "Extractor"),
        ("loader", "Loader"),
        ("transformer", "Transformer"),
        ("orchestrator", "Orchestrator"),
        ("utility", "Utility"),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=PLUGIN_TYPES)
    variant = models.CharField(max_length=255, blank=True)
    version = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    # Installation
    installed = models.BooleanField(default=False)
    installed_at = models.DateTimeField(null=True, blank=True)

    # Configuration
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [["name", "type"]]
        ordering = ["type", "name"]

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"
