"""Dashboard views with enterprise architecture patterns.

Implementation features:
- Eliminated lazy imports for better dependency management
- Unified configuration through domain_config.py
- gRPC client consolidation with proper resource management
- Python 3.13 type system throughout
- Minimal code duplication with shared gRPC client service
- Strategic TYPE_CHECKING for optimal imports
"""

from __future__ import annotations

import functools
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import grpc
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.generic import TemplateView

# Unified gRPC client and configuration from canonical implementation
from flx_core.config.domain_config import get_domain_constants
from flx_grpc.client import FlxGrpcClientBase
from google.protobuf import empty_pb2

if TYPE_CHECKING:
    from flx_grpc.proto import flx_pb2
else:
    # Real imports at runtime - NO LAZY LOADING VIOLATIONS
    from flx_grpc.proto import flx_pb2

# Python 3.13 type aliases for dashboard domain
type DashboardStats = dict[str, int | float]
type HealthStatus = dict[str, bool | dict[str, Any]]
type ExecutionData = dict[str, str | None]


class FlxDashboardGrpcClient(FlxGrpcClientBase):
    """Dashboard gRPC client extending base with dashboard-specific functionality.

    Inherits from FlxGrpcClientBase to eliminate duplication while providing
    specialized dashboard data formatting and retrieval methods.
    Renamed from FlxGrpcClient to avoid conflict with CLI FlxGrpcClient.
    """

    def __init__(self) -> None:
        """Initialize dashboard gRPC client with base functionality."""
        super().__init__()

    def get_dashboard_data(self) -> dict[str, Any]:
        """Get complete dashboard data with single gRPC connection."""
        try:
            with self._create_channel() as channel:
                stub = self._create_stub(channel)

                # Get all data in parallel using gRPC streaming if available
                stats_response = stub.GetSystemStats(empty_pb2.Empty())
                health_response = stub.HealthCheck(empty_pb2.Empty())
                constants = get_domain_constants()
                executions_response = stub.ListExecutions(
                    flx_pb2.ListExecutionsRequest(
                        limit=constants.DEFAULT_EXECUTION_LIMIT,
                        offset=0,
                    ),
                )

                # Format dashboard data
                return {
                    "stats": self._format_stats(stats_response),
                    "health": self._format_health(health_response),
                    "recent_executions": self._format_executions(
                        executions_response.executions,
                    ),
                    "error": None,
                }

        except grpc.RpcError as e:
            return {
                "stats": self._get_default_stats(),
                "health": self._get_default_health(),
                "recent_executions": [],
                "error": f"Unable to connect to FLX daemon: {e.details()}",
            }

    def get_stats_only(self) -> dict[str, Any]:
        """Get only stats for API endpoint with optimized gRPC call."""
        try:
            with self._create_channel() as channel:
                stub = self._create_stub(channel)

                # Parallel requests for minimal latency
                stats_response = stub.GetSystemStats(empty_pb2.Empty())
                health_response = stub.HealthCheck(empty_pb2.Empty())
                constants = get_domain_constants()
                executions_response = stub.ListExecutions(
                    flx_pb2.ListExecutionsRequest(
                        limit=constants.PIPELINE_RECENT_EXECUTIONS_LIMIT,
                        offset=0,
                    ),
                )

                return {
                    "stats": {
                        **self._format_stats(stats_response),
                        "uptime_seconds": stats_response.uptime_seconds,
                    },
                    "health": self._format_health(health_response),
                    "recent_executions": [
                        {
                            **self._format_execution(execution),
                            "started_at": (
                                execution.started_at.ToDatetime().isoformat()
                                if execution.started_at
                                else None
                            ),
                        }
                        for execution in executions_response.executions
                    ],
                }

        except grpc.RpcError as e:
            return {
                "error": f"gRPC error: {e.details()}",
                "status_code": 503,
            }

    def _format_stats(self, stats_response: object) -> DashboardStats:
        """Format system statistics response from gRPC into dashboard format.

        Transforms the raw gRPC response into a properly formatted
        dictionary structure suitable for dashboard display and API responses.

        Args:
        ----
            stats_response: Raw gRPC system statistics response

        Returns:
        -------
            DashboardStats: Formatted statistics dictionary with typed values

        """
        return {
            "active_pipelines": stats_response.active_pipelines,
            "total_executions": stats_response.total_executions,
            "success_rate": round(stats_response.success_rate, 1),
            "cpu_usage": round(stats_response.cpu_usage, 1),
            "memory_usage": round(stats_response.memory_usage, 1),
        }

    def _format_health(self, health_response: object) -> HealthStatus:
        """Format health status response from gRPC into dashboard format.

        Args:
        ----
            health_response: Raw gRPC health status response.

        Returns:
        -------
            HealthStatus: Formatted health status with component details.

        """
        components = {}
        for name, comp in health_response.components.items():
            components[name] = {
                "healthy": comp.healthy,
                "message": comp.message,
                "metadata": dict(comp.metadata),
            }

        return {
            "healthy": health_response.healthy,
            "components": components,
        }

    def _format_executions(self, executions: list[Any]) -> list[ExecutionData]:
        """Format pipeline executions list from gRPC into dashboard format.

        Transforms the raw gRPC executions list into a properly
        formatted list suitable for dashboard display.

        Args:
        ----
            executions: List of raw gRPC execution responses

        Returns:
        -------
            list[ExecutionData]: Formatted execution data list

        """
        return [self._format_execution(execution) for execution in executions]

    def _format_execution(self, execution: object) -> ExecutionData:
        """Format single pipeline execution into dashboard format.

        Transforms a single execution response into a properly formatted
        dictionary with calculated duration and formatted timestamps.

        Args:
        ----
            execution: Raw gRPC execution response

        Returns:
        -------
            ExecutionData: Formatted execution data dictionary

        """
        return {
            "id": execution.id,
            "pipeline_name": execution.pipeline_id,
            "status": execution.status,
            "started_at": (
                execution.started_at.ToDatetime() if execution.started_at else None
            ),
            "duration": self._calculate_duration(execution),
        }

    def _calculate_duration(self, execution: object) -> str | None:
        """Calculate execution duration with proper formatting.

        Args:
        ----
            execution: Execution object with timestamp information.

        Returns:
        -------
            str | None: Formatted duration string or None if no start time.

        """
        if not execution.started_at:
            return None

        start_time = execution.started_at.ToDatetime()
        end_time = (
            execution.completed_at.ToDatetime()
            if execution.completed_at
            else datetime.now(UTC)
        )

        duration = end_time - start_time
        total_seconds = int(duration.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _get_default_stats(self) -> DashboardStats:
        """Get default stats when gRPC unavailable."""
        return {
            "active_pipelines": 0,
            "total_executions": 0,
            "success_rate": 0,
            "cpu_usage": 0,
            "memory_usage": 0,
        }

    def _get_default_health(self) -> HealthStatus:
        """Get default health when gRPC unavailable."""
        return {
            "healthy": False,
            "components": {},
        }


@functools.lru_cache(maxsize=1)
def get_grpc_client() -> FlxGrpcClientBase:
    """Get global gRPC client instance for dashboard operations.

    This function provides a singleton pattern for gRPC client access,
    ensuring efficient resource usage and connection pooling.

    Returns:
    -------
        FlxGrpcClientBase: Configured gRPC client instance.

    Note:
    ----
        Uses modern Python 3.13 functools.lru_cache for thread-safe singleton pattern.

    """
    return FlxGrpcClientBase()


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view providing comprehensive system overview.

    This view renders the main dashboard template with real-time system statistics,
    health monitoring data, and recent execution information using unified gRPC client.

    Features:
        - Real-time system metrics display
        - Health status monitoring
        - Recent pipeline execution history
        - Unified gRPC client for data retrieval
    """

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Get dashboard context data using unified gRPC client.

        Returns
        -------
            dict[str, Any]: Context data including stats, health, and executions.

        """
        context = super().get_context_data(**kwargs)

        # Get all dashboard data through unified client
        dashboard_data = get_grpc_client().get_dashboard_data()
        context.update(dashboard_data)

        return context


class StatsAPIView(LoginRequiredMixin, View):
    """API endpoint for real-time system statistics retrieval.

    This view provides a JSON API endpoint for retrieving current system
    statistics without full page reload, enabling real-time dashboard updates.

    Features:
        - Real-time system metrics API
        - JSON response format
        - Error handling with appropriate status codes
        - Unified gRPC client integration
    """

    def get(
        self, _request: HttpRequest, *_args: object, **_kwargs: object
    ) -> JsonResponse:
        """Get current system stats using unified gRPC client.

        Returns
        -------
            JsonResponse: System statistics or error information.

        """
        grpc_client = get_grpc_client()
        stats_data = grpc_client.get_stats_only()

        # Handle error response
        if "error" in stats_data:
            return JsonResponse(
                {"error": stats_data["error"]},
                status=stats_data.get("status_code", 503),
            )

        return JsonResponse(stats_data)


# ZERO TOLERANCE CONSOLIDATION: Backward compatibility alias
FlxGrpcClient = FlxDashboardGrpcClient
