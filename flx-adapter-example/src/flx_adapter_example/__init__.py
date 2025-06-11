"""FLX Adapter Example - Template for creating FLX bidirectional plugins.

This module provides a complete example of how to create a bidirectional plugin
for the FLX framework, demonstrating best practices and patterns.

The adapter can operate in both inbound and outbound modes:
- Inbound: Receives requests from external systems
- Outbound: Makes calls to external APIs/services
- Bidirectional: Supports both modes simultaneously

Example:
    Basic usage:

    ```python
    from flx_adapter_example import create_adapter, FlxAdapterConfig

    # Create adapter with default configuration
    adapter = create_adapter()

    # Or with custom configuration
    config = FlxAdapterConfig(
        name="my-adapter",
        api_url="https://api.example.com",
        timeout_seconds=30.0
    )
    adapter = create_adapter(config)

    # Initialize and start
    await adapter.initialize()
    await adapter.start()
    ```
"""

from __future__ import annotations

from .adapter import FlxAdapterExample
from .client import FlxAdapterClient
from .config import FlxAdapterConfig


def create_adapter(config: FlxAdapterConfig | None = None) -> FlxAdapterExample:
    """Create FLX adapter with configuration.

    Args:
        config: Adapter configuration. If None, loads from environment.

    Returns:
        Configured FLX adapter instance

    Example:
        ```python
        # With default configuration
        adapter = create_adapter()

        # With custom configuration
        config = FlxAdapterConfig(name="my-adapter")
        adapter = create_adapter(config)
        ```
    """
    if config is None:
        config = FlxAdapterConfig.from_env()

    return FlxAdapterExample(config)


def create_client(config: FlxAdapterConfig | None = None) -> FlxAdapterClient:
    """Create FLX adapter client with configuration.

    Args:
        config: Adapter configuration. If None, loads from environment.

    Returns:
        Configured FLX adapter client

    Example:
        ```python
        client = create_client()
        response = await client.get_resource("123")
        ```
    """
    if config is None:
        config = FlxAdapterConfig.from_env()

    return FlxAdapterClient(config)


__version__ = "1.0.0"

__all__ = [
    "FlxAdapterClient",
    "FlxAdapterConfig",
    "FlxAdapterExample",
    "create_adapter",
    "create_client",
]
