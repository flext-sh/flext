"""Base Django settings module for FLX Web application.

This module provides the foundational Django configuration that is shared across all
deployment environments (development, staging, production). It integrates with the
FLX domain configuration system to maintain a single source of truth for all settings,
following the Zero Tolerance architectural principles.

The settings are organized into logical sections:
- Core Django configuration (security, middleware, installed apps)
- Database and caching configuration from domain config
- Static and media file handling with WhiteNoise
- REST Framework API configuration
- CORS (Cross-Origin Resource Sharing) settings
- Celery task queue configuration
- Logging configuration from domain config

All environment-specific values are retrieved from the unified domain configuration
to prevent configuration duplication and ensure consistency across the FLX platform.
"""

import os
from pathlib import Path

# Get unified domain configuration
from flx_core.config.django_integration import get_complete_django_settings
from flx_core.config.domain_config import get_config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Get ALL Django settings from unified domain configuration
domain_django_settings = get_complete_django_settings()
config = get_config()

# Extract core settings
SECRET_KEY = domain_django_settings["SECRET_KEY"]
DEBUG = domain_django_settings["DEBUG"]
ALLOWED_HOSTS = domain_django_settings["ALLOWED_HOSTS"]

# Application definition
INSTALLED_APPS = [
    # Django Core
    "django.contrib.REDACTED_LDAP_BIND_PASSWORD",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party apps
    "corsheaders",
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_celery_beat",
    "django_celery_results",
    "django_extensions",
    # Local apps - FLX Enterprise Applications by Datacosmos
    "flx_web.apps.dashboard",
    "flx_web.apps.pipelines",
    "flx_web.apps.monitoring",  # Enterprise system monitoring
    "flx_web.apps.projects",  # Enterprise project management
    "flx_web.apps.users",  # Enterprise user management
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "flx_web.flx_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "flx_web.wsgi.application"
ASGI_APPLICATION = "flx_web.asgi.application"

# Database - from unified domain configuration
DATABASES = domain_django_settings["DATABASES"]

# Cache - from unified domain configuration
CACHES = domain_django_settings["CACHES"]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization - from unified domain configuration
LANGUAGE_CODE = domain_django_settings["LANGUAGE_CODE"]
TIME_ZONE = domain_django_settings["TIME_ZONE"]
USE_I18N = domain_django_settings["USE_I18N"]
USE_TZ = domain_django_settings["USE_TZ"]

# Static files (CSS, JavaScript, Images) - from unified domain configuration
STATIC_URL = domain_django_settings["STATIC_URL"]
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", str(BASE_DIR / "staticfiles"))
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files - from unified domain configuration
MEDIA_URL = domain_django_settings["MEDIA_URL"]
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type - from unified domain configuration
DEFAULT_AUTO_FIELD = domain_django_settings["DEFAULT_AUTO_FIELD"]

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": config.api["default_page_size"],
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

# CORS settings - from unified domain configuration
CORS_ALLOWED_ORIGINS = domain_django_settings["CORS_ALLOWED_ORIGINS"]
CORS_ALLOW_ALL_ORIGINS = domain_django_settings["CORS_ALLOW_ALL_ORIGINS"]
CORS_ALLOW_CREDENTIALS = domain_django_settings["CORS_ALLOW_CREDENTIALS"]

# Celery Configuration - integrated with unified domain configuration
CELERY_BROKER_URL = os.environ.get(
    "FLX_CELERY_BROKER_URL",
    f"redis://{config.network.redis_host}:{config.network.redis_port}/{config.network.celery_broker_db}",
)
CELERY_RESULT_BACKEND = os.environ.get(
    "FLX_CELERY_RESULT_BACKEND",
    f"redis://{config.network.redis_host}:{config.network.redis_port}/{config.network.celery_result_db}",
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = domain_django_settings["TIME_ZONE"]
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = (
    config.meltano.celery_timeout_minutes * 60
)  # From domain configuration
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers: DatabaseScheduler"

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# FLX Settings - from unified domain configuration
FLX_GRPC_HOST = domain_django_settings["FLX_GRPC_HOST"]
FLX_GRPC_PORT = domain_django_settings["FLX_GRPC_PORT"]
FLX_API_PORT = domain_django_settings["FLX_API_PORT"]
FLX_WEB_PORT = domain_django_settings["FLX_WEB_PORT"]
FLX_WEBSOCKET_PORT = domain_django_settings["FLX_WEBSOCKET_PORT"]

# Logging - from unified domain configuration
LOGGING = domain_django_settings["LOGGING"]
