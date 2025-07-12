"""Target Oracle WMS implementation using Singer SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from singer_sdk import Target
from singer_sdk import typing as th

from target_oracle_wms.sinks import OracleWMSSink

if TYPE_CHECKING:
    import oracledb


class TargetOracleWMS(Target):
    """FLEXT Target Oracle WMS - Singer target for Oracle WMS data loading."""

    name = "target-oracle-wms"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "host",
            th.StringType,
            required=True,
            description="Oracle database host",
        ),
        th.Property(
            "port",
            th.IntegerType,
            default=1521,
            description="Oracle database port",
        ),
        th.Property(
            "service_name",
            th.StringType,
            required=True,
            description="Oracle service name",
        ),
        th.Property(
            "user",
            th.StringType,
            required=True,
            description="Oracle database user",
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
            secret=True,
            description="Oracle database password",
        ),
        th.Property(
            "schema",
            th.StringType,
            default="WMS",
            description="Oracle schema name",
        ),
        th.Property(
            "batch_size",
            th.IntegerType,
            default=1000,
            description="Number of records to insert in each batch",
        ),
        th.Property(
            "connection_timeout",
            th.IntegerType,
            default=30,
            description="Connection timeout in seconds",
        ),
        th.Property(
            "pool_size",
            th.IntegerType,
            default=5,
            description="Connection pool size",
        ),
        th.Property(
            "pool_max_overflow",
            th.IntegerType,
            default=10,
            description="Maximum overflow connections in pool",
        ),
        th.Property(
            "default_target_schema",
            th.StringType,
            description="Default target schema name",
        ),
        th.Property(
            "add_record_metadata",
            th.BooleanType,
            default=True,
            description="Add metadata columns to target tables",
        ),
        th.Property(
            "hard_delete",
            th.BooleanType,
            default=False,
            description="Use hard delete instead of soft delete",
        ),
        th.Property(
            "validate_records",
            th.BooleanType,
            default=True,
            description="Validate records against schema before loading",
        ),
    ).to_dict()

    default_sink_class = OracleWMSSink

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
    ) -> None:
        """Initialize the target."""
        super().__init__(
            config=config,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

        # Initialize Oracle connection pool
        self._engine: sa.Engine | None = None
        self._connection_pool: oracledb.ConnectionPool | None = None

    @property
    def engine(self) -> sa.Engine:
        """Get or create SQLAlchemy engine with Oracle connection."""
        if self._engine is None:
            connection_string = self._build_connection_string()

            self._engine = sa.create_engine(
                connection_string,
                pool_size=self.config["pool_size"],
                max_overflow=self.config["pool_max_overflow"],
                pool_timeout=self.config["connection_timeout"],
                pool_recycle=3600,  # Recycle connections after 1 hour
                echo=self.logger.isEnabledFor(10),  # Echo SQL if debug logging
            )

        return self._engine

    def _build_connection_string(self) -> str:
        """Build Oracle connection string from config."""
        host = self.config["host"]
        port = self.config["port"]
        service_name = self.config["service_name"]
        user = self.config["user"]
        password = self.config["password"]

        # Oracle connection string format
        return f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service_name}"

    def get_sink(
        self,
        stream_name: str,
        record: dict[str, Any] | None = None,
        schema: dict[str, Any] | None = None,
        key_properties: list[str] | None = None,
    ) -> OracleWMSSink:
        """Get a sink for the given stream."""
        return self.default_sink_class(
            target=self,
            stream_name=stream_name,
            schema=schema,
            key_properties=key_properties,
        )
