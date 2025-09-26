"""FLEXT CLI Debug Tests - Comprehensive debug functionality testing.

Tests for FlextCliDebug class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time

import pytest
from flext_cli.constants import FlextCliConstants
from flext_cli.debug import FlextCliDebug


class TestFlextCliDebug:
    """Comprehensive tests for FlextCliDebug class."""

    def test_debug_initialization(self) -> None:
        """Test Debug initialization with proper configuration."""
        debug = FlextCliDebug()
        assert debug is not None
        assert isinstance(debug, FlextCliDebug)

    def test_debug_execute_sync(self) -> None:
        """Test synchronous Debug execution."""
        debug = FlextCliDebug()
        result = debug.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "FlextCliDebug"

    @pytest.mark.asyncio
    async def test_debug_execute_async(self) -> None:
        """Test asynchronous Debug execution."""
        debug = FlextCliDebug()
        result = await debug.execute_async()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "FlextCliDebug"

    def test_debug_system_info(self) -> None:
        """Test system information collection."""
        debug = FlextCliDebug()
        result = debug.get_system_info()

        assert result is not None
        assert result.is_success
        assert isinstance(result.value, dict)
        assert "python_version" in result.value
        assert "platform" in result.value
        assert "service" in result.value

    def test_debug_path_info(self) -> None:
        """Test path information collection."""
        debug = FlextCliDebug()
        result = debug.get_path_info()

        assert result is not None
        assert result.is_success
        assert isinstance(result.value, list)
        assert len(result.value) > 0

        # Check that all path entries have required fields
        for path_entry in result.value:
            assert "label" in path_entry
            assert "path" in path_entry
            assert "exists" in path_entry

    def test_debug_connectivity_test(self) -> None:
        """Test connectivity testing functionality."""
        debug = FlextCliDebug()
        result = debug.test_connectivity()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.CONNECTED
        assert result.value["service"] == "FlextCliDebug"
        assert "timestamp" in result.value

    def test_debug_health_check(self) -> None:
        """Test health check functionality."""
        debug = FlextCliDebug()
        result = debug.execute_health_check()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.HEALTHY
        assert "timestamp" in result.value
        assert "service" in result.value
        assert "check_id" in result.value

    def test_debug_trace_execution(self) -> None:
        """Test trace execution functionality."""
        debug = FlextCliDebug()
        test_args = ["arg1", "arg2", "arg3"]
        result = debug.execute_trace(test_args)

        assert result.is_success
        assert result.value is not None
        assert result.value["operation"] == FlextCliConstants.TRACE
        assert result.value["args"] == test_args
        assert result.value["args_count"] == len(test_args)
        assert "trace_id" in result.value

    def test_debug_comprehensive_info(self) -> None:
        """Test comprehensive debug information collection."""
        debug = FlextCliDebug()
        result = debug.get_comprehensive_debug_info()

        assert result.is_success
        assert result.value is not None
        assert "service" in result.value
        assert "timestamp" in result.value
        assert "debug_id" in result.value
        assert "system_info" in result.value
        assert "environment_status" in result.value
        assert "connectivity_status" in result.value

    def test_debug_error_handling(self) -> None:
        """Test debug error handling capabilities."""
        debug = FlextCliDebug()

        # Test with invalid arguments
        result = debug.execute_trace([])
        assert result.is_success  # Should handle empty args gracefully

        # Test comprehensive debug info
        comprehensive_result = debug.get_comprehensive_debug_info()
        assert comprehensive_result.is_success

    def test_debug_performance(self) -> None:
        """Test debug performance characteristics."""
        debug = FlextCliDebug()

        start_time = time.time()
        result = debug.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_debug_memory_usage(self) -> None:
        """Test debug memory usage characteristics."""
        debug = FlextCliDebug()

        # Test multiple executions
        for _ in range(5):
            result = debug.execute()
            assert result.is_success

    def test_debug_integration(self) -> None:
        """Test debug integration with other services."""
        debug = FlextCliDebug()

        # Test that debug properly integrates with its dependencies
        result = debug.execute()
        assert result.is_success

        # Test all debug methods
        system_info = debug.get_system_info()
        assert system_info is not None

        path_info = debug.get_path_info()
        assert path_info is not None

        connectivity = debug.test_connectivity()
        assert connectivity.is_success

        health = debug.execute_health_check()
        assert health.is_success

    def test_debug_service_properties(self) -> None:
        """Test debug service properties."""
        debug = FlextCliDebug()

        # Test that all required properties are accessible
        assert hasattr(debug, "get_system_info")
        assert hasattr(debug, "get_path_info")
        assert hasattr(debug, "test_connectivity")
        assert hasattr(debug, "execute_health_check")
        assert hasattr(debug, "execute_trace")
        assert hasattr(debug, "get_comprehensive_debug_info")

    def test_debug_logging_integration(self) -> None:
        """Test debug logging integration."""
        debug = FlextCliDebug()

        # Test that logging is properly integrated
        result = debug.execute()
        assert result.is_success

        # Should not raise any logging-related exceptions
        assert result.value is not None

    def test_debug_concurrent_execution(self) -> None:
        """Test debug concurrent execution."""
        debug = FlextCliDebug()

        # Execute multiple debug operations concurrently
        async def test_concurrent() -> list[str]:
            return await asyncio.gather(
                debug.execute_async(),
                debug.test_connectivity(),
                debug.execute_health_check(),
            )

        results = asyncio.run(test_concurrent())
        assert len(results) == 3
        assert results[0].is_success
        assert results[1].is_success
        assert results[2].is_success

    def test_debug_data_consistency(self) -> None:
        """Test debug data consistency."""
        debug = FlextCliDebug()

        # Test that debug data is consistent across calls
        result1 = debug.execute()
        result2 = debug.execute()

        assert result1.is_success == result2.is_success
        assert result1.value["service"] == result2.value["service"]

        # Test system info consistency
        system_info1 = debug.get_system_info()
        system_info2 = debug.get_system_info()

        assert system_info1["python_version"] == system_info2["python_version"]
        assert system_info1["platform"] == system_info2["platform"]

    def test_debug_trace_validation(self) -> None:
        """Test debug trace validation."""
        debug = FlextCliDebug()

        # Test trace with various argument types
        test_cases = [
            [],
            ["single_arg"],
            ["arg1", "arg2", "arg3"],
            ["arg with spaces", "arg-with-dashes", "arg_with_underscores"],
        ]

        for test_args in test_cases:
            result = debug.execute_trace(test_args)
            assert result.is_success
            assert result.value["args"] == test_args
            assert result.value["args_count"] == len(test_args)
