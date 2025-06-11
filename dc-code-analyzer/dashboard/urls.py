"""URL configuration for dashboard views."""

from __future__ import annotations

from django.urls import path

from . import charts, views

app_name = "dashboard"

urlpatterns = [
    # Main dashboard
    path("", views.dashboard_home, name="home"),
    path("dashboard/", views.dashboard_home, name="dashboard"),
    # Projects
    path("projects/", views.projects_list, name="projects_list"),
    path("projects/create/", views.create_project, name="create_project"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path(
        "projects/<int:project_id>/analyze/",
        views.start_analysis,
        name="start_analysis",
    ),
    # Package discovery
    path("packages/", views.packages_discovery, name="packages_discovery"),
    path(
        "packages/create/",
        views.create_project_from_package,
        name="create_project_from_package",
    ),
    path("packages/refresh/", views.refresh_packages, name="refresh_packages"),
    # Chart endpoints
    path("charts/summary-stats/", charts.dashboard_summary_stats, name="summary_stats"),
    path("charts/quality-trends/", charts.quality_trends_chart, name="quality_trends"),
    path(
        "charts/security-issues-distribution/",
        charts.security_issues_distribution,
        name="security_issues",
    ),
    path(
        "charts/projects-comparison/",
        charts.projects_comparison_chart,
        name="projects_comparison",
    ),
    path("charts/quality-radar/", charts.quality_radar_chart, name="quality_radar"),
    path(
        "charts/issues-timeline/",
        charts.issues_timeline_chart,
        name="issues_timeline",
    ),
    path(
        "charts/complexity-distribution/",
        charts.complexity_distribution_chart,
        name="complexity_distribution",
    ),
    # Analysis URLs
    path("analysis/", views.analysis_overview, name="analysis_overview"),
    path("projects/<int:project_id>/analyze/", views.run_analysis, name="run_analysis"),
    path(
        "analysis/<int:session_id>/",
        views.analysis_session_detail,
        name="analysis_session_detail",
    ),
    path(
        "analysis/<int:session_id>/hierarchical/",
        views.hierarchical_report,
        name="hierarchical_report",
    ),
    path(
        "analysis/<int:session_id>/backend-issues/",
        views.backend_issues_report,
        name="backend_issues_report",
    ),
    path(
        "analysis/<int:session_id>/packages/<int:package_id>/",
        views.package_analysis_view,
        name="package_analysis",
    ),
    path(
        "analysis/<int:session_id>/classes/<int:class_id>/",
        views.class_analysis_view,
        name="class_analysis",
    ),
    path(
        "analysis/<int:session_id>/functions/<int:function_id>/",
        views.function_analysis_view,
        name="function_analysis",
    ),
]
