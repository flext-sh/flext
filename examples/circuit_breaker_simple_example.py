#!/usr/bin/env python3
"""Simple example of using py-breaker circuit breaker.

This example demonstrates the circuit breaker pattern without
the complexity of the full FLX adapter infrastructure.
"""

import asyncio
import random
from typing import Any

import pybreaker


class UnreliableAPI:
    """Simulates an unreliable external API."""

    def __init__(self, failure_rate: float = 0.7) -> None:
        self.failure_rate = failure_rate
        self.call_count = 0
        self.success_count = 0
        self.fail_count = 0

    async def fetch_user(self, user_id: int) -> dict[str, Any]:
        """Fetch user data with random failures."""
        self.call_count += 1

        # Simulate network delay
        await asyncio.sleep(0.1)

        # Random failures
        if random.random() < self.failure_rate:
            self.fail_count += 1
            msg = f"API unavailable for user {user_id}"
            raise ConnectionError(msg)

        self.success_count += 1
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
        }


class ResilientService:
    """Service with circuit breaker protection."""

    def __init__(self, api: UnreliableAPI) -> None:
        self.api = api

        # Configure circuit breaker with listeners
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=3,          # Open after 3 failures
            reset_timeout=5,     # Try recovery after 5 seconds
            name="api_breaker",
            listeners=[self._on_state_change],
        )

    def _on_state_change(self, cb, old_state, new_state) -> None:
        """Called when circuit state changes."""
        if new_state == pybreaker.STATE_OPEN or (new_state == pybreaker.STATE_CLOSED and old_state != pybreaker.STATE_CLOSED) or new_state == pybreaker.STATE_HALF_OPEN:
            pass

    async def get_user(self, user_id: int) -> dict[str, Any]:
        """Get user with circuit breaker protection."""
        try:
            # Wrap the async call with circuit breaker
            @self.breaker
            async def protected_call():
                return await self.api.fetch_user(user_id)

            return await protected_call()

        except pybreaker.CircuitBreakerError:
            # Circuit is open - return fallback
            return {
                "id": user_id,
                "name": f"Cached User {user_id}",
                "email": f"cached{user_id}@example.com",
                "cached": True,
            }
        except Exception as e:
            # Other errors - return error response
            return {
                "id": user_id,
                "error": str(e),
            }


async def main() -> None:
    """Demonstrate circuit breaker behavior."""
    # Create unreliable API
    api = UnreliableAPI(failure_rate=0.8)  # 80% failure rate
    service = ResilientService(api)

    # Make multiple calls to trigger circuit breaker
    for i in range(15):

        await service.get_user(i)

        # Show stats

        await asyncio.sleep(0.5)

    await asyncio.sleep(5)

    # Try again after recovery timeout

    for i in range(5):
        await service.get_user(100 + i)
        await asyncio.sleep(0.3)

    # Final stats


if __name__ == "__main__":
    asyncio.run(main())
