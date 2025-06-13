"""Stream discovery for Oracle DB."""

from singer_sdk import Stream
from singer_sdk import typing as th
from singer_sdk.streams import SQLStream
from tap_oracle_db.connection import OracleConnection


def discover_streams(tap, connection: OracleConnection) -> list[Stream]:
    """Discover streams from the database."""
    streams = []

    # Get configured tables/views/queries
    tables = tap.config.get("tables", [])
    views = tap.config.get("views", [])
    select_queries = tap.config.get("select_queries", [])

    # Default schema patterns
    include_schemas = tap.config.get("include_schemas", [])
    exclude_schemas = tap.config.get("exclude_schemas", ["SYS", "SYSTEM"])

    # Create streams for specifically configured tables
    if tables:
        streams.extend(
            create_table_stream(
                tap,
                connection,
                table_config.get("schema"),
                table_config.get("table_name"),
                table_config.get("replication_method"),
                table_config.get("replication_key"),
            )
            for table_config in tables
        )

    # Create streams for specifically configured views
    if views:
        streams.extend(
            create_view_stream(
                tap,
                connection,
                view_config.get("schema"),
                view_config.get("view_name"),
            )
            for view_config in views
        )

    # Create streams for custom SQL queries
    if select_queries:
        streams.extend(
            create_query_stream(
                tap,
                connection,
                query_config.get("name"),
                query_config.get("query"),
                query_config.get("replication_method"),
            )
            for query_config in select_queries
        )

    # If no specific tables/views/queries are configured, discover all tables/views
    if not tables and not views and not select_queries:
        streams.extend(
            discover_all_streams(tap, connection, include_schemas, exclude_schemas),
        )

    return streams


def create_table_stream(
    tap,
    connection: OracleConnection,
    schema_name: str | None,
    table_name: str,
    replication_method: str | None = None,
    replication_key: str | None = None,
) -> Stream:
    """Create a stream for a table."""
    conn = connection.get_connection()
    cursor = conn.cursor()

    # Set default schema if not provided
    if not schema_name:
        schema_name = connection.config.get("user").upper()

    # Get table columns
    query = """
    SELECT
        column_name,
        data_type,
        data_length,
        data_precision,
        data_scale,
        nullable
    FROM all_tab_columns
    WHERE owner = :owner
    AND table_name = :table_name
    ORDER BY column_id
    """
    cursor.execute(
        query,
        {"owner": schema_name.upper(), "table_name": table_name.upper()},
    )

    columns = []

    # Get primary keys
    pk_query = """
    SELECT cols.column_name
    FROM all_constraints cons, all_cons_columns cols
    WHERE cons.constraint_type = 'P'
    AND cons.constraint_name = cols.constraint_name
    AND cons.owner = cols.owner
    AND cons.owner = :owner
    AND cols.table_name = :table_name
    """
    cursor.execute(
        pk_query,
        {"owner": schema_name.upper(), "table_name": table_name.upper()},
    )
    pk_results = cursor.fetchall()
    primary_keys = [row[0] for row in pk_results]

    # Map columns to properties
    for row in cursor.fetchall():
        (
            column_name,
            data_type,
            _data_length,
            data_precision,
            data_scale,
            nullable,
        ) = row
        nullable = nullable == "Y"

        column_type = map_oracle_type_to_json_schema(
            data_type,
            data_precision,
            data_scale,
        )

        columns.append(
            th.Property(
                column_name.lower(),
                column_type,
                required=not nullable,
            ),
        )

    # Set replication method
    if not replication_method:
        replication_method = tap.config.get("default_replication_method", "INCREMENTAL")

    # Create schema
    schema = th.PropertiesList(*columns).to_dict()

    # Create class for the stream
    stream_class = type(
        f"{schema_name}_{table_name}_Stream",
        (SQLStream,),
        {
            "name": f"{schema_name.lower()}_{table_name.lower()}",
            "primary_keys": [pk.lower() for pk in primary_keys],
            "replication_key": (replication_key.lower() if replication_key else None),
            "schema": schema,
            "database": connection.config.get("service_name")
            or connection.config.get("sid"),
            "table": f"{schema_name}.{table_name}",
        },
    )

    return stream_class(tap=tap)


def create_view_stream(
    tap,
    connection: OracleConnection,
    schema_name: str | None,
    view_name: str,
) -> Stream:
    """Create a stream for a view."""
    # Views are handled the same way as tables for our purposes
    return create_table_stream(tap, connection, schema_name, view_name)


