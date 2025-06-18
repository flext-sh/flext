#!/usr/bin/env python3
"""
Simple test to verify FLX core functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flx.config import Settings
from flx.event_bus import EventBus


async def test_event_bus():
    """Test basic event bus functionality."""
    print("🔍 Testing FLX Event Bus...")

    # Create event bus
    event_bus = EventBus()

    # Start event bus
    await event_bus.start()
    print("✅ Event bus started")

    # Subscribe to test event
    received_events = []

    async def handler(event):
        received_events.append(event)
        print(f"📨 Received event: {event}")

    await event_bus.subscribe("test.event", handler)
    print("✅ Subscribed to test.event")

    # Publish test event
    test_event = {
        "type": "test.event",
        "data": {"message": "Hello from FLX!"},
    }

    await event_bus.publish("test.event", test_event)
    print("✅ Published test event")

    # Wait a bit for async processing
    await asyncio.sleep(0.1)

    # Check if event was received
    if received_events:
        print(f"✅ Event received successfully: {received_events[0]}")
    else:
        print("❌ No event received")

    # Stop event bus
    await event_bus.stop()
    print("✅ Event bus stopped")

    return len(received_events) > 0


async def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing FLX Configuration...")

    settings = Settings()
    print(f"✅ Environment: {settings.environment}")
    print(f"✅ gRPC Port: {settings.grpc_port}")
    print(f"✅ Database URL: {settings.database_url}")

    return True


async def main():
    """Run all tests."""
    print("🚀 FLX Core Simple Test")
    print("=" * 40)

    tests = [
        ("Configuration", test_config),
        ("Event Bus", test_event_bus),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed: {e}")
            results.append((name, False))

    print("\n📊 Test Results:")
    print("=" * 40)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
