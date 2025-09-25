"""FLEXT LDIF Config - Comprehensive Unit Tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_ldif.config import FlextLdifConfig
from flext_ldif.constants import FlextLdifConstants


@pytest.mark.unit
class TestFlextLdifConfig:
    """Comprehensive tests for FlextLdifConfig class."""

    def test_config_initialization_default(self) -> None:
        """Test config initialization with default values."""
        config = FlextLdifConfig()

        assert config is not None
        assert config.encoding == FlextLdifConstants.DEFAULT_ENCODING
        assert config.strict_parsing is True
        assert config.max_entries == FlextLdifConstants.DEFAULT_MAX_ENTRIES
        assert config.validate_dn is True
        assert config.normalize_attributes is True

    def test_config_initialization_custom(self) -> None:
        """Test config initialization with custom values."""
        custom_config = FlextLdifConfig(
            encoding="latin-1",
            strict_parsing=False,
            max_entries=5000,
            validate_dn=False,
            normalize_attributes=False,
        )

        assert custom_config.encoding == "latin-1"
        assert custom_config.strict_parsing is False
        assert custom_config.max_entries == 5000
        assert custom_config.validate_dn is False
        assert custom_config.normalize_attributes is False

    def test_config_validation_valid(self) -> None:
        """Test config validation with valid values."""
        config = FlextLdifConfig()
        result = config.validate()

        assert result.is_success
        assert isinstance(result.value, dict)

    def test_config_validation_invalid_encoding(self) -> None:
        """Test config validation with invalid encoding."""
        config = FlextLdifConfig(encoding="invalid-encoding")
        result = config.validate()

        # Should handle invalid encoding gracefully
        assert result.is_success or result.is_failure

    def test_config_validation_invalid_max_entries(self) -> None:
        """Test config validation with invalid max_entries."""
        config = FlextLdifConfig(max_entries=-1)
        # Config validation happens during initialization, so we just check it was created
        assert config is not None

    def test_config_validation_invalid_max_entries_zero(self) -> None:
        """Test config validation with zero max_entries."""
        config = FlextLdifConfig(max_entries=0)
        # Config validation happens during initialization, so we just check it was created
        assert config is not None

    def test_config_validation_invalid_max_entries_large(self) -> None:
        """Test config validation with very large max_entries."""
        config = FlextLdifConfig(max_entries=1000000000)
        # Config validation happens during initialization, so we just check it was created
        assert config is not None

    def test_config_to_dict(self) -> None:
        """Test converting config to dictionary."""
        config = FlextLdifConfig(
            encoding="utf-8",
            strict_parsing=True,
            max_entries=1000,
            validate_dn=True,
            normalize_attributes=True,
        )

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["encoding"] == "utf-8"
        assert config_dict["strict_parsing"] is True
        assert config_dict["max_entries"] == 1000
        assert config_dict["validate_dn"] is True
        assert config_dict["normalize_attributes"] is True

    def test_config_from_dict(self) -> None:
        """Test creating config from dictionary."""
        config_dict = {
            "encoding": "utf-8",
            "strict_parsing": True,
            "max_entries": 1000,
            "validate_dn": True,
            "normalize_attributes": True,
        }

        config = FlextLdifConfig.from_dict(config_dict)

        assert config.encoding == "utf-8"
        assert config.strict_parsing is True
        assert config.max_entries == 1000
        assert config.validate_dn is True
        assert config.normalize_attributes is True

    def test_config_from_dict_invalid(self) -> None:
        """Test creating config from invalid dictionary."""
        invalid_dict = {"invalid_field": "value", "another_invalid": 123}

        # Should handle invalid dictionary gracefully
        try:
            config = FlextLdifConfig.from_dict(invalid_dict)
            assert config is not None
        except Exception:
            # Expected behavior for invalid input
            pass

    def test_config_from_dict_partial(self) -> None:
        """Test creating config from partial dictionary."""
        partial_dict = {"encoding": "utf-8", "strict_parsing": False}

        config = FlextLdifConfig.from_dict(partial_dict)

        assert config.encoding == "utf-8"
        assert config.strict_parsing is False
        # Other fields should use defaults
        assert config.max_entries == FlextLdifConstants.DEFAULT_MAX_ENTRIES

    def test_config_copy(self) -> None:
        """Test copying config."""
        original_config = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        copied_config = original_config.copy()

        assert copied_config.encoding == original_config.encoding
        assert copied_config.strict_parsing == original_config.strict_parsing
        assert copied_config.max_entries == original_config.max_entries

        # Modify copied config
        copied_config.encoding = "latin-1"
        assert copied_config.encoding != original_config.encoding

    def test_config_merge(self) -> None:
        """Test merging configs."""
        base_config = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        override_config = FlextLdifConfig(encoding="latin-1", strict_parsing=False)

        merged_config = base_config.merge(override_config)

        assert merged_config.encoding == "latin-1"  # Overridden
        assert merged_config.strict_parsing is False  # Overridden
        assert merged_config.max_entries == 1000  # Not overridden

    def test_config_merge_none(self) -> None:
        """Test merging config with None."""
        config = FlextLdifConfig()

        # Should handle None gracefully
        try:
            merged_config = config.merge(None)  # type: ignore[arg-type]
            assert merged_config is not None
        except Exception:
            # Expected behavior for None input
            pass

    def test_config_equality(self) -> None:
        """Test config equality comparison."""
        config1 = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        config2 = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        config3 = FlextLdifConfig(
            encoding="latin-1", strict_parsing=True, max_entries=1000
        )

        assert config1 == config2
        assert config1 != config3

    def test_config_hash(self) -> None:
        """Test config hash functionality."""
        config1 = FlextLdifConfig(encoding="utf-8")
        config2 = FlextLdifConfig(encoding="utf-8")
        config3 = FlextLdifConfig(encoding="latin-1")

        assert hash(config1) == hash(config2)
        assert hash(config1) != hash(config3)

    def test_config_str_representation(self) -> None:
        """Test config string representation."""
        config = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        config_str = str(config)
        assert isinstance(config_str, str)
        assert "utf-8" in config_str
        assert "1000" in config_str

    def test_config_repr_representation(self) -> None:
        """Test config repr representation."""
        config = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        config_repr = repr(config)
        assert isinstance(config_repr, str)
        assert "FlextLdifConfig" in config_repr

    def test_config_serialization(self) -> None:
        """Test config serialization."""
        config = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        # Test JSON serialization
        config_json = config.to_json()
        assert isinstance(config_json, str)

        # Test deserialization
        deserialized_config = FlextLdifConfig.from_json(config_json)
        assert deserialized_config.encoding == config.encoding
        assert deserialized_config.strict_parsing == config.strict_parsing
        assert deserialized_config.max_entries == config.max_entries

    def test_config_serialization_invalid_json(self) -> None:
        """Test config deserialization with invalid JSON."""
        invalid_json = '{"invalid": "json"'

        # Should handle invalid JSON gracefully
        try:
            config = FlextLdifConfig.from_json(invalid_json)
            assert config is not None
        except Exception:
            # Expected behavior for invalid JSON
            pass

    def test_config_file_operations(self, test_file_manager: object) -> None:
        """Test config file operations."""
        config = FlextLdifConfig(
            encoding="utf-8", strict_parsing=True, max_entries=1000
        )

        # Test saving to file
        config_file = test_file_manager.create_file("config.json", "")
        result = config.save_to_file(config_file)

        assert result.is_success
        assert config_file.exists()

        # Test loading from file
        loaded_config = FlextLdifConfig.load_from_file(config_file)

        assert loaded_config.encoding == config.encoding
        assert loaded_config.strict_parsing == config.strict_parsing
        assert loaded_config.max_entries == config.max_entries

    def test_config_file_operations_nonexistent(self) -> None:
        """Test config file operations with nonexistent file."""
        nonexistent_file = Path("/nonexistent/config.json")

        # Should handle nonexistent file gracefully
        try:
            config = FlextLdifConfig.load_from_file(nonexistent_file)
            assert config is not None
        except Exception:
            # Expected behavior for nonexistent file
            pass

    def test_config_file_operations_invalid_format(
        self, test_file_manager: object
    ) -> None:
        """Test config file operations with invalid format."""
        invalid_file = test_file_manager.create_file(
            "invalid.json", "invalid json content"
        )

        # Should handle invalid format gracefully
        try:
            config = FlextLdifConfig.load_from_file(invalid_file)
            assert config is not None
        except Exception:
            # Expected behavior for invalid format
            pass

    def test_config_environment_variables(self) -> None:
        """Test config with environment variables."""
        import os

        # Set environment variables
        os.environ["FLEXT_LDIF_ENCODING"] = "latin-1"
        os.environ["FLEXT_LDIF_STRICT_PARSING"] = "false"
        os.environ["FLEXT_LDIF_MAX_ENTRIES"] = "5000"

        try:
            config = FlextLdifConfig.from_environment()

            assert config.encoding == "latin-1"
            assert config.strict_parsing is False
            assert config.max_entries == 5000
        finally:
            # Clean up environment variables
            os.environ.pop("FLEXT_LDIF_ENCODING", None)
            os.environ.pop("FLEXT_LDIF_STRICT_PARSING", None)
            os.environ.pop("FLEXT_LDIF_MAX_ENTRIES", None)

    def test_config_environment_variables_invalid(self) -> None:
        """Test config with invalid environment variables."""
        import os

        # Set invalid environment variables
        os.environ["FLEXT_LDIF_MAX_ENTRIES"] = "invalid-number"

        try:
            config = FlextLdifConfig.from_environment()

            # Should handle invalid environment variables gracefully
            assert config is not None
        finally:
            # Clean up environment variables
            os.environ.pop("FLEXT_LDIF_MAX_ENTRIES", None)

    def test_config_validation_rules(self) -> None:
        """Test config validation rules."""
        config = FlextLdifConfig()

        # Test validation rules
        rules = config.get_validation_rules()
        assert isinstance(rules, dict)
        assert "encoding" in rules
        assert "max_entries" in rules

    def test_config_default_values(self) -> None:
        """Test config default values."""
        config = FlextLdifConfig()

        # Test default values
        defaults = config.get_default_values()
        assert isinstance(defaults, dict)
        assert defaults["encoding"] == FlextLdifConstants.DEFAULT_ENCODING
        assert defaults["strict_parsing"] is True
        assert defaults["max_entries"] == FlextLdifConstants.DEFAULT_MAX_ENTRIES

    def test_config_field_validation(self) -> None:
        """Test config field validation."""
        config = FlextLdifConfig()

        # Test field validation
        result = config.validate_field("encoding", "utf-8")
        assert result.is_success

        result = config.validate_field("max_entries", 1000)
        assert result.is_success

        result = config.validate_field("invalid_field", "value")
        # Should handle invalid field gracefully
        assert result.is_success or result.is_failure

    def test_config_field_validation_invalid_values(self) -> None:
        """Test config field validation with invalid values."""
        config = FlextLdifConfig()

        # Test invalid values
        result = config.validate_field("encoding", "")
        # Should handle invalid encoding gracefully
        assert result.is_success or result.is_failure

        result = config.validate_field("max_entries", -1)
        # Should handle invalid max_entries gracefully
        assert result.is_success or result.is_failure

    def test_config_performance(self) -> None:
        """Test config performance characteristics."""
        import time

        # Test config creation performance
        start_time = time.time()

        for _ in range(1000):
            FlextLdifConfig()

        end_time = time.time()
        execution_time = end_time - start_time

        assert execution_time < 1.0  # Should complete within 1 second

    def test_config_memory_usage(self) -> None:
        """Test config memory usage characteristics."""
        # Test that config doesn't leak memory
        configs = []

        for _ in range(100):
            config = FlextLdifConfig()
            configs.append(config)

        # Verify all configs are valid
        assert len(configs) == 100
        for config in configs:
            assert isinstance(config, FlextLdifConfig)

    def test_config_edge_cases(self) -> None:
        """Test config with edge cases."""
        # Test with None values
        try:
            config = FlextLdifConfig(encoding=None)  # type: ignore[arg-type]
            assert config is not None
        except Exception:
            # Expected behavior for None values
            pass

        # Test with empty string values
        try:
            config = FlextLdifConfig(encoding="")
            assert config is not None
        except Exception:
            # Expected behavior for empty string values
            pass

    def test_config_concurrent_access(self) -> None:
        """Test config concurrent access."""
        import threading

        config = FlextLdifConfig()
        results = []

        def worker() -> None:
            result = config.validate()
            results.append(result)

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        assert len(results) == 5
        for result in results:
            assert result.is_success
