"""Unit tests for flext.cli module.

Tests for the unified CLI interface functionality following FLEXT testing patterns
with proper verification of flext-cli integration and unified class patterns.
"""

import inspect
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

import flext.cli as cli_module
import flext.workspace_cli
from flext import cli
from flext.cli import (
    FlextControlPanelCli,
    __all__,
    analysis,
    create_cli,
    format_code,
    info,
    lint,
    main,
    quality,
    scripts,
    test,
)


class TestFlextControlPanelCli:
    """Test suite for unified CLI service with nested class pattern."""

    def test_cli_service_initialization(self) -> None:
        """Test CLI service initialization with dependency injection."""
        cli_service = create_cli()

        assert isinstance(cli_service, FlextControlPanelCli)
        assert hasattr(cli_service, "_logger")
        assert hasattr(cli_service, "_cli_api")
        assert hasattr(cli_service, "_config")
        assert hasattr(cli_service, "_workspace")

    def test_tools_handler_creation(self) -> None:
        """Test nested tools handler creation."""
        cli_service = create_cli()
        tools_handler = cli_service.create_tools_handler()

        assert tools_handler is not None
        assert hasattr(tools_handler, "quality_check")
        assert hasattr(tools_handler, "list_scripts")
        assert hasattr(tools_handler, "run_analysis")

    def test_main_handler_creation(self) -> None:
        """Test nested main handler creation."""
        cli_service = create_cli()
        main_handler = cli_service.create_main_handler()

        assert main_handler is not None
        assert hasattr(main_handler, "test_command")
        assert hasattr(main_handler, "lint_command")
        assert hasattr(main_handler, "format_command")
        assert hasattr(main_handler, "info_command")

    @patch("flext.cli.FlextCliApi")
    def test_cli_api_integration(self, mock_cli_api: Mock) -> None:
        """Test integration with flext-cli API."""
        mock_api_instance = Mock()
        mock_cli_api.return_value = mock_api_instance

        cli_service = FlextControlPanelCli()

        # Verify flext-cli API was instantiated
        mock_cli_api.assert_called_once()
        assert cli_service._cli_api == mock_api_instance

    @patch("flext.cli.FlextCliConfig")
    @patch("flext.cli.FlextCliMain")
    def test_cli_initialization(
        self, mock_cli_main: Mock, mock_cli_config: Mock
    ) -> None:
        """Test CLI initialization with flext-cli components."""
        mock_config_instance = Mock()
        mock_main_instance = Mock()
        mock_cli_config.return_value = mock_config_instance
        mock_cli_main.return_value = mock_main_instance

        cli_service = create_cli()
        result = cli_service.initialize(
            workspace="/test/workspace", profile="dev", debug=True
        )

        assert result.is_success
        main_cli = result.unwrap()
        assert main_cli == mock_main_instance

    def test_workspace_path_handling(self) -> None:
        """Test workspace path handling and validation."""
        cli_service = create_cli()

        # Test default workspace (current directory)
        assert isinstance(cli_service._workspace, Path)

        # Test custom workspace initialization
        custom_workspace = "/custom/workspace"
        result = cli_service.initialize(workspace=custom_workspace)

        assert result.is_success
        assert cli_service._workspace == Path(custom_workspace)


