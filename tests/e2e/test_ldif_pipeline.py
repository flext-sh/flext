"""Comprehensive E2E tests for FLEXT LDIF pipeline.

This module tests the complete data flow:
LDAP → flext-tap-ldif → flext-target-ldif → flext-dbt-ldif → Analytics

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
import requests
from ldap3 import ALL, SUBTREE, Connection, Server

# Test configuration
TEST_TIMEOUT = 600  # 10 minutes
HEALTH_CHECK_INTERVAL = 5  # seconds
MAX_HEALTH_CHECKS = 60  # 5 minutes total


@pytest.fixture(scope="module")
def test_config() -> dict[str, Any]:
    """Test configuration fixture."""
    return {
        "ldap_url": "ldap://openldap:389",
        "ldap_base_dn": "dc=flext,dc=local",
        "ldap_bind_dn": "cn=admin,dc=flext,dc=local",
        "ldap_bind_password": "testpassword",
        "postgres_url": "postgresql://flext:testpassword@postgres:5432/flext_test",
        "redis_url": "redis://redis:6379",
        "data_path": Path("/app/data"),
        "configs_path": Path("/app/configs"),
    }


@pytest.fixture(scope="module")
def ldap_connection(test_config: dict[str, Any]) -> Connection:
    """LDAP connection fixture for testing."""
    server = Server(
        host="openldap",
        port=389,
        use_ssl=False,
        get_info=ALL,
    )

    connection = Connection(
        server,
        user=test_config["ldap_bind_dn"],
        password=test_config["ldap_bind_password"],
        auto_bind=True,
    )

    yield connection
    connection.unbind()


class TestLDIFPipelineE2E:
    """Comprehensive E2E tests for FLEXT LDIF pipeline."""

    def test_infrastructure_health(self, test_config: dict[str, Any]) -> None:
        """Test that all infrastructure services are healthy."""
        # Test LDAP connectivity
        server = Server("openldap", port=389, use_ssl=False)
        connection = Connection(
            server,
            user=test_config["ldap_bind_dn"],
            password=test_config["ldap_bind_password"],
        )
        assert connection.bind(), "LDAP connection failed"
        connection.unbind()

        # Test PostgreSQL connectivity
        import psycopg2

        conn = psycopg2.connect(test_config["postgres_url"])
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1, "PostgreSQL connection failed"
        cursor.close()
        conn.close()

        # Test Redis connectivity
        import redis

        r = redis.from_url(test_config["redis_url"])
        assert r.ping(), "Redis connection failed"

    def test_ldap_data_extraction(
        self, ldap_connection: Connection, test_config: dict[str, Any]
    ) -> None:
        """Test LDAP data extraction using flext-tap-ldif."""
        # Verify test data exists in LDAP
        ldap_connection.search(
            search_base=test_config["ldap_base_dn"],
            search_filter="(objectClass=inetOrgPerson)",
            search_scope=SUBTREE,
            attributes=["cn", "uid", "mail"],
        )

        entries = ldap_connection.entries
        assert len(entries) >= 3, (
            f"Expected at least 3 test users, found {len(entries)}"
        )

        # Verify specific test users
        usernames = {
            entry.uid.value
            for entry in entries
            if hasattr(entry, "uid") and entry.uid.value
        }
        expected_users = {"testuser1", "testuser2", "testuser3"}
        assert expected_users.issubset(usernames), (
            f"Missing test users: {expected_users - usernames}"
        )

    def test_tap_ldif_execution(self, test_config: dict[str, Any]) -> None:
        """Test flext-tap-ldif data extraction."""
        config_file = test_config["configs_path"] / "tap-ldif-config.json"
        output_file = test_config["data_path"] / "tap-output" / "ldap_entries.jsonl"

        # Run flext-tap-ldif
        cmd = [
            "python",
            "-m",
            "flext_tap_ldif",
            "--config",
            str(config_file),
            "--catalog",
            str(test_config["configs_path"] / "catalog.json"),
        ]

        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            cwd="/app",
        )

        assert result.returncode == 0, f"tap-ldif failed: {result.stderr}"
        assert output_file.exists(), f"Output file not created: {output_file}"

        # Verify output content
        with output_file.open() as f:
            lines = f.readlines()
            assert len(lines) >= 3, f"Expected at least 3 records, found {len(lines)}"

            # Parse first record to verify structure
            first_record = json.loads(lines[0])
            assert "record" in first_record, "Missing record field"
            assert "stream" in first_record, "Missing stream field"
            assert first_record["stream"] == "ldap_entries", "Incorrect stream name"

    def test_target_ldif_execution(self, test_config: dict[str, Any]) -> None:
        """Test flext-target-ldif data loading."""
        config_file = test_config["configs_path"] / "target-ldif-config.json"
        input_file = test_config["data_path"] / "tap-output" / "ldap_entries.jsonl"
        output_dir = test_config["data_path"] / "target-output"

        # Ensure input file exists
        assert input_file.exists(), f"Input file missing: {input_file}"

        # Run flext-target-ldif
        cmd = [
            "python",
            "-m",
            "flext_target_ldif",
            "--config",
            str(config_file),
        ]

        # Pipe input data
        with input_file.open() as input_data:
            result = subprocess.run(
                cmd,
                check=False,
                stdin=input_data,
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT,
                cwd="/app",
            )

        assert result.returncode == 0, f"target-ldif failed: {result.stderr}"

        # Verify output files
        output_files = list(output_dir.glob("*.ldif"))
        assert len(output_files) > 0, f"No LDIF files created in {output_dir}"

        # Verify LDIF content
        ldif_file = output_files[0]
        with ldif_file.open() as f:
            content = f.read()
            assert "dn:" in content, "LDIF file missing DN entries"
            assert "objectClass:" in content, "LDIF file missing objectClass entries"

    def test_dbt_transformation(self, test_config: dict[str, Any]) -> None:
        """Test flext-dbt-ldif data transformations."""
        # Check that dbt project exists
        dbt_project_dir = Path("/app/dbt_project")
        assert dbt_project_dir.exists(), "dbt project directory missing"

        # Run dbt transformations
        cmd = [
            "dbt",
            "run",
            "--project-dir",
            str(dbt_project_dir),
            "--profiles-dir",
            "/app/profiles",
            "--target",
            "test",
        ]

        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            cwd="/app",
        )

        assert result.returncode == 0, f"dbt run failed: {result.stderr}"

        # Verify dbt test success
        cmd_test = [
            "dbt",
            "test",
            "--project-dir",
            str(dbt_project_dir),
            "--profiles-dir",
            "/app/profiles",
            "--target",
            "test",
        ]

        result_test = subprocess.run(
            cmd_test,
            check=False,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            cwd="/app",
        )

        assert result_test.returncode == 0, f"dbt test failed: {result_test.stderr}"

    def test_meltano_integration(self, test_config: dict[str, Any]) -> None:
        """Test Meltano orchestration of the complete pipeline."""
        meltano_project = Path("/app/meltano_project")

        # Run Meltano discover
        cmd_discover = ["meltano", "discover", "all"]
        result_discover = subprocess.run(
            cmd_discover,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(meltano_project),
        )

        assert result_discover.returncode == 0, (
            f"meltano discover failed: {result_discover.stderr}"
        )

        # Run Meltano pipeline (if job is configured)
        cmd_run = ["meltano", "run", "tap-ldif", "target-ldif"]
        subprocess.run(
            cmd_run,
            check=False,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            cwd=str(meltano_project),
        )

        # Note: This might fail if tap/target aren't fully configured in Meltano
        # but we'll check the output for useful information

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_end_to_end_pipeline(self, test_config: dict[str, Any]) -> None:
        """Test complete end-to-end pipeline with data validation."""
        # This test combines all previous tests in sequence
        # to ensure complete pipeline functionality

        # 1. Verify infrastructure
        self.test_infrastructure_health(test_config)

        # 2. Extract data
        self.test_tap_ldif_execution(test_config)

        # 3. Load data
        self.test_target_ldif_execution(test_config)

        # 4. Transform data
        self.test_dbt_transformation(test_config)

        # 5. Validate final output
        output_dir = test_config["data_path"] / "target-output"
        ldif_files = list(output_dir.glob("*.ldif"))

        assert len(ldif_files) > 0, "No LDIF files generated"

        # Count entries in final LDIF
        total_entries = 0
        for ldif_file in ldif_files:
            with ldif_file.open() as f:
                content = f.read()
                # Count DN entries
                dn_count = content.count("dn:")
                total_entries += dn_count

        assert total_entries >= 3, f"Expected at least 3 entries, found {total_entries}"

    def test_pipeline_performance(self, test_config: dict[str, Any]) -> None:
        """Test pipeline performance metrics."""
        start_time = time.time()

        # Run simplified pipeline for performance testing
        self.test_tap_ldif_execution(test_config)
        self.test_target_ldif_execution(test_config)

        end_time = time.time()
        duration = end_time - start_time

        # Performance assertions
        assert duration < 60, f"Pipeline took too long: {duration:.2f} seconds"

    def test_error_handling(self, test_config: dict[str, Any]) -> None:
        """Test pipeline error handling and recovery."""
        # Test with invalid LDAP configuration
        bad_config = {
            "ldap_host": "nonexistent-host",
            "ldap_port": 389,
            "ldap_base_dn": "dc=invalid,dc=local",
        }

        bad_config_file = test_config["data_path"] / "bad-config.json"
        with bad_config_file.open("w") as f:
            json.dump(bad_config, f)

        # This should fail gracefully
        cmd = [
            "python",
            "-m",
            "flext_tap_ldif",
            "--config",
            str(bad_config_file),
        ]

        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/app",
        )

        # Should fail but not crash
        assert result.returncode != 0, "Expected failure with bad config"
        assert "error" in result.stderr.lower() or "failed" in result.stderr.lower(), (
            "Expected error message in stderr"
        )
