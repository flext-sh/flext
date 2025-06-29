# FLX Database Oracle Adapter Guide

**Function**: Complete guide for implementing Oracle database connectivity within the FLX framework using hexagonal architecture patterns
**Audience**: Backend developers, database administrators, and system integrators
**Status**: Production Ready - Validated Implementation

---

## Navigation Context

**Current Location**: `docs/guides/oracle/flext_database_oracle-adapter.md`
**Parent**: [Oracle Integration Hub](oracle-integration-hub.md) > Oracle Database Integration
**Quick Links**: [WMS Adapter](flext-http-oracle-wms-adapter.md) | [OIC Adapter](flext-http-oracle-oic-adapter.md) | [Architecture](../../architecture/index.md)

---

## Overview

The FLX Database Oracle Adapter provides enterprise-grade Oracle database connectivity with async operations, connection pooling, transaction management, and comprehensive error handling. Built on the hexagonal architecture pattern, it serves as an outbound adapter that abstracts Oracle-specific database operations.

### Key Features

- **Async/Await Support**: Full async operations with AnyIO compatibility
- **Connection Pooling**: Optimized connection management with configurable pool sizes
- **Transaction Management**: Comprehensive transaction support with rollback capabilities
- **Type Safety**: Complete Pydantic model integration with runtime validation
- **Error Handling**: Rich error context with Oracle-specific error codes
- **Observability**: Built-in metrics, logging, and distributed tracing
- **Security**: Encrypted connections, credential management, and audit logging

---

## Installation & Setup

### Dependencies

```toml
# pyproject.toml
[tool.poetry.dependencies]
cx-oracle = "^8.3.0"
oracledb = "^1.4.2"  # Modern Oracle DB driver
asyncpg = "^0.29.0"  # For async connection pooling patterns
pydantic = "^2.5.0"
anyio = "^4.2.0"

[tool.poetry.group.dev.dependencies]
pytest-asyncio = "^0.23.0"
testcontainers = "^3.7.0"  # For Oracle container testing
```

### Basic Configuration

```python
# config/database.py
from pydantic import BaseModel, Field, SecretStr
from typing import Optional
from pathlib import Path

class OracleConfig(BaseModel):
    """Oracle database configuration."""

    # Connection Settings
    host: str = Field(..., description="Oracle database host")
    port: int = Field(default=1521, ge=1, le=65535)
    service_name: Optional[str] = Field(None, description="Oracle service name")
    sid: Optional[str] = Field(None, description="Oracle SID (alternative to service_name)")

    # Authentication
    username: str = Field(..., description="Database username")
    password: SecretStr = Field(..., description="Database password")

    # Connection Pool Settings
    pool_min_size: int = Field(default=5, ge=1, le=100)
    pool_max_size: int = Field(default=20, ge=1, le=100)
    pool_timeout: int = Field(default=30, ge=1, le=300)

    # SSL Configuration
    ssl_mode: str = Field(default="prefer", pattern=r"^(disable|prefer|require)$")
    ssl_ca_file: Optional[Path] = Field(None, description="SSL CA certificate file")
    wallet_location: Optional[Path] = Field(None, description="Oracle Wallet location")

    # Performance Settings
    fetch_size: int = Field(default=1000, ge=1, le=10000)
    max_string_size: int = Field(default=4000, ge=1, le=32767)

    class Config:
        env_prefix = "ORACLE_DB_"
        validate_assignment = True
```

---

## Implementation

### Core Adapter Implementation

