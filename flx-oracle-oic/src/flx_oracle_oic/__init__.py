"""FLX Oracle Integration Cloud HTTP Adapter - Enterprise integration implementation.

This module implements Oracle Integration Cloud HTTP connectivity as part of the Infrastructure layer
in the hexagonal architecture. It provides type-safe OIC operations with JWT authentication,
endpoint management, and comprehensive monitoring capabilities for enterprise integrations.

Architecture:
    Layer: Infrastructure (HTTP Adapter)
    Pattern: Hexagonal Architecture with Adapter Pattern
    Dependencies: Outbound (HTTP clients, authentication services, monitoring)

Example:
-------
    Basic OIC integration operations:

    ```python
    from flx_http_oracle_oic import (
        create_modern_client,
        OracleOicConfigModern
    )

    # Create configuration
    config = OracleOicConfigModern(
        base_url="https://oic-instance.oracle.com",
        username="integration_user",
        password="secure_password"
    )

    # Initialize client
    client = create_modern_client(config)

    # Execute integration operations
    async with client:
        response = await client.get_integrations()
        status = await client.check_integration_status("my-integration")
    ```

Note:
----
    This adapter enforces hexagonal architecture constraints where OIC operations
    are abstracted through clean interfaces, enabling easy testing and service
    substitution while maintaining enterprise security standards.


"""

from __future__ import annotations

from typing import Any

# Version information - import at top
from .__version__ import __version__
from .adapter import OracleOicHttpAdapter
from .adapter_modern import OracleOicHttpAdapterModern
from .client import OracleOicClient
from .client_modern import OracleOicClientModern
from .config import OracleOicConfig
from .config_modern import OracleOicConfigModern


# Convenience functions for adapter creation
def create_oic_adapter(**kwargs: Any) -> OracleOicHttpAdapter:  # type: ignore[misc]
    """Create Oracle OIC HTTP adapter with configuration.

    Args:
    ----
        **kwargs: Adapter configuration parameters

    Returns:
    -------
        Configured Oracle OIC HTTP adapter

    """
    return OracleOicHttpAdapter(**kwargs)


def create_modern_adapter(
    config: OracleOicConfig | None = None,
    **kwargs: Any,  # type: ignore[misc]
) -> OracleOicHttpAdapterModern:
    """Create modern Oracle OIC HTTP adapter with FLX 0.4.0 patterns.

    Args:
    ----
        config: Oracle OIC configuration. If None, created from kwargs.
        **kwargs: Adapter configuration parameters

    Returns:
    -------
        Configured modern Oracle OIC HTTP adapter

    """
    return OracleOicHttpAdapterModern(config=config, **kwargs)


def create_modern_client(
    config: OracleOicConfigModern | None = None,
    **kwargs: Any,  # type: ignore[misc]
) -> OracleOicClientModern:
    """Create modern Oracle OIC client with FLX 0.4.0 patterns.

    Args:
    ----
        config: Modern Oracle OIC configuration. If None, loads from environment.
        **kwargs: Additional client configuration

    Returns:
    -------
        Configured modern Oracle OIC client

    """
    if config is None:
        config = OracleOicConfigModern()
    return OracleOicClientModern(config=config, **kwargs)


# Standard client creation functions
def create_client(
    config: OracleOicConfig | None = None,
    **kwargs: Any,  # type: ignore[misc]
) -> OracleOicClient:
    """Create Oracle OIC client with configuration.

    Args:
    ----
        config: Oracle OIC configuration. If None, loads from environment.
        **kwargs: Additional adapter configuration

    Returns:
    -------
        Configured Oracle OIC client

    """
    if config is None:
        config = OracleOicConfig.from_env()
    return OracleOicClient(config, **kwargs)


def from_env(prefix: str = "OIC_", **kwargs: Any) -> OracleOicClient:  # type: ignore[misc]
    """Create Oracle OIC client from environment variables.

    Args:
    ----
        prefix: Environment variable prefix
        **kwargs: Additional adapter configuration

    Returns:
    -------
        Configured Oracle OIC client

    """
    config = OracleOicConfig.from_env(prefix)
    return OracleOicClient(config, **kwargs)


# Backward compatibility alias
flx_create_client = create_client


__all__ = [
    "OracleOicClient",
    "OracleOicClientModern",
    "OracleOicConfig",
    "OracleOicConfigModern",
    "OracleOicHttpAdapter",
    "OracleOicHttpAdapterModern",
    "__version__",
    "create_client",
    "create_modern_adapter",
    "create_modern_client",
    "create_oic_adapter",
    "flx_create_client",
    "from_env",
]
