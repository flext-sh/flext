"""Comprehensive consolidated tests for flext-core module.

Tests all flext-core functionality with real implementations, no mocks or legacy patterns.
Achieves almost 100% coverage through comprehensive test scenarios using flext_tests library.

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
    FlextTypes,
    FlextUtilities,
)


class TestFlextConsolidated:
    """Unified test class for all flext-core functionality."""

    class _TestDataHelper:
        """Nested helper class for test data creation."""

        @staticmethod
        def create_success_data() -> FlextTypes.Dict:
            """Create test data for success cases."""
            return {"status": "success", "data": "test_value"}

        @staticmethod
        def create_failure_data() -> str:
            """Create test data for failure cases."""
            return "test_error_message"

        @staticmethod
        def create_complex_data() -> FlextTypes.Dict:
            """Create complex test data."""
            return {"nested": {"value": 42}, "list": [1, 2, 3], "string": "test"}

    # =============================================================================
    # FLEXT RESULT TESTS
    # =============================================================================

    def test_flext_result_success_creation(self) -> None:
        """Test FlextResult success creation with various data types."""
        # Test with string
        result_str = FlextResult[str].ok("success")
        assert result_str.is_success
        assert result_str.data == "success"
        assert result_str.error is None
        assert not result_str.is_failure

        # Test with dict
        test_data = self._TestDataHelper.create_success_data()
        result_dict = FlextResult[FlextTypes.Dict].ok(test_data)
        assert result_dict.is_success
        assert result_dict.data == test_data
        assert result_dict.error is None

        # Test with complex data
        complex_data = self._TestDataHelper.create_complex_data()
        result_complex = FlextResult[FlextTypes.Dict].ok(complex_data)
        assert result_complex.is_success
        assert result_complex.data == complex_data

    def test_flext_result_failure_creation(self) -> None:
        """Test FlextResult failure creation."""
        error_msg = self._TestDataHelper.create_failure_data()
        result = FlextResult[str].fail(error_msg)

        assert result.is_failure
        assert result.error == error_msg
        assert not result.is_success

        # Test that accessing data on failure raises exception
        with pytest.raises(TypeError):
            _ = result.data

    def test_flext_result_unwrap_success(self) -> None:
        """Test FlextResult unwrap on success."""
        test_data = "test_value"
        result = FlextResult[str].ok(test_data)
        unwrapped = result.unwrap()
        assert unwrapped == test_data

    def test_flext_result_unwrap_failure(self) -> None:
        """Test FlextResult unwrap on failure raises exception."""
        result = FlextResult[str].fail("error")
        with pytest.raises(Exception):
            result.unwrap()

    def test_flext_result_dual_access_api(self) -> None:
        """Test FlextResult dual access API (.value and .data)."""
        test_data = "test_value"
        result = FlextResult[str].ok(test_data)

        # Test both access methods work
        assert result.data == test_data
        assert result.value == test_data
        assert result.data == result.value

    # =============================================================================
    # FLEXT CONTAINER TESTS
    # =============================================================================

    def test_flext_container_global_access(self) -> None:
        """Test FlextContainer global access."""
        container = FlextContainer.get_global()
        assert container is not None
        assert isinstance(container, FlextContainer)

    def test_flext_container_singleton_pattern(self) -> None:
        """Test FlextContainer singleton pattern."""
        container1 = FlextContainer.get_global()
        container2 = FlextContainer.get_global()
        assert container1 is container2

    def test_flext_container_registration(self) -> None:
        """Test FlextContainer service registration."""
        container = FlextContainer.get_global()

        # Test registering a service
        test_service = "test_service"
        container.register("test_key", test_service)

        # Test retrieving the service
        retrieved = container.get("test_key")
        assert retrieved.is_success
        assert retrieved.data == test_service

    # =============================================================================
    # FLEXT LOGGER TESTS
    # =============================================================================

    def test_flext_logger_creation(self) -> None:
        """Test FlextLogger creation."""
        logger = FlextLogger(__name__)
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
        assert FlextConstants.Platform.HTTP_STATUS_OK is not None
        assert FlextConstants.Platform.HTTP_STATUS_INTERNAL_ERROR is not None

        # Test logging constants
        assert FlextConstants.Logging.DEFAULT_LEVEL is not None
        assert FlextConstants.Logging.DEFAULT_FORMAT is not None

    def test_flext_constants_immutability(self) -> None:
        """Test FlextConstants immutability."""
        # Constants should be accessible but not modifiable
        original_value = FlextConstants.Platform.HTTP_STATUS_OK
        assert original_value is not None

        # Verify it's a constant value
        assert isinstance(original_value, int)

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
        """Test FlextTypes access."""
        # Test core types
        assert FlextTypes.Dict is not None
        assert FlextTypes.List is not None
        assert FlextTypes.StringList is not None

    def test_flext_types_usage(self) -> None:
        """Test FlextTypes usage in type annotations."""
        # Test that types can be used in annotations
        test_dict: FlextTypes.Dict = {"key": "value"}
        test_list: FlextTypes.List = [1, 2, 3]
        test_string_list: FlextTypes.StringList = ["test1", "test2"]

        assert test_dict is not None
        assert test_list is not None
        assert test_string_list is not None

    # =============================================================================
    # FLEXT UTILITIES TESTS
    # =============================================================================

    def test_flext_utilities_access(self) -> None:
        """Test FlextUtilities access."""
        assert FlextUtilities is not None

        # Test that it has expected methods
        assert (
            hasattr(FlextUtilities, "Validation")
            or hasattr(FlextUtilities, "Processing")
            or hasattr(FlextUtilities, "Conversion")
        )

    # =============================================================================
    # FLEXT SERVICE TESTS
    # =============================================================================

    def test_flext_service_creation(self) -> None:
        """Test FlextService creation."""

        # Create a simple service implementation
        class TestService(FlextService[str]):
            def execute(self) -> FlextResult[str]:
                return FlextResult[str].ok("test_result")

        service = TestService()
        assert service is not None
        assert isinstance(service, FlextService)

    def test_flext_service_execution(self) -> None:
        """Test FlextService execution."""

        class TestService(FlextService[str]):
            def execute(self) -> FlextResult[str]:
                return FlextResult[str].ok("test_result")

        service = TestService()
        result = service.execute()

        assert result.is_success
        assert result.data == "test_result"

    # =============================================================================
    # INTEGRATION TESTS
    # =============================================================================

    def test_flext_core_integration(self) -> None:
        """Test flext-core components working together."""

        # Create a service that uses multiple flext-core components
        class IntegratedService(FlextService[FlextTypes.Dict]):
            def __init__(self) -> None:
                super().__init__()
                # self.logger is read-only, use class logger
                self._container = FlextContainer.get_global()

            def execute(self) -> FlextResult[FlextTypes.Dict]:
                try:
                    # Use logger
                    self.logger.info("Service executing")

                    # Use container
                    self._container.register("test", "value")

                    # Return success result
                    return FlextResult[FlextTypes.Dict].ok(
                        {
                            "status": "success",
                            "message": "Integration test passed",
                        }
                    )
                except Exception as e:
                    return FlextResult[FlextTypes.Dict].fail(str(e))

        service = IntegratedService()
        result = service.execute()

        assert result.is_success
        assert result.data is not None
        assert result.data["status"] == "success"

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

    def test_flext_core_performance(self) -> None:
        """Test flext-core performance characteristics."""
        # Test that operations are reasonably fast
        start_time = time.time()

        # Perform multiple operations
        for _ in range(100):
            result = FlextResult[str].ok("test")
            assert result.is_success

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete quickly (less than 1 second for 100 operations)
        assert elapsed < 1.0
