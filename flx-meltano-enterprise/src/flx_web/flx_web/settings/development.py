"""Development settings."""

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Additional apps for development
INSTALLED_APPS += [
    "debug_toolbar",
]

# Additional middleware for development
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Debug toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable caching in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
