"""Web Entry Point - SINGLE UNIVERSAL INTERFACE - ZERO TOLERANCE."""

from __future__ import annotations

import asyncio

from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from flx_core.universe import universal_http


@csrf_exempt
def universal_django_view(request: object, command: str) -> JsonResponse:
    """Universal Django view handling all commands."""
    body = getattr(request, "body", None)

    status, data = asyncio.run(universal_http(request.method, command, body))

    response_data = data if isinstance(data, dict) else {"result": data}
    return JsonResponse(response_data, status=status)


urlpatterns = [
    # Universal view for all commands - ZERO TOLERANCE ARCHITECTURE
    path("<path: command>", universal_django_view, name="universal"),
    path(
        "",
        lambda _: JsonResponse({"service": "FLX Universal Web", "status": "active"}),
    ),
    path("health/", lambda _: JsonResponse({"status": "healthy"})),
]

# In a real enterprise application, you'd have more robust health checks,
# dependency injection for Django, and more structured URL patterns.
