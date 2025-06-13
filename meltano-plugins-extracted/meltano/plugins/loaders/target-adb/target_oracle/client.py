"""Oracle ADB Client.

This module provides a client for interacting with Oracle Autonomous Database.
"""

import json
import logging
import os
from typing import Any

import cx_Oracle
import pandas as pd
from sqlalchemy import MetaData, create_engine

logger = logging.getLogger(__name__)


class OracleADBClient:
    """Client for interacting with Oracle Autonomous Database."""

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
        self.metadata = MetaData()

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

    def execute_dml(self, query: str, params: dict | None = None) -> int:
        """Execute a DML query (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows

        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            affected_rows = cursor.rowcount
            self.connection.commit()
            return affected_rows
        finally:
            cursor.close()

    def bulk_insert(self, table_name: str, data: list[dict]) -> int:
        """Insert multiple rows into a table.

        Args:
            table_name: Table name
            data: list of row dictionaries

        Returns:
            Number of inserted rows

        """
        if not self.connection:
            self.connect()

        if not data:
            return 0

        # Get column names from first row
        columns = list(data[0].keys())
        column_names = ", ".join(columns)
        placeholders = ", ".join([f":{i + 1}" for i in range(len(columns))])

        # Prepare SQL
        sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        # Convert data to list of tuples
        rows = [[row.get(col) for col in columns] for row in data]

        cursor = self.connection.cursor()
        try:
            cursor.executemany(sql, rows)
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    def get_table_schema(self, table_name: str) -> list[dict]:
        """Get schema information for a table.

        Args:
            table_name: Table name

        Returns:
            Table schema

        """
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
        """

        if self.schema:
            query += " AND OWNER = :owner"
            params = {
                "table_name": table_name.upper(),
                "owner": self.schema.upper(),
            }
        else:
            params = {"table_name": table_name.upper()}

        return self.execute_query(query, params)

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists.

        Args:
            table_name: Table name

        Returns:
            True if table exists, False otherwise

        """
        query = """
        SELECT
            COUNT(*) AS COUNT
        FROM
            ALL_TABLES
        WHERE
            TABLE_NAME = :table_name
        """

        if self.schema:
            query += " AND OWNER = :owner"
            params = {
                "table_name": table_name.upper(),
                "owner": self.schema.upper(),
            }
        else:
            params = {"table_name": table_name.upper()}

        result = self.execute_query(query, params)
        return result[0]["COUNT"] > 0

    def create_table(
        self,
        table_name: str,
        columns: list[dict[str, Any]],
        drop_if_exists: bool = False,
    ) -> None:
        """Create a table.

        Args:
            table_name: Table name
            columns: list of column definitions
            drop_if_exists: Whether to drop the table if it exists

        """
        if not self.connection:
            self.connect()

        # Check if table exists
        if self.table_exists(table_name):
            if drop_if_exists:
                self.execute_dml(f"DROP TABLE {table_name}")
            else:
                logger.info(f"Table {table_name} already exists, skipping creation")
                return

        # Build CREATE TABLE SQL
        column_defs = []
        for col in columns:
            nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
            data_type = col["data_type"]

            if col.get("length"):
                data_type = f"{data_type}({col['length']})"

            if (
                "precision" in col
                and "scale" in col
                and col["precision"]
                and col["scale"]
            ):
                data_type = f"{data_type}({col['precision']}, {col['scale']})"

            column_defs.append(f"{col['name']} {data_type} {nullable}")

        sql = f"CREATE TABLE {table_name} (\n    "
        sql += ",\n    ".join(column_defs)
        sql += "\n)"

        logger.info(f"Creating table {table_name}")
        self.execute_dml(sql)

    def load_data_from_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "append",
    ) -> int:
        """Load data from a pandas DataFrame into a table.

        Args:
            df: Pandas DataFrame
            table_name: Target table name
            if_exists: Action if table exists: 'append', 'replace', 'fail'

        Returns:
            Number of loaded rows

        """
        if not self.connection:
            self.connect()

        logger.info(f"Loading {len(df)} rows into {table_name}")
        df.to_sql(
            table_name,
            self.engine,
            if_exists=if_exists,
            index=False,
            schema=self.schema,
        )

        return len(df)

    def load_data_from_json(
        self,
        data: list[dict] | dict,
        table_name: str,
        if_exists: str = "append",
    ) -> int:
        """Load data from JSON into a table.

        Args:
            data: JSON data as list of dictionaries or dictionary
            table_name: Target table name
            if_exists: Action if table exists: 'append', 'replace', 'fail'

        Returns:
            Number of loaded rows

        """
        # Convert single dict to list
        if isinstance(data, dict):
            data = [data]

        # Convert to DataFrame
        df = pd.DataFrame(data)

        return self.load_data_from_dataframe(df, table_name, if_exists)

    def load_data_from_file(
        self,
        file_path: str,
        table_name: str,
        if_exists: str = "append",
        file_format: str = "json",
    ) -> int:
        """Load data from a file into a table.

        Args:
            file_path: Path to input file
            table_name: Target table name
            if_exists: Action if table exists: 'append', 'replace', 'fail'
            file_format: File format ('json', 'csv')

        Returns:
            Number of loaded rows

        """
        if file_format == "json":
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            return self.load_data_from_json(data, table_name, if_exists)
        if file_format == "csv":
            df = pd.read_csv(file_path)
            return self.load_data_from_dataframe(df, table_name, if_exists)
        msg = f"Unsupported file format: {file_format}"
        raise ValueError(msg)

    def export_data_to_dataframe(
        self,
        query: str,
        params: dict | None = None,
    ) -> pd.DataFrame:
        """Export data to a pandas DataFrame.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Pandas DataFrame

        """
        results = self.execute_query(query, params)
        return pd.DataFrame(results)

    def export_data_to_file(
        self,
        query: str,
        file_path: str,
        params: dict | None = None,
        file_format: str = "json",
    ) -> int:
        """Export data to a file.

        Args:
            query: SQL query
            file_path: Output file path
            params: Query parameters
            file_format: Output file format ('json', 'csv')

        Returns:
            Number of exported rows

        """
        df = self.export_data_to_dataframe(query, params)

        if file_format == "json":
            df.to_json(file_path, orient="records", lines=False, indent=2)
        elif file_format == "csv":
            df.to_csv(file_path, index=False)
        else:
            msg = f"Unsupported file format: {file_format}"
            raise ValueError(msg)

        return len(df)
