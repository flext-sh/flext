"""Celery configuration for FLX Web."""

import logging
import os

from celery import Celery
from celery.app.task import Task

logger = logging.getLogger(__name__)

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flx_web.settings.production")

# Create Celery app
app = Celery("flx_web")

# Load configuration from Django settings
app.config_from_object("django.conf: settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True)  # type: ignore[misc]
def debug_task(self: Task) -> str:
    """Debug task to test Celery functionality.

    A simple task used to verify that Celery is properly configured
    and can execute tasks. Logs the task request details and returns
    a success message.

    Args:
    ----
        self: The bound task instance providing access to request metadata.

    Returns:
    -------
        str: Success message indicating task completion.

    """
    logger.info("Request: %r", self.request)
    return "Debug task completed"
