"""Example: FLX Async Infrastructure Usage with Flexible Brokers.

This example demonstrates how to use the FLX async infrastructure with
different message brokers (Redis, RabbitMQ, or in-memory).
"""

import asyncio
import importlib
import os
from uuid import uuid4

from flx.core import (
    flx_get_broker_info,
    flx_get_health_status,
)

flx_async = importlib.import_module('flx.infrastructure.async')


async def main() -> None:
    """Demonstrate async infrastructure usage."""
    print("🚀 FLX Async Infrastructure Demo")
    print("=" * 50)

    # Show current broker configuration
    broker_info = flx_get_broker_info()
    print(f"📡 Current Broker: {broker_info['broker_type']}")
    print(f"📊 Broker Class: {broker_info['broker_class']}")
    print(f"🔄 Result Backend: {'✅' if broker_info['has_result_backend'] else '❌'}")
    print()

    # Initialize command bus
    bus = flx_async.FlxAsyncCommandBus()

    # Check health status
    health = flx_get_health_status()
    print(f"💚 Health Status: {health}")
    print()

    # Example 1: Send command asynchronously (fire-and-forget)
    print("📤 Example 1: Async Command (Fire-and-Forget)")
    command = flx_async.FlxCreateResourceCommand(
        resource_name="demo-api",
        resource_type="REST",
        priority=2,  # Medium priority
    )

    message_id = await bus.send_command(command)
    print(f"   ✅ Command sent: {message_id}")
    print()

    # Example 2: Send command with result waiting (if backend available)
    print("📥 Example 2: Command with Result Backend")
    if broker_info["has_result_backend"]:
        print("   🔄 Result backend available - can wait for results")
        sync_command = flx_async.FlxCreateResourceCommand(
            resource_name="sync-resource",
            resource_type="database",
            priority=1,  # High priority
            timeout_seconds=5,  # Wait up to 5 seconds
        )

        try:
            result = await bus.send_command(sync_command)
            print(f"   ✅ Command result: {result}")
        except TimeoutError:
            print("   ⏰ Command timed out")
    else:
        print("   ℹ️  In-memory broker - all commands are fire-and-forget")
        async_command = flx_async.FlxCreateResourceCommand(
            resource_name="another-resource",
            resource_type="cache",
            priority=3,
        )
        message_id = await bus.send_command(async_command)
        print(f"   ✅ Message ID returned: {message_id}")
    print()

    # Example 3: Queue statistics
    print("📊 Example 3: Queue Statistics")
    stats = bus.get_queue_stats()
    for queue_name, queue_stats in stats.items():
        status = "🟢 Empty" if queue_stats["empty"] else f"🔵 {queue_stats['length']} items"
        print(f"   {queue_name}: {status}")
    print()

    # Example 4: Event creation (for reference)
    print("📢 Example 4: Domain Event Creation")
    event = flx_async.FlxResourceCreatedEvent(
        aggregate_id=uuid4(),
        aggregate_type="Resource",
        resource_id=uuid4(),
        resource_name="demo-api",
        resource_type="REST",
        created_by="demo-user",
    )
    print(f"   ✅ Event created: {event.event_name}")
    print(f"   📝 Resource ref: {event.resource_reference}")
    print()


def configure_broker_examples() -> None:
    """Show different broker configuration examples."""
    print("🔧 Broker Configuration Examples")
    print("=" * 50)

    print("1. Auto-Detection (Padrão - Recomendado):")
    print("   # Sem configuração ou:")
    print("   export FLX_BROKER_TYPE=auto")
    print("   # Tenta Redis primeiro, fallback para in-memory")
    print()

    print("2. Redis Explícito (Configuração Específica):")
    print("   export FLX_BROKER_TYPE=redis")
    print("   export REDIS_HOST=redis-server")
    print("   export REDIS_PORT=6380")
    print("   export REDIS_PASSWORD=secret")
    print()

    print("3. In-Memory Forçado (Testes):")
    print("   export FLX_BROKER_TYPE=stub")
    print("   # Força in-memory mesmo com Redis disponível")
    print()

    print("4. RabbitMQ (Enterprise):")
    print("   export FLX_BROKER_TYPE=rabbitmq")
    print("   export RABBITMQ_HOST=rabbit-cluster")
    print("   export RABBITMQ_PORT=5672")
    print("   export RABBITMQ_USER=REDACTED_LDAP_BIND_PASSWORD")
    print("   export RABBITMQ_PASSWORD=REDACTED_LDAP_BIND_PASSWORD123")
    print()


if __name__ == "__main__":
    # Show configuration examples
    configure_broker_examples()

    # Run demonstration
    print("Current Configuration:")
    configured_type = os.getenv('FLX_BROKER_TYPE', 'auto (default)')
    print(f"FLX_BROKER_TYPE = {configured_type}")
    print()

    # Run async demo
    asyncio.run(main())

    print("🎉 Demo completed successfully!")
    print("\nAuto-Detection Strategy:")
    print("✅ Default behavior tries Redis first (localhost:6379)")
    print("✅ Falls back to in-memory if Redis not available")
    print("✅ Install Redis anytime to get automatic performance boost:")
    print("   sudo apt install redis-server  # Linux")
    print("   brew install redis            # macOS")
    print("   docker run -d -p 6379:6379 redis:latest  # Docker")
