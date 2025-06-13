"""OIC to ADB Client.

This module provides functionality to load data from OIC to Oracle Autonomous Database.
"""

import logging
import os
from typing import Any

import cx_Oracle
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


class OICADBClient:
    """Client for loading data from OIC to Oracle ADB."""

    def __init__(
        self,
        oic_base_url: str,
        oic_username: str,
        oic_password: str,
        adb_username: str,
        adb_password: str,
        adb_dsn: str,
        adb_wallet_path: str | None = None,
        adb_schema: str | None = None,
    ) -> None:
        """Initialize OIC to ADB client.

        Args:
            oic_base_url: OIC base URL
            oic_username: OIC username
            oic_password: OIC password
            adb_username: ADB username
            adb_password: ADB password
            adb_dsn: ADB connection string
            adb_wallet_path: Path to Oracle wallet
            adb_schema: Default ADB schema

        """
        self.oic_base_url = oic_base_url.rstrip("/")
        self.oic_auth = HTTPBasicAuth(oic_username, oic_password)
        self.oic_session = requests.Session()

        self.adb_username = adb_username
        self.adb_password = adb_password
        self.adb_dsn = adb_dsn
        self.adb_wallet_path = adb_wallet_path
        self.adb_schema = adb_schema

        # Set wallet location if provided
        if adb_wallet_path:
            os.environ["TNS_ADMIN"] = adb_wallet_path

        self.adb_connection = None
        self.adb_engine = None

    def connect_adb(self) -> None:
        """Connect to Oracle ADB."""
        try:
            self.adb_connection = cx_Oracle.connect(
                user=self.adb_username,
                password=self.adb_password,
                dsn=self.adb_dsn,
            )

            # Create SQLAlchemy engine
            conn_str = f"oracle+cx_oracle://{self.adb_username}:{self.adb_password}@{self.adb_dsn}"
            self.adb_engine = create_engine(conn_str)

            logger.info(f"Connected to Oracle ADB: {self.adb_dsn}")
        except Exception as e:
            logger.exception(f"Failed to connect to Oracle ADB: {e!s}")
            raise

    def disconnect_adb(self) -> None:
        """Disconnect from Oracle ADB."""
        if self.adb_connection:
            self.adb_connection.close()
            self.adb_connection = None
            logger.info("Disconnected from Oracle ADB")

    def get_oic_integrations(self) -> list[dict]:
        """Get list of OIC integrations.

        Returns:
            list of integration configurations

        """
        endpoint = f"{self.oic_base_url}/ic/api/integration/v1/integrations"
        response = self.oic_session.get(endpoint, auth=self.oic_auth, timeout=60)
        response.raise_for_status()
        return response.json()

    def get_oic_integration(self, integration_id: str) -> dict:
        """Get details of a specific OIC integration.

        Args:
            integration_id: Integration ID

        Returns:
            Integration details

        """
        endpoint = (
            f"{self.oic_base_url}/ic/api/integration/v1/integrations/{integration_id}"
        )
        response = self.oic_session.get(endpoint, auth=self.oic_auth, timeout=60)
        response.raise_for_status()
        return response.json()

    def get_oic_integration_executions(self, integration_id: str) -> list[dict]:
        """Get execution history for an OIC integration.

        Args:
            integration_id: Integration ID

        Returns:
            list of execution records

        """
        endpoint = f"{self.oic_base_url}/ic/api/integration/v1/monitoring/integrations/{integration_id}/instances"
        response = self.oic_session.get(endpoint, auth=self.oic_auth, timeout=60)
        response.raise_for_status()
        return response.json()

    def get_oic_execution_details(self, execution_id: str) -> dict:
        """Get details of a specific OIC execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details

        """
        endpoint = f"{self.oic_base_url}/ic/api/integration/v1/monitoring/instances/{execution_id}"
        response = self.oic_session.get(endpoint, auth=self.oic_auth, timeout=60)
        response.raise_for_status()
        return response.json()

    def execute_adb_query(self, query: str, params: dict | None = None) -> list[dict]:
        """Execute a SQL query on Oracle ADB.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query results as list of dictionaries

        """
        if not self.adb_connection:
            self.connect_adb()

        cursor = self.adb_connection.cursor()
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

    def execute_adb_dml(self, query: str, params: dict | None = None) -> int:
        """Execute a DML query on Oracle ADB.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Number of affected rows

        """
        if not self.adb_connection:
            self.connect_adb()

        cursor = self.adb_connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            affected_rows = cursor.rowcount
            self.adb_connection.commit()
            return affected_rows
        finally:
            cursor.close()

    def create_adb_table(
        self,
        table_name: str,
        columns: list[dict[str, Any]],
        drop_if_exists: bool = False,
    ) -> None:
        """Create a table in Oracle ADB.

        Args:
            table_name: Table name
            columns: list of column definitions
            drop_if_exists: Whether to drop the table if it exists

        """
        if not self.adb_connection:
            self.connect_adb()

        # Check if table exists
        query = """
        SELECT
            COUNT(*) AS COUNT
        FROM
            ALL_TABLES
        WHERE
            TABLE_NAME = :table_name
        """

        if self.adb_schema:
            query += " AND OWNER = :owner"
            params = {
                "table_name": table_name.upper(),
                "owner": self.adb_schema.upper(),
            }
        else:
            params = {"table_name": table_name.upper()}

        result = self.execute_adb_query(query, params)
        table_exists = result[0]["COUNT"] > 0

        if table_exists:
            if drop_if_exists:
                self.execute_adb_dml(f"DROP TABLE {table_name}")
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
        self.execute_adb_dml(sql)

    def load_oic_data_to_adb(
        self,
        integration_id: str,
        execution_id: str | None = None,
        table_name: str | None = None,
        auto_create_table: bool = True,
    ) -> int:
        """Load data from OIC integration execution to Oracle ADB.

        Args:
            integration_id: Integration ID
            execution_id: Execution ID (most recent if None)
            table_name: Target table name (if None, uses integration ID)
            auto_create_table: Whether to auto-create the table if it doesn't exist

        Returns:
            Number of loaded rows

        """
        # Get execution details
        if not execution_id:
            # Get most recent execution
            executions = self.get_oic_integration_executions(integration_id)
            if not executions:
                logger.warning(f"No executions found for integration {integration_id}")
                return 0

            # Sort by start time and get most recent
            executions.sort(key=lambda x: x.get("startTime", ""), reverse=True)
            execution_id = executions[0]["id"]

        execution = self.get_oic_execution_details(execution_id)

        # Extract payload data
        if "payload" not in execution or not execution["payload"]:
            logger.warning(f"No payload data found in execution {execution_id}")
            return 0

        payload = execution["payload"]

        # Determine table name
        if not table_name:
            table_name = f"OIC_{integration_id.replace('-', '_')}"

        # Auto-create table if needed
        if auto_create_table:
            # Extract schema from payload
            if isinstance(payload, list) and payload:
                first_row = payload[0]
                columns = []
                for key, value in first_row.items():
                    column = {"name": key, "nullable": True}

                    if isinstance(value, int):
                        column["data_type"] = "NUMBER"
                    elif isinstance(value, float):
                        column["data_type"] = "NUMBER"
                        column["precision"] = 38
                        column["scale"] = 10
                    elif isinstance(value, bool):
                        column["data_type"] = "NUMBER"
                        column["precision"] = 1
                    elif isinstance(value, dict | list):
                        column["data_type"] = "CLOB"
                    else:
                        column["data_type"] = "VARCHAR2"
                        column["length"] = 4000

                    columns.append(column)

                # Add metadata columns
                columns.extend(
                    (
                        {
                            "name": "OIC_INTEGRATION_ID",
                            "data_type": "VARCHAR2",
                            "length": 255,
                            "nullable": False,
                        },
                        {
                            "name": "OIC_EXECUTION_ID",
                            "data_type": "VARCHAR2",
                            "length": 255,
                            "nullable": False,
                        },
                        {
                            "name": "OIC_LOADED_AT",
                            "data_type": "TIMESTAMP",
                            "nullable": False,
                        },
                    ),
                )

                # Create the table
                self.create_adb_table(table_name, columns, drop_if_exists=False)

        # Convert payload to DataFrame
        df = pd.DataFrame([payload]) if isinstance(payload, dict) else pd.DataFrame(payload)

        # Add metadata columns
        df["OIC_INTEGRATION_ID"] = integration_id
        df["OIC_EXECUTION_ID"] = execution_id
        df["OIC_LOADED_AT"] = pd.Timestamp.now()

        # Load data into ADB
        if not self.adb_engine:
            self.connect_adb()

        logger.info(f"Loading {len(df)} rows into {table_name}")
        df.to_sql(
            table_name,
            self.adb_engine,
            if_exists="append",
            index=False,
            schema=self.adb_schema,
        )

        return len(df)

    def sync_all_oic_integrations_to_adb(
        self,
        integration_filter: str | None = None,
        max_executions_per_integration: int = 1,
        table_prefix: str = "OIC_",
        auto_create_tables: bool = True,
    ) -> dict:
        """Sync data from all OIC integrations to Oracle ADB.

        Args:
            integration_filter: Regex filter for integration IDs
            max_executions_per_integration: Maximum number of executions per integration
            table_prefix: Prefix for auto-generated table names
            auto_create_tables: Whether to auto-create tables if they don't exist

        Returns:
            Sync statistics

        """
        import re

        # Connect to ADB if not already connected
        if not self.adb_connection:
            self.connect_adb()

        # Get all integrations
        integrations = self.get_oic_integrations()
        logger.info(f"Found {len(integrations)} OIC integrations")

        # Apply filter if provided
        if integration_filter:
            pattern = re.compile(integration_filter)
            integrations = [i for i in integrations if pattern.match(i["id"])]
            logger.info(
                f"Filtered to {len(integrations)} integrations matching '{integration_filter}'",
            )

        # Initialize stats
        stats = {
            "total_integrations": len(integrations),
            "processed_integrations": 0,
            "total_executions": 0,
            "total_rows": 0,
            "errors": 0,
            "details": [],
        }

        # Process each integration
        for integration in integrations:
            integration_id = integration["id"]
            integration_name = integration.get("name", integration_id)

            try:
                # Get executions for this integration
                executions = self.get_oic_integration_executions(integration_id)

                # Sort by start time and get most recent N
                executions.sort(key=lambda x: x.get("startTime", ""), reverse=True)
                executions = executions[:max_executions_per_integration]

                integration_stats = {
                    "integration_id": integration_id,
                    "integration_name": integration_name,
                    "executions_processed": 0,
                    "total_rows": 0,
                    "errors": 0,
                }

                # Process each execution
                for execution in executions:
                    execution_id = execution["id"]
                    table_name = f"{table_prefix}{integration_id.replace('-', '_')}"

                    try:
                        rows = self.load_oic_data_to_adb(
                            integration_id=integration_id,
                            execution_id=execution_id,
                            table_name=table_name,
                            auto_create_table=auto_create_tables,
                        )

                        integration_stats["executions_processed"] += 1
                        integration_stats["total_rows"] += rows
                        stats["total_executions"] += 1
                        stats["total_rows"] += rows

                    except Exception as e:
                        logger.exception(
                            f"Error processing execution {execution_id}: {e!s}",
                        )
                        integration_stats["errors"] += 1
                        stats["errors"] += 1

                stats["details"].append(integration_stats)
                stats["processed_integrations"] += 1

            except Exception as e:
                logger.exception(
                    f"Error processing integration {integration_id}: {e!s}",
                )
                stats["errors"] += 1
                stats["details"].append(
                    {
                        "integration_id": integration_id,
                        "integration_name": integration_name,
                        "error": str(e),
                    },
                )

        logger.info(
            f"Completed sync: {stats['processed_integrations']} integrations, "
            f"{stats['total_executions']} executions, {stats['total_rows']} rows",
        )
        return stats