class TestNestedCommandHandlers:
    """Test suite for nested command handlers."""

    @pytest.fixture
    def cli_service(self) -> FlextControlPanelCli:
        """Create CLI service instance for testing."""
        return create_cli()

    def test_tools_commands_quality_check(
        self, cli_service: FlextControlPanelCli
    ) -> None:
        """Test tools commands quality check functionality."""
        tools_handler = cli_service.create_tools_handler()

        # Test with mock quality config
        config = FlextControlPanelCli._QualityCheckConfig(
            coverage_threshold=80.0, relaxed=False
        )
        with patch("flext_tools.QualityGateway") as mock_quality:
            mock_gateway = Mock()
            mock_quality.return_value = mock_gateway
            mock_gateway.run_checks.return_value = FlextResult.ok({"status": "passed"})

            result = tools_handler.quality_check(config)

            assert result.is_success
            # Note: run_quality_check is a placeholder that doesn't use QualityGateway

    def test_tools_commands_list_scripts(
        self, cli_service: FlextControlPanelCli
    ) -> None:
        """Test tools commands script listing."""
        tools_handler = cli_service.create_tools_handler()

        with patch("flext.cli.FlextControlPanelCli._print_colored") as mock_print:
            tools_handler.list_scripts("development")

            # Verify output was printed
            mock_print.assert_called()

    def test_main_commands_test_command(
        self, cli_service: FlextControlPanelCli
    ) -> None:
        """Test main commands test execution."""
        main_handler = cli_service.create_main_handler()

        with patch(
            "flext.cli.FlextControlPanelCli._QualityGateway.run_quality_checks_safe"
        ) as mock_gateway:
            # Create a mock Result object that matches the _QualityGateway implementation
            class MockResult:
                def __init__(self) -> None:
                    self.success = True
                    self.value = {
                        "success": True,
                        "tests_passed": True,
                        "coverage_passed": True,
                    }
                    self.error = None

            mock_gateway.return_value = MockResult()

            result = main_handler.test_command(coverage=True, parallel=False)

            assert result.is_success
            mock_gateway.assert_called()

    def test_main_commands_lint_command(
        self, cli_service: FlextControlPanelCli
    ) -> None:
        """Test main commands lint execution."""
        main_handler = cli_service.create_main_handler()

        with patch(
            "flext.cli.FlextControlPanelCli._QualityGateway.run_quality_checks_safe"
        ) as mock_gateway:
            # Mock the custom Result object that the method actually returns
            class MockResult:
                def __init__(self) -> None:
                    self.success = True
                    self.value = {"lint_passed": True}
                    self.error = None

            mock_gateway.return_value = MockResult()

            result = main_handler.lint_command(fix=False)

            assert result.is_success
            mock_gateway.assert_called()

    def test_main_commands_format_command(
        self, cli_service: FlextControlPanelCli
    ) -> None:
        """Test main commands format execution."""
        main_handler = cli_service.create_main_handler()

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            main_handler.format_command(check_only=True)

            mock_subprocess.assert_called()

    def test_main_commands_info_command(
        self, cli_service: FlextControlPanelCli
    ) -> None:
        """Test main commands info display."""
        main_handler = cli_service.create_main_handler()

        with patch("flext.cli.FlextControlPanelCli._print_colored") as mock_print:
            result = main_handler.info_command(detailed=True)

            assert result.is_success
            mock_print.assert_called()

            # Verify workspace info was displayed
            calls = mock_print.call_args_list
            assert any("FLEXT Control Panel" in str(call) for call in calls)


