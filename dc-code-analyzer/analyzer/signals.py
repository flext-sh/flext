"""Django signals for analyzer app."""

from __future__ import annotations

import logging

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import AnalysisSession, QualityMetrics

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AnalysisSession)
def update_session_timestamps(sender, instance, created, **kwargs):
    """Update session timestamps based on status changes."""
    if not created:  # Only for updates
        if instance.status == "running" and not instance.started_at:
            instance.started_at = timezone.now()
            AnalysisSession.objects.filter(pk=instance.pk).update(
                started_at=instance.started_at,
            )
        elif (
            instance.status in {"completed", "failed", "cancelled"}
            and not instance.completed_at
        ):
            instance.completed_at = timezone.now()
            AnalysisSession.objects.filter(pk=instance.pk).update(
                completed_at=instance.completed_at,
            )


@receiver(post_save, sender=QualityMetrics)
def update_session_scores(sender, instance, created, **kwargs):
    """Update session overall score when quality metrics are saved."""
    if created or instance.session.overall_score != instance.overall_score:
        grade = _calculate_grade(instance.overall_score)
        AnalysisSession.objects.filter(pk=instance.session.pk).update(
            overall_score=instance.overall_score,
            quality_grade=grade,
        )


@receiver(pre_delete, sender=AnalysisSession)
def cleanup_analysis_files(sender, instance, **kwargs):
    """Clean up analysis files when session is deleted."""
    # This would clean up any generated files or reports
    logger.info(f"Cleaning up files for analysis session {instance.id}")


def _calculate_grade(score: float) -> str:
    """Calculate letter grade from numeric score."""
    grade_mapping = [
        (95, "A+"),
        (90, "A"),
        (85, "A-"),
        (80, "B+"),
        (75, "B"),
        (70, "B-"),
        (65, "C+"),
        (60, "C"),
        (55, "C-"),
        (50, "D"),
    ]

    for threshold, grade in grade_mapping:
        if score >= threshold:
            return grade
    return "F"
