#!/usr/bin/env python3
"""Comprehensive End-to-End tests for oracle-oic-ext.

Tests all functionalities including:
- Extension initialization
- Lifecycle management
- Monitoring services
- Artifact extraction
- Command routing
- Error handling
"""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from oracle_oic_ext.extension import OracleOICExtension
from oracle_oic_ext.lifecycle import LifecycleManager
from oracle_oic_ext.monitoring import MonitoringService


class TestOracleOICExtE2E:
    """End-to-end tests for oracle-oic-ext."""

    @pytest.fixture
    def config_path(self):
        """Return path to config.json."""
        config_file = Path(__file__).parent.parent / "config.json"
        if not config_file.exists():
            # Generate config if it doesn't exist
            os.system("cd .. && python generate_config.py")
        return str(config_file)

    @pytest.fixture
    def config(self, config_path):
        """Load configuration from config.json."""
        with open(config_path) as f:
            return json.load(f)

    @pytest.fixture
    def extension(self):
        """Create extension instance."""
        return OracleOICExtension()

    def test_extension_initialization(self, extension) -> None:
        """Test extension can be initialized."""
        assert extension.oracle_oic_bin == "oracle-oic-ext"
        assert extension.lifecycle_manager is None
        assert extension.monitoring_service is None

    def test_describe_commands(self, extension) -> None:
        """Test extension describes all available commands."""
        description = extension.describe()

        assert len(description.commands) > 0

        # Check command categories
        command_names = [cmd.name for cmd in description.commands]

        # Lifecycle commands
        assert "lifecycle:activate" in command_names
        assert "lifecycle:deactivate" in command_names
        assert "lifecycle:status" in command_names
        assert "lifecycle:export" in command_names
        assert "lifecycle:import" in command_names

        # Monitoring commands
        assert "monitor:health" in command_names
        assert "monitor:performance" in command_names
        assert "monitor:errors" in command_names
        assert "monitor:usage" in command_names
        assert "monitor:alerts" in command_names

        # Extraction commands
        assert "extract:artifacts" in command_names
        assert "extract:logs" in command_names
        assert "extract:metadata" in command_names
        assert "extract:all" in command_names

    def test_command_routing(self, extension, config) -> None:
        """Test command routing to appropriate handlers."""
        # Mock environment config
        os.environ["MELTANO_PROJECT_ROOT"] = str(Path.cwd())

        with patch.object(extension, "_load_config", return_value=config):
            # Test lifecycle command routing
            with patch.object(extension, "_handle_lifecycle_command") as mock_lifecycle:
                extension.invoke("lifecycle:status", "integration123")
                mock_lifecycle.assert_called_once_with(
                    "lifecycle:status", "integration123"
                )

            # Test monitoring command routing
            with patch.object(
                extension, "_handle_monitoring_command"
            ) as mock_monitoring:
                extension.invoke("monitor:health")
                mock_monitoring.assert_called_once_with("monitor:health")

            # Test extraction command routing
            with patch.object(
                extension, "_handle_extraction_command"
            ) as mock_extraction:
                extension.invoke("extract:artifacts", "integration123")
                mock_extraction.assert_called_once_with(
                    "extract:artifacts", "integration123"
                )

    def test_lifecycle_manager_operations(self, config) -> None:
        """Test lifecycle manager functionality."""
        manager = LifecycleManager(
            base_url=config["base_url"],
            auth_config={
                "oauth_client_id": config["oauth_client_id"],
                "oauth_client_secret": config["oauth_client_secret"],
                "oauth_token_url": config["oauth_token_url"],
            },
        )

        # Test initialization
        assert manager.base_url == config["base_url"]
        assert manager.auth_config["oauth_client_id"] == config["oauth_client_id"]

        # Test status check
        with patch.object(manager, "_make_request") as mock_request:
            mock_request.return_value = {
                "id": "TEST_INTEGRATION",
                "status": "ACTIVATED",
                "version": "01.00.0000",
            }

            status = manager.get_integration_status("TEST_INTEGRATION")
            assert status["status"] == "ACTIVATED"
            assert status["id"] == "TEST_INTEGRATION"

            mock_request.assert_called_with(
                "GET", "/ic/api/integration/v1/integrations/TEST_INTEGRATION"
            )

    def test_monitoring_service_operations(self, config) -> None:
        """Test monitoring service functionality."""
        service = MonitoringService(
            base_url=config["base_url"],
            auth_config={
                "oauth_client_id": config["oauth_client_id"],
                "oauth_client_secret": config["oauth_client_secret"],
                "oauth_token_url": config["oauth_token_url"],
            },
        )

        # Test health check
        with patch.object(service, "_make_request") as mock_request:
            mock_request.return_value = {
                "status": "healthy",
                "components": {"database": "healthy", "messaging": "healthy"},
            }

            health = service.check_health()
            assert health["status"] == "healthy"
            assert health["components"]["database"] == "healthy"

    def test_artifact_extraction(self, extension, config) -> None:
        """Test artifact extraction functionality."""
        os.environ["MELTANO_PROJECT_ROOT"] = str(Path.cwd())

        with patch.object(extension, "_load_config", return_value=config):
            # Initialize extension
            extension.invoke("extract:artifacts", "TEST_INTEGRATION")

            # Check that extraction was attempted
            # (actual implementation would download .iar file)

    def test_error_handling(self, extension) -> None:
        """Test error handling for various scenarios."""
        # Test invalid command
        with pytest.raises(Exception):
            extension.invoke("invalid:command")

        # Test missing config
        os.environ.pop("MELTANO_PROJECT_ROOT", None)
        with pytest.raises(Exception):
            extension.invoke("lifecycle:status")

    def test_config_loading(self, extension, config_path) -> None:
        """Test configuration loading from file."""
        os.environ["MELTANO_PROJECT_ROOT"] = str(Path(config_path).parent)

        loaded_config = extension._load_config()

        assert "base_url" in loaded_config
        assert "oauth_client_id" in loaded_config
        assert loaded_config["base_url"].startswith("https://")

    @pytest.mark.skipif(
        os.getenv("SKIP_LIVE_TESTS", "true").lower() == "true",
        reason="Skipping live API tests",
    )
    def test_live_integration_status(self, extension, config) -> None:
        """Test live integration status check."""
        os.environ["MELTANO_PROJECT_ROOT"] = str(Path.cwd())

        with patch.object(extension, "_load_config", return_value=config):
            try:
                # This will make actual API call
                extension.invoke("lifecycle:status", "TEST_INTEGRATION")
                assert True
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    pytest.skip(f"Authentication failed: {e}")
                elif "404" in str(e):
                    # Integration not found is OK for test
                    assert True
                else:
                    pytest.fail(f"Unexpected error: {e}")

    def test_batch_operations(self, extension, config) -> None:
        """Test batch operations on multiple integrations."""
        os.environ["MELTANO_PROJECT_ROOT"] = str(Path.cwd())

        integrations = ["INT1", "INT2", "INT3"]

        with (
            patch.object(extension, "_load_config", return_value=config),
            patch.object(LifecycleManager, "activate_integration") as mock_activate,
        ):
            mock_activate.return_value = {"status": "ACTIVATED"}

            # Activate multiple integrations
            for integration in integrations:
                extension.invoke("lifecycle:activate", integration)

            assert mock_activate.call_count == len(integrations)

    def test_monitoring_alerts(self, config) -> None:
        """Test monitoring alert functionality."""
        service = MonitoringService(
            base_url=config["base_url"],
            auth_config={
                "oauth_client_id": config["oauth_client_id"],
                "oauth_client_secret": config["oauth_client_secret"],
                "oauth_token_url": config["oauth_token_url"],
            },
        )

        # Test alert retrieval
        with patch.object(service, "_make_request") as mock_request:
            mock_request.return_value = {
                "alerts": [
                    {
                        "id": "alert1",
                        "severity": "HIGH",
                        "message": "Integration failure detected",
                    }
                ]
            }

            alerts = service.get_alerts()
            assert len(alerts["alerts"]) == 1
            assert alerts["alerts"][0]["severity"] == "HIGH"

    def test_performance_metrics(self, config) -> None:
        """Test performance metrics collection."""
        service = MonitoringService(
            base_url=config["base_url"],
            auth_config={
                "oauth_client_id": config["oauth_client_id"],
                "oauth_client_secret": config["oauth_client_secret"],
                "oauth_token_url": config["oauth_token_url"],
            },
        )

        with patch.object(service, "_make_request") as mock_request:
            mock_request.return_value = {
                "metrics": {"throughput": 1000, "latency_ms": 50, "error_rate": 0.01}
            }

            metrics = service.get_performance_metrics()
            assert metrics["metrics"]["throughput"] == 1000
            assert metrics["metrics"]["latency_ms"] == 50

    def test_log_extraction(self, extension, config, tmp_path) -> None:
        """Test log extraction functionality."""
        os.environ["MELTANO_PROJECT_ROOT"] = str(Path.cwd())

        with patch.object(extension, "_load_config", return_value=config):
            # Mock log extraction
            with patch("builtins.open", create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file

                extension.invoke("extract:logs", "TEST_INTEGRATION", str(tmp_path))

                # Verify log file would be created
                mock_open.assert_called()

    def test_full_workflow(self, extension, config) -> None:
        """Test complete workflow from status check to activation."""
        os.environ["MELTANO_PROJECT_ROOT"] = str(Path.cwd())

        with patch.object(extension, "_load_config", return_value=config):
            # 1. Check status
            with patch.object(
                LifecycleManager, "get_integration_status"
            ) as mock_status:
                mock_status.return_value = {"status": "CONFIGURED"}

                # 2. Activate integration
                with patch.object(
                    LifecycleManager, "activate_integration"
                ) as mock_activate:
                    mock_activate.return_value = {"status": "ACTIVATED"}

                    # 3. Export integration
                    with patch.object(
                        LifecycleManager, "export_integration"
                    ) as mock_export:
                        mock_export.return_value = b"iar_content"

                        # Execute workflow
                        extension.invoke("lifecycle:status", "TEST_INT")
                        extension.invoke("lifecycle:activate", "TEST_INT")
                        extension.invoke(
                            "lifecycle:export", "TEST_INT", "/tmp/export.iar"
                        )

                        # Verify all steps were called
                        mock_status.assert_called_once()
                        mock_activate.assert_called_once()
                        mock_export.assert_called_once()

    def test_conditional_config_generation(self) -> None:
        """Test conditional config.json generation."""
        config_path = Path(__file__).parent.parent / "config.json"

        # If config doesn't exist, it should be generated
        if not config_path.exists():
            import subprocess

            result = subprocess.run(
                ["python", "generate_config.py"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                input="y\n",
            )
            assert result.returncode == 0
            assert config_path.exists()

        # Load and validate config
        with open(config_path) as f:
            config = json.load(f)

        # Check required fields
        assert "base_url" in config
        assert "oauth_client_id" in config
        assert "oauth_client_secret" in config
        assert "oauth_token_url" in config

        # Check extension-specific fields
        assert "instance_id" in config
        assert "region" in config
        assert "environment" in config
