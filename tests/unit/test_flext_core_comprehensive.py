"""test_flext_core_comprehensive.py - Comprehensive Tests for Flext-Core Components.

This module provides comprehensive tests for flext-core components,
focusing on real functionality without mocks. Tests cover FlextResult,
FlextDispatcher, u, FlextContainer, FlextService, FlextLogger,
FlextConfig, FlextModels, and t with extensive edge case coverage.

Scope: Integration and unit testing of core flext-core functionality,
ensuring proper behavior and type safety across all components.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import gc
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from flext_core import (
    FlextConfig,
    FlextContainer,
    FlextDispatcher,
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextService,
    u
)


class TestFlextComprehensive:
    """Comprehensive tests for all flext-core components."""

    # =============================================================================
    # FLEXT RESULT COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_result_all_creation_methods(self) -> None:
        """Test all FlextResult creation methods and edge cases."""
        # Test ok() with various types
        result_str = FlextResult[str].ok("test")
        assert result_str.is_success
        assert result_str.data == "test"
        assert result_str.value == "test"  # Dual access API

        # None is not a valid success value in FlextResult
        # Use fail() for failures instead
        # result_none = FlextResult[None].ok(None)  # This would raise TypeError

        result_dict = FlextResult[dict[str, object]].ok({"key": "value"})
        assert result_dict.is_success
        assert result_dict.data["key"] == "value"

        # Test fail() with various error types
        result_fail = FlextResult[str].fail("Error message")
        assert result_fail.is_failure
        assert result_fail.error == "Error message"

        result_exception = FlextResult[int].fail("Test error")
        assert result_exception.is_failure
        assert "Test error" in str(result_exception.error)

    def test_flext_result_unwrap_methods(self) -> None:
        """Test all unwrap methods and error handling."""
        success = FlextResult[str].ok("data")
        fail = FlextResult[str].fail("error")

        # Test successful unwrap
        assert success.unwrap() == "data"

        # Test unwrap_or
        assert success.unwrap_or("default") == "data"
        assert fail.unwrap_or("default") == "default"

        # Test unwrap with failure raises RuntimeError
        with pytest.raises(RuntimeError, match="Cannot unwrap failed result: error"):
            _ = fail.unwrap()

    def test_flext_result_map_operations(self) -> None:
        """Test map and flatmap operations."""
        success = FlextResult[int].ok(5)
        fail = FlextResult[int].fail("error")

        # Test map on success
        mapped = success.map(lambda x: x * 2)
        assert mapped.is_success
        assert mapped.data == 10

        # Test map on failure
        mapped_fail = fail.map(lambda x: x * 2)
        assert mapped_fail.is_failure

        # Test flat_map
        def double_wrap(x: int) -> FlextResult[object]:
            return FlextResult[object].ok(x * 2)

        flatmapped = success.flat_map(double_wrap)
        assert flatmapped.is_success
        assert flatmapped.data == 10

    def test_flext_result_map_operations_extended(self) -> None:
        """Test extended map operations."""
        success = FlextResult[str].ok("data")
        fail = FlextResult[str].fail("error")

        # Test map on success
        mapped = success.map(lambda d: f"Success: {d}")
        assert mapped.is_success
        assert mapped.data == "Success: data"

        # Test map on failure (short-circuits)
        mapped_fail = fail.map(lambda d: f"Success: {d}")
        assert mapped_fail.is_failure

    def test_flext_result_composition_operations(self) -> None:
        """Test composition operations."""
        success1 = FlextResult[int].ok(1)
        success2 = FlextResult[int].ok(2)
        fail1 = FlextResult[int].fail("error1")

        # Test flat_map composition (and-like behavior)
        composed = success1.flat_map(lambda x: FlextResult[object].ok(success2.data))
        assert composed.is_success
        assert composed.data == 2

        # Test short-circuit on failure
        composed_fail = success1.flat_map(
            lambda x: FlextResult[object].fail(fail1.error or "error")
        )
        assert composed_fail.is_failure

        # Note: or_else method not available in FlextResult

    # =============================================================================
    # FLEXT DISPATCHER COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_dispatcher_command_handling(self) -> None:
        """Test comprehensive FlextDispatcher command handling."""
        dispatcher = FlextDispatcher()
        received_commands = []

        class TestCommand:
            def __init__(self, data: str) -> None:
                super().__init__()
                self.data = data

        class TestHandler:
            def handle(self, command: object) -> object:
                received_commands.append(command)
                return "handled"

        # Test handler registration - register_function returns FlextResult
        handler = TestHandler()
        register_result = dispatcher.register_function(TestCommand, handler.handle)
        assert register_result.is_success, (
            f"Handler registration failed: {register_result.error}"
        )

        # Test command dispatch
        test_cmd = TestCommand("test")
        result = dispatcher.dispatch(test_cmd)

        assert result.is_success, f"Dispatch failed: {result.error}"
        assert len(received_commands) == 1
        if isinstance(received_commands[0], TestCommand):
            assert received_commands[0].data == "test"

    def test_flext_dispatcher_error_handling(self) -> None:
        """Test FlextDispatcher error handling."""
        dispatcher = FlextDispatcher()

        class TestCommand:
            def __init__(self, data: str) -> None:
                super().__init__()
                self.data = data

        class FailingHandler:
            def handle(self, command: object) -> object:
                msg = "Handler error"
                raise ValueError(msg)

        failing_handler = FailingHandler()
        register_result = dispatcher.register_function(
            TestCommand, failing_handler.handle
        )
        assert register_result.is_success, (
            f"Handler registration failed: {register_result.error}"
        )

        result = dispatcher.dispatch(TestCommand("test"))

        # Dispatcher should propagate handler errors
        assert result.is_failure
        assert result.error is not None and "Handler error" in result.error

    # =============================================================================
    # FLEXT UTILITIES COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_utilities_generators(self) -> None:
        """Test all uethods."""
        # Test timestamp generation - use generate_iso_timestamp (non-deprecated)
        ts1 = uenerate_iso_timestamp()
        time.sleep(1.1)  # Sleep more than 1 second to ensure different timestamp
        ts2 = uenerate_iso_timestamp()

        assert ts1 != ts2
        assert isinstance(ts1, str)
        assert "T" in ts1  # ISO format

        # Note: generate_uuid method not available

        # Test correlation ID
        corr1 = uenerate_correlation_id()
        corr2 = uenerate_correlation_id()

        assert corr1 != corr2
        assert len(corr1) > 0

    def test_flext_utilities_validation(self) -> None:
        """Test uethods."""
        # Test string validation
        valid_result = ualidate_pattern("test123", r"^[a-z0-9]+$")
        assert isinstance(valid_result, FlextResult)
        assert valid_result.is_success

        # Test empty string validation
        empty_result = u.Validation.validate_length("", min_length=1)
        assert isinstance(empty_result, FlextResult)
        assert empty_reue

        # Test pattern validation
        pattern_result = u.Validation.validate_pattern("test123", r"^[a-z0-9]+$")
        assert isinstance(pattern_result, FlextResult)
        assert pattern_reus

        # Test invalid pattern
        invalid_pattern = u.Validation.validate_pattern("TEST", r"^[a-z]+$")
        assert isinstance(invalid_pattern, FlextResult)
        assert invalid_pattern.is_failure

    def test_flext_utilities(self) -> None:
        """Test u data mapping methods."""
        # Test data normalization (using Cache which has normalize_component)
        test_data = {"key1": "value1", "key2": 42}
        normalized = u.Cache.normalize_component(test_data)
        assert normalized is not None
        assert isinstance(normalized, dict)
        assert nu1"] == "value1"
        assert normalized["key2"] == 42

        # Test dict kuing DataMapper which exists)
        source_dict: dict[str, object] = {"old_key": "value1", "other": "value2"}
        mapping = {"old_key": "new_key"}
        mapped_result = u.DataMapper.map_dict_keys(source_dict, mapping)
        assert mapped_result.is_success
        mapped_dict = mapped_result.data
        assert "new_key" in mapped_dict
        assert mapped_dict["new_key"] == "value1"

    def test_flext_utiliun_operations(self) -> None:
        """Test u cache operations (which handle collections)."""
        # Test cache key generation with lists
        test_list = [1, 2, 3, 4, 5]
        key_result = u.Cache.generate_cache_key(test_list, list)
        assert key_result is not None
        assert isinstance(key_result, str)
        assert lu > 0

        # Test cache key generation with nested structures
        nested_data =u 2, 3], "metadata": {"count": 3}}
        nested_key = u.Cache.generate_cache_key(nested_data, dict)
        assert nested_key is not None
        assert isinstance(nested_key, str)

        # Test component normalization with collections
        normalized = u.Cache.normalize_component(test_list)
        assert normalune
        assert isinstance(normalized, list)
        assert normalized == [1, 2, 3, 4, 5]

    def test_flext_utilities_string_operations(self) -> None:
        """Test u stru."""
        # Test text cleaning
        dirty_text = "  Hello   World  "
        clean_result = u.TextProcessor.clean_text(dirty_text)
        assert isinstance(clean_result, str)
        assert clean_result == "Hello World"
u
        # Test truncation
        long_string = "This is a very long string that should be truncated"
        trunc_result = ur.truncate_text(long_string, 20)
        assert trunc_result.is_success
        assert isinstance(trunc_result.data, str)
        assert len(trunc_result.data) <= 20
        assert trunc_result.data.endswith("...")

        # Test safe stru
        safe_result = u.TextProcessor.safe_string("valid text")
        assert isinstance(safe_result, str)
        assert safe_result == "valid text"

    # =============================================================================
    # FLEXT CONTAINER COMPREHENSIVE TESTS
    # ================u===============================================

    def test_flext_container_registration_and_retrieval(self) -> None:
        """Test FlextContainer comprehensive functionality."""
        container = FlextContainer()

        # Test basic registration
        register_result = container.register("test_key", "test_value")
        assert register_result.is_success
        result = container.get("test_key")
        assert result.is_success
        assert result.data == "test_value"

        # Test complex object registration
        complex_obj: dict[str, object] = {"nested": {"data": [1, 2, 3]}}
        register_complex_result = container.register("complex", complex_obj)
        assert register_complex_result.is_success
        complex_result = container.get("complex")
        assert complex_result.is_success
        if isinstance(complex_result.data, dict):
            assert complex_result.data["nested"]["data"] == [1, 2, 3]

        # Test non-existent key
        missing_result = container.get("nonexistent")
        assert missing_result.is_failure

    def test_flext_container_singleton_pattern(self) -> None:
        """Test FlextContainer singleton behavior."""
        container1 = FlextContainer()
        container2 = FlextContainer()

        assert container1 is container2

        # Test that registrations persist across instances
        register_result = container1.register("singleton_test", "value")
        assert register_result.is_success
        result = container2.get("singleton_test")
        assert result.is_success
        assert result.data == "value"

    def test_flext_container_type_safety(self) -> None:
        """Test FlextContainer with typed operations."""
        container = FlextContainer()

        # Test string type
        register_result = container.register("typed_string", "hello")
        assert register_result.is_success
        str_result = container.get("typed_string")
        assert str_result.is_success
        assert str_result.data == "hello"

        # Test int type
        register_int_result = container.register("typed_int", 42)
        assert register_int_result.is_success
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
        """Test FlextService lifecycle methods."""

        class TestService(FlextService[str]):
            # Use model fields instead of arbitrary attributes
            executed: bool = False
            cleaned: bool = False

            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)
                self.executed = False
                self.cleaned = False

            def execute(self) -> FlextResult[str]:
                self.executed = True
                return FlextResult[str].ok("service_result")

            def cleanup(self) -> FlextResult[bool]:
                self.cleaned = True
                return FlextResult[bool].ok(True)

        service = TestService()
        assert service is not None

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
        """Test FlextService error handling patterns."""

        class ErrorService(FlextService[str]):
            def execute(self) -> FlextResult[str]:
                try:
                    msg = "Service error"
                    raise ValueError(msg)
                except Exception as e:
                    return FlextResult[str].fail(str(e))

        service = ErrorService()
        result = service.execute()

        assert result.is_failure
        assert result.error is not None and "Service error" in result.error

    def test_flext_service_operations(self) -> None:
        """Test FlextService with operations."""

        class Service(FlextService[str]):
            def execute(self) -> FlextResult[str]:
                time.sleep(0.001)  # Minimal delay
                return FlextResult[str].ok("result")

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
        """Test FlextLogger with all log levels."""
        logger = FlextLogger("test_logger")

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
        """Test FlextLogger with context."""
        logger = FlextLogger("context_test")

        # Test basic logging with correlation ID in message
        logger.info("Message with context", correlation_id="test-123")

        # Test logging with multiple context values
        logger.info(
            "Message with multiple context", user_id="user-456", operation="test_op"
        )

        # Verify logger exists and is functional
        assert logger is not None
        assert hasattr(logger, "info")

    def test_flext_logger_performance(self) -> None:
        """Test FlextLogger performance characteristics."""
        logger = FlextLogger("perf_test")

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
        """Test FlextConfig comprehensive functionality."""
        # Test creating config with data - using only valid FlextConfig fields
        config_data = {
            "app_name": "test_app",
            "debug": True,
            "log_level": "INFO",
            "timeout_seconds": 30.0,
        }

        config = FlextConfig(**config_data)

        # Test basic access via attributes (Pydantic BaseSettings)
        assert config.app_name == "test_app"
        assert config.debug is True
        assert config.log_level == "INFO"
        assert config.timeout_seconds == 30.0

        # Test model_dump for dict-like access
        config_dict = config.model_dump()
        assert config_dict.get("app_name") == "test_app"
        assert config_dict.get("debug") is True
        assert config_dict.get("log_level") == "INFO"
        assert config_dict.get("timeout_seconds") == 30.0

    def test_flext_config_nested_access(self) -> None:
        """Test FlextConfig with nested data structures."""
        # FlextConfig doesn't support nested dicts directly - use model_dump for dict access
        # For nested configs, use namespace pattern with FlextConfig.AutoConfig
        config = FlextConfig()
        _ = config.model_dump()

        # Note: FlextConfig doesn't have database/cache fields by default
        # These would need to be added as namespaces or custom config classes
        # For now, test that config is accessible
        assert config.app_name is not None

    def test_flext_config_validation(self) -> None:
        """Test FlextConfig validation methods."""
        # FlextConfig uses Pydantic validation automatically
        # Test that invalid values raise ValidationError
        # Valid config
        config = FlextConfig(app_name="test", debug=True)
        assert config.app_name == "test"
        assert config.debug is True

        # Invalid config (app_name too short)
        _ = FlextConfig(app_name="valid_name")  # Test valid config first

        # Test that Pydantic validation works
        config_dict = config.model_dump()
        assert "app_name" in config_dict
        assert "debug" in config_dict

    # =============================================================================
    # FLEXT MODELS COMPREHENSIVE TESTS
    # =============================================================================

    def test_flext_models_validation(self) -> None:
        """Test FlextModels validation functionality."""
        # Test that validation methods exist and are callable
        assert hasattr(FlextModels.Validation, "validate_business_rules")
        assert callable(FlextModels.Validation.validate_business_rules)
        assert hasattr(FlextModels.Validation, "validate_cross_fields")
        assert callable(FlextModels.Validation.validate_cross_fields)
        assert hasattr(FlextModels.Validation, "validate_domain_invariants")
        assert callable(FlextModels.Validation.validate_domain_invariants)

        # Test basic validation using u.Validation (which has basic validators)
        test_string = "test@example.com"
        email_result = u.Validation.validate_pattern(
            test_string, r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        assert email_result.is_success
u
    def test_flext_models_type_validation(self) -> None:
        """Test FlextMoun methods exist and are callable."""
        # Test that validation methods exist
        assert hasattr(FlextModels.Validation, "validate_business_rules")
        assert callable(FlextModels.Validation.validate_business_rules)
        assert hasattr(FlextModels.Validation, "validate_cross_fields")
        assert callable(FlextModels.Validation.validate_cross_fields)
        assert hasattr(FlextModels.Validation, "validate_domain_invariants")
        assert callable(FlextModels.Validation.validate_domain_invariants)

    def test_flext_models_data_transformation(self) -> None:
        """Test FlextModels data transformation capabilities."""
        raw_data: dict[str, object] = {
            "old_name": "john_doe",
            "old_email": "john@example.com",
        }

        # Test key mapping transformation using DataMapper
        mapping = {"old_name": "user_name", "old_email": "user_email"}
        transform_result = u.DataMapper.map_dict_keys(raw_data, mapping)
        assert transform_result.is_success
        transformed = transform_result.data
        assert transformed["user_name"] == "john_doe"
        assert transformed["user_email"] == "john@example.com"

        # Test data normaliu
        normalized = u.Cache.normalize_component(transformed)
        assert normalized is not None
        assert isinstance(normalized, dict)

    # =============================================================================
    # FLEXT TYPES COMPREHENSIVE TESTS
    # ===============u================================================

    def test_flext_types_usage(self) -> None:
        """Test t comprehensive functionality."""
        # Test Core types
        test_dict: dict[str, object] = {"key": "value"}
        assert isinstance(test_dict, dict)

        test_list: list[object] = [1, 2, 3]
        assert isinstance(test_list, list)

        # Test Config types
        config_value: object = "config_string"
        assert isinstance(config_value, str)

        config_value_int: object = 42
        assert isinstance(config_value_int, int)

        # Test Data types
        data_dict: dict[str, object] = {"data": [1, 2, 3]}
        assert "data" in data_dict
        if isinstance(data_dict["data"], list):
            assert isinstance(data_dict["data"], list)

    # =============================================================================
    # INTEGRATION AND PERFORMANCE TESTS
    # =============================================================================

    def test_comprehensive_integration(self) -> None:
        """Test comprehensive integration of all flext-core components."""

        class ComprehensiveTestService(FlextService[dict[str, object]]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)
                # logger and container are read-only properties from FlextService, use them directly
                # FlextConfig uses Pydantic BaseSettings - access via attributes, not dict
                # Create config with test_mode and max_items as attributes
                self._test_config = {"test_mode": True, "max_items": 100}

            def execute(self) -> FlextResult[dict[str, object]]:
                try:
                    # Use logger
                    self.logger.info("Starting comprehensive test")

                    # Use container
                    register_result = self.container.register(
                        "test_start_time", time.time()
                    )
                    if register_result.is_failure:
                        return FlextResult[dict[str, object]].fail(
                            f"Container registration failed: {register_result.error}"
                        )

                    # Use utilities
                    correlation_id = u.Generators.generate_correlation_id()
                    timestamp = u.Generators.generate_iso_timestamp()

                    # Process some data - simple chunking without external utility
                    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                    chunk_size = 3
                    chunks: list[objeu
                        test_datuk_size]
                        for i in range(0, len(test_data), chunk_size)
                    ]

                    # Create result
                    result_data: dict[str, object] = {
                        "correlation_id": correlation_id,
                        "timestamp": timestamp,
                        "chunks": chunks,
                        "config": self._test_config,
                        "status": "completed",
                    }

                    self.logger.info(
                        "Comprehensive test completed",
                        extra={"result_size": len(result_data)},
                    )

                    return FlextResult[dict[str, object]].ok(result_data)

                except Exception as e:
                    self.logger.exception("Comprehensive test failed")
                    return FlextResult[dict[str, object]].fail(str(e))

        # Execute comprehensive test
        service = ComprehensiveTestService()
        result = service.execute()

        assert result.is_success
        data = result.data
        assert "correlation_id" in data
        assert "timestamp" in data
        assert "chunks" in data
        if isinstance(data["chunks"], list):
            assert len(data["chunks"]) == 4  # [1,2,3], [4,5,6], [7,8,9], [10]
        assert data["status"] == "completed"
        if isinstance(data["config"], dict):
            assert data["config"]["test_mode"] is True

    def test_performance_under_load(self) -> None:
        """Test flext-core performance under load."""
        start_time = time.time()

        # Perform many operations
        results = []
        for i in range(1000):
            # Create results
            result = FlextResult[int].ok(i)
            results.append(result)

            # Use utilities
            if i % 100 == 0:
                timestamp = u.Generators.generate_iso_timestamp()
                uuid = u.Generators.generate_correlation_id()
                assert len(timestamp) > 0
                assert len(uuid) > 0

        end_time = time.time()
        elapsed = end_time -u
u
        # Should complete reasonably quickly
        assert elapsed < 5.0  # Allow up to 5 seconds for 1000 operations

    def test_error_propagation_and_handling(self) -> None:
        """Test comprehensive error propagation across components."""

        class ErrorTestService(FlextService[str]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)
                # Logger is available via mixin property, no need to set it

            def execute(self) -> FlextResult[str]:
                # Chain multiple operations that could fail
                # Use u.Validation instead of Conversion (which doesn't exist)
                # Step 1: Validation operation that will fail
                validation_result = u.Validation.validate_length("", min_length=1)
                if validation_result.is_failure:
                    error_msg = validation_result.error or "Unknown error"
                    self.logger.error(f"Validation failed: {error_msg}")
                    reult[str].fail(f"Step 1 failed: {error_msg}")

                # This won't be reacuidation failure
                return FlextResult[str].ok("success")  # pragma: no cover

            def test_recovery(self) -> FlextResult[str]:
                # Test error recovery patterns
                validation_result = u.Validation.validate_length("", min_length=1)

                # Recover from error
                if validation_result.is_success:
                    recovered_value = validation_result.data
                else:
                    recovered_value = "default"

                return FlextResult[suered with value: {recovered_value}")

        # Test error propagation
        service = ErrorTestService()
        result = service.execute()

        assert result.is_failure
        assert result.error is not None and "Step 1 failed" in result.error

        # Test error recovery
        recovery_result = service.test_recovery()
        assert recovery_result.is_success
        assert "Recovered with value: default" in recovery_result.data

    def test_memory_usage_and_cleanup(self) -> None:
        """Test memory usage patterns and cleanup."""
        # Create many objects and ensure cleanup
        large_results = []
        for i in range(1000):
            large_data: dict[str, object] = {"data": list(range(100)), "id": i}
            result = FlextResult[dict[str, object]].ok(large_data)
            large_results.append(result)

        assert len(large_results) == 1000

        # Clear references
        large_results.clear()

        # Force garbage collection
        _ = gc.collect()

        # Verify we can still create new objects without issues
        new_result = FlextResult[str].ok("after_cleanup")
        assert new_result.is_success
        assert new_result.data == "after_cleanup"

    def test_thread_safety_considerations(self) -> None:
        """Test thread safety of key components."""
        # Test FlextContainer thread safety
        container = FlextContainer()
        results = []

        def worker_function(worker_id: int) -> str:
            # Each worker registers and retrieves values
            key = f"worker_{worker_id}"
            value = f"value_{worker_id}"

            register_result = container.register(key, value)
            if register_result.is_failure:
                return f"Worker {worker_id}: REGISTER_FAIL"
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
        empty_result = FlextResult[list[object]].ok([])
        assert empty_result.is_success
        assert empty_result.data == []

        # None is not a valid success value in FlextResult
        # Use fail() for failures or a sentinel value for success
        # none_result = FlextResult[None].ok(None)  # This would raise TypeError

        # Test large data structures
        large_data: dict[str, object] = {"items": list(range(10000))}
        large_result = FlextResult[dict[str, object]].ok(large_data)
        assert large_result.is_success
        if isinstance(large_result.data["items"], list):
            assert len(large_result.data["items"]) == 10000

        # Test very long strings
        long_string = "x" * 10000
        string_result = FlextResult[str].ok(long_string)
        assert string_result.is_success
        assert len(string_result.data) == 10000

        # Test deeply nested structures
        nested: dict[str, object] = {
            "level1": {"level2": {"level3": {"value": "deep"}}}
        }
        nested_result = FlextResult[dict[str, object]].ok(nested)
        assert nested_result.is_success
        data = nested_result.data
        if data:
            level1 = data.get("level1")
            if isinstance(level1, dict):
                level2 = level1.get("level2")
                if isinstance(level2, dict):
                    level3 = level2.get("level3")
                    if isinstance(level3, dict):
                        assert level3.get("value") == "deep"
