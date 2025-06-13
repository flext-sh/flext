"""Oracle DB extractor."""

from singer_sdk import Stream, Tap
from singer_sdk import typing as th
from tap_oracle_db.connection import OracleConnection
from tap_oracle_db.discovery import discover_streams


class TapOracleDB(Tap):
    """Oracle database tap class."""

    name = "tap-oracle-db"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "connection_type",
            th.StringType,
            allowed_values=["normal", "autonomous"],
            default="normal",
            description="Connection type: normal or autonomous",
        ),
        th.Property(
            "host",
            th.StringType,
            required=True,
            description="Database host",
        ),
        th.Property(
            "port",
            th.IntegerType,
            default=1521,
            description="Database port",
        ),
        th.Property(
            "user",
            th.StringType,
            required=True,
            description="Database user",
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
            secret=True,
            description="Database password",
        ),
        th.Property(
            "service_name",
            th.StringType,
            description="Database service name",
        ),
        th.Property(
            "sid",
            th.StringType,
            description="Database SID (alternative to service_name)",
        ),
        th.Property(
            "driver_type",
            th.StringType,
            allowed_values=["thin", "thick"],
            default="thin",
            description="Oracle driver type: thin or thick",
        ),
        th.Property(
            "wallet_location",
            th.StringType,
            description="Wallet location for Autonomous DB",
        ),
        th.Property(
            "wallet_password",
            th.StringType,
            secret=True,
            description="Wallet password for Autonomous DB",
        ),
        th.Property(
            "include_schemas",
            th.ArrayType(th.StringType),
            description="list of schemas to include",
        ),
        th.Property(
            "exclude_schemas",
            th.ArrayType(th.StringType),
            default=["SYS", "SYSTEM"],
            description="list of schemas to exclude",
        ),
        th.Property(
            "default_replication_method",
            th.StringType,
            allowed_values=["FULL_TABLE", "INCREMENTAL", "LOG_BASED"],
            default="INCREMENTAL",
            description="Default replication method if not specified in table config",
        ),
        th.Property(
            "tables",
            th.ArrayType(
                th.ObjectType(
                    th.Property("table_name", th.StringType, required=True),
                    th.Property("schema", th.StringType),
                    th.Property("replication_method", th.StringType),
                    th.Property("replication_key", th.StringType),
                ),
            ),
            description="list of tables to extract",
        ),
        th.Property(
            "views",
            th.ArrayType(
                th.ObjectType(
                    th.Property("view_name", th.StringType, required=True),
                    th.Property("schema", th.StringType),
                ),
            ),
            description="list of views to extract",
        ),
        th.Property(
            "select_queries",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType, required=True),
                    th.Property("query", th.StringType, required=True),
                    th.Property("replication_method", th.StringType),
                ),
            ),
            description="list of custom SQL queries to extract",
        ),
        th.Property(
            "batch_size",
            th.IntegerType,
            default=50000,
            description="Number of records to fetch in each batch",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        connection = OracleConnection(self.config)
        return discover_streams(self, connection)
