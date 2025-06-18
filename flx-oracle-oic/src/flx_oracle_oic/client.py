"""Oracle Integration Cloud client using FLX adapter with zero redundancy."""

from typing import Any

from .adapter import OracleOicHttpAdapter
from .config import OracleOicConfig


class OracleOicClient:
    """Simple client facade for Oracle Integration Cloud operations."""

    def __init__(self, config: OracleOicConfig | None = None, **kwargs: Any) -> None:  # type: ignore[misc]
        """Initialize client with configuration."""
        if config is None:
            config = OracleOicConfig()

        self._adapter = OracleOicHttpAdapter(config=config, **kwargs)
        self.config = config

    async def __aenter__(self) -> "OracleOicClient":
        """Async context manager entry."""
        await self._adapter.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self._adapter.disconnect()

    async def connect(self) -> None:
        """Connect to OIC."""
        await self._adapter.connect()

    async def disconnect(self) -> None:
        """Disconnect from OIC."""
        await self._adapter.disconnect()

    # Delegate all operations to adapter
    async def get_integrations(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get integrations with pagination."""
        return await self._adapter.get_integrations(limit=limit, offset=offset)

    async def get_integration(self, integration_id: str) -> dict[str, Any] | None:
        """Get specific integration."""
        return await self._adapter.get_integration(integration_id)

    async def create_integration(
        self,
        integration_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create new integration."""
        return await self._adapter.create_integration(integration_data)

    async def update_integration(
        self,
        integration_id: str,
        integration_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update integration."""
        return await self._adapter.update_integration(integration_id, integration_data)

    async def delete_integration(self, integration_id: str) -> dict[str, Any]:
        """Delete integration."""
        return await self._adapter.delete_integration(integration_id)

    async def get_connections(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get connections with pagination."""
        return await self._adapter.get_connections(limit=limit, offset=offset)

    async def get_connection(self, connection_id: str) -> dict[str, Any] | None:
        """Get specific connection."""
        return await self._adapter.get_connection(connection_id)

    async def get_monitoring_data(self, entity_type: str) -> dict[str, Any]:
        """Get monitoring data."""
        return await self._adapter.get_monitoring_data(entity_type)

    async def get_packages(self) -> list[dict[str, Any]]:
        """Get packages."""
        return await self._adapter.get_packages()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        return await self._adapter.health_check()

    def get_operations(self) -> dict[str, Any]:
        """Get available operations."""
        return self._adapter.get_operations()
