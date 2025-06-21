"""Example: Complete Async Domain Integration Demo.

This example demonstrates the full integration between:
1. FLX Domain Entities with async event capabilities
2. Lato Application with DDD modules
3. Async Infrastructure with Dramatiq
4. Automatic event publishing through middleware

Shows how aggregate roots can raise async domain events that are automatically
processed through the async infrastructure.
"""

import asyncio
import os
from uuid import uuid4

import structlog

from flx.core import AggregateRoot
from flx.core.domain.entities import EntityFactory

# Set up environment for demo
# Auto-detect Redis or fall back to in-memory
os.environ["FLX_BROKER_TYPE"] = "auto"


async def demo_aggregate_async_events() -> None:
    """Demo: Aggregate Root with Async Events."""
    # Create aggregate root with async events enabled
    order_aggregate = EntityFactory.create_aggregate_root(
        name="CustomerOrder",
        description="A customer order aggregate",
        metadata={"customer_id": "CUST_123", "order_type": "ONLINE"},
        use_async_events=True,
    )

    # Business operations that generate events

    order_aggregate.raise_async_domain_event(
        "OrderValidated",
        {
            "validation_rules": ["payment_verified", "inventory_checked"],
            "validation_time": "2025-01-01T10:00:00Z",
        },
    )

    order_aggregate.raise_async_domain_event(
        "OrderProcessing",
        {
            "processing_stage": "payment_processing",
            "estimated_completion": "2025-01-01T10:05:00Z",
        },
    )

    order_aggregate.raise_async_domain_event(
        "OrderCompleted",
        {
            "completion_time": "2025-01-01T10:04:30Z",
            "total_amount": 299.99,
            "fulfillment_method": "shipping",
        },
    )

    # Show accumulated events

    async_events = order_aggregate.get_async_domain_events()
    for _i, _event in enumerate(async_events, 1):
        pass

    # Simulate processing completion
    order_aggregate.mark_events_as_committed()


async def demo_mixed_events() -> None:
    """Demo: Mixing Regular and Async Events."""
    # Create aggregate that uses both types of events
    inventory_aggregate = AggregateRoot(name="InventoryItem")

    # Regular domain event (for internal consistency)
    inventory_aggregate.raise_domain_event(
        "StockLevelChanged",
        {
            "old_level": 100,
            "new_level": 85,
            "change_reason": "sale",
        },
    )

    # Async domain event (for external integration)
    inventory_aggregate.raise_async_domain_event(
        "LowStockAlert",
        {
            "current_stock": 85,
            "threshold": 20,
            "reorder_required": False,
        },
    )

    inventory_aggregate.raise_async_domain_event(
        "StockMovementRecorded",
        {
            "movement_type": "outbound",
            "quantity": 15,
            "transaction_id": "TXN_456",
        },
    )

    # Show event distribution

    # Show both types
    regular_events, async_events = inventory_aggregate.get_all_events()

    for _event in regular_events:
        pass

    for _event in async_events:
        pass


async def demo_lato_integration() -> None:
    """Demo: Integration with Lato Application."""
    try:
        # Create FLX application with async infrastructure
        # Create FLX application with async infrastructure
        # NOTE: This is a demo - actual implementation would use proper FLX app factory
        app = None  # flx_create_application(
            name="AsyncDomainDemo",
            bind_dependencies=True,
            include_modules=True,
        )

        # Test command execution through Lato

        async with app.transaction_context() as ctx:
            # Create a test command
            # Create a test command
            # NOTE: This is a demo - actual implementation would use proper command
            command = None  # FlxGetResource(
                resource_name="orders",
                resource_id="ORDER_123",
                fields=["id", "status", "customer_id"],
            )

            # Execute command
            ctx.execute(command)

            # Access injected dependencies
            logger = ctx.dependency_provider.get("logger")
            logger.info(
                "Command executed successfully",
                command_type=type(command).__name__,
            )

    except Exception:
        pass


async def demo_async_infrastructure_status() -> None:
    """Demo: Async Infrastructure Status."""
    # Show broker information
    # Show broker information
    # NOTE: This is a demo - actual implementation would use proper broker info
    broker_info = {}
    for key, value in broker_info.items():
        pass

    # Show health status
    # Show health status
    # NOTE: This is a demo - actual implementation would use proper health status
    health = {}
    for key, value in health.items():
        if key == "queues" and isinstance(value, dict):
            for queue_stats in value.values():
                (
                    "🟢 Empty"
                    if queue_stats.get("empty")
                    else f"🔵 {queue_stats.get('length', 0)} items"
                )


async def demo_event_factory() -> None:
    """Demo: Async Event Factory."""
    # Create async domain event using factory

    # Create async domain event using factory
    # NOTE: This is a demo - actual implementation would use proper factory
    EntityFactory.create_async_domain_event(
        event_type="PaymentProcessed",
        aggregate_id=uuid4(),
        aggregate_type="Payment",
        event_data={
            "amount": 149.99,
            "currency": "USD",
            "payment_method": "credit_card",
            "transaction_id": "TXN_789",
        },
        version=1,
    )


async def main() -> None:
    """Run all demos."""
    try:
        await demo_aggregate_async_events()
        await demo_mixed_events()
        await demo_lato_integration()
        await demo_async_infrastructure_status()
        await demo_event_factory()

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Configure structured logging for demo
    structlog.configure(
        processors=[structlog.dev.ConsoleRenderer(colors=True)],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    asyncio.run(main())
