"""URL configuration for Code Analyzer Web Interface flx_project."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/v1/analyzer/", include("analyzer.urls")),
    # Dashboard views
    path("", include("dashboard.urls")),
    # Redirect root to dashboard
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Add Django Debug Toolbar if installed
    try:
        import debug_toolbar  # type: ignore[import-not-found]

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass

# Customize admin site
admin.site.site_header = "Code Analyzer Administration"
admin.site.site_title = "Code Analyzer Admin"
admin.site.index_title = "Welcome to Code Analyzer Administration"
