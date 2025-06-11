"""Tests for FLX CLI functionality.

Tests the specific FLX CLI implementation, ensuring proper separation
of concerns between CLI and framework components.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from flx.cli import fix_create_cli


@pytest.fixture()
def cli() -> Any:
    """Create FLX CLI instance for testing."""
    return fix_create_cli()


class TestFlxCli:
    """Test FLX specific CLI functionality."""

    def test_cli_creation(self) -> None:
        """Test CLI instance creation."""
        cli = fix_create_cli()

        assert cli.name == "flx"
        assert cli.description == "FLX Framework CLI"
        assert hasattr(cli, "context")
        assert hasattr(cli, "formatter")
        assert hasattr(cli, "config_hierarchy")
        assert hasattr(cli, "adapter")

    def test_cli_creation_with_custom_params(self) -> None:
        """Test CLI creation with custom parameters."""
        cli = fix_create_cli(
            name="custom-flx",
            description="Custom FLX CLI",
            version="2.0.0",
            env_prefix="CUSTOM_",
        )

        assert cli.name == "custom-flx"
        assert cli.description == "Custom FLX CLI"
        assert cli.version == "2.0.0"
        assert cli.config_hierarchy.env_prefix == "CUSTOM_"

    def test_configuration_hierarchy(self, cli: Any) -> None:
        """Test configuration hierarchy functionality."""
        # Test setting CLI overrides
        cli.config_hierarchy.set_overrides(
            {
                "debug": True,
                "verbose": True,
            },
        )

        config = cli.config_hierarchy.get_effective_config()
        assert config["debug"] is True
        assert config["verbose"] is True

    def test_commands_exist(self, cli: Any) -> None:
        """Test that command methods exist."""
        assert hasattr(cli, "version")
        assert hasattr(cli, "status")
        assert hasattr(cli, "health")
        assert hasattr(cli, "config_show")
        assert hasattr(cli, "service_list")
        assert hasattr(cli, "plugin_list")
        assert callable(cli.version)

    @pytest.mark.asyncio()
    async def test_version_command(self, cli: Any) -> None:
        """Test version command execution."""
        result = await cli.version()

        assert result.status == "success"
        assert "flx_version" in result.data
        assert "cli_version" in result.data

    @pytest.mark.asyncio()
    async def test_status_command(self, cli: Any) -> None:
        """Test status command execution."""
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.data = {
            "status": "operational",
            "adapter": "FlxIngoingCliAdapter",
        }

        with patch.object(cli.adapter, "execute_command", return_value=mock_response):
            result = await cli.status()
            assert result.status == "success"
            assert result.data == mock_response.data

    @pytest.mark.asyncio()
    async def test_config_show_command(self, cli: Any) -> None:
        """Test config show command."""
        result = await cli.config_show()

        assert result.status == "success"
        assert "settings" in result.data

    def test_run_command_method(self, cli: Any) -> None:
        """Test run_command method."""
        # Test invalid command
        exit_code = cli.run_command("invalid-command")
        assert exit_code == 1

    def test_cli_run_help(self, cli: Any) -> None:
        """Test CLI run with help."""
        exit_code = cli.run(["--help"])
        assert exit_code == 0

    def test_cli_run_version_flag(self, cli: Any) -> None:
        """Test CLI run with version flag."""
        exit_code = cli.run(["--version"])
        assert exit_code == 0

    def test_adapter_integration(self, cli: Any) -> None:
        """Test adapter integration."""
        # Verify adapter is properly initialized
        assert cli.adapter is not None
        assert hasattr(cli.adapter, "execute_command")
        assert hasattr(cli.adapter, "list_commands")

    def test_formatter_integration(self, cli: Any) -> None:
        """Test output formatter integration."""
        # Verify formatter is properly initialized
        assert cli.formatter is not None
        assert hasattr(cli.formatter, "format_and_display")

        # Test basic formatting
        test_data = {"test": "value"}
        # Should not raise exceptions
        cli.formatter.format_and_display(test_data, "json")

    def test_context_integration(self, cli: Any) -> None:
        """Test CLI context integration."""
        assert cli.context is not None
        assert hasattr(cli.context, "console")
        assert hasattr(cli.context, "config")
        assert hasattr(cli.context, "print_result")


class TestFlxCliBackwardCompatibility:
    """Test backward compatibility for CLI functionality."""

    def test_main_function_exists(self) -> None:
        """Test that main function exists for entry point."""
        from flx.cli import main

        assert callable(main)

    def test_create_function_exists(self) -> None:
        """Test that create function exists."""
        from flx.cli import fix_create_cli

        assert callable(fix_create_cli)

    def test_cli_class_exists(self) -> None:
        """Test that CLI class exists."""
        from flx.cli import FlxCli

        assert FlxCli is not None


class TestFlxCliErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio()
    async def test_status_command_error(self, cli: Any) -> None:
        """Test status command with adapter error."""
        with patch.object(
            cli.adapter, "execute_command", side_effect=RuntimeError("Test error"),
        ):
            result = await cli.status()
            assert result.status == "error"
            assert "Test error" in result.message

    def test_run_command_keyboard_interrupt(self, cli: Any) -> None:
        """Test run_command with keyboard interrupt."""
        with patch.object(cli, "version", side_effect=KeyboardInterrupt()):
            exit_code = cli.run_command("version")
            assert exit_code == 130

    def test_run_command_general_exception(self, cli: Any) -> None:
        """Test run_command with general exception."""
        with patch.object(cli, "version", side_effect=Exception("Test error")):
            exit_code = cli.run_command("version")
            assert exit_code == 1
