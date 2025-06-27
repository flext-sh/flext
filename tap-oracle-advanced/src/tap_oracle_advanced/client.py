"""Oracle database client with FLX framework integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import structlog
from singer_sdk.streams import Stream

if TYPE_CHECKING:
    from collections.abc import Iterator

    from singer_sdk.typing import PropertiesList

    from tap_oracle_advanced.tap import TapOracleAdvanced

logger = structlog.get_logger()


class OracleStream(Stream):
    """Base stream class for Oracle database streams.

    This class provides the foundation for all Oracle streams, integrating
    with the FLX database adapter for robust connection management and
    advanced Oracle-specific features.
    """

    def __init__(
        self,
        tap: TapOracleAdvanced,
        name: str | None = None,
        schema: PropertiesList | None = None,
        path: str | None = None,
    ) -> None:
        """Initialize Oracle stream.

        Args:
            tap: Parent tap instance
            name: Stream name (defaults to class name)
            schema: Stream schema
            path: API path (not used for database streams)

        """
        super().__init__(tap, name, schema, path)
        self._database_adapter: Any = None

    @property
    def database_adapter(self) -> Any:
        """Get or create FLX database adapter instance.

        Returns:
            Configured FLX Oracle database adapter.

        """
        if self._database_adapter is None:
            self._database_adapter = self._create_database_adapter()
        return self._database_adapter

    def _create_database_adapter(self) -> Any:
        """Create FLX Oracle database adapter from configuration.

        Returns:
            Configured adapter instance.

        """
        from flx_database_oracle.adapters import StandaloneOracleAdapter
        from flx_database_oracle.config import DatabaseConfig

        # Build connection string from tap configuration
        config = self.tap.config

        # Determine connection type (SID vs Service Name)
        if config.get("sid"):
            f"{config['host']}:{config.get('port', 1521)}/{config['sid']}"
        elif config.get("service_name"):
            (f"{config['host']}:{config.get('port', 1521)}/{config['service_name']}")
        else:
            msg = "Either 'sid' or 'service_name' must be provided"
            raise ValueError(msg)

        # Create database configuration
        db_config = DatabaseConfig(
            host=config["host"],
            port=config.get("port", 1521),
            database=config.get("sid") or config.get("service_name", ""),
            username=config["user"],
            password=config["password"],
            connection_pool_size=config.get("connection_pool_size", 5),
            connection_timeout=config.get("connection_timeout", 30),
            command_timeout=config.get("command_timeout", 300),
        )

        logger.info(
            "Creating Oracle database adapter",
            host=config["host"],
            port=config.get("port", 1521),
            schema=config.get("default_schema"),
        )

        return StandaloneOracleAdapter(db_config)

    def get_records(self, context: dict[str, Any] | None) -> Iterator[dict[str, Any]]:
        """Retrieve records from Oracle database.

        Args:
            context: Stream context with partition information

        Yields:
            Record dictionaries from the database.

        """
        query = self.build_query(context)

        logger.debug(
            "Executing Oracle query",
            stream=self.name,
            query=query[:200] + "..." if len(query) > 200 else query,
        )

        try:
            # Execute query using FLX adapter
            with self.database_adapter.get_connection() as connection:
                cursor = connection.cursor()
                cursor.arraysize = self.tap.config.get("cursor_array_size", 1000)

                cursor.execute(query)

                # Get column names from cursor description
                columns = [desc[0].lower() for desc in cursor.description]

                # Fetch records in batches
                batch_size = self.tap.config.get("batch_size", 10000)

                while True:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break

                    for row in rows:
                        # Convert row to dictionary
                        record = dict(zip(columns, row, strict=False))

                        # Apply any necessary transformations
                        record = self.transform_record(record)

                        yield record

        except Exception as e:
            logger.error(
                "Error executing Oracle query",
                stream=self.name,
                error=str(e),
                query=query[:200] + "..." if len(query) > 200 else query,
            )
            raise

    def build_query(self, context: dict[str, Any] | None) -> str:
        """Build SQL query for the stream.

        Args:
            context: Stream context

        Returns:
            SQL query string.

        """
        # Base implementation - should be overridden by subclasses
        msg = "build_query must be implemented by subclasses"
        raise NotImplementedError(msg)

    def transform_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Transform a database record.

        Args:
            record: Raw record from database

        Returns:
            Transformed record ready for Singer output.

        """
        # Apply Oracle-specific transformations
        transformed = {}

        for key, value in record.items():
            # Handle Oracle-specific data types
            if value is None:
                transformed[key] = None
            elif isinstance(value, int | float | str | bool):
                transformed[key] = value
            else:
                # Convert other types to string representation
                transformed[key] = str(value)

        return transformed

    def get_starting_replication_key_value(
        self,
        context: dict[str, Any] | None,
    ) -> Any:
        """Get starting value for replication key.

        Args:
            context: Stream context

        Returns:
            Starting replication key value.

        """
        # Implementation depends on the specific stream
        return None

    def close(self) -> None:
        """Close database connections and clean up resources."""
        if self._database_adapter:
            try:
                self._database_adapter.close()
            except Exception as e:
                logger.warning(
                    "Error closing database adapter",
                    error=str(e),
                )
            finally:
                self._database_adapter = None
