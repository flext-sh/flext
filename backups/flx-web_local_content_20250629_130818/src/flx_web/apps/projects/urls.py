"""FLX Projects URL Configuration - Enterprise Project Management.

This module defines URL patterns for the FLX Projects app,
providing RESTful endpoints for enterprise project management operations.

Author: Datacosmos
Date: 2025-06-22
"""

from __future__ import annotations

from django.urls import path

from flx_web import views

app_name = "projects"

urlpatterns = [
    # Project management views
    path("", views.ProjectListView.as_view(), name="list"),
    path("create/", views.ProjectCreateView.as_view(), name="create"),
    path("<uuid: pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("<uuid: pk>/edit/", views.ProjectUpdateView.as_view(), name="update"),
    path("<uuid: pk>/delete/", views.ProjectDeleteView.as_view(), name="delete"),
    # Project operations
    path("<uuid: pk>/deploy/", views.ProjectDeployView.as_view(), name="deploy"),
    path("<uuid: pk>/members/", views.ProjectMembersView.as_view(), name="members"),
    path(
        "<uuid: pk>/deployments/",
        views.ProjectDeploymentsView.as_view(),
        name="deployments",
    ),
    # Template management
    path("templates/", views.TemplateListView.as_view(), name="template-list"),
    path(
        "templates/create/",
        views.TemplateCreateView.as_view(),
        name="template-create",
    ),
    path(
        "templates/<uuid: pk>/",
        views.TemplateDetailView.as_view(),
        name="template-detail",
    ),
    # API endpoints
    path("api/projects/", views.ProjectAPIView.as_view(), name="api-projects"),
    path(
        "api/projects/<uuid: pk>/status/",
        views.ProjectStatusAPIView.as_view(),
        name="api-project-status",
    ),
    path("api/deployments/", views.DeploymentAPIView.as_view(), name="api-deployments"),
]
