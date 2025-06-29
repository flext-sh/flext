"""ASGI configuration module for FLX Web application.

This module configures the Asynchronous Server Gateway Interface (ASGI) for the FLX Web
Django application, enabling support for asynchronous views, WebSockets, and other
async protocols. It provides the entry point for ASGI-compatible servers like
Uvicorn, Daphne, or Hypercorn to serve the Django application.

The module sets up the Django settings module environment variable and exposes the ASGI
application callable that servers use to communicate with the Django application.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flx_web.settings.production")

application = get_asgi_application()
