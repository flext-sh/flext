"""Unit tests for flext.base_cli module.

Tests for the CLI facade functionality following FLEXT testing patterns
with proper verification of flext-cli integration and facade pattern compliance.
"""

import inspect

from flext import base_cli
from flext.base_cli import (
    FlextCliApi,
    FlextCliConfig,
    FlextCliFormatters,
    FlextCliMain,
    FlextCliServices,
    __all__,
)


class TestFlextCliDirectExports:
    """Test suite for flext-cli direct exports - NO facades, NO aliases."""

    def test_flext_cli_main_import(self) -> None:
        """Test that FlextCliMain is properly imported from flext-cli."""
        assert FlextCliMain is not None
        assert hasattr(FlextCliMain, "__name__")

        # Verify it's imported from flext-cli, not local implementation
        assert "flext_cli" in str(FlextCliMain.__module__)

    def test_flext_cli_config_import(self) -> None:
        """Test that FlextCliConfig is properly imported from flext-cli."""
        assert FlextCliConfig is not None
        assert hasattr(FlextCliConfig, "__name__")

        # Verify it's imported from flext-cli
        assert "flext_cli" in str(FlextCliConfig.__module__)

    def test_flext_cli_services_import(self) -> None:
        """Test that FlextCliServices is properly imported from flext-cli."""
        assert FlextCliServices is not None
        assert hasattr(FlextCliServices, "__name__")

        # Verify it's imported from flext-cli
        assert "flext_cli" in str(FlextCliServices.__module__)

    def test_api_import(self) -> None:
        """Test that FlextCliApi is properly imported from flext-cli."""
        assert FlextCliApi is not None
        assert hasattr(FlextCliApi, "__name__")

        # Verify it's imported from flext-cli
        assert "flext_cli" in str(FlextCliApi.__module__)

    def test_formatters_import(self) -> None:
        """Test that FlextCliFormatters is properly imported from flext-cli."""
        assert FlextCliFormatters is not None
        assert hasattr(FlextCliFormatters, "__name__")

        # Verify it's imported from flext-cli
        assert "flext_cli" in str(FlextCliFormatters.__module__)

    def test_all_exports_available(self) -> None:
        """Test that all items in __all__ are actually exported."""
        expected_exports = [
            # Direct flext-cli exports
            "FlextCliApi",
            "FlextCliConfig",
            "FlextCliFormatters",
            "FlextCliMain",
            "FlextCliModels",
            "FlextCliServices",
        ]

        for export in expected_exports:
            assert export in __all__, f"Export {export} missing from __all__"

    def test_no_local_cli_implementation(self) -> None:
        """Test that no local CLI implementation exists - only direct re-exports."""
        # Verify all imports come from flext-cli, not local modules
        # Check module source to ensure it's just direct re-exports
        source_lines = inspect.getsourcelines(base_cli)[0]
        source_code = "".join(source_lines)

        # Should contain flext-cli imports
        assert "from flext_cli import" in source_code

        # Should NOT contain local class definitions
        assert "class BaseCLI" not in source_code
        assert "class FlextCLI" not in source_code

        # Should contain direct re-export comment
        assert "Direct re-export" in source_code or "re-exports" in source_code

    def test_classes_are_directly_accessible(self) -> None:
        """Test that all classes are directly accessible without instantiation."""
        # Verify all classes exist and are callable
        assert callable(FlextCliMain)
        assert callable(FlextCliConfig)
        assert callable(FlextCliApi)
        assert callable(FlextCliFormatters)
        assert callable(FlextCliServices)

    def test_classes_have_correct_names(self) -> None:
        """Test that all classes have correct names matching flext-cli."""
        assert FlextCliMain.__name__ == "FlextCliMain"
        assert FlextCliConfig.__name__ == "FlextCliConfig"
        assert FlextCliApi.__name__ == "FlextCliApi"
        assert FlextCliFormatters.__name__ == "FlextCliFormatters"
        assert FlextCliServices.__name__ == "FlextCliService"


class TestDirectImportCompliance:
    """Test suite for direct import compliance and anti-duplication enforcement."""

    def test_no_duplicate_functionality(self) -> None:
        """Test that no functionality is duplicated locally."""
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
            "# Backward compatibility",  # No compatibility aliases
            "FlextBaseCLI",  # No deprecated aliases
            "CLIConfig",  # No deprecated aliases
        ]

        for pattern in forbidden_patterns:
            assert pattern not in source_code, f"Found forbidden pattern: {pattern}"

    def test_anti_duplication_comments(self) -> None:
        """Test that anti-duplication enforcement comments are present."""
        source_lines = inspect.getsourcelines(base_cli)[0]
        source_code = "".join(source_lines)

        # Should contain direct re-export enforcement messaging
        required_comments = [
            "ZERO TOLERANCE",
            "NO ALIASES",
            "NO WRAPPERS",
            "Direct re-exports",
        ]

        for comment in required_comments:
            assert comment in source_code, f"Missing required comment: {comment}"


class TestDirectImportValidation:
    """Test suite for validating direct import approach."""

    def test_all_imports_are_direct(self) -> None:
        """Test that all imports are direct from flext-cli with no wrappers."""
        # Get all classes imported
        classes = [
            FlextCliApi,
            FlextCliConfig,
            FlextCliFormatters,
            FlextCliMain,
            FlextCliServices,
        ]

        # All classes should be directly from flext_cli module
        for cls in classes:
            assert "flext_cli" in str(cls.__module__), (
                f"{cls} not directly from flext_cli"
            )

    def test_no_alias_definitions(self) -> None:
        """Test that no alias definitions exist in the module."""
        source_lines = inspect.getsourcelines(base_cli)[0]
        source_code = "".join(source_lines)

        # Should not contain any alias assignments
        forbidden_aliases = [
            "FlextBaseCLI =",
            "CLIConfig =",
            "FlextCLI =",
            "with_config =",
            "with_output_format =",
        ]

        for alias in forbidden_aliases:
            assert alias not in source_code, f"Found forbidden alias: {alias}"


class TestModuleDocumentation:
    """Test suite for module documentation and standards compliance."""

    def test_module_docstring_present(self) -> None:
        """Test that module has proper docstring."""
        assert base_cli.__doc__ is not None
        assert len(base_cli.__doc__.strip()) > 0

        # Should contain key information
        doc = base_cli.__doc__
        assert doc is not None
        assert "FLEXT CLI" in doc
        assert "Direct Re-export" in doc
        assert "flext-cli" in doc

    def test_copyright_and_license(self) -> None:
        """Test that proper copyright and license are present."""
        doc = base_cli.__doc__
        assert doc is not None
        # Type narrowing for pyright
        doc_str: str = doc
        assert "Copyright" in doc_str
        assert "2025 FLEXT Team" in doc_str
        assert "SPDX-License-Identifier: MIT" in doc_str

    def test_direct_import_documentation(self) -> None:
        """Test that direct import policy is documented."""
        doc = base_cli.__doc__
        assert doc is not None
        # Type narrowing for pyright
        doc_str: str = doc
        assert "ZERO TOLERANCE" in doc_str
        assert "NO ALIASES" in doc_str
        assert "NO WRAPPERS" in doc_str
