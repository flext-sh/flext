"""Modern Oracle Integration Cloud client using FLX 0.4.0 patterns.

This modern client provides a clean facade over both legacy and modern adapters,
following the hexagonal architecture principle of adapter interchangeability.
"""

from typing import Any, Union

from .adapter import OracleOicHttpAdapter
from .adapter_modern import OracleOicHttpAdapterModern
from .config import OracleOicConfig
from .config_modern import OracleOicConfigModern

AdapterType = Union[OracleOicHttpAdapter, OracleOicHttpAdapterModern]


class OracleOicClientModern:
    """Modern Oracle Integration Cloud client with adapter flexibility.

    This client can work with either the legacy or modern adapter implementations,
    demonstrating the power of hexagonal architecture's adapter interchangeability.

    Features:
        - Support for both legacy and modern adapters
        - Async context manager for automatic resource management
        - Clean delegation to adapter operations
        - Type-safe interface with modern Python patterns
    """

    def __init__(
        self,
        config: OracleOicConfig | OracleOicConfigModern | None = None,
        *,
        use_modern_adapter: bool = True,
        **kwargs: Any,  # type: ignore[misc],
    ) -> None:
        """Initialize client with configuration and adapter choice.

        Args:
        ----
            config: Oracle OIC configuration. If None, loads from environment.
            use_modern_adapter: Whether to use the modern FLX 0.4.0 adapter.
            **kwargs: Additional adapter configuration.

        """
        if config is None:
            config = OracleOicConfig.from_env()

        self.config = config
        self._use_modern = use_modern_adapter

        # Create appropriate adapter based on preference
        if use_modern_adapter:
            # Convert to modern config if needed
            if isinstance(config, OracleOicConfig):
                # Use the legacy config directly with modern adapter
                self._adapter: AdapterType = OracleOicHttpAdapterModern(
                    config=config,
                    **kwargs,
                )
            else:
                self._adapter = OracleOicHttpAdapterModern(config=config, **kwargs)
        # Legacy adapter expects legacy config
        elif isinstance(config, OracleOicConfigModern):
            # Convert modern config to legacy (create legacy config with same values)
            legacy_config = OracleOicConfig(
                instance_id=config.instance_id,
                region=config.region,
                client_id=config.client_id,
                client_secret=config.client_secret,
                client_aud=config.client_aud,
                scope=config.scope,
                idcs_url=config.idcs_url,
                api_version=config.api_version,
                base_path=config.base_path,
                timeout=config.timeout,
                max_retries=config.max_retries,
                rate_limit_calls=config.rate_limit_calls,
                rate_limit_period=config.rate_limit_period,
                page_size=config.page_size,
                enable_monitoring=config.enable_monitoring,
                enable_caching=config.enable_caching,
                debug_mode=config.debug_mode,
            )
            self._adapter = OracleOicHttpAdapter(config=legacy_config, **kwargs)
        else:
            self._adapter = OracleOicHttpAdapter(config=config, **kwargs)

    async def __aenter__(self) -> "OracleOicClientModern":
        """Async context manager entry with automatic connection."""
        await self._adapter.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with automatic cleanup."""
        await self._adapter.disconnect()

    @property
    def adapter_type(self) -> str:
        """Get the type of adapter being used."""
        return "modern" if self._use_modern else "legacy"

    # Connection management

    async def connect(self) -> None:
        """Connect to Oracle Integration Cloud."""
        await self._adapter.connect()

    async def disconnect(self) -> None:
        """Disconnect from Oracle Integration Cloud."""
        await self._adapter.disconnect()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the connection."""
        return await self._adapter.health_check()

    # Authentication operations

    async def authenticate(self) -> dict[str, Any]:
        """Perform authentication and return token information."""
        return await self._adapter.authenticate()

    async def refresh_token(self) -> dict[str, Any]:
        """Refresh the authentication token."""
        return await self._adapter.refresh_token()

    def set_jwt_token(self, jwt_token: str) -> None:
        """Set JWT token for authentication."""
        self._adapter.set_jwt_token(jwt_token)

    def use_oauth2_auth(self) -> None:
        """Switch to OAuth2 authentication strategy."""
        self._adapter.use_oauth2_auth()

    def use_idcs_auth(self) -> None:
        """Switch to IDCS authentication strategy."""
        self._adapter.use_idcs_auth()

    def clear_auth_cache(self) -> None:
        """Clear authentication cache."""
        self._adapter.clear_auth_cache()

    # Integration operations

    async def get_integrations(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get integrations with optional pagination.

        Args:
        ----
            limit: Maximum number of integrations to return.
            offset: Number of integrations to skip.

        Returns:
        -------
            List of integration details.

        """
        return await self._adapter.get_integrations(limit=limit, offset=offset)

    async def get_integration(self, integration_id: str) -> dict[str, Any] | None:
        """Get specific integration by ID.

        Args:
        ----
            integration_id: The integration identifier.

        Returns:
        -------
            Integration details or None if not found.

        """
        return await self._adapter.get_integration(integration_id)

    # Connection operations

    async def get_connections(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get connections with optional pagination.

        Args:
        ----
            limit: Maximum number of connections to return.
            offset: Number of connections to skip.

        Returns:
        -------
            List of connection details.

        """
        return await self._adapter.get_connections(limit=limit, offset=offset)

    async def get_connection(self, connection_id: str) -> dict[str, Any] | None:
        """Get specific connection by ID.

        Args:
        ----
            connection_id: The connection identifier.

        Returns:
        -------
            Connection details or None if not found.

        """
        return await self._adapter.get_connection(connection_id)

    # Monitoring operations

    async def get_monitoring_data(
        self,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get monitoring data with optional time range.

        Args:
        ----
            start_time: Start time in ISO format.
            end_time: End time in ISO format.

        Returns:
        -------
            List of monitoring data points.

        """
        return await self._adapter.get_monitoring_data(
            start_time=start_time,
            end_time=end_time,
        )

    # Package operations

    async def get_packages(self) -> list[dict[str, Any]]:
        """Get deployment packages.

        Returns
        -------
            List of package details.

        """
        return await self._adapter.get_packages()

    # Utility methods

    def get_adapter_info(self) -> dict[str, Any]:
        """Get information about the current adapter.

        Returns
        -------
            Dictionary containing adapter type, configuration, and status.

        """
        return {
            "adapter_type": self.adapter_type,
            "adapter_class": type(self._adapter).__name__,
            "config": {
                "instance_id": self.config.instance_id,
                "base_url": self.config.base_url,
                "timeout": self.config.timeout,
            },
            "features": {
                "modern_patterns": self._use_modern,
                "advanced_mixins": self._use_modern,
                "operation_tracking": self._use_modern,
                "automatic_metrics": self._use_modern,
            },
        }

    async def get_operations_metrics(self) -> dict[str, Any]:
        """Get operation metrics (only available with modern adapter).

        Returns
        -------
            Operation metrics if using modern adapter, otherwise basic info.

        """
        if self._use_modern and hasattr(self._adapter, "_get_operation_metrics"):
            # Access mixin metrics if available
            return self._adapter._get_operation_metrics()
        return {
            "adapter_type": self.adapter_type,
            "metrics_available": self._use_modern,
            "message": "Operation metrics only available with modern adapter",
        }
