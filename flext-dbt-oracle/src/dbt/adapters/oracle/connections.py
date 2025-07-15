"""Oracle Connection Manager for DBT using FLEXT DB Oracle Services.

This module provides the connection management layer for the DBT Oracle adapter,
leveraging flext-db-oracle's modern DDD services for enterprise-grade reliability.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

import agate
from dbt_common.exceptions import DbtDatabaseError, DbtRuntimeError

from dbt.adapters.base.connections import BaseConnectionManager
from dbt.adapters.contracts.connection import AdapterResponse, Connection, Credentials
from flext_db_oracle import (
    OracleConfig,
    OracleConnectionService,
    OracleQueryService,
    run_async_in_sync_context,
)
from flext_observability.logging import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from collections.abc import Iterator

    # Mock Connection type for now
    Connection = Any

logger = get_logger(__name__)


@dataclass
class OracleCredentials(Credentials):
    """Oracle database credentials for DBT.

    Extends DBT's base Credentials class with Oracle-specific configuration
    using flext-db-oracle standards for consistency across the FLEXT ecosystem.
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
        """Get database identifier for flext-db-oracle."""
        return self.service_name or self.sid or "ORCL"

    def to_oracle_config(self) -> OracleConfig:
        """Convert DBT credentials to flext-db-oracle configuration with full parameterization."""
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
    """Oracle connection manager using flext-db-oracle services.

    Provides DBT connection management while leveraging the enterprise-grade
    Oracle connectivity from flext-db-oracle, ensuring zero code duplication
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
        """Open Oracle connection using flext-db-oracle services."""
        if connection.state == "open":
            logger.debug("Connection already open: %s", connection.name)
            return connection

        credentials = connection.credentials
        if not isinstance(credentials, OracleCredentials):
            msg = f"Invalid credentials type: {type(credentials)}"
            raise DbtRuntimeError(msg)

        try:
            # Create Oracle configuration using enhanced parameterization
            oracle_config = credentials.to_oracle_config()
            logger.info(
                "Created Oracle DB config for DBT with parameterization: pool_size=%d, query_timeout=%d",
                oracle_config.pool_max_size,
                oracle_config.query_timeout,
            )

            # Initialize FLEXT services
            connection_service = OracleConnectionService(oracle_config)
            query_service = OracleQueryService(connection_service)

            # Test connection using modern async/sync bridge
            result = run_async_in_sync_context(connection_service.test_connection())
            if not result.is_success:
                error_message = f"Connection test failed: {result.error}"
                raise DbtDatabaseError(error_message)

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
            error_message = f"Failed to connect to Oracle: {e}"
            raise DbtDatabaseError(error_message) from e

        return connection

    @classmethod
    def get_response(cls, cursor: Any) -> AdapterResponse:  # noqa: ANN401
        """Get response from Oracle query execution."""
        # For FLEXT services, we get results directly
        rows_affected = cursor.row_count if hasattr(cursor, "row_count") else -1

        return AdapterResponse(
            _message="Query completed successfully",
            rows_affected=rows_affected,
            code="SELECT",
        )

    def cancel_open(self) -> list[str]:  # type: ignore[override]
        """Cancel open connections."""
        for connection in self.thread_connections.values():
            if connection.state == "open" and connection.handle:
                try:
                    handle = connection.handle
                    if isinstance(handle, dict) and "connection_service" in handle:
                        # Close FLEXT connection service using modern async/sync bridge
                        run_async_in_sync_context(
                            handle["connection_service"].close_pool(),
                        )
                except Exception as e:  # noqa: BLE001
                    logger.warning("Error closing connection: %s", e)

                connection.state = "closed"  # type: ignore[assignment]
                connection.handle = None

        return []  # Return empty list to match signature

    @contextmanager
    def exception_handler(self, sql: str) -> Iterator[None]:
        """Handle Oracle-specific exceptions."""
        try:
            yield
        except Exception as e:
            logger.exception("Oracle query failed: %s", sql)
            error_message = f"Oracle query failed: {e}"
            raise DbtDatabaseError(error_message) from e

    def execute(  # type: ignore[override]
        self,
        sql: str,
        auto_begin: bool = False,  # noqa: FBT001, FBT002, ARG002
        fetch: bool = False,  # noqa: FBT001, FBT002
        limit: int | None = None,  # noqa: ARG002
    ) -> tuple[AdapterResponse, Any]:
        """Execute SQL using flext-db-oracle query service."""
        connection = self.get_thread_connection()

        if connection.state != "open":
            connection = self.open(connection)

        if not connection.handle:
            error_message = "Connection not properly initialized"
            raise DbtRuntimeError(error_message)

        with self.exception_handler(sql):
            handle = connection.handle
            query_service = handle["query_service"]

            # Execute query using modern async/sync bridge
            result = run_async_in_sync_context(query_service.execute_query(sql))

            if not result.is_success:
                error_message = f"Query execution failed: {result.error}"
                raise DbtDatabaseError(error_message)

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

    def add_query(  # noqa: PLR0913  # type: ignore[override]
        self,
        sql: str,
        auto_begin: bool = True,  # noqa: FBT001, FBT002, ARG002
        bindings: dict[str, Any] | None = None,
        abridge_sql_log: bool = False,  # noqa: FBT001, FBT002, ARG002
        retryable_exceptions: tuple[type[Exception], ...] = (),  # noqa: ARG002
        retry_limit: int = 0,  # noqa: ARG002
    ) -> tuple[Any, Any]:
        """Add query to connection with enhanced logging."""
        logger.debug(
            "Executing Oracle query: %s",
            sql[:100] + "..." if len(sql) > 100 else sql,  # noqa: PLR2004
        )

        connection = self.get_thread_connection()

        with self.exception_handler(sql):
            if connection.state != "open":
                connection = self.open(connection)

            # For FLEXT services, we return a mock cursor with the SQL
            # The actual execution happens in execute()
            cursor = type(
                "MockCursor",
                (),
                {
                    "sql": sql,
                    "bindings": bindings or {},
                    "row_count": 0,
                },
            )()

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
