"""
URL configuration for FLX Web.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import REDACTED_LDAP_BIND_PASSWORD
from django.urls import include, path

urlpatterns = [
    path("REDACTED_LDAP_BIND_PASSWORD/", REDACTED_LDAP_BIND_PASSWORD.site.urls),
    path("api/", include("apps.api.urls")),
    path("pipelines/", include("apps.pipelines.urls")),
    path("monitoring/", include("apps.monitoring.urls")),
    path("", include("apps.dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug toolbar
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
