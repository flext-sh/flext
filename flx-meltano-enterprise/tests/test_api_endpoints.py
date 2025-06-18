"""
Tests for FastAPI endpoints.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from flx_api.dependencies import get_current_user, get_grpc_stub
from flx_api.main import app
from flx_api.models.auth import User

# Mock user for authentication
mock_user = User(
    id="user-123",
    username="testuser",
    email="test@example.com",
    is_active=True,
)

# Mock gRPC stub
mock_stub = MagicMock()


# Override dependencies
app.dependency_overrides[get_current_user] = lambda: mock_user
app.dependency_overrides[get_grpc_stub] = lambda: mock_stub


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FLX Enterprise API"
    assert "version" in data
    assert "docs" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    # Mock health response
    mock_health = MagicMock()
    mock_health.healthy = True
    mock_health.components = {
        "grpc": MagicMock(healthy=True, message="Running"),
        "database": MagicMock(healthy=True, message="Connected"),
    }
    mock_health.timestamp = MagicMock()
    mock_health.timestamp.ToDatetime.return_value = "2024-01-01T00:00:00Z"

    mock_stub.HealthCheck = AsyncMock(return_value=mock_health)

    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["healthy"] is True
    assert "components" in data
    assert data["components"]["grpc"]["healthy"] is True


def test_stats_endpoint(client):
    """Test system stats endpoint."""
    # Mock stats response
    mock_stats = MagicMock()
    mock_stats.active_pipelines = 5
    mock_stats.total_executions = 100
    mock_stats.success_rate = 95.5
    mock_stats.uptime_seconds = 3600
    mock_stats.cpu_usage = 45.2
    mock_stats.memory_usage = 62.8
    mock_stats.active_connections = 10

    mock_stub.GetSystemStats = AsyncMock(return_value=mock_stats)

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["active_pipelines"] == 5
    assert data["total_executions"] == 100
    assert data["success_rate"] == 95.5


def test_list_pipelines(client):
    """Test list pipelines endpoint."""
    # Mock pipeline list response
    mock_response = MagicMock()
    mock_pipeline1 = MagicMock()
    mock_pipeline1.id = "pipeline-1"
    mock_pipeline1.name = "Test Pipeline 1"
    mock_pipeline1.type = "extract_load"
    mock_pipeline1.is_active = True
    mock_pipeline1.created_at = MagicMock()
    mock_pipeline1.created_at.ToDatetime.return_value = "2024-01-01T00:00:00Z"
    mock_pipeline1.updated_at = MagicMock()
    mock_pipeline1.updated_at.ToDatetime.return_value = "2024-01-01T00:00:00Z"

    mock_response.pipelines = [mock_pipeline1]
    mock_stub.ListPipelines = AsyncMock(return_value=mock_response)

    response = client.get("/api/pipelines/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "pipeline-1"
    assert data[0]["name"] == "Test Pipeline 1"


def test_create_pipeline(client):
    """Test create pipeline endpoint."""
    # Mock create response
    mock_response = MagicMock()
    mock_response.id = "new-pipeline-123"
    mock_response.name = "New Pipeline"
    mock_response.type = "extract_load"
    mock_response.is_active = True
    mock_response.created_at = MagicMock()
    mock_response.created_at.ToDatetime.return_value = "2024-01-01T00:00:00Z"
    mock_response.updated_at = MagicMock()
    mock_response.updated_at.ToDatetime.return_value = "2024-01-01T00:00:00Z"

    mock_stub.CreatePipeline = AsyncMock(return_value=mock_response)

    payload = {
        "name": "New Pipeline",
        "type": "extract_load",
        "config": {"source": "test", "destination": "test"},
        "schedule": "0 * * * *",
    }

    response = client.post("/api/pipelines/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "new-pipeline-123"
    assert data["name"] == "New Pipeline"


def test_run_pipeline(client):
    """Test run pipeline endpoint."""
    # Mock run response
    mock_response = MagicMock()
    mock_response.id = "exec-123"
    mock_response.pipeline_id = "pipeline-123"
    mock_response.status = "running"
    mock_response.started_at = MagicMock()
    mock_response.started_at.ToDatetime.return_value = "2024-01-01T00:00:00Z"

    mock_stub.RunPipeline = AsyncMock(return_value=mock_response)

    response = client.post("/api/pipelines/pipeline-123/run")
    assert response.status_code == 200
    data = response.json()
    assert data["execution_id"] == "exec-123"
    assert data["status"] == "running"


def test_authentication_required(client):
    """Test endpoints require authentication."""
    # Remove auth override temporarily
    app.dependency_overrides.pop(get_current_user, None)

    response = client.get("/api/pipelines/")
    assert response.status_code == 401

    # Restore auth override
    app.dependency_overrides[get_current_user] = lambda: mock_user


def test_websocket_connection():
    """Test WebSocket connection."""
    with TestClient(app) as client:
        with client.websocket_connect("/api/ws/test-client") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})

            # Receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "connected"

            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"


def test_error_handling(client):
    """Test API error handling."""
    # Mock gRPC error
    mock_stub.GetPipeline = AsyncMock(side_effect=Exception("Pipeline not found"))

    response = client.get("/api/pipelines/nonexistent")
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data


def test_pagination(client):
    """Test pagination parameters."""
    # Mock paginated response
    mock_response = MagicMock()
    mock_response.pipelines = []
    mock_stub.ListPipelines = AsyncMock(return_value=mock_response)

    response = client.get("/api/pipelines/?limit=10&offset=20")
    assert response.status_code == 200

    # Verify pagination parameters were passed
    mock_stub.ListPipelines.assert_called_once()
    call_args = mock_stub.ListPipelines.call_args[0][0]
    assert call_args.limit == 10
    assert call_args.offset == 20


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/api/pipelines/")
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


def test_request_validation(client):
    """Test request validation."""
    # Invalid pipeline creation request
    payload = {
        "name": "",  # Empty name should fail validation
        "type": "invalid_type",  # Invalid type
    }

    response = client.post("/api/pipelines/", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
