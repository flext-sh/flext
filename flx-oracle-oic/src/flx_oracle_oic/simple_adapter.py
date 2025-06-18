"""Simple OIC adapter bypassing complex FLX dependencies."""

import logging
from typing import Any

from .auth import OICAuthenticator
from .config import OracleOicConfig
from .constants import (
    OIC_CONNECTIONS_PATH,
    OIC_INTEGRATIONS_PATH,
    PARAM_INTEGRATION_INSTANCE,
    PARAM_LIMIT,
    PARAM_OFFSET,
    RESPONSE_ITEMS,
)

logger = logging.getLogger(__name__)


class SimpleOicAdapter:
    """Simple OIC adapter with minimal dependencies."""

    def __init__(self, config: OracleOicConfig) -> None:
        self.config = config
        self._authenticator = OICAuthenticator(config, self)
        self._current_token = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._authenticate()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Async context manager exit."""

    async def _authenticate(self):
        """Perform authentication."""
        if not self._current_token:
            self._current_token = await self._authenticator.authenticate()
        return self._current_token

    async def _make_token_request(
        self,
        url: str,
        headers: dict[str, str],
        data: str,
    ) -> dict[str, Any]:
        """Make HTTP request for authentication token."""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    data=data,
                    timeout=60.0,
                )

                if response.status_code != 200:
                    msg = f"Token request failed: {response.status_code}"
                    raise RuntimeError(msg)

                response_data = response.json()
                if not isinstance(response_data, dict):
                    msg = "Invalid token response format"
                    raise RuntimeError(msg)

                return response_data

        except Exception as e:
            msg = f"Token request failed: {e}"
            raise RuntimeError(msg) from e

    async def list_connections(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """List connections using direct httpx."""
        if not self._current_token:
            await self._authenticate()

        url = f"{self.config.base_url}{self.config.base_path}{OIC_CONNECTIONS_PATH}"
        params = {PARAM_INTEGRATION_INSTANCE: self.config.instance_id}

        if limit is not None:
            params[PARAM_LIMIT] = str(limit)
        if offset is not None:
            params[PARAM_OFFSET] = str(offset)

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self._current_token.access_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=60.0,
                )

                if response.status_code != 200:
                    msg = f"API request failed: {response.status_code}"
                    raise RuntimeError(msg)

                response_data = response.json()
                if isinstance(response_data, dict) and RESPONSE_ITEMS in response_data:
                    return response_data[RESPONSE_ITEMS]
                msg = "Unexpected response format"
                raise RuntimeError(msg)

        except Exception as e:
            msg = f"Failed to get connections: {e}"
            raise RuntimeError(msg) from e

    async def list_integrations(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """List integrations using direct httpx."""
        if not self._current_token:
            await self._authenticate()

        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}"
        params = {PARAM_INTEGRATION_INSTANCE: self.config.instance_id}

        if limit is not None:
            params[PARAM_LIMIT] = str(limit)
        if offset is not None:
            params[PARAM_OFFSET] = str(offset)

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self._current_token.access_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=60.0,
                )

                if response.status_code != 200:
                    msg = f"API request failed: {response.status_code}"
                    raise RuntimeError(msg)

                response_data = response.json()
                if isinstance(response_data, dict) and RESPONSE_ITEMS in response_data:
                    return response_data[RESPONSE_ITEMS]
                msg = "Unexpected response format"
                raise RuntimeError(msg)

        except Exception as e:
            msg = f"Failed to get integrations: {e}"
            raise RuntimeError(msg) from e

    async def authenticate(self) -> dict[str, Any]:
        """Perform authentication and return token info."""
        try:
            await self._authenticate()
            if self._current_token:
                return {
                    "access_token": self._current_token.access_token,
                    "token_type": self._current_token.token_type,
                    "authenticated": True,
                }
            return {
                "authenticated": False,
                "error": "Authentication failed - no token received",
            }
        except Exception as e:
            return {
                "authenticated": False,
                "error": str(e),
            }

    async def health_check(self) -> dict[str, Any]:
        """Simple health check."""
        try:
            await self.list_integrations(limit=1)
            return {"status": "healthy", "connectivity": "ok"}
        except Exception as e:
            return {"status": "error", "connectivity": f"error: {e}"}

    async def ping(self) -> dict[str, Any]:
        """Simple ping test."""
        health = await self.health_check()
        if health.get("status") == "healthy":
            return {"status": "ok", "message": "OIC is reachable"}
        return {"status": "error", "message": "OIC health check failed"}