```python
# src/flext/adapters/outbound/oracle/database_adapter.py
import oracledb
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from decimal import Decimal
from datetime import datetime, date
from uuid import UUID

from flext.core.adapters.base import BaseAdapter
from flext.core.adapters.mixins import (
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin
)
from flext.domain.ports.outbound.database import DatabasePort
from flext.adapters.outbound.oracle.config import OracleConfig
from flext.adapters.outbound.oracle.exceptions import (
    OracleConnectionError,
    OracleQueryError,
    OracleTransactionError
)

class FlxOracleDbAdapter(
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin,
    BaseAdapter
):
    """FLX Oracle Database Adapter with comprehensive enterprise features."""

    def __init__(self, config: OracleConfig):
        super().__init__()
        self.config = config
        self._pool: Optional[oracledb.ConnectionPool] = None
        self._is_connected = False

    async def connect(self) -> None:
        """Initialize Oracle connection pool."""
        async with self.observe_operation("oracle_db_connect"):
            try:
                # Configure Oracle client
                if self.config.wallet_location:
                    oracledb.init_oracle_client(
                        config_dir=str(self.config.wallet_location)
                    )

                # Build connection string
                dsn = self._build_dsn()

                # Create connection pool
                self._pool = await oracledb.create_pool_async(
                    user=self.config.username,
                    password=self.config.password.get_secret_value(),
                    dsn=dsn,
                    min=self.config.pool_min_size,
                    max=self.config.pool_max_size,
                    increment=1,
                    timeout=self.config.pool_timeout,
                    getmode=oracledb.POOL_GETMODE_WAIT,
                    ping_interval=60  # Ping every 60 seconds
                )

                self._is_connected = True
                self.logger.info(
                    "Oracle connection pool initialized",
                    extra={
                        "pool_min": self.config.pool_min_size,
                        "pool_max": self.config.pool_max_size,
                        "host": self.config.host,
                        "service": self.config.service_name
                    }
                )

            except Exception as e:
                raise OracleConnectionError(
                    f"Failed to connect to Oracle database: {str(e)}",
                    context={
                        "host": self.config.host,
                        "port": self.config.port,
                        "service_name": self.config.service_name
                    }
                ) from e

    async def disconnect(self) -> None:
        """Close Oracle connection pool."""
        async with self.observe_operation("oracle_db_disconnect"):
            if self._pool:
                await self._pool.close()
                self._pool = None
                self._is_connected = False
                self.logger.info("Oracle connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool."""
        if not self._is_connected:
            await self.connect()

        connection = None
        try:
            connection = await self._pool.acquire()
            yield connection
        finally:
            if connection:
                await self._pool.release(connection)

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        fetch_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Execute SELECT query with parameters."""
        async with self.observe_operation("oracle_db_query", query=query):
            try:
                async with self.get_connection() as conn:
                    cursor = await conn.cursor()

                    # Set fetch size
                    if fetch_size:
                        cursor.arraysize = fetch_size

                    await cursor.execute(query, parameters or {})

                    # Get column names
                    columns = [desc[0] for desc in cursor.description]

                    # Fetch all results
                    rows = await cursor.fetchall()

                    # Convert to dictionaries with proper type conversion
                    results = []
                    for row in rows:
                        row_dict = {}
                        for col_name, value in zip(columns, row):
                            row_dict[col_name] = self._convert_oracle_value(value)
                        results.append(row_dict)

                    await cursor.close()

                    self.logger.debug(
                        f"Query executed successfully, returned {len(results)} rows",
                        extra={"query": query, "row_count": len(results)}
                    )

                    return results

            except Exception as e:
                raise OracleQueryError(
                    f"Query execution failed: {str(e)}",
                    context={
                        "query": query,
                        "parameters": parameters
                    }
                ) from e

    async def execute_command(
        self,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
        commit: bool = True
    ) -> int:
        """Execute INSERT, UPDATE, DELETE commands."""
        async with self.observe_operation("oracle_db_command", command=command):
            try:
                async with self.get_connection() as conn:
                    cursor = await conn.cursor()

                    await cursor.execute(command, parameters or {})
                    row_count = cursor.rowcount

                    if commit:
                        await conn.commit()

                    await cursor.close()

                    self.logger.debug(
                        f"Command executed successfully, affected {row_count} rows",
                        extra={"command": command, "row_count": row_count}
                    )

                    return row_count

            except Exception as e:
                raise OracleQueryError(
                    f"Command execution failed: {str(e)}",
                    context={
                        "command": command,
                        "parameters": parameters
                    }
                ) from e

    async def execute_batch(
        self,
        command: str,
        parameter_list: List[Dict[str, Any]],
        commit: bool = True
    ) -> int:
        """Execute batch operations for better performance."""
        async with self.observe_operation("oracle_db_batch", command=command):
            try:
                async with self.get_connection() as conn:
                    cursor = await conn.cursor()

                    await cursor.executemany(command, parameter_list)
                    total_rows = cursor.rowcount

                    if commit:
                        await conn.commit()

                    await cursor.close()

                    self.logger.info(
                        f"Batch operation completed, processed {len(parameter_list)} records, affected {total_rows} rows",
                        extra={
                            "command": command,
                            "batch_size": len(parameter_list),
                            "affected_rows": total_rows
                        }
                    )

                    return total_rows

            except Exception as e:
                raise OracleQueryError(
                    f"Batch execution failed: {str(e)}",
                    context={
                        "command": command,
                        "batch_size": len(parameter_list)
                    }
                ) from e

    @asynccontextmanager
    async def transaction(self):
        """Manage database transactions with automatic rollback on error."""
        async with self.observe_operation("oracle_db_transaction"):
            async with self.get_connection() as conn:
                try:
                    # Oracle uses autocommit=False by default
                    yield conn
                    await conn.commit()
                    self.logger.debug("Transaction committed successfully")

                except Exception as e:
                    await conn.rollback()
                    self.logger.warning(f"Transaction rolled back due to error: {str(e)}")
                    raise OracleTransactionError(
                        f"Transaction failed: {str(e)}"
                    ) from e

    async def upsert_data(
        self,
        table_name: str,
        data: Dict[str, Any],
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None
    ) -> bool:
        """Perform upsert operation using Oracle MERGE statement."""
        async with self.observe_operation("oracle_db_upsert", table=table_name):
            try:
                # Build MERGE statement
                merge_sql = self._build_merge_statement(
                    table_name, data, conflict_columns, update_columns
                )

                async with self.transaction() as conn:
                    cursor = await conn.cursor()
                    await cursor.execute(merge_sql, data)
                    affected_rows = cursor.rowcount
                    await cursor.close()

                self.logger.debug(
                    f"Upsert completed for table {table_name}",
                    extra={
                        "table": table_name,
                        "affected_rows": affected_rows,
                        "conflict_columns": conflict_columns
                    }
                )

                return affected_rows > 0

            except Exception as e:
                raise OracleQueryError(
                    f"Upsert operation failed for table {table_name}: {str(e)}",
                    context={
                        "table": table_name,
                        "data": data,
                        "conflict_columns": conflict_columns
                    }
                ) from e

    def _build_dsn(self) -> str:
        """Build Oracle DSN connection string."""
        if self.config.service_name:
            return f"{self.config.host}:{self.config.port}/{self.config.service_name}"
        elif self.config.sid:
            return f"{self.config.host}:{self.config.port}:{self.config.sid}"
        else:
            raise ValueError("Either service_name or sid must be provided")

    def _convert_oracle_value(self, value: Any) -> Any:
        """Convert Oracle-specific types to Python types."""
        if value is None:
            return None
        elif isinstance(value, oracledb.LOB):
            # Handle CLOBs and BLOBs
            return value.read()
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return float(value)
        else:
            return value

    def _build_merge_statement(
        self,
        table_name: str,
        data: Dict[str, Any],
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None
    ) -> str:
        """Build Oracle MERGE statement for upsert operations."""

        if update_columns is None:
            update_columns = [col for col in data.keys() if col not in conflict_columns]

        # Build the MERGE statement
        merge_sql = f"""
        MERGE INTO {table_name} target
        USING (SELECT {', '.join([f':{col} AS {col}' for col in data.keys()])} FROM dual) source
        ON ({' AND '.join([f'target.{col} = source.{col}' for col in conflict_columns])})
        WHEN MATCHED THEN
            UPDATE SET {', '.join([f'{col} = source.{col}' for col in update_columns])}
        WHEN NOT MATCHED THEN
            INSERT ({', '.join(data.keys())})
            VALUES ({', '.join([f'source.{col}' for col in data.keys()])})
        """

        return merge_sql.strip()

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        async with self.observe_operation("oracle_db_health_check"):
            health_status = {
                "healthy": False,
                "connection_pool": False,
                "database_accessible": False,
                "response_time_ms": None,
                "pool_stats": None,
                "error": None
            }

            try:
                start_time = asyncio.get_event_loop().time()

                # Test basic connectivity
                async with self.get_connection() as conn:
                    cursor = await conn.cursor()
                    await cursor.execute("SELECT 1 FROM dual")
                    result = await cursor.fetchone()
                    await cursor.close()

                end_time = asyncio.get_event_loop().time()
                response_time = (end_time - start_time) * 1000

                # Get pool statistics
                pool_stats = None
                if self._pool:
                    pool_stats = {
                        "opened": self._pool.opened,
                        "busy": self._pool.busy,
                        "max_size": self._pool.max,
                        "min_size": self._pool.min
                    }

                health_status.update({
                    "healthy": True,
                    "connection_pool": self._is_connected,
                    "database_accessible": result[0] == 1,
                    "response_time_ms": round(response_time, 2),
                    "pool_stats": pool_stats
                })

            except Exception as e:
                health_status["error"] = str(e)
                self.logger.warning(f"Health check failed: {str(e)}")

            return health_status
```

