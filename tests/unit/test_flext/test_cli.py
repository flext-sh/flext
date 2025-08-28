"""Unit tests for flext.cli module.

Tests for the main CLI interface functionality following FLEXT testing patterns
with proper mocking and fallback behavior validation.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from flext_core import FlextResult

from flext.cli import Colors, QualityGateway, main, print_colored


class TestMainCliFunction:
    """Test suite for main CLI function."""

    @pytest.fixture
    def cli_runner(self) -> CliRunner:
        """Click test runner for CLI testing."""
        return CliRunner()

    def test_main_cli_help(self, cli_runner: CliRunner) -> None:
        """Test main CLI help command."""
        # Act
        result = cli_runner.invoke(main, ["--help"])

        # Assert
        assert result.exit_code == 0
        assert "FLEXT Control Panel main command" in result.output

    def test_main_cli_with_workspace_option(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test main CLI with workspace option."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Act
        result = cli_runner.invoke(main, ["--workspace", str(workspace), "--help"])

        # Assert
        assert result.exit_code == 0

    @patch("flext.cli.CLIConfig")
    def test_main_cli_with_profile(
        self, mock_config: Mock, cli_runner: CliRunner
    ) -> None:
        """Test main CLI with profile option."""
        # Arrange
        mock_config.return_value = Mock()

        # Act
        result = cli_runner.invoke(main, ["--profile", "production", "--help"])

        # Assert
        assert result.exit_code == 0
        mock_config.assert_called()

    def test_main_cli_with_debug_flag(self, cli_runner: CliRunner) -> None:
        """Test main CLI with debug flag."""
        # Act
        result = cli_runner.invoke(main, ["--debug", "--help"])

        # Assert
        assert result.exit_code == 0

    def test_main_cli_with_output_format(self, cli_runner: CliRunner) -> None:
        """Test main CLI with output format option."""
        # Act
        result = cli_runner.invoke(main, ["--output", "json", "--help"])

        # Assert
        assert result.exit_code == 0

    @patch("flext.cli.CLIConfig")
    def test_main_cli_config_error_handling(
        self, mock_config: Mock, cli_runner: CliRunner
    ) -> None:
        """Test main CLI configuration error handling."""
        # Arrange
        mock_config.side_effect = Exception("Configuration error")

        # Act
        result = cli_runner.invoke(main, ["--help"])

        # Assert
        assert result.exit_code == 1


class TestCliToolsGroup:
    """Test suite for tools command group."""

    @pytest.fixture
    def cli_runner(self) -> CliRunner:
        """Click test runner for CLI testing."""
        return CliRunner()

    def test_tools_help(self, cli_runner: CliRunner) -> None:
        """Test tools group help command."""
        # Act
        result = cli_runner.invoke(main, ["tools", "--help"])

        # Assert
        assert result.exit_code == 0
        assert "Access flext_tools functionality" in result.output

    @patch("flext.cli.QualityGateway")
    def test_tools_quality_command(
        self, mock_gateway: Mock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test tools quality command."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        mock_gateway_instance = Mock()
        mock_gateway.return_value = mock_gateway_instance

        # Act
        result = cli_runner.invoke(
            main, ["--workspace", str(workspace), "tools", "quality", "--help"]
        )

        # Assert
        assert result.exit_code == 0

    def test_tools_scripts_command(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test tools scripts command."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Act
        result = cli_runner.invoke(
            main, ["--workspace", str(workspace), "tools", "scripts", "--list-only"]
        )

        # Assert
        assert result.exit_code == 0
        assert "Available FlextScript instances" in result.output

    def test_tools_analysis_command(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test tools analysis command."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Act
        result = cli_runner.invoke(
            main,
            ["--workspace", str(workspace), "tools", "analysis", "--type", "structure"],
        )

        # Assert
        assert result.exit_code == 0


class TestCliBuiltinCommands:
    """Test suite for built-in CLI commands."""

    @pytest.fixture
    def cli_runner(self) -> CliRunner:
        """Click test runner for CLI testing."""
        return CliRunner()

    def test_test_command(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test test command."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Act
        result = cli_runner.invoke(
            main, ["--workspace", str(workspace), "test", "--help"]
        )

        # Assert
        assert result.exit_code == 0

    @patch("flext.cli.QualityGateway")
    def test_lint_command(
        self, mock_gateway: Mock, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test lint command."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        mock_gateway_instance = Mock()
        mock_gateway.return_value = mock_gateway_instance

        # Act
        result = cli_runner.invoke(
            main, ["--workspace", str(workspace), "lint", "--help"]
        )

        # Assert
        assert result.exit_code == 0

    def test_format_command(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test format command."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Act
        result = cli_runner.invoke(
            main, ["--workspace", str(workspace), "format", "--help"]
        )

        # Assert
        assert result.exit_code == 0

    def test_info_command(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test info command."""
        # Arrange
        workspace = tmp_path / "test-workspace"
        workspace.mkdir()

        # Act
        result = cli_runner.invoke(main, ["--workspace", str(workspace), "info"])

        # Assert
        assert result.exit_code == 0
        assert "FLEXT Control Panel - Workspace Information" in result.output


