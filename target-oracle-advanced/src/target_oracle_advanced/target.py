"""Main TARGET implementation for Oracle databases with FLX framework integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from singer_sdk import Target
from singer_sdk.typing import (
    BooleanType,
    IntegerType,
    NumberType,
    PropertiesList,
    Property,
    StringType,
)

from target_oracle_advanced.sinks import OracleBulkSink, OracleSink, OracleUpsertSink

if TYPE_CHECKING:
    from singer_sdk.sinks import Sink

logger = structlog.get_logger()


class TargetOracleAdvanced(Target):
    """Advanced Singer target for Oracle databases.

    This target leverages the FLX framework's database adapters to provide
    enterprise-grade Oracle data loading with modern Python patterns.
    """

    name = "target-oracle-advanced"
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
        # Schema and table configuration
        Property(
            "default_target_schema",
            StringType,
            description="Default schema for target tables",
        ),
        Property(
            "table_prefix",
            StringType,
            default="",
            description="Prefix to add to all table names",
        ),
        Property(
            "table_suffix",
            StringType,
            default="",
            description="Suffix to add to all table names",
        ),
        # Loading behavior
        Property(
            "load_method",
            StringType,
            default="upsert",
            allowed_values=["append", "upsert", "overwrite"],
            description="Method for loading data into tables",
        ),
        Property(
            "batch_size",
            IntegerType,
            default=10000,
            description="Number of records per batch",
        ),
        Property(
            "use_bulk_loading",
            BooleanType,
            default=True,
            description="Use Oracle bulk loading capabilities",
        ),
        Property(
            "bulk_load_threshold",
            IntegerType,
            default=1000,
            description="Minimum records to trigger bulk loading",
        ),
        # Schema management
        Property(
            "add_record_metadata",
            BooleanType,
            default=True,
            description="Add metadata columns (_sdc_* fields)",
        ),
        Property(
            "auto_create_tables",
            BooleanType,
            default=True,
            description="Automatically create tables if they don't exist",
        ),
        Property(
            "auto_alter_tables",
            BooleanType,
            default=True,
            description="Automatically alter tables when schema changes",
        ),
        Property(
            "hard_delete",
            BooleanType,
            default=False,
            description="Permanently delete records on DELETE operations",
        ),
        # Data type handling
        Property(
            "use_singer_decimal",
            BooleanType,
            default=False,
            description="Use singer.decimal for numeric types",
        ),
        Property(
            "varchar_max_length",
            IntegerType,
            default=4000,
            description="Maximum length for VARCHAR2 columns",
        ),
        Property(
            "use_clob_for_text",
            BooleanType,
            default=False,
            description="Use CLOB for large text fields",
        ),
        Property(
            "date_format",
            StringType,
            default="YYYY-MM-DD HH24:MI:SS",
            description="Oracle date format for string to date conversion",
        ),
        # Performance optimization
        Property(
            "enable_parallel_dml",
            BooleanType,
            default=False,
            description="Enable Oracle parallel DML operations",
        ),
        Property(
            "parallel_degree",
            IntegerType,
            default=4,
            description="Degree of parallelism for DML operations",
        ),
        Property(
            "commit_interval",
            IntegerType,
            default=5000,
            description="Number of records between commits",
        ),
        Property(
            "use_merge_statement",
            BooleanType,
            default=True,
            description="Use MERGE statement for upsert operations",
        ),
        # Error handling and recovery
        Property(
            "max_retries",
            IntegerType,
            default=3,
            description="Maximum number of retry attempts",
        ),
        Property(
            "retry_delay",
            NumberType,
            default=1.0,
            description="Delay between retry attempts (seconds)",
        ),
        Property(
            "ignore_errors",
            BooleanType,
            default=False,
            description="Continue processing on non-fatal errors",
        ),
        Property(
            "error_table_suffix",
            StringType,
            default="_errors",
            description="Suffix for error logging tables",
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
        Property(
            "log_performance_metrics",
            BooleanType,
            default=True,
            description="Log performance metrics for monitoring",
        ),
    ).to_dict()

    default_sink_class = OracleSink

    def get_sink_class(self, stream_name: str) -> type[Sink]:
        """Get appropriate sink class based on configuration and stream.

        Args:
            stream_name: Name of the stream

        Returns:
            Sink class to use for the stream.

        """
        config = self.config

        # Use bulk sink for large datasets
        if config.get("use_bulk_loading", True):
            return OracleBulkSink

        # Use upsert sink for merge operations
        if config.get("load_method") == "upsert":
            return OracleUpsertSink

        # Default to standard sink
        return OracleSink


if __name__ == "__main__":
    TargetOracleAdvanced.cli()
