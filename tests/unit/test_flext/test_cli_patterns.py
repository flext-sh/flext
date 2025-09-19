"""Unit tests for flext.cli_patterns module.

Tests for CLI patterns and direct re-exports following FLEXT testing patterns
with proper validation of domain separation compliance.
"""

from __future__ import annotations

import inspect

import flext.cli_patterns as patterns_module
from flext.cli_patterns import (
    FlextCliApi,
    FlextCliConfigs,
    FlextCliFormatters,
    FlextCliMain,
    __all__,
)
from flext_cli import (
    FlextCliApi as OriginalApi,
    FlextCliConfigs as OriginalConfigs,
    FlextCliFormatters as OriginalFormatters,
    FlextCliMain as OriginalMain,
)


class TestCliPatterns:
    """Test suite for CLI patterns module."""

    def test_cli_patterns_exports(self) -> None:
        """Test that cli_patterns module exports expected components."""
        # Assert
        assert "__all__" in dir(__import__("flext.cli_patterns"))
        assert isinstance(__all__, list)
        assert "FlextCliApi" in __all__
        assert "FlextCliConfigs" in __all__
        assert "FlextCliFormatters" in __all__
        assert "FlextCliMain" in __all__

    def test_flext_cli_api_import_from_patterns(self) -> None:
        """Test that FlextCliApi can be imported from cli_patterns."""
        # Act & Assert
        assert FlextCliApi is not None
        assert hasattr(FlextCliApi, "__name__")

    def test_flext_cli_configs_import_from_patterns(self) -> None:
        """Test that FlextCliConfigs can be imported from cli_patterns."""
        # Act & Assert
        assert FlextCliConfigs is not None
        assert hasattr(FlextCliConfigs, "__name__")

    def test_flext_cli_formatters_import_from_patterns(self) -> None:
        """Test that FlextCliFormatters can be imported from cli_patterns."""
        # Act & Assert
        assert FlextCliFormatters is not None
        assert hasattr(FlextCliFormatters, "__name__")

    def test_flext_cli_main_import_from_patterns(self) -> None:
        """Test that FlextCliMain can be imported from cli_patterns."""
        # Act & Assert
        assert FlextCliMain is not None
        assert hasattr(FlextCliMain, "__name__")

    def test_module_structure(self) -> None:
        """Test that cli_patterns module has correct structure."""
        # Assert module properties
        assert hasattr(patterns_module, "__all__")
        assert hasattr(patterns_module, "__doc__")
        assert patterns_module.__doc__ is not None
        assert "FLEXT CLI Patterns" in patterns_module.__doc__

    def test_zero_tolerance_enforcement_documentation(self) -> None:
        """Test that zero tolerance enforcement is properly documented."""
        doc = patterns_module.__doc__ or ""

        # Assert key concepts are documented
        assert "FLEXT CLI Patterns" in doc
        assert "ZERO TOLERANCE ENFORCEMENT" in doc
        assert "DIRECT re-exports" in doc
        assert "NO aliases" in doc
        assert "NO wrappers" in doc
        assert "NO compatibility layers" in doc

    def test_direct_re_exports_compliance(self) -> None:
        """Test that module only contains direct re-exports."""
        # Test that the module exports only the expected classes
        expected_exports = {
            "FlextCliApi",
            "FlextCliConfigs",
            "FlextCliFormatters",
            "FlextCliMain",
        }

        actual_exports = set(__all__)
        assert actual_exports == expected_exports

    def test_no_aliases_or_wrappers(self) -> None:
        """Test that there are no aliases or wrappers in the module."""
        # Import the module and check it has no additional attributes
        cp = patterns_module

        # Get all public attributes (excluding special methods and annotations)
        public_attrs = [
            attr
            for attr in dir(cp)
            if not attr.startswith("_") and attr != "annotations"
        ]

        # Should only contain the four direct re-exports
        expected_attrs = {
            "FlextCliApi",
            "FlextCliConfigs",
            "FlextCliFormatters",
            "FlextCliMain",
        }

        actual_attrs = set(public_attrs)
        assert actual_attrs == expected_attrs

    def test_flext_domain_separation_compliance(self) -> None:
        """Test compliance with FLEXT domain separation rules."""
        # Test that all exported classes are from flext_cli

        # Assert that the re-exports are the same as the originals
        assert FlextCliApi is OriginalApi
        assert FlextCliConfigs is OriginalConfigs
        assert FlextCliFormatters is OriginalFormatters
        assert FlextCliMain is OriginalMain


class TestDirectReExportsPattern:
    """Test suite for direct re-exports pattern compliance."""

    def test_pattern_follows_zero_aliases_rule(self) -> None:
        """Test that pattern follows zero aliases rule."""
        cp = patterns_module

        # Get the source lines of the module
        source_lines = inspect.getsourcelines(cp)[0]
        source_text = "".join(source_lines)

        # Should not contain any alias assignments
        assert " = FlextCli" not in source_text
        assert "BaseCLI" not in source_text
        assert "with_config" not in source_text
        assert "with_output_format" not in source_text

    def test_pattern_uses_direct_imports_only(self) -> None:
        """Test that pattern uses only direct imports."""
        cp = patterns_module

        # Get the source lines of the module
        source_lines = inspect.getsourcelines(cp)[0]
        source_text = "".join(source_lines)

        # Should contain direct imports from flext_cli
        assert "from flext_cli import (" in source_text
        assert "FlextCliApi," in source_text
        assert "FlextCliConfigs," in source_text
        assert "FlextCliFormatters," in source_text
        assert "FlextCliMain," in source_text

    def test_copyright_and_licensing(self) -> None:
        """Test that module has proper copyright and licensing."""
        doc = patterns_module.__doc__ or ""

        # Assert licensing information
        assert "Copyright (c) 2025 FLEXT Team" in doc
        assert "SPDX-License-Identifier: MIT" in doc


class TestModuleExportsCompliance:
    """Test suite for module exports compliance."""

    def test_all_list_matches_actual_exports(self) -> None:
        """Test that __all__ list matches what's actually exported."""
        cp = patterns_module

        # Get what's in __all__
        all_exports = set(__all__)

        # Get what's actually available for import
        available_exports = {
            name
            for name in dir(cp)
            if not name.startswith("_") and name != "annotations" and hasattr(cp, name)
        }

        assert all_exports == available_exports

    def test_no_legacy_exports_remain(self) -> None:
        """Test that no legacy exports remain in __all__."""
        # These should not be in __all__ anymore
        legacy_exports = {
            "BaseCLI",
            "FlextCLI",
            "FlextCLICommand",
            "FlextCLIConfig",
            "FlextCLIGroup",
            "with_config",
            "with_output_format",
        }

        actual_exports = set(__all__)
        assert not actual_exports.intersection(legacy_exports)

    def test_only_clean_api_exported(self) -> None:
        """Test that only clean API is exported."""
        # Should only export the four clean classes
        clean_exports = {
            "FlextCliApi",
            "FlextCliConfigs",
            "FlextCliFormatters",
            "FlextCliMain",
        }

        actual_exports = set(__all__)
        assert actual_exports == clean_exports
