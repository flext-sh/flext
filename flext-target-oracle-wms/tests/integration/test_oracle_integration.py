"""Integration tests for Oracle WMS target."""

import json

import pytest
from testcontainers.oracle import OracleDbContainer

from flext_target_oracle_wms.target import TargetOracleWMS


@pytest.mark.integration
@pytest.mark.oracle
class TestOracleIntegration:
    """Integration tests requiring Oracle database."""

    @pytest.fixture(scope="class")
    def oracle_container(self):
        """Start Oracle container for integration tests."""
        with OracleDbContainer("gvenzl/oracle-xe:21-slim") as container:
            yield container

    @pytest.fixture
    def oracle_config(self, oracle_container):
        """Oracle configuration from test container."""
        return {
            "host": oracle_container.get_container_host_ip(),
            "port": oracle_container.get_exposed_port(1521),
            "service_name": "XEPDB1",
            "user": "system",
            "password": oracle_container.password,
            "schema": "SYSTEM",
            "batch_size": 100,
            "add_record_metadata": True,
        }

    def test_target_connection(self, oracle_config) -> None:
        """Test target can connect to Oracle database."""
        target = TargetOracleWMS(config=oracle_config, validate_config=False)

        # Test engine creation
        engine = target.engine
        assert engine is not None

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(sa.text("SELECT 1 FROM DUAL"))
            assert result.fetchone()[0] == 1

    def test_sink_table_creation(self, oracle_config) -> None:
        """Test sink can create tables in Oracle."""
        target = TargetOracleWMS(config=oracle_config, validate_config=False)

        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "maxLength": 100},
                "created_at": {"type": "string", "format": "date-time"},
                "is_active": {"type": "boolean"},
            },
        }

        sink = target.get_sink(
            stream_name="test_users",
            schema=schema,
            key_properties=["id"],
        )

        # Test table creation with sample records
        records = [
            {
                "id": 1,
                "name": "John Doe",
                "created_at": "2023-01-01T12:00:00Z",
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "created_at": "2023-01-02T12:00:00Z",
                "is_active": False,
            },
        ]

        sink.create_table_with_records(
            full_table_name="SYSTEM.TEST_USERS",
            schema=schema,
            records=records,
        )

        # Verify table exists and has data
        with target.engine.connect() as conn:
            result = conn.execute(sa.text("SELECT COUNT(*) FROM SYSTEM.TEST_USERS"))
            count = result.fetchone()[0]
            assert count == 2

            # Verify data content
            result = conn.execute(sa.text("SELECT ID, NAME, IS_ACTIVE FROM SYSTEM.TEST_USERS ORDER BY ID"))
            rows = result.fetchall()

            assert rows[0] == (1, "John Doe", "Y")
            assert rows[1] == (2, "Jane Smith", "N")

    def test_batch_processing(self, oracle_config) -> None:
        """Test batch processing with multiple records."""
        target = TargetOracleWMS(config=oracle_config, validate_config=False)

        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "value": {"type": "string"},
            },
        }

        sink = target.get_sink(
            stream_name="test_batch",
            schema=schema,
            key_properties=["id"],
        )

        # Create large batch of records
        records = [
            {"id": i, "value": f"value_{i}"}
            for i in range(250)  # Test batch processing
        ]

        sink.create_table_with_records(
            full_table_name="SYSTEM.TEST_BATCH",
            schema=schema,
            records=records,
        )

        # Verify all records were inserted
        with target.engine.connect() as conn:
            result = conn.execute(sa.text("SELECT COUNT(*) FROM SYSTEM.TEST_BATCH"))
            count = result.fetchone()[0]
            assert count == 250

    @pytest.mark.slow
    def test_complex_data_types(self, oracle_config) -> None:
        """Test handling of complex data types."""
        target = TargetOracleWMS(config=oracle_config, validate_config=False)

        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "metadata": {"type": "object"},
                "tags": {"type": "array"},
                "config": {"type": "object"},
                "created_at": {"type": "string", "format": "date-time"},
                "price": {"type": "number"},
            },
        }

        sink = target.get_sink(
            stream_name="test_complex",
            schema=schema,
            key_properties=["id"],
        )

        records = [
            {
                "id": 1,
                "metadata": {"source": "api", "version": "1.0"},
                "tags": ["important", "customer"],
                "config": {"timeout": 30, "retries": 3},
                "created_at": "2023-01-01T12:00:00Z",
                "price": 29.99,
            },
        ]

        sink.create_table_with_records(
            full_table_name="SYSTEM.TEST_COMPLEX",
            schema=schema,
            records=records,
        )

        # Verify complex data is stored as JSON
        with target.engine.connect() as conn:
            result = conn.execute(sa.text("SELECT METADATA, TAGS FROM SYSTEM.TEST_COMPLEX WHERE ID = 1"))
            row = result.fetchone()

            metadata = json.loads(row[0])
            tags = json.loads(row[1])

            assert metadata == {"source": "api", "version": "1.0"}
            assert tags == ["important", "customer"]