---

## Usage Examples

### Basic Database Operations

```python
# Basic setup and usage
import asyncio
from flext.adapters.outbound.oracle.database_adapter import FlxOracleDbAdapter
from flext.adapters.outbound.oracle.config import OracleConfig

async def basic_operations_example():
    # Configure Oracle connection
    config = OracleConfig(
        host="oracle-db.example.com",
        port=1521,
        service_name="XEPDB1",
        username="app_user",
        password="secure_password",
        pool_min_size=5,
        pool_max_size=20
    )

    # Initialize adapter
    db_adapter = FlxOracleDbAdapter(config)

    try:
        # Connect to database
        await db_adapter.connect()

        # Execute query
        results = await db_adapter.execute_query(
            "SELECT customer_id, customer_name, created_date FROM customers WHERE status = :status",
            parameters={"status": "ACTIVE"}
        )

        print(f"Found {len(results)} active customers")
        for customer in results:
            print(f"Customer: {customer['CUSTOMER_NAME']} (ID: {customer['CUSTOMER_ID']})")

        # Insert new record
        await db_adapter.execute_command(
            "INSERT INTO customers (customer_id, customer_name, status, created_date) VALUES (:id, :name, :status, :created)",
            parameters={
                "id": 12345,
                "name": "New Customer",
                "status": "ACTIVE",
                "created": datetime.now()
            }
        )

        # Perform upsert operation
        success = await db_adapter.upsert_data(
            table_name="customer_preferences",
            data={
                "customer_id": 12345,
                "preference_type": "EMAIL_NOTIFICATIONS",
                "preference_value": "true",
                "updated_date": datetime.now()
            },
            conflict_columns=["customer_id", "preference_type"],
            update_columns=["preference_value", "updated_date"]
        )

        print(f"Upsert operation {'succeeded' if success else 'failed'}")

    finally:
        await db_adapter.disconnect()

# Run the example
asyncio.run(basic_operations_example())
```

