"""Test configuration for flext-dbt-oracle.

Provides pytest fixtures and configuration for testing dbt Oracle adapter functionality
using real Oracle connections and dbt-core patterns.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


# Test environment setup
@pytest.fixture(autouse=True)
def set_test_environment() -> Generator[None]:
    """Set test environment variables."""
    os.environ["FLEXT_ENV"] = "test"
    os.environ["FLEXT_LOG_LEVEL"] = "debug"
    import tempfile

    temp_dir = tempfile.mkdtemp(prefix="dbt_profiles_")
    os.environ["DBT_PROFILES_DIR"] = temp_dir
    os.environ["DBT_TEST_USER_1"] = "dbt_test_user_1"
    os.environ["DBT_TEST_USER_2"] = "dbt_test_user_2"
    os.environ["DBT_TEST_USER_3"] = "dbt_test_user_3"
    yield
    # Cleanup
    os.environ.pop("FLEXT_ENV", None)
    os.environ.pop("FLEXT_LOG_LEVEL", None)
    os.environ.pop("DBT_PROFILES_DIR", None)
    os.environ.pop("DBT_TEST_USER_1", None)
    os.environ.pop("DBT_TEST_USER_2", None)
    os.environ.pop("DBT_TEST_USER_3", None)


# dbt configuration fixtures
@pytest.fixture
def dbt_oracle_profile() -> dict[str, Any]:
    """Dbt Oracle profile configuration for testing."""
    return {
        "config": {
            "partial_parse": True,
            "printer_width": 120,
            "send_anonymous_usage_stats": False,
            "use_colors": True,
        },
        "test": {
            "outputs": {
                "default": {
                    "type": "oracle",
                    "host": "localhost",
                    "port": 1521,
                    "database": "XEPDB1",
                    "schema": "DBT_TEST",
                    "user": "dbt_test_user",
                    "password": "dbt_test_pass",
                    "protocol": "tcp",
                    "service": "XEPDB1",
                    "threads": 4,
                    "keepalives_idle": 0,
                    "search_path": "DBT_TEST",
                },
                "ci": {
                    "type": "oracle",
                    "host": "oracle-ci.test.com",
                    "port": 1521,
                    "database": "CIDB",
                    "schema": "DBT_CI",
                    "user": "{{ env_var('DBT_TEST_USER_1') }}",
                    "password": "{{ env_var('DBT_TEST_PASS_1') }}",
                    "service": "CIDB",
                    "threads": 2,
                },
            },
            "target": "default",
        },
    }


@pytest.fixture
def dbt_project_config() -> dict[str, Any]:
    """Dbt project configuration for testing."""
    return {
        "name": "flext_dbt_oracle_test",
        "version": "1.0.0",
        "profile": "test",
        "model-paths": ["models"],
        "analysis-paths": ["analyses"],
        "test-paths": ["tests"],
        "seed-paths": ["seeds"],
        "macro-paths": ["macros"],
        "snapshot-paths": ["snapshots"],
        "docs-paths": ["docs"],
        "asset-paths": ["assets"],
        "target-path": "target",
        "clean-targets": ["target", "dbt_packages"],
        "require-dbt-version": ">=1.8.0",
        "model_config": {
            "materialized": "table",
            "oracle": {
                "tablespace": "USERS",
                "compression": "NONE",
                "parallel": 4,
            },
        },
        "vars": {
            "test_schema": "DBT_TEST",
            "test_database": "XEPDB1",
            "enable_oracle_features": True,
        },
    }


# Oracle adapter fixtures
@pytest.fixture
def oracle_adapter_config() -> dict[str, Any]:
    """Oracle adapter configuration for testing."""
    return {
        "type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "XEPDB1",
        "schema": "DBT_TEST",
        "user": "dbt_test_user",
        "password": "dbt_test_pass",
        "service": "XEPDB1",
        "protocol": "tcp",
        "threads": 4,
        "keepalives_idle": 0,
        "search_path": "DBT_TEST",
        "oracle_features": {
            "enable_merge": True,
            "enable_parallel": True,
            "enable_hints": True,
            "enable_compression": False,
        },
    }


@pytest.fixture
def dbt_model_definitions() -> dict[str, str]:
    """Dbt model SQL definitions for testing."""
    return {
        "staging_customers": """
            {{ config(materialized='view') }}

            SELECT
                customer_id,
                customer_name,
                customer_email,
                created_at,
                updated_at
            FROM {{ source('raw', 'customers') }}
            WHERE customer_id IS NOT NULL
        """,
        "dim_customers": """
            {{ config(
                materialized='table',
                oracle={'tablespace': 'USERS', 'parallel': 2}
            ) }}

            SELECT
                customer_id,
                customer_name,
                customer_email,
                CASE
                    WHEN customer_email LIKE '%@%.%' THEN 'valid'
                    ELSE 'invalid'
                END as email_status,
                created_at,
                updated_at,
                CURRENT_TIMESTAMP as dbt_updated_at
            FROM {{ ref('staging_customers') }}
        """,
        "fact_orders": """
            {{ config(
                materialized='incremental',
                unique_key='order_id',
                oracle={'merge_update_columns': ['order_status', 'total_amount']}
            ) }}

            SELECT
                order_id,
                customer_id,
                order_date,
                order_status,
                total_amount,
                created_at,
                updated_at
            FROM {{ source('raw', 'orders') }}

            {% if is_incremental() %}
                WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
            {% endif %}
        """,
    }


@pytest.fixture
def dbt_macro_definitions() -> dict[str, str]:
    """Dbt macro definitions for testing."""
    return {
        "oracle_create_table_as": """
            {% macro oracle_create_table_as(temporary, relation, sql) -%}
                {% if temporary %}
                    CREATE GLOBAL TEMPORARY TABLE {{ relation }}
                    ON COMMIT PRESERVE ROWS
                    AS (
                        {{ sql }}
                    )
                {% else %}
                    CREATE TABLE {{ relation }}
                    {% if config.get('oracle', {}).get('tablespace') %}
                        TABLESPACE {{ config.get('oracle', {}).get('tablespace') }}
                    {% endif %}
                    {% if config.get('oracle', {}).get('parallel') %}
                        PARALLEL {{ config.get('oracle', {}).get('parallel') }}
                    {% endif %}
                    AS (
                        {{ sql }}
                    )
                {% endif %}
            {%- endmacro %}
        """,
        "oracle_merge_sql": """
            {% macro oracle_merge_sql(target, source, unique_key, dest_columns) -%}
                MERGE INTO {{ target }} AS target_table
                USING ({{ source }}) AS source_table
                ON (target_table.{{ unique_key }} = source_table.{{ unique_key }})
                WHEN MATCHED THEN
                    UPDATE SET
                    {% for column in dest_columns %}
                        {{ column }} = source_table.{{ column }}
                        {%- if not loop.last -%},{%- endif %}
                    {% endfor %}
                WHEN NOT MATCHED THEN
                    INSERT ({{ dest_columns | join(', ') }})
                    VALUES ({{
                        dest_columns | map('prepend', 'source_table.') | join(', ')
                    }})
            {%- endmacro %}
        """,
    }


# dbt test fixtures
@pytest.fixture
def dbt_test_definitions() -> dict[str, str]:
    """Dbt test definitions for testing."""
    return {
        "test_unique_customer_id": """
            SELECT customer_id, COUNT(*)
            FROM {{ ref('dim_customers') }}
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        """,
        "test_not_null_order_id": """
            SELECT *
            FROM {{ ref('fact_orders') }}
            WHERE order_id IS NULL
        """,
        "test_valid_email_format": """
            SELECT *
            FROM {{ ref('dim_customers') }}
            WHERE email_status = 'invalid'
            AND customer_email IS NOT NULL
        """,
    }


@pytest.fixture
def dbt_source_definitions() -> dict[str, Any]:
    """Dbt source definitions for testing."""
    return {
        "version": 2,
        "sources": [
            {
                "name": "raw",
                "description": "Raw data from Oracle source system",
                "tables": [
                    {
                        "name": "customers",
                        "description": "Customer master data",
                        "columns": [
                            {
                                "name": "customer_id",
                                "description": "Unique customer identifier",
                                "tests": ["unique", "not_null"],
                            },
                            {
                                "name": "customer_name",
                                "description": "Customer full name",
                                "tests": ["not_null"],
                            },
                            {
                                "name": "customer_email",
                                "description": "Customer email address",
                            },
                        ],
                    },
                    {
                        "name": "orders",
                        "description": "Order transaction data",
                        "columns": [
                            {
                                "name": "order_id",
                                "description": "Unique order identifier",
                                "tests": ["unique", "not_null"],
                            },
                            {
                                "name": "customer_id",
                                "description": "Customer identifier",
                                "tests": ["not_null"],
                            },
                        ],
                    },
                ],
            },
        ],
    }


# Oracle SQL fixtures
@pytest.fixture
def oracle_sql_queries() -> dict[str, str]:
    """Oracle SQL queries for testing."""
    return {
        "create_test_schema": """
            CREATE USER DBT_TEST IDENTIFIED BY dbt_test_pass
            DEFAULT TABLESPACE USERS
            TEMPORARY TABLESPACE TEMP
            QUOTA UNLIMITED ON USERS
        """,
        "grant_permissions": """
            GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE PROCEDURE TO DBT_TEST
        """,
        "create_customers_table": """
            CREATE TABLE DBT_TEST.customers (
                customer_id NUMBER(10) PRIMARY KEY,
                customer_name VARCHAR2(100) NOT NULL,
                customer_email VARCHAR2(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "create_orders_table": """
            CREATE TABLE DBT_TEST.orders (
                order_id NUMBER(10) PRIMARY KEY,
                customer_id NUMBER(10) NOT NULL,
                order_date DATE NOT NULL,
                order_status VARCHAR2(20) DEFAULT 'pending',
                total_amount NUMBER(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_orders_customer
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """,
        "insert_test_data": """
            INSERT ALL
                INTO customers VALUES (1, 'John Doe', 'john@example.com',
                    SYSTIMESTAMP, SYSTIMESTAMP)
                INTO customers VALUES (2, 'Jane Smith', 'jane@example.com',
                    SYSTIMESTAMP, SYSTIMESTAMP)
                INTO orders VALUES (1, 1, SYSDATE, 'completed', 99.99,
                    SYSTIMESTAMP, SYSTIMESTAMP)
                INTO orders VALUES (2, 2, SYSDATE, 'pending', 149.99,
                    SYSTIMESTAMP, SYSTIMESTAMP)
            SELECT * FROM dual
        """,
    }


# dbt execution fixtures
@pytest.fixture
def dbt_run_config() -> dict[str, Any]:
    """Dbt run configuration for testing."""
    return {
        "threads": 4,
        "target": "default",
        "models": ["dim_customers", "fact_orders"],
        "exclude": ["staging_*"],
        "vars": {
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        },
        "full_refresh": False,
    }


@pytest.fixture
def dbt_test_config() -> dict[str, Any]:
    """Dbt test configuration for testing."""
    return {
        "threads": 2,
        "target": "default",
        "models": ["dim_customers"],
        "data": True,
        "schema": True,
        "store_failures": True,
    }


# Performance test fixtures
@pytest.fixture
def performance_test_config() -> dict[str, Any]:
    """Performance test configuration."""
    return {
        "large_table_rows": 100000,
        "concurrent_models": 5,
        "memory_threshold": "2GB",
        "execution_time_threshold": 300,  # 5 minutes
        "parallel_threads": [1, 2, 4, 8],
    }


# Error handling fixtures
@pytest.fixture
def dbt_error_scenarios() -> list[dict[str, Any]]:
    """Dbt error scenarios for testing."""
    return [
        {
            "name": "connection_failure",
            "error_type": "DatabaseConnectionError",
            "cause": "invalid_credentials",
            "expected_behavior": "fail_fast",
        },
        {
            "name": "compilation_error",
            "error_type": "CompilationError",
            "cause": "invalid_sql_syntax",
            "expected_behavior": "detailed_error_message",
        },
        {
            "name": "runtime_error",
            "error_type": "RuntimeError",
            "cause": "table_not_found",
            "expected_behavior": "graceful_failure",
        },
        {
            "name": "permission_error",
            "error_type": "DatabaseError",
            "cause": "insufficient_privileges",
            "expected_behavior": "clear_error_message",
        },
    ]


# Pytest markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "dbt: dbt-specific tests")
    config.addinivalue_line("markers", "oracle: Oracle database tests")
    config.addinivalue_line("markers", "adapter: Adapter functionality tests")
    config.addinivalue_line("markers", "materialization: Materialization tests")
    config.addinivalue_line("markers", "macro: Macro tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# Mock services
@pytest.fixture
def mock_dbt_oracle_adapter() -> object:
    """Mock dbt Oracle adapter for testing."""

    class MockDbtOracleAdapter:
        def __init__(self, config: dict[str, Any]) -> None:
            self.config = config
            self.connections: dict[str, Any] = {}
            self.compiled_models: dict[str, Any] = {}

        def open_connection(self, name: str) -> dict[str, Any]:
            """Open database connection."""
            connection = {
                "name": name,
                "state": "open",
                "handle": f"mock_handle_{name}",
                "credentials": self.config,
            }
            self.connections[name] = connection
            return connection

        def close_connection(self, name: str) -> None:
            """Close database connection."""
            if name in self.connections:
                self.connections[name]["state"] = "closed"
                del self.connections[name]

        def execute(self, sql: str, auto_begin: bool = True) -> tuple[str, list[Any]]:
            """Execute SQL statement."""
            # Mock execution results
            if "CREATE TABLE" in sql:
                return "CREATE", []
            if "INSERT" in sql:
                return "INSERT", []
            if "SELECT" in sql:
                return "SELECT", [{"column1": "value1", "column2": "value2"}]
            return "UNKNOWN", []

        def compile_model(self, model_sql: str, context: dict[str, Any]) -> str:
            """Compile dbt model SQL."""
            # Simple mock compilation
            compiled = model_sql
            for var, value in context.get("vars", {}).items():
                compiled = compiled.replace(f"{{{{ var('{var}') }}}}", str(value))

            return compiled

        def get_relation(
            self,
            database: str,
            schema: str,
            identifier: str,
        ) -> dict[str, str]:
            """Get relation information."""
            return {
                "database": database,
                "schema": schema,
                "identifier": identifier,
                "type": "table",
            }

        def list_relations_without_caching(self, schema: str) -> list[dict[str, str]]:
            """List relations in schema."""
            return [
                {"schema": schema, "identifier": "customers", "type": "table"},
                {"schema": schema, "identifier": "orders", "type": "table"},
            ]

    return MockDbtOracleAdapter


@pytest.fixture
def mock_dbt_runner() -> object:
    """Mock dbt runner for testing."""

    class MockDbtRunner:
        def __init__(self, project_dir: str, profiles_dir: str) -> None:
            self.project_dir = project_dir
            self.profiles_dir = profiles_dir
            self.results: dict[str, Any] = {}

        def run_models(self, models: list[str] | None = None) -> dict[str, Any]:
            """Run dbt models."""
            results = []
            models = models or ["dim_customers", "fact_orders"]

            for model in models:
                result = {
                    "unique_id": f"model.test.{model}",
                    "status": "success",
                    "execution_time": 2.5,
                    "rows_affected": 1000,
                }
                results.append(result)

            return {"results": results, "elapsed_time": 10.5}

        def run_tests(self, models: list[str] | None = None) -> dict[str, Any]:
            """Run dbt tests."""
            results = []
            tests = ["test_unique_customer_id", "test_not_null_order_id"]

            for test in tests:
                result = {
                    "unique_id": f"test.test.{test}",
                    "status": "pass",
                    "execution_time": 1.2,
                    "failures": 0,
                }
                results.append(result)

            return {"results": results, "elapsed_time": 5.0}

        def compile(self, models: list[str] | None = None) -> dict[str, Any]:
            """Compile dbt models."""
            compiled = {}
            models = models or ["dim_customers", "fact_orders"]

            for model in models:
                # Mock compiled SQL - not executed, just template
                compiled[model] = f"SELECT * FROM compiled_{model}"  # noqa: S608

            return {"compiled": compiled}

    return MockDbtRunner
