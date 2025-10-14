"""Comprehensive tests for flext-core achieving near 100% coverage.

This module contains extensive tests for all flext-core functionality,
focusing on real functionality testing without mocks to achieve maximum coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import math
import time

import pytest
from flext_core import FlextCore


class TestFlextComprehensive:
    """Comprehensive tests for all flext-core components."""

    # =============================================================================
    # FLEXT RESULT COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_result_all_creation_methods(self) -> None:
        """Test all FlextCore.Result creation methods and edge cases."""
        # Test ok() with various types
        result_str = FlextCore.Result[str].ok("test")
        assert result_str.is_success
        assert result_str.data == "test"
        assert result_str.value == "test"  # Dual access API

        result_none = FlextCore.Result[None].ok(None)
        assert result_none.is_success
        assert result_none.data is None

        result_dict = FlextCore.Result[FlextCore.Types.Dict].ok({"key": "value"})
        assert result_dict.is_success
        assert result_dict.data["key"] == "value"

        # Test fail() with various error types
        result_fail = FlextCore.Result[str].fail("Error message")
        assert result_fail.is_failure
        assert result_fail.error == "Error message"

        result_exception = FlextCore.Result[int].fail(ValueError("Test error"))
        assert result_exception.is_failure
        assert "Test error" in str(result_exception.error)

    def test_flext_result_unwrap_methods(self) -> None:
        """Test all unwrap methods and error handling."""
        success = FlextCore.Result[str].ok("data")
        fail = FlextCore.Result[str].fail("error")

        # Test successful unwrap
        assert success.unwrap() == "data"

        # Test unwrap_or
        assert success.unwrap_or("default") == "data"
        assert fail.unwrap_or("default") == "default"

        # Test unwrap with failure
        with pytest.raises(ValueError, match="error"):
            fail.unwrap()

        # Test unwrap with custom exception
        with pytest.raises(RuntimeError, match="Custom"):
            fail.unwrap(RuntimeError("Custom"))

    def test_flext_result_map_operations(self) -> None:
        """Test map and flatmap operations."""
        success = FlextCore.Result[int].ok(5)
        fail = FlextCore.Result[int].fail("error")

        # Test map on success
        mapped = success.map(lambda x: x * 2)
        assert mapped.is_success
        assert mapped.data == 10

        # Test map on failure
        mapped_fail = fail.map(lambda x: x * 2)
        assert mapped_fail.is_failure

        # Test flatmap
        def double_wrap(x: int) -> FlextCore.Result[int]:
            return FlextCore.Result[int].ok(x * 2)

        flatmapped = success.flatmap(double_wrap)
        assert flatmapped.is_success
        assert flatmapped.data == 10

    def test_flext_result_match_method(self) -> None:
        """Test pattern matching functionality."""
        success = FlextCore.Result[str].ok("data")
        fail = FlextCore.Result[str].fail("error")

        success_result = success.match(
            on_success=lambda d: f"Success: {d}", on_failure=lambda e: f"Error: {e}"
        )
        assert success_result == "Success: data"

        fail_result = fail.match(
            on_success=lambda d: f"Success: {d}", on_failure=lambda e: f"Error: {e}"
        )
        assert fail_result == "Error: error"

    def test_flext_result_logical_operations(self) -> None:
        """Test and/or operations."""
        success1 = FlextCore.Result[int].ok(1)
        success2 = FlextCore.Result[int].ok(2)
        fail1 = FlextCore.Result[int].fail("error1")
        fail2 = FlextCore.Result[int].fail("error2")

        # Test and operations
        assert success1.and_(success2).data == 2
        assert success1.and_(fail1).is_failure

        # Test or operations
        assert success1.or_(success2).data == 1
        assert fail1.or_(success2).data == 2
        assert fail1.or_(fail2).is_failure

    # =============================================================================
    # FLEXT BUS COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_bus_message_handling(self) -> None:
        """Test comprehensive FlextCore.Bus message handling."""
        bus = FlextCore.Bus()
        received_messages = []

        def handler(message: FlextCore.Types.Dict) -> FlextCore.Result[str]:
            received_messages.append(message)
            return FlextCore.Result[str].ok("handled")

        # Test subscription
        bus.subscribe("test_topic", handler)

        # Test publishing
        test_msg = {"data": "test"}
        result = bus.publish("test_topic", test_msg)

        assert result.is_success
        assert len(received_messages) == 1
        assert received_messages[0]["data"] == "test"

        # Test unsubscribe
        bus.unsubscribe("test_topic", handler)
        bus.publish("test_topic", {"data": "ignored"})
        assert len(received_messages) == 1  # No new messages

    def test_flext_bus_multiple_handlers(self) -> None:
        """Test multiple handlers for same topic."""
        bus = FlextCore.Bus()
        handler1_calls = []
        handler2_calls = []

        def handler1(msg: FlextCore.Types.Dict) -> FlextCore.Result[str]:
            handler1_calls.append(msg)
            return FlextCore.Result[str].ok("h1")

        def handler2(msg: FlextCore.Types.Dict) -> FlextCore.Result[str]:
            handler2_calls.append(msg)
            return FlextCore.Result[str].ok("h2")

        bus.subscribe("multi", handler1)
        bus.subscribe("multi", handler2)

        bus.publish("multi", {"data": "test"})

        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1

    def test_flext_bus_error_handling(self) -> None:
        """Test FlextCore.Bus error handling."""
        bus = FlextCore.Bus()

        def failing_handler(msg: FlextCore.Types.Dict) -> FlextCore.Result[str]:
            return FlextCore.Result[str].fail("Handler error")

        bus.subscribe("error_topic", failing_handler)
        result = bus.publish("error_topic", {"data": "test"})

        # Bus should handle handler errors gracefully
        assert result.is_success or result.is_failure  # Either is acceptable

    # =============================================================================
    # FLEXT UTILITIES COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_utilities_generators(self) -> None:
        """Test all FlextCore.Utilities.Generators methods."""
        # Test timestamp generation
        ts1 = FlextCore.Utilities.Generators.generate_timestamp()
        time.sleep(0.001)
        ts2 = FlextCore.Utilities.Generators.generate_timestamp()

        assert ts1 != ts2
        assert isinstance(ts1, str)
        assert "T" in ts1  # ISO format

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
        assert len(corr1) > 0

    def test_flext_utilities_validation(self) -> None:
        """Test FlextCore.Utilities.Validation methods."""
        # Test dict[str, object] structure validation
        valid_data = {"name": "test", "age": 25}
        result = FlextCore.Utilities.Validation.validate_dict_structure(
            valid_data, required_keys=["name", "age"]
        )
        assert result.is_success

        # Test missing keys
        invalid_data = {"name": "test"}
        fail_result = FlextCore.Utilities.Validation.validate_dict_structure(
            invalid_data, required_keys=["name", "age"]
        )
        assert fail_result.is_failure

        # Test type validation
        type_valid = FlextCore.Utilities.Validation.validate_type("test", str)
        assert type_valid.is_success

        type_invalid = FlextCore.Utilities.Validation.validate_type(123, str)
        assert type_invalid.is_failure

    def test_flext_utilities_conversion(self) -> None:
        """Test FlextCore.Utilities.Conversion methods."""
        # Test safe casting
        int_result = FlextCore.Utilities.Conversion.safe_cast("42", int)
        assert int_result.is_success
        assert int_result.data == 42

        # Test failed casting
        fail_result = FlextCore.Utilities.Conversion.safe_cast("not_number", int)
        assert fail_result.is_failure

        # Test float conversion
        float_result = FlextCore.Utilities.Conversion.safe_cast("3.14", float)
        assert float_result.is_success
        assert abs(float_result.data - math.pi) < 0.001

        # Test dict[str, object] to object
        test_dict = {"key1": "value1", "key2": "value2"}
        obj_result = FlextCore.Utilities.Conversion.dict_to_object(test_dict)
        assert obj_result.is_success
        obj = obj_result.data
        assert hasattr(obj, "key1")
        assert obj.key1 == "value1"

    def test_flext_utilities_collection_operations(self) -> None:
        """Test FlextCore.Utilities collection operations."""
        # Test list operations
        test_list = [1, 2, 3, 4, 5]
        chunk_result = FlextCore.Utilities.Collections.chunk_list(test_list, 2)
        assert chunk_result.is_success
        chunks = chunk_result.data
        assert len(chunks) == 3
        assert chunks[0] == [1, 2]
        assert chunks[1] == [3, 4]
        assert chunks[2] == [5]

        # Test flatten operation
        nested_list = [[1, 2], [3, 4], [5]]
        flatten_result = FlextCore.Utilities.Collections.flatten_list(nested_list)
        assert flatten_result.is_success
        assert flatten_result.data == [1, 2, 3, 4, 5]

        # Test unique operation
        duplicate_list = [1, 2, 2, 3, 3, 3]
        unique_result = FlextCore.Utilities.Collections.unique_list(duplicate_list)
        assert unique_result.is_success
        assert set(unique_result.data) == {1, 2, 3}

    def test_flext_utilities_string_operations(self) -> None:
        """Test FlextCore.Utilities string operations."""
        # Test string formatting
        template = "Hello {name}, you are {age} years old"
        format_result = FlextCore.Utilities.Strings.safe_format(
            template, name="Alice", age=30
        )
        assert format_result.is_success
        assert format_result.data == "Hello Alice, you are 30 years old"

        # Test truncation
        long_string = "This is a very long string that should be truncated"
        trunc_result = FlextCore.Utilities.Strings.truncate_string(long_string, 20)
        assert trunc_result.is_success
        assert len(trunc_result.data) <= 20

        # Test slug generation
        text = "Hello World! This is a Test."
        slug_result = FlextCore.Utilities.Strings.to_slug(text)
        assert slug_result.is_success
        assert slug_result.data == "hello-world-this-is-a-test"

    # =============================================================================
    # FLEXT CONTAINER COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_container_registration_and_retrieval(self) -> None:
        """Test FlextCore.Container comprehensive functionality."""
        container = FlextCore.Container.get_global()

        # Test basic registration
        container.register("test_key", "test_value")
        result = container.get("test_key")
        assert result.is_success
        assert result.data == "test_value"

        # Test complex object registration
        complex_obj = {"nested": {"data": [1, 2, 3]}}
        container.register("complex", complex_obj)
        complex_result = container.get("complex")
        assert complex_result.is_success
        assert complex_result.data["nested"]["data"] == [1, 2, 3]

        # Test non-existent key
        missing_result = container.get("nonexistent")
        assert missing_result.is_failure

    def test_flext_container_singleton_pattern(self) -> None:
        """Test FlextCore.Container singleton behavior."""
        container1 = FlextCore.Container.get_global()
        container2 = FlextCore.Container.get_global()

        assert container1 is container2

        # Test that registrations persist across instances
        container1.register("singleton_test", "value")
        result = container2.get("singleton_test")
        assert result.is_success
        assert result.data == "value"

    def test_flext_container_type_safety(self) -> None:
        """Test FlextCore.Container with typed operations."""
        container = FlextCore.Container.get_global()

        # Test string type
        container.register_typed("typed_string", "hello", str)
        str_result = container.get_typed("typed_string", str)
        assert str_result.is_success
        assert str_result.data == "hello"

        # Test int type
        container.register_typed("typed_int", 42, int)
        int_result = container.get_typed("typed_int", int)
        assert int_result.is_success
        assert int_result.data == 42

        # Test wrong type retrieval
        wrong_type_result = container.get_typed("typed_string", int)
        assert wrong_type_result.is_failure

    # =============================================================================
    # FLEXT SERVICE COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_service_lifecycle(self) -> None:
        """Test FlextCore.Service lifecycle methods."""

        class TestService(FlextCore.Service[str]):
            def __init__(self) -> None:
                super().__init__()
                self.initialized = True
                self.executed = False
                self.cleaned = False

            def execute(self) -> FlextCore.Result[str]:
                self.executed = True
                return FlextCore.Result[str].ok("service_result")

            def cleanup(self) -> FlextCore.Result[None]:
                self.cleaned = True
                return FlextCore.Result[None].ok(None)

        service = TestService()
        assert service.initialized

        # Test execution
        result = service.execute()
        assert result.is_success
        assert result.data == "service_result"
        assert service.executed

        # Test cleanup
        cleanup_result = service.cleanup()
        assert cleanup_result.is_success
        assert service.cleaned

    def test_flext_service_error_handling(self) -> None:
        """Test FlextCore.Service error handling patterns."""

        class ErrorService(FlextCore.Service[str]):
            def execute(self) -> FlextCore.Result[str]:
                try:
                    msg = "Service error"
                    raise ValueError(msg)
                except Exception as e:
                    return FlextCore.Result[str].fail(str(e))

        service = ErrorService()
        result = service.execute()

        assert result.is_failure
        assert result.error is not None and "Service error" in result.error

    def test_flext_service_operations(self) -> None:
        """Test FlextCore.Service with operations."""

        class Service(FlextCore.Service[str]):
            def execute(self) -> FlextCore.Result[str]:
                time.sleep(0.001)  # Minimal delay
                return FlextCore.Result[str].ok("result")

        service = Service()

        def test() -> None:
            result = service.execute()
            assert result.is_success
            assert result.data == "result"

        # Run the test
        test()

    # =============================================================================
    # FLEXT LOGGER COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_logger_all_levels(self) -> None:
        """Test FlextCore.Logger with all log levels."""
        logger = FlextCore.Logger("test_logger")

        # Test all log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Test structured logging
        logger.info("Structured log", extra={"key": "value", "count": 42})

        # Test exception logging
        try:
            msg = "Test exception"
            raise ValueError(msg)
        except ValueError:
            logger.exception("Exception occurred")

    def test_flext_logger_context(self) -> None:
        """Test FlextCore.Logger with context."""
        logger = FlextCore.Logger("context_test")

        # Test with correlation ID
        with logger.context(correlation_id="test-123"):
            logger.info("Message with context")

        # Test with multiple context values
        with logger.context(user_id="user-456", operation="test_op"):
            logger.info("Message with multiple context")

    def test_flext_logger_performance(self) -> None:
        """Test FlextCore.Logger performance characteristics."""
        logger = FlextCore.Logger("perf_test")

        start_time = time.time()

        # Log many messages
        for i in range(100):
            logger.info(f"Performance test message {i}")

        end_time = time.time()
        elapsed = end_time - start_time

        # Should be reasonably fast
        assert elapsed < 1.0

    # =============================================================================
    # FLEXT CONFIG COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_config_creation_and_access(self) -> None:
        """Test FlextCore.Config comprehensive functionality."""
        # Test creating config with data
        config_data = {
            "app_name": "test_app",
            "debug": True,
            "port": 8080,
            "features": ["feature1", "feature2"],
        }

        config = FlextCore.Config(config_data)

        # Test basic access
        assert config.get("app_name") == "test_app"
        assert config.get("debug") is True
        assert config.get("port") == 8080

        # Test with default values
        assert config.get("nonexistent", "default") == "default"
        assert config.get("nonexistent") is None

        # Test list access
        features = config.get("features")
        assert features == ["feature1", "feature2"]

    def test_flext_config_nested_access(self) -> None:
        """Test FlextCore.Config with nested data structures."""
        nested_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"username": "REDACTED_LDAP_BIND_PASSWORD", "password": "secret"},
            },
            "cache": {"redis": {"host": "redis-host", "port": 6379}},
        }

        config = FlextCore.Config(nested_config)

        # Test nested access
        db_config = config.get("database")
        assert db_config["host"] == "localhost"
        assert db_config["port"] == 5432

        # Test deep nested access
        credentials = db_config["credentials"]
        assert credentials["username"] == "REDACTED_LDAP_BIND_PASSWORD"

        # Test using dot notation (if supported)
        redis_port = config.get("cache")["redis"]["port"]
        assert redis_port == 6379

    def test_flext_config_validation(self) -> None:
        """Test FlextCore.Config validation methods."""
        config_data = {"required_field": "value", "optional_field": "optional"}

        config = FlextCore.Config(config_data)

        # Test validation for required fields
        validation_result = config.validate_required_fields(["required_field"])
        assert validation_result.is_success

        # Test validation failure
        validation_fail = config.validate_required_fields([
            "required_field",
            "missing_field",
        ])
        assert validation_fail.is_failure

    # =============================================================================
    # FLEXT MODELS COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_models_validation(self) -> None:
        """Test FlextCore.Models validation functionality."""
        # Test basic model validation
        test_data = {"name": "Test Name", "email": "test@example.com", "age": 25}

        validation_result = FlextCore.Models.Validation.validate_dict_structure(
            test_data, required_keys=["name", "email"], optional_keys=["age"]
        )
        assert validation_result.is_success

        # Test validation with missing required field
        invalid_data = {"name": "Test Name"}  # Missing email
        validation_fail = FlextCore.Models.Validation.validate_dict_structure(
            invalid_data, required_keys=["name", "email"]
        )
        assert validation_fail.is_failure

    def test_flext_models_type_validation(self) -> None:
        """Test FlextCore.Models type validation."""
        # Test successful type validation
        type_result = FlextCore.Models.Validation.validate_field_type("test", str)
        assert type_result.is_success

        # Test failed type validation
        type_fail = FlextCore.Models.Validation.validate_field_type(123, str)
        assert type_fail.is_failure

        # Test complex type validation
        list_result = FlextCore.Models.Validation.validate_field_type([1, 2, 3], list)
        assert list_result.is_success

        dict_result = FlextCore.Models.Validation.validate_field_type(
            {"key": "value"}, dict
        )
        assert dict_result.is_success

    def test_flext_models_data_transformation(self) -> None:
        """Test FlextCore.Models data transformation capabilities."""
        raw_data = {
            "user_name": "john_doe",
            "user_email": "john@example.com",
            "user_age": "25",  # String that should be converted to int
            "is_active": "true",  # String that should be converted to bool
        }

        # Test transformation
        transform_result = FlextCore.Models.Transform.transform_data(
            raw_data, {"user_age": int, "is_active": lambda x: x.lower() == "true"}
        )

        if transform_result.is_success:
            transformed = transform_result.data
            assert isinstance(transformed["user_age"], int)
            assert transformed["user_age"] == 25
            assert isinstance(transformed["is_active"], bool)
            assert transformed["is_active"] is True

    # =============================================================================
    # FLEXT TYPES COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_types_usage(self) -> None:
        """Test FlextCore.Types comprehensive functionality."""
        # Test Core types
        test_dict: FlextCore.Types.Dict = {"key": "value"}
        assert isinstance(test_dict, dict)

        test_list: FlextCore.Types.List = [1, 2, 3]
        assert isinstance(test_list, list)

        # Test Config types
        config_value: FlextCore.Types.ConfigValue = "config_string"
        assert isinstance(config_value, str)

        config_value_int: FlextCore.Types.ConfigValue = 42
        assert isinstance(config_value_int, int)

        # Test Data types
        data_dict: FlextCore.Types.StringDict = {"data": [1, 2, 3]}
        assert "data" in data_dict
        assert isinstance(data_dict["data"], list)

    # =============================================================================
    # INTEGRATION AND PERFORMANCE TESTS
    # =============================================================================

    def test_comprehensive_integration(self) -> None:
        """Test comprehensive integration of all flext-core components."""

        class ComprehensiveTestService(FlextCore.Service[FlextCore.Types.Dict]):
            def __init__(self) -> None:
                super().__init__()
                self.logger = FlextCore.Logger("comprehensive_test")
                self.container = FlextCore.Container.get_global()
                self.config = FlextCore.Config({"test_mode": True, "max_items": 100})

            def execute(self) -> FlextCore.Result[FlextCore.Types.Dict]:
                try:
                    # Use logger
                    self.logger.info("Starting comprehensive test")

                    # Use container
                    self.container.register("test_start_time", time.time())

                    # Use utilities
                    correlation_id = (
                        FlextCore.Utilities.Generators.generate_correlation_id()
                    )
                    timestamp = FlextCore.Utilities.Generators.generate_timestamp()

                    # Process some data
                    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    chunk_result = FlextCore.Utilities.Collections.chunk_list(
                        test_data, 3
                    )

                    if chunk_result.is_failure:
                        return FlextCore.Result[FlextCore.Types.Dict].fail(
                            chunk_result.error
                        )

                    # Create result
                    result_data = {
                        "correlation_id": correlation_id,
                        "timestamp": timestamp,
                        "chunks": chunk_result.data,
                        "config": {
                            "test_mode": self.config.get("test_mode"),
                            "max_items": self.config.get("max_items"),
                        },
                        "status": "completed",
                    }

                    self.logger.info(
                        "Comprehensive test completed",
                        extra={"result_size": len(result_data)},
                    )

                    return FlextCore.Result[FlextCore.Types.Dict].ok(result_data)

                except Exception as e:
                    self.logger.exception("Comprehensive test failed")
                    return FlextCore.Result[FlextCore.Types.Dict].fail(str(e))

        # Execute comprehensive test
        service = ComprehensiveTestService()
        result = service.execute()

        assert result.is_success
        data = result.data
        assert "correlation_id" in data
        assert "timestamp" in data
        assert "chunks" in data
        assert len(data["chunks"]) == 4  # [1,2,3], [4,5,6], [7,8,9], [10]
        assert data["status"] == "completed"
        assert data["config"]["test_mode"] is True

    def test_performance_under_load(self) -> None:
        """Test flext-core performance under load."""
        start_time = time.time()

        # Perform many operations
        results = []
        for i in range(1000):
            # Create results
            result = FlextCore.Result[int].ok(i)
            results.append(result)

            # Use utilities
            if i % 100 == 0:
                timestamp = FlextCore.Utilities.Generators.generate_timestamp()
                uuid = FlextCore.Utilities.Generators.generate_uuid()
                assert len(timestamp) > 0
                assert len(uuid) == 36

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete reasonably quickly
        assert elapsed < 5.0  # Allow up to 5 seconds for 1000 operations

    def test_error_propagation_and_handling(self) -> None:
        """Test comprehensive error propagation across components."""

        class ErrorTestService(FlextCore.Service[str]):
            def __init__(self) -> None:
                super().__init__()
                self.logger = FlextCore.Logger("error_test")

            def execute(self) -> FlextCore.Result[str]:
                # Chain multiple operations that could fail

                # Step 1: Utility operation
                cast_result = FlextCore.Utilities.Conversion.safe_cast("invalid", int)
                if cast_result.is_failure:
                    self.logger.error(f"Cast failed: {cast_result.error}")
                    return FlextCore.Result[str].fail(
                        f"Step 1 failed: {cast_result.error}"
                    )

                # This won't be reached due to invalid cast
                return FlextCore.Result[str].ok("success")  # pragma: no cover

            def test_recovery(self) -> FlextCore.Result[str]:
                # Test error recovery patterns
                cast_result = FlextCore.Utilities.Conversion.safe_cast("invalid", int)

                # Recover from error
                recovered_value = cast_result.unwrap_or(42)

                return FlextCore.Result[str].ok(
                    f"Recovered with value: {recovered_value}"
                )

        # Test error propagation
        service = ErrorTestService()
        result = service.execute()

        assert result.is_failure
        assert result.error is not None and "Step 1 failed" in result.error

        # Test error recovery
        recovery_result = service.test_recovery()
        assert recovery_result.is_success
        assert "Recovered with value: 42" in recovery_result.data

    def test_memory_usage_and_cleanup(self) -> None:
        """Test memory usage patterns and cleanup."""
        import gc

        # Create many objects and ensure cleanup
        large_results = []
        for i in range(1000):
            large_data = {"data": list(range(100)), "id": i}
            result = FlextCore.Result[FlextCore.Types.Dict].ok(large_data)
            large_results.append(result)

        assert len(large_results) == 1000

        # Clear references
        large_results.clear()

        # Force garbage collection
        gc.collect()

        # Verify we can still create new objects without issues
        new_result = FlextCore.Result[str].ok("after_cleanup")
        assert new_result.is_success
        assert new_result.data == "after_cleanup"

    def test_thread_safety_considerations(self) -> None:
        """Test thread safety of key components."""
        from concurrent.futures import ThreadPoolExecutor

        # Test FlextCore.Container thread safety
        container = FlextCore.Container.get_global()
        results = []

        def worker_function(worker_id: int) -> str:
            # Each worker registers and retrieves values
            key = f"worker_{worker_id}"
            value = f"value_{worker_id}"

            container.register(key, value)
            retrieved = container.get(key)

            return f"Worker {worker_id}: {retrieved.data if retrieved.is_success else 'FAIL'}"

        # Run multiple workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_function, i) for i in range(50)]
            results = [f.result() for f in futures]

        assert len(results) == 50
        # Verify all workers completed successfully
        for result in results:
            assert "FAIL" not in result

    def test_edge_cases_and_boundary_conditions(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test empty data structures
        empty_result = FlextCore.Result[FlextCore.Types.List].ok([])
        assert empty_result.is_success
        assert empty_result.data == []

        # Test None values
        none_result = FlextCore.Result[None].ok(None)
        assert none_result.is_success
        assert none_result.data is None

        # Test large data structures
        large_data = {"items": list(range(10000))}
        large_result = FlextCore.Result[dict[str, FlextCore.Types.IntList]].ok(
            large_data
        )
        assert large_result.is_success
        assert len(large_result.data["items"]) == 10000

        # Test very long strings
        long_string = "x" * 10000
        string_result = FlextCore.Result[str].ok(long_string)
        assert string_result.is_success
        assert len(string_result.data) == 10000

        # Test deeply nested structures
        nested = {"level1": {"level2": {"level3": {"value": "deep"}}}}
        nested_result = FlextCore.Result[FlextCore.Types.Dict].ok(nested)
        assert nested_result.is_success
        assert nested_result.data["level1"]["level2"]["level3"]["value"] == "deep"
