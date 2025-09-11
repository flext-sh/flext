"""Unit tests for flext.base_cli module.

Tests for the CLI facade functionality following FLEXT testing patterns
with proper verification of flext-cli integration and facade pattern compliance.
"""

from unittest.mock import Mock, patch

from flext.base_cli import (
    CLIConfig,
    # Backward compatibility (deprecated)
    FlextBaseCLI,
    FlextCLI,
    FlextCLICommand,
    FlextCLIConfig,
    FlextCLIGroup,
    __all__,
    with_config,
    with_output_format,
)


class TestFlextCLIFacade:
    """Test suite for flext-cli facade functionality."""

    def test_flext_cli_import(self) -> None:
        """Test that FlextCLI is properly imported from flext-cli."""
        assert FlextCLI is not None
        assert hasattr(FlextCLI, "__name__")

        # Verify it's imported from flext-cli, not local implementation
        assert "flext_cli" in str(FlextCLI.__module__)

    def test_flext_cli_config_import(self) -> None:
        """Test that FlextCLIConfig is properly imported from flext-cli."""
        assert FlextCLIConfig is not None
        assert hasattr(FlextCLIConfig, "__name__")

        # Verify it's imported from flext-cli
        assert "flext_cli" in str(FlextCLIConfig.__module__)

    def test_flext_cli_command_import(self) -> None:
        """Test that FlextCLICommand is properly imported from flext-cli."""
        assert FlextCLICommand is not None
        assert hasattr(FlextCLICommand, "__name__")

        # Verify it's imported from flext-cli
        assert "flext_cli" in str(FlextCLICommand.__module__)

    def test_flext_cli_group_import(self) -> None:
        """Test that FlextCLIGroup is properly imported from flext-cli."""
        assert FlextCLIGroup is not None
        assert hasattr(FlextCLIGroup, "__name__")

        # Verify it's imported from flext-cli
        assert "flext_cli" in str(FlextCLIGroup.__module__)

    def test_decorators_import(self) -> None:
        """Test that decorators are properly imported from flext-cli."""
        assert with_config is not None
        assert with_output_format is not None

        # Verify they are callable decorators
        assert callable(with_config)
        assert callable(with_output_format)

    def test_backward_compatibility_aliases(self) -> None:
        """Test backward compatibility aliases are properly set up."""
        # Test FlextBaseCLI alias
        assert FlextBaseCLI is FlextCLI
        assert FlextBaseCLI == FlextCLI

        # Test CLIConfig alias
        assert CLIConfig is FlextCLIConfig
        assert CLIConfig == FlextCLIConfig

    def test_all_exports_available(self) -> None:
        """Test that all items in __all__ are actually exported."""
        expected_exports = [
            # Modern flext-cli patterns
            "FlextCLI",
            "FlextCLIConfig",
            "FlextCLICommand",
            "FlextCLIGroup",
            "with_config",
            "with_output_format",
            # Backward compatibility (deprecated)
            "FlextBaseCLI",
            "CLIConfig",
        ]

        for export in expected_exports:
            assert export in __all__, f"Export {export} missing from __all__"

    def test_no_local_cli_implementation(self) -> None:
        """Test that no local CLI implementation exists - only facade."""
        # Verify all imports come from flext-cli, not local modules
        # Check module source to ensure it's just a facade
        import inspect

        from flext import base_cli

        source_lines = inspect.getsourcelines(base_cli)[0]
        source_code = "".join(source_lines)

        # Should contain flext-cli imports
        assert "from flext_cli import" in source_code

        # Should NOT contain local class definitions
        assert "class BaseCLI" not in source_code
        assert "class FlextCLI" not in source_code

        # Should contain facade comment
        assert "facade" in source_code.lower() or "FACADE" in source_code

    @patch("flext_cli.FlextCLI")
    def test_flext_cli_instantiation(self, mock_flext_cli) -> None:
        """Test that FlextCLI can be instantiated through facade."""
        mock_instance = Mock()
        mock_flext_cli.return_value = mock_instance

        # Create instance through facade
        cli_instance = FlextCLI()

        # Verify mock was called
        mock_flext_cli.assert_called_once()
        assert cli_instance == mock_instance

    @patch("flext_cli.FlextCLIConfig")
    def test_flext_cli_config_instantiation(self, mock_config) -> None:
        """Test that FlextCLIConfig can be instantiated through facade."""
        mock_instance = Mock()
        mock_config.return_value = mock_instance

        # Create instance through facade
        config_instance = FlextCLIConfig()

        # Verify mock was called
        mock_config.assert_called_once()
        assert config_instance == mock_instance


