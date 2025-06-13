"""Example: FLX Async Infrastructure Usage with Flexible Brokers.

This example demonstrates how to use the FLX async infrastructure with
different message brokers (Redis, RabbitMQ, or in-memory).
"""

import asyncio
import contextlib
import importlib
import os
from uuid import uuid4

from flx.core import (
    flx_get_broker_info,
    flx_get_health_status,
)

flx_async = importlib.import_module("flx.infrastructure.async")


async def main() -> None:
    """Demonstrate async infrastructure usage."""
    # Show current broker configuration
    broker_info = flx_get_broker_info()

    # Initialize command bus
    bus = flx_async.FlxAsyncCommandBus()

    # Check health status
    flx_get_health_status()

    # Example 1: Send command asynchronously (fire-and-forget)
    command = flx_async.FlxCreateResourceCommand(
        resource_name="demo-api",
        resource_type="REST",
        priority=2,  # Medium priority
    )

    await bus.send_command(command)

    # Example 2: Send command with result waiting (if backend available)
    if broker_info["has_result_backend"]:
        sync_command = flx_async.FlxCreateResourceCommand(
            resource_name="sync-resource",
            resource_type="database",
            priority=1,  # High priority
            timeout_seconds=5,  # Wait up to 5 seconds
        )

        with contextlib.suppress(TimeoutError):
            await bus.send_command(sync_command)
    else:
        async_command = flx_async.FlxCreateResourceCommand(
            resource_name="another-resource",
            resource_type="cache",
            priority=3,
        )
        await bus.send_command(async_command)

    # Example 3: Queue statistics
    stats = bus.get_queue_stats()
    for queue_stats in stats.values():
        "🟢 Empty" if queue_stats["empty"] else f"🔵 {queue_stats['length']} items"

    # Example 4: Event creation (for reference)
    flx_async.FlxResourceCreatedEvent(
        aggregate_id=uuid4(),
        aggregate_type="Resource",
        resource_id=uuid4(),
        resource_name="demo-api",
        resource_type="REST",
        created_by="demo-user",
    )


def configure_broker_examples() -> None:
    """Show different broker configuration examples."""


if __name__ == "__main__":
    # Show configuration examples
    configure_broker_examples()

    # Run demonstration
    configured_type = os.getenv("FLX_BROKER_TYPE", "auto (default)")

    # Run async demo
    asyncio.run(main())
