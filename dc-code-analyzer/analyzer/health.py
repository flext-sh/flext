"""
Health check utilities for the dc-code-analyzer application.
"""

import time
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

try:
    import redis
    from celery import current_app

    REDIS_AVAILABLE = True
    CELERY_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    CELERY_AVAILABLE = False


def check_database() -> dict[str, Any]:
    """Check database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return {
                "status": "healthy" if result[0] == 1 else "unhealthy",
                "details": "Database connection successful",
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "details": f"Database connection failed: {str(e)}",
        }


def check_cache() -> dict[str, Any]:
    """Check cache connectivity."""
    try:
        test_key = "health_check_test"
        test_value = "ok"

        cache.set(test_key, test_value, 30)
        cached_value = cache.get(test_key)

        if cached_value == test_value:
            cache.delete(test_key)
            return {"status": "healthy", "details": "Cache working properly"}
        else:
            return {"status": "unhealthy", "details": "Cache test failed"}
    except Exception as e:
        return {"status": "unhealthy", "details": f"Cache connection failed: {str(e)}"}


def check_redis() -> dict[str, Any]:
    """Check Redis connectivity."""
    if not REDIS_AVAILABLE:
        return {"status": "unknown", "details": "Redis client not available"}

    try:
        redis_url = getattr(settings, "CELERY_BROKER_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        return {"status": "healthy", "details": "Redis connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "details": f"Redis connection failed: {str(e)}"}


def check_celery() -> dict[str, Any]:
    """Check Celery worker status."""
    if not CELERY_AVAILABLE:
        return {"status": "unknown", "details": "Celery not available"}

    try:
        # Check if workers are available
        inspect = current_app.control.inspect()
        stats = inspect.stats()

        if stats:
            active_workers = len(stats)
            return {
                "status": "healthy",
                "details": f"Celery has {active_workers} active workers",
            }
        else:
            return {"status": "unhealthy", "details": "No active Celery workers found"}
    except Exception as e:
        return {"status": "unhealthy", "details": f"Celery check failed: {str(e)}"}


@csrf_exempt
@never_cache
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Comprehensive health check endpoint.
    Returns the health status of all critical services.
    """
    start_time = time.time()

    checks = {
        "database": check_database(),
        "cache": check_cache(),
        "redis": check_redis(),
        "celery": check_celery(),
    }

    # Determine overall status
    overall_status = "healthy"
    for check_result in checks.values():
        if check_result["status"] == "unhealthy":
            overall_status = "unhealthy"
            break
        elif check_result["status"] == "unknown" and overall_status == "healthy":
            overall_status = "degraded"

    response_time = time.time() - start_time

    response_data = {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time_ms": round(response_time * 1000, 2),
        "version": "1.0.0",
        "checks": checks,
        "environment": {
            "debug": settings.DEBUG,
            "python_version": f"{settings.PYTHON_VERSION}"
            if hasattr(settings, "PYTHON_VERSION")
            else "unknown",
        },
    }

    # Set HTTP status code based on health
    status_code = 200 if overall_status == "healthy" else 503

    return JsonResponse(response_data, status=status_code)


@csrf_exempt
@never_cache
@require_http_methods(["GET", "HEAD"])
def readiness_check(request):
    """
    Readiness check for Kubernetes/container orchestration.
    Returns 200 if the application is ready to serve traffic.
    """
    # Check critical services only
    db_check = check_database()

    if db_check["status"] == "healthy":
        return JsonResponse({"status": "ready"}, status=200)
    else:
        return JsonResponse(
            {"status": "not ready", "reason": db_check["details"]}, status=503
        )


@csrf_exempt
@never_cache
@require_http_methods(["GET", "HEAD"])
def liveness_check(request):
    """
    Liveness check for Kubernetes/container orchestration.
    Returns 200 if the application is alive (basic functionality works).
    """
    return JsonResponse({"status": "alive", "timestamp": time.time()}, status=200)
