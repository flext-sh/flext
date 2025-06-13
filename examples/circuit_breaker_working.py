#!/usr/bin/env python3
"""Working example of circuit breaker with py-breaker.

This demonstrates proper usage of py-breaker with sync/async functions.
"""

import random
import time
from typing import Any

import pybreaker


class UnreliableAPI:
    """Simulates an unreliable external API."""

    def __init__(self, failure_rate: float = 0.7) -> None:
        self.failure_rate = failure_rate
        self.call_count = 0
        self.success_count = 0
        self.fail_count = 0

    def fetch_user_sync(self, user_id: int) -> dict[str, Any]:
        """Synchronous version for circuit breaker."""
        self.call_count += 1

        # Simulate processing
        time.sleep(0.05)

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


def main() -> None:
    """Demonstrate circuit breaker with synchronous calls."""
    # Create unreliable API
    api = UnreliableAPI(failure_rate=0.8)  # 80% failure rate

    # Configure circuit breaker
    breaker = pybreaker.CircuitBreaker(
        fail_max=3,
        reset_timeout=5,
        name="api_breaker",
    )

    # Decorate the API call
    protected_fetch = breaker(api.fetch_user_sync)

    # Track state changes
    states = []

    class StateListener:
        def __init__(self, states_list) -> None:
            self.states = states_list

        def before_call(self, cb, func, *args, **kwargs) -> None:
            pass

        def on_success(self, cb, result) -> None:
            pass

        def on_failure(self, cb, exc) -> None:
            pass

        def state_change(self, cb, old_state, new_state) -> None:
            self.states.append((old_state, new_state))
            if new_state == pybreaker.STATE_OPEN or (new_state == pybreaker.STATE_CLOSED and old_state != pybreaker.STATE_CLOSED) or new_state == pybreaker.STATE_HALF_OPEN:
                pass

    listener = StateListener(states)
    breaker.add_listener(listener)

    # Make multiple calls

    for i in range(12):

        try:
            protected_fetch(i)
        except pybreaker.CircuitBreakerError:
            pass
        except ConnectionError:
            pass
        except Exception:
            pass

        # Show stats periodically
        if i % 4 == 3:
            pass

        time.sleep(0.2)

    # Wait for recovery
    time.sleep(5)

    # Test recovery
    api.failure_rate = 0.2  # Reduce failure rate to 20%

    for i in range(5):
        try:
            protected_fetch(100 + i)
        except pybreaker.CircuitBreakerError:
            pass
        except ConnectionError:
            pass

        time.sleep(0.3)

    # Final report
    if api.call_count > 0:
        pass

    # Show state history
    if states:
        for _old, _new in states:
            pass


if __name__ == "__main__":
    main()
