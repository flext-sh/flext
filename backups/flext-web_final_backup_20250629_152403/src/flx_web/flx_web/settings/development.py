"""Development settings for FLX Meltano Enterprise Web application.

This module provides development-specific Django settings that extend the base
configuration with debugging tools and development-friendly features.

Features:
    - Debug mode enabled with detailed error pages
    - Django Debug Toolbar for performance profiling
    - Console email backend for testing email functionality
    - Permissive CORS settings for frontend development
    - Dummy caching to avoid Redis dependency in development
    - Hot reloading support for template and static file changes

Warning:
-------
    These settings should NEVER be used in production environments
    as they expose sensitive debugging information.


"""

from flx_web.base import *

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
    config.network.host,
    "localhost",  # Fallback for development
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable caching in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}
