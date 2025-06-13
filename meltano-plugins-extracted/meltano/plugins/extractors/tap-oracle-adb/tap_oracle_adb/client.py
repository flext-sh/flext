"""Oracle ADB Client.

This module provides a client for extracting data from Oracle Autonomous Database.
"""

import logging
import os

import cx_Oracle
import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class OracleADBClient:
    """Client for extracting data from Oracle Autonomous Database."""

    def __init__(
        self,
        username: str,
        password: str,
        dsn: str,
        wallet_path: str | None = None,
        schema: str | None = None,
    ) -> None:
        """Initialize Oracle ADB client.

        Args:
            username: Database username
            password: Database password
            dsn: Database connection string
            wallet_path: Path to Oracle wallet
            schema: Default schema

        """
        self.username = username
        self.password = password
        self.dsn = dsn
        self.wallet_path = wallet_path
        self.schema = schema

        # Set wallet location if provided
        if wallet_path:
            os.environ["TNS_ADMIN"] = wallet_path

        self.connection = None
        self.engine = None

    def connect(self) -> None:
        """Connect to Oracle database."""
        try:
            self.connection = cx_Oracle.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn,
            )

            # Create SQLAlchemy engine
            conn_str = f"oracle+cx_oracle://{self.username}:{self.password}@{self.dsn}"
            self.engine = create_engine(conn_str)

            logger.info(f"Connected to Oracle database: {self.dsn}")
        except Exception as e:
            logger.exception(f"Failed to connect to Oracle database: {e!s}")
            raise

    def disconnect(self) -> None:
        """Disconnect from Oracle database."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from Oracle database")

    def __enter__(self):
        """Enter context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.disconnect()

    def execute_query(self, query: str, params: dict | None = None) -> list[dict]:
        """Execute a SQL query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query results as list of dictionaries

        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get column names
            columns = [col[0] for col in cursor.description]

            # Fetch results
            return [dict(zip(columns, row, strict=False)) for row in cursor]

        finally:
            cursor.close()

    def query_to_dataframe(
        self,
        query: str,
        params: dict | None = None,
    ) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query results as pandas DataFrame

        """
        if not self.engine:
            self.connect()

        if params:
            return pd.read_sql_query(text(query), self.engine, params=params)
        return pd.read_sql_query(text(query), self.engine)

    def get_tables(self, schema: str | None = None) -> list[str]:
        """Get list of tables in a schema.

        Args:
            schema: Schema name (defaults to user's schema)

        Returns:
            list of table names

        """
        schema_name = schema or self.schema or self.username.upper()

        query = """
        SELECT
            TABLE_NAME
        FROM
            ALL_TABLES
        WHERE
            OWNER = :schema_name
        ORDER BY
            TABLE_NAME
        """

        results = self.execute_query(query, {"schema_name": schema_name.upper()})
        return [row["TABLE_NAME"] for row in results]

    def get_table_schema(
        self,
        table_name: str,
        schema: str | None = None,
    ) -> list[dict]:
        """Get schema information for a table.

        Args:
            table_name: Table name
            schema: Schema name (defaults to user's schema)

        Returns:
            Table schema

        """
        schema_name = schema or self.schema or self.username.upper()

        query = """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            DATA_LENGTH,
            DATA_PRECISION,
            DATA_SCALE,
            NULLABLE
        FROM
            ALL_TAB_COLUMNS
        WHERE
            TABLE_NAME = :table_name
            AND OWNER = :schema_name
        ORDER BY
            COLUMN_ID
        """

        return self.execute_query(
            query,
            {
                "table_name": table_name.upper(),
                "schema_name": schema_name.upper(),
            },
        )

    def get_table_data(
        self,
        table_name: str,
        schema: str | None = None,
        columns: list[str] | None = None,
        where: str | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> pd.DataFrame:
        """Get data from a table.

        Args:
            table_name: Table name
            schema: Schema name (defaults to user's schema)
            columns: list of columns to select
            where: WHERE clause
            order_by: ORDER BY clause
            limit: LIMIT clause
            offset: OFFSET clause

        Returns:
            Table data as pandas DataFrame

        """
        schema_name = schema or self.schema or self.username.upper()

        # Build column list
        column_list = ", ".join(columns) if columns else "*"

        # Build query
        query = f"SELECT {column_list} FROM {schema_name}.{table_name}"

        if where:
            query += f" WHERE {where}"

        if order_by:
            query += f" ORDER BY {order_by}"

        # Oracle doesn't have LIMIT/OFFSET directly, use ROWNUM instead
        if limit or offset:
            # If only limit is provided
            if limit and not offset:
                query = f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit}"
            # If both limit and offset are provided
            elif limit and offset:
                query = f"""
                SELECT *
                FROM (
                    SELECT a.*, ROWNUM rnum
                    FROM ({query}) a
                    WHERE ROWNUM <= {limit + offset}
                )
                WHERE rnum > {offset}
                """
            # If only offset is provided
            elif offset and not limit:
                query = f"""
                SELECT *
                FROM (
                    SELECT a.*, ROWNUM rnum
                    FROM ({query}) a
                )
                WHERE rnum > {offset}
                """

        return self.query_to_dataframe(query)

    def extract_table_to_json(
        self,
        table_name: str,
        output_file: str,
        schema: str | None = None,
        where: str | None = None,
        batch_size: int = 10000,
    ) -> int:
        """Extract table data to a JSON file.

        Args:
            table_name: Table name
            output_file: Output file path
            schema: Schema name (defaults to user's schema)
            where: WHERE clause
            batch_size: Batch size for extraction

        Returns:
            Number of extracted rows

        """
        schema_name = schema or self.schema or self.username.upper()

        # Get total row count
        count_query = f"SELECT COUNT(*) AS ROW_COUNT FROM {schema_name}.{table_name}"
        if where:
            count_query += f" WHERE {where}"

        count_result = self.execute_query(count_query)
        total_rows = count_result[0]["ROW_COUNT"]

        logger.info(f"Extracting {total_rows} rows from {schema_name}.{table_name}")

        # Extract data in batches
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("[\n")

            for offset in range(0, total_rows, batch_size):
                df = self.get_table_data(
                    table_name=table_name,
                    schema=schema_name,
                    where=where,
                    limit=batch_size,
                    offset=offset,
                )

                # Write batch to file
                batch_json = df.to_json(
                    orient="records",
                    lines=False,
                    date_format="iso",
                )
                # Remove square brackets from batch JSON
                batch_json = batch_json[1:-1]

                if offset > 0:
                    f.write(",\n")

                f.write(batch_json)

                logger.info(f"Extracted {offset + len(df)} of {total_rows} rows")

                # If batch is smaller than batch_size, we're done
                if len(df) < batch_size:
                    break

            f.write("\n]")

        logger.info(f"Extracted {total_rows} rows to {output_file}")
        return total_rows

    def extract_table_to_csv(
        self,
        table_name: str,
        output_file: str,
        schema: str | None = None,
        where: str | None = None,
        batch_size: int = 10000,
    ) -> int:
        """Extract table data to a CSV file.

        Args:
            table_name: Table name
            output_file: Output file path
            schema: Schema name (defaults to user's schema)
            where: WHERE clause
            batch_size: Batch size for extraction

        Returns:
            Number of extracted rows

        """
        schema_name = schema or self.schema or self.username.upper()

        # Get total row count
        count_query = f"SELECT COUNT(*) AS ROW_COUNT FROM {schema_name}.{table_name}"
        if where:
            count_query += f" WHERE {where}"

        count_result = self.execute_query(count_query)
        total_rows = count_result[0]["ROW_COUNT"]

        logger.info(f"Extracting {total_rows} rows from {schema_name}.{table_name}")

        # Extract data in batches

        for offset in range(0, total_rows, batch_size):
            df = self.get_table_data(
                table_name=table_name,
                schema=schema_name,
                where=where,
                limit=batch_size,
                offset=offset,
            )

            # Write batch to file
            if offset == 0:
                df.to_csv(output_file, index=False, mode="w")
            else:
                df.to_csv(output_file, index=False, mode="a", header=False)

            logger.info(f"Extracted {offset + len(df)} of {total_rows} rows")

            # If batch is smaller than batch_size, we're done
            if len(df) < batch_size:
                break

        logger.info(f"Extracted {total_rows} rows to {output_file}")
        return total_rows

    def extract_query_to_json(
        self,
        query: str,
        output_file: str,
        params: dict | None = None,
        batch_size: int = 10000,
    ) -> int:
        """Extract query results to a JSON file.

        Args:
            query: SQL query
            output_file: Output file path
            params: Query parameters
            batch_size: Batch size for extraction

        Returns:
            Number of extracted rows

        """
        # Get total row count (using ROWNUM in a subquery)
        count_query = f"SELECT COUNT(*) AS ROW_COUNT FROM ({query})"

        count_result = self.execute_query(count_query, params) if params else self.execute_query(count_query)

        total_rows = count_result[0]["ROW_COUNT"]

        logger.info(f"Extracting {total_rows} rows from query")

        # Extract data in batches
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("[\n")

            for offset in range(0, total_rows, batch_size):
                # Modify query to include pagination
                paginated_query = f"""
                SELECT *
                FROM (
                    SELECT a.*, ROWNUM rnum
                    FROM ({query}) a
                    WHERE ROWNUM <= {offset + batch_size}
                )
                WHERE rnum > {offset}
                """

                # Execute paginated query
                if params:
                    df = self.query_to_dataframe(paginated_query, params)
                else:
                    df = self.query_to_dataframe(paginated_query)

                # Remove rnum column
                if "RNUM" in df.columns:
                    df = df.drop(columns=["RNUM"])

                # Write batch to file
                batch_json = df.to_json(
                    orient="records",
                    lines=False,
                    date_format="iso",
                )
                # Remove square brackets from batch JSON
                batch_json = batch_json[1:-1]

                if offset > 0:
                    f.write(",\n")

                f.write(batch_json)

                logger.info(f"Extracted {offset + len(df)} of {total_rows} rows")

                # If batch is smaller than batch_size, we're done
                if len(df) < batch_size:
                    break

            f.write("\n]")

        logger.info(f"Extracted {total_rows} rows to {output_file}")
        return total_rows

    def extract_query_to_csv(
        self,
        query: str,
        output_file: str,
        params: dict | None = None,
        batch_size: int = 10000,
    ) -> int:
        """Extract query results to a CSV file.

        Args:
            query: SQL query
            output_file: Output file path
            params: Query parameters
            batch_size: Batch size for extraction

        Returns:
            Number of extracted rows

        """
        # Get total row count (using ROWNUM in a subquery)
        count_query = f"SELECT COUNT(*) AS ROW_COUNT FROM ({query})"

        count_result = self.execute_query(count_query, params) if params else self.execute_query(count_query)

        total_rows = count_result[0]["ROW_COUNT"]

        logger.info(f"Extracting {total_rows} rows from query")

        # Extract data in batches

        for offset in range(0, total_rows, batch_size):
            # Modify query to include pagination
            paginated_query = f"""
            SELECT *
            FROM (
                SELECT a.*, ROWNUM rnum
                FROM ({query}) a
                WHERE ROWNUM <= {offset + batch_size}
            )
            WHERE rnum > {offset}
            """

            # Execute paginated query
            if params:
                df = self.query_to_dataframe(paginated_query, params)
            else:
                df = self.query_to_dataframe(paginated_query)

            # Remove rnum column
            if "RNUM" in df.columns:
                df = df.drop(columns=["RNUM"])

            # Write batch to file
            if offset == 0:
                df.to_csv(output_file, index=False, mode="w")
            else:
                df.to_csv(output_file, index=False, mode="a", header=False)

            logger.info(f"Extracted {offset + len(df)} of {total_rows} rows")

            # If batch is smaller than batch_size, we're done
            if len(df) < batch_size:
                break

        logger.info(f"Extracted {total_rows} rows to {output_file}")
        return total_rows