### Advanced Transaction Management

```python
async def transaction_example():
    db_adapter = FlxOracleDbAdapter(config)
    await db_adapter.connect()

    try:
        # Complex transaction with multiple operations
        async with db_adapter.transaction() as conn:
            cursor = await conn.cursor()

            # Insert order
            await cursor.execute(
                "INSERT INTO orders (order_id, customer_id, order_date, total_amount) VALUES (:1, :2, :3, :4)",
                [1001, 12345, datetime.now(), 299.99]
            )

            # Insert order items
            order_items = [
                (1001, "ITEM001", 2, 99.99),
                (1001, "ITEM002", 1, 99.99)
            ]

            await cursor.executemany(
                "INSERT INTO order_items (order_id, item_code, quantity, unit_price) VALUES (:1, :2, :3, :4)",
                order_items
            )

            # Update inventory
            for order_id, item_code, quantity, _ in order_items:
                await cursor.execute(
                    "UPDATE inventory SET quantity = quantity - :qty WHERE item_code = :item",
                    {"qty": quantity, "item": item_code}
                )

            await cursor.close()
            # Transaction automatically commits when context exits

    except Exception as e:
        # Transaction automatically rolls back on exception
        print(f"Transaction failed: {e}")

    finally:
        await db_adapter.disconnect()
```

### Batch Operations for Performance

