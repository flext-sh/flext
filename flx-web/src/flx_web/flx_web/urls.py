"""URL configuration for FLX Web Django application.

This module defines the main URL routing for the FLX Web interface,
including REDACTED_LDAP_BIND_PASSWORD interface, dashboard, and API endpoints for the
enterprise Meltano platform.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import REDACTED_LDAP_BIND_PASSWORD
from django.urls import include, path

urlpatterns = [
    path("REDACTED_LDAP_BIND_PASSWORD/", REDACTED_LDAP_BIND_PASSWORD.site.urls),
    path("pipelines/", include("flx_web.apps.pipelines.urls")),
    path("monitoring/", include("flx_web.apps.monitoring.urls")),
    path("projects/", include("flx_web.apps.projects.urls")),
    path("users/", include("flx_web.apps.users.urls")),
    path("", include("flx_web.apps.dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # ZERO TOLERANCE CONSOLIDATION: Use centralized debug toolbar import management
    from flx_core.utils.import_fallback_patterns import get_debug_toolbar

    debug_toolbar = get_debug_toolbar()
    if debug_toolbar:
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
