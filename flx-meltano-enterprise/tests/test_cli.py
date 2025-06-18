"""
Tests for Click CLI.
"""

import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from click.testing import CliRunner
from flx_cli.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_grpc_client():
    """Create mock gRPC client."""
    with patch("flx_cli.cli.FlxClient") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance


def test_cli_version(runner):
    """Test version command."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_cli_help(runner):
    """Test help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "FLX Enterprise CLI" in result.output
    assert "Commands:" in result.output


def test_status_command(runner, mock_grpc_client):
    """Test status command."""
    # Mock health and stats responses
    mock_grpc_client.health_check.return_value = {
        "healthy": True,
        "components": {
            "grpc": {"healthy": True, "message": "Running"},
            "database": {"healthy": True, "message": "Connected"},
        },
    }

    mock_grpc_client.get_stats.return_value = {
        "active_pipelines": 5,
        "total_executions": 100,
        "success_rate": 95.5,
        "uptime_seconds": 3600,
    }

    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "System Status" in result.output
    assert "Healthy" in result.output
    assert "Active Pipelines: 5" in result.output


def test_pipeline_list(runner, mock_grpc_client):
    """Test pipeline list command."""
    mock_grpc_client.list_pipelines.return_value = [
        {
            "id": "pipeline-1",
            "name": "Test Pipeline 1",
            "type": "extract_load",
            "is_active": True,
        },
        {
            "id": "pipeline-2",
            "name": "Test Pipeline 2",
            "type": "transform",
            "is_active": False,
        },
    ]

    result = runner.invoke(cli, ["pipeline", "list"])
    assert result.exit_code == 0
    assert "Test Pipeline 1" in result.output
    assert "Test Pipeline 2" in result.output
    assert "extract_load" in result.output


def test_pipeline_create(runner, mock_grpc_client):
    """Test pipeline create command."""
    mock_grpc_client.create_pipeline.return_value = {
        "id": "new-pipeline-123",
        "name": "New Pipeline",
        "type": "extract_load",
        "is_active": True,
    }

    result = runner.invoke(
        cli,
        [
            "pipeline",
            "create",
            "New Pipeline",
            "--type",
            "extract_load",
            "--schedule",
            "0 * * * *",
        ],
    )
    assert result.exit_code == 0
    assert "Pipeline created successfully" in result.output
    assert "new-pipeline-123" in result.output


def test_pipeline_create_from_file(runner, mock_grpc_client):
    """Test pipeline create from config file."""
    config_data = {
        "name": "File Pipeline",
        "type": "extract_load",
        "config": {
            "source": "database",
            "destination": "s3",
        },
        "schedule": "0 */6 * * *",
    }

    mock_grpc_client.create_pipeline.return_value = {
        "id": "file-pipeline-123",
        "name": "File Pipeline",
        "type": "extract_load",
        "is_active": True,
    }

    with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
        result = runner.invoke(
            cli,
            [
                "pipeline",
                "create",
                "File Pipeline",
                "--config-file",
                "config.json",
            ],
        )

    assert result.exit_code == 0
    assert "Pipeline created successfully" in result.output


def test_pipeline_run(runner, mock_grpc_client):
    """Test pipeline run command."""
    mock_grpc_client.run_pipeline.return_value = {
        "execution_id": "exec-123",
        "status": "running",
    }

    result = runner.invoke(cli, ["pipeline", "run", "pipeline-123"])
    assert result.exit_code == 0
    assert "Pipeline execution started" in result.output
    assert "exec-123" in result.output


def test_pipeline_run_with_follow(runner, mock_grpc_client):
    """Test pipeline run with log following."""
    mock_grpc_client.run_pipeline.return_value = {
        "execution_id": "exec-123",
        "status": "running",
    }

    # Mock log streaming
    mock_grpc_client.stream_logs.return_value = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "INFO",
            "message": "Starting pipeline",
        },
        {
            "timestamp": "2024-01-01T00:00:01Z",
            "level": "INFO",
            "message": "Pipeline completed",
        },
    ]

    result = runner.invoke(cli, ["pipeline", "run", "pipeline-123", "--follow"])
    assert result.exit_code == 0
    assert "Starting pipeline" in result.output
    assert "Pipeline completed" in result.output


