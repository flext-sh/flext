"""Tests for flext_cli.api.FlextCli class - initialization, execution, component validation, and edge cases.

Comprehensive testing of CLI coordinator with real implementations, advanced Python 3.13 patterns,
factories for test data generation, and 100% edge case coverage using dynamic parametrized tests.
Uses FlextTestsUtilities for assertions, domain helpers from tests.helpers, and constants from tests.fixtures.constants.

Scope: FlextCli initialization, execute() method, component validation, data structures, and error handling.
Tested modules: flext_cli.api.FlextCli, flext_cli.config.FlextCliConfig, flext_cli.core.FlextCliCore,
flext_cli.formatters.FlextCliFormatters, flext_cli.prompts.FlextCliPrompts.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TypedDict, cast

import pytest
from flext_cli import (
    FlextCli,
    FlextCliConfig,
    FlextCliCore,
    FlextCliFormatters,
    FlextCliPrompts,
)
from flext_core import FlextResult, t
from flext_tests import u

from tests.fixtures.constants import TestConstants

CliTestData = StrEnum(
    "CliTestData",
    {
        "OPERATIONAL": TestConstants.Cli.SERVICE_STATUS,
        "FLEXT_CLI": TestConstants.Cli.SERVICE_NAME,
        "AVAILABLE": TestConstants.Cli.COMPONENT_AVAILABLE,
        "STATUS": "status",
        "SERVICE": "service",
        "TIMESTAMP": "timestamp",
        "VERSION": "version",
        "COMPONENTS": "components",
    },
)


class ComponentTestCase(TypedDict):
    """TypedDict for component test cases."""

    component_name: str
    component_attr: str
    expected_type: type
    expected_available: bool


class ExecuteResultTestCase(TypedDict):
    """TypedDict for execute result test cases."""

    field: str
    expected_type: type
    expected_value: object


class TestFlextCli:
    """Comprehensive test suite for FlextCli class using advanced Python patterns."""

    # =========================================================================
    # NESTED: Test Cases Factory
    # =========================================================================

    class TestCasesFactory:
        """Factory for generating test cases using flext_tests patterns."""

        @staticmethod
        def get_component_test_cases() -> list[ComponentTestCase]:
            """Generate component validation test cases."""
            return [
                {
                    "component_name": "config",
                    "component_attr": "config",
                    "expected_type": FlextCliConfig,
                    "expected_available": True,
                },
                {
                    "component_name": "formatters",
                    "component_attr": "formatters",
                    "expected_type": FlextCliFormatters,
                    "expected_available": True,
                },
                {
                    "component_name": "core",
                    "component_attr": "core",
                    "expected_type": FlextCliCore,
                    "expected_available": True,
                },
                {
                    "component_name": "prompts",
                    "component_attr": "prompts",
                    "expected_type": FlextCliPrompts,
                    "expected_available": True,
                },
            ]

        @staticmethod
        def get_execute_result_test_cases() -> list[ExecuteResultTestCase]:
            """Generate execute result validation test cases."""
            return [
                {
                    "field": CliTestData.STATUS,
                    "expected_type": str,
                    "expected_value": CliTestData.OPERATIONAL,
                },
                {
                    "field": CliTestData.SERVICE,
                    "expected_type": str,
                    "expected_value": CliTestData.FLEXT_CLI,
                },
                {
                    "field": CliTestData.TIMESTAMP,
                    "expected_type": str,
                    "expected_value": None,  # Will be validated as string
                },
                {
                    "field": CliTestData.VERSION,
                    "expected_type": str,
                    "expected_value": None,  # Will be validated as string
                },
                {
                    "field": CliTestData.COMPONENTS,
                    "expected_type": dict,
                    "expected_value": None,  # Will be validated separately
                },
            ]

        @staticmethod
        def get_flext_result_property_test_cases() -> list[tuple[str, bool]]:
            """Generate FlextResult property validation test cases."""
            return [
                ("is_success", True),
                ("is_failure", False),
                ("unwrap", True),  # Has method
                ("error", False),  # Should be None
            ]

    # =========================================================================
    # NESTED: Test Helpers
    # =========================================================================

    class TestHelpers:
        """Test-specific helpers for CLI testing."""

        @staticmethod
        def create_cli_instance() -> FlextCli:
            """Create a FlextCli instance using factory pattern."""
            return FlextCli()

        @staticmethod
        def execute_and_validate(cli: FlextCli) -> FlextResult[t.JsonDict]:
            """Execute CLI and perform basic validation using FlextTestsUtilities."""
            result = cli.execute()
            u.Tests.Result.assert_success(result)
            return result

        @staticmethod
        def validate_component_status(components: dict[str, object]) -> None:
            """Validate component status dictionary."""
            assert len(components) == TestConstants.Cli.COMPONENT_COUNT

            components_dict = cast("dict[str, str]", components)
            for name, status in components_dict.items():
                assert isinstance(name, str), f"Component name {name} not string"
                assert isinstance(status, str), f"Component status {status} not string"
                assert status == TestConstants.Cli.COMPONENT_AVAILABLE, (
                    f"Component {name} not available"
                )

    # =========================================================================
    # TEST METHODS
    # =========================================================================

    @pytest.mark.parametrize(
        "component_case",
        TestCasesFactory.get_component_test_cases(),
        ids=lambda case: f"{case['component_name']}_component",
    )
    def test_cli_component_initialization(
        self, component_case: ComponentTestCase
    ) -> None:
        """Test CLI component initialization using parametrized cases."""
        cli = self.TestHelpers.create_cli_instance()

        # Get component attribute
        component = getattr(cli, component_case["component_attr"])
        assert component is not None, (
            f"Component {component_case['component_name']} not initialized"
        )

        # Validate type
        assert isinstance(component, component_case["expected_type"]), (
            f"Component {component_case['component_name']} type mismatch"
        )

        # Validate availability (if expected)
        if component_case["expected_available"]:
            assert hasattr(component, "__class__"), "Component lacks class attribute"

    def test_cli_initialization_comprehensive(self) -> None:
        """Test comprehensive CLI initialization."""
        cli = self.TestHelpers.create_cli_instance()

        # Validate all components exist
        assert cli.config is not None
        assert cli.formatters is not None
        assert cli.core is not None
        assert cli.prompts is not None

        # Validate component types
        assert isinstance(cli.config, FlextCliConfig)
        assert isinstance(cli.formatters, FlextCliFormatters)
        assert isinstance(cli.core, FlextCliCore)
        assert isinstance(cli.prompts, FlextCliPrompts)

    @pytest.mark.parametrize(
        "field_case",
        TestCasesFactory.get_execute_result_test_cases(),
        ids=lambda case: f"execute_{case['field']}_field",
    )
    def test_execute_result_structure(self, field_case: ExecuteResultTestCase) -> None:
        """Test execute result data structure using parametrized cases."""
        cli = self.TestHelpers.create_cli_instance()
        result = self.TestHelpers.execute_and_validate(cli)
        data = result.value

        # Validate field presence
        field_name = field_case["field"]
        assert field_name in data, f"Missing field: {field_name}"

        # Validate field type
        field_value = data[field_name]
        assert isinstance(field_value, field_case["expected_type"]), (
            f"Field {field_name} type mismatch: {type(field_value)} != {field_case['expected_type']}"
        )

        # Validate specific values where expected
        if field_case["expected_value"] is not None:
            assert field_value == field_case["expected_value"], (
                f"Field {field_name} value mismatch: {field_value} != {field_case['expected_value']}"
            )

        # Special validation for components
        if field_name == CliTestData.COMPONENTS:
            self.TestHelpers.validate_component_status(
                cast("dict[str, object]", field_value)
            )

    def test_execute_returns_flext_result(self) -> None:
        """Test that execute returns proper FlextResult."""
        cli = self.TestHelpers.create_cli_instance()
        result = cli.execute()

        # Validate FlextResult interface
        assert hasattr(result, "is_success")
        assert hasattr(result, "is_failure")
        assert hasattr(result, "unwrap")
        assert hasattr(result, "error")

        # Validate success state
        assert result.is_success
        assert not result.is_failure
        assert result.error is None

        # Validate data extraction
        data = result.value
        assert isinstance(data, dict)
        assert len(data) > 0

    @pytest.mark.parametrize(
        ("property_name", "expected"),
        TestCasesFactory.get_flext_result_property_test_cases(),
    )
    def test_flext_result_properties(self, property_name: str, expected: bool) -> None:
        """Test FlextResult properties using parametrized cases."""
        cli = self.TestHelpers.create_cli_instance()
        result = cli.execute()

        if property_name in {"is_success", "is_failure"}:
            # Boolean properties
            value = getattr(result, property_name)
            assert value == expected, (
                f"Property {property_name} = {value}, expected {expected}"
            )
        elif property_name == "unwrap":
            # Method presence
            assert hasattr(result, property_name), f"Missing method: {property_name}"
            # Can unwrap successfully
            data = result.value
            assert data is not None
        elif property_name == "error":
            # Error property
            error_value = getattr(result, property_name)
            if expected:
                assert error_value is None, f"Unexpected error: {error_value}"
            else:
                # For failure cases, would expect error, but this is success case
                assert error_value is None

    def test_execute_success_state(self) -> None:
        """Test execute method success state and data."""
        cli = self.TestHelpers.create_cli_instance()
        result = self.TestHelpers.execute_and_validate(cli)
        data = result.value

        # Validate core success indicators
        assert data[CliTestData.STATUS] == CliTestData.OPERATIONAL
        assert data[CliTestData.SERVICE] == CliTestData.FLEXT_CLI

        # Validate timestamp and version are present and valid
        timestamp = data[CliTestData.TIMESTAMP]
        version = data[CliTestData.VERSION]
        assert isinstance(timestamp, str) and len(timestamp) > 0
        assert isinstance(version, str) and len(version) > 0

    def test_execute_component_validation(self) -> None:
        """Test execute method component validation."""
        cli = self.TestHelpers.create_cli_instance()
        result = self.TestHelpers.execute_and_validate(cli)
        data = result.value

        components = data[CliTestData.COMPONENTS]
        self.TestHelpers.validate_component_status(
            cast("dict[str, object]", components)
        )

        # Validate all expected components are present

        components_dict = cast("dict[str, str]", components)
        expected_components = {"config", "formatters", "core", "prompts"}
        actual_components = set(components_dict.keys())
        assert actual_components == expected_components, (
            f"Component mismatch: {actual_components} != {expected_components}"
        )

    def test_execute_data_integrity(self) -> None:
        """Test execute method data integrity and completeness."""
        cli = self.TestHelpers.create_cli_instance()
        result = self.TestHelpers.execute_and_validate(cli)
        data = result.value

        # Required fields presence
        required_fields = {
            CliTestData.STATUS,
            CliTestData.SERVICE,
            CliTestData.TIMESTAMP,
            CliTestData.VERSION,
            CliTestData.COMPONENTS,
        }
        actual_fields = set(data.keys())
        missing_fields = {str(field) for field in required_fields} - actual_fields
        assert not missing_fields, f"Missing required fields: {missing_fields}"

        # Data type validation
        type_validations = {
            CliTestData.STATUS: str,
            CliTestData.SERVICE: str,
            CliTestData.TIMESTAMP: str,
            CliTestData.VERSION: str,
            CliTestData.COMPONENTS: dict,
        }

        for field, expected_type in type_validations.items():
            value = data[field]
            assert isinstance(value, expected_type), (
                f"Field {field} type error: {type(value)} != {expected_type}"
            )

    @pytest.mark.parametrize("execution_count", range(3))
    def test_execute_idempotent(self, execution_count: int) -> None:
        """Test execute method idempotency across multiple calls."""
        cli = self.TestHelpers.create_cli_instance()

        # Execute multiple times
        results = []
        for _ in range(execution_count + 1):  # At least once
            result = cli.execute()
            results.append(result)
            assert result.is_success

        # All results should be consistent
        first_data = results[0].value
        for result in results[1:]:
            data = result.value
            assert data == first_data, "Execute results not consistent"

    def test_cli_instance_isolation(self) -> None:
        """Test that CLI instances are properly isolated."""
        cli1 = self.TestHelpers.create_cli_instance()
        cli2 = self.TestHelpers.create_cli_instance()

        # Different instances
        assert cli1 is not cli2

        # Execute both
        result1 = self.TestHelpers.execute_and_validate(cli1)
        result2 = self.TestHelpers.execute_and_validate(cli2)

        # Results should be equivalent but independent
        data1 = result1.value
        data2 = result2.value

        # Core fields should match
        assert data1["status"] == data2["status"]
        assert data1["service"] == data2["service"]
        # Timestamps might differ slightly, versions should match
        assert data1["version"] == data2["version"]
