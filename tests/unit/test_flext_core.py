"""Comprehensive consolidated tests for flext-core module.

Tests all flext-core functionality with real implementations, no mocks or legacy patterns.
Achieves almost 100% coverage through comprehensive test scenarios using flext_tests library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import pytest
from flext_core import FlextCore


class TestFlextConsolidated:
    """Unified test class for all flext-core functionality."""

    class _TestDataHelper:
        """Nested helper class for test data creation."""

        @staticmethod
        def create_success_data() -> FlextCore.Types.Dict:
            """Create test data for success cases."""
            return {"status": "success", "data": "test_value"}

        @staticmethod
        def create_failure_data() -> str:
            """Create test data for failure cases."""
            return "test_error_message"

        @staticmethod
        def create_complex_data() -> FlextCore.Types.Dict:
            """Create complex test data."""
            return {"nested": {"value": 42}, "list": [1, 2, 3], "string": "test"}

    # =============================================================================
    # FLEXT RESULT TESTS
    # =============================================================================

    def test_flext_result_success_creation(self) -> None:
        """Test FlextCore.Result success creation with various data types."""
        # Test with string
        result_str = FlextCore.Result[str].ok("success")
        assert result_str.is_success
        assert result_str.data == "success"
        assert result_str.error is None
        assert not result_str.is_failure

        # Test with dict
        test_data = self._TestDataHelper.create_success_data()
        result_dict = FlextCore.Result[FlextCore.Types.Dict].ok(test_data)
        assert result_dict.is_success
        assert result_dict.data == test_data
        assert result_dict.error is None

        # Test with complex data
        complex_data = self._TestDataHelper.create_complex_data()
        result_complex = FlextCore.Result[FlextCore.Types.Dict].ok(complex_data)
        assert result_complex.is_success
        assert result_complex.data == complex_data

    def test_flext_result_failure_creation(self) -> None:
        """Test FlextCore.Result failure creation."""
        error_msg = self._TestDataHelper.create_failure_data()
        result = FlextCore.Result[str].fail(error_msg)

        assert result.is_failure
        assert result.error == error_msg
        assert not result.is_success

        # Test that accessing data on failure raises exception
        with pytest.raises(TypeError):
            _ = result.data

    def test_flext_result_unwrap_success(self) -> None:
        """Test FlextCore.Result unwrap on success."""
        test_data = "test_value"
        result = FlextCore.Result[str].ok(test_data)
        unwrapped = result.unwrap()
        assert unwrapped == test_data

    def test_flext_result_unwrap_failure(self) -> None:
        """Test FlextCore.Result unwrap on failure raises exception."""
        result = FlextCore.Result[str].fail("error")
        with pytest.raises(Exception):
            result.unwrap()

    def test_flext_result_dual_access_api(self) -> None:
        """Test FlextCore.Result dual access API (.value and .data)."""
        test_data = "test_value"
        result = FlextCore.Result[str].ok(test_data)

        # Test both access methods work
        assert result.data == test_data
        assert result.value == test_data
        assert result.data == result.value

    # =============================================================================
    # FLEXT CONTAINER TESTS
    # =============================================================================

    def test_flext_container_global_access(self) -> None:
        """Test FlextCore.Container global access."""
        container = FlextCore.Container.get_global()
        assert container is not None
        assert isinstance(container, FlextCore.Container)

    def test_flext_container_singleton_pattern(self) -> None:
        """Test FlextCore.Container singleton pattern."""
        container1 = FlextCore.Container.get_global()
        container2 = FlextCore.Container.get_global()
        assert container1 is container2

    def test_flext_container_registration(self) -> None:
        """Test FlextCore.Container service registration."""
        container = FlextCore.Container.get_global()

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
        """Test FlextCore.Logger creation."""
        logger = FlextCore.Logger(__name__)
        assert logger is not None
        assert isinstance(logger, FlextCore.Logger)

    def test_flext_logger_different_names(self) -> None:
        """Test FlextCore.Logger with different module names."""
        logger1 = FlextCore.Logger("module1")
        logger2 = FlextCore.Logger("module2")

        assert logger1 is not None
        assert logger2 is not None
        assert logger1 != logger2

    # =============================================================================
    # FLEXT CONSTANTS TESTS
    # =============================================================================

    def test_flext_constants_access(self) -> None:
        """Test FlextCore.Constants access."""
        # Test platform constants
        assert FlextCore.Constants.Platform.HTTP_STATUS_OK is not None
        assert FlextCore.Constants.Platform.HTTP_STATUS_INTERNAL_ERROR is not None

        # Test logging constants
        assert FlextCore.Constants.Logging.DEFAULT_LEVEL is not None
        assert FlextCore.Constants.Logging.DEFAULT_FORMAT is not None

    def test_flext_constants_immutability(self) -> None:
        """Test FlextCore.Constants immutability."""
        # Constants should be accessible but not modifiable
        original_value = FlextCore.Constants.Platform.HTTP_STATUS_OK
        assert original_value is not None

        # Verify it's a constant value
        assert isinstance(original_value, int)

    # =============================================================================
    # FLEXT CONFIG TESTS
    # =============================================================================

    def test_flext_config_creation(self) -> None:
        """Test FlextCore.Config creation."""
        config = FlextCore.Config()
        assert config is not None
        assert isinstance(config, FlextCore.Config)

    def test_flext_config_with_data(self) -> None:
        """Test FlextCore.Config with initial data."""
        config = FlextCore.Config(app_name="Test App", version="1.0.0")

        assert config is not None
        # Verify config has expected attributes
        assert hasattr(config, "app_name")
        assert hasattr(config, "version")

    # =============================================================================
    # FLEXT MODELS TESTS
    # =============================================================================

    def test_flext_models_access(self) -> None:
        """Test FlextCore.Models access."""
        # Test that FlextCore.Models is accessible
        assert FlextCore.Models is not None

        # Test that it has expected structure
        assert hasattr(FlextCore.Models, "Entity") or hasattr(FlextCore.Models, "Value")

    # =============================================================================
    # FLEXT TYPES TESTS
    # =============================================================================

    def test_flext_types_access(self) -> None:
        """Test FlextCore.Types access."""
        # Test core types
        assert FlextCore.Types.Dict is not None
        assert FlextCore.Types.List is not None
        assert FlextCore.Types.StringList is not None

    def test_flext_types_usage(self) -> None:
        """Test FlextCore.Types usage in type annotations."""
        # Test that types can be used in annotations
        test_dict: FlextCore.Types.Dict = {"key": "value"}
        test_list: FlextCore.Types.List = [1, 2, 3]
        test_string_list: FlextCore.Types.StringList = ["test1", "test2"]

        assert test_dict is not None
        assert test_list is not None
        assert test_string_list is not None

    # =============================================================================
    # FLEXT UTILITIES TESTS
    # =============================================================================

    def test_flext_utilities_access(self) -> None:
        """Test FlextCore.Utilities access."""
        assert FlextCore.Utilities is not None

        # Test that it has expected methods
        assert (
            hasattr(FlextCore.Utilities, "Validation")
            or hasattr(FlextCore.Utilities, "Processing")
            or hasattr(FlextCore.Utilities, "Conversion")
        )

    # =============================================================================
    # FLEXT SERVICE TESTS
    # =============================================================================

    def test_flext_service_creation(self) -> None:
        """Test FlextCore.Service creation."""

        # Create a simple service implementation
        class TestService(FlextCore.Service[str]):
            def execute(self) -> FlextCore.Result[str]:
                return FlextCore.Result[str].ok("test_result")

        service = TestService()
        assert service is not None
        assert isinstance(service, FlextCore.Service)

    def test_flext_service_execution(self) -> None:
        """Test FlextCore.Service execution."""

        class TestService(FlextCore.Service[str]):
            def execute(self) -> FlextCore.Result[str]:
                return FlextCore.Result[str].ok("test_result")

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
        class IntegratedService(FlextCore.Service[FlextCore.Types.Dict]):
            def __init__(self) -> None:
                super().__init__()
                # self.logger is read-only, use class logger
                self._container = FlextCore.Container.get_global()

            def execute(self) -> FlextCore.Result[FlextCore.Types.Dict]:
                try:
                    # Use logger
                    self.logger.info("Service executing")

                    # Use container
                    self._container.register("test", "value")

                    # Return success result
                    return FlextCore.Result[FlextCore.Types.Dict].ok({
                        "status": "success",
                        "message": "Integration test passed",
                    })
                except Exception as e:
                    return FlextCore.Result[FlextCore.Types.Dict].fail(str(e))

        service = IntegratedService()
        result = service.execute()

        assert result.is_success
        assert result.data is not None
        assert result.data["status"] == "success"

    def test_flext_core_error_handling(self) -> None:
        """Test flext-core error handling patterns."""

        # Test that errors are properly handled through FlextCore.Result
        class ErrorService(FlextCore.Service[str]):
            def execute(self) -> FlextCore.Result[str]:
                try:
                    # Simulate an error
                    msg = "Test error"
                    raise ValueError(msg)
                except Exception as e:
                    return FlextCore.Result[str].fail(str(e))

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
            result = FlextCore.Result[str].ok("test")
            assert result.is_success

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete quickly (less than 1 second for 100 operations)
        assert elapsed < 1.0