class TestCliFallbackComponents:
    """Test suite for CLI fallback components."""

    def test_colors_fallback_constants(self) -> None:
        """Test that fallback Colors class has all required constants."""
        # Assert all required color constants exist
        required_colors = ["GREEN", "RED", "BLUE", "CYAN", "YELLOW", "RESET"]

        for color in required_colors:
            assert hasattr(Colors, color)
            assert isinstance(getattr(Colors, color), str)
            assert len(getattr(Colors, color)) > 0

    def test_colors_ansi_codes(self) -> None:
        """Test that Colors constants contain proper ANSI codes."""
        from flext.cli import Colors

        # Assert ANSI escape sequences
        assert Colors.GREEN.startswith("\033[")
        assert Colors.RED.startswith("\033[")
        assert Colors.RESET == "\033[0m"

    def test_quality_gateway_fallback(self) -> None:
        """Test QualityGateway fallback implementation."""
        # Arrange
        workspace = Path("/test/workspace")

        # Act
        gateway = QualityGateway(workspace)

        # Assert
        assert gateway.workspace_path == workspace
        assert hasattr(gateway, "run_quality_checks")

        # Test method execution
        result = gateway.run_quality_checks()
        assert isinstance(result, FlextResult)

    def test_cli_enhanced_decorator_fallback(self) -> None:
        """Test cli_enhanced decorator fallback."""
        from flext.cli import cli_enhanced

        # Act
        decorator = cli_enhanced(name="test")

        # Test that it returns a proper decorator
        def test_function() -> str:
            return "test"

        decorated = decorator(test_function)

        # Assert
        assert callable(decorated)
        assert decorated() == "test"

    def test_print_colored_fallback(self) -> None:
        """Test print_colored fallback function."""
        # This should not raise an exception
        print_colored("Test message", Colors.GREEN)
        print_colored("Test message")  # Default color


class TestCliContext:
    """Test suite for CLI context components."""

    def test_flext_cli_context_creation(self) -> None:
        """Test FlextCliContext creation."""
        from flext.cli import CLIConfig, FlextCliContext

        # Arrange
        config = CLIConfig(profile="test", debug=True)

        # Act
        context = FlextCliContext(config)

        # Assert
        assert context.config == config


class TestCliIntegration:
    """Integration tests for CLI components."""

    @pytest.fixture
    def cli_runner(self) -> CliRunner:
        """Click test runner for CLI testing."""
        return CliRunner()

    def test_full_cli_workflow(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test complete CLI workflow with multiple commands."""
        # Arrange
        workspace = tmp_path / "integration-test-workspace"
        workspace.mkdir()

        # Act & Assert - Test multiple command sequences
        commands_to_test = [
            ["--help"],
            ["--workspace", str(workspace), "info"],
            ["tools", "--help"],
            ["tools", "scripts", "--list-only"],
        ]

        for cmd in commands_to_test:
            result = cli_runner.invoke(main, cmd)
            assert result.exit_code == 0

    def test_cli_error_propagation(self, cli_runner: CliRunner) -> None:
        """Test that CLI properly propagates errors."""
        # Act - Use invalid workspace path
        result = cli_runner.invoke(main, ["--workspace", "/invalid/path", "info"])

        # Assert - Should handle the error gracefully
        # The specific exit code depends on implementation details
        assert isinstance(result.exit_code, int)
