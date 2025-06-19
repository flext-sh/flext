"""
Monitoring and health endpoints.
"""

import grpc
from fastapi import APIRouter, Depends, HTTPException, status
from flx_api.dependencies import get_grpc_stub
from flx_api.models.monitoring import HealthResponse, SystemStatsResponse
from google.protobuf import empty_pb2
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies


# Lazy import to avoid circular dependencies
flx_pb2_grpc = lazy_import('flx.grpc.proto', 'flx_pb2_grpc')

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
):
    """Check system health."""
    try:
        health = await stub.HealthCheck(empty_pb2.Empty())

        components = {}
        for name, component in health.components.items():
            components[name] = {
                "healthy": component.healthy,
                "message": component.message,
                "metadata": dict(component.metadata),
            }

        return HealthResponse(
            healthy=health.healthy,
            components=components,
            timestamp=health.timestamp.ToDatetime(),
        )

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    stub: flx_pb2_grpc.FlxServiceStub = Depends(get_grpc_stub),
):
    """Get system statistics."""
    try:
        stats = await stub.GetSystemStats(empty_pb2.Empty())

        return SystemStatsResponse(
            active_pipelines=stats.active_pipelines,
            total_executions=stats.total_executions,
            success_rate=stats.success_rate,
            uptime_seconds=stats.uptime_seconds,
            cpu_usage=stats.cpu_usage,
            memory_usage=stats.memory_usage,
            active_connections=stats.active_connections,
        )

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"gRPC error: {e.details()}",
        )
