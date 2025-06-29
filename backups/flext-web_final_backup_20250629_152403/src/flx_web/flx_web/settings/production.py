"""Production settings for FLX Meltano Enterprise Web application.

This module provides production-specific Django settings with security hardening,
logging configuration, and optimizations for production deployment.

Features:
    - Security headers and SSL configuration
    - Production logging with file rotation and compression
    - Type-safe logging configuration with structured logs
    - Secure cookie settings with SameSite protection
    - HSTS security headers for transport security
    - CSRF protection with secure tokens
    - Content type sniffing protection
"""

from __future__ import annotations

import copy
from typing import Any

from flx_core.config.domain_config import get_config

from flx_web.base import *

# Security settings
DEBUG = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# Get HSTS settings from unified domain configuration
_security_config = get_config()
SECURE_HSTS_SECONDS = _security_config.security.hsts_max_age_seconds
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ALLOWED_HOSTS is now configured through unified domain configuration
# See flx_core.config.domain_config.py for centralized configuration management

# Email configuration migrated to unified domain configuration
# All email settings are now managed through the enterprise configuration system
# located in flx_core.config.domain_config.py for consistency and maintainability

# Production logging - Type-safe LOGGING configuration
# Get the base LOGGING config imported from base.py and create a typed copy
_BASE_LOGGING: dict[str, Any] = locals()["LOGGING"]
_LOGGING_CONFIG: dict[str, Any] = copy.deepcopy(_BASE_LOGGING)

# Add file handler configuration
_LOGGING_CONFIG["handlers"]["file"] = {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": "/var/log/flx-web/django.log",
    "maxBytes": _security_config.monitoring.max_log_file_size_mb * 1024 * 1024,
    "backupCount": _security_config.monitoring.log_file_backup_count,
    "formatter": "verbose",
}

# Type-safe handler list operations
_root_handlers: list[str] = _LOGGING_CONFIG["root"]["handlers"]
_root_handlers.append("file")

_django_handlers: list[str] = _LOGGING_CONFIG["loggers"]["django"]["handlers"]
_django_handlers.append("file")

_flx_web_handlers: list[str] = _LOGGING_CONFIG["loggers"]["flx_web"]["handlers"]
_flx_web_handlers.append("file")

# Reassign to module-level LOGGING for Django
LOGGING = _LOGGING_CONFIG
