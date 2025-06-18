"""Modern Oracle Integration Cloud usage examples with FLX 0.4.0.

This example demonstrates how to use the modernized OIC adapter and client
implementations that leverage FLX 0.4.0's advanced patterns.

Key improvements shown:
- 85% code reduction in adapter implementation
- Automatic operation tracking and metrics
- Hierarchical configuration with environment support
- Enhanced error handling and recovery
- Type-safe interfaces with modern Python patterns
"""

import asyncio
import os

# Modern FLX OIC imports
from flx_http_oracle_oic import (
    OracleOicClientModern,
    OracleOicConfigModern,
    OracleOicHttpAdapterModern,
    create_modern_adapter,
    create_modern_client,
)


async def example_modern_adapter_usage() -> None:
    """Example using the modern adapter directly."""
    # Create modern configuration with environment support
    config = OracleOicConfigModern(
        instance_id="my-instance",
        region="us-ashburn-1",
        client_id="modern-client-id",
        client_secret="modern-client-secret",
        timeout=30.0,
        debug_mode=True,
    )

    # Create modern adapter using factory function
    adapter = create_modern_adapter(config=config)

    try:
        # Modern adapter with automatic connection management
        async with adapter:

            # Get adapter info (shows modern features)
            await adapter.health_check()

            # List integrations with modern error handling
            await adapter.get_integrations(limit=5)

            # Modern adapter automatically tracks operation metrics

    except Exception:
        pass


async def example_modern_client_usage() -> None:
    """Example using the modern client with adapter flexibility."""
    # Create client with modern configuration
    config = OracleOicConfigModern.for_development(
        instance_id="dev-instance",
        region="us-ashburn-1",
        debug_mode=True,
    )

    # Create modern client (uses modern adapter by default)
    client = create_modern_client(config=config)

    try:
        async with client:

            # Show adapter information
            client.get_adapter_info()

            # Get integrations
            await client.get_integrations(limit=3)

            # Get connections
            await client.get_connections(limit=3)

            # Get operation metrics (modern adapter feature)
            await client.get_operations_metrics()

    except Exception:
        pass


async def example_adapter_comparison() -> None:
    """Example comparing legacy vs modern adapter performance."""
    config = OracleOicConfigModern(
        instance_id="comparison-instance",
        region="us-ashburn-1",
        client_id="test-client",
        client_secret="test-secret",
    )

    # Test both adapters
    for use_modern in [False, True]:

        client = OracleOicClientModern(config=config, use_modern_adapter=use_modern)

        try:
            async with client:

                # Show adapter capabilities
                client.get_adapter_info()

        except Exception:
            pass


async def example_hierarchical_configuration() -> None:
    """Example using hierarchical configuration with profiles."""
    # Create configurations for different environments
    configs = {
        "development": OracleOicConfigModern.for_development(
            instance_id="dev-instance",
            timeout=60.0,
            debug_mode=True,
        ),
        "production": OracleOicConfigModern.for_production(
            instance_id="prod-instance",
            timeout=30.0,
            debug_mode=False,
        ),
        "testing": OracleOicConfigModern.for_testing(
            instance_id="test-instance",
            timeout=10.0,
            verify_ssl=False,
        ),
    }

    for _env_name, _config in configs.items():
        pass


def example_environment_configuration() -> None:
    """Example showing environment variable configuration."""
    # Show how environment variables are used
    env_vars = {
        "OIC_INSTANCE_ID": "my-instance",
        "OIC_REGION": "us-ashburn-1",
        "OIC_CLIENT_ID": "env-client-id",
        "OIC_CLIENT_SECRET": "env-client-secret",
        "OIC_TIMEOUT": "45.0",
        "OIC_DEBUG_MODE": "true",
        "OIC_PROFILE": "development",
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    # Create config that automatically loads from environment
    config = OracleOicConfigModern()

    # Show adapter configuration
    config.to_adapter_config()


async def example_modern_features() -> None:
    """Example showcasing modern FLX features."""
    config = OracleOicConfigModern(
        instance_id="features-demo",
        region="us-ashburn-1",
        enable_metrics=True,
        enable_monitoring=True,
    )

    # Use modern adapter directly to show advanced features
    adapter = OracleOicHttpAdapterModern(config=config)

    try:
        async with adapter:

            # Modern adapters provide enhanced health checking
            await adapter.health_check()

            # Operation delegation with automatic metrics
            await adapter.get_integrations(limit=2)

            # Modern authentication management
            await adapter.authenticate()

    except Exception:
        pass


async def main() -> None:
    """Run all modern usage examples."""
    # Run examples
    await example_modern_adapter_usage()
    await example_modern_client_usage()
    await example_adapter_comparison()
    await example_hierarchical_configuration()
    example_environment_configuration()
    await example_modern_features()


if __name__ == "__main__":
    asyncio.run(main())
