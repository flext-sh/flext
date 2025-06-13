"""Oracle DB target sink."""

import json
import time
from typing import Any

from singer_sdk.sinks import SQLSink
from singer_sdk.target_base import Target

from target_oracle.connection import OracleConnection


class OracleTarget(Target):
    """Target for Oracle Database."""

    name = "target-oracle"
    config_jsonschema = {
        "type": "object",
        "properties": {
            "connection_type": {
                "type": "string",
                "enum": ["normal", "autonomous"],
                "default": "normal",
                "description": "Connection type: normal or autonomous",
            },
            "host": {
                "type": "string",
                "description": "Database host",
            },
            "port": {
                "type": "integer",
                "default": 1521,
                "description": "Database port",
            },
            "user": {
                "type": "string",
                "description": "Database user",
            },
            "password": {
                "type": "string",
                "description": "Database password",
            },
            "service_name": {
                "type": "string",
                "description": "Database service name",
            },
            "sid": {
                "type": "string",
                "description": "Database SID (alternative to service_name)",
            },
            "driver_type": {
                "type": "string",
                "enum": ["thin", "thick"],
                "default": "thin",
                "description": "Oracle driver type: thin or thick",
            },
            "wallet_location": {
                "type": "string",
                "description": "Wallet location for Autonomous DB",
            },
            "wallet_password": {
                "type": "string",
                "description": "Wallet password for Autonomous DB",
            },
            "default_target_schema": {
                "type": "string",
                "description": "Default target schema",
            },
            "schema_mapping": {
                "type": "object",
                "additionalProperties": {"type": "string"},
                "description": "Mapping from stream names to target schemas",
            },
            "add_record_metadata": {
                "type": "boolean",
                "default": True,
                "description": "Add _sdc columns to replicated tables",
            },
            "batch_size_rows": {
                "type": "integer",
                "default": 1000,
                "description": "Maximum number of rows to process in each batch",
            },
            "flush_interval_secs": {
                "type": "integer",
                "default": 60,
                "description": "Number of seconds after which to force flush",
            },
            "primary_key_required": {
                "type": "boolean",
                "default": True,
                "description": "Whether primary keys are required",
            },
            "load_method": {
                "type": "string",
                "enum": ["append", "upsert", "overwrite"],
                "default": "append",
                "description": "Method used to load data",
            },
            "bulk_load": {
                "type": "boolean",
                "default": False,
                "description": "Use direct path insert for faster loading (requires additional permissions)",
            },
            "validate_records": {
                "type": "boolean",
                "default": True,
                "description": "Validate records against schema before loading",
            },
            "table_cache_size": {
                "type": "integer",
                "default": 100,
                "description": "Number of tables to cache in memory",
            },
            "array_size": {
                "type": "integer",
                "default": 10000,
                "description": "Oracle array size for buffer optimization",
            },
            "prefetch_rows": {
                "type": "integer",
                "default": 1000,
                "description": "Oracle prefetch rows for buffer optimization",
            },
            "max_retries": {
                "type": "integer",
                "default": 3,
                "description": "Maximum number of retries for Oracle operations",
            },
            "retry_delay": {
                "type": "number",
                "default": 1.0,
                "description": "Retry delay between attempts for Oracle operations",
            },
        },
        "required": ["user", "password"],
        "anyOf": [
            {
                "required": [
                    "connection_type",
                    "wallet_location",
                    "service_name",
                ],
                "properties": {"connection_type": {"enum": ["autonomous"]}},
            },
            {
                "required": ["host"],
                "anyOf": [
                    {"required": ["service_name"]},
                    {"required": ["sid"]},
                ],
            },
        ],
    }

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        parse_env_config: bool = False,
    ) -> None:
        """Initialize the target."""
        super().__init__(config=config, parse_env_config=parse_env_config)
        self._connection = None

    @property
    def max_parallelism(self) -> int:
        """Get max number of parallel sink processes (threads).

        This target supports limited parallelism.
        """
        return min(8, len(self.input_messages))

    def get_connection(self) -> OracleConnection:
        """Get a connection to the target database."""
        if self._connection is None:
            self._connection = OracleConnection(self.config)
        return self._connection

    def get_sink_class(self):
        """Return the sink class."""
        return OracleSink

    def setup(self) -> None:
        """Set up the target."""
        # Create a connection and test it
        connection = self.get_connection()
        conn = connection.get_connection()

        # Test the connection by executing a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        row = cursor.fetchone()
        if row[0] != 1:
            msg = "Connection test failed"
            raise RuntimeError(msg)
        cursor.close()

    def teardown(self) -> None:
        """Clean up resources."""
        if self._connection:
            self._connection.close()
            self._connection = None


