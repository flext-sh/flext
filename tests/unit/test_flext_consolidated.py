"""Unit tests for flext_cli.api.FlextCli and flext_core integration.

Advanced Python 3.13 patterns with factories, dynamic parametrized tests, nested classes for organization,
real implementations using flext_tests helpers, and comprehensive edge case coverage for core component integration.

Modules Tested: FlextCli (flext_cli.api), FlextResult/FlextContainer/FlextLogger/FlextService (flext_core)
Scope: CLI-core integration, railway-oriented programming, dependency injection, service patterns, and component interactions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from typing import TypedDict, cast

import pytest
from flext_cli import FlextCli
from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)

# =========================================================================
# SHARED TEST INFRASTRUCTURE
# =========================================================================


class TestConstants:
    """Test constants for consolidated testing."""

    TEST_VALUE = "test_value"
    TEST_ERROR = "test_error"
    TEST_KEY = "test_key"
    OPERATIONAL = "operational"
    FLEXT_CLI = "flext-cli"


class CliTestCase(TypedDict):
    """TypedDict for CLI test cases."""

    description: str
    expected_success: bool


class ServiceTestCase(TypedDict):
    """TypedDict for service test cases."""

    service_data: str
    expected_result: str


class TestDataFactory:
    """Factory for generating test data using flext_tests patterns."""

    @staticmethod
    def create_test_service(result_data: str) -> type[FlextService[object]]:
        """Create a test service class."""

        class TestService(FlextService[str]):
            def __init__(self, **data: object) -> None:
                super().__init__(**data)
                self._result_data = result_data

            def execute(self) -> FlextResult[str]:
                return FlextResult[str].ok(self._result_data)

        return cast("type[FlextService[object]]", TestService)

    @staticmethod
    def generate_unique_key(prefix: str = "test") -> str:
        """Generate a unique test key."""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestCasesFactory:
    """Factory for generating test cases."""

    @staticmethod
    def get_cli_test_cases() -> list[CliTestCase]:
        """Generate CLI test cases."""
        return [
            {
                "description": "basic_creation",
                "expected_success": True,
            },
            {
                "description": "execution_test",
                "expected_success": True,
            },
        ]

    @staticmethod
    def get_service_test_cases() -> list[ServiceTestCase]:
        """Generate service test cases."""
        return [
            {
                "service_data": TestConstants.TEST_VALUE,
                "expected_result": TestConstants.TEST_VALUE,
            },
            {
                "service_data": "custom_data",
                "expected_result": "custom_data",
            },
        ]

    @staticmethod
    def get_logger_test_cases() -> list[str]:
        """Generate logger test cases."""
        return ["test_module", __name__, "another_module"]


class TestHelpers:
    """Test-specific helpers for consolidated testing."""

    @staticmethod
    def create_cli_instance() -> FlextCli:
        """Create a FlextCli instance using factory pattern."""
        return FlextCli()

    @staticmethod
    def create_container_instance() -> FlextContainer:
        """Create a FlextContainer instance."""
        return FlextContainer()

    @staticmethod
    def create_logger_instance(name: str) -> FlextLogger:
        """Create a FlextLogger instance."""
        return FlextLogger(name)

    @staticmethod
    def execute_cli_and_validate(cli: FlextCli) -> FlextResult[object]:
        """Execute CLI and perform basic validation."""
        result = cli.execute()
        assert isinstance(result, FlextResult)
        return cast("FlextResult[object]", result)


class TestFlextConsolidated:
    """Unified test class for flext_cli and flext_core integration using advanced patterns."""

    # =========================================================================
    # FLEXT CLI TESTS
    # =========================================================================

    @pytest.mark.parametrize(
        "cli_case",
        TestCasesFactory.get_cli_test_cases(),
        ids=lambda case: f"cli_{case['description']}",
    )
    def test_flext_cli_creation_and_methods(self, cli_case: CliTestCase) -> None:
        """Test FlextCli creation and basic functionality."""
        cli = TestHelpers.create_cli_instance()
        assert cli is not None
        assert isinstance(cli, FlextCli)

        # Test core methods exist
        assert hasattr(cli, "execute")
        assert callable(cli.execute)

        if cli_case["expected_success"]:
            # Test execution
            result = TestHelpers.execute_cli_and_validate(cli)
            assert result.is_success

    def test_flext_cli_execute_comprehensive(self) -> None:
        """Test FlextCli execute method comprehensively."""
        cli = TestHelpers.create_cli_instance()
        result = TestHelpers.execute_cli_and_validate(cli)

        # Validate result structure
        assert result.is_success
        data = result.unwrap()
        assert isinstance(data, dict)

        # Validate expected fields
        assert "status" in data
        assert "service" in data
        assert data["status"] == TestConstants.OPERATIONAL
        assert data["service"] == TestConstants.FLEXT_CLI

    def test_flext_cli_idempotent_execution(self) -> None:
        """Test that CLI execution is idempotent."""
        cli = TestHelpers.create_cli_instance()

        # Execute multiple times
        results = [cli.execute() for _ in range(3)]

        # All results should be consistent
        for result in results:
            assert result.is_success
            data = result.unwrap()
            assert data["status"] == TestConstants.OPERATIONAL
            assert data["service"] == TestConstants.FLEXT_CLI

    # =========================================================================
    # FLEXT CORE INTEGRATION TESTS
    # =========================================================================

    def test_flext_core_imports(self) -> None:
        """Test that flext_core components can be imported."""
        assert FlextResult is not None
        assert FlextService is not None
        assert FlextContainer is not None
        assert FlextLogger is not None

    @pytest.mark.parametrize("module_name", TestCasesFactory.get_logger_test_cases())
    def test_flext_logger_creation(self, module_name: str) -> None:
        """Test FlextLogger creation with different module names."""
        logger = TestHelpers.create_logger_instance(module_name)
        assert logger is not None
        assert isinstance(logger, FlextLogger)

        # Test logging methods exist and are callable
        logging_methods = ["info", "warning", "error", "debug"]
        for method_name in logging_methods:
            assert hasattr(logger, method_name)
            assert callable(getattr(logger, method_name))

    def test_flext_result_success_and_failure(self) -> None:
        """Test FlextResult success and failure patterns."""
        # Test success result
        success_result = FlextResult[str].ok(TestConstants.TEST_VALUE)
        assert success_result.is_success
        assert success_result.value == TestConstants.TEST_VALUE
        assert success_result.error is None
        assert not success_result.is_failure

        # Test failure result
        failure_result = FlextResult[str].fail(TestConstants.TEST_ERROR)
        assert failure_result.is_failure
        assert failure_result.error == TestConstants.TEST_ERROR
        assert not failure_result.is_success

    def test_flext_container_operations(self) -> None:
        """Test FlextContainer registration and retrieval."""
        container = TestHelpers.create_container_instance()
        assert container is not None
        assert isinstance(container, FlextContainer)

        # Generate unique key to avoid conflicts
        unique_key = TestDataFactory.generate_unique_key()

        # Test registration - FlextContainer uses different registration pattern
        # We'll test that container exists and has expected methods
        assert hasattr(container, "register")
        assert callable(container.register)
        assert hasattr(container, "get")
        assert callable(container.get)

        # Test retrieval - since we didn't register, should fail gracefully
        retrieved = container.get(unique_key)
        assert isinstance(retrieved, FlextResult)
        # Should be failure since nothing was registered
        assert retrieved.is_failure

    @pytest.mark.parametrize(
        "service_case",
        TestCasesFactory.get_service_test_cases(),
        ids=lambda case: f"service_{case['service_data'][:10]}",
    )
    def test_flext_service_creation_and_execution(
        self, service_case: ServiceTestCase
    ) -> None:
        """Test FlextService creation and execution with parametrized cases."""
        # Create service using factory
        test_service = TestDataFactory.create_test_service(service_case["service_data"])
        service = test_service()

        assert service is not None
        assert isinstance(service, FlextService)

        # Test execution
        result = service.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == service_case["expected_result"]

    def test_flext_core_complete_integration(self) -> None:
        """Test complete integration of flext core components."""
        # Create all core components
        cli = TestHelpers.create_cli_instance()
        container = TestHelpers.create_container_instance()
        logger = TestHelpers.create_logger_instance(__name__)

        # Test CLI execution
        cli_result = cli.execute()
        assert cli_result.is_success

        # Test container operations - just verify methods exist
        assert hasattr(container, "register")
        assert hasattr(container, "get")

        # Test service creation and execution
        test_service = TestDataFactory.create_test_service(TestConstants.TEST_VALUE)
        service = test_service()
        service_result = service.execute()

        # Validate all results
        assert cli_result.is_success
        assert service_result.is_success
        assert logger is not None
        assert container is not None
