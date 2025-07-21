"""Test configuration for flext-tap-oracle.

Provides pytest fixtures and configuration for testing Oracle Singer tap functionality
using real Oracle connections and Singer SDK patterns.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


# Test environment setup
@pytest.fixture(autouse=True)
def set_test_environment() -> Generator[None]:
    """Set test environment variables."""
    os.environ["FLEXT_ENV"] = "test"
    os.environ["FLEXT_LOG_LEVEL"] = "debug"
    os.environ["SINGER_SDK_LOG_LEVEL"] = "DEBUG"
    os.environ["ORACLE_TAP_TEST_MODE"] = "true"
    yield
    # Cleanup
    os.environ.pop("FLEXT_ENV", None)
    os.environ.pop("FLEXT_LOG_LEVEL", None)
    os.environ.pop("SINGER_SDK_LOG_LEVEL", None)
    os.environ.pop("ORACLE_TAP_TEST_MODE", None)


# Oracle connection fixtures
@pytest.fixture
def oracle_tap_config() -> dict[str, Any]:
    """Oracle tap configuration for testing."""
    return {
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "tap_user",
        "password": "tap_pass",
        "service_name": "XEPDB1",
        "default_replication_method": "INCREMENTAL",
        "filter_schemas": ["TAP_SCHEMA"],
        "batch_config": {
            "encoding": {
                "format": "jsonl",
                "compression": "gzip",
            },
        },
    }


@pytest.fixture
def oracle_tap(oracle_tap_config: dict[str, Any]) -> Any:
    """Oracle tap instance for testing."""
    from flext_tap_oracle.tap import TapOracle

    return TapOracle(config=oracle_tap_config)


# Singer protocol fixtures
@pytest.fixture
def singer_catalog() -> dict[str, Any]:
    """Singer catalog for testing."""
    return {
        "streams": [
            {
                "tap_stream_id": "employees",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": ["string", "null"]},
                        "department_id": {"type": ["integer", "null"]},
                        "hire_date": {"type": "string", "format": "date-time"},
                        "salary": {"type": "number"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "table-key-properties": ["id"],
                            "forced-replication-method": "INCREMENTAL",
                            "replication-key": "hire_date",
                        },
                    },
                    {
                        "breadcrumb": ["properties", "id"],
                        "metadata": {"inclusion": "automatic"},
                    },
                    {
                        "breadcrumb": ["properties", "name"],
                        "metadata": {"inclusion": "available"},
                    },
                ],
            },
            {
                "tap_stream_id": "departments",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "manager_id": {"type": ["integer", "null"]},
                        "created_at": {"type": "string", "format": "date-time"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "table-key-properties": ["id"],
                            "forced-replication-method": "FULL_TABLE",
                        },
                    },
                ],
            },
        ],
    }


@pytest.fixture
def singer_state() -> dict[str, Any]:
    """Singer state for testing."""
    return {
        "bookmarks": {
            "employees": {
                "replication_key": "hire_date",
                "replication_key_value": "2023-01-01T00:00:00Z",
                "version": 1,
            },
            "departments": {
                "version": 1,
            },
        },
    }


@pytest.fixture
def sample_oracle_tables() -> list[dict[str, Any]]:
    """Sample Oracle table definitions for testing."""
    return [
        {
            "table_name": "EMPLOYEES",
            "owner": "TAP_SCHEMA",
            "table_type": "TABLE",
            "columns": [
                {
                    "column_name": "ID",
                    "data_type": "NUMBER",
                    "data_length": 22,
                    "data_precision": 10,
                    "data_scale": 0,
                    "nullable": "N",
                    "column_id": 1,
                },
                {
                    "column_name": "NAME",
                    "data_type": "VARCHAR2",
                    "data_length": 100,
                    "nullable": "N",
                    "column_id": 2,
                },
                {
                    "column_name": "EMAIL",
                    "data_type": "VARCHAR2",
                    "data_length": 255,
                    "nullable": "Y",
                    "column_id": 3,
                },
                {
                    "column_name": "HIRE_DATE",
                    "data_type": "TIMESTAMP",
                    "data_length": 11,
                    "nullable": "N",
                    "column_id": 4,
                },
            ],
            "primary_key": ["ID"],
            "indexes": [
                {
                    "index_name": "PK_EMPLOYEES",
                    "uniqueness": "UNIQUE",
                    "columns": ["ID"],
                },
                {
                    "index_name": "IDX_EMPLOYEES_EMAIL",
                    "uniqueness": "NONUNIQUE",
                    "columns": ["EMAIL"],
                },
            ],
        },
        {
            "table_name": "DEPARTMENTS",
            "owner": "TAP_SCHEMA",
            "table_type": "TABLE",
            "columns": [
                {
                    "column_name": "ID",
                    "data_type": "NUMBER",
                    "data_precision": 10,
                    "data_scale": 0,
                    "nullable": "N",
                    "column_id": 1,
                },
                {
                    "column_name": "NAME",
                    "data_type": "VARCHAR2",
                    "data_length": 100,
                    "nullable": "N",
                    "column_id": 2,
                },
            ],
            "primary_key": ["ID"],
        },
    ]


@pytest.fixture
def sample_oracle_data() -> dict[str, list[dict[str, Any]]]:
    """Sample Oracle data for testing."""
    return {
        "employees": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "department_id": 1,
                "hire_date": "2022-01-15T09:00:00Z",
                "salary": 75000.00,
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "department_id": 2,
                "hire_date": "2022-03-01T09:00:00Z",
                "salary": 82000.00,
            },
            {
                "id": 3,
                "name": "Bob Johnson",
                "email": "bob.johnson@example.com",
                "department_id": 1,
                "hire_date": "2023-01-10T09:00:00Z",
                "salary": 68000.00,
            },
        ],
        "departments": [
            {
                "id": 1,
                "name": "Engineering",
                "manager_id": 1,
                "created_at": "2021-01-01T00:00:00Z",
            },
            {
                "id": 2,
                "name": "Marketing",
                "manager_id": 2,
                "created_at": "2021-01-01T00:00:00Z",
            },
        ],
    }


# Stream configuration fixtures
@pytest.fixture
def stream_config() -> dict[str, Any]:
    """Stream configuration for testing."""
    return {
        "selected": True,
        "replication_method": "INCREMENTAL",
        "replication_key": "hire_date",
        "key_properties": ["id"],
        "batch_size": 1000,
        "datetime_error_treatment": "max",
    }


@pytest.fixture
def discovery_config() -> dict[str, Any]:
    """Discovery configuration for testing."""
    return {
        "include_views": False,
        "include_system_tables": False,
        "filter_schemas": ["TAP_SCHEMA"],
        "filter_tables": None,
        "max_table_scan": 100,
        "discover_pk": True,
        "discover_fk": True,
    }


# SQL query fixtures
@pytest.fixture
def oracle_queries() -> dict[str, str]:
    """Oracle SQL queries for testing."""
    return {
        "list_tables": """
            SELECT table_name, owner, table_type
            FROM all_tables
            WHERE owner = :schema_name
            ORDER BY table_name
        """,
        "table_columns": """
            SELECT column_name, data_type, data_length, data_precision,
                   data_scale, nullable, column_id
            FROM all_tab_columns
            WHERE table_name = :table_name
            AND owner = :schema_name
            ORDER BY column_id
        """,
        "primary_keys": """
            SELECT cols.column_name
            FROM all_constraints cons
            JOIN all_cons_columns cols ON cons.constraint_name = cols.constraint_name
            WHERE cons.constraint_type = 'P'
            AND cons.table_name = :table_name
            AND cons.owner = :schema_name
            ORDER BY cols.position
        """,
        "select_with_replication_key": """
            SELECT {columns}
            FROM {schema}.{table}
            WHERE {replication_key} >= :bookmark_value
            ORDER BY {replication_key}
        """,
        "full_table_select": """
            SELECT {columns}
            FROM {schema}.{table}
            ORDER BY {key_properties}
        """,
    }


# Singer message fixtures
@pytest.fixture
def singer_schema_message() -> dict[str, Any]:
    """Singer schema message for testing."""
    return {
        "type": "SCHEMA",
        "stream": "employees",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": ["string", "null"]},
                "hire_date": {"type": "string", "format": "date-time"},
            },
        },
        "key_properties": ["id"],
    }


@pytest.fixture
def singer_record_messages() -> list[dict[str, Any]]:
    """Singer record messages for testing."""
    return [
        {
            "type": "RECORD",
            "stream": "employees",
            "record": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "hire_date": "2022-01-15T09:00:00Z",
            },
            "time_extracted": "2023-01-01T12:00:00Z",
        },
        {
            "type": "RECORD",
            "stream": "employees",
            "record": {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "hire_date": "2022-03-01T09:00:00Z",
            },
            "time_extracted": "2023-01-01T12:00:01Z",
        },
    ]


@pytest.fixture
def singer_state_message() -> dict[str, Any]:
    """Singer state message for testing."""
    return {
        "type": "STATE",
        "value": {
            "bookmarks": {
                "employees": {
                    "replication_key": "hire_date",
                    "replication_key_value": "2023-01-01T00:00:00Z",
                    "version": 1,
                },
            },
        },
    }


# Performance test fixtures
@pytest.fixture
def performance_test_config() -> dict[str, Any]:
    """Performance test configuration."""
    return {
        "large_table_rows": 100000,
        "batch_sizes": [100, 500, 1000, 5000],
        "concurrent_streams": 3,
        "memory_threshold": "1GB",
        "time_threshold": 300,  # 5 minutes
    }


# Error handling fixtures
@pytest.fixture
def error_scenarios() -> list[dict[str, Any]]:
    """Error scenarios for testing."""
    return [
        {
            "name": "connection_failure",
            "error_type": "DatabaseError",
            "oracle_error": "ORA-12541",
            "message": "TNS:no listener",
            "recovery_strategy": "reconnect",
        },
        {
            "name": "invalid_table",
            "error_type": "ProgrammingError",
            "oracle_error": "ORA-00942",
            "message": "table or view does not exist",
            "recovery_strategy": "skip_table",
        },
        {
            "name": "insufficient_privileges",
            "error_type": "DatabaseError",
            "oracle_error": "ORA-00942",
            "message": "insufficient privileges",
            "recovery_strategy": "log_warning",
        },
        {
            "name": "data_type_conversion",
            "error_type": "DataError",
            "oracle_error": "ORA-01722",
            "message": "invalid number",
            "recovery_strategy": "null_value",
        },
    ]


# Pytest markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "oracle: Oracle database tests")
    config.addinivalue_line("markers", "singer: Singer protocol tests")
    config.addinivalue_line("markers", "discovery: Schema discovery tests")
    config.addinivalue_line("markers", "extraction: Data extraction tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# Mock services
@pytest.fixture
def mock_oracle_tap() -> type[object]:
    """Mock Oracle tap for testing."""

    class MockOracleTap:
        def __init__(self, config: dict[str, Any]) -> None:
            self.config = config
            self._catalog = None
            self._state: dict[str, Any] = {}

        async def discover(self) -> dict[str, Any]:
            """Discover schema using mock data."""
            return {
                "streams": [
                    {
                        "tap_stream_id": "employees",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                            },
                        },
                        "metadata": [],
                    },
                ],
            }

        async def sync(
            self,
            catalog: dict[str, Any],
            state: dict[str, Any],
        ) -> AsyncGenerator[dict[str, Any]]:
            """Sync data using mock extraction."""
            for stream in catalog["streams"]:
                if stream.get("metadata", [{}])[0].get("metadata", {}).get("selected"):
                    yield {
                        "type": "SCHEMA",
                        "stream": stream["tap_stream_id"],
                        "schema": stream["schema"],
                        "key_properties": ["id"],
                    }

                    yield {
                        "type": "RECORD",
                        "stream": stream["tap_stream_id"],
                        "record": {"id": 1, "name": "Test Record"},
                        "time_extracted": "2023-01-01T12:00:00Z",
                    }

                    yield {
                        "type": "STATE",
                        "value": {
                            "bookmarks": {
                                stream["tap_stream_id"]: {
                                    "version": 1,
                                    "replication_key_value": "2023-01-01T12:00:00Z",
                                },
                            },
                        },
                    }

    return MockOracleTap


@pytest.fixture
def mock_oracle_connection() -> type[object]:
    """Mock Oracle connection for testing."""

    class MockOracleConnection:
        def __init__(self, config: dict[str, Any]) -> None:
            self.config = config
            self.connected = False

        async def connect(self) -> bool:
            self.connected = True
            return True

        async def disconnect(self) -> bool:
            self.connected = False
            return True

        async def execute_query(
            self,
            query: str,
            parameters: dict[str, Any] | None = None,
        ) -> list[dict[str, Any]]:
            """Execute query and return mock results."""
            if "all_tables" in query:
                return [
                    {
                        "table_name": "EMPLOYEES",
                        "owner": "TAP_SCHEMA",
                        "table_type": "TABLE",
                    },
                    {
                        "table_name": "DEPARTMENTS",
                        "owner": "TAP_SCHEMA",
                        "table_type": "TABLE",
                    },
                ]
            if "all_tab_columns" in query:
                return [
                    {
                        "column_name": "ID",
                        "data_type": "NUMBER",
                        "data_length": 22,
                        "nullable": "N",
                        "column_id": 1,
                    },
                    {
                        "column_name": "NAME",
                        "data_type": "VARCHAR2",
                        "data_length": 100,
                        "nullable": "N",
                        "column_id": 2,
                    },
                ]
            return [{"id": 1, "name": "Test Record"}]

        async def get_table_schema(self, table_name: str) -> dict[str, Any]:
            """Get table schema information."""
            return {
                "table_name": table_name,
                "columns": [
                    {"name": "id", "type": "NUMBER", "nullable": False},
                    {"name": "name", "type": "VARCHAR2", "nullable": False},
                ],
                "primary_key": ["id"],
            }

    return MockOracleConnection