def test_pipeline_delete(runner, mock_grpc_client):
    """Test pipeline delete command."""
    # Confirm deletion
    result = runner.invoke(cli, ["pipeline", "delete", "pipeline-123"], input="y\n")
    assert result.exit_code == 0
    assert "Pipeline deleted successfully" in result.output

    # Cancel deletion
    result = runner.invoke(cli, ["pipeline", "delete", "pipeline-123"], input="n\n")
    assert result.exit_code == 0
    assert "Deletion cancelled" in result.output


def test_execution_list(runner, mock_grpc_client):
    """Test execution list command."""
    mock_grpc_client.list_executions.return_value = [
        {
            "id": "exec-1",
            "pipeline_id": "pipeline-1",
            "status": "completed",
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:05:00Z",
        },
        {
            "id": "exec-2",
            "pipeline_id": "pipeline-1",
            "status": "failed",
            "started_at": "2024-01-01T01:00:00Z",
            "error": "Connection timeout",
        },
    ]

    result = runner.invoke(cli, ["execution", "list"])
    assert result.exit_code == 0
    assert "exec-1" in result.output
    assert "completed" in result.output
    assert "failed" in result.output


def test_execution_logs(runner, mock_grpc_client):
    """Test execution logs command."""
    mock_grpc_client.get_execution_logs.return_value = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "INFO",
            "message": "Starting pipeline",
        },
        {
            "timestamp": "2024-01-01T00:00:01Z",
            "level": "ERROR",
            "message": "Connection failed",
        },
    ]

    result = runner.invoke(cli, ["execution", "logs", "exec-123"])
    assert result.exit_code == 0
    assert "Starting pipeline" in result.output
    assert "Connection failed" in result.output


def test_config_show(runner, mock_grpc_client):
    """Test config show command."""
    with patch("flx_cli.cli.load_config") as mock_load_config:
        mock_load_config.return_value = {
            "host": "localhost",
            "port": 50051,
            "timeout": 30,
        }

        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "localhost" in result.output
        assert "50051" in result.output


def test_config_set(runner):
    """Test config set command."""
    with patch("flx_cli.cli.save_config") as mock_save_config:
        result = runner.invoke(cli, ["config", "set", "host", "flx.example.com"])
        assert result.exit_code == 0
        assert "Configuration updated" in result.output

        # Verify config was saved
        mock_save_config.assert_called_once()
        saved_config = mock_save_config.call_args[0][0]
        assert saved_config["host"] == "flx.example.com"


def test_error_handling(runner, mock_grpc_client):
    """Test CLI error handling."""
    # Mock gRPC error
    mock_grpc_client.health_check.side_effect = Exception("Connection refused")

    result = runner.invoke(cli, ["status"])
    assert result.exit_code != 0
    assert "Error" in result.output
    assert "Connection refused" in result.output


def test_output_formats(runner, mock_grpc_client):
    """Test different output formats."""
    mock_grpc_client.list_pipelines.return_value = [
        {
            "id": "pipeline-1",
            "name": "Test Pipeline",
            "type": "extract_load",
            "is_active": True,
        },
    ]

    # Table format (default)
    result = runner.invoke(cli, ["pipeline", "list"])
    assert result.exit_code == 0
    assert "│" in result.output  # Table borders

    # JSON format
    result = runner.invoke(cli, ["pipeline", "list", "--output", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["id"] == "pipeline-1"

    # CSV format
    result = runner.invoke(cli, ["pipeline", "list", "--output", "csv"])
    assert result.exit_code == 0
    assert "pipeline-1,Test Pipeline,extract_load,True" in result.output