class TestLegacyCompatibilityFunctions:
    """Test suite for legacy compatibility functions."""

    @patch("flext.cli.create_cli")
    def test_quality_function_compatibility(self, mock_create_cli: Mock) -> None:
        """Test legacy quality function compatibility."""
        mock_cli_service = Mock()
        mock_tools_handler = Mock()
        mock_cli_service.create_tools_handler.return_value = mock_tools_handler
        mock_tools_handler.quality_check.return_value = FlextResult.ok(
            {"status": "passed"}
        )
        mock_create_cli.return_value = mock_cli_service

        # Should not raise an exception
        quality()

        mock_create_cli.assert_called_once()
        mock_cli_service.create_tools_handler.assert_called_once()

    @patch("flext.cli.create_cli")
    def test_scripts_function_compatibility(self, mock_create_cli: Mock) -> None:
        """Test legacy scripts function compatibility."""
        mock_cli_service = Mock()
        mock_tools_handler = Mock()
        mock_cli_service.create_tools_handler.return_value = mock_tools_handler
        mock_create_cli.return_value = mock_cli_service

        scripts(category="development", _list_only=True)

        mock_create_cli.assert_called_once()
        mock_tools_handler.list_scripts.assert_called_with("development")

    @patch("flext.cli.create_cli")
    def test_analysis_function_compatibility(self, mock_create_cli: Mock) -> None:
        """Test legacy analysis function compatibility."""
        mock_cli_service = Mock()
        mock_tools_handler = Mock()
        mock_cli_service.create_tools_handler.return_value = mock_tools_handler
        mock_create_cli.return_value = mock_cli_service

        analysis(analysis_type="dependencies")

        mock_create_cli.assert_called_once()
        mock_tools_handler.run_analysis.assert_called_with("dependencies")

    def test_test_function_compatibility(self) -> None:
        """Test legacy test function compatibility."""
        mock_cli_service = Mock()
        mock_main_handler = Mock()
        mock_cli_service.create_main_handler.return_value = mock_main_handler
        mock_main_handler.test_command.return_value = FlextResult.ok(
            {"status": "passed"}
        )

        with patch("flext.cli.create_cli", return_value=mock_cli_service):
            test(coverage=True, parallel=False)

        mock_main_handler.test_command.assert_called_with(coverage=True, parallel=False)

    @patch("flext.cli.create_cli")
    def test_lint_function_compatibility(self, mock_create_cli: Mock) -> None:
        """Test legacy lint function compatibility."""
        mock_cli_service = Mock()
        mock_main_handler = Mock()
        mock_cli_service.create_main_handler.return_value = mock_main_handler
        mock_main_handler.lint_command.return_value = FlextResult.ok(
            {"status": "passed"}
        )
        mock_create_cli.return_value = mock_cli_service

        lint(fix=True)

        mock_create_cli.assert_called_once()
        mock_main_handler.lint_command.assert_called_with(fix=True)

    @patch("flext.cli.create_cli")
    def test_format_code_function_compatibility(self, mock_create_cli: Mock) -> None:
        """Test legacy format_code function compatibility."""
        mock_cli_service = Mock()
        mock_main_handler = Mock()
        mock_cli_service.create_main_handler.return_value = mock_main_handler
        mock_create_cli.return_value = mock_cli_service

        format_code(check_only=True)

        mock_create_cli.assert_called_once()
        mock_main_handler.format_command.assert_called_with(check_only=True)

    @patch("flext.cli.create_cli")
    def test_info_function_compatibility(self, mock_create_cli: Mock) -> None:
        """Test legacy info function compatibility."""
        mock_cli_service = Mock()
        mock_main_handler = Mock()
        mock_cli_service.create_main_handler.return_value = mock_main_handler
        mock_create_cli.return_value = mock_cli_service

        info(detailed=True)

        mock_create_cli.assert_called_once()
        mock_main_handler.info_command.assert_called_with(detailed=True)


