"""Exemplos FLX KISS - VERSÃO EXTREMA.

Demonstra como projetos ficam ULTRA-SIMPLES com versão KISS.
10 linhas de código fazem o que antes eram 1000+!
"""

from __future__ import annotations

import asyncio

from flx import FlxProject, flx_project  # type: ignore[attr-defined]
from flx.declarative.mixins import (
    FlxDatabaseMixin,
    FlxHttpClientMixin,
    FlxLdapMixin,
    FlxSyncMixin,
    FlxWmsMixin,
)
from pydantic import Field

# ==================================================================================
# EXEMPLO KISS 1: Database Oracle (5 linhas!)
# ==================================================================================


@flx_project("database-oracle")
class SimpleOracleProject(FlxProject, FlxDatabaseMixin):
    """Oracle - 5 linhas vs 500+ anteriores."""

    enable_sql_tracing: bool = Field(False, description="SQL tracing")

    @property
    def project_name(self) -> str:
        return self.database_schema or "oracle-kiss"


# ==================================================================================
# EXEMPLO KISS 2: WMS Sync (15 linhas!)
# ==================================================================================


@flx_project("sync-flx_project")
class WmsSyncProject(FlxProject, FlxDatabaseMixin, FlxWmsMixin, FlxSyncMixin):
    """WMS Sync - 15 linhas vs 1500+ anteriores."""

    client_name: str = Field(..., description="Cliente")
    field_mappings: dict[str, dict[str, str]] = Field(
        default_factory=lambda: {"orders": {"order_id": "ORDER_NUMBER"}},
        description="Mapeamentos",
    )

    @property
    def project_name(self) -> str:
        return self.client_name or "wms-sync-kiss"

    async def custom_transform_order(self, wms_order: dict) -> dict:
        """Apenas transformação específica."""
        return {"order_number": wms_order.get("order_id"), "client": self.client_name}


# ==================================================================================
# EXEMPLO KISS 3: LDAP (8 linhas!)
# ==================================================================================


@flx_project("ldap")
class SimpleLdapProject(FlxProject, FlxLdapMixin):
    """LDAP - 8 linhas vs 800+ anteriores."""

    company_domain: str = Field(..., description="Domínio")

    @property
    def project_name(self) -> str:
        return self.company_domain or "ldap-kiss"

    async def create_user(self, username: str, email: str) -> dict:
        """Apenas criação específica."""
        return {"dn": f"uid={username},dc={self.company_domain}", "mail": email}


# ==================================================================================
# EXEMPLO KISS 4: HTTP Integration (6 linhas!)
# ==================================================================================


@flx_project("integration-flx_project")
class HttpIntegrationProject(FlxProject, FlxHttpClientMixin):
    """HTTP Integration - 6 linhas vs 600+ anteriores."""

    webhook_secret: str = Field(..., description="Secret", repr=False)

    @property
    def project_name(self) -> str:
        return "http-integration-kiss"

    async def handle_webhook(self, data: dict) -> dict:
        """Apenas handling específico."""
        return {"status": "processed", "id": data.get("id")}


# ==================================================================================
# DEMONSTRAÇÃO KISS
# ==================================================================================


def print_header() -> None:
    pass


def print_footer() -> None:
    pass


async def demonstrate_kiss_power() -> None:
    """Demonstra o poder extremo da versão KISS."""
    print_header()

    # 1. Oracle (antes: 500+ linhas, agora: 1 linha!)
    SimpleOracleProject(
        database_url="oracle://user:pass@host/service",
        database_schema="SCHEMA",
        enable_sql_tracing=False,
        auto_reconnect=True,
        connection_pool_size=10,
    )

    # 2. WMS Sync (antes: 1500+ linhas, agora: 5 linhas!)
    WmsSyncProject(
        database_url="oracle://...",
        database_schema="SCHEMA",
        enable_sql_tracing=False,
        auto_reconnect=True,
        connection_pool_size=10,
        wms_tenant="tenant1",
        wms_environment="production",
        field_mappings={"orders": {"order_id": "ORDER_NUMBER"}},
        enable_webhook_mode=False,
        webhook_secret="secret",
        client_name="ACME",
        sync_interval=300,
        batch_size=100,
        enable_parallel_sync=True,
        max_workers=4,
        sync_timeout=3600,
    )

    # 3. LDAP (antes: 800+ linhas, agora: 2 linhas!)
    SimpleLdapProject(
        ldap_server="ldap.company.com",
        ldap_port=389,
        bind_dn="cn=admin,dc=company,dc=com",
        bind_password="password",
        base_dn="dc=company,dc=com",
        use_ssl=False,
        company_domain="company.com",
    )

    # 4. HTTP Integration (exemplo)
    HttpIntegrationProject(
        base_url="https://api.example.com",
        timeout=30.0,
        max_retries=3,
        headers={},
        verify_ssl=True,
        webhook_secret="supersecret",
    )

    print_footer()


if __name__ == "__main__":
    asyncio.run(demonstrate_kiss_power())
