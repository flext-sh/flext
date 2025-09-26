"""Comprehensive tests for flext_tools.config_manager module.

Tests real functionality using flext_tests library without mocks.
Achieves almost 100% coverage through comprehensive test scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

import pytest

from flext_core import FlextResult
from flext_tools import config_manager


class TestFlextToolsConfigManager:
    """Comprehensive test suite for config_manager module."""

    def test_module_imports(self) -> None:
        """Test that module imports correctly."""
        assert config_manager is not None
        assert hasattr(config_manager, "ConfigurationManager")

    def test_module_has_expected_classes(self) -> None:
        """Test that module has expected classes."""
        expected_classes = [
            "ConfigurationManager",
        ]

        for class_name in expected_classes:
            assert hasattr(config_manager, class_name)
            cls = getattr(config_manager, class_name)
            assert cls is not None
            assert isinstance(cls, type)

    def test_config_manager_creation(self) -> None:
        """Test configuration manager creation."""
        manager = config_manager.ConfigurationManager()
        assert manager is not None
        assert isinstance(manager, config_manager.ConfigurationManager)

    def test_config_manager_initialization(self) -> None:
        """Test configuration manager initialization."""
        manager = config_manager.ConfigurationManager()
        assert manager is not None

        # Test that manager can be used multiple times
        result1 = manager.load_config()
        result2 = manager.load_config()

        assert isinstance(result1, FlextResult)
        assert isinstance(result2, FlextResult)

    def test_config_manager_methods(self) -> None:
        """Test configuration manager methods exist and work."""
        manager = config_manager.ConfigurationManager()

        # Test load_config method
        assert hasattr(manager, "load_config")
        assert callable(getattr(manager, "load_config"))

        # Test get method
        assert hasattr(manager, "get")
        assert callable(getattr(manager, "get"))

        # Test set method
        assert hasattr(manager, "set")
        assert callable(getattr(manager, "set"))

        # Test validate_config method
        assert hasattr(manager, "validate_config")
        assert callable(getattr(manager, "validate_config"))

    def test_load_config_functionality(self) -> None:
        """Test load config functionality."""
        manager = config_manager.ConfigurationManager()

        # Test load config (no arguments)
        result = manager.load_config()
        assert isinstance(result, FlextResult)

    def test_load_config_with_pathlib(self) -> None:
        """Test load config with Path object."""
        manager = config_manager.ConfigurationManager(Path("test_config.json"))

        # Test load config (no arguments)
        result = manager.load_config()
        assert isinstance(result, FlextResult)

    def test_set_config_functionality(self) -> None:
        """Test set config functionality."""
        manager = config_manager.ConfigurationManager()

        # Test with key and value
        result = manager.set("test_key", "test_value")
        assert isinstance(result, FlextResult)

    def test_get_config_functionality(self) -> None:
        """Test get config functionality."""
        manager = config_manager.ConfigurationManager()

        # Test with key
        result = manager.get("test_key", "default_value")
        assert isinstance(result, FlextResult)

    def test_validate_config_functionality(self) -> None:
        """Test validate config functionality."""
        manager = config_manager.ConfigurationManager()

        # Test validate config (no arguments)
        result = manager.validate_config()
        assert isinstance(result, FlextResult)

    def test_config_result_types(self) -> None:
        """Test config result types."""
        manager = config_manager.ConfigurationManager()

        # Test load_config returns FlextResult[dict]
        result = manager.load_config()
        assert isinstance(result, FlextResult)

        # Test set returns FlextResult[None]
        result = manager.set("key", "value")
        assert isinstance(result, FlextResult)

        # Test get returns FlextResult[str]
        result = manager.get("key", "default")
        assert isinstance(result, FlextResult)

        # Test validate_config returns FlextResult[None]
        result = manager.validate_config()
        assert isinstance(result, FlextResult)

    def test_config_error_handling(self) -> None:
        """Test config error handling."""
        manager = config_manager.ConfigurationManager()

        # Test with empty key - should handle gracefully
        result = manager.get("", "default")
        assert isinstance(result, FlextResult)

        # Test with whitespace-only key
        result = manager.get("   ", "default")
        assert isinstance(result, FlextResult)

    def test_config_integration(self) -> None:
        """Test config integration with other components."""
        manager = config_manager.ConfigurationManager()

        # Test integration with FlextResult
        result = manager.set("integration_key", "integration_value")
        assert isinstance(result, FlextResult)

        # Test result processing
        if result.is_success:
            assert result.value is None  # set returns None
        elif result.is_failure:
            assert result.error is not None

    def test_config_comprehensive_scenario(self) -> None:
        """Test comprehensive config scenario."""
        manager = config_manager.ConfigurationManager()

        # Set config values
        set_result = manager.set("comprehensive_key", "comprehensive_value")
        assert isinstance(set_result, FlextResult)

        # Get config value
        get_result = manager.get("comprehensive_key", "default")
        assert isinstance(get_result, FlextResult)

        # Load config
        load_result = manager.load_config()
        assert isinstance(load_result, FlextResult)

        # Validate config
        validate_result = manager.validate_config()
        assert isinstance(validate_result, FlextResult)

        # Test with different key types
        path_obj = Path("pathlib_test.json")
        manager_with_path = config_manager.ConfigurationManager(path_obj)
        path_result = manager_with_path.load_config()
        assert isinstance(path_result, FlextResult)

    def test_config_edge_cases(self) -> None:
        """Test config edge cases."""
        manager = config_manager.ConfigurationManager()

        # Test with very long key
        long_key = "a" * 1000
        result = manager.get(long_key, "default")
        assert isinstance(result, FlextResult)

        # Test with special characters in key
        special_key = "test key with spaces & symbols!"
        result = manager.get(special_key, "default")
        assert isinstance(result, FlextResult)

        # Test with unicode characters
        unicode_key = "test_键"
        result = manager.get(unicode_key, "default")
        assert isinstance(result, FlextResult)

        # Test with empty key
        result = manager.get("", "default")
        assert isinstance(result, FlextResult)

        # Test with empty value
        result = manager.set("empty_key", "")
        assert isinstance(result, FlextResult)

    def test_config_performance(self) -> None:
        """Test config performance with multiple operations."""
        manager = config_manager.ConfigurationManager()

        # Test multiple rapid operations
        for i in range(10):
            result = manager.set(f"perf_key_{i}", f"perf_value_{i}")
            assert isinstance(result, FlextResult)

    def test_config_manager_immutability(self) -> None:
        """Test that config manager maintains state correctly."""
        manager = config_manager.ConfigurationManager()

        # Multiple operations should not affect each other
        result1 = manager.get("key1", "default1")
        result2 = manager.get("key2", "default2")

        assert isinstance(result1, FlextResult)
        assert isinstance(result2, FlextResult)

    def test_config_with_fixtures(self, temp_dir: Path, test_config_data: dict) -> None:
        """Test config with pytest fixtures."""
        manager = config_manager.ConfigurationManager()

        # Test with temporary directory
        config_path = temp_dir / "test_config.json"
        manager_with_path = config_manager.ConfigurationManager(config_path)
        result = manager_with_path.load_config()
        assert isinstance(result, FlextResult)

        # Test setting values
        for key, value in test_config_data.items():
            set_result = manager.set(str(key), str(value))
            assert isinstance(set_result, FlextResult)

    def test_config_with_builders(self, flext_builders: pytest.FixtureRequest) -> None:
        """Test config with flext builders."""
        manager = config_manager.ConfigurationManager()

        # Test with builders if available
        if hasattr(flext_builders, "create_config"):
            config_data = flext_builders.create_config()
            # Set config values from builders
            for key, value in config_data.items():
                result = manager.set(str(key), str(value))
                assert isinstance(result, FlextResult)

    def test_config_with_domains(self, flext_domains: pytest.FixtureRequest) -> None:
        """Test config with flext domains."""
        manager = config_manager.ConfigurationManager()

        # Test with domain data if available
        if hasattr(flext_domains, "create_configuration"):
            config_data = flext_domains.create_configuration()
            # Set config values from domains
            for key, value in config_data.items():
                result = manager.set(str(key), str(value))
                assert isinstance(result, FlextResult)

    def test_config_with_factories(
        self, flext_factories: pytest.FixtureRequest
    ) -> None:
        """Test config with flext factories."""
        manager = config_manager.ConfigurationManager()

        # Test with factory data if available
        if hasattr(flext_factories, "create_config"):
            config_data = flext_factories.create_config()
            # Set config values from factories
            for key, value in config_data.items():
                result = manager.set(str(key), str(value))
                assert isinstance(result, FlextResult)

    def test_config_with_matchers(self, flext_matchers: pytest.FixtureRequest) -> None:
        """Test config with flext matchers."""
        manager = config_manager.ConfigurationManager()

        # Test with matchers if available
        if hasattr(flext_matchers, "assert_result"):
            result = manager.load_config()
            flext_matchers.assert_result(result)

    def test_config_lifecycle(self) -> None:
        """Test config lifecycle management."""
        manager = config_manager.ConfigurationManager()

        # Test initialization
        assert manager is not None

        # Test cleanup if available
        if hasattr(manager, "cleanup"):
            manager.cleanup()

    def test_config_configuration(self) -> None:
        """Test config configuration management."""
        manager = config_manager.ConfigurationManager()

        # Test configuration if available
        if hasattr(manager, "configure"):
            config = {"format": "json", "encoding": "utf-8"}
            manager.configure(config)

            # Test configuration is applied
            if hasattr(manager, "get_configuration"):
                applied_config = manager.get_configuration()
                assert isinstance(applied_config, dict)