def create_query_stream(
    tap,
    connection: OracleConnection,
    name: str,
    query: str,
    replication_method: str | None = None,
) -> Stream:
    """Create a stream for a custom query."""
    conn = connection.get_connection()
    cursor = conn.cursor()

    # Execute query with ROWNUM=1 to get column structure
    limited_query = f"SELECT * FROM ({query}) WHERE ROWNUM = 1"
    cursor.execute(limited_query)

    columns = []
    for col in cursor.description:
        column_name = col[0]
        oracle_type = col[1]

        # Map type (simplistic approach)
        if oracle_type in {1, 96}:  # CHAR, NCHAR
            column_type = th.StringType()
        elif oracle_type in {2, 100}:  # NUMBER
            column_type = th.NumberType()
        elif oracle_type in {12, 178, 179, 180, 181, 231}:  # DATE, TIMESTAMP
            column_type = th.DateTimeType()
        elif oracle_type in {8, 112} or oracle_type in {
            23,
            24,
            69,
            208,
        }:  # LONG, CLOB
            column_type = th.StringType()
        else:
            column_type = th.StringType()  # Default

        columns.append(
            th.Property(
                column_name.lower(),
                column_type,
            ),
        )

    # Create schema
    schema = th.PropertiesList(*columns).to_dict()

    # Create class for the stream
    stream_class = type(
        f"{name}_Stream",
        (SQLStream,),
        {
            "name": name.lower(),
            "primary_keys": [],  # Custom queries may not have PKs
            "schema": schema,
            "database": connection.config.get("service_name")
            or connection.config.get("sid"),
            "query": query,
        },
    )

    return stream_class(tap=tap)


def discover_all_streams(
    tap,
    connection: OracleConnection,
    include_schemas: list[str],
    exclude_schemas: list[str],
) -> list[Stream]:
    """Discover all tables and views in the database."""
    conn = connection.get_connection()
    cursor = conn.cursor()

    schema_clause = ""
    params = {}

    # Build schema filter
    if include_schemas:
        schema_patterns = []
        for i, schema in enumerate(include_schemas):
            schema_patterns.append(f":include{i}")
            params[f"include{i}"] = schema.upper()
        schema_clause = f"AND owner IN ({', '.join(schema_patterns)})"
    elif exclude_schemas:
        schema_patterns = []
        for i, schema in enumerate(exclude_schemas):
            schema_patterns.append(f":exclude{i}")
            params[f"exclude{i}"] = schema.upper()
        schema_clause = f"AND owner NOT IN ({', '.join(schema_patterns)})"

    # Query for tables
    query = f"""
    SELECT owner, table_name
    FROM all_tables
    WHERE owner NOT LIKE 'BIN$%'
    {schema_clause}
    ORDER BY owner, table_name
    """
    cursor.execute(query, params)

    streams = []
    for row in cursor.fetchall():
        schema_name, table_name = row
        streams.append(
            create_table_stream(
                tap,
                connection,
                schema_name,
                table_name,
            ),
        )

    # Query for views
    view_query = f"""
    SELECT owner, view_name
    FROM all_views
    WHERE owner NOT LIKE 'BIN$%'
    {schema_clause}
    ORDER BY owner, view_name
    """
    cursor.execute(view_query, params)

    for row in cursor.fetchall():
        schema_name, view_name = row
        streams.append(
            create_view_stream(
                tap,
                connection,
                schema_name,
                view_name,
            ),
        )

    return streams


def map_oracle_type_to_json_schema(
    data_type: str,
    data_precision: int | None,
    data_scale: int | None,
) -> th.JSONTypeHelper:
    """Map Oracle data type to JSON schema type."""
    # Convert to uppercase for comparison
    data_type = data_type.upper()

    # Character types
    if data_type in {
        "CHAR",
        "NCHAR",
        "VARCHAR",
        "VARCHAR2",
        "NVARCHAR2",
        "CLOB",
        "NCLOB",
        "LONG",
    }:
        return th.StringType()

    # Numeric types
    if data_type == "NUMBER":
        if data_scale == 0 or data_scale is None:
            return th.IntegerType()
        return th.NumberType()
    if data_type in {"FLOAT", "BINARY_FLOAT", "BINARY_DOUBLE"}:
        return th.NumberType()

    # Date/time types
    if data_type in {
        "DATE",
        "TIMESTAMP",
        "TIMESTAMP WITH TIME ZONE",
        "TIMESTAMP WITH LOCAL TIME ZONE",
    }:
        return th.DateTimeType()

    # Binary types - encode as base64 strings
    if data_type in {"BLOB", "RAW", "LONG RAW"}:
        return th.StringType()

    # Boolean - Oracle doesn't have a native boolean
    if data_type == "BOOLEAN":
        return th.BooleanType()

    # Default to string for unknown types
    return th.StringType()
