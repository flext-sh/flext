"""Standalone Oracle Integration Cloud HTTP adapter that works without FLX dependencies."""

from typing import Any

import aiohttp
from pydantic import BaseModel, Field

try:
    from .standalone_config import StandaloneOracleOicConfig
except ImportError:
    from standalone_config import StandaloneOracleOicConfig


class StandaloneOracleOicHttpAdapter(BaseModel):
    """Standalone Oracle Integration Cloud HTTP adapter."""

    config: StandaloneOracleOicConfig
    session: aiohttp.ClientSession | None = Field(default=None, exclude=True)
    auth_token: str | None = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow dynamic method injection

    def __init__(
        self,
        config: StandaloneOracleOicConfig | None = None,
        **kwargs: Any,  # type: ignore[misc],
    ) -> None:
        """Initialize adapter with configuration."""
        if config is None:
            config = StandaloneOracleOicConfig()

        super().__init__(config=config, **kwargs)

    async def connect(self) -> None:
        """Connect and authenticate."""
        if self.session is None:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)

            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.config.get_headers(),
            )

        # Authenticate
        await self._authenticate()

    async def disconnect(self) -> None:
        """Disconnect and cleanup."""
        if self.session:
            await self.session.close()
            self.session = None
        self.auth_token = None

    async def _authenticate(self) -> None:
        """Authenticate with OIC OAuth."""
        if not self.session:
            msg = "Session not initialized. Call connect() first."
            raise RuntimeError(msg) from e

        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret.get_secret_value(),
            "scope": self.config.oauth_scope,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            async with self.session.post(
                self.config.oauth_url,
                data=auth_data,
                headers=headers,
            ) as response:
                if response.status == 200:
                    auth_response = await response.json()
                    self.auth_token = auth_response.get("access_token")

                    # Update session headers with auth token
                    if self.auth_token:
                        self.session.headers.update(
                            {"Authorization": f"Bearer {self.auth_token}"},
                        )
                else:
                    msg = f"Authentication failed: {response.status}"
                    raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"Authentication error: {e}"
            raise RuntimeError(msg) from e

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make GET request."""
        if not self.session:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg) from e

        url = f"{self.config.base_url}{path}"

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                if response.status == 404:
                    return {"error": "Not found", "status": 404}
                msg = f"HTTP {response.status}: {await response.text()}"
                raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"GET request failed: {e}"
            raise RuntimeError(msg) from e

    async def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make POST request."""
        if not self.session:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg) from e

        url = f"{self.config.base_url}{path}"

        try:
            async with self.session.post(url, json=data) as response:
                if response.status in {200, 201}:
                    return await response.json()
                msg = f"HTTP {response.status}: {await response.text()}"
                raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"POST request failed: {e}"
            raise RuntimeError(msg) from e

    # OIC-specific methods
    async def get_integrations(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Get integrations list."""
        params = {"limit": min(limit, self.config.page_size), "offset": offset}
        return await self.get("/ic/api/integration/v1/integrations", params)

    async def get_integration(self, integration_id: str) -> dict[str, Any]:
        """Get specific integration."""
        return await self.get(f"/ic/api/integration/v1/integrations/{integration_id}")

    async def get_connections(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Get connections list."""
        params = {"limit": min(limit, self.config.page_size), "offset": offset}
        return await self.get("/ic/api/integration/v1/connections", params)

    async def get_connection(self, connection_id: str) -> dict[str, Any]:
        """Get specific connection."""
        return await self.get(f"/ic/api/integration/v1/connections/{connection_id}")

    async def put(
        self,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make PUT request."""
        if not self.session:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg) from e

        url = f"{self.config.base_url}{path}"

        try:
            async with self.session.put(url, json=data) as response:
                if response.status in {200, 201}:
                    return await response.json()
                if response.status == 404:
                    return {"error": "Not found", "status": 404}
                msg = f"HTTP {response.status}: {await response.text()}"
                raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"PUT request failed: {e}"
            raise RuntimeError(msg) from e

    async def delete(self, path: str) -> dict[str, Any]:
        """Make DELETE request."""
        if not self.session:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg) from e

        url = f"{self.config.base_url}{path}"

        try:
            async with self.session.delete(url) as response:
                if response.status in {200, 204}:
                    if response.content_length and response.content_length > 0:
                        return await response.json()
                    return {"success": True}
                if response.status == 404:
                    return {"error": "Not found", "status": 404}
                msg = f"HTTP {response.status}: {await response.text()}"
                raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"DELETE request failed: {e}"
            raise RuntimeError(msg) from e

    async def patch(
        self,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make PATCH request."""
        if not self.session:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg) from e

        url = f"{self.config.base_url}{path}"

        try:
            async with self.session.patch(url, json=data) as response:
                if response.status in {200, 201}:
                    return await response.json()
                if response.status == 404:
                    return {"error": "Not found", "status": 404}
                msg = f"HTTP {response.status}: {await response.text()}"
                raise RuntimeError(msg) from e
        except Exception as e:
            msg = f"PATCH request failed: {e}"
            raise RuntimeError(msg) from e

    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        try:
            result = await self.get("/ic/api/integration/v1/monitoring/health")
            return {"status": "HEALTHY", "details": result}
        except Exception as e:
            return {"status": "UNHEALTHY", "error": str(e)}

    async def get_packages(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Get packages list."""
        params = {"limit": min(limit, self.config.page_size), "offset": offset}
        return await self.get("/ic/api/integration/v1/packages", params)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Async context manager exit."""
        await self.disconnect()