class OracleSink(SQLSink):
    """Oracle target sink class."""

    def __init__(
        self,
        target: Target,
        stream_name: str,
        schema: dict,
        key_properties: list[str] | None,
    ) -> None:
        """Initialize the sink."""
        super().__init__(target, stream_name, schema, key_properties)
        self.batch_size = target.config.get("batch_size_rows", 1000)
        self.last_flush_time = time.time()
        self.flush_interval = target.config.get("flush_interval_secs", 60)
        self.records_buffer = []
        self.target_schema = self._get_target_schema()
        self.load_method = target.config.get("load_method", "append")
        self.bulk_load = target.config.get("bulk_load", False)
        self.validate_records = target.config.get("validate_records", True)
        self.add_record_metadata = target.config.get("add_record_metadata", True)

        # Oracle optimization settings
        self.array_size = target.config.get("array_size", 10000)
        self.prefetch_rows = target.config.get("prefetch_rows", 1000)
        self.max_retries = target.config.get("max_retries", 3)
        self.retry_delay = target.config.get("retry_delay", 1.0)

        # Create table if it doesn't exist
        self._create_table_if_not_exists()

    def _get_target_schema(self) -> str:
        """Get the target schema for this stream."""
        schema_mapping = self.target.config.get("schema_mapping", {})
        default_schema = self.target.config.get(
            "default_target_schema",
            self.target.config["user"].upper(),
        )
        return schema_mapping.get(self.stream_name, default_schema)

    def _configure_cursor(self, cursor) -> None:
        """Configure cursor with optimal settings for Oracle buffer management."""
        try:
            # Set optimal array size for Oracle operations
            cursor.arraysize = self.array_size
            cursor.prefetchrows = self.prefetch_rows

            # Additional Oracle optimizations
            if hasattr(cursor, "setinputsizes"):
                cursor.setinputsizes(None)

        except Exception as e:
            self.logger.warning("Failed to configure cursor optimization", error=str(e))

    def _execute_with_retry(self, cursor, query: str, params=None) -> None:
        """Execute query with retry mechanism for Oracle connection issues."""
        import time

        last_error = None

        for attempt in range(self.max_retries):
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return  # Success, exit retry loop

            except Exception as e:
                last_error = e

                # Check for Oracle-specific errors
                error_str = str(e).lower()
                if any(
                    code in error_str for code in ["ora-03146", "ora-04011", "dpy-4011"]
                ):
                    self.logger.warning(
                        "Oracle buffer/connection error encountered, retrying",
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        error=str(e),
                    )

                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue

                # Non-retryable error or max retries reached
                raise

        # All retries failed
        if last_error:
            msg = f"Query failed after {self.max_retries} retries: {last_error}"
            raise Exception(
                msg,
            ) from last_error

    def _create_table_if_not_exists(self) -> None:
        """Create target table if it doesn't exist."""
        # Connection
        connection = self.target.get_connection()
        conn = connection.get_connection()

        # Check if table exists
        cursor = conn.cursor()
        try:
            # Configure cursor for optimal performance
            self._configure_cursor(cursor)

            self._execute_with_retry(
                cursor,
                """
                SELECT COUNT(*)
                FROM ALL_TABLES
                WHERE OWNER = :schema
                AND TABLE_NAME = :table
                """,
                {
                    "schema": self.target_schema.upper(),
                    "table": self.stream_name.upper(),
                },
            )

            if cursor.fetchone()[0] == 0:
                # Table doesn't exist, create it
                create_stmt = self._get_create_table_sql()
                self._execute_with_retry(cursor, create_stmt)
                conn.commit()

        finally:
            cursor.close()

    def _get_create_table_sql(self) -> str:
        """Generate CREATE TABLE SQL statement based on schema."""
        field_defs = []
        primary_keys = []

        # Process schema fields
        for field_name, field_schema in self.schema["properties"].items():
            # Skip metadata fields
            if field_name.startswith("_sdc_"):
                continue

            # Extract type info
            col_type = self._schema_type_to_oracle_type(field_schema)
            nullable = field_name not in self.key_properties

            # Add field definition
            field_def = f'"{field_name.upper()}" {col_type}'
            if not nullable:
                field_def += " NOT NULL"
            field_defs.append(field_def)

            # Track primary keys
            if field_name in self.key_properties:
                primary_keys.append(f'"{field_name.upper()}"')

        # Add metadata columns if configured
        if self.add_record_metadata:
            field_defs.extend(
                (
                    '"_SDC_EXTRACTED_AT" TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    '"_SDC_BATCHED_AT" TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    '"_SDC_DELETED_AT" TIMESTAMP',
                ),
            )

        # Build CREATE TABLE statement
        create_stmt = (
            f'CREATE TABLE "{self.target_schema}"."{self.stream_name.upper()}" (\n'
        )
        create_stmt += ",\n".join(field_defs)

        # Add primary key constraint if key properties exist
        if primary_keys and self.target.config.get("primary_key_required", True):
            create_stmt += f',\nCONSTRAINT "PK_{self.stream_name.upper()}" PRIMARY KEY ({", ".join(primary_keys)})'

        create_stmt += "\n)"

        return create_stmt

    def _schema_type_to_oracle_type(self, field_schema: dict) -> str:
        """Convert JSON Schema type to Oracle data type."""
        json_type = field_schema.get("type", ["string"])

        # Handle array type
        if isinstance(json_type, list):
            # Use the first non-null type
            for t in json_type:
                if t != "null":
                    json_type = t
                    break

        # Get format if available
        format_str = field_schema.get("format", "")

        # Map types
        if json_type == "string":
            if format_str == "date-time":
                return "TIMESTAMP"
            if format_str == "date":
                return "DATE"
            if format_str == "time":
                return "VARCHAR2(40)"

            # Check for max length
            max_length = field_schema.get("maxLength", 4000)
            if max_length > 4000:
                return "CLOB"
            return f"VARCHAR2({max_length})"

        if json_type == "integer":
            return "NUMBER(38,0)"

        if json_type == "number":
            return "NUMBER"

        if json_type == "boolean":
            return "NUMBER(1,0)"

        if json_type in {"object", "array"}:
            return "CLOB"

        # Default fallback
        return "VARCHAR2(4000)"

    def process_record(self, record: dict, context: dict) -> None:
        """Process a single record."""
        # Add the record to our buffer
        self.records_buffer.append(record)

        # Check if we should flush based on batch size
        if (
            len(self.records_buffer) >= self.batch_size
            or time.time() - self.last_flush_time >= self.flush_interval
        ):
            self.flush_batch()

    def flush_batch(self) -> None:
        """Flush all buffered records to target."""
        if not self.records_buffer:
            return

        # Get connection
        connection = self.target.get_connection()
        conn = connection.get_connection()
        cursor = conn.cursor()

        try:
            # Configure cursor for optimal buffer management
            self._configure_cursor(cursor)

            # If bulk loading is enabled, use direct path insert
            if self.bulk_load:
                self._execute_bulk_load(cursor)
            else:
                # Standard approach for lower batches
                self._execute_batch_load(cursor)

            # Commit the transaction
            conn.commit()

            # Reset buffer
            self.records_buffer = []
            self.last_flush_time = time.time()
        except Exception:
            # Rollback on error
            conn.rollback()
            raise
        finally:
            cursor.close()

    def _execute_batch_load(self, cursor) -> None:
        """Execute a standard batch load."""
        # Determine the SQL operation based on load method
        if self.load_method == "append":
            sql, bind_data = self._prepare_insert(self.records_buffer)
        elif self.load_method == "upsert":
            sql, bind_data = self._prepare_merge(self.records_buffer)
        elif self.load_method == "overwrite":
            # If overwrite, first truncate the table
            self._execute_with_retry(
                cursor,
                f'TRUNCATE TABLE "{self.target_schema}"."{self.stream_name.upper()}"',
            )
            sql, bind_data = self._prepare_insert(self.records_buffer)
        else:
            msg = f"Unsupported load method: {self.load_method}"
            raise ValueError(msg)

        # Execute the batch with optimized chunking
        chunk_size = min(1000, len(bind_data))  # Oracle-friendly chunk size
        for i in range(0, len(bind_data), chunk_size):
            chunk = bind_data[i : i + chunk_size]
            cursor.executemany(sql, chunk)

    def _execute_bulk_load(self, cursor) -> None:
        """Execute a direct path insert (fast bulk load)."""
        # Adjust how the cursor processes arrays with Oracle optimization
        cursor.arraysize = min(self.array_size, len(self.records_buffer))

        # Direct path insert hint
        if self.load_method == "overwrite":
            # If overwrite, first truncate the table
            self._execute_with_retry(
                cursor,
                f'TRUNCATE TABLE "{self.target_schema}"."{self.stream_name.upper()}"',
            )

        sql, bind_data = self._prepare_insert(self.records_buffer, direct_path=True)

        # Process in chunks to avoid Oracle buffer issues
        chunk_size = min(1000, len(bind_data))
        for i in range(0, len(bind_data), chunk_size):
            chunk = bind_data[i : i + chunk_size]
            cursor.executemany(sql, chunk)

    def _prepare_insert(self, records, direct_path=False):
        """Prepare INSERT statement and bind data."""
        if not records:
            return None, None

        # Sample record to get fields
        sample = records[0]
        fields = list(sample.keys())

        # Add metadata fields if configured
        if self.add_record_metadata:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            for record in records:
                record["_sdc_extracted_at"] = now
                record["_sdc_batched_at"] = now
                record["_sdc_deleted_at"] = None

            fields.extend(["_sdc_extracted_at", "_sdc_batched_at", "_sdc_deleted_at"])

        # Build the INSERT statement
        columns = [f'"{field.upper()}"' for field in fields]
        placeholders = [f":{field}" for field in fields]

        sql = f'INSERT {"/*+ APPEND */" if direct_path else ""} INTO "{self.target_schema}"."{self.stream_name.upper()}" '
        sql += f"({', '.join(columns)}) VALUES ({', '.join(placeholders)})"

        # Prepare bind data
        bind_data = []
        for record in records:
            # Fill in any missing fields with None
            row_data = {}
            for field in fields:
                row_data[field] = record.get(field)

                # Handle JSON data
                if isinstance(row_data[field], dict | list):
                    row_data[field] = json.dumps(row_data[field])

            bind_data.append(row_data)

        return sql, bind_data

    def _prepare_merge(self, records):
        """Prepare MERGE statement for upsert operation."""
        if not records:
            return None, None

        # Sample record to get fields
        sample = records[0]
        fields = list(sample.keys())

        # Add metadata fields if configured
        if self.add_record_metadata:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            for record in records:
                record["_sdc_extracted_at"] = now
                record["_sdc_batched_at"] = now
                record["_sdc_deleted_at"] = None

            fields.extend(["_sdc_extracted_at", "_sdc_batched_at", "_sdc_deleted_at"])

        # Check for key properties
        if not self.key_properties:
            msg = "Cannot perform MERGE operation without primary key"
            raise ValueError(msg)

        # Build the MERGE statement
        merge_sql = (
            f'MERGE INTO "{self.target_schema}"."{self.stream_name.upper()}" target\n'
        )
        merge_sql += "USING (SELECT "

        # Values from source
        for field in fields:
            merge_sql += f":{field} as {field.upper()}, "

        # Remove trailing comma and add FROM DUAL
        merge_sql = merge_sql[:-2] + " FROM DUAL) source\n"

        # ON clause (primary key match)
        merge_sql += "ON ("
        for key in self.key_properties:
            merge_sql += f'target."{key.upper()}" = source.{key.upper()} AND '

        # Remove trailing AND
        merge_sql = merge_sql[:-5] + ")\n"

        # WHEN MATCHED (update non-key fields)
        merge_sql += "WHEN MATCHED THEN UPDATE SET\n"
        update_fields = [f for f in fields if f not in self.key_properties]

        for field in update_fields:
            merge_sql += f'target."{field.upper()}" = source.{field.upper()},\n'

        # Remove trailing comma
        merge_sql = merge_sql[:-2] + "\n"

        # WHEN NOT MATCHED (insert all fields)
        merge_sql += "WHEN NOT MATCHED THEN\n"
        merge_sql += "INSERT ("
        for field in fields:
            merge_sql += f'"{field.upper()}", '

        # Remove trailing comma
        merge_sql = merge_sql[:-2] + ")\n"

        merge_sql += "VALUES ("
        for field in fields:
            merge_sql += f"source.{field.upper()}, "

        # Remove trailing comma
        merge_sql = merge_sql[:-2] + ")"

        # Prepare bind data (same as for insert)
        bind_data = []
        for record in records:
            # Fill in any missing fields with None
            row_data = {}
            for field in fields:
                row_data[field] = record.get(field)

                # Handle JSON data
                if isinstance(row_data[field], dict | list):
                    row_data[field] = json.dumps(row_data[field])

            bind_data.append(row_data)

        return merge_sql, bind_data