class TestFacadePatternCompliance:
    """Test suite for facade pattern compliance and anti-duplication enforcement."""

    def test_no_duplicate_functionality(self) -> None:
        """Test that no functionality is duplicated locally."""
        import inspect

        from flext import base_cli

        # Get all members of base_cli module
        members = inspect.getmembers(base_cli)

        # Filter for classes and functions (excluding imports)
        local_definitions = [
            name
            for name, obj in members
            if (inspect.isclass(obj) or inspect.isfunction(obj))
            and obj.__module__ == "flext.base_cli"
        ]

        # Should have no local class or function definitions
        # Everything should be imported from flext-cli
        assert len(local_definitions) == 0, (
            f"Found local definitions: {local_definitions}"
        )

    def test_domain_separation_compliance(self) -> None:
        """Test that module respects domain separation - only CLI functionality."""
        import inspect

        from flext import base_cli

        source_lines = inspect.getsourcelines(base_cli)[0]
        source_code = "".join(source_lines)

        # Should only import from flext-cli for CLI functionality
        assert "from flext_cli import" in source_code

        # Should NOT import from other domains
        forbidden_imports = [
            "from flext_core import",  # Core domain (except FlextResult which is universal)
            "from flext_api import",  # API domain
            "from flext_auth import",  # Auth domain
            "from flext_db import",  # Database domain
        ]

        for forbidden in forbidden_imports:
            assert forbidden not in source_code, f"Found forbidden import: {forbidden}"

    def test_zero_tolerance_enforcement(self) -> None:
        """Test zero tolerance policy - no local CLI implementations."""
        import inspect

        from flext import base_cli

        source_lines = inspect.getsourcelines(base_cli)[0]
        source_code = "".join(source_lines)

        # Forbidden patterns that would indicate local implementation
        forbidden_patterns = [
            "import click",  # Direct Click usage forbidden
            "import rich",  # Direct Rich usage forbidden
            "from click import",  # Click components forbidden
            "from rich import",  # Rich components forbidden
            "class.*CLI",  # Local CLI class definitions
            "def.*command",  # Local command functions
            "def.*group",  # Local group functions
        ]

        for pattern in forbidden_patterns:
            assert pattern not in source_code, f"Found forbidden pattern: {pattern}"

    def test_anti_duplication_comments(self) -> None:
        """Test that anti-duplication enforcement comments are present."""
        import inspect

        from flext import base_cli

        source_lines = inspect.getsourcelines(base_cli)[0]
        source_code = "".join(source_lines)

        # Should contain anti-duplication enforcement messaging
        required_comments = [
            "ANTI-DUPLICATION ENFORCEMENT",
            "ZERO TOLERANCE",
            "NO LOCAL IMPLEMENTATIONS",
            "facade",
        ]

        for comment in required_comments:
            assert comment in source_code, f"Missing required comment: {comment}"


class TestBackwardCompatibility:
    """Test suite for backward compatibility with deprecated aliases."""

    def test_deprecated_aliases_work(self) -> None:
        """Test that deprecated aliases still function for backward compatibility."""
        # Test FlextBaseCLI alias
        assert FlextBaseCLI is not None
        assert FlextBaseCLI == FlextCLI

        # Test CLIConfig alias
        assert CLIConfig is not None
        assert CLIConfig == FlextCLIConfig

    def test_deprecated_aliases_point_to_modern_equivalents(self) -> None:
        """Test that deprecated aliases point to modern flext-cli equivalents."""
        # FlextBaseCLI should be the same object as FlextCLI
        assert FlextBaseCLI is FlextCLI
        assert id(FlextBaseCLI) == id(FlextCLI)

        # CLIConfig should be the same object as FlextCLIConfig
        assert CLIConfig is FlextCLIConfig
        assert id(CLIConfig) == id(FlextCLIConfig)

    @patch("flext_cli.FlextCLI")
    def test_deprecated_alias_instantiation(self, mock_flext_cli) -> None:
        """Test that deprecated aliases can still be instantiated."""
        mock_instance = Mock()
        mock_flext_cli.return_value = mock_instance

        # Create instance using deprecated alias
        cli_instance = FlextBaseCLI()

        # Should work the same as modern equivalent
        mock_flext_cli.assert_called_once()
        assert cli_instance == mock_instance


class TestModuleDocumentation:
    """Test suite for module documentation and standards compliance."""

    def test_module_docstring_present(self) -> None:
        """Test that module has proper docstring."""
        from flext import base_cli

        assert base_cli.__doc__ is not None
        assert len(base_cli.__doc__.strip()) > 0

        # Should contain key information
        doc = base_cli.__doc__
        assert "FLEXT CLI" in doc
        assert "facade" in doc.lower()
        assert "flext-cli" in doc

    def test_copyright_and_license(self) -> None:
        """Test that proper copyright and license are present."""
        from flext import base_cli

        doc = base_cli.__doc__
        assert "Copyright" in doc
        assert "2025 FLEXT Team" in doc
        assert "SPDX-License-Identifier: MIT" in doc

    def test_anti_duplication_documentation(self) -> None:
        """Test that anti-duplication policy is documented."""
        from flext import base_cli

        doc = base_cli.__doc__
        assert "ANTI-DUPLICATION ENFORCEMENT" in doc
        assert "ZERO TOLERANCE" in doc
        assert "NO LOCAL IMPLEMENTATIONS" in doc