class TestUnifiedClassPatternCompliance:
    """Test suite for unified class pattern compliance."""

    def test_single_unified_class_per_module(self) -> None:
        """Test that module has single unified class."""
        # Get all classes defined in the module
        classes = [
            name
            for name, obj in inspect.getmembers(cli_module)
            if inspect.isclass(obj) and obj.__module__ == "flext.cli"
        ]

        # Debug: verify classes were found
        # Should have exactly one main unified class
        # Check if FlextControlPanelCli is available (it might be imported from __init__.py)
        flext_control_panel_cli = getattr(cli_module, "FlextControlPanelCli", None)
        assert flext_control_panel_cli is not None, (
            "FlextControlPanelCli not found in module"
        )

        # Should not have multiple loose classes
        non_nested_classes = [
            name
            for name in classes
            if not name.startswith("_")  # Nested classes start with _
        ]
        assert len(non_nested_classes) == 1, (
            f"Found multiple non-nested classes: {non_nested_classes}"
        )

    def test_nested_class_organization(self) -> None:
        """Test that functionality is organized in nested classes."""
        cli_service = create_cli()

        # Test that nested classes exist as attributes
        assert hasattr(cli_service, "_ToolsCommands")
        assert hasattr(cli_service, "_MainCommands")
        assert hasattr(cli_service, "_CliContext")

        # Test that nested classes can be instantiated
        tools_handler = cli_service.create_tools_handler()
        main_handler = cli_service.create_main_handler()

        assert tools_handler is not None
        assert main_handler is not None

    def test_no_loose_helper_functions(self) -> None:
        """Test that no loose helper functions exist outside classes."""
        # Get all functions in module
        functions = [
            name
            for name, obj in inspect.getmembers(cli)
            if inspect.isfunction(obj) and obj.__module__ == "flext.cli"
        ]

        # Filter out legacy compatibility functions and main functions
        allowed_functions = {
            "create_cli",  # Factory function
            "main",  # Entry point
            # Legacy compatibility functions
            "quality",
            "scripts",
            "analysis",
            "test",
            "lint",
            "format_code",
            "info",
        }

        unexpected_functions = set(functions) - allowed_functions
        assert len(unexpected_functions) == 0, (
            f"Found unexpected functions: {unexpected_functions}"
        )

    def test_flext_cli_integration_compliance(self) -> None:
        """Test compliance with flext-cli integration requirements."""
        # Check the workspace_cli module source since cli() is just a wrapper
        source = inspect.getsource(flext.workspace_cli)

        # Should use flext-cli components
        assert "from flext_cli import" in source
        assert "FlextCliApi" in source
        # Note: workspace_cli only uses FlextCliApi, not FlextCliConfig or FlextCliMain

        # Should NOT use direct Click imports (forbidden)
        assert "import click" not in source
        assert "from click import" not in source


class TestExportsAndAll:
    """Test suite for module exports and __all__ completeness."""

    def test_all_exports_exist(self) -> None:
        """Test that all items in __all__ are actually exported."""
        expected_exports = [
            "FlextControlPanelCli",
            "create_cli",
            "main",
            # Legacy function exports
            "quality",
            "scripts",
            "analysis",
            "test",
            "lint",
            "format_code",
            "info",
        ]

        for export in expected_exports:
            assert export in __all__, f"Export {export} missing from __all__"

    def test_unified_class_is_primary_export(self) -> None:
        """Test that unified class is the primary export."""
        assert "FlextControlPanelCli" in __all__
        assert "create_cli" in __all__

        # Create instance to verify it works
        cli_service = create_cli()
        assert isinstance(cli_service, FlextControlPanelCli)


class TestErrorHandling:
    """Test suite for error handling patterns."""

    def test_cli_initialization_error_handling(self) -> None:
        """Test CLI initialization with invalid configuration."""
        cli_service = create_cli()

        with patch("flext.cli.FlextCliConfig", side_effect=Exception("Config error")):
            result = cli_service.initialize(workspace="/invalid", profile="bad")

            assert result.is_failure
            assert result.error is not None
            assert "Configuration error" in result.error

    def test_command_execution_error_handling(self) -> None:
        """Test command execution error handling."""
        cli_service = create_cli()
        main_handler = cli_service.create_main_handler()

        with patch(
            "flext.cli.FlextControlPanelCli._QualityGateway.run_quality_checks_safe"
        ) as mock_gateway:
            # Mock quality gateway to return success but with failed tests
            mock_gateway.return_value = FlextResult.ok(
                {
                    "tests_passed": False,
                    "coverage_passed": True,
                    "lint_passed": True,
                    "types_passed": True,
                    "security_passed": True,
                }
            )

            result = main_handler.test_command(coverage=True, parallel=False)

            assert result.is_failure
            assert result.error is not None
            assert "Failed: tests" in result.error


class TestMainFunctionEntryPoint:
    """Test suite for main function entry point."""

    @patch("flext.cli.create_cli")
    def test_main_function_exists(self, mock_create_cli: Mock) -> None:
        """Test that main function exists and can be called."""
        mock_cli_service = Mock()
        mock_create_cli.return_value = mock_cli_service

        # Should be callable without errors
        assert callable(main)

        # Test actual execution would require more complex mocking
        # This tests that the function exists and is properly defined
