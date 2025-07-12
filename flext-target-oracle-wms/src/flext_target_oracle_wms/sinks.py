"""Oracle WMS sink implementation."""

from __future__ import annotations

import json
from datetime import UTC
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from singer_sdk.sinks import SQLSink
from sqlalchemy.dialects import oracle

if TYPE_CHECKING:
    from flext_target_oracle_wms.target import TargetOracleWMS


class OracleWMSSink(SQLSink):
    """Oracle WMS sink for handling WMS-specific data loading."""

    connector_class = None  # We'll handle connections via target.engine

    def __init__(
        self,
        target: TargetOracleWMS,
        stream_name: str,
        schema: dict[str, Any] | None = None,
        key_properties: list[str] | None = None,
    ) -> None:
        """Initialize the Oracle WMS sink."""
        super().__init__(
            target=target,
            stream_name=stream_name,
            schema=schema,
            key_properties=key_properties,
        )
        self._target = target

    @property
    def connection(self) -> sa.engine.Connection:
        """Get SQLAlchemy connection from target engine."""
        return self._target.engine.connect()

    @property
    def schema_name(self) -> str:
        """Get the schema name for this sink."""
        return self.config.get("schema", "WMS")

    @property
    def table_name(self) -> str:
        """Get the table name for this sink."""
        # Convert stream name to Oracle-compatible table name
        return self.stream_name.upper().replace("-", "_")

    def conform_name(self, name: str, object_type: str | None = None) -> str:
        """Conform names to Oracle WMS naming conventions."""
        # Oracle identifiers are case-insensitive and limited to 30 chars (pre-12.2)
        # Convert to uppercase and replace hyphens with underscores
        conformed = name.upper().replace("-", "_").replace(".", "_")

        # Truncate if necessary (Oracle 11g/12.1 limit is 30 chars)
        if len(conformed) > 30:
            conformed = conformed[:30]

        return conformed

    def get_column_type(self, property_schema: dict[str, Any]) -> sa.types.TypeEngine:
        """Get SQLAlchemy column type for a property schema."""
        property_type = property_schema.get("type", ["null"])

        if isinstance(property_type, list):
            # Handle nullable types like ["null", "string"]
            non_null_types = [t for t in property_type if t != "null"]
            if non_null_types:
                property_type = non_null_types[0]
            else:
                property_type = "string"  # Default fallback

        # Map Singer types to Oracle types
        type_mapping = {
            "string": sa.VARCHAR(4000),  # Oracle VARCHAR2 max in 11g
            "integer": sa.INTEGER,
            "number": sa.NUMERIC(38, 10),  # Oracle NUMBER with precision
            "boolean": sa.CHAR(1),  # Oracle doesn't have native BOOLEAN
            "array": sa.CLOB,  # Store arrays as JSON in CLOB
            "object": sa.CLOB,  # Store objects as JSON in CLOB
            "date-time": oracle.TIMESTAMP(timezone=True),
            "date": oracle.DATE,
            "time": oracle.TIMESTAMP,
        }

        # Handle format-specific types
        if property_type == "string":
            format_type = property_schema.get("format")
            if format_type == "date-time":
                return oracle.TIMESTAMP(timezone=True)
            if format_type == "date":
                return oracle.DATE
            if format_type == "time":
                return oracle.TIMESTAMP

            # Check maxLength for VARCHAR sizing
            max_length = property_schema.get("maxLength")
            if max_length and max_length <= 4000:
                return sa.VARCHAR(max_length)

        return type_mapping.get(property_type, sa.VARCHAR(4000))

    def create_table_with_records(
        self,
        full_table_name: str,
        schema: dict[str, Any],
        records: list[dict[str, Any]],
    ) -> None:
        """Create table and insert records."""
        # Create table structure
        columns = []

        # Add data columns
        for property_name, property_schema in schema.get("properties", {}).items():
            column_name = self.conform_name(property_name)
            column_type = self.get_column_type(property_schema)
            columns.append(sa.Column(column_name, column_type))

        # Add metadata columns if configured
        if self.config.get("add_record_metadata", True):
            columns.extend([
                sa.Column("_SDC_EXTRACTED_AT", oracle.TIMESTAMP(timezone=True)),
                sa.Column("_SDC_RECEIVED_AT", oracle.TIMESTAMP(timezone=True)),
                sa.Column("_SDC_BATCHED_AT", oracle.TIMESTAMP(timezone=True)),
                sa.Column("_SDC_DELETED_AT", oracle.TIMESTAMP(timezone=True)),
                sa.Column("_SDC_SEQUENCE", sa.INTEGER),
                sa.Column("_SDC_TABLE_VERSION", sa.INTEGER),
            ])

        # Create table
        table = sa.Table(
            self.table_name,
            sa.MetaData(),
            *columns,
            schema=self.schema_name,
        )

        with self.connection as conn:
            # Drop table if exists (for development)
            conn.execute(sa.text(f"DROP TABLE {self.schema_name}.{self.table_name}"))
            conn.commit()

            # Create new table
            table.create(conn)
            conn.commit()

            # Insert records
            if records:
                self._insert_records(conn, table, records)

    def _insert_records(
        self,
        connection: sa.engine.Connection,
        table: sa.Table,
        records: list[dict[str, Any]],
    ) -> None:
        """Insert records into Oracle table."""
        batch_size = self.config.get("batch_size", 1000)

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            prepared_batch = []

            for record in batch:
                prepared_record = self._prepare_record(record)
                prepared_batch.append(prepared_record)

            # Use Oracle-specific INSERT
            connection.execute(table.insert().values(prepared_batch))
            connection.commit()

            self.logger.info(f"Inserted batch of {len(prepared_batch)} records")

    def _prepare_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Prepare record for Oracle insertion."""
        prepared = {}

        for key, value in record.items():
            column_name = self.conform_name(key)

            # Handle different data types
            if value is None:
                prepared[column_name] = None
            elif isinstance(value, dict | list):
                # Convert complex types to JSON strings for CLOB storage
                prepared[column_name] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, bool):
                # Convert boolean to Oracle CHAR(1) format
                prepared[column_name] = "Y" if value else "N"
            else:
                prepared[column_name] = value

        # Add metadata if configured
        if self.config.get("add_record_metadata", True):
            from datetime import datetime
            now = datetime.now(UTC)

            prepared.update({
                "_SDC_EXTRACTED_AT": record.get("_sdc_extracted_at", now),
                "_SDC_RECEIVED_AT": record.get("_sdc_received_at", now),
                "_SDC_BATCHED_AT": now,
                "_SDC_DELETED_AT": record.get("_sdc_deleted_at"),
                "_SDC_SEQUENCE": record.get("_sdc_sequence"),
                "_SDC_TABLE_VERSION": record.get("_sdc_table_version", 1),
            })

        return prepared

    def process_batch(self, context: dict[str, Any]) -> None:
        """Process a batch of records."""
        records = context["records"]

        if not records:
            return

        table_exists = self._table_exists()

        if not table_exists:
            # Create table with first batch
            self.create_table_with_records(
                full_table_name=f"{self.schema_name}.{self.table_name}",
                schema=self.schema,
                records=records,
            )
        else:
            # Insert into existing table
            with self.connection as conn:
                table = self._get_table_metadata(conn)
                self._insert_records(conn, table, records)

    def _table_exists(self) -> bool:
        """Check if the target table exists."""
        with self.connection as conn:
            inspector = sa.inspect(conn)
            return inspector.has_table(self.table_name, schema=self.schema_name)

    def _get_table_metadata(self, connection: sa.engine.Connection) -> sa.Table:
        """Get table metadata for existing table."""
        metadata = sa.MetaData()
        return sa.Table(
            self.table_name,
            metadata,
            autoload_with=connection,
            schema=self.schema_name,
        )
