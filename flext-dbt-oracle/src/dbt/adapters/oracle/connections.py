"""Oracle Connection Manager for DBT using FLEXT DB Oracle Services.

This module provides the connection management layer for the DBT Oracle adapter,
leveraging flext-infrastructure.databases.flext-db-oracle's modern DDD services
for enterprise-grade reliability.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

import agate
from dbt_common.exceptions import DbtDatabaseError, DbtRuntimeError
from flext_db_oracle import (
    OracleConfig,
    OracleConnectionService,
    OracleQueryService,
    run_async_in_sync_context,
)
from flext_observability.logging import get_logger

from dbt.adapters.base.connections import BaseConnectionManager
from dbt.adapters.contracts.connection import AdapterResponse, Connection, Credentials

logger = get_logger(__name__)

if TYPE_CHECKING:
    from cx_Oracle import Connection

try:
    from cx_Oracle import Connection

    CX_ORACLE_AVAILABLE = True
except ImportError:
    # Fallback when cx_Oracle is not available
    CX_ORACLE_AVAILABLE = False
    Connection = Any

logger = get_logger(__name__)


@dataclass
class OracleCredentials(Credentials):
    """Oracle database credentials for DBT.

    Extends DBT's base Credentials class with Oracle-specific configuration
    using flext-infrastructure.databases.flext-db-oracle standards for consistency
    across the FLEXT ecosystem.
    """

    # Oracle connection parameters - required first
    host: str
    username: str
    password: str
    schema: str  # Required by DBT

    # DBT-specific settings - required
    database: str

    # Oracle connection parameters with defaults
    port: int = 1521
    service_name: str | None = None
    sid: str | None = None
    protocol: str = "tcp"

    # Connection pool configuration
    pool_min_size: int = 1
    pool_max_size: int = 5
    pool_increment: int = 1

    # Advanced Oracle settings
    ssl_server_dn_match: bool = False
    nls_lang: str | None = None
    nls_date_format: str = "YYYY-MM-DD HH24:MI:SS"

    # Optional DBT-specific settings
    search_path: str | None = None

    # DBT required attributes
    _ALIASES: ClassVar[dict[str, str]] = {
        "dbname": "database",
        "pass": "password",
        "user": "username",
    }

    @property
    def type(self) -> str:
        """Return adapter type."""
        return "oracle"

    @property
    def unique_field(self) -> str:
        """Return unique identifier for connection."""
        return self.host

    def _connection_keys(self) -> set[str]:
        """Return keys used for connection pooling."""
        return {
            "host",
            "port",
            "username",
            "password",
            "service_name",
            "sid",
            "protocol",
            "schema",
        }

    @property
    def database_identifier(self) -> str:
        """Get database identifier for flext-infrastructure.databases.flext-db-oracle.

        Get database identifier for
        flext-infrastructure.databases.flext-db-oracle.
        """
        return self.service_name or self.sid or "ORCL"

    def to_oracle_config(self) -> OracleConfig:
        """Convert DBT credentials to flext-infrastructure.databases.flext-db-oracle configuration.

        Convert DBT credentials to
        flext-infrastructure.databases.flext-db-oracle configuration with full
        parameterization.
        """
        return OracleConfig(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            service_name=self.service_name or "XEPDB1",  # Default service name
            sid=self.sid,
            protocol=self.protocol,
            # Enhanced parameterization for DBT workloads
            pool_min_size=self.pool_min_size,
            pool_max_size=self.pool_max_size,
            pool_increment=self.pool_increment,
            query_timeout=300,  # DBT queries can be long-running
            fetch_size=1000,  # Balanced for analytical workloads
            connect_timeout=30,
            retry_attempts=3,
            retry_delay=1.0,
        )


class OracleConnectionManager(BaseConnectionManager):
    """Oracle connection manager using flext-infrastructure.databases.flext-db-oracle services.

    Oracle connection manager using
    flext-infrastructure.databases.flext-db-oracle services.

    Provides DBT connection management while leveraging the enterprise-grade
    Oracle connectivity from flext-infrastructure.databases.flext-db-oracle,
    ensuring zero code duplication
    and consistent error handling across the FLEXT ecosystem.
    """

    TYPE = "oracle"

    def __init__(self, profile: dict[str, Any]) -> None:
        """Initialize connection manager with FLEXT services."""
        super().__init__(profile)
        self._oracle_services: dict[
            str,
            tuple[OracleConnectionService, OracleQueryService],
        ] = {}

    @classmethod
    def open(cls, connection: Connection) -> Connection:
        """Open Oracle connection using flext-infrastructure.databases.flext-db-oracle services.

        Open Oracle connection using
        flext-infrastructure.databases.flext-db-oracle services.
        """
        if connection.state == "open":
            logger.debug("Connection already open: %s", connection.name)
            return connection

        credentials = connection.credentials
        if not isinstance(credentials, OracleCredentials):
            msg = "Invalid credentials type"
            raise DbtRuntimeError(msg)
        try:
            # Create Oracle configuration using enhanced parameterization
            oracle_config = credentials.to_oracle_config()
            logger.info(
                "Created Oracle DB config for DBT with parameterization: "
                "pool_size=%d, query_timeout=%d",
                oracle_config.pool_max_size,
                oracle_config.query_timeout,
            )

            # Initialize FLEXT services
            connection_service = OracleConnectionService(oracle_config)
            query_service = OracleQueryService(connection_service)

            # Test connection using modern async/sync bridge
            result = run_async_in_sync_context(connection_service.test_connection())
            if not result.is_success:
                cls._handle_connection_error(result.error)

            # Store services for later use
            connection.handle = {
                "connection_service": connection_service,
                "query_service": query_service,
                "oracle_config": oracle_config,
            }

            connection.state = "open"
            logger.info("Oracle connection opened: %s", connection.name)
        except Exception as e:
            logger.exception("Failed to open Oracle connection: %s", connection.name)
            connection.state = "fail"
            connection.handle = None
            msg = f"Failed to open Oracle connection: {e}"
            raise DbtDatabaseError(msg) from e

        return connection

    @classmethod
    def get_response(cls, cursor: Any) -> AdapterResponse:
        """Get response from Oracle query execution."""
        # For FLEXT services, we get results directly
        rows_affected = cursor.row_count if hasattr(cursor, "row_count") else -1

        return AdapterResponse(
            _message="Query completed successfully",
            rows_affected=rows_affected,
            code="SELECT",
        )

    def cancel_open(self) -> list[str]:
        """Cancel open connections."""
        for connection in self.thread_connections.values():
            try:
                handle = connection.handle
                if isinstance(handle, dict) and "connection_service" in handle:
                    # Close FLEXT connection service using modern async/sync bridge
                    run_async_in_sync_context(
                        handle["connection_service"].close_pool(),
                    )
            except Exception as e:
                logger.warning("Error closing connection: %s", e)
            connection.state = "closed"
            connection.handle = None
        return []

    @classmethod
    def _handle_connection_error(cls, error: str | None) -> None:
        """Handle connection errors by raising appropriate exception."""
        error_message = (
            f"Connection test failed: {error}" if error else "Connection test failed"
        )
        raise DbtDatabaseError(error_message)

    @contextmanager
    def exception_handler(self, sql: str) -> Any:
        try:
            yield
        except Exception as e:
            logger.exception("Oracle query failed: %s", sql)
            msg = f"Oracle query failed: {e}"
            raise DbtDatabaseError(msg) from e

    def execute(
        self,
        sql: str,
        fetch: bool = False,
    ) -> tuple[AdapterResponse, Any]:
        """Execute SQL using flext-infrastructure.databases.flext-db-oracle query service.

        Execute SQL using flext-infrastructure.databases.flext-db-oracle
        query service.
        """
        connection = self.get_thread_connection()

        if connection.state != "open":
            connection = self.open(connection)

        if not connection.handle:
            msg = "No connection handle available"
            raise DbtRuntimeError(msg)

        with self.exception_handler(sql):
            handle = connection.handle
            query_service = handle["query_service"]

            # Execute query using modern async/sync bridge
            result = run_async_in_sync_context(query_service.execute_query(sql))

            if not result.is_success:
                msg = f"Query execution failed: {result.error}"
                raise DbtDatabaseError(msg)

            query_result = result.value

            # Convert to agate table if fetching results
            if fetch and query_result.rows:
                # Create agate table from results
                columns = query_result.columns or []
                rows = query_result.rows or []

                if columns and rows:
                    table = agate.Table(rows, column_names=columns)
                else:
                    table = agate.Table([])
            else:
                table = agate.Table([])

            # Create response with metrics
            response = AdapterResponse(
                _message=f"Query completed in {query_result.execution_time_ms:.2f}ms",
                rows_affected=query_result.row_count,
                code="SELECT" if sql.strip().upper().startswith("SELECT") else "DDL",
            )

            return response, table

    def add_query(
        self,
        sql: str,
        bindings: dict[str, Any] | None = None,
    ) -> tuple[Any, Any]:
        """Add query to connection with enhanced logging."""
        logger.debug(
            "Executing Oracle query: %s",
            sql[:100] + "..." if len(sql) > 100 else sql,
        )

        connection = self.get_thread_connection()

        with self.exception_handler(sql):
            if connection.state != "open":
                connection = self.open(connection)

            # Get actual cursor from Oracle connection
            if CX_ORACLE_AVAILABLE and hasattr(connection.handle, "cursor"):
                cursor = connection.handle.cursor()
                # Store execution context for debugging - intentional dynamic attributes
                cursor._flext_sql = sql  # noqa: SLF001
                cursor._flext_bindings = bindings or {}  # noqa: SLF001
            else:
                # Development/testing fallback cursor
                class FallbackCursor:
                    """Fallback cursor for development/testing."""

                    def __init__(self) -> None:
                        self.sql = sql
                        self.bindings = bindings or {}
                        self.row_count = 0
                        self.arraysize = 1

                    def execute(self, sql: str, bindings: Any = None) -> None:
                        """Execute SQL (no-op in fallback mode)."""
                        logger.warning(
                            "Using fallback cursor - SQL not executed: %s",
                            sql[:100],
                        )

                    def fetchone(self) -> None:
                        """Fetch one row (no-op in fallback mode)."""
                        return

                    def fetchall(self) -> list[Any]:
                        """Fetch all rows (empty in fallback mode)."""
                        return []

                    def close(self) -> None:
                        """Close cursor (no-op in fallback mode)."""

                cursor = FallbackCursor()

            return connection, cursor

    def begin(self) -> None:
        """Begin transaction (Oracle auto-commit mode)."""
        # Oracle in DBT typically uses auto-commit mode
        # Transactions are handled at the SQL level
        connection = self.get_thread_connection()
        if connection.state != "open":
            self.open(connection)

        logger.debug("Oracle transaction begin (auto-commit mode)")

    def commit(self) -> None:
        """Commit transaction (Oracle auto-commit mode)."""
        # Oracle in DBT typically uses auto-commit mode
        connection = self.get_thread_connection()
        if connection.state == "open":
            logger.debug("Oracle transaction commit (auto-commit mode)")

    def rollback(self) -> None:
        """Rollback transaction (Oracle auto-commit mode)."""
        # Oracle in DBT typically uses auto-commit mode
        connection = self.get_thread_connection()
        if connection.state == "open":
            logger.debug("Oracle transaction rollback (auto-commit mode)")
