"""Adapter Oracle OIC com métodos dinâmicos baseados na declaração da API."""

from typing import Any

try:
    from .api_generator import DynamicApiMixin
    from .standalone_adapter import StandaloneOracleOicHttpAdapter
    from .standalone_config import StandaloneOracleOicConfig
except ImportError:
    from api_generator import DynamicApiMixin
    from standalone_adapter import StandaloneOracleOicHttpAdapter
    from standalone_config import StandaloneOracleOicConfig


class DynamicOracleOicAdapter(DynamicApiMixin, StandaloneOracleOicHttpAdapter):
    """Adapter Oracle OIC com todos os métodos da API gerados dinamicamente.

    Este adapter herda toda a funcionalidade básica do StandaloneOracleOicHttpAdapter
    e adiciona automaticamente todos os métodos da API Oracle OIC baseados na
    declaração declarativa.

    Métodos disponíveis incluem:
    - CRUD para integrations, connections, packages, projects, lookups, libraries, certificates
    - Monitoramento: instances, errors, activity streams
    - Operações específicas: activate, deactivate, clone, test, validate
    - Gerenciamento de ambiente: CORS domains
    """

    def __init__(self, config: Any = None, **kwargs: Any) -> None:
        """Initialize dynamic adapter."""
        if config is None:
            config = StandaloneOracleOicConfig()

        super().__init__(config=config, **kwargs)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Async context manager exit."""
        await self.disconnect()
        return False


class OracleOicApiClient:
    """Cliente de alto nível para Oracle Integration Cloud.

    Fornece uma interface amigável para todas as operações da API OIC
    """

    def __init__(self, config: Any = None) -> None:
        """Initialize client."""
        self.config = config or StandaloneOracleOicConfig()
        self.adapter = DynamicOracleOicAdapter(config=self.config)

    async def connect(self) -> None:
        """Connect to OIC."""
        await self.adapter.connect()

    async def disconnect(self) -> None:
        """Disconnect from OIC."""
        await self.adapter.disconnect()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Async context manager exit."""
        await self.disconnect()
        return False

    # Convenience methods for common operations

    async def list_integrations(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List integrations with filters."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_integrations(**params)

    async def activate_integration(self, integration_id: str) -> Any:
        """Activate an integration."""
        return await self.adapter.activate_integration(id=integration_id)

    async def deactivate_integration(self, integration_id: str) -> Any:
        """Deactivate an integration."""
        return await self.adapter.deactivate_integration(id=integration_id)

    async def get_integration_status(self, integration_id: str) -> Any:
        """Get integration activation status."""
        return await self.adapter.get_activation_status(id=integration_id)

    async def clone_integration(
        self, integration_id: str, clone_data: dict[str, Any]
    ) -> Any:
        """Clone an integration."""
        return await self.adapter.clone_integration(
            id=integration_id,
            clone_request=clone_data,
        )

    async def list_connections(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List connections with filters."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_connections(**params)

    async def test_connection(self, connection_id: str) -> Any:
        """Test a connection."""
        return await self.adapter.test_connection(id=connection_id)

    async def validate_connection(self, connection_id: str) -> Any:
        """Validate a connection."""
        return await self.adapter.validate_connection(id=connection_id)

    async def monitor_instances(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """Monitor integration instances."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_instances(**params)

    async def monitor_errors(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """Monitor integration errors."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_errors(**params)

    async def resubmit_error(self, error_id: str) -> Any:
        """Resubmit an error."""
        return await self.adapter.resubmit_error(id=error_id)

    async def discard_error(self, error_id: str) -> Any:
        """Discard an error."""
        return await self.adapter.discard_error(id=error_id)

    async def list_packages(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List packages."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_packages(**params)

    async def load_sample_packages(self) -> Any:
        """Load sample packages."""
        return await self.adapter.load_sample_packages()

    async def list_projects(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List projects."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_projects(**params)

    async def clone_project(self, project_id: str, clone_data: dict[str, Any]) -> Any:
        """Clone a project."""
        return await self.adapter.clone_project(id=project_id, clone_request=clone_data)

    async def list_lookups(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List lookups."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_lookups(**params)

    async def clone_lookup(self, lookup_name: str, clone_data: dict[str, Any]) -> Any:
        """Clone a lookup."""
        return await self.adapter.clone_lookup(
            name=lookup_name,
            clone_request=clone_data,
        )

    async def list_libraries(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List libraries."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_libraries(**params)

    async def list_certificates(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List certificates."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_certificates(**params)

    async def list_adapter_bundles(
        self, limit: int = 50, offset: int = 0, **filters: Any
    ) -> Any:
        """List adapter bundles."""
        params = {"limit": limit, "offset": offset}
        params.update(filters)
        return await self.adapter.get_adapter_bundles(**params)

    async def get_cors_domains(self) -> Any:
        """Get CORS domains."""
        return await self.adapter.get_cors_domains()

    async def add_cors_domain(self, domain_data: dict[str, Any]) -> Any:
        """Add CORS domain."""
        return await self.adapter.create_cors_domain(domain_data=domain_data)

    def list_available_methods(self) -> Any:
        """List all available API methods."""
        return self.adapter.list_available_methods()

    def get_method_info(self, method_name: str) -> Any:
        """Get information about a specific method."""
        return self.adapter.get_method_info(method_name)


# Funções utilitárias


def create_oic_client(config: Any = None) -> OracleOicApiClient:
    """Factory function to create OIC client."""
    return OracleOicApiClient(config)


def create_oic_adapter(config: Any = None) -> DynamicOracleOicAdapter:
    """Factory function to create OIC adapter."""
    return DynamicOracleOicAdapter(config)


async def quick_oic_test(config: Any = None) -> dict[str, Any]:
    """Quick test of OIC connectivity."""
    async with create_oic_client(config) as client:
        try:
            # Test basic connectivity
            integrations = await client.list_integrations(limit=1)
            connections = await client.list_connections(limit=1)

            return {
                "status": "SUCCESS",
                "integrations_count": integrations.get("count", 0),
                "connections_count": connections.get("count", 0),
                "available_methods": len(client.list_available_methods()),
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
