"""Generic helpers for CLI testing.

Provides reusable helper methods that reduce test code significantly for FlextCli components.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

from flext_cli import (
    FlextCli,
    FlextCliConfig,
    FlextCliCore,
    FlextCliFormatters,
    FlextCliPrompts,
)
from flext_core import FlextResult, FlextTypes
from flext_tests import FlextTestsUtilities

from tests.fixtures.constants import TestConstants


class CliTestHelpers:
    """Generic helpers for testing FlextCli components.

    Reduces test code by providing reusable methods for common CLI testing patterns.
    """

    @staticmethod
    def create_cli_instance() -> FlextCli:
        """Create a FlextCli instance using factory pattern."""
        return FlextCli()

    @staticmethod
    def execute_and_validate(cli: FlextCli) -> FlextResult[FlextTypes.JsonDict]:
        """Execute CLI and perform basic validation using FlextTestsUtilities.

        Reduces 2-3 lines per test by centralizing success assertion.
        """
        result = cli.execute()
        FlextTestsUtilities.TestUtilities.assert_result_success(result)
        return result

    @staticmethod
    def validate_component_status(components: dict[str, object]) -> None:
        """Validate component status dictionary.

        Reduces 4-5 lines per test by centralizing component validation logic.
        """
        FlextTestsUtilities.TestUtilities.assert_result_success(
            FlextResult.ok(components)
            if isinstance(components, dict)
            else FlextResult.fail("Not a dict")
        )
        assert (
            len(components) == TestConstants.Cli.COMPONENT_COUNT
        )  # config, formatters, core, prompts

        components_dict = cast("dict[str, str]", components)
        for name, status in components_dict.items():
            assert isinstance(name, str), f"Component name {name} not string"
            assert isinstance(status, str), f"Component status {status} not string"
            assert status == TestConstants.Cli.COMPONENT_AVAILABLE, (
                f"Component {name} not available"
            )

    @staticmethod
    def validate_execute_result_structure(
        result: FlextResult[FlextTypes.JsonDict],
        expected_fields: list[str],
    ) -> FlextTypes.JsonDict:
        """Validate execute result has required fields and return data.

        Reduces 5-6 lines per test by centralizing result structure validation.
        """
        FlextTestsUtilities.TestUtilities.assert_result_success(result)
        data = result.unwrap()

        for field in expected_fields:
            assert field in data, f"Missing required field: {field}"

        return data

    @classmethod
    def test_component_initialization_pattern(
        cls,
        component_name: str,
        component_attr: str,
        expected_type: type,
        cli: FlextCli | None = None,
    ) -> dict[str, object]:
        """Test component initialization pattern.

        Reduces 4-5 lines per component test by generalizing the pattern.
        """
        cli = cli or cls.create_cli_instance()

        component = getattr(cli, component_attr)
        assert component is not None, f"Component {component_name} not initialized"
        assert isinstance(component, expected_type), (
            f"Component {component_name} type mismatch: {type(component)} != {expected_type}"
        )

        return {
            "cli": cli,
            "component": component,
            "component_name": component_name,
            "component_attr": component_attr,
        }

    @classmethod
    def get_component_test_cases(cls) -> list[dict[str, object]]:
        """Generate component validation test cases.

        Centralizes test case generation, reducing duplication.
        Uses real component types for type safety.
        """
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

    @classmethod
    def get_execute_result_test_cases(cls) -> list[dict[str, object]]:
        """Generate execute result validation test cases.

        Centralizes test case generation for result structure validation.
        """
        return [
            {
                "field": TestConstants.Cli.STATUS,
                "expected_type": str,
                "expected_value": TestConstants.Cli.SERVICE_STATUS,
            },
            {
                "field": TestConstants.Cli.SERVICE,
                "expected_type": str,
                "expected_value": TestConstants.Cli.SERVICE_NAME,
            },
            {
                "field": TestConstants.Cli.TIMESTAMP,
                "expected_type": str,
                "expected_value": None,  # Will be validated as string
            },
            {
                "field": TestConstants.Cli.VERSION,
                "expected_type": str,
                "expected_value": None,  # Will be validated as string
            },
            {
                "field": TestConstants.Cli.COMPONENTS,
                "expected_type": dict,
                "expected_value": None,  # Will be validated separately
            },
        ]

    @classmethod
    def parametrize_component_tests(cls) -> list[tuple[str, str, type, bool]]:
        """Parametrize component initialization tests."""
        cases = cls.get_component_test_cases()
        return [
            (
                case["component_name"],
                case["component_attr"],
                case["expected_type"],
                case["expected_available"],
            )
            for case in cases
        ]

    @classmethod
    def parametrize_execute_result_tests(cls) -> list[tuple[str, type, object]]:
        """Parametrize execute result structure tests."""
        cases = cls.get_execute_result_test_cases()
        return [
            (case["field"], case["expected_type"], case["expected_value"])
            for case in cases
        ]
