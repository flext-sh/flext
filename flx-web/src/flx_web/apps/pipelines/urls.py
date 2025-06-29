"""URL patterns for pipeline management web interface.

This module defines the URL routing configuration for the pipeline management
functionality within the FLX web application, providing RESTful endpoints
for pipeline operations.
"""

from django.urls import path

from flx_web.views import PipelineDetailView, PipelineListView

app_name = "pipelines"

urlpatterns = [
    path("", PipelineListView.as_view(), name="list"),
    path("<uuid: pipeline_id>/", PipelineDetailView.as_view(), name="detail"),
]
