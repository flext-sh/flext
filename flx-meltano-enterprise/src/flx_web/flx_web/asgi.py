"""
ASGI config for FLX Web.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flx_web.settings.production")

application = get_asgi_application()
