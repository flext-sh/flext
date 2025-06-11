"""URL configuration for analyzer API."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalysisSessionViewSet,
    DeadCodeIssueViewSet,
    DuplicateCodeBlockViewSet,
    FileAnalysisViewSet,
    ProjectViewSet,
    QualityMetricsViewSet,
    SecurityIssueViewSet,
    analysis_session_detail,
    create_project_from_package,
    dashboard_view,
    generate_report,
    packages_discovery,
    project_detail,
    refresh_packages,
    start_analysis,
    view_report,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"sessions", AnalysisSessionViewSet)
router.register(r"files", FileAnalysisViewSet)
router.register(r"security-issues", SecurityIssueViewSet)
router.register(r"dead-code", DeadCodeIssueViewSet)
router.register(r"duplicates", DuplicateCodeBlockViewSet)
router.register(r"metrics", QualityMetricsViewSet)

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
    # Web interface
    path("", dashboard_view, name="dashboard"),
    path("packages/", packages_discovery, name="packages_discovery"),
    path(
        "packages/create/",
        create_project_from_package,
        name="create_project_from_package",
    ),
    path("packages/refresh/", refresh_packages, name="refresh_packages"),
    # Project views
    path("flx_project/<int:project_id>/", project_detail, name="project_detail"),
    path(
        "flx_project/<int:project_id>/analyze/",
        start_analysis,
        name="start_analysis",
    ),
    # Analysis session views
    path(
        "session/<int:session_id>/",
        analysis_session_detail,
        name="analysis_session_detail",
    ),
    path("session/<int:session_id>/report/", generate_report, name="generate_report"),
    path("session/<int:session_id>/view-report/", view_report, name="view_report"),
]
