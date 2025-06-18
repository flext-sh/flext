"""Production settings."""

from .base import *  # noqa

# Security settings
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Allowed hosts must be set in environment
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # noqa: F405

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("FLX_EMAIL_HOST")  # noqa: F405
EMAIL_PORT = env("FLX_EMAIL_PORT")  # noqa: F405
EMAIL_HOST_USER = env("FLX_EMAIL_USER")  # noqa: F405
EMAIL_HOST_PASSWORD = env("FLX_EMAIL_PASSWORD")  # noqa: F405
EMAIL_USE_TLS = env("FLX_EMAIL_USE_TLS")  # noqa: F405
DEFAULT_FROM_EMAIL = env("FLX_EMAIL_FROM", default="noreply@flx.io")  # noqa: F405

# Production logging
LOGGING["handlers"]["file"] = {  # noqa: F405
    "class": "logging.handlers.RotatingFileHandler",
    "filename": "/var/log/flx-web/django.log",
    "maxBytes": 1024 * 1024 * 100,  # 100MB
    "backupCount": 10,
    "formatter": "verbose",
}

LOGGING["root"]["handlers"].append("file")  # noqa: F405
LOGGING["loggers"]["django"]["handlers"].append("file")  # noqa: F405
LOGGING["loggers"]["flx_web"]["handlers"].append("file")  # noqa: F405
