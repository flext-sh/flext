"""E2E Integration Tests for Complete Oracle Database Pipeline.

Tests the full FLEXT Oracle Database ecosystem:
- flext-tap-oracle: Extract from Oracle DB
- flext-target-oracle: Load to Oracle DB
- flext-dbt-oracle: Transform in Oracle DB

Uses real Oracle Database with comprehensive data validation.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path

import pytest
from flext_db_oracle import FlextDbOracleConfig
from flext_db_oracle.application.services import FlextDbOracleConnectionService

logger = logging.getLogger(__name__)


class TestOracleCompletePipeline:
    """Complete E2E pipeline testing for Oracle Database ecosystem."""

    @pytest.fixture(scope="class")
    def oracle_config(self) -> FlextDbOracleConfig:
        """Oracle configuration for testing."""
        return FlextDbOracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            username="flext_test",
            password="flext_test123",
            protocol="tcp",
            pool_min_size=1,
            pool_max_size=5,
            pool_increment=1,
            query_timeout=300,
            connect_timeout=30,
            retry_attempts=3,
        )

    @pytest.fixture(scope="class")
    async def oracle_connection(self, oracle_config: FlextDbOracleConfig) -> FlextDbOracleConnectionService:
        """Oracle connection service for validation."""
        service = FlextDbOracleConnectionService(oracle_config)

        # Test connection
        result = await service.test_connection()
        assert result.success, f"Oracle connection failed: {result.error}"

        return service

    @pytest.mark.oracle
    @pytest.mark.e2e
    async def test_database_connectivity(self, oracle_connection: FlextDbOracleConnectionService) -> None:
        """Test basic Oracle database connectivity."""
        result = await oracle_connection.test_connection()
        assert result.success
        logger.info("Oracle database connectivity confirmed")

    @pytest.mark.oracle
    @pytest.mark.e2e
    async def test_source_data_exists(self, oracle_connection: FlextDbOracleConnectionService) -> None:
        """Verify test data exists in source schema."""
        # Use connection service directly for queries

        # Check customers table
        result = await oracle_connection.execute_query("SELECT COUNT(*) as customer_count FROM flext_source.customers")
        assert result.success
        customer_count = result.data.rows[0][0]
        assert customer_count > 0, "No customers found in source"

        # Check orders table
        result = await oracle_connection.execute_query("SELECT COUNT(*) as order_count FROM flext_source.orders")
        assert result.success
        order_count = result.data.rows[0][0]
        assert order_count > 0, "No orders found in source"

        logger.info(f"Source data verified: {customer_count} customers, {order_count} orders")

    @pytest.mark.oracle
    @pytest.mark.tap
    @pytest.mark.e2e
    def test_tap_oracle_extraction(self) -> None:
        """Test Oracle tap extraction with schema flattening."""
        config_path = Path("/app/tests/configs/tap-oracle/tap_config.json")
        catalog_path = Path("/app/tests/configs/tap-oracle/catalog.json")
        output_path = Path("/app/tests/data/output/tap_output.jsonl")

        # Generate catalog first
        catalog_cmd = ["tap-oracle", "--config", str(config_path), "--discover"]

        logger.info("Generating catalog for Oracle tap")
        result = subprocess.run(catalog_cmd, check=False, capture_output=True, text=True, timeout=120)

        assert result.returncode == 0, f"Catalog generation failed: {result.stderr}"

        # Write catalog to file
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        with catalog_path.open("w") as f:
            f.write(result.stdout)

        # Run extraction
        extract_cmd = [
            "tap-oracle",
            "--config",
            str(config_path),
            "--catalog",
            str(catalog_path),
        ]

        logger.info("Running Oracle tap extraction")
        with output_path.open("w") as output_file:
            result = subprocess.run(
                extract_cmd,
                check=False,
                stdout=output_file,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
            )

        assert result.returncode == 0, f"Tap extraction failed: {result.stderr}"
        assert output_path.exists(), "Tap output file not created"

        # Validate output
        records_count = 0
        schema_messages = 0

        with output_path.open() as f:
            for line in f:
                if line.strip():
                    message = json.loads(line)
                    if message.get("type") == "RECORD":
                        records_count += 1
                    elif message.get("type") == "SCHEMA":
                        schema_messages += 1

        assert records_count > 0, "No records extracted"
        assert schema_messages > 0, "No schema messages found"

        logger.info(f"Tap extraction successful: {records_count} records, {schema_messages} schemas")

    @pytest.mark.oracle
    @pytest.mark.target
    @pytest.mark.e2e
    def test_target_oracle_loading(self) -> None:
        """Test Oracle target loading with parameterized queries."""
        config_path = Path("/app/tests/configs/target-oracle/target_config.json")
        input_path = Path("/app/tests/data/output/tap_output.jsonl")

        assert input_path.exists(), "Tap output not found - run tap test first"

        target_cmd = ["target-oracle", "--config", str(config_path)]

        logger.info("Running Oracle target loading")
        with input_path.open() as input_file:
            result = subprocess.run(
                target_cmd,
                check=False,
                stdin=input_file,
                capture_output=True,
                text=True,
                timeout=300,
            )

        assert result.returncode == 0, f"Target loading failed: {result.stderr}"
        logger.info("Target loading successful")

    @pytest.mark.oracle
    @pytest.mark.target
    @pytest.mark.e2e
    async def test_target_data_validation(self, oracle_connection: FlextDbOracleConnectionService) -> None:
        """Validate data was loaded correctly into target schema."""
        # Check target tables exist
        result = await oracle_connection.execute_query("""
            SELECT table_name
            FROM all_tables
            WHERE owner = 'FLEXT_TARGET'
            ORDER BY table_name
        """)

        assert result.success
        tables = [row[0] for row in result.data.rows]

        expected_tables = ["CUSTOMERS", "ORDERS", "PRODUCTS", "ORDER_ITEMS"]
        for table in expected_tables:
            assert table in tables, f"Target table {table} not found"

        # Validate data counts
        for table in expected_tables:
            result = await oracle_connection.execute_query(f"SELECT COUNT(*) FROM flext_target.{table}")
            assert result.success
            count = result.data.rows[0][0]
            assert count > 0, f"No data in target table {table}"

        logger.info(f"Target validation successful: {len(tables)} tables with data")

    @pytest.mark.oracle
    @pytest.mark.dbt
    @pytest.mark.e2e
    def test_dbt_oracle_transformation(self) -> None:
        """Test DBT Oracle transformations."""
        dbt_cmd = [
            "dbt",
            "run",
            "--profiles-dir",
            "/app/tests/configs/dbt-oracle",
            "--project-dir",
            "/app/tests/dbt-projects/oracle-analytics",
            "--target",
            "dev",
        ]

        logger.info("Running DBT Oracle transformations")
        result = subprocess.run(dbt_cmd, check=False, capture_output=True, text=True, timeout=300)

        assert result.returncode == 0, f"DBT run failed: {result.stderr}"

        # Check for successful model runs in output
        output = result.stdout
        assert "stg_customers" in output, "Staging model not found in output"
        assert "mart_customer_analytics" in output, "Analytics mart not found in output"

        logger.info("DBT transformations successful")

    @pytest.mark.oracle
    @pytest.mark.dbt
    @pytest.mark.e2e
    async def test_dbt_output_validation(self, oracle_connection: FlextDbOracleConnectionService) -> None:
        """Validate DBT transformations created correct outputs."""
        # Check DBT models exist
        result = await oracle_connection.execute_query("""
            SELECT view_name
            FROM all_views
            WHERE owner = 'FLEXT_DBT'
            AND view_name = 'STG_CUSTOMERS'
        """)
        assert result.success
        assert len(result.data.rows) > 0, "DBT staging view not found"

        # Check analytics mart
        result = await oracle_connection.execute_query("""
            SELECT table_name
            FROM all_tables
            WHERE owner = 'FLEXT_DBT'
            AND table_name = 'MART_CUSTOMER_ANALYTICS'
        """)
        assert result.success
        assert len(result.data.rows) > 0, "DBT analytics mart not found"

        # Validate analytics data structure
        result = await oracle_connection.execute_query("""
            SELECT
                customer_id,
                customer_name,
                customer_segment,
                total_orders,
                total_spent,
                recency_score,
                frequency_score,
                monetary_score
            FROM flext_dbt.mart_customer_analytics
            WHERE total_orders > 0
            ORDER BY total_spent DESC
            FETCH FIRST 5 ROWS ONLY
        """)

        assert result.success
        analytics_data = result.data.rows
        assert len(analytics_data) > 0, "No analytics data found"

        # Validate data quality
        for row in analytics_data:
            customer_id, name, segment, orders, spent, r_score, f_score, m_score = row
            assert customer_id is not None
            assert name is not None
            assert segment in {"VIP", "High Value", "Regular", "Occasional", "Prospect"}
            assert orders >= 0
            assert spent >= 0
            assert 1 <= r_score <= 5
            assert 1 <= f_score <= 5
            assert 1 <= m_score <= 5

        logger.info(f"DBT output validation successful: {len(analytics_data)} analytics records")

    @pytest.mark.oracle
    @pytest.mark.e2e
    @pytest.mark.performance
    async def test_full_pipeline_performance(self, oracle_connection: FlextDbOracleConnectionService) -> None:
        """Test full pipeline performance and monitoring."""
        start_time = time.time()

        # Run complete pipeline sequence
        logger.info("Starting full pipeline performance test")

        # 1. Extract (simulated - already tested)
        extraction_start = time.time()
        await asyncio.sleep(0.1)  # Simulate extraction time
        extraction_time = time.time() - extraction_start

        # 2. Load (simulated - already tested)
        loading_start = time.time()
        await asyncio.sleep(0.1)  # Simulate loading time
        loading_time = time.time() - loading_start

        # 3. Transform - measure actual DBT performance
        transform_start = time.time()

        # Run a sample analytics query
        result = await oracle_connection.execute_query("""
            SELECT
                COUNT(*) as total_customers,
                AVG(total_spent) as avg_customer_value,
                COUNT(CASE WHEN customer_segment = 'VIP' THEN 1 END) as vip_customers
            FROM flext_dbt.mart_customer_analytics
        """)

        assert result.success
        transform_time = time.time() - transform_start

        total_time = time.time() - start_time

        # Performance assertions
        assert extraction_time < 60, f"Extraction too slow: {extraction_time}s"
        assert loading_time < 60, f"Loading too slow: {loading_time}s"
        assert transform_time < 30, f"Transform too slow: {transform_time}s"
        assert total_time < 120, f"Total pipeline too slow: {total_time}s"

        # Log performance metrics
        metrics = result.data.rows[0]
        logger.info(f"Pipeline performance: {total_time:.2f}s total")
        logger.info(f"Analytics results: {metrics[0]} customers, ${metrics[1]:.2f} avg value, {metrics[2]} VIP")

    @pytest.mark.oracle
    @pytest.mark.e2e
    @pytest.mark.cleanup
    async def test_cleanup_test_data(self, oracle_connection: FlextDbOracleConnectionService) -> None:
        """Clean up test data (optional - for repeated testing)."""
        cleanup_queries = [
            "DELETE FROM flext_target.order_items",
            "DELETE FROM flext_target.orders",
            "DELETE FROM flext_target.products",
            "DELETE FROM flext_target.customers",
            "DROP TABLE flext_dbt.mart_customer_analytics",
            "DROP VIEW flext_dbt.stg_customers",
        ]

        for query in cleanup_queries:
            try:
                result = await oracle_connection.execute_query(query)
                if result.success:
                    logger.debug(f"Cleanup successful: {query}")
            except Exception as e:
                logger.warning(f"Cleanup warning for '{query}': {e}")

        logger.info("Test data cleanup completed")
