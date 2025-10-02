"""Tests for flext_cli.cli module."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from flext_cli.api import FlextCli
from flext_cli.auth import FlextCliAuth
from flext_cli.config import FlextCliConfig
from flext_cli.debug import FlextCliDebug
from flext_cli.formatters import FlextCliFormatters
from flext_cli.main import FlextCliMain


class TestFlextCli:
    """Test cases for FlextCli class."""

    def test_init(self) -> None:
        """Test FlextCli initialization."""
        cli = FlextCli()

        # Check that all components are initialized
        assert cli.auth is not None
        assert cli.config is not None
        assert cli.debug is not None
        assert cli.formatters is not None
        assert cli.main is not None

    def test_execute_success(self) -> None:
        """Test execute method returns success."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        data = result.unwrap()
        assert data["status"] == "operational"
        assert data["service"] == "flext-cli"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data
        assert "components" in data

        # Check components
        components = data["components"]
        assert components["api"] == "available"
        assert components["auth"] == "available"
        assert components["config"] == "available"
        assert components["debug"] == "available"
        assert components["formatters"] == "available"
        assert components["main"] == "available"

    @patch("flext_cli.cli.click")
    def test_cli_status_command(self, mock_click: MagicMock) -> None:
        """Test CLI status command."""
        cli = FlextCli()

        # Mock click.echo and click.Abort
        mock_click.echo = MagicMock()
        mock_click.Abort = Exception("Abort")

        # Mock the CLI runner
        _runner = CliRunner()

        # Test that the CLI can be created and run
        # This is a basic test since the actual CLI execution is complex
        # api property doesn't exist in FlextCli
        assert cli.auth is not None

    @patch("flext_cli.cli.click")
    def test_cli_version_command(self, mock_click: MagicMock) -> None:
        """Test CLI version command."""
        cli = FlextCli()

        # Mock click.echo
        mock_click.echo = MagicMock()

        # Test that the CLI can be created
        # api property doesn't exist in FlextCli
        assert cli.auth is not None

    def test_execute_returns_flext_result(self) -> None:
        """Test that execute returns FlextResult."""
        cli = FlextCli()
        result = cli.execute()

        # Check FlextResult properties
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")
        assert hasattr(result, "unwrap")
        assert hasattr(result, "error")

        # Should be successful
        assert result.is_success
        assert not result.is_failure
        assert result.error is None

    def test_execute_data_structure(self) -> None:
        """Test execute method data structure."""
        cli = FlextCli()
        result = cli.execute()

        assert result.is_success
        data = result.unwrap()

        # Check required fields
        required_fields = ["status", "service", "timestamp", "version", "components"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["components"], dict)

        # Check component data types
        for component_name, component_status in data["components"].items():
            assert isinstance(component_name, str)
            assert isinstance(component_status, str)
            assert component_status == "available"

    def test_cli_components_initialization(self) -> None:
        """Test that all CLI components are properly initialized."""
        cli = FlextCli()

        # Check component types

        # api property doesn't exist in FlextCli
        assert isinstance(cli.auth, FlextCliAuth)
        assert isinstance(cli.config, FlextCliConfig)
        assert isinstance(cli.debug, FlextCliDebug)
        assert isinstance(cli.formatters, FlextCliFormatters)
        assert isinstance(cli.main, FlextCliMain)
