# Oracle Integration Quickstart - Getting Started

> **Function**: Fast Oracle system integration setup | **Audience**: Oracle developers, integration engineers | **Status**: Production-Ready

[![Oracle WMS](https://img.shields.io/badge/Oracle-WMS-blue.svg)](#oracle-wms-setup)
[![Oracle OIC](https://img.shields.io/badge/Oracle-OIC-green.svg)](#oracle-oic-setup)
[![Oracle DB](https://img.shields.io/badge/Oracle-Database-orange.svg)](#oracle-database-setup)

**Get Oracle systems integrated with FLX Framework in 10 minutes - based on real production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Getting Started](./index.md) → **📄 Current**: Oracle Integration Quickstart

### **📍 Learning Path Position**

```
[Quickstart](./basics/quickstart.md) → **[ORACLE INTEGRATION]** → [Real-World Guide](./real-world-implementation-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Getting Started Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Next Step**: [Oracle Guides](../guides/oracle/index.md)

---

## 📋 **Overview**

This quickstart guide shows you how to integrate Oracle systems (WMS, OIC, Database) with FLX Framework using real patterns from production implementations. All examples are based on actual working code from `/flx-*-oracle-*` projects.

### **What You'll Build**

- **Oracle WMS Integration**: Connect to Oracle Warehouse Management System
- **Oracle OIC Integration**: Integrate with Oracle Integration Cloud
- **Oracle Database**: Connect to Oracle Database with connection pooling
- **Unified CLI**: Command-line tools for all Oracle operations

## 🚀 **10-Minute Oracle Setup**

### **Step 1: Install Oracle Adapters**

```bash
# Navigate to workspace
cd /home/marlonsc/pyauto

# Activate virtual environment
source .venv/bin/activate

# Install Oracle adapters
cd flx-database-oracle && pip install -e . && cd ..
cd flx-http-oracle-wms && pip install -e . && cd ..
cd flx-http-oracle-oic && pip install -e . && cd ..
```

### **Step 2: Configure Environment**

Create `.env` file with your Oracle credentials:

```bash
# .env file - based on real production configuration
# Oracle Database Configuration
ORACLE_DB_HOST="your-oracle-host.com"
ORACLE_DB_PORT="1521"
ORACLE_DB_SERVICE_NAME="ORCL"
ORACLE_DB_USERNAME="your_db_user"
ORACLE_DB_PASSWORD="your_db_password"

# Oracle WMS Configuration
WMS_URL="https://your-wms.oracle.com"
WMS_USERNAME="wms_user"
WMS_PASSWORD="wms_password"
WMS_COMPANY="01"
WMS_FACILITY="01"

# Oracle OIC Configuration
OIC_INSTANCE_ID="your-oic-instance"
OIC_REGION="us-ashburn-1"
OIC_CLIENT_ID="your_client_id"
OIC_CLIENT_SECRET="your_client_secret"
OIC_CLIENT_AUD="https://your-idcs.identity.oraclecloud.com"
OIC_IDCS_URL="https://your-idcs.identity.oraclecloud.com"
```

### **Step 3: Test Oracle Database Connection**

```python
# test_oracle_db.py - based on real implementation
import asyncio
from flx_database_oracle import FlxOracleDbAdapter, FlxDatabaseConfig

async def test_oracle_database():
    """Test Oracle database connection."""

    # Load configuration from environment
    config = FlxDatabaseConfig.from_env()
    adapter = FlxOracleDbAdapter(config)

    try:
        # Connect to database
        await adapter.connect()
        print("✅ Oracle Database connected successfully")

        # Test query - real Oracle system tables
        tables = await adapter.execute_query("""
            SELECT table_name, owner
            FROM all_tables
            WHERE owner NOT IN ('SYS', 'SYSTEM', 'CTXSYS', 'MDSYS', 'OLAPSYS')
            AND rownum <= 10
            ORDER BY table_name
        """)

        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['OWNER']}.{table['TABLE_NAME']}")

        # Test connection info
        info = await adapter.get_connection_info()
        print(f"🔗 Connected to: {info['database_name']} (Version: {info['version']})")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    finally:
        await adapter.close()

# Run test
asyncio.run(test_oracle_database())
```

### **Step 4: Test Oracle WMS Integration**

```python
# test_oracle_wms.py - based on real WMS client implementation
import asyncio
from flx_http_oracle_wms import WmsClient, WmsConfig

async def test_oracle_wms():
    """Test Oracle WMS integration."""

    # Load WMS configuration
    config = WmsConfig.from_env()
    client = WmsClient(config)

    try:
        # Start WMS client (includes authentication)
        await client.start()
        print("✅ Oracle WMS authenticated successfully")

        # Test WMS operations - real endpoints
        print("🔍 Discovering WMS entities...")
        entities = await client.get_entities()
        print(f"📋 Available entities: {', '.join(entities[:5])}...")

        # Test specific WMS query
        if "orders" in entities:
            orders = await client.get_orders(limit=5)
            print(f"📦 Found {len(orders)} recent orders")

            for order in orders[:3]:
                print(f"  - Order {order.get('order_id', 'N/A')}: {order.get('status', 'N/A')}")

        # Test WMS facility info
        facility_info = await client.get_facility_info()
        print(f"🏭 Facility: {facility_info.get('facility_code', 'N/A')} - {facility_info.get('name', 'N/A')}")

    except Exception as e:
        print(f"❌ WMS connection failed: {e}")
    finally:
        await client.close()

# Run test
asyncio.run(test_oracle_wms())
```

### **Step 5: Test Oracle OIC Integration**

```python
# test_oracle_oic.py - based on real OIC implementation
import asyncio
from flx_http_oracle_oic import OicClient, OracleOicConfig

async def test_oracle_oic():
    """Test Oracle OIC integration."""

    # Load OIC configuration
    config = OracleOicConfig.from_env()
    client = OicClient(config)

    try:
        # Authenticate with OIC (OAuth2)
        token = await client.authenticate()
        print("✅ Oracle OIC authenticated successfully")
        print(f"🎫 Token: {token[:20]}...")

        # List integrations
        print("🔍 Listing OIC integrations...")
        integrations = await client.list_integrations()
        print(f"⚙️  Found {len(integrations)} integrations")

        for integration in integrations[:3]:
            print(f"  - {integration.get('name', 'N/A')}: {integration.get('status', 'N/A')}")

        # Test integration details
        if integrations:
            first_integration = integrations[0]
            integration_id = first_integration.get('id')

            details = await client.get_integration_details(integration_id)
            print(f"📄 Integration '{details.get('name')}' has {len(details.get('connections', []))} connections")

        print("✨ OIC integration test completed successfully")

    except Exception as e:
        print(f"❌ OIC connection failed: {e}")

# Run test
asyncio.run(test_oracle_oic())
```

## 🔧 **Complete Oracle Integration**

### **Unified Oracle Application**

```python
# oracle_integration_app.py - complete Oracle integration
import asyncio
from flx.application import create_bootstrap
from flx_database_oracle import FlxOracleDbAdapter, FlxDatabaseConfig
from flx_http_oracle_wms import WmsClient, WmsConfig
from flx_http_oracle_oic import OicClient, OracleOicConfig

class OracleIntegrationApp:
    """Complete Oracle integration application."""

    def __init__(self):
        # Initialize configurations
        self.db_config = FlxDatabaseConfig.from_env()
        self.wms_config = WmsConfig.from_env()
        self.oic_config = OracleOicConfig.from_env()

        # Initialize clients
        self.db_adapter = FlxOracleDbAdapter(self.db_config)
        self.wms_client = WmsClient(self.wms_config)
        self.oic_client = OicClient(self.oic_config)

    async def start(self):
        """Start all Oracle connections."""
        print("🚀 Starting Oracle integration...")

        # Connect to Oracle Database
        await self.db_adapter.connect()
        print("✅ Oracle Database connected")

        # Connect to Oracle WMS
        await self.wms_client.start()
        print("✅ Oracle WMS connected")

        # Authenticate with Oracle OIC
        await self.oic_client.authenticate()
        print("✅ Oracle OIC authenticated")

        print("🎉 All Oracle systems connected successfully!")

    async def sync_wms_to_database(self):
        """Sync WMS data to Oracle Database."""
        print("🔄 Syncing WMS data to database...")

        try:
            # Get orders from WMS
            orders = await self.wms_client.get_orders(status="PENDING")
            print(f"📦 Retrieved {len(orders)} pending orders from WMS")

            # Insert into database
            for order in orders:
                await self.db_adapter.execute_query("""
                    INSERT INTO wms_orders (
                        order_id, status, facility_code, created_date, item_count
                    ) VALUES (
                        :order_id, :status, :facility_code, SYSDATE, :item_count
                    )
                """, {
                    "order_id": order.get("order_id"),
                    "status": order.get("status"),
                    "facility_code": order.get("facility_code"),
                    "item_count": len(order.get("items", []))
                })

            print(f"✅ Synced {len(orders)} orders to database")

        except Exception as e:
            print(f"❌ Sync failed: {e}")

    async def trigger_oic_integration(self, integration_name: str, data: dict):
        """Trigger OIC integration with data."""
        print(f"⚡ Triggering OIC integration: {integration_name}")

        try:
            result = await self.oic_client.trigger_integration(integration_name, data)
            print(f"✅ Integration triggered successfully: {result.get('status')}")
            return result

        except Exception as e:
            print(f"❌ Integration trigger failed: {e}")
            return None

    async def health_check(self):
        """Check health of all Oracle connections."""
        health = {
            "database": False,
            "wms": False,
            "oic": False
        }

        try:
            # Test database
            await self.db_adapter.execute_query("SELECT 1 FROM DUAL")
            health["database"] = True
        except:
            pass

        try:
            # Test WMS
            await self.wms_client.get_entities()
            health["wms"] = True
        except:
            pass

        try:
            # Test OIC
            await self.oic_client.list_integrations()
            health["oic"] = True
        except:
            pass

        return health

    async def close(self):
        """Close all connections."""
        await self.db_adapter.close()
        await self.wms_client.close()
        print("🔌 All Oracle connections closed")

# Usage example
async def main():
    """Main application example."""
    app = OracleIntegrationApp()

    try:
        # Start all Oracle connections
        await app.start()

        # Perform operations
        await app.sync_wms_to_database()

        # Trigger OIC integration
        await app.trigger_oic_integration("INVENTORY_SYNC", {
            "source": "WMS",
            "timestamp": "2025-06-11T10:00:00Z",
            "data": {"sync_type": "incremental"}
        })

        # Health check
        health = await app.health_check()
        print(f"🏥 Health status: {health}")

    finally:
        await app.close()

# Run application
if __name__ == "__main__":
    asyncio.run(main())
```

## 💻 **Oracle CLI Tools**

### **Unified Oracle CLI**

```python
# oracle_cli.py - unified CLI for all Oracle operations
import asyncio
import cyclopts
from typing import Optional, List
from oracle_integration_app import OracleIntegrationApp

# Create CLI app
app = cyclopts.App(
    name="oracle-cli",
    version="1.0.0",
    help="Oracle Integration CLI",
    help_format="markdown"
)

# Initialize Oracle app
oracle_app = OracleIntegrationApp()

@app.command
async def db_tables(
    schema: Optional[str] = None,
    limit: int = 10
) -> None:
    """List Oracle database tables.

    Args:
        schema: Schema name to filter tables
        limit: Maximum number of tables to show
    """
    try:
        await oracle_app.db_adapter.connect()

        if schema:
            sql = """
            SELECT table_name, owner, num_rows
            FROM all_tables
            WHERE owner = UPPER(:schema)
            AND rownum <= :limit
            ORDER BY table_name
            """
            params = {"schema": schema, "limit": limit}
        else:
            sql = """
            SELECT table_name, num_rows
            FROM user_tables
            WHERE rownum <= :limit
            ORDER BY table_name
            """
            params = {"limit": limit}

        tables = await oracle_app.db_adapter.execute_query(sql, params)

        print(f"📊 Database Tables ({len(tables)} found):")
        for table in tables:
            owner = table.get('OWNER', 'USER')
            name = table['TABLE_NAME']
            rows = table.get('NUM_ROWS', 'N/A')
            print(f"  {owner}.{name} ({rows} rows)")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await oracle_app.db_adapter.close()

@app.command
async def wms_orders(
    status: str = "PENDING",
    facility: Optional[str] = None,
    limit: int = 10
) -> None:
    """List Oracle WMS orders.

    Args:
        status: Order status filter
        facility: Facility code filter
        limit: Maximum number of orders to show
    """
    try:
        await oracle_app.wms_client.start()

        orders = await oracle_app.wms_client.get_orders(
            status=status,
            facility=facility,
            limit=limit
        )

        print(f"📦 WMS Orders ({len(orders)} found, status={status}):")
        for order in orders:
            order_id = order.get('order_id', 'N/A')
            order_status = order.get('status', 'N/A')
            items = len(order.get('items', []))
            print(f"  {order_id}: {order_status} ({items} items)")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await oracle_app.wms_client.close()

@app.command
async def oic_integrations() -> None:
    """List Oracle OIC integrations."""
    try:
        await oracle_app.oic_client.authenticate()

        integrations = await oracle_app.oic_client.list_integrations()

        print(f"⚙️  OIC Integrations ({len(integrations)} found):")
        for integration in integrations:
            name = integration.get('name', 'N/A')
            status = integration.get('status', 'N/A')
            version = integration.get('version', 'N/A')
            print(f"  {name} (v{version}): {status}")

    except Exception as e:
        print(f"❌ Error: {e}")

@app.command
async def sync_data(
    source: str,
    target: str,
    dry_run: bool = False
) -> None:
    """Sync data between Oracle systems.

    Args:
        source: Source system (wms|database|oic)
        target: Target system (wms|database|oic)
        dry_run: Preview changes without applying
    """
    try:
        await oracle_app.start()

        if source == "wms" and target == "database":
            if dry_run:
                orders = await oracle_app.wms_client.get_orders(status="PENDING")
                print(f"🔍 Would sync {len(orders)} orders from WMS to Database")
            else:
                await oracle_app.sync_wms_to_database()

        elif source == "database" and target == "oic":
            # Trigger OIC integration with database data
            result = await oracle_app.trigger_oic_integration("DATA_EXPORT", {
                "source": "database",
                "export_type": "incremental"
            })
            print(f"✅ OIC integration triggered: {result}")

        else:
            print(f"❌ Unsupported sync: {source} -> {target}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await oracle_app.close()

@app.command
async def health() -> None:
    """Check health of all Oracle systems."""
    try:
        await oracle_app.start()

        health = await oracle_app.health_check()

        print("🏥 Oracle Systems Health:")
        for system, status in health.items():
            icon = "✅" if status else "❌"
            print(f"  {icon} {system.upper()}: {'healthy' if status else 'unhealthy'}")

        overall = "✅ All systems healthy" if all(health.values()) else "⚠️  Some systems unhealthy"
        print(f"\n{overall}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await oracle_app.close()

# CLI entry point
def main():
    """Main CLI entry point."""
    app()

if __name__ == "__main__":
    main()
```

### **Using the Oracle CLI**

```bash
# Make CLI executable
chmod +x oracle_cli.py

# Database operations
python oracle_cli.py db-tables --schema=WMS --limit=20
python oracle_cli.py db-tables  # List user tables

# WMS operations
python oracle_cli.py wms-orders --status=PENDING --limit=10
python oracle_cli.py wms-orders --status=SHIPPED --facility=01

# OIC operations
python oracle_cli.py oic-integrations

# Data synchronization
python oracle_cli.py sync-data --source=wms --target=database --dry-run
python oracle_cli.py sync-data --source=wms --target=database

# Health checks
python oracle_cli.py health
```

## 🔧 **Configuration Templates**

### **Production Configuration**

```yaml
# config/oracle_production.yaml
oracle:
  database:
    host: "${ORACLE_DB_HOST}"
    port: ${ORACLE_DB_PORT:1521}
    service_name: "${ORACLE_DB_SERVICE_NAME}"
    username: "${ORACLE_DB_USERNAME}"
    password: "${ORACLE_DB_PASSWORD}"
    pool_size: ${DB_POOL_SIZE:20}
    use_ssl: ${DB_USE_SSL:true}
    connection_timeout: 30

  wms:
    base_url: "${WMS_URL}"
    username: "${WMS_USERNAME}"
    password: "${WMS_PASSWORD}"
    company_code: "${WMS_COMPANY:01}"
    facility_code: "${WMS_FACILITY:01}"
    timeout: 30.0
    max_retries: 3

  oic:
    instance_id: "${OIC_INSTANCE_ID}"
    region: "${OIC_REGION}"
    client_id: "${OIC_CLIENT_ID}"
    client_secret: "${OIC_CLIENT_SECRET}"
    client_aud: "${OIC_CLIENT_AUD}"
    idcs_url: "${OIC_IDCS_URL}"

  monitoring:
    health_check_interval: 60
    metrics_enabled: true
    log_level: "INFO"
```

### **Development Configuration**

```yaml
# config/oracle_development.yaml
oracle:
  database:
    host: "localhost"
    port: 1521
    service_name: "XE"
    username: "hr"
    password: "hr"
    pool_size: 5
    use_ssl: false

  wms:
    base_url: "https://test-wms.oracle.com"
    username: "test_user"
    password: "test_password"
    company_code: "TEST"
    facility_code: "TEST01"
    timeout: 10.0

  oic:
    instance_id: "test-instance"
    region: "us-ashburn-1"
    # Use test credentials

  monitoring:
    health_check_interval: 30
    metrics_enabled: false
    log_level: "DEBUG"
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Installation Guide](./setup/installation-guide.md) - FLX Framework and Oracle adapters installation
- [Import Guide](./setup/import-guide.md) - Oracle adapter import patterns and configuration
- [Environment Setup](https://docs.oracle.com/en/cloud/) - Oracle Cloud account and credentials

### **Next Steps**

- [Oracle Integration Guide](../guides/oracle/index.md) - Complete Oracle integration documentation
- [Real-World Implementation](./real-world-implementation-guide.md) - Production patterns and best practices
- [Oracle Examples](../examples/oracle-wms/index.md) - Working Oracle integration examples

### **Related Topics**

- [API Reference](../api-reference/index.md) - Oracle adapter API documentation
- [Architecture Guide](../architecture/index.md) - Hexagonal architecture with Oracle adapters
- [Development Tools](../development/index.md) - Testing and debugging Oracle integrations
- [Security Guide](../security/index.md) - Oracle authentication and security patterns
- [Infrastructure Guide](../infrastructure/index.md) - Production Oracle infrastructure setup

---

## 🆘 **Troubleshooting**

### **Common Oracle Issues**

**Database Connection Issues**:

- **TNS Error**: Check `ORACLE_DB_HOST` and `ORACLE_DB_SERVICE_NAME`
- **Authentication**: Verify `ORACLE_DB_USERNAME` and `ORACLE_DB_PASSWORD`
- **SSL Issues**: Set `DB_USE_SSL=false` for development

**WMS Connection Issues**:

- **401 Unauthorized**: Check WMS credentials and company/facility codes
- **404 Not Found**: Verify WMS URL and endpoint availability
- **Timeout**: Increase timeout settings for slow WMS responses

**OIC Authentication Issues**:

- **OAuth2 Failure**: Verify client credentials and IDCS URL
- **Token Expired**: Check token refresh logic and expiration handling
- **Permission Denied**: Verify OIC integration permissions

### **Debug Commands**

```bash
# Test individual components
python -c "
import asyncio
from flx_database_oracle import FlxOracleDbAdapter, FlxDatabaseConfig
config = FlxDatabaseConfig.from_env()
adapter = FlxOracleDbAdapter(config)
asyncio.run(adapter.test_connection())
"

# Enable debug logging
export LOG_LEVEL=DEBUG
python oracle_cli.py health
```

---

**📂 Hub**: [Getting Started Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
