"""FLEXT CLI Mixins Tests - Comprehensive mixins functionality testing.

Tests for FlextCliMixins class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.mixins import FlextCliMixins


class TestFlextCliMixins:
    """Comprehensive tests for FlextCliMixins class."""

    def test_mixins_initialization(self) -> None:
        """Test Mixins initialization with proper configuration."""
        mixins = FlextCliMixins()
        assert mixins is not None
        assert isinstance(mixins, FlextCliMixins)

    def test_validation_mixin_not_empty(self) -> None:
        """Test ValidationMixin.validate_not_empty method."""
        # Test valid non-empty string
        result = FlextCliMixins.ValidationMixin.validate_not_empty(
            "test_field", "valid_value"
        )
        assert result.is_success

        # Test empty string
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", "")
        assert result.is_failure
        assert "cannot be empty" in result.error

        # Test whitespace-only string
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", "   ")
        assert result.is_failure
        assert "cannot be empty" in result.error

        # Test None value
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", None)
        assert result.is_failure
        assert "cannot be empty" in result.error

        # Test zero value
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", 0)
        assert result.is_failure
        assert "cannot be empty" in result.error

        # Test valid number
        result = FlextCliMixins.ValidationMixin.validate_not_empty("test_field", 42)
        assert result.is_success

    def test_validation_mixin_url(self) -> None:
        """Test ValidationMixin.validate_url method."""
        # Test valid HTTP URL
        result = FlextCliMixins.ValidationMixin.validate_url(
            "url_field", "http://example.com"
        )
        assert result.is_success

        # Test valid HTTPS URL
        result = FlextCliMixins.ValidationMixin.validate_url(
            "url_field", "https://example.com"
        )
        assert result.is_success

        # Test empty URL
        result = FlextCliMixins.ValidationMixin.validate_url("url_field", "")
        assert result.is_failure
        assert "cannot be empty" in result.error

        # Test invalid URL format
        result = FlextCliMixins.ValidationMixin.validate_url(
            "url_field", "ftp://example.com"
        )
        assert result.is_failure
        assert "must start with http:// or https://" in result.error

    def test_validation_mixin_enum_value(self) -> None:
        """Test ValidationMixin.validate_enum_value method."""
        valid_values = ["option1", "option2", "option3"]

        # Test valid enum value
        result = FlextCliMixins.ValidationMixin.validate_enum_value(
            "test_field", "option1", valid_values
        )
        assert result.is_success

        # Test invalid enum value
        result = FlextCliMixins.ValidationMixin.validate_enum_value(
            "test_field", "invalid_option", valid_values
        )
        assert result.is_failure
        assert "Invalid test_field" in result.error
        assert "Valid values:" in result.error

    def test_validation_mixin_positive_number(self) -> None:
        """Test ValidationMixin.validate_positive_number method."""
        # Test positive number
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_field", 42
        )
        assert result.is_success

        # Test zero
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_field", 0
        )
        assert result.is_failure
        assert "must be positive" in result.error

        # Test negative number
        result = FlextCliMixins.ValidationMixin.validate_positive_number(
            "test_field", -5
        )
        assert result.is_failure
        assert "must be positive" in result.error

    def test_validation_mixin_non_negative_number(self) -> None:
        """Test ValidationMixin.validate_non_negative_number method."""
        # Test positive number
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_field", 42
        )
        assert result.is_success

        # Test zero
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_field", 0
        )
        assert result.is_success

        # Test negative number
        result = FlextCliMixins.ValidationMixin.validate_non_negative_number(
            "test_field", -5
        )
        assert result.is_failure
        assert "cannot be negative" in result.error

    def test_validation_mixin_output_format(self) -> None:
        """Test ValidationMixin.validate_output_format method."""
        # Test valid output format
        result = FlextCliMixins.ValidationMixin.validate_output_format("json")
        assert result.is_success

        # Test invalid output format
        result = FlextCliMixins.ValidationMixin.validate_output_format("invalid_format")
        assert result.is_failure
        assert "Invalid output format" in result.error

    def test_validation_mixin_log_level(self) -> None:
        """Test ValidationMixin.validate_log_level method."""
        # Test valid log level
        result = FlextCliMixins.ValidationMixin.validate_log_level("INFO")
        assert result.is_success

        # Test invalid log level
        result = FlextCliMixins.ValidationMixin.validate_log_level("INVALID_LEVEL")
        assert result.is_failure
        assert "Invalid log level" in result.error

    def test_validation_mixin_status(self) -> None:
        """Test ValidationMixin.validate_status method."""
        # Test valid status
        result = FlextCliMixins.ValidationMixin.validate_status("pending")
        assert result.is_success

        # Test invalid status
        result = FlextCliMixins.ValidationMixin.validate_status("invalid_status")
        assert result.is_failure
        assert "Invalid status" in result.error

    def test_business_rules_mixin_command_execution_state(self) -> None:
        """Test BusinessRulesMixin.validate_command_execution_state method."""
        # Test valid state
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            "ready", "ready", "execute"
        )
        assert result.is_success

        # Test invalid state
        result = FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
            "running", "ready", "execute"
        )
        assert result.is_failure
        assert "Cannot execute" in result.error
        assert "running" in result.error
        assert "ready" in result.error

    def test_business_rules_mixin_session_state(self) -> None:
        """Test BusinessRulesMixin.validate_session_state method."""
        valid_states = ["active", "inactive", "pending"]

        # Test valid session state
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            "active", valid_states
        )
        assert result.is_success

        # Test invalid session state
        result = FlextCliMixins.BusinessRulesMixin.validate_session_state(
            "invalid", valid_states
        )
        assert result.is_failure
        assert "Invalid session status" in result.error
        assert "invalid" in result.error

    def test_business_rules_mixin_pipeline_step(self) -> None:
        """Test BusinessRulesMixin.validate_pipeline_step method."""
        # Test valid pipeline step
        valid_step = {"name": "test_step", "type": "transform"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(valid_step)
        assert result.is_success

        # Test None pipeline step
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(None)
        assert result.is_failure
        assert "must be a non-empty dictionary" in result.error

        # Test empty pipeline step (falsy, so returns first error)
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step({})
        assert result.is_failure
        assert "must be a non-empty dictionary" in result.error

        # Test pipeline step with empty name
        invalid_step = {"name": "", "type": "transform"}
        result = FlextCliMixins.BusinessRulesMixin.validate_pipeline_step(invalid_step)
        assert result.is_failure
        assert "name cannot be empty" in result.error

    def test_business_rules_mixin_configuration_consistency(self) -> None:
        """Test BusinessRulesMixin.validate_configuration_consistency method."""
        config_data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        required_fields = ["field1", "field2"]

        # Test valid configuration
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_success

        # Test missing required fields
        required_fields = ["field1", "field2", "missing_field"]
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            config_data, required_fields
        )
        assert result.is_failure
        assert "Missing required configuration fields" in result.error
        assert "missing_field" in result.error

        # Test None configuration
        result = FlextCliMixins.BusinessRulesMixin.validate_configuration_consistency(
            None, required_fields
        )
        assert result.is_success  # None config is valid if no fields are required

    def test_mixins_nested_classes_access(self) -> None:
        """Test that nested mixin classes are accessible."""
        # Test ValidationMixin access
        assert hasattr(FlextCliMixins, "ValidationMixin")
        assert hasattr(FlextCliMixins.ValidationMixin, "validate_not_empty")
        assert hasattr(FlextCliMixins.ValidationMixin, "validate_url")
        assert hasattr(FlextCliMixins.ValidationMixin, "validate_enum_value")

        # Test BusinessRulesMixin access
        assert hasattr(FlextCliMixins, "BusinessRulesMixin")
        assert hasattr(
            FlextCliMixins.BusinessRulesMixin, "validate_command_execution_state"
        )
        assert hasattr(FlextCliMixins.BusinessRulesMixin, "validate_session_state")
        assert hasattr(FlextCliMixins.BusinessRulesMixin, "validate_pipeline_step")

    def test_mixins_inheritance(self) -> None:
        """Test that FlextCliMixins properly inherits from FlextMixins."""
        mixins = FlextCliMixins()
        assert isinstance(mixins, FlextCliMixins)
        # Should inherit from FlextMixins (base class)
        from flext_core import FlextMixins

        assert isinstance(mixins, FlextMixins)
