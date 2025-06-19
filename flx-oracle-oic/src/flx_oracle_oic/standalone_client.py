"""Standalone Oracle Integration Cloud client that works without FLX dependencies."""

from typing import Any

from pydantic import BaseModel

try:
    from .standalone_adapter import StandaloneOracleOicHttpAdapter
    from .standalone_config import StandaloneOracleOicConfig
except ImportError:
    from standalone_adapter import StandaloneOracleOicHttpAdapter
    from standalone_config import StandaloneOracleOicConfig


class StandaloneOracleOicClient(BaseModel):
    """Standalone Oracle Integration Cloud client."""

    config: StandaloneOracleOicConfig
    adapter: StandaloneOracleOicHttpAdapter

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        config: StandaloneOracleOicConfig | None = None,
        **kwargs: Any,  # type: ignore[misc],
    ) -> None:
        """Initialize client with configuration."""
        if config is None:
            config = StandaloneOracleOicConfig()

        adapter = StandaloneOracleOicHttpAdapter(config=config)
        super().__init__(config=config, adapter=adapter, **kwargs)

    async def connect(self) -> None:
        """Connect to OIC."""
        await self.adapter.connect()

    async def disconnect(self) -> None:
        """Disconnect from OIC."""
        await self.adapter.disconnect()

    async def get_integrations(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Get integrations list."""
        return await self.adapter.get_integrations(limit, offset)

    async def get_integration(self, integration_id: str) -> dict[str, Any]:
        """Get specific integration."""
        return await self.adapter.get_integration(integration_id)

    async def get_connections(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Get connections list."""
        return await self.adapter.get_connections(limit, offset)

    async def get_connection(self, connection_id: str) -> dict[str, Any]:
        """Get specific connection."""
        return await self.adapter.get_connection(connection_id)

    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        return await self.adapter.health_check()

    async def get_packages(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Get packages list."""
        return await self.adapter.get_packages(limit, offset)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Async context manager exit."""
        await self.disconnect()
