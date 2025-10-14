"""Targeted tests for flext-core modules focusing on actual existing API.

Tests the real API methods to achieve maximum coverage with working functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time

import pytest
from flext_core import FlextCore


class TestFlextTargeted:
    """Targeted tests for actual flext-core API methods."""

    # =============================================================================
    # FLEXT RESULT TARGETED TESTS - Based on Actual API
    # =============================================================================

    def test_flext_result_creation_and_basic_properties(self) -> None:
        """Test FlextCore.Result creation and basic property access."""
        # Test successful creation
        success = FlextCore.Result[str].ok("test_data")
        assert success.is_success
        assert not success.is_failure
        assert success.data == "test_data"
        assert success.value == "test_data"  # Dual access API
        assert success.error is None

        # Test failure creation
        failure = FlextCore.Result[str].fail("error_message")
        assert failure.is_failure
        assert not failure.is_success
        # Use safe access for failure (property, not method)
        assert failure.value_or_none is None
        assert failure.error == "error_message"

    def test_flext_result_unwrap_methods(self) -> None:
        """Test unwrap methods."""
        success = FlextCore.Result[str].ok("data")
        failure = FlextCore.Result[str].fail("error")

        # Test unwrap
        assert success.unwrap() == "data"

        with pytest.raises(Exception):
            failure.unwrap()

        # Test unwrap_or
        assert success.unwrap_or("default") == "data"
        assert failure.unwrap_or("default") == "default"

        # Test value_or_none property
        assert success.value_or_none == "data"
        assert failure.value_or_none is None

    def test_flext_result_map_operations(self) -> None:
        """Test map and flat_map operations."""
        success = FlextCore.Result[int].ok(5)
        failure = FlextCore.Result[int].fail("error")

        # Test map
        mapped_success = success.map(lambda x: x * 2)
        assert mapped_success.is_success
        assert mapped_success.data == 10

        mapped_failure = failure.map(lambda x: x * 2)
        assert mapped_failure.is_failure

        # Test flat_map
        def double_wrap(x: int) -> FlextCore.Result[int]:
            return FlextCore.Result[int].ok(x * 2)

        flat_mapped = success.flat_map(double_wrap)
        assert flat_mapped.is_success
        assert flat_mapped.data == 10

    def test_flext_result_logical_operations(self) -> None:
        """Test logical operations and operators."""
        success1 = FlextCore.Result[int].ok(1)
        success2 = FlextCore.Result[int].ok(2)
        failure = FlextCore.Result[int].fail("error")

        # Test or_else method instead of | operator
        or_result = success1.or_else(success2)
        assert or_result.is_success
        assert or_result.data == 1

        or_with_failure = failure.or_else(success2)
        assert or_with_failure.is_success
        assert or_with_failure.data == 2

    def test_flext_result_error_handling(self) -> None:
        """Test error handling methods."""
        failure = FlextCore.Result[str].fail("original_error")

        # Test or_else
        recovered = failure.or_else(FlextCore.Result[str].ok("recovered"))
        assert recovered.is_success
        assert recovered.data == "recovered"

        # Test recover
        def recovery_fn(error: str) -> str:
            return f"recovered_from_{error}"

        recovered_with_fn = failure.recover(recovery_fn)
        assert recovered_with_fn.is_success
        assert "recovered_from_original_error" in recovered_with_fn.data

    def test_flext_result_filtering_and_validation(self) -> None:
        """Test filter and validation methods."""
        success = FlextCore.Result[int].ok(5)

        # Test filter
        filtered_pass = success.filter(lambda x: x > 3, "Value too small")
        assert filtered_pass.is_success

        filtered_fail = success.filter(lambda x: x > 10, "Value too small")
        assert filtered_fail.is_failure

    def test_flext_result_context_manager(self) -> None:
        """Test FlextCore.Result as context manager."""
        success = FlextCore.Result[str].ok("test_data")

        with success as value:
            assert value == "test_data"

        # Test with failure
        failure = FlextCore.Result[str].fail("error")

        with pytest.raises(Exception), failure as value:
            pass  # Should raise

    def test_flext_result_equality_and_hashing(self) -> None:
        """Test equality and hashing."""
        success1 = FlextCore.Result[int].ok(42)
        success2 = FlextCore.Result[int].ok(42)
        success3 = FlextCore.Result[int].ok(43)
        failure1 = FlextCore.Result[int].fail("error")
        failure2 = FlextCore.Result[int].fail("error")

        # Test equality
        assert success1 == success2
        assert success1 != success3
        assert success1 != failure1
        assert failure1 == failure2

        # Test hashing (for use in sets/dicts)
        result_set = {success1, success2, failure1}
        assert len(result_set) == 2  # success1 and success2 are equal

    # =============================================================================
    # FLEXT UTILITIES TARGETED TESTS
    # =============================================================================

    def test_flext_utilities_generators(self) -> None:
        """Test FlextCore.Utilities.Generators methods."""
        # Test timestamp generation
        ts1 = FlextCore.Utilities.Generators.generate_timestamp()
        time.sleep(0.001)
        ts2 = FlextCore.Utilities.Generators.generate_timestamp()

        assert ts1 != ts2
        assert isinstance(ts1, str)
        assert "T" in ts1

        # Test UUID generation
        uuid1 = FlextCore.Utilities.Generators.generate_uuid()
        uuid2 = FlextCore.Utilities.Generators.generate_uuid()

        assert uuid1 != uuid2
        assert len(uuid1) == 36
        assert uuid1.count("-") == 4

        # Test correlation ID
        corr1 = FlextCore.Utilities.Generators.generate_correlation_id()
        corr2 = FlextCore.Utilities.Generators.generate_correlation_id()

        assert corr1 != corr2
        assert isinstance(corr1, str)
        assert len(corr1) > 0

    def test_flext_utilities_conversions(self) -> None:
        """Test FlextCore.Utilities.TypeConversions methods."""
        # Test to_int conversion
        int_result = FlextCore.Utilities.TypeConversions.to_int("42")
        assert int_result.is_success
        assert int_result.data == 42

        # Test failed int conversion
        fail_result = FlextCore.Utilities.TypeConversions.to_int("not_number")
        assert fail_result.is_failure

        # Test to_bool conversion (uses keyword argument)
        bool_result = FlextCore.Utilities.TypeConversions.to_bool(value="true")
        assert bool_result.is_success
        assert bool_result.data is True

    def test_flext_utilities_validation(self) -> None:
        """Test FlextCore.Utilities.Validation methods."""
        # Test string validation
        string_valid = FlextCore.Utilities.Validation.validate_string("test")
        assert string_valid.is_success

        # Test email validation
        email_valid = FlextCore.Utilities.Validation.validate_email("test@example.com")
        assert email_valid.is_success

        # Test port validation
        port_valid = FlextCore.Utilities.Validation.validate_port(8080)
        assert port_valid.is_success

    # =============================================================================
    # FLEXT CONTAINER TARGETED TESTS
    # =============================================================================

    def test_flext_container_basic_operations(self) -> None:
        """Test FlextCore.Container basic operations."""
        container = FlextCore.Container.get_global()

        # Test registration and retrieval
        key = "test_container_key"
        value = "test_value"

        container.register(key, value)
        result = container.get(key)

        assert result.is_success
        assert result.data == value

        # Test non-existent key
        missing_result = container.get("nonexistent_key")
        assert missing_result.is_failure

    def test_flext_container_singleton_behavior(self) -> None:
        """Test FlextCore.Container singleton pattern."""
        container1 = FlextCore.Container.get_global()
        container2 = FlextCore.Container.get_global()

        assert container1 is container2

    # =============================================================================
    # FLEXT BUS TARGETED TESTS
    # =============================================================================

    def test_flext_bus_basic_pubsub(self) -> None:
        """Test FlextCore.Bus basic handler registration and execution."""
        bus = FlextCore.Bus()

        def handler(command: str) -> FlextCore.Result[str]:
            return FlextCore.Result[str].ok(f"handled_{command}")

        # Test handler registration
        reg_result = bus.register_handler("TestCommand", handler)
        assert reg_result.is_success

        # Test command execution
        exec_result = bus.send_command("TestCommand")
        assert isinstance(exec_result, FlextCore.Result)

    # =============================================================================
    # FLEXT SERVICE TARGETED TESTS
    # =============================================================================

    def test_flext_service_basic_functionality(self) -> None:
        """Test FlextCore.Service basic functionality."""

        class TestService(FlextCore.Service[str]):
            def execute(self) -> FlextCore.Result[str]:
                return FlextCore.Result[str].ok("service_executed")

        service = TestService()
        result = service.execute()

        assert result.is_success
        assert result.data == "service_executed"

    def test_flext_service_with_error(self) -> None:
        """Test FlextCore.Service error handling."""

        class ErrorService(FlextCore.Service[str]):
            def execute(self) -> FlextCore.Result[str]:
                return FlextCore.Result[str].fail("service_error")

        service = ErrorService()
        result = service.execute()

        assert result.is_failure
        assert result.error == "service_error"

    # =============================================================================
    # FLEXT LOGGER TARGETED TESTS
    # =============================================================================

    def test_flext_logger_basic_logging(self) -> None:
        """Test FlextCore.Logger basic functionality."""
        logger = FlextCore.Logger("test_logger")

        # Test basic logging methods
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Test structured logging
        logger.info("Structured message", extra={"key": "value"})

    # =============================================================================
    # FLEXT CONFIG TARGETED TESTS
    # =============================================================================

    def test_flext_config_basic_operations(self) -> None:
        """Test FlextCore.Config basic operations."""
        # Test basic config creation
        config = FlextCore.Config()

        # Test config exists
        assert config is not None
        assert isinstance(config, FlextCore.Config)

    # =============================================================================
    # FLEXT MODELS TARGETED TESTS
    # =============================================================================

    def test_flext_models_basic_validation(self) -> None:
        """Test FlextCore.Models basic validation functionality."""
        # Test model functionality with actual model classes
        entity_model = FlextCore.Models.Entity()
        assert entity_model is not None

        # Test model validation exists
        assert hasattr(FlextCore.Models, "Validation")

        # Test validation methods
        validation = FlextCore.Models.Validation()
        assert validation is not None

    # =============================================================================
    # FLEXT CONSTANTS TARGETED TESTS
    # =============================================================================

    def test_flext_constants_access(self) -> None:
        """Test FlextCore.Constants access."""
        # Test that constants exist and are accessible
        assert hasattr(FlextCore.Constants, "Core")
        core_constants = FlextCore.Constants
        assert core_constants is not None

    # =============================================================================
    # FLEXT TYPES TARGETED TESTS
    # =============================================================================

    def test_flext_types_usage(self) -> None:
        """Test FlextCore.Types usage."""
        # Test basic type usage
        test_dict: FlextCore.Types.Dict = {"key": "value"}
        assert isinstance(test_dict, dict)

        test_list: FlextCore.Types.List = [1, 2, 3]
        assert isinstance(test_list, list)

        # Test config types
        config_value: FlextCore.Types.ConfigValue = "config_string"
        assert isinstance(config_value, str)

    # =============================================================================
    # PERFORMANCE AND STRESS TESTS
    # =============================================================================

    def test_performance_basic(self) -> None:
        """Test basic performance characteristics."""
        start_time = time.time()

        # Create many FlextCore.Result instances
        results = []
        for i in range(1000):
            result = FlextCore.Result[int].ok(i)
            results.append(result)

        # Test basic operations
        for result in results[:100]:
            mapped = result.map(lambda x: x * 2)
            assert mapped.is_success

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete reasonably quickly
        assert elapsed < 2.0

    # =============================================================================
    # ERROR HANDLING AND EDGE CASES
    # =============================================================================

    def test_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test with None values
        none_result = FlextCore.Result[None].ok(None)
        assert none_result.is_success
        assert none_result.data is None

        # Test empty collections
        empty_list = FlextCore.Result[FlextCore.Types.List].ok([])
        assert empty_list.is_success
        assert empty_list.data == []

        empty_dict = FlextCore.Result[FlextCore.Types.Dict].ok({})
        assert empty_dict.is_success
        assert empty_dict.data == {}

        # Test large strings
        large_string = "x" * 10000
        large_result = FlextCore.Result[str].ok(large_string)
        assert large_result.is_success
        assert len(large_result.data) == 10000

    def test_exception_handling(self) -> None:
        """Test exception handling patterns."""
        # Test creating result from exception
        try:
            msg = "Test exception"
            raise ValueError(msg)
        except ValueError as e:
            result = FlextCore.Result[str].fail(str(e))
            assert result.is_failure
            assert result.error is not None and "Test exception" in result.error

        # Test safe operations
        def risky_operation() -> str:
            msg = "Risky operation failed"
            raise RuntimeError(msg)

        try:
            risky_operation()
            result = FlextCore.Result[str].ok("success")
        except Exception as e:
            result = FlextCore.Result[str].fail(str(e))

        assert result.is_failure
        assert result.error is not None and "Risky operation failed" in result.error

    # =============================================================================
    # INTEGRATION TESTS
    # =============================================================================

    def test_component_integration(self) -> None:
        """Test integration between different components."""
        # Create a comprehensive test that uses multiple components
        container = FlextCore.Container.get_global()
        logger = FlextCore.Logger("integration_test")
        FlextCore.Bus()

        class IntegrationService(FlextCore.Service[FlextCore.Types.Dict]):
            def execute(self) -> FlextCore.Result[FlextCore.Types.Dict]:
                # Use container
                container.register("integration_key", "integration_value")

                # Use logger
                logger.info("Integration service executing")

                # Create result with timestamp
                timestamp = FlextCore.Utilities.Generators.generate_timestamp()

                return FlextCore.Result[FlextCore.Types.Dict].ok({
                    "status": "success",
                    "timestamp": timestamp,
                    "container_value": container.get("integration_key").unwrap_or(
                        "default"
                    ),
                })

        service = IntegrationService()
        result = service.execute()

        assert result.is_success
        data = result.data
        assert data["status"] == "success"
        assert "timestamp" in data
        assert data["container_value"] == "integration_value"

    def test_compatibility(self) -> None:
        """Test compatibility where applicable."""

        def operation() -> FlextCore.Result[str]:
            time.sleep(0.001)
            return FlextCore.Result[str].ok("success")

        # Run test
        result = operation()
        assert result.is_success
        assert result.data == "success"
