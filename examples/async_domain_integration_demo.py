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

import structlog

# Set up environment for demo
os.environ["FLX_BROKER_TYPE"] = "auto"  # Auto-detect Redis or fall back to in-memory

from flx.core import (
    FlxAggregateRoot,
    FlxEntityFactory,
    FlxGetResource,
    flx_create_application,
    flx_get_broker_info,
    flx_get_health_status,
)


async def demo_aggregate_async_events() -> None:
    """Demo: Aggregate Root with Async Events."""
    print("\n🏗️  DEMO 1: Aggregate Root with Async Events")
    print("=" * 60)

    # Create aggregate root with async events enabled
    print("📝 Creating aggregate root with async events...")
    order_aggregate = FlxEntityFactory.create_aggregate_root(
        name="CustomerOrder",
        description="A customer order aggregate",
        metadata={"customer_id": "CUST_123", "order_type": "ONLINE"},
        use_async_events=True,
    )

    print(f"✅ Created aggregate: {order_aggregate.name} (ID: {order_aggregate.id})")
    print(f"📊 Initial async events: {order_aggregate.async_domain_event_count}")

    # Business operations that generate events
    print("\n🔄 Performing business operations...")

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
    print(
        f"📈 Total async events accumulated: {order_aggregate.async_domain_event_count}",
    )

    async_events = order_aggregate.get_async_domain_events()
    print("\n📋 Async Events Generated:")
    for i, event in enumerate(async_events, 1):
        print(f"   {i}. {event.event_name} (Aggregate: {event.aggregate_type})")
        print(f"      Data: {event.event_data}")

    # Simulate processing completion
    print("\n✅ Simulating event processing completion...")
    order_aggregate.mark_events_as_committed()
    print(f"📊 Events after commit: {order_aggregate.total_event_count}")


async def demo_mixed_events() -> None:
    """Demo: Mixing Regular and Async Events."""
    print("\n🔀 DEMO 2: Mixed Regular and Async Events")
    print("=" * 60)

    # Create aggregate that uses both types of events
    inventory_aggregate = FlxAggregateRoot(name="InventoryItem")

    print("📝 Adding mixed event types...")

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
    print(f"📊 Regular domain events: {inventory_aggregate.domain_event_count}")
    print(f"📊 Async domain events: {inventory_aggregate.async_domain_event_count}")
    print(f"📊 Total events: {inventory_aggregate.total_event_count}")

    # Show both types
    regular_events, async_events = inventory_aggregate.get_all_events()

    print("\n📋 Regular Events:")
    for event in regular_events:
        print(f"   • {event.event_type}: {event.event_data}")

    print("\n📋 Async Events:")
    for event in async_events:
        print(f"   • {event.event_name}: {event.event_data}")


async def demo_lato_integration() -> None:
    """Demo: Integration with Lato Application."""
    print("\n🎯 DEMO 3: Lato Application Integration")
    print("=" * 60)

    try:
        # Create FLX application with async infrastructure
        print("🚀 Creating FLX application with async infrastructure...")
        app = flx_create_application(
            name="AsyncDomainDemo",
            bind_dependencies=True,
            include_modules=True,
        )

        print("✅ Application created successfully")

        # Test command execution through Lato
        print("\n📤 Executing command through Lato...")

        async with app.transaction_context() as ctx:
            # Create a test command
            command = FlxGetResource(
                resource_name="orders",
                resource_id="ORDER_123",
                fields=["id", "status", "customer_id"],
            )

            # Execute command
            result = ctx.execute(command)
            print(f"✅ Command executed: {result}")

            # Access injected dependencies
            logger = ctx.dependency_provider.get("logger")
            logger.info(
                "Command executed successfully", command_type=type(command).__name__,
            )

    except Exception as e:
        print(f"⚠️  Lato integration demo skipped: {e}")


async def demo_async_infrastructure_status() -> None:
    """Demo: Async Infrastructure Status."""
    print("\n📡 DEMO 4: Async Infrastructure Status")
    print("=" * 60)

    # Show broker information
    broker_info = flx_get_broker_info()
    print("📊 Broker Configuration:")
    for key, value in broker_info.items():
        print(f"   {key}: {value}")

    # Show health status
    health = flx_get_health_status()
    print("\n💚 Health Status:")
    for key, value in health.items():
        if key == "queues" and isinstance(value, dict):
            print(f"   {key}:")
            for queue_name, queue_stats in value.items():
                status = (
                    "🟢 Empty"
                    if queue_stats.get("empty")
                    else f"🔵 {queue_stats.get('length', 0)} items"
                )
                print(f"      {queue_name}: {status}")
        else:
            print(f"   {key}: {value}")


async def demo_event_factory() -> None:
    """Demo: Async Event Factory."""
    print("\n🏭 DEMO 5: Async Event Factory")
    print("=" * 60)

    from uuid import uuid4

    # Create async domain event using factory
    print("🔧 Creating async domain event using factory...")

    event = FlxEntityFactory.create_async_domain_event(
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

    print(f"✅ Event created: {event.event_name}")
    print("📋 Event details:")
    print(f"   Aggregate Type: {event.aggregate_type}")
    print(f"   Aggregate ID: {event.aggregate_id}")
    print(f"   Version: {event.version}")
    print(f"   Data: {event.event_data}")


async def main() -> None:
    """Run all demos."""
    print("🚀 FLX ASYNC DOMAIN INTEGRATION DEMO")
    print("=" * 80)

    try:
        await demo_aggregate_async_events()
        await demo_mixed_events()
        await demo_lato_integration()
        await demo_async_infrastructure_status()
        await demo_event_factory()

        print("\n🎉 All demos completed successfully!")
        print("\n📚 Key Takeaways:")
        print("   ✅ Domain entities can raise async events seamlessly")
        print("   ✅ Mixed regular and async events work together")
        print("   ✅ Lato application integrates with async infrastructure")
        print("   ✅ Auto-detection works (Redis or in-memory fallback)")
        print("   ✅ Factory methods support both event types")
        print("   ✅ Zero breaking changes - existing code still works")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
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
