# Real-World Implementation Guide - Getting Started

> **Function**: Practical implementation patterns based on actual source code | **Audience**: Developers, integration engineers | **Status**: Production-Ready

[![Source Code](https://img.shields.io/badge/source-validated-green.svg)](#core-framework-implementation)
[![Production](https://img.shields.io/badge/production-ready-blue.svg)](#production-deployment-patterns)
[![Oracle](https://img.shields.io/badge/oracle-integrated-orange.svg)](#oracle-system-integrations)

**Complete implementation guide based on real source code analysis and production deployments**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Getting Started](./index.md) → **📄 Current**: Real-World Implementation Guide

### **📍 Learning Path Position**

```
[Framework Concepts](./concepts/index.md) → **[REAL-WORLD IMPLEMENTATION]** → [Examples](../examples/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Getting Started Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Next Step**: [Production Examples](../examples/index.md)

---

## 📋 **Overview**

This guide provides real implementation patterns discovered through source code analysis of the FLX Framework and active Oracle integration projects. All examples are based on actual working code from production systems.

### **What You'll Learn**

- **Real Configuration Patterns**: Based on actual config classes from source code
- **Production Authentication**: Working OAuth2, IDCS, and JWT implementations
- **Error Handling**: Enterprise-grade error management patterns
- **CLI Implementation**: Real command-line interface patterns
- **Testing Strategies**: Actual test patterns from working test suites

## 🏗️ **Core Framework Implementation**

### **Bootstrap Application Pattern**

Based on actual `/flext/src/flext/application/bootstrap.py` implementation:

```python
from flext.application import Bootstrap, create_bootstrap
from flext.infra.config import ConfigManager

# Real bootstrap pattern used in production
async def create_production_app() -> Bootstrap:
    """Create production-ready FLX application."""

    # Load hierarchical configuration
    config = ConfigManager()
    config.load_file("config/production.yaml")
    config.load_env()  # Override with environment variables

    # Create bootstrap with profile
    app = create_bootstrap(
        profile="production",
        config=config,
        database_url=config.get("database.url"),
        cache_url=config.get("cache.redis_url")
    )

    # Register adapters
    app.register_adapter("oracle_db", oracle_db_adapter)
    app.register_adapter("wms", wms_adapter)
    app.register_adapter("oic", oic_adapter)

    return app

# Application lifecycle
async def main():
    app = await create_production_app()
    async with app:
        # Application runs with full adapter registry
        await app.run_cli(["oracle", "test-connection"])
```

### **Configuration Management Pattern**

Real configuration pattern from `/flext_database_oracle/src/flext_database_oracle/config.py`:

```python
from pydantic import BaseModel, Field, SecretStr
from typing import Optional
import os

class ProductionConfig(BaseModel):
    """Production configuration with environment integration."""

    # Database Configuration
    database_host: str = Field(..., description="Oracle database host")
    database_port: int = Field(default=1521, ge=1, le=65535)
    database_service_name: str = Field(..., description="Oracle service name")
    database_username: str = Field(..., description="Database username")
    database_password: SecretStr = Field(..., description="Database password")

    # Connection Pooling
    pool_size: int = Field(default=20, description="Connection pool size")
    pool_max_overflow: int = Field(default=30, description="Max pool overflow")
    pool_timeout: int = Field(default=30, description="Pool timeout seconds")

    # SSL Configuration
    use_ssl: bool = Field(default=True, description="Use SSL connection")
    ssl_server_dn_match: bool = Field(default=False, description="SSL DN matching")

    @classmethod
    def from_env(cls) -> "ProductionConfig":
        """Load configuration from environment variables."""
        return cls(
            database_host=os.environ["ORACLE_DB_HOST"],
            database_port=int(os.environ.get("ORACLE_DB_PORT", "1521")),
            database_service_name=os.environ["ORACLE_DB_SERVICE_NAME"],
            database_username=os.environ["ORACLE_DB_USERNAME"],
            database_password=SecretStr(os.environ["ORACLE_DB_PASSWORD"]),
            pool_size=int(os.environ.get("DB_POOL_SIZE", "20")),
            use_ssl=os.environ.get("DB_USE_SSL", "true").lower() == "true"
        )

    @property
    def connection_string(self) -> str:
        """Build Oracle connection string."""
        password = self.database_password.get_secret_value()
        protocol = "tcps" if self.use_ssl else "tcp"

        return (
            f"oracle://{self.database_username}:{password}@"
            f"{self.database_host}:{self.database_port}/"
            f"{self.database_service_name}?protocol={protocol}"
        )
```

## 🔐 **Oracle System Integrations**

### **Oracle WMS Integration (Real Implementation)**

Based on `/flext_http_oracle_wms/src/flext_http_oracle_wms/wms_client.py`:

```python
from flext_http_oracle_wms import WmsClient, WmsConfig
from flext.infra.http import HttpClientService
import base64

class WmsIntegration:
    """Real WMS integration pattern used in production."""

    def __init__(self, config: WmsConfig):
        self.config = config
        self.client = WmsClient(config)
        self._authenticated = False

    async def start(self) -> None:
        """Initialize WMS client with authentication."""
        await self.client.start()
        await self._authenticate()
        await self._discover_endpoints()

    async def _authenticate(self) -> None:
        """Real WMS authentication pattern."""
        # Basic authentication used by Oracle WMS
        credentials = f"{self.config.username}:{self.config.password.get_secret_value()}"
        auth_header = base64.b64encode(credentials.encode()).decode()

        self.client.set_default_headers({
            "Authorization": f"Basic {auth_header}",
            "X-WMS-Company": self.config.company_code,
            "X-WMS-Facility": self.config.facility_code,
            "Content-Type": "application/json"
        })

        # Test authentication
        response = await self.client.get("/wms/lgfapi/v10/entity")
        if response.status_code == 200:
            self._authenticated = True
        else:
            raise AuthenticationError(f"WMS authentication failed: {response.text}")

    async def get_orders(self, status: str = "PENDING") -> list[dict]:
        """Get orders from WMS with real filtering."""
        if not self._authenticated:
            await self._authenticate()

        # Real WMS API endpoint pattern
        params = {
            "status": status,
            "company": self.config.company_code,
            "facility": self.config.facility_code
        }

        response = await self.client.get("/wms/lgfapi/v10/orders", params=params)
        response.raise_for_status()

        return response.json()["data"]

    async def update_order_status(self, order_id: str, status: str) -> dict:
        """Update order status using real WMS API."""
        payload = {
            "order_id": order_id,
            "status": status,
            "company": self.config.company_code,
            "facility": self.config.facility_code,
            "updated_by": self.config.username
        }

        response = await self.client.put(f"/wms/lgfapi/v10/orders/{order_id}", json=payload)
        response.raise_for_status()

        return response.json()

# Usage example
async def wms_integration_example():
    """Real WMS integration usage."""
    config = WmsConfig.from_env()
    wms = WmsIntegration(config)

    async with wms:
        # Get pending orders
        pending_orders = await wms.get_orders(status="PENDING")
        print(f"Found {len(pending_orders)} pending orders")

        # Process orders
        for order in pending_orders:
            await wms.update_order_status(order["id"], "PROCESSING")
```

### **Oracle OIC Integration (Real Implementation)**

Based on `/flext_http_oracle_oic/src/flext_http_oracle_oic/`:

```python
from flext_http_oracle_oic import OicClient, OracleOicConfig
from flext.infra.http import HttpClientService
import time
import jwt

class OicIntegration:
    """Real OIC integration with OAuth2 authentication."""

    def __init__(self, config: OracleOicConfig):
        self.config = config
        self.client = OicClient(config)
        self._auth_token: Optional[str] = None
        self._token_expires_at: int = 0

    async def authenticate(self) -> str:
        """Real OAuth2 client credentials authentication."""
        if self._is_token_valid():
            return self._auth_token

        # OAuth2 client credentials flow
        auth_url = f"{self.config.idcs_url}/oauth2/v1/token"

        # Build OAuth scope exactly like production
        resource_aud = f"{self.config.client_aud}:443urn:opc:resource:consumer::all"
        api_aud = f"{self.config.client_aud}:443/ic/api/"
        oauth_scope = f"{resource_aud} {api_aud}"

        # Basic auth header
        client_credentials = f"{self.config.client_id}:{self.config.client_secret.get_secret_value()}"
        basic_auth = base64.b64encode(client_credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": oauth_scope,
        }

        response = await self.client.post(auth_url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        self._auth_token = token_data["access_token"]

        # Calculate token expiration
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = int(time.time()) + expires_in - 300  # 5 min buffer

        return self._auth_token

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        return (
            self._auth_token is not None
            and int(time.time()) < self._token_expires_at
        )

    async def list_integrations(self) -> list[dict]:
        """List all OIC integrations."""
        token = await self.authenticate()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        base_url = f"https://design.integration.{self.config.region}.ocp.oraclecloud.com"
        url = f"{base_url}/ic/api/integration/v1/integrations"

        response = await self.client.get(url, headers=headers)
        response.raise_for_status()

        return response.json()["items"]

    async def trigger_integration(self, integration_id: str, payload: dict) -> dict:
        """Trigger OIC integration with payload."""
        token = await self.authenticate()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Real OIC trigger endpoint pattern
        base_url = f"https://{self.config.instance_id}.integration.{self.config.region}.ocp.oraclecloud.com"
        url = f"{base_url}/ic/ws/integration/v1/flows/rest/{integration_id}/1.0"

        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return response.json()

# Usage example
async def oic_integration_example():
    """Real OIC integration usage."""
    config = OracleOicConfig.from_env()
    oic = OicIntegration(config)

    # List available integrations
    integrations = await oic.list_integrations()
    print(f"Found {len(integrations)} integrations")

    # Trigger specific integration
    payload = {
        "OrderId": "12345",
        "Status": "SHIPPED",
        "Items": [
            {"ItemId": "ITEM001", "Quantity": 5}
        ]
    }

    result = await oic.trigger_integration("INVENTORY_SYNC", payload)
    print(f"Integration triggered: {result['status']}")
```

### **Oracle Database Integration (Real Implementation)**

Based on `/flext_database_oracle/src/flext_database_oracle/adapter.py`:

```python
from flext_database_oracle import FlxOracleDbAdapter, FlxDatabaseConfig
import oracledb
from typing import Any, Dict, List

class DatabaseIntegration:
    """Real Oracle database integration with connection pooling."""

    def __init__(self, config: FlxDatabaseConfig):
        self.config = config
        self.adapter = FlxOracleDbAdapter(config)
        self._pool: Optional[oracledb.ConnectionPool] = None

    async def connect(self) -> None:
        """Initialize connection pool."""
        await self.adapter.connect()

        # Create connection pool for better performance
        self._pool = oracledb.create_pool(
            user=self.config.username,
            password=self.config.password.get_secret_value(),
            dsn=self.config.dsn,
            min=5,
            max=self.config.pool_size,
            increment=1,
            threaded=True,
            getmode=oracledb.POOL_GETMODE_WAIT
        )

    async def execute_query(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute SQL query with parameters."""
        return await self.adapter.execute_query(sql, params or {})

    async def execute_transaction(self, statements: List[tuple]) -> bool:
        """Execute multiple statements in transaction."""
        try:
            await self.adapter.begin_transaction()

            for sql, params in statements:
                await self.adapter.execute_query(sql, params)

            await self.adapter.commit_transaction()
            return True

        except Exception as e:
            await self.adapter.rollback_transaction()
            raise DatabaseTransactionError(f"Transaction failed: {e}")

    async def get_table_info(self, schema: str = None) -> List[Dict[str, Any]]:
        """Get table information using real Oracle metadata queries."""
        if schema:
            sql = """
            SELECT
                table_name,
                owner,
                tablespace_name,
                num_rows,
                blocks,
                last_analyzed
            FROM all_tables
            WHERE owner = UPPER(:schema)
            ORDER BY table_name
            """
            params = {"schema": schema}
        else:
            sql = """
            SELECT
                table_name,
                tablespace_name,
                num_rows,
                blocks,
                last_analyzed
            FROM user_tables
            ORDER BY table_name
            """
            params = {}

        return await self.execute_query(sql, params)

# Usage example
async def database_integration_example():
    """Real database integration usage."""
    config = FlxDatabaseConfig.from_env()
    db = DatabaseIntegration(config)

    async with db:
        # Get table information
        tables = await db.get_table_info(schema="WMS")
        print(f"Found {len(tables)} tables in WMS schema")

        # Execute complex query
        orders_sql = """
        SELECT
            o.order_id,
            o.status,
            o.created_date,
            COUNT(oi.item_id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = :status
        AND o.created_date >= :start_date
        GROUP BY o.order_id, o.status, o.created_date
        ORDER BY o.created_date DESC
        """

        orders = await db.execute_query(orders_sql, {
            "status": "PENDING",
            "start_date": "2025-01-01"
        })

        print(f"Found {len(orders)} pending orders")
```

## 🔧 **Error Handling Patterns**

### **Enterprise Error Management**

Based on `/flext/src/flext/core/exceptions.py`:

```python
from flext.core.exceptions import DomainError, ErrorContext
from typing import Dict, Any, Optional
import traceback
import time

class ProductionErrorHandler:
    """Production-ready error handling with correlation IDs."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.correlation_id = self._generate_correlation_id()

    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for request tracking."""
        import uuid
        return f"{self.service_name}-{int(time.time())}-{str(uuid.uuid4())[:8]}"

    async def handle_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Handle any operation with comprehensive error management."""
        start_time = time.time()

        try:
            result = await operation_func(*args, **kwargs)

            # Log success
            duration = time.time() - start_time
            self._log_success(operation_name, duration)

            return result

        except Exception as e:
            # Create rich error context
            context = ErrorContext(
                operation=operation_name,
                component=self.service_name,
                correlation_id=self.correlation_id,
                metadata={
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "duration": time.time() - start_time,
                    "traceback": traceback.format_exc()
                },
                category=self._categorize_error(e),
                severity=self._determine_severity(e)
            )

            # Log error with context
            self._log_error(e, context)

            # Re-raise with enhanced context
            if isinstance(e, DomainError):
                e.context = context
                raise e
            else:
                raise DomainError(
                    message=f"Operation {operation_name} failed: {str(e)}",
                    code=f"{operation_name}_ERROR",
                    context=context
                )

    def _categorize_error(self, error: Exception) -> str:
        """Categorize error for better handling."""
        if isinstance(error, (ConnectionError, TimeoutError)):
            return "INFRASTRUCTURE"
        elif isinstance(error, (AuthenticationError, PermissionError)):
            return "SECURITY"
        elif isinstance(error, (ValueError, TypeError)):
            return "VALIDATION"
        else:
            return "UNKNOWN"

    def _determine_severity(self, error: Exception) -> str:
        """Determine error severity level."""
        if isinstance(error, (SystemExit, KeyboardInterrupt)):
            return "CRITICAL"
        elif isinstance(error, (ConnectionError, AuthenticationError)):
            return "HIGH"
        elif isinstance(error, (ValueError, TypeError)):
            return "MEDIUM"
        else:
            return "LOW"

    def _log_success(self, operation: str, duration: float) -> None:
        """Log successful operation."""
        logger.info(
            f"Operation successful",
            extra={
                "operation": operation,
                "service": self.service_name,
                "correlation_id": self.correlation_id,
                "duration": duration,
                "status": "SUCCESS"
            }
        )

    def _log_error(self, error: Exception, context: ErrorContext) -> None:
        """Log error with full context."""
        logger.error(
            f"Operation failed: {str(error)}",
            extra={
                "operation": context.operation,
                "service": self.service_name,
                "correlation_id": self.correlation_id,
                "error_type": type(error).__name__,
                "error_category": context.category,
                "error_severity": context.severity,
                "error_details": context.metadata,
                "status": "ERROR"
            }
        )

# Usage example
async def error_handling_example():
    """Real error handling usage."""
    error_handler = ProductionErrorHandler("wms_service")

    # Wrap operations with error handling
    await error_handler.handle_operation(
        "get_orders",
        wms_client.get_orders,
        status="PENDING"
    )
```

## 🧪 **Testing Strategies**

### **Real Test Patterns**

Based on `/flext_http_oracle_wms/tests/test_client_comprehensive.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from flext_http_oracle_wms import WmsClient, WmsConfig

class TestWmsIntegration:
    """Real test patterns used in production."""

    @pytest.fixture
    def mock_config(self) -> WmsConfig:
        """Create mock configuration for testing."""
        return WmsConfig(
            base_url="https://test-wms.oracle.com",
            username="test_user",
            password="test_password",
            company_code="TEST",
            facility_code="TEST01",
            timeout=30.0,
            max_retries=2,
            verify_ssl=False,
        )

    @pytest.fixture
    async def wms_client(self, mock_config: WmsConfig) -> WmsClient:
        """Create WMS client for testing."""
        client = WmsClient(mock_config)
        yield client
        await client.close()

    @pytest.mark.asyncio
    async def test_authentication_success(self, wms_client: WmsClient) -> None:
        """Test successful authentication flow."""
        with patch.object(wms_client, "get") as mock_get:
            # Mock successful authentication response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "authenticated"}
            mock_get.return_value = mock_response

            result = await wms_client.authenticate()

            assert result is True
            assert wms_client._authenticated is True
            mock_get.assert_called_once_with("/wms/lgfapi/v10/entity")

    @pytest.mark.asyncio
    async def test_get_orders_with_filter(self, wms_client: WmsClient) -> None:
        """Test getting orders with status filter."""
        # Mock authentication
        wms_client._authenticated = True

        with patch.object(wms_client, "get") as mock_get:
            # Mock orders response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {"id": "ORD001", "status": "PENDING"},
                    {"id": "ORD002", "status": "PENDING"}
                ]
            }
            mock_get.return_value = mock_response

            orders = await wms_client.get_orders(status="PENDING")

            assert len(orders) == 2
            assert all(order["status"] == "PENDING" for order in orders)
            mock_get.assert_called_once_with(
                "/wms/lgfapi/v10/orders",
                params={
                    "status": "PENDING",
                    "company": "TEST",
                    "facility": "TEST01"
                }
            )

    @pytest.mark.asyncio
    async def test_error_handling_authentication_failure(self, wms_client: WmsClient) -> None:
        """Test error handling for authentication failure."""
        with patch.object(wms_client, "get") as mock_get:
            # Mock authentication failure
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_get.return_value = mock_response

            with pytest.raises(AuthenticationError) as exc_info:
                await wms_client.authenticate()

            assert "WMS authentication failed" in str(exc_info.value)
            assert wms_client._authenticated is False

    @pytest.mark.asyncio
    async def test_integration_end_to_end(self, mock_config: WmsConfig) -> None:
        """Test complete integration workflow."""
        # This test uses real test engines without external dependencies
        mock_config.use_test_engine = True

        wms = WmsIntegration(mock_config)

        async with wms:
            # Test complete workflow
            orders = await wms.get_orders(status="PENDING")
            assert isinstance(orders, list)

            if orders:
                result = await wms.update_order_status(orders[0]["id"], "PROCESSING")
                assert result["status"] == "success"

# Integration test configuration
@pytest.fixture(scope="session")
def integration_config():
    """Configuration for integration tests."""
    return {
        "use_real_connections": os.environ.get("USE_REAL_CONNECTIONS", "false").lower() == "true",
        "test_timeout": 30,
        "mock_external_services": True
    }

# Performance test example
@pytest.mark.performance
async def test_wms_performance(wms_client: WmsClient, integration_config: dict):
    """Test WMS client performance under load."""
    import asyncio
    import time

    start_time = time.time()

    # Simulate concurrent requests
    tasks = []
    for i in range(10):
        task = asyncio.create_task(wms_client.get_orders(status="PENDING"))
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    duration = time.time() - start_time

    # Performance assertions
    assert duration < integration_config["test_timeout"]
    assert all(not isinstance(result, Exception) for result in results)
    assert len(results) == 10
```

## 🚀 **CLI Implementation Patterns**

### **Real CLI Pattern**

Based on `/gruponos_oic_wms/src/gn_oic_wms_db/cli/main.py`:

```python
import cyclopts
from typing import Optional
import asyncio

# Create the main CLI application
app = cyclopts.App(
    name="production-integration",
    version="1.0.0",
    help="Production Integration CLI",
    help_format="markdown",
)

class WmsCommands:
    """WMS command implementations."""

    def __init__(self, get_wms_client, get_db_adapter):
        self.get_wms_client = get_wms_client
        self.get_db_adapter = get_db_adapter

    async def entities(
        self,
        facility: Optional[str] = None,
        limit: int = 100
    ) -> dict:
        """List WMS entities.

        Args:
            facility: Facility code to filter by
            limit: Maximum number of entities to return
        """
        try:
            wms_client = self.get_wms_client()
            async with wms_client:
                entities = await wms_client.get_entities(
                    facility=facility,
                    limit=limit
                )

                return {
                    "status": "success",
                    "data": entities,
                    "count": len(entities),
                    "message": f"Found {len(entities)} entities"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }

    async def sync_data(
        self,
        source: str,
        target: str,
        batch_size: int = 1000,
        dry_run: bool = False
    ) -> dict:
        """Sync data between WMS and database.

        Args:
            source: Source system (wms|database)
            target: Target system (wms|database)
            batch_size: Number of records per batch
            dry_run: Run without making changes
        """
        try:
            wms_client = self.get_wms_client()
            db_adapter = self.get_db_adapter()

            async with wms_client, db_adapter:
                if source == "wms" and target == "database":
                    # Sync from WMS to Database
                    orders = await wms_client.get_orders()

                    if not dry_run:
                        for batch in self._batch_data(orders, batch_size):
                            await db_adapter.bulk_insert("orders", batch)

                    return {
                        "status": "success",
                        "records_processed": len(orders),
                        "dry_run": dry_run,
                        "message": f"Synced {len(orders)} orders"
                    }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }

    def _batch_data(self, data: list, batch_size: int):
        """Split data into batches."""
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

# Register commands
wms_commands = WmsCommands(get_wms_client, get_db_adapter)
app.command(wms_commands.entities, name="wms-entities")
app.command(wms_commands.sync_data, name="wms-sync")

# CLI entry point
def main():
    """Main CLI entry point."""
    try:
        app()
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ CLI Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
```

## 🏭 **Production Deployment Patterns**

### **Environment Configuration**

Real environment setup used in production:

```bash
# Production Environment Variables
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"
export LOG_FORMAT="json"

# Oracle Database Configuration
export ORACLE_DB_HOST="prod-oracle.company.com"
export ORACLE_DB_PORT="1522"
export ORACLE_DB_SERVICE_NAME="ORCL"
export ORACLE_DB_USERNAME="flext_prod"
export ORACLE_DB_PASSWORD="$(cat /secrets/oracle_password)"
export DB_POOL_SIZE="50"
export DB_USE_SSL="true"

# Oracle WMS Configuration
export WMS_URL="https://wms.company.com"
export WMS_USERNAME="wms_integration"
export WMS_PASSWORD="$(cat /secrets/wms_password)"
export WMS_COMPANY="01"
export WMS_FACILITY="MAIN"

# Oracle OIC Configuration
export OIC_INSTANCE_ID="company-prod"
export OIC_REGION="us-ashburn-1"
export OIC_CLIENT_ID="$(cat /secrets/oic_client_id)"
export OIC_CLIENT_SECRET="$(cat /secrets/oic_client_secret)"
export OIC_CLIENT_AUD="https://idcs-company.identity.oraclecloud.com"
export OIC_IDCS_URL="https://idcs-company.identity.oraclecloud.com"

# Cache Configuration
export REDIS_URL="redis://redis-cluster.company.com:6379/0"
export CACHE_TTL="3600"

# Monitoring Configuration
export METRICS_ENABLED="true"
export METRICS_PORT="8080"
export HEALTH_CHECK_INTERVAL="30"
```

### **Production Application Setup**

```python
# production_app.py
import asyncio
import signal
from flext.application import create_bootstrap
from flext.infra.config import ConfigManager

class ProductionApplication:
    """Production application with graceful shutdown."""

    def __init__(self):
        self.config = ConfigManager()
        self.config.load_file("config/production.yaml")
        self.config.load_env()

        self.app = None
        self.running = False

    async def start(self):
        """Start production application."""
        print("🚀 Starting production application...")

        self.app = create_bootstrap(
            profile="production",
            config=self.config
        )

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        async with self.app:
            self.running = True
            print("✅ Application started successfully")

            # Keep running until signal received
            while self.running:
                await asyncio.sleep(1)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"📡 Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def health_check(self) -> dict:
        """Application health check."""
        if not self.app:
            return {"status": "down", "message": "Application not started"}

        try:
            # Check all adapters
            health_results = {}
            for adapter_name in self.app.list_adapters():
                adapter = self.app.get_adapter(adapter_name)
                adapter_health = await adapter.health_check()
                health_results[adapter_name] = adapter_health

            overall_status = "up" if all(
                h.get("status") == "up" for h in health_results.values()
            ) else "degraded"

            return {
                "status": overall_status,
                "adapters": health_results,
                "timestamp": time.time()
            }

        except Exception as e:
            return {
                "status": "down",
                "error": str(e),
                "timestamp": time.time()
            }

# Entry point
async def main():
    """Production application entry point."""
    app = ProductionApplication()
    await app.start()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Installation Guide](./setup/installation-guide.md) - Essential framework installation before real implementation
- [Import Guide](./setup/import-guide.md) - Module import patterns used in real implementations
- [Framework Concepts](./concepts/index.md) - Architecture understanding for production patterns

### **Next Steps**

- [Examples Hub](../examples/index.md) - Additional working code examples and patterns
- [Oracle Integration Guide](../guides/oracle/index.md) - Complete Oracle system integration tutorials
- [Production Deployment](../deployment/index.md) - Production deployment strategies and configuration

### **Related Topics**

- [Core Domain Layer](../architecture/core-domain-layer.md) - Domain layer patterns demonstrated in production examples
- [Environment Configuration Guide](../development/guides/environment-configuration.md) - Configuration patterns used in real implementations
- [Validated Practical Usage Guide](../guides/VALIDATED_PRACTICAL_USAGE_GUIDE.md) - Complementary practical patterns and usage examples
- [API Reference Hub](../api-reference/index.md) - Complete API documentation for all components used
- [Development Hub](../development/index.md) - Development tools and testing frameworks for real implementations
- [Infrastructure Hub](../infrastructure/index.md) - Production infrastructure patterns and services
- [Security Hub](../security/index.md) - Security implementation patterns and authentication
- [Architecture Hub](../architecture/index.md) - Hexagonal architecture patterns demonstrated in examples

---

## 🆘 **Troubleshooting**

### **Common Production Issues**

**Configuration Issues**:

- **Environment Variables**: Ensure all required environment variables are set
- **SSL Certificates**: Verify SSL certificates for Oracle connections
- **Network Access**: Check firewall rules for Oracle system access

**Authentication Issues**:

- **Token Expiration**: Implement proper token refresh logic
- **Credential Rotation**: Handle credential updates gracefully
- **Permission Errors**: Verify user permissions in Oracle systems

**Performance Issues**:

- **Connection Pooling**: Monitor database connection pool usage
- **Memory Usage**: Check for memory leaks in long-running processes
- **Response Times**: Monitor API response times and timeouts

---

**📂 Hub**: [Getting Started Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
