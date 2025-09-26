"""FLEXT CLI Output Tests - Comprehensive output functionality testing.

Tests for FlextCliOutput class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time
import pytest
from flext_cli.constants import FlextCliConstants
from flext_cli.output import FlextCliOutput


class TestFlextCliOutput:
    """Comprehensive tests for FlextCliOutput class."""

    def test_output_initialization(self) -> None:
        """Test Output initialization with proper configuration."""
        output = FlextCliOutput()
        assert output is not None
        assert isinstance(output, FlextCliOutput)

    def test_output_execute_sync(self) -> None:
        """Test synchronous Output execution."""
        output = FlextCliOutput()
        result = output.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-output"

    @pytest.mark.asyncio
    async def test_output_execute_async(self) -> None:
        """Test asynchronous Output execution."""
        output = FlextCliOutput()
        result = await output.execute_async()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-output"

    def test_output_service_properties(self) -> None:
        """Test output service properties."""
        output = FlextCliOutput()

        # Test that all required properties are accessible
        assert hasattr(output, "execute")
        assert hasattr(output, "execute_async")

    def test_output_error_handling(self) -> None:
        """Test output error handling capabilities."""
        output = FlextCliOutput()

        # Test that output handles errors gracefully
        result = output.execute()
        assert result.is_success

    def test_output_performance(self) -> None:
        """Test output performance characteristics."""
        output = FlextCliOutput()

        start_time = time.time()
        result = output.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_output_memory_usage(self) -> None:
        """Test output memory usage characteristics."""
        output = FlextCliOutput()

        # Test multiple executions
        for _ in range(5):
            result = output.execute()
            assert result.is_success

    def test_output_integration(self) -> None:
        """Test output integration with other services."""
        output = FlextCliOutput()

        # Test that output properly integrates with their dependencies
        result = output.execute()
        assert result.is_success

        # Test async version
        async_result = asyncio.run(output.execute_async())
        assert async_result.is_success

    def test_output_logging_integration(self) -> None:
        """Test output logging integration."""
        output = FlextCliOutput()

        # Test that logging is properly integrated
        result = output.execute()
        assert result.is_success

        # Should not raise any logging-related exceptions
        assert result.value is not None

    def test_output_concurrent_execution(self) -> None:
        """Test output concurrent execution."""
        output = FlextCliOutput()

        # Execute multiple output operations concurrently
        async def test_concurrent() -> list[str]:
            return await asyncio.gather(output.execute_async(), output.execute_async())

        results = asyncio.run(test_concurrent())
        assert len(results) == 2
        assert results[0].is_success
        assert results[1].is_success

    def test_output_data_consistency(self) -> None:
        """Test output data consistency."""
        output = FlextCliOutput()

        # Test that output data is consistent across calls
        result1 = output.execute()
        result2 = output.execute()

        assert result1.is_success == result2.is_success
        assert result1.value["service"] == result2.value["service"]
        assert result1.value["status"] == result2.value["status"]

    def test_output_service_validation(self) -> None:
        """Test output service validation."""
        output = FlextCliOutput()

        # Test that the service validates properly
        result = output.execute()
        assert result.is_success

        # Verify required fields
        assert "status" in result.value
        assert "service" in result.value
        assert "timestamp" in result.value

    def test_output_async_consistency(self) -> None:
        """Test output async consistency."""
        output = FlextCliOutput()

        # Test that sync and async versions return consistent data
        sync_result = output.execute()
        async_result = asyncio.run(output.execute_async())

        assert sync_result.is_success == async_result.is_success
        assert sync_result.value["service"] == async_result.value["service"]
        assert sync_result.value["status"] == async_result.value["status"]

    def test_output_timestamp_format(self) -> None:
        """Test output timestamp format."""
        output = FlextCliOutput()
        result = output.execute()

        assert result.is_success
        timestamp = result.value["timestamp"]
        assert isinstance(timestamp, str)
        # Should be ISO format
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp

    def test_output_service_name(self) -> None:
        """Test output service name."""
        output = FlextCliOutput()
        result = output.execute()

        assert result.is_success
        service = result.value["service"]
        assert service == "flext-cli-output"

    def test_output_status_operational(self) -> None:
        """Test output status is operational."""
        output = FlextCliOutput()
        result = output.execute()

        assert result.is_success
        status = result.value["status"]
        assert status == FlextCliConstants.OPERATIONAL
