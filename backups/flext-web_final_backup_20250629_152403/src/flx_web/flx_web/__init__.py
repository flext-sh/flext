"""FLX Web main package for Django web application.

This module provides the main package initialization for the FLX Meltano Enterprise
web application, setting up Celery integration and ensuring proper app startup.

Features:
    - Celery app integration for async task processing
    - Django app initialization
    - Shared task setup for distributed processing

Note:
----
    Initializes Django web application with Celery integration for distributed task processing.


"""

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from flx_web.celery import app as celery_app

__all__ = ("celery_app",)
