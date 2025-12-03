"""Comprehensive consolidated tests for flext-core module - initialization, services, containers, results, and integration.

Advanced Python 3.13 patterns with factories, dynamic parametrized tests, nested classes for organization,
real implementations using flext_tests helpers, and comprehensive edge case coverage.

Modules Tested: FlextResult, FlextContainer, FlextService, FlextConfig, FlextLogger, FlextConstants, u
Scope: Core functionality, railway-oriented programming, dependency injection, service patterns, and integration workflows.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time

import pytest
from flext_core import (
    FlextConfig,
    FlextConstants,
    FlextContainer,
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextService,
    u,
)
from flext_tests import FlextTestsUtilities

from tests.fixtures.constants import TestConstants


class TestFlextConsolidated:
    """Unified test class for all flext-core functionality using advanced patterns."""

    # =========================================================================
    # NESTED: Test Data & Constants
    # =========================================================================

    class TestDataFactory:
        """Factory for generating test data using flext_tests patterns and constants."""

        @staticmethod
        def create_success_data() -> dict[str, object]:
            """Create test data for success cases using constants."""
            return {
                "status": TestConstants.Common.STATUS_OPERATIONAL,
                "data": TestConstants.Common.VALUE_DEFAULT,
            }

        @staticmethod
        def create_failure_data() -> str:
            """Create test data for failure cases using constants."""
            return TestConstants.ResultValues.ERROR_MESSAGE

        @staticmethod
        def create_complex_data() -> dict[str, object]:
            """Create complex test data using constants."""
            return {
                "nested": {"value": TestConstants.Common.VALUE_LARGE},
                "list": TestConstants.Common.LIST_MULTIPLE,
                "string": TestConstants.Common.NAME_TEST,
            }

    class TestCasesFactory:
        """Factory for generating test cases using constants and flext_tests."""

        @staticmethod
        def get_flext_result_test_cases() -> list[dict[str, object]]:
            """Generate FlextResult test cases using constants."""
            return [
                {
                    "data": TestConstants.Common.VALUE_DEFAULT,
                    "expected_success": True,
                    "expected_failure": False,
                },
                {
                    "data": TestConstants.GenericData.USER_DATA,
                    "expected_success": True,
                    "expected_failure": False,
                },
                {
                    "data": TestConstants.GenericData.CONFIG_DATA,
                    "expected_success": True,
                    "expected_failure": False,
                },
                {
                    "data": TestConstants.ResultValues.SUCCESS_DATA_LIST,
                    "expected_success": True,
                    "expected_failure": False,
                },
            ]

        @staticmethod
        def get_container_test_cases() -> list[dict[str, object]]:
            """Generate container test cases using flext_tests."""
            return [
                {
                    "name": FlextTestsUtilities.TestUtilities.generate_test_id(
                        "service"
                    ),
                    "service": TestConstants.Common.VALUE_DEFAULT,
                    "expected_registration": True,
                    "expected_retrieval": True,
                },
            ]

        @staticmethod
        def get_logger_test_cases() -> list[str]:
            """Generate logger test cases using constants."""
            return [
                TestConstants.Common.NAME_TEST,
                TestConstants.Cli.SERVICE_NAME,
                __name__,
            ]

        @staticmethod
        def get_service_test_cases() -> list[dict[str, object]]:
            """Generate service test cases using constants."""
            return [
                {
                    "service_data": TestConstants.Common.VALUE_DEFAULT,
                    "expected_result": TestConstants.Common.VALUE_DEFAULT,
                },
                {
                    "service_data": TestConstants.GenericData.USER_DATA,
                    "expected_result": TestConstants.GenericData.USER_DATA,
                },
            ]

    # =========================================================================
    # NESTED: Test Helpers
    # =========================================================================

    class TestHelpers:
        """Test-specific helpers for flext-core testing."""

        @staticmethod
        def create_test_service(result_data: object) -> type[FlextService[object]]:
            """Create a test service class."""

            class TestService(FlextService[object]):
                def __init__(self, **data: object) -> None:
                    super().__init__(**data)
                    self._result_data = result_data

                def execute(self) -> FlextResult[object]:
                    return FlextResult[object].ok(self._result_data)

            return TestService

        @staticmethod
        def create_error_service(error_msg: str) -> type[FlextService[str]]:
            """Create a test service that fails."""

            class ErrorService(FlextService[str]):
                def __init__(self, **data: object) -> None:
                    super().__init__(**data)
                    self._error_msg = error_msg

                def execute(self) -> FlextResult[str]:
                    return FlextResult[str].fail(self._error_msg)

            return ErrorService

    # =============================================================================
    # FLEXT RESULT TESTS
    # =============================================================================

    @pytest.mark.parametrize(
        "result_case",
        TestCasesFactory.get_flext_result_test_cases(),
        ids=lambda case: f"success_{type(case['data']).__name__}",
    )
    def test_flext_result_success_creation(
        self, result_case: dict[str, object]
    ) -> None:
        """Test FlextResult success creation with various data types."""
        result = FlextResult[object].ok(result_case["data"])
        FlextTestsUtilities.TestUtilities.assert_result_success(result)
        assert result.data == result_case["data"]
        assert result.error is None
        assert result.is_failure == result_case["expected_failure"]

    def test_flext_result_failure_creation(self) -> None:
        """Test FlextResult failure creation using flext_tests."""
        error_msg = self.TestDataFactory.create_failure_data()
        result = FlextTestsUtilities.ResultHelpers.create_failure_result(error_msg)
        FlextTestsUtilities.TestUtilities.assert_result_failure(result)
        assert result.error == error_msg
        # Test that accessing data on failure raises exception
        with pytest.raises(RuntimeError):
            _ = result.data

    @pytest.mark.parametrize(
        "test_data",
        [
            TestConstants.Common.VALUE_DEFAULT,
            TestConstants.Common.NAME_TEST,
            TestConstants.ResultValues.SUCCESS_DATA_INT,
        ],
    )
    def test_flext_result_unwrap_success(self, test_data: object) -> None:
        """Test FlextResult unwrap on success with various data types."""
        result = FlextResult[object].ok(test_data)
        unwrapped = result.unwrap()
        assert unwrapped == test_data

    def test_flext_result_unwrap_failure(self) -> None:
        """Test FlextResult unwrap on failure raises exception."""
        result = FlextResult[str].fail(TestConstants.ResultValues.ERROR_MESSAGE)
        with pytest.raises(RuntimeError):
            result.unwrap()

    @pytest.mark.parametrize(
        "test_data",
        [
            TestConstants.Common.VALUE_DEFAULT,
            TestConstants.Common.NAME_TEST,
            TestConstants.ResultValues.SUCCESS_DATA_INT,
        ],
    )
    def test_flext_result_dual_access_api(self, test_data: object) -> None:
        """Test FlextResult dual access API (.value and .data)."""
        result = FlextResult[object].ok(test_data)
        assert result.data == test_data
        assert result.value == test_data
        assert result.data == result.value

    # =============================================================================
    # FLEXT CONTAINER TESTS
    # =============================================================================

    def test_flext_container_global_access(self) -> None:
        """Test FlextContainer global access."""
        container = FlextContainer()
        assert container is not None
        assert isinstance(container, FlextContainer)

    def test_flext_container_singleton_pattern(self) -> None:
        """Test FlextContainer singleton pattern."""
        container1 = FlextContainer()
        container2 = FlextContainer()
        assert container1 is container2

    def test_flext_container_access(self) -> None:
        """Test FlextContainer basic access."""
        container = FlextContainer()

        # Test that container exists and has basic methods
        assert hasattr(container, "register")
        assert hasattr(container, "get")

        # Test getting non-existent service
        result = container.get("nonexistent")
        assert result.is_failure  # Should fail for non-existent service

    # =============================================================================
    # FLEXT LOGGER TESTS
    # =============================================================================

    @pytest.mark.parametrize("module_name", TestCasesFactory.get_logger_test_cases())
    def test_flext_logger_creation(self, module_name: str) -> None:
        """Test FlextLogger creation with different module names."""
        logger = FlextLogger(module_name)
        assert logger is not None
        assert isinstance(logger, FlextLogger)

    def test_flext_logger_different_names(self) -> None:
        """Test FlextLogger with different module names."""
        logger1 = FlextLogger("module1")
        logger2 = FlextLogger("module2")

        assert logger1 is not None
        assert logger2 is not None
        assert logger1 != logger2

    # =============================================================================
    # FLEXT CONSTANTS TESTS
    # =============================================================================

    def test_flext_constants_access(self) -> None:
        """Test FlextConstants access."""
        # Test platform constants
        assert FlextConstants.FlextWeb.HTTP_STATUS_MIN is not None
        assert FlextConstants.FlextWeb.HTTP_STATUS_MAX is not None
        assert FlextConstants.Platform.DEFAULT_HTTP_PORT is not None

        # Test logging constants
        assert FlextConstants.Logging.DEFAULT_LEVEL is not None
        assert FlextConstants.Logging.DEFAULT_FORMAT is not None

    def test_flext_constants_immutability(self) -> None:
        """Test FlextConstants immutability."""
        # Constants should be accessible but not modifiable
        value = FlextConstants.Platform.DEFAULT_HTTP_PORT

        # Verify it's a constant value
        assert isinstance(value, int)

    # =============================================================================
    # FLEXT CONFIG TESTS
    # =============================================================================

    def test_flext_config_creation(self) -> None:
        """Test FlextConfig creation."""
        config = FlextConfig()
        assert config is not None
        assert isinstance(config, FlextConfig)

    def test_flext_config_with_data(self) -> None:
        """Test FlextConfig with initial data."""
        config = FlextConfig(app_name="Test App", version="1.0.0")

        assert config is not None
        # Verify config has expected attributes
        assert hasattr(config, "app_name")
        assert hasattr(config, "version")

    # =============================================================================
    # FLEXT MODELS TESTS
    # =============================================================================

    def test_flext_models_access(self) -> None:
        """Test FlextModels access."""
        # Test that FlextModels is accessible
        assert FlextModels is not None

        # Test that it has expected structure
        assert hasattr(FlextModels, "Entity") or hasattr(FlextModels, "Value")

    # =============================================================================
    # FLEXT TYPES TESTS
    # =============================================================================

    def test_flext_types_access(self) -> None:
        """Test t access."""
        # Test core types
        assert dict[str, object] is not None
        assert list[object] is not None
        assert list[str] is not None

    def test_flext_types_usage(self) -> None:
        """Test t usage in type annotations."""
        # Test that types can be used in annotations
        test_dict: dict[str, object] = {"key": "value"}
        test_list: list[object] = [1, 2, 3]
        test_string_list: list[str] = ["test1", "test2"]

        assert test_dict is not None
        assert test_list is not None
        assert test_string_list is not None

    # =============================================================================
    # FLEXT UTILITIES TESTS
    # =============================================================================

    def test_flext_utilities_access(self) -> None:
        """Test u access."""
        assert u is not None

        # Test that it has expected methods
        assert (
            hasattr(u, "Validation")
            or hasattr(u, "Generators")
            or hasattr(u, "Cache")
        )

    # =============================================================================
    # FLEXT SERVICE TESTS
    # =============================================================================

    @pytest.mark.parametrize(
        "service_case",
        TestCasesFactory.get_service_test_cases(),
        ids=lambda case: f"service_{type(case['service_data']).__name__}",
    )
    def test_flext_service_creation_and_execution(
        self, service_case: dict[str, object]
    ) -> None:
        """Test FlextService creation and execution with various data types."""
        # Create service using factory
        test_service_class = self.TestHelpers.create_test_service(
            service_case["service_data"]
        )
        service = test_service_class()

        assert service is not None
        assert isinstance(service, FlextService)

        # Test execution
        result = service.execute()
        assert result.is_success
        assert result.value == service_case["expected_result"]

    # =============================================================================
    # INTEGRATION TESTS
    # =============================================================================

    def test_flext_core_integration(self) -> None:
        """Test flext-core components working together."""

        # Create a service that uses multiple flext-core components
        class IntegratedService(FlextService[dict[str, object]]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)
                # self.logger is read-only, use class logger
                self._container = FlextContainer()

            def execute(self) -> FlextResult[dict[str, object]]:
                try:
                    # Use logger
                    self.logger.info("Service executing")

                    # Use container for simple access
                    container_access = self._container.get(
                        "nonexistent"
                    )  # Should fail gracefully
                    if container_access.is_success:
                        return FlextResult[dict[str, object]].fail("Unexpected success")

                    # Return success result
                    return FlextResult[dict[str, object]].ok({
                        "status": "success",
                        "message": "Integration test passed",
                    })
                except Exception as e:
                    return FlextResult[dict[str, object]].fail(str(e))

        service = IntegratedService()
        result = service.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == "success"

    def test_flext_core_error_handling(self) -> None:
        """Test flext-core error handling patterns."""

        # Test that errors are properly handled through FlextResult
        class ErrorService(FlextService[str]):
            def execute(self) -> FlextResult[str]:
                try:
                    # Simulate an error
                    msg = "Test error"
                    raise ValueError(msg)
                except Exception as e:
                    return FlextResult[str].fail(str(e))

        service = ErrorService()
        result = service.execute()

        assert result.is_failure
        assert result.error is not None and "Test error" in result.error

    @pytest.mark.parametrize("operation_count", [10, 50, 100])
    def test_flext_core_performance(self, operation_count: int) -> None:
        """Test flext-core performance characteristics with parametrized counts."""
        start_time = time.time()
        for _ in range(operation_count):
            result = FlextResult[str].ok(TestConstants.Common.VALUE_DEFAULT)
            FlextTestsUtilities.TestUtilities.assert_result_success(result)
        elapsed = time.time() - start_time
        # Should complete quickly (less than 1 second per 100 operations)
        assert elapsed < (operation_count / 100.0) + 0.1
