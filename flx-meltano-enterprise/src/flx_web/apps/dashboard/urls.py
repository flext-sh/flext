"""Dashboard URL configuration."""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="index"),
    path("api/stats/", views.SystemStatsAPIView.as_view(), name="api_stats"),
]
