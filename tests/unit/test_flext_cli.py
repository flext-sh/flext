"""Unit tests for flext_cli.api.FlextCli class - initialization, components, execution, and domain libraries.

Advanced Python 3.13 patterns with factories, dynamic parametrized tests, nested classes for organization,
real implementations using flext_tests helpers, and comprehensive edge case coverage for CLI coordinator.

Modules Tested: FlextCli (flext_cli.api), domain libraries (formatters, file_tools, output, core, cmd, prompts, config)
Scope: CLI initialization, component validation, execution flow, domain library integration, and error handling.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import inspect
from enum import StrEnum
from typing import TypedDict

import pytest
from flext_cli import (
    FlextCli,
    FlextCliConfig,
    FlextCliCore,
    FlextCliFormatters,
    FlextCliPrompts,
)
from flext_core import FlextResult


class TestData(StrEnum):
    """Test data enumeration for type safety."""

    CONFIG_PATH = "/tmp/test_config.json"
    TEST_COMMAND = "test_command"
    ARG1 = "arg1"
    ARG2 = "arg2"
    JSON_FORMAT = "json"
    OPERATIONAL = "operational"
    FLEXT_CLI = "flext-cli"


class ComponentTestCase(TypedDict):
    """TypedDict for component validation test cases."""

    component_name: str
    component_attr: str
    expected_type: type


class MethodTestCase(TypedDict):
    """TypedDict for method validation test cases."""

    method_name: str
    should_be_callable: bool


class TestFlextCli:
    """Unified test class for FlextCli functionality using advanced patterns."""

    # =========================================================================
    # NESTED: Test Data & Constants
    # =========================================================================

    class TestDataFactory:
        """Factory for generating test data using flext_tests patterns."""

        @staticmethod
        def create_test_cli_data() -> dict[str, object]:
            """Create test CLI data."""
            return {
                "config_path": TestData.CONFIG_PATH,
                "verbose": True,
                "output_format": TestData.JSON_FORMAT,
            }

        @staticmethod
        def create_test_command_data() -> dict[str, object]:
            """Create test command data."""
            return {
                "command": TestData.TEST_COMMAND,
                "args": [TestData.ARG1, TestData.ARG2],
                "options": {"verbose": True, "output": TestData.JSON_FORMAT},
            }

    class TestCasesFactory:
        """Factory for generating test cases."""

        @staticmethod
        def get_component_test_cases() -> list[ComponentTestCase]:
            """Generate component validation test cases."""
            return [
                {
                    "component_name": "config",
                    "component_attr": "config",
                    "expected_type": FlextCliConfig,
                },
                {
                    "component_name": "formatters",
                    "component_attr": "formatters",
                    "expected_type": FlextCliFormatters,
                },
                {
                    "component_name": "core",
                    "component_attr": "core",
                    "expected_type": FlextCliCore,
                },
                {
                    "component_name": "prompts",
                    "component_attr": "prompts",
                    "expected_type": FlextCliPrompts,
                },
                {
                    "component_name": "file_tools",
                    "component_attr": "file_tools",
                    "expected_type": object,  # Will be validated as not None
                },
                {
                    "component_name": "output",
                    "component_attr": "output",
                    "expected_type": object,  # Will be validated as not None
                },
                {
                    "component_name": "cmd",
                    "component_attr": "cmd",
                    "expected_type": object,  # Will be validated as not None
                },
            ]

        @staticmethod
        def get_method_test_cases() -> list[MethodTestCase]:
            """Generate method validation test cases."""
            return [
                {"method_name": "execute", "should_be_callable": True},
                {"method_name": "authenticate", "should_be_callable": True},
                {"method_name": "__init__", "should_be_callable": True},
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
        def validate_component_exists(cli: FlextCli, component_name: str) -> bool:
            """Validate that a component exists on the CLI instance."""
            return (
                hasattr(cli, component_name)
                and getattr(cli, component_name) is not None
            )

        @staticmethod
        def validate_method_exists(
            cli: FlextCli, method_name: str, should_be_callable: bool
        ) -> bool:
            """Validate that a method exists and is callable if expected."""
            has_method = hasattr(cli, method_name)
            if not has_method:
                return False
            method = getattr(cli, method_name)
            return callable(method) == should_be_callable

    # =============================================================================
    # INITIALIZATION TESTS
    # =============================================================================

    def test_cli_initialization_basic(self) -> None:
        """Test basic FlextCli initialization."""
        cli = self.TestHelpers.create_cli_instance()
        assert cli is not None
        assert isinstance(cli, FlextCli)

    def test_cli_initialization_with_validation(self) -> None:
        """Test FlextCli initialization with comprehensive validation."""
        cli = self.TestHelpers.create_cli_instance()

        # Validate core attributes
        assert hasattr(cli, "_container")
        assert hasattr(cli, "logger")
        assert cli._container is not None
        assert cli.logger is not None

    @pytest.mark.parametrize("init_count", range(1, 4))
    def test_cli_multiple_initializations(self, init_count: int) -> None:
        """Test multiple CLI initializations for consistency."""
        clis = [self.TestHelpers.create_cli_instance() for _ in range(init_count)]

        # All instances should be valid
        for cli in clis:
            assert isinstance(cli, FlextCli)
            assert cli is not None

    # =============================================================================
    # SERVICE EXECUTION TESTS
    # =============================================================================

    @pytest.mark.parametrize(
        "method_case",
        TestCasesFactory.get_method_test_cases(),
        ids=lambda case: f"method_{case['method_name']}",
    )
    def test_cli_methods_exist_and_callable(self, method_case: MethodTestCase) -> None:
        """Test that CLI has expected methods and they are callable when expected."""
        cli = self.TestHelpers.create_cli_instance()
        assert self.TestHelpers.validate_method_exists(
            cli, method_case["method_name"], method_case["should_be_callable"]
        )

    def test_cli_execute_method_functionality(self) -> None:
        """Test FlextCli execute method functionality."""
        cli = self.TestHelpers.create_cli_instance()
        result = cli.execute()

        # Validate result is FlextResult
        assert isinstance(result, FlextResult)
        assert result.is_success

        # Validate result data structure
        data = result.value
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data
        assert data["status"] == TestData.OPERATIONAL
        assert data["service"] == TestData.FLEXT_CLI

    def test_cli_execute_idempotent(self) -> None:
        """Test that execute method is idempotent."""
        cli = self.TestHelpers.create_cli_instance()

        # Execute multiple times
        results = [cli.execute() for _ in range(3)]

        # All results should be successful and consistent
        for result in results:
            assert result.is_success
            data = result.value
            assert data["status"] == TestData.OPERATIONAL
            assert data["service"] == TestData.FLEXT_CLI

    # =============================================================================
    # DOMAIN LIBRARY COMPONENTS TESTS
    # =============================================================================

    @pytest.mark.parametrize(
        "component_case",
        TestCasesFactory.get_component_test_cases(),
        ids=lambda case: f"component_{case['component_name']}",
    )
    def test_cli_domain_components(self, component_case: ComponentTestCase) -> None:
        """Test FlextCli domain library components using parametrized cases."""
        cli = self.TestHelpers.create_cli_instance()

        # Validate component exists
        assert self.TestHelpers.validate_component_exists(
            cli, component_case["component_attr"]
        )

        # Validate component type if expected type is specific
        if component_case["expected_type"] is not object:
            component = getattr(cli, component_case["component_attr"])
            assert isinstance(component, component_case["expected_type"])

    def test_cli_all_domain_components_initialized(self) -> None:
        """Test that all domain library components are properly initialized."""
        cli = self.TestHelpers.create_cli_instance()

        # Core domain components that should always exist
        core_components = [
            "formatters",
            "file_tools",
            "output",
            "core",
            "cmd",
            "prompts",
            "config",
            "logger",
        ]

        for component_name in core_components:
            assert self.TestHelpers.validate_component_exists(cli, component_name), (
                f"Component {component_name} not properly initialized"
            )

    def test_cli_component_types_correct(self) -> None:
        """Test that CLI components have correct types."""
        cli = self.TestHelpers.create_cli_instance()

        # Validate specific component types
        assert isinstance(cli.config, FlextCliConfig)
        assert isinstance(cli.core, FlextCliCore)
        assert isinstance(cli.formatters, FlextCliFormatters)
        assert isinstance(cli.prompts, FlextCliPrompts)

        # Other components should at least be objects
        assert isinstance(cli.file_tools, object)
        assert isinstance(cli.output, object)
        assert isinstance(cli.cmd, object)

    # =============================================================================
    # FUNCTIONALITY TESTS
    # =============================================================================

    def test_cli_execute_method_exists_and_callable(self) -> None:
        """Test that execute method exists and is callable."""
        cli = self.TestHelpers.create_cli_instance()
        assert hasattr(cli, "execute")
        assert callable(cli.execute)

    def test_cli_authenticate_method_exists(self) -> None:
        """Test that authenticate method exists."""
        cli = self.TestHelpers.create_cli_instance()
        assert hasattr(cli, "authenticate")
        assert callable(cli.authenticate)

    def test_cli_domain_library_methods(self) -> None:
        """Test that CLI provides access to domain library methods."""
        cli = self.TestHelpers.create_cli_instance()

        # Test key domain library methods are accessible
        methods_to_check = ["print", "create_table"]
        for method_name in methods_to_check:
            if hasattr(cli, method_name):
                method = getattr(cli, method_name)
                assert callable(method), f"Method {method_name} should be callable"

    # =============================================================================
    # INTEGRATION TESTS
    # =============================================================================

    def test_cli_integration_with_execute(self) -> None:
        """Test FlextCli integration with execute method."""
        cli = self.TestHelpers.create_cli_instance()
        result = cli.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Validate integration with data structure
        data = result.value
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_cli_component_integration(self) -> None:
        """Test CLI component integration and cross-component functionality."""
        cli = self.TestHelpers.create_cli_instance()

        # Test that all components work together
        assert cli.config is not None
        assert cli.core is not None
        assert cli.formatters is not None
        assert cli.prompts is not None

        # Test container integration
        assert cli._container is not None

    def test_cli_domain_separation(self) -> None:
        """Test that CLI properly uses domain separation patterns."""
        cli = self.TestHelpers.create_cli_instance()

        # Test that CLI doesn't directly import HTTP libraries
        source = inspect.getsource(cli.__class__)

        # Should not contain direct HTTP library imports (domain separation)
        assert "import requests" not in source.lower()
        assert "import httpx" not in source.lower()
        assert "from requests" not in source.lower()
        assert "from httpx" not in source.lower()

    def test_cli_complete_integration_workflow(self) -> None:
        """Test complete CLI integration workflow."""
        cli = self.TestHelpers.create_cli_instance()

        # Execute and validate full workflow
        result = cli.execute()
        assert result.is_success

        data = result.value
        assert isinstance(data, dict)

        # Validate all components are working
        assert cli.formatters is not None
        assert cli.file_tools is not None
        assert cli.output is not None
        assert cli.core is not None
        assert cli.prompts is not None
        assert cli.config is not None
        assert cli.logger is not None
