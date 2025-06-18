#!/usr/bin/env python3
"""Example of using circuit breaker with FLX adapters.

This example demonstrates how to use the simplified circuit breaker
mixin with py-breaker backend for resilient service communication.
"""

import asyncio
import random
from typing import Any

from flx.adapters.base import BaseAdapter
from flx.adapters.mixins.circuit_breaker_simple import CircuitBreakerHealthMixin
from flx.infra.adapters.circuit_breaker_adapter import create_circuit_breaker_factory
from flx.utils.logging import get_logger

logger = get_logger(__name__)


class UnreliableService:
    """Simulates an unreliable external service."""

    def __init__(self, failure_rate: float = 0.3) -> None:
        self.failure_rate = failure_rate
        self.call_count = 0

    async def fetch_data(self, id: str) -> dict[str, Any]:
        """Simulate fetching data with random failures."""
        self.call_count += 1

        # Simulate network delay
        await asyncio.sleep(0.1)

        # Random failures
        if random.random() < self.failure_rate:
            msg = f"Failed to fetch data for {id}"
            raise ConnectionError(msg)

        return {
            "id": id,
            "data": f"Sample data for {id}",
            "call_count": self.call_count,
        }


class ResilientAdapter(BaseAdapter, CircuitBreakerHealthMixin):
    """Example adapter with circuit breaker protection."""

    # Circuit breaker configuration
    circuit_breaker_failure_threshold: int = 3  # Open after 3 failures
    circuit_breaker_recovery_timeout: int = 5  # Try recovery after 5 seconds

    def __init__(self, service: UnreliableService, **kwargs) -> None:
        # Inject circuit breaker factory
        self._circuit_breaker_factory = create_circuit_breaker_factory()

        super().__init__(name="resilient", **kwargs)
        self._service = service

    async def _connect(self) -> None:
        """Connect to the service."""
        logger.info("Connecting to unreliable service")

    async def _disconnect(self) -> None:
        """Disconnect from the service."""
        logger.info("Disconnecting from unreliable service")

    async def _health_check(self) -> dict[str, object]:
        """Perform health check."""
        # Circuit breaker health is handled by the mixin
        return {
            "service_calls": self._service.call_count,
            "service_available": not self.is_circuit_open(),
        }

    async def _perform_health_check_operation(self) -> dict[str, Any]:
        """Perform health check operation."""
        # Get base health check
        health_info = await self._health_check()

        # Add circuit breaker info from mixin
        health_info.update(await super()._perform_health_check_operation())

        return health_info

    async def fetch_data(self, id: str) -> dict[str, Any]:
        """Fetch data with circuit breaker protection."""
        try:
            # Use circuit breaker to protect the call
            return await self.with_circuit_breaker(
                self._service.fetch_data,
                id,
            )
        except Exception as e:
            logger.exception(f"Failed to fetch data: {e}")
            # Return fallback response
            return {
                "id": id,
                "data": "Fallback data",
                "error": str(e),
                "circuit_state": self.circuit_breaker_state,
            }


async def demonstrate_circuit_breaker() -> None:
    """Demonstrate circuit breaker behavior."""
    # Create unreliable service
    service = UnreliableService(failure_rate=0.7)  # 70% failure rate

    # Create adapter with circuit breaker
    adapter = ResilientAdapter(service)

    async with adapter:

        # Make multiple calls to trigger circuit breaker
        for i in range(10):

            # Check circuit state

            # Try to fetch data
            await adapter.fetch_data(f"item_{i}")

            # Show metrics

            # Small delay between calls
            await asyncio.sleep(0.5)

        await adapter.health_check()

        # Wait for circuit recovery
        await asyncio.sleep(5)

        # Try again after recovery
        await adapter.fetch_data("recovery_test")


async def demonstrate_manual_control() -> None:
    """Demonstrate manual circuit breaker control."""
    service = UnreliableService(failure_rate=0.9)  # 90% failure rate
    adapter = ResilientAdapter(service)

    async with adapter:

        # Force some failures
        for i in range(5):
            await adapter.fetch_data(f"test_{i}")

        if adapter.is_circuit_open():
            adapter.reset_circuit_breaker()

        # Try again
        await adapter.fetch_data("after_reset")


if __name__ == "__main__":

    # Run demonstrations
    asyncio.run(demonstrate_circuit_breaker())
    asyncio.run(demonstrate_manual_control())
