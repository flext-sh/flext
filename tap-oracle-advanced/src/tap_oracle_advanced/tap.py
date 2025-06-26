"""Main TAP implementation for Oracle databases with FLX framework integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from singer_sdk import Tap
from singer_sdk.typing import (
    ArrayType,
    BooleanType,
    IntegerType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)
from tap_oracle_advanced.streams import CustomQueryStream, TablesStream, ViewsStream

if TYPE_CHECKING:
    from tap_oracle_advanced.client import OracleStream

logger = structlog.get_logger()


class TapOracleAdvanced(Tap):
    """Advanced Singer tap for Oracle databases.

    This tap leverages the FLX framework's database adapters to provide
    enterprise-grade Oracle data extraction with modern Python patterns.
    """

    name = "tap-oracle-advanced"
    config_jsonschema = PropertiesList(
        # Connection configuration
        Property(
            "host",
            StringType,
            required=True,
            description="Oracle database host",
        ),
        Property(
            "port",
            IntegerType,
            default=1521,
            description="Oracle database port",
        ),
        Property(
            "sid",
            StringType,
            description="Oracle database SID (either sid or service_name required)",
        ),
        Property(
            "service_name",
            StringType,
            description="Oracle database service name (either sid or service_name required)",
        ),
        Property(
            "user",
            StringType,
            required=True,
            secret=True,
            description="Oracle database username",
        ),
        Property(
            "password",
            StringType,
            required=True,
            secret=True,
            description="Oracle database password",
        ),
        # Advanced connection options
        Property(
            "connection_pool_size",
            IntegerType,
            default=5,
            description="Maximum number of connections in the pool",
        ),
        Property(
            "connection_timeout",
            IntegerType,
            default=30,
            description="Connection timeout in seconds",
        ),
        Property(
            "command_timeout",
            IntegerType,
            default=300,
            description="SQL command timeout in seconds",
        ),
        # Schema and table filtering
        Property(
            "default_schema",
            StringType,
            description="Default schema for table discovery",
        ),
        Property(
            "schema_filter",
            ArrayType(StringType),
            description="List of schemas to include in discovery",
        ),
        Property(
            "table_filter",
            ArrayType(StringType),
            description="List of table patterns to include (supports wildcards)",
        ),
        Property(
            "exclude_tables",
            ArrayType(StringType),
            description="List of table patterns to exclude (supports wildcards)",
        ),
        # Sync behavior
        Property(
            "use_singer_decimal",
            BooleanType,
            default=False,
            description="Use singer.decimal for numeric types",
        ),
        Property(
            "batch_size",
            IntegerType,
            default=10000,
            description="Number of records per batch",
        ),
        Property(
            "incremental_strategy",
            StringType,
            default="replication_key",
            allowed_values=["replication_key", "log_based", "full_table"],
            description="Strategy for incremental sync",
        ),
        # Custom queries
        Property(
            "custom_queries",
            ObjectType(
                Property("name", StringType, required=True),
                Property("sql", StringType, required=True),
                Property("replication_method", StringType, default="FULL_TABLE"),
                Property("replication_key", StringType),
                Property("primary_keys", ArrayType(StringType)),
            ),
            description="Custom SQL queries to execute as streams",
        ),
        # Performance and optimization
        Property(
            "use_date_datatype",
            BooleanType,
            default=True,
            description="Use native date datatype for Oracle DATE columns",
        ),
        Property(
            "cursor_array_size",
            IntegerType,
            default=1000,
            description="Array size for cursor fetching",
        ),
        Property(
            "use_binds_for_partition",
            BooleanType,
            default=True,
            description="Use bind variables for partition queries",
        ),
        # Logging and debugging
        Property(
            "log_level",
            StringType,
            default="INFO",
            allowed_values=["DEBUG", "INFO", "WARNING", "ERROR"],
            description="Logging level",
        ),
        Property(
            "enable_sql_logging",
            BooleanType,
            default=False,
            description="Enable SQL statement logging",
        ),
    ).to_dict()

    def discover_streams(self) -> list[OracleStream]:
        """Discover available streams from Oracle database.

        Returns:
            List of discovered streams including tables, views, and custom queries.

        """
        streams: list[OracleStream] = []

        # Add standard table and view streams
        streams.extend(
            [
                TablesStream(self),
                ViewsStream(self),
            ],
        )

        # Add custom query streams if configured
        custom_queries = self.config.get("custom_queries", [])
        for query_config in custom_queries:
            streams.append(CustomQueryStream(self, query_config))

        logger.info(
            "Discovered Oracle streams",
            stream_count=len(streams),
            config_host=self.config.get("host"),
            config_schema=self.config.get("default_schema"),
        )

        return streams


if __name__ == "__main__":
    TapOracleAdvanced.cli()
