"""
Tests for FLX Core Daemon.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from flx.config import Settings
from flx.daemon import FlxDaemon


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        environment="test",
        grpc_port=50052,
        metrics_port=9091,
        database_url="sqlite:///test.db",
        redis_url="redis://localhost:6379/15",
    )


@pytest.fixture
def daemon(settings):
    """Create test daemon instance."""
    return FlxDaemon(settings)


@pytest.mark.asyncio
async def test_daemon_initialization(daemon):
    """Test daemon initializes correctly."""
    assert daemon.settings.environment == "test"
    assert daemon.settings.grpc_port == 50052
    assert daemon._running is False
    assert daemon._tasks == []


@pytest.mark.asyncio
async def test_daemon_start_stop(daemon):
    """Test daemon start and stop lifecycle."""
    # Mock dependencies
    daemon._start_grpc_server = AsyncMock()
    daemon._start_event_bus = AsyncMock()
    daemon._start_health_checker = AsyncMock()
    daemon._start_metrics_collector = AsyncMock()
    daemon._start_meltano_engine = AsyncMock()

    # Start daemon
    start_task = asyncio.create_task(daemon.start())
    await asyncio.sleep(0.1)  # Let it start

    assert daemon._running is True
    assert len(daemon._tasks) > 0

    # Stop daemon
    await daemon.stop()
    assert daemon._running is False

    # Cancel start task
    start_task.cancel()
    try:
        await start_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_daemon_signal_handling(daemon):
    """Test daemon handles signals correctly."""
    with patch("signal.signal") as mock_signal:
        daemon._setup_signal_handlers()

        # Verify signal handlers were registered
        assert mock_signal.call_count >= 2

        # Test signal handler
        await daemon._handle_signal(15, None)  # SIGTERM
        assert daemon._running is False


@pytest.mark.asyncio
async def test_daemon_error_handling(daemon):
    """Test daemon handles errors gracefully."""
    # Mock a component that raises an error
    daemon._start_grpc_server = AsyncMock(side_effect=Exception("Test error"))
    daemon._start_event_bus = AsyncMock()
    daemon._start_health_checker = AsyncMock()
    daemon._start_metrics_collector = AsyncMock()
    daemon._start_meltano_engine = AsyncMock()

    # Daemon should handle the error and continue
    with pytest.raises(Exception, match="Test error"):
        await daemon.start()


@pytest.mark.asyncio
async def test_daemon_health_check(daemon):
    """Test daemon health check functionality."""
    # Mock components
    daemon.grpc_server = MagicMock()
    daemon.grpc_server.is_running = MagicMock(return_value=True)

    daemon.event_bus = MagicMock()
    daemon.event_bus.is_healthy = MagicMock(return_value=True)

    daemon.meltano_engine = MagicMock()
    daemon.meltano_engine.is_healthy = MagicMock(return_value=True)

    health = await daemon.health_check()

    assert health["healthy"] is True
    assert "components" in health
    assert health["components"]["grpc"]["healthy"] is True
    assert health["components"]["event_bus"]["healthy"] is True
    assert health["components"]["meltano"]["healthy"] is True


@pytest.mark.asyncio
async def test_daemon_metrics_collection(daemon):
    """Test daemon metrics collection."""
    daemon.metrics_collector = MagicMock()
    daemon.metrics_collector.get_metrics = MagicMock(
        return_value={
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "active_pipelines": 3,
            "total_executions": 150,
        }
    )

    metrics = await daemon.get_metrics()

    assert metrics["cpu_usage"] == 45.2
    assert metrics["memory_usage"] == 62.8
    assert metrics["active_pipelines"] == 3
    assert metrics["total_executions"] == 150


@pytest.mark.asyncio
async def test_daemon_graceful_shutdown(daemon):
    """Test daemon shuts down gracefully."""
    # Create some mock tasks
    task1 = AsyncMock()
    task2 = AsyncMock()
    daemon._tasks = [
        asyncio.create_task(task1()),
        asyncio.create_task(task2()),
    ]

    # Mock components
    daemon.grpc_server = MagicMock()
    daemon.grpc_server.stop = AsyncMock()

    daemon.event_bus = MagicMock()
    daemon.event_bus.stop = AsyncMock()

    # Stop daemon
    await daemon.stop()

    # Verify components were stopped
    daemon.grpc_server.stop.assert_called_once()
    daemon.event_bus.stop.assert_called_once()

    # Verify tasks were cancelled
    for task in daemon._tasks:
        assert task.cancelled()


@pytest.mark.asyncio
async def test_daemon_reconnection_logic(daemon):
    """Test daemon reconnects to services when they fail."""
    # Mock a service that fails then succeeds
    attempt = 0

    async def mock_connect():
        nonlocal attempt
        attempt += 1
        if attempt < 3:
            raise ConnectionError("Service unavailable")
        return True

    daemon._connect_to_database = mock_connect

    # Should retry and eventually succeed
    result = await daemon._connect_with_retry("database", daemon._connect_to_database)
    assert result is True
    assert attempt == 3


@pytest.mark.asyncio
async def test_daemon_resource_cleanup(daemon):
    """Test daemon cleans up resources properly."""
    # Mock resources
    daemon._db_connection = MagicMock()
    daemon._db_connection.close = AsyncMock()

    daemon._redis_connection = MagicMock()
    daemon._redis_connection.close = AsyncMock()

    # Cleanup
    await daemon._cleanup_resources()

    # Verify resources were cleaned up
    daemon._db_connection.close.assert_called_once()
    daemon._redis_connection.close.assert_called_once()
