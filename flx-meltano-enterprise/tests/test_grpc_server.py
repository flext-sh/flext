"""
Tests for gRPC server implementation.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import grpc
import pytest
from google.protobuf import empty_pb2

from flx.grpc.proto import flx_pb2
from flx.grpc.server import FlxServicer


@pytest.fixture
def servicer():
    """Create test servicer instance."""
    servicer = FlxServicer()
    servicer.daemon = MagicMock()
    return servicer


@pytest.fixture
async def grpc_channel():
    """Create test gRPC channel."""
    async with grpc.aio.insecure_channel("localhost:50052") as channel:
        yield channel


@pytest.mark.asyncio
async def test_health_check(servicer):
    """Test HealthCheck RPC method."""
    # Mock daemon health response
    servicer.daemon.health_check = AsyncMock(
        return_value={
            "healthy": True,
            "components": {
                "grpc": {"healthy": True, "message": "Running"},
                "database": {"healthy": True, "message": "Connected"},
            },
        }
    )

    # Call health check
    response = await servicer.HealthCheck(empty_pb2.Empty(), None)

    assert response.healthy is True
    assert len(response.components) == 2
    assert response.components["grpc"].healthy is True
    assert response.components["database"].healthy is True


@pytest.mark.asyncio
async def test_get_system_stats(servicer):
    """Test GetSystemStats RPC method."""
    # Mock daemon stats
    servicer.daemon.get_metrics = AsyncMock(
        return_value={
            "active_pipelines": 5,
            "total_executions": 1234,
            "success_rate": 95.5,
            "uptime_seconds": 3600,
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "active_connections": 10,
        }
    )

    # Call get stats
    response = await servicer.GetSystemStats(empty_pb2.Empty(), None)

    assert response.active_pipelines == 5
    assert response.total_executions == 1234
    assert response.success_rate == 95.5
    assert response.uptime_seconds == 3600
    assert response.cpu_usage == 45.2
    assert response.memory_usage == 62.8
    assert response.active_connections == 10


@pytest.mark.asyncio
async def test_create_pipeline(servicer):
    """Test CreatePipeline RPC method."""
    # Mock pipeline creation
    servicer.daemon.pipeline_manager = MagicMock()
    servicer.daemon.pipeline_manager.create_pipeline = AsyncMock(
        return_value={
            "id": "test-pipeline-123",
            "name": "Test Pipeline",
            "type": "extract_load",
            "config": {"source": "test", "destination": "test"},
            "schedule": "0 * * * *",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    )

    # Create request
    request = flx_pb2.CreatePipelineRequest(
        name="Test Pipeline",
        type="extract_load",
        config={"source": "test", "destination": "test"},
        schedule="0 * * * *",
    )

    # Call create pipeline
    response = await servicer.CreatePipeline(request, None)

    assert response.id == "test-pipeline-123"
    assert response.name == "Test Pipeline"
    assert response.type == "extract_load"
    assert response.is_active is True


@pytest.mark.asyncio
async def test_run_pipeline(servicer):
    """Test RunPipeline RPC method."""
    # Mock pipeline execution
    servicer.daemon.pipeline_manager = MagicMock()
    servicer.daemon.pipeline_manager.run_pipeline = AsyncMock(
        return_value={
            "id": "exec-123",
            "pipeline_id": "pipeline-123",
            "status": "running",
            "started_at": "2024-01-01T00:00:00Z",
            "logs": [],
        }
    )

    # Create request
    request = flx_pb2.RunPipelineRequest(
        pipeline_id="pipeline-123",
        parameters={"force": "true"},
    )

    # Call run pipeline
    response = await servicer.RunPipeline(request, None)

    assert response.id == "exec-123"
    assert response.pipeline_id == "pipeline-123"
    assert response.status == "running"


@pytest.mark.asyncio
async def test_list_pipelines(servicer):
    """Test ListPipelines RPC method."""
    # Mock pipeline list
    servicer.daemon.pipeline_manager = MagicMock()
    servicer.daemon.pipeline_manager.list_pipelines = AsyncMock(
        return_value={
            "pipelines": [
                {
                    "id": "pipeline-1",
                    "name": "Pipeline 1",
                    "type": "extract_load",
                    "is_active": True,
                },
                {
                    "id": "pipeline-2",
                    "name": "Pipeline 2",
                    "type": "transform",
                    "is_active": False,
                },
            ],
            "total": 2,
        }
    )

    # Create request
    request = flx_pb2.ListPipelinesRequest(
        limit=10,
        offset=0,
    )

    # Call list pipelines
    response = await servicer.ListPipelines(request, None)

    assert len(response.pipelines) == 2
    assert response.pipelines[0].id == "pipeline-1"
    assert response.pipelines[1].id == "pipeline-2"


@pytest.mark.asyncio
async def test_stream_logs(servicer):
    """Test StreamLogs RPC method."""

    # Mock log streaming
    async def mock_stream_logs(execution_id):
        logs = [
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "level": "INFO",
                "message": "Starting pipeline",
            },
            {
                "timestamp": "2024-01-01T00:00:01Z",
                "level": "INFO",
                "message": "Processing data",
            },
            {
                "timestamp": "2024-01-01T00:00:02Z",
                "level": "INFO",
                "message": "Pipeline completed",
            },
        ]
        for log in logs:
            yield log
            await asyncio.sleep(0.1)

    servicer.daemon.pipeline_manager = MagicMock()
    servicer.daemon.pipeline_manager.stream_logs = mock_stream_logs

    # Create request
    request = flx_pb2.StreamLogsRequest(
        execution_id="exec-123",
    )

    # Call stream logs
    logs = []
    async for log in servicer.StreamLogs(request, None):
        logs.append(log)

    assert len(logs) == 3
    assert logs[0].message == "Starting pipeline"
    assert logs[1].message == "Processing data"
    assert logs[2].message == "Pipeline completed"


@pytest.mark.asyncio
async def test_error_handling(servicer):
    """Test gRPC error handling."""
    # Mock a method that raises an exception
    servicer.daemon.pipeline_manager = MagicMock()
    servicer.daemon.pipeline_manager.get_pipeline = AsyncMock(
        side_effect=ValueError("Pipeline not found")
    )

    # Create request
    request = flx_pb2.GetPipelineRequest(id="nonexistent")

    # Call should raise gRPC error
    context = MagicMock()
    with pytest.raises(ValueError, match="Pipeline not found"):
        await servicer.GetPipeline(request, context)


@pytest.mark.asyncio
async def test_concurrent_requests(servicer):
    """Test handling concurrent gRPC requests."""
    # Mock methods
    servicer.daemon.health_check = AsyncMock(
        return_value={"healthy": True, "components": {}}
    )
    servicer.daemon.get_metrics = AsyncMock(
        return_value={
            "active_pipelines": 5,
            "total_executions": 100,
            "success_rate": 95.0,
            "uptime_seconds": 3600,
            "cpu_usage": 50.0,
            "memory_usage": 60.0,
            "active_connections": 5,
        }
    )

    # Make concurrent requests
    tasks = []
    for _ in range(10):
        tasks.append(servicer.HealthCheck(empty_pb2.Empty(), None))
        tasks.append(servicer.GetSystemStats(empty_pb2.Empty(), None))

    responses = await asyncio.gather(*tasks)

    # Verify all requests succeeded
    assert len(responses) == 20
    health_responses = [r for r in responses if hasattr(r, "healthy")]
    stats_responses = [r for r in responses if hasattr(r, "active_pipelines")]

    assert len(health_responses) == 10
    assert len(stats_responses) == 10
    assert all(r.healthy for r in health_responses)
    assert all(r.active_pipelines == 5 for r in stats_responses)
