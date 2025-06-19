"""Oracle Integration Cloud HTTP adapter using FLX architecture with zero redundancy."""

import logging
from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict

if TYPE_CHECKING:
    from flx.adapters.outbound.http import HttpClientAdapter
else:
    # Runtime: Use dummy base class to avoid lazy_import as base class
    class HttpClientAdapter:
        """Dummy base class for runtime."""

        def __init__(self, **kwargs: Any) -> None:
            pass

from .auth import AuthenticationError, AuthToken, OICAuthenticator
from .config import OracleOicConfig
from .constants import (
    HTTP_GET,
    HTTP_POST,
    OIC_CONNECTIONS_PATH,
    OIC_INTEGRATIONS_PATH,
    OIC_MONITORING_PATH,
    OIC_PACKAGES_PATH,
    PARAM_INTEGRATION_INSTANCE,
    PARAM_LIMIT,
    PARAM_OFFSET,
    RESPONSE_HEALTHY,
    RESPONSE_ITEMS,
)

# Initialize module-level logger
logger = logging.getLogger(__name__)


class OracleOicHttpAdapter(HttpClientAdapter):
    """Oracle Integration Cloud HTTP adapter using FLX HTTP base with zero code duplication."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=False, extra="allow"
    )

    def __init__(self, config: OracleOicConfig | None = None, **kwargs: Any) -> None:  # type: ignore[misc]
        """Initialize with OIC configuration and all FLX dependencies."""
        if config is None:
            config = OracleOicConfig()

        # Use config values for HTTP adapter
        adapter_config = config.to_adapter_config()

        # ZERO TOLERANCE: Provide ALL required FLX dependencies upfront
        if "logger" not in kwargs:
            kwargs["logger"] = logging.getLogger(__name__)

        if "labels" not in kwargs:
            try:
                # Lazy import to avoid circular dependencies
                MetricLabels = lazy_import("flx.infra.observability.metrics_system", "MetricLabels")

                kwargs["labels"] = MetricLabels(
                    {"service": "oic-cli", "adapter": "oic-http"}
                )
            except ImportError:
                kwargs["labels"] = {"service": "oic-cli", "adapter": "oic-http"}

        # Override HTTP adapter defaults with OIC config and ensure required fields
        kwargs.update(
            {
                "name": kwargs.get("name", "oic-http"),
                # Use correct field names that HttpClientAdapter expects
                "operation_timeout_seconds": adapter_config["timeout"],
                "retry_attempts": adapter_config["max_retries"],
                "default_headers": adapter_config["headers"],
                "auth_token": kwargs.get("auth_token"),  # Set via separate auth flow
                # Required HttpClientAdapter fields from config or defaults
                "verify_ssl": kwargs.get(
                    "verify_ssl", adapter_config.get("verify_ssl", True)
                ),
                "user_agent": kwargs.get(
                    "user_agent",
                    adapter_config.get("user_agent", "FLX-OIC-HTTP-Client/1.0"),
                ),
                "buffer_size_bytes": kwargs.get(
                    "buffer_size_bytes", adapter_config.get("buffer_size_bytes", 8192)
                ),
                "keepalive_timeout_seconds": kwargs.get(
                    "keepalive_timeout_seconds",
                    adapter_config.get("keepalive_timeout_seconds", 30.0),
                ),
                # Additional FLX requirements
                "connection_timeout_seconds": kwargs.get(
                    "connection_timeout_seconds", 30.0
                ),
                "max_connections": kwargs.get("max_connections", 10),
                "enable_compression": kwargs.get("enable_compression", True),
                "retry_delay_seconds": kwargs.get("retry_delay_seconds", 1.0),
            }
        )

        super().__init__(**kwargs)
        self.config = config

        # Initialize the comprehensive authentication system
        self._authenticator = OICAuthenticator(config, self)
        self._current_token: AuthToken | None = None

    async def _connect(self) -> None:
        """Connect with OIC-specific authentication."""
        # First establish HTTP connection
        await super()._connect()

        # Then perform OIC authentication using the comprehensive auth system
        await self._authenticate()

    async def _authenticate(self, *, force_refresh: bool = False) -> AuthToken:
        """Perform authentication using the comprehensive auth system."""
        try:
            logger.debug(f"🔐 Starting authentication (force_refresh={force_refresh})")

            # Use the authenticator to get a valid token
            self._current_token = await self._authenticator.authenticate(force_refresh)
            logger.debug(
                f"✅ Authentication successful, token expires at {self._current_token.expires_at}"
            )

            # Update the auth_token for the HTTP adapter
            self.auth_token = self._current_token.access_token
            logger.debug(f"🔑 Auth token updated: {self.auth_token[:20]}...")

            # Update the HTTP service with the new token
            if hasattr(self, "_http_service") and self._http_service:
                self._http_service.auth_token = self.auth_token
                logger.debug("🔗 HTTP service auth token updated")

            return self._current_token

        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            msg = f"Authentication failed: {e}"
            raise RuntimeError(msg) from e

    async def _make_token_request(
        self, url: str, headers: dict[str, str], data: str
    ) -> dict[str, Any]:
        """Make HTTP request for authentication token using direct httpx like bash script."""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, data=data, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"Token request failed with status {response.status_code}: {response.text}"
                    raise AuthenticationError(msg)

                response_data = response.json()

                if not isinstance(response_data, dict):
                    msg = f"Invalid token response format: {type(response_data)}"
                    raise AuthenticationError(msg)

                return response_data

        except Exception as e:
            msg = f"Token request failed: {e}"
            raise AuthenticationError(msg) from e

    async def ensure_authenticated(self) -> None:
        """Ensure we have a valid authentication token."""
        if self._current_token is None or self._current_token.is_expired:
            await self._authenticate(force_refresh=True)

    # Authentication API methods for CLI and external use
    async def authenticate(self) -> dict[str, Any]:
        """Perform authentication and return token info for CLI use."""
        try:
            token = await self._authenticate()
            return {
                "access_token": token.access_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in,
                "expires_at": (
                    token.expires_at.isoformat() if token.expires_at else None
                ),
                "scope": token.scope,
                "authenticated": True,
                "strategy": (
                    type(self._authenticator._strategy).__name__
                    if self._authenticator._strategy
                    else "Unknown"
                ),
            }
        except Exception as e:
            return {
                "authenticated": False,
                "error": str(e),
                "strategy": (
                    type(self._authenticator._strategy).__name__
                    if self._authenticator._strategy
                    else "Unknown"
                ),
            }

    async def refresh_token(self) -> dict[str, Any]:
        """Refresh authentication token."""
        try:
            token = await self._authenticator.refresh_token()
            self._current_token = token
            self.auth_token = token.access_token

            # Update the HTTP service with the new token
            if hasattr(self, "_http_service") and self._http_service:
                self._http_service.auth_token = self.auth_token

            return {
                "access_token": token.access_token,
                "token_type": token.token_type,
                "expires_in": token.expires_in,
                "expires_at": (
                    token.expires_at.isoformat() if token.expires_at else None
                ),
                "refreshed": True,
            }
        except Exception as e:
            return {"refreshed": False, "error": str(e)}

    def set_jwt_token(self, jwt_token: str) -> None:
        """Set JWT token for authentication."""
        self._authenticator.use_jwt_strategy(jwt_token)

    def use_oauth2_auth(self) -> None:
        """Use OAuth2 Client Credentials authentication."""
        self._authenticator.use_oauth2_strategy()

    def use_idcs_auth(self) -> None:
        """Use IDCS authentication."""
        self._authenticator.use_idcs_strategy()

    def clear_auth_cache(self) -> None:
        """Clear authentication cache."""
        self._authenticator.clear_cache()
        self._current_token = None
        self.auth_token = None

    @classmethod
    def from_config(cls, config: OracleOicConfig) -> "OracleOicHttpAdapter":
        """Create adapter from configuration."""
        return cls(config=config)

    @property
    def oic_base_url(self) -> str:
        """Get OIC base URL."""
        return self.config.base_url

    @property
    def oic_instance_id(self) -> str:
        """Get OIC instance ID."""
        return self.config.instance_id

    @property
    def api_version(self) -> str:
        """Get API version."""
        return self.config.api_version

    async def list_integrations(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[dict[str, Any]]:
        """List integrations - alias for get_integrations."""
        return await self.get_integrations(limit=limit, offset=offset)

    async def list_connections(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[dict[str, Any]]:
        """List connections - alias for get_connections."""
        return await self.get_connections(limit=limit, offset=offset)

    # OIC API Methods - Using constants to eliminate redundancy
    async def get_integrations(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[dict[str, Any]]:
        """Get OIC integrations with pagination using direct httpx."""
        await self.ensure_authenticated()

        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}"

        params = {PARAM_INTEGRATION_INSTANCE: self.config.instance_id}
        if limit is not None:
            params[PARAM_LIMIT] = str(limit)
        if offset is not None:
            params[PARAM_OFFSET] = str(offset)

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                response_data = response.json()

                if isinstance(response_data, dict) and RESPONSE_ITEMS in response_data:
                    return response_data[RESPONSE_ITEMS]  # type: ignore[no-any-return]

                msg = f"Unexpected response format: {type(response_data)}"
                raise RuntimeError(msg)

        except Exception as e:
            msg = f"Failed to get integrations: {e}"
            raise RuntimeError(msg) from e

    async def get_integration(self, integration_id: str) -> dict[str, Any] | None:
        """Get specific integration by ID."""
        await self.ensure_authenticated()

        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}/{integration_id}"
        params = {PARAM_INTEGRATION_INSTANCE: self.config.instance_id}

        try:
            response = await self.get(url, params=params)
            return response if isinstance(response, dict) else None

        except Exception as e:
            msg = f"Failed to get integration {integration_id}: {e}"
            raise RuntimeError(msg) from e

    async def get_connections(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[dict[str, Any]]:
        """Get OIC connections with pagination using direct httpx."""
        logger.debug(f"🔌 get_connections called with limit={limit}, offset={offset}")
        await self.ensure_authenticated()

        url = f"{self.config.base_url}{self.config.base_path}{OIC_CONNECTIONS_PATH}"

        params = {PARAM_INTEGRATION_INSTANCE: self.config.instance_id}
        if limit is not None:
            params[PARAM_LIMIT] = str(limit)
        if offset is not None:
            params[PARAM_OFFSET] = str(offset)

        logger.debug(f"🌐 Making API request to: {url}")
        logger.debug(f"📋 Request params: {params}")

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token[:20]}..."}
            logger.debug(f"🔐 Request headers: {headers}")

            async with httpx.AsyncClient() as client:
                logger.debug("📡 Sending HTTP GET request...")
                response = await client.get(
                    url,
                    params=params,
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    timeout=60.0,
                )
                logger.debug(f"📥 Response status: {response.status_code}")

                if response.status_code != 200:
                    logger.error(
                        f"❌ API request failed with status {response.status_code}: {response.text}"
                    )
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                response_data = response.json()
                logger.debug(f"📊 Response data type: {type(response_data)}")

                if isinstance(response_data, dict) and RESPONSE_ITEMS in response_data:
                    items = response_data[RESPONSE_ITEMS]
                    logger.debug(f"✅ Found {len(items)} connections in response")
                    return items  # type: ignore[no-any-return]

                logger.debug("⚠️ No 'items' key found in response")
                msg = f"Unexpected response format: {type(response_data)}"
                raise RuntimeError(msg)

        except Exception as e:
            logger.error(f"❌ Failed to get connections: {e}")
            msg = f"Failed to get connections: {e}"
            raise RuntimeError(msg) from e

    async def get_connection(self, connection_id: str) -> dict[str, Any] | None:
        """Get specific connection by ID."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_CONNECTIONS_PATH}/{connection_id}"
        params = {PARAM_INTEGRATION_INSTANCE: self.config.instance_id}

        try:
            response = await self.get(url, params=params)
            return response if isinstance(response, dict) else None

        except Exception as e:
            msg = f"Failed to get connection {connection_id}: {e}"
            raise RuntimeError(msg) from e

    async def create_integration(
        self, integration_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create new integration."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}"

        try:
            response = await self.post(url, json=integration_data)
            return response if isinstance(response, dict) else {}

        except Exception as e:
            msg = f"Failed to create integration: {e}"
            raise RuntimeError(msg) from e

    async def update_integration(
        self, integration_id: str, integration_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update existing integration."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}/{integration_id}"

        try:
            response = await self.put(url, json=integration_data)
            return response if isinstance(response, dict) else {}

        except Exception as e:
            msg = f"Failed to update integration {integration_id}: {e}"
            raise RuntimeError(msg) from e

    async def delete_integration(self, integration_id: str) -> dict[str, Any]:
        """Delete integration."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}/{integration_id}"

        try:
            response = await self.delete(url)
            return response if isinstance(response, dict) else {}

        except Exception as e:
            msg = f"Failed to delete integration {integration_id}: {e}"
            raise RuntimeError(msg) from e

    async def get_monitoring_data(self, entity_type: str) -> dict[str, Any]:
        """Get monitoring data for entity type."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_MONITORING_PATH}/{entity_type}"

        try:
            response = await self.get(url)
            return response if isinstance(response, dict) else {}

        except Exception as e:
            msg = f"Failed to get monitoring data: {e}"
            raise RuntimeError(msg) from e

    async def get_packages(self) -> list[dict[str, Any]]:
        """Get OIC packages."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_PACKAGES_PATH}"
        params = {PARAM_INTEGRATION_INSTANCE: self.config.instance_id}

        try:
            response = await self.get(url, params=params)

            if isinstance(response, dict) and RESPONSE_ITEMS in response:
                return response[RESPONSE_ITEMS]  # type: ignore[no-any-return]

            return []

        except Exception as e:
            msg = f"Failed to get packages: {e}"
            raise RuntimeError(msg) from e

    async def health_check(self) -> dict[str, Any]:
        """Perform OIC-specific health check."""
        base_health = await self._perform_health_check_operation()

        # Add OIC-specific health information
        oic_health = {
            "oic_instance": self.config.instance_id,
            "oic_region": self.config.region,
            "oauth_configured": bool(self.config.client_id),
            "base_url": self.config.base_url,
        }

        # Test connectivity to OIC
        try:
            # Try to get integrations as connectivity test
            await self.get_integrations(limit=1)
            oic_health["connectivity"] = RESPONSE_HEALTHY
        except Exception as e:
            oic_health["connectivity"] = f"error: {e}"
            base_health["status"] = "degraded"

        base_health.update(oic_health)
        return base_health  # type: ignore[no-any-return]

    def get_operations(self) -> dict[str, Any]:
        """Get OIC-specific operations metadata."""
        base_ops = self._get_specific_operations()

        oic_operations = {
            "get_integrations": {
                "description": "Get list of OIC integrations",
                "method": HTTP_GET,
                "parameters": {
                    "limit": {"type": "integer", "required": False},
                    "offset": {"type": "integer", "required": False},
                },
                "returns": "list[dict]",
            },
            "get_integration": {
                "description": "Get specific integration by ID",
                "method": HTTP_GET,
                "parameters": {
                    "integration_id": {"type": "string", "required": True},
                },
                "returns": "dict|None",
            },
            "create_integration": {
                "description": "Create new integration",
                "method": HTTP_POST,
                "parameters": {
                    "integration_data": {"type": "dict", "required": True},
                },
                "returns": "dict",
            },
            "get_connections": {
                "description": "Get list of OIC connections",
                "method": HTTP_GET,
                "parameters": {
                    "limit": {"type": "integer", "required": False},
                    "offset": {"type": "integer", "required": False},
                },
                "returns": "list[dict]",
            },
            "get_monitoring_data": {
                "description": "Get monitoring data for entity type",
                "method": HTTP_GET,
                "parameters": {
                    "entity_type": {"type": "string", "required": True},
                },
                "returns": "dict",
            },
        }

        base_ops.update(oic_operations)
        return base_ops  # type: ignore[no-any-return]

    # CLI Support Methods

    async def get_integration_status(self, integration_id: str) -> dict[str, Any]:
        """Get detailed status of an integration."""
        try:
            integration = await self.get_integration(integration_id)
            if not integration:
                return {
                    "error": "Integration not found",
                    "integration_id": integration_id,
                }

            # Extract status information
            return {
                "integration_id": integration_id,
                "name": integration.get("name", ""),
                "status": integration.get("status", "UNKNOWN"),
                "version": integration.get("version", ""),
                "last_updated": integration.get("lastUpdated", ""),
                "is_active": integration.get("status", "").upper() == "ACTIVATED",
                "runtime_health": integration.get("runtimeHealth", {}),
                "activation_time": integration.get("activationTime", ""),
                "deactivation_time": integration.get("deactivationTime", ""),
            }

        except Exception as e:
            return {"error": str(e), "integration_id": integration_id}

    async def activate_integration(self, integration_id: str) -> dict[str, Any]:
        """Activate an integration."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}/{integration_id}/activate"

        try:
            response = await self.post(url, json={})
            return {
                "success": True,
                "integration_id": integration_id,
                "response": response,
            }

        except Exception as e:
            msg = f"Failed to activate integration {integration_id}: {e}"
            raise RuntimeError(msg) from e

    async def deactivate_integration(self, integration_id: str) -> dict[str, Any]:
        """Deactivate an integration."""
        url = f"{self.config.base_url}{self.config.base_path}{OIC_INTEGRATIONS_PATH}/{integration_id}/deactivate"

        try:
            response = await self.post(url, json={})
            return {
                "success": True,
                "integration_id": integration_id,
                "response": response,
            }

        except Exception as e:
            msg = f"Failed to deactivate integration {integration_id}: {e}"
            raise RuntimeError(msg) from e

    async def get_token_info(self) -> dict[str, Any]:
        """Get current token information."""
        if not self.auth_token:
            msg = "No active authentication token"
            raise RuntimeError(msg)

        return {
            "access_token": self.auth_token,
            "token_type": "Bearer",
            "authenticated": True,
            "scope": self.config.oauth_scope,
        }

    async def get_logs(
        self, integration_id: str = "", hours: int = 1, level: str = ""
    ) -> list[dict[str, Any]]:
        """Get integration logs."""
        try:
            # Build logs endpoint URL
            if integration_id:
                url = f"{self.config.base_url}{self.config.base_path}/integrations/{integration_id}/logs"
            else:
                url = f"{self.config.base_url}{self.config.base_path}/logs"

            params = {"hours": str(hours)}
            if level:
                params["level"] = level.upper()

            response = await self.get(url, params=params)

            if isinstance(response, dict) and "logs" in response:
                return response["logs"]  # type: ignore[no-any-return]
            if isinstance(response, list):
                return response  # type: ignore[no-any-return]
            return []

        except Exception as e:
            msg = f"Failed to retrieve logs: {e}"
            raise RuntimeError(msg) from e

    async def get_metrics(
        self, integration_id: str = "", metric_type: str = "performance"
    ) -> dict[str, Any]:
        """Get integration metrics."""
        try:
            # Build metrics endpoint URL
            if integration_id:
                url = f"{self.config.base_url}{self.config.base_path}/integrations/{integration_id}/metrics"
            else:
                url = f"{self.config.base_url}{self.config.base_path}/metrics"

            params = {"type": metric_type}

            response = await self.get(url, params=params)
            return response if isinstance(response, dict) else {}

        except Exception as e:
            msg = f"Failed to retrieve metrics: {e}"
            raise RuntimeError(msg) from e

    async def get_integration_instances(
        self, integration_id: str, status: str = ""
    ) -> list[dict[str, Any]]:
        """Get integration execution instances."""
        try:
            url = f"{self.config.base_url}{self.config.base_path}/integrations/{integration_id}/instances"

            params = {}
            if status:
                params["status"] = status.upper()

            response = await self.get(url, params=params)

            if isinstance(response, dict) and RESPONSE_ITEMS in response:
                return response[RESPONSE_ITEMS]  # type: ignore[no-any-return]
            if isinstance(response, list):
                return response  # type: ignore[no-any-return]
            return []

        except Exception as e:
            msg = f"Failed to retrieve integration instances: {e}"
            raise RuntimeError(msg) from e

    async def get_system_status(self) -> dict[str, Any]:
        """Get overall system status."""
        try:
            url = f"{self.config.base_url}{self.config.base_path}/system/status"
            response = await self.get(url)
            if not isinstance(response, dict):
                msg = f"Unexpected response format: {type(response)}"
                raise RuntimeError(msg)
            return response

        except Exception as e:
            msg = f"Failed to retrieve system status: {e}"
            raise RuntimeError(msg) from e

    async def ping(self) -> dict[str, Any]:
        """Simple connectivity test."""
        try:
            # Try to get basic health information
            health = await self.health_check()

            if health.get("status") == "healthy":
                return {"status": "ok", "message": "OIC is reachable"}
            return {"status": "error", "message": "OIC health check failed"}

        except Exception as e:
            msg = f"Failed to ping OIC: {e}"
            raise RuntimeError(msg) from e

    # Import all standardized dump methods from Oracle OIC v3 documentation
    from .dump_methods import (
        _dump_generic_entity,
        dump_standardized_adapters,
        dump_standardized_REDACTED_LDAP_BIND_PASSWORDistration,
        dump_standardized_certificates,
        dump_standardized_connections,
        dump_standardized_instances,
        dump_standardized_integrations,
        dump_standardized_libraries,
        dump_standardized_lookups,
        dump_standardized_metadata,
        dump_standardized_monitoring,
        dump_standardized_packages,
        dump_standardized_projects,
        dump_standardized_schedules,
        dump_standardized_security,
        dump_standardized_system,
        dump_standardized_tracking,
    )

    # Additional OIC v3 API methods following Oracle documentation
    async def list_packages(self) -> list[dict[str, Any]]:
        """List packages - alias for get_packages."""
        return await self.get_packages()

    async def list_lookups(self) -> list[dict[str, Any]]:
        """List lookups using Oracle OIC v3 API."""
        url = f"{self.config.base_url}{self.config.base_path}/ic/api/integration/v1/lookups"
        params = {"integrationInstance": self.config.instance_id}

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            msg = f"Failed to get lookups: {e}"
            raise RuntimeError(msg) from e

    async def list_libraries(self) -> list[dict[str, Any]]:
        """List libraries using Oracle OIC v3 API."""
        url = f"{self.config.base_url}{self.config.base_path}/ic/api/integration/v1/libraries"
        params = {"integrationInstance": self.config.instance_id}

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            msg = f"Failed to get libraries: {e}"
            raise RuntimeError(msg) from e

    async def list_certificates(self) -> list[dict[str, Any]]:
        """List certificates using Oracle OIC v3 API."""
        url = f"{self.config.base_url}{self.config.base_path}/ic/api/integration/v1/certificates"
        params = {"integrationInstance": self.config.instance_id}

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            msg = f"Failed to get certificates: {e}"
            raise RuntimeError(msg) from e

    async def list_adapters(self) -> list[dict[str, Any]]:
        """List adapters using Oracle OIC v3 API."""
        url = f"{self.config.base_url}{self.config.base_path}/ic/api/integration/v1/adapters"
        params = {"integrationInstance": self.config.instance_id}

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            msg = f"Failed to get adapters: {e}"
            raise RuntimeError(msg) from e

    async def list_projects(self) -> list[dict[str, Any]]:
        """List projects using Oracle OIC v3 API."""
        url = f"{self.config.base_url}{self.config.base_path}/ic/api/integration/v1/projects"
        params = {"integrationInstance": self.config.instance_id}

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            msg = f"Failed to get projects: {e}"
            raise RuntimeError(msg) from e

    async def get_instances(self) -> list[dict[str, Any]]:
        """Get instances using Oracle OIC v3 API."""
        url = f"{self.config.base_url}{self.config.base_path}/ic/api/integration/v1/monitoring/instances"
        params = {"integrationInstance": self.config.instance_id}

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            msg = f"Failed to get instances: {e}"
            raise RuntimeError(msg) from e

    async def get_activity_stream(self, hours: int = 1) -> list[dict[str, Any]]:
        """Get activity stream using Oracle OIC v3 API."""
        url = f"{self.config.base_url}{self.config.base_path}/ic/api/integration/v1/monitoring/instances"
        params = {"integrationInstance": self.config.instance_id, "hours": str(hours)}

        try:
            import httpx

            headers = {"Authorization": f"Bearer {self.auth_token}"}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=headers, timeout=60.0
                )

                if response.status_code != 200:
                    msg = f"API request failed with status {response.status_code}: {response.text}"
                    raise RuntimeError(msg)

                data = response.json()
                return data.get("items", [])

        except Exception as e:
            msg = f"Failed to get activity stream: {e}"
            raise RuntimeError(msg) from e

    async def get_system_info(self) -> dict[str, Any]:
        """Get system info using Oracle OIC v3 API."""
        try:
            return {
                "instance_id": self.config.instance_id,
                "region": self.config.region,
                "base_url": self.config.base_url,
                "api_version": self.config.api_version,
                "status": "active",
            }
        except Exception as e:
            msg = f"Failed to get system info: {e}"
            raise RuntimeError(msg) from e
