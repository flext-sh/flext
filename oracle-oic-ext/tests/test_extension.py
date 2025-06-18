"""Tests for oracle-oic-ext."""

from oracle_oic_ext.extension import OracleOICExtension
from oracle_oic_ext.lifecycle import LifecycleManager
from oracle_oic_ext.monitoring import MonitoringService


class TestOracleOICExtension:
    """Test cases for OracleOICExtension."""

    def test_extension_initialization(self) -> None:
        """Test extension can be initialized."""
        ext = OracleOICExtension()
        assert ext.oracle_oic_bin == "oracle-oic-ext"
        assert ext.lifecycle_manager is None
        assert ext.monitoring_service is None

    def test_describe_commands(self) -> None:
        """Test extension describes available commands."""
        ext = OracleOICExtension()
        description = ext.describe()

        assert len(description.commands) > 0

        # Check lifecycle commands
        command_names = [cmd.name for cmd in description.commands]
        assert "lifecycle:activate" in command_names
        assert "lifecycle:deactivate" in command_names
        assert "lifecycle:status" in command_names

        # Check monitoring commands
        assert "monitor:health" in command_names
        assert "monitor:performance" in command_names
        assert "monitor:errors" in command_names
        assert "monitor:usage" in command_names

        # Check extraction commands
        assert "extract:artifacts" in command_names
        assert "extract:logs" in command_names
        assert "extract:metadata" in command_names

    def test_lifecycle_manager_initialization(self) -> None:
        """Test lifecycle manager can be initialized."""
        manager = LifecycleManager(
            base_url="https://test.integration.ocp.oraclecloud.com",
            auth_config={
                "oauth_client_id": "test_client",
                "oauth_client_secret": "test_secret",
                "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
            },
        )
        assert manager.base_url == "https://test.integration.ocp.oraclecloud.com"
        assert manager.auth_config["oauth_client_id"] == "test_client"

    def test_monitoring_service_initialization(self) -> None:
        """Test monitoring service can be initialized."""
        service = MonitoringService(
            base_url="https://test.integration.ocp.oraclecloud.com",
            auth_config={
                "oauth_client_id": "test_client",
                "oauth_client_secret": "test_secret",
                "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
            },
        )
        assert service.base_url == "https://test.integration.ocp.oraclecloud.com"
        assert service.auth_config["oauth_client_id"] == "test_client"
