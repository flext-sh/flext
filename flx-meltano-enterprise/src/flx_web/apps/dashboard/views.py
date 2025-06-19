"""Dashboard views."""

from datetime import datetime, timezone
from typing import Any, Dict

import grpc
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from flx_web.settings import base as settings
from google.protobuf import empty_pb2

# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies



# Lazy imports to avoid circular dependencies
flx_pb2 = lazy_import("flx.grpc.proto", "flx_pb2")
flx_pb2_grpc = lazy_import("flx.grpc.proto", "flx_pb2_grpc")


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Get dashboard context data."""
        context = super().get_context_data(**kwargs)

        # Initialize default values
        context.update(
            {
                "stats": {
                    "active_pipelines": 0,
                    "total_executions": 0,
                    "success_rate": 0,
                    "cpu_usage": 0,
                    "memory_usage": 0,
                },
                "health": {
                    "healthy": True,
                    "components": {},
                },
                "recent_executions": [],
            }
        )

        try:
            # Connect to gRPC daemon
            channel = grpc.insecure_channel(
                f"{settings.FLX_GRPC_HOST}:{settings.FLX_GRPC_PORT}"
            )
            stub = flx_pb2_grpc.FlxServiceStub(channel)

            # Get system stats
            stats_response = stub.GetSystemStats(empty_pb2.Empty())

            context["stats"] = {
                "active_pipelines": stats_response.active_pipelines,
                "total_executions": stats_response.total_executions,
                "success_rate": round(stats_response.success_rate, 1),
                "cpu_usage": round(stats_response.cpu_usage, 1),
                "memory_usage": round(stats_response.memory_usage, 1),
            }

            # Get health status
            health_response = stub.HealthCheck(empty_pb2.Empty())

            components = {}
            for name, comp in health_response.components.items():
                components[name] = {
                    "healthy": comp.healthy,
                    "message": comp.message,
                    "metadata": dict(comp.metadata),
                }

            context["health"] = {
                "healthy": health_response.healthy,
                "components": components,
            }

            # Get recent executions
            executions_response = stub.ListExecutions(
                flx_pb2.ListExecutionsRequest(
                    limit=10,
                    offset=0,
                )
            )

            context["recent_executions"] = [
                {
                    "id": exec.id,
                    "pipeline_name": exec.pipeline_id,
                    "status": exec.status,
                    "started_at": (
                        exec.started_at.ToDatetime() if exec.started_at else None
                    ),
                    "duration": self._calculate_duration(exec),
                }
                for exec in executions_response.executions
            ]

        except grpc.RpcError as e:
            context["error"] = f"Unable to connect to FLX daemon: {e.details()}"

        return context

    def _calculate_duration(self, execution):
        """Calculate execution duration."""
        if not execution.started_at:
            return None

        start_time = execution.started_at.ToDatetime()

        if execution.completed_at:
            end_time = execution.completed_at.ToDatetime()
        else:
            end_time = datetime.now(timezone.utc)

        duration = end_time - start_time

        # Format duration
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class StatsAPIView(LoginRequiredMixin, View):
    """API endpoint for real-time system stats."""

    def get(self, request, *args, **kwargs):
        """Get current system stats."""
        try:
            channel = grpc.insecure_channel(
                f"{settings.FLX_GRPC_HOST}:{settings.FLX_GRPC_PORT}"
            )
            stub = flx_pb2_grpc.FlxServiceStub(channel)

            # Get system stats
            stats_response = stub.GetSystemStats(empty_pb2.Empty())

            # Get health status
            health_response = stub.HealthCheck(empty_pb2.Empty())

            # Get recent executions
            executions_response = stub.ListExecutions(
                flx_pb2.ListExecutionsRequest(
                    limit=5,
                    offset=0,
                )
            )

            # Format response
            components = {}
            for name, comp in health_response.components.items():
                components[name] = {
                    "healthy": comp.healthy,
                    "message": comp.message,
                    "metadata": dict(comp.metadata),
                }

            recent_executions = []
            for exec in executions_response.executions:
                recent_executions.append(
                    {
                        "id": exec.id,
                        "pipeline_name": exec.pipeline_id,
                        "status": exec.status,
                        "started_at": (
                            exec.started_at.ToDatetime().isoformat()
                            if exec.started_at
                            else None
                        ),
                        "duration": self._calculate_duration(exec),
                    }
                )

            return JsonResponse(
                {
                    "stats": {
                        "active_pipelines": stats_response.active_pipelines,
                        "total_executions": stats_response.total_executions,
                        "success_rate": round(stats_response.success_rate, 1),
                        "cpu_usage": round(stats_response.cpu_usage, 1),
                        "memory_usage": round(stats_response.memory_usage, 1),
                        "uptime_seconds": stats_response.uptime_seconds,
                    },
                    "health": {
                        "healthy": health_response.healthy,
                        "components": components,
                    },
                    "recent_executions": recent_executions,
                }
            )

        except grpc.RpcError as e:
            return JsonResponse(
                {
                    "error": f"gRPC error: {e.details()}",
                },
                status=503,
            )

    def _calculate_duration(self, execution):
        """Calculate execution duration."""
        if not execution.started_at:
            return None

        start_time = execution.started_at.ToDatetime()

        if execution.completed_at:
            end_time = execution.completed_at.ToDatetime()
        else:
            end_time = datetime.now(timezone.utc)

        duration = end_time - start_time

        # Format duration
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
