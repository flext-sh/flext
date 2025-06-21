#!/usr/bin/env python3
"""Test file to verify mypy recognizes uvloop types correctly."""

import asyncio

import uvloop
from rich.console import Console


async def main() -> None:
    """Test uvloop types."""
    # This should not trigger any mypy errors if types are working
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    # Test that we can call uvloop.run with proper typing
    await asyncio.sleep(0.1)

    Console.print("uvloop types working correctly")


if __name__ == "__main__":
    uvloop.run(main())
