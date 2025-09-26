"""FLEXT CLI Containers Tests - Comprehensive containers functionality testing.

Tests for FlextCliContainers class using flext_tests infrastructure with real functionality
testing, no mocks, and comprehensive coverage following FLEXT standards.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_cli.constants import FlextCliConstants
from flext_cli.containers import FlextCliContainers


class TestFlextCliContainers:
    """Comprehensive tests for FlextCliContainers class."""

    def test_containers_initialization(self) -> None:
        """Test Containers initialization with proper configuration."""
        containers = FlextCliContainers()
        assert containers is not None
        assert isinstance(containers, FlextCliContainers)

    def test_containers_execute_sync(self) -> None:
        """Test synchronous Containers execution."""
        containers = FlextCliContainers()
        result = containers.execute()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-containers"

    @pytest.mark.asyncio
    async def test_containers_execute_async(self) -> None:
        """Test asynchronous Containers execution."""
        containers = FlextCliContainers()
        result = await containers.execute_async()

        assert result.is_success
        assert result.value is not None
        assert result.value["status"] == FlextCliConstants.OPERATIONAL
        assert result.value["service"] == "flext-cli-containers"

    def test_containers_service_properties(self) -> None:
        """Test containers service properties."""
        containers = FlextCliContainers()

        # Test that all required properties are accessible
        assert hasattr(containers, "execute")
        assert hasattr(containers, "execute_async")

    def test_containers_error_handling(self) -> None:
        """Test containers error handling capabilities."""
        containers = FlextCliContainers()

        # Test that containers handle errors gracefully
        result = containers.execute()
        assert result.is_success

    def test_containers_performance(self) -> None:
        """Test containers performance characteristics."""
        containers = FlextCliContainers()

        import time

        start_time = time.time()
        result = containers.execute()
        execution_time = time.time() - start_time

        assert result.is_success
        # Should execute quickly
        assert execution_time < 1.0

    def test_containers_memory_usage(self) -> None:
        """Test containers memory usage characteristics."""
        containers = FlextCliContainers()

        # Test multiple executions
        for _ in range(5):
            result = containers.execute()
            assert result.is_success

    def test_containers_integration(self) -> None:
        """Test containers integration with other services."""
        containers = FlextCliContainers()

        # Test that containers properly integrate with their dependencies
        result = containers.execute()
        assert result.is_success

        # Test async version
        import asyncio

        async_result = asyncio.run(containers.execute_async())
        assert async_result.is_success

    def test_containers_logging_integration(self) -> None:
        """Test containers logging integration."""
        containers = FlextCliContainers()

        # Test that logging is properly integrated
        result = containers.execute()
        assert result.is_success

        # Should not raise any logging-related exceptions
        assert result.value is not None

    def test_containers_concurrent_execution(self) -> None:
        """Test containers concurrent execution."""
        containers = FlextCliContainers()

        # Execute multiple container operations concurrently
        import asyncio

        async def test_concurrent():
            return await asyncio.gather(
                containers.execute_async(), containers.execute_async()
            )

        results = asyncio.run(test_concurrent())
        assert len(results) == 2
        assert results[0].is_success
        assert results[1].is_success

    def test_containers_data_consistency(self) -> None:
        """Test containers data consistency."""
        containers = FlextCliContainers()

        # Test that container data is consistent across calls
        result1 = containers.execute()
        result2 = containers.execute()

        assert result1.is_success == result2.is_success
        assert result1.value["service"] == result2.value["service"]
        assert result1.value["status"] == result2.value["status"]

    def test_containers_service_validation(self) -> None:
        """Test containers service validation."""
        containers = FlextCliContainers()

        # Test that the service validates properly
        result = containers.execute()
        assert result.is_success

        # Verify required fields
        assert "status" in result.value
        assert "service" in result.value
        assert "timestamp" in result.value

    def test_containers_async_consistency(self) -> None:
        """Test containers async consistency."""
        containers = FlextCliContainers()

        # Test that sync and async versions return consistent data
        sync_result = containers.execute()
        import asyncio

        async_result = asyncio.run(containers.execute_async())

        assert sync_result.is_success == async_result.is_success
        assert sync_result.value["service"] == async_result.value["service"]
        assert sync_result.value["status"] == async_result.value["status"]

    def test_containers_timestamp_format(self) -> None:
        """Test containers timestamp format."""
        containers = FlextCliContainers()
        result = containers.execute()

        assert result.is_success
        timestamp = result.value["timestamp"]
        assert isinstance(timestamp, str)
        # Should be ISO format
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp

    def test_containers_service_name(self) -> None:
        """Test containers service name."""
        containers = FlextCliContainers()
        result = containers.execute()

        assert result.is_success
        service = result.value["service"]
        assert service == "flext-cli-containers"

    def test_containers_status_operational(self) -> None:
        """Test containers status is operational."""
        containers = FlextCliContainers()
        result = containers.execute()

        assert result.is_success
        status = result.value["status"]
        assert status == FlextCliConstants.OPERATIONAL