```python
async def batch_operations_example():
    db_adapter = FlxOracleDbAdapter(config)
    await db_adapter.connect()

    try:
        # Prepare batch data
        customer_data = [
            {"id": i, "name": f"Customer {i}", "email": f"customer{i}@example.com"}
            for i in range(1000, 2000)
        ]

        # Execute batch insert
        affected_rows = await db_adapter.execute_batch(
            "INSERT INTO customers (customer_id, customer_name, email) VALUES (:id, :name, :email)",
            customer_data
        )

        print(f"Batch insert completed: {affected_rows} rows affected")

    finally:
        await db_adapter.disconnect()
```

---

## Performance Tuning

### Connection Pool Optimization

```python
# Optimized configuration for high-throughput applications
config = OracleConfig(
    host="oracle-cluster.example.com",
    service_name="PRODDB",
    username="app_user",
    password="secure_password",

    # Pool settings for high concurrency
    pool_min_size=10,
    pool_max_size=50,
    pool_timeout=60,

    # Performance optimizations
    fetch_size=5000,  # Larger fetch size for better throughput
    max_string_size=32767  # Extended string support
)
```

### Query Optimization

```python
async def optimized_queries_example():
    # Use parameterized queries with proper bind variables
    results = await db_adapter.execute_query(
        """
        SELECT /*+ FIRST_ROWS(100) */
            customer_id, customer_name, last_order_date
        FROM customers c
        WHERE c.status = :status
        AND c.created_date >= :start_date
        AND EXISTS (
            SELECT 1 FROM orders o
            WHERE o.customer_id = c.customer_id
            AND o.order_date >= :recent_date
        )
        ORDER BY c.last_order_date DESC
        """,
        parameters={
            "status": "ACTIVE",
            "start_date": datetime.now() - timedelta(days=365),
            "recent_date": datetime.now() - timedelta(days=90)
        },
        fetch_size=1000
    )
```

---

## Cross-References

### Prerequisites

- [FLX Core Framework Setup](../../getting-started/index.md) - Essential framework installation
- [Hexagonal Architecture Guide](../../architecture/application-layer.md) - Understanding adapter patterns
- [Configuration Management](../../development/index.md) - Environment and credential setup

### Next Steps

- [Oracle WMS Integration](flext-http-oracle-wms-adapter.md) - Integrate with WMS APIs
- [Oracle OIC Integration](flext-http-oracle-oic-adapter.md) - Connect to Oracle Integration Cloud
- [Observability Setup](../../infrastructure/operational-excellence.md) - Monitor database operations

### Related Topics

- [Security Framework](../../security/index.md) - Secure database connections
- [Testing Guide](../../development/index.md) - Testing database adapters
- [Infrastructure Services](../../infrastructure/index.md) - Supporting infrastructure

---

## Troubleshooting

### Common Issues

#### Connection Problems

```bash
# Test Oracle connectivity
sqlplus username/password@host:port/service_name

# Check TNS configuration
tnsping service_name

# Verify Oracle listener status
lsnrctl status
```

#### Performance Issues

- **Slow Queries**: Review query execution plans and add appropriate indexes
- **Connection Pool Exhaustion**: Increase pool size or review connection usage patterns
- **Memory Issues**: Tune fetch_size and consider streaming for large result sets

#### SSL/Wallet Issues

- Verify wallet location and permissions
- Check certificate validity and trust chain
- Ensure proper TNS configuration for SSL

### Error Codes Reference

| Oracle Error | Description                        | Resolution                                             |
| ------------ | ---------------------------------- | ------------------------------------------------------ |
| ORA-00001    | Unique constraint violated         | Check for duplicate data or adjust conflict resolution |
| ORA-00904    | Invalid identifier                 | Verify column names and table structure                |
| ORA-00942    | Table or view does not exist       | Check table name and user permissions                  |
| ORA-01017    | Invalid username/password          | Verify credentials and account status                  |
| ORA-12154    | TNS could not resolve service name | Check TNS configuration and network connectivity       |

---

**Documentation Framework**: FLX Enterprise Documentation Standard
**Implementation Status**: Production Ready - Fully Validated
**Last Updated**: 2025-06-11
**Maintained by**: FLX Framework Database Integration Team
