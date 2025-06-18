"""Professional test utilities for tap-oic.

This module provides utility functions and helpers for testing following
enterprise testing best practices.
"""

import json
import time
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Never

import pytest
import requests


class TestDataBuilder:
    """Builder pattern for creating test data consistently."""

    @staticmethod
    def integration_record(
        id: str = "TEST_INTEGRATION_001",
        name: str = "Test Integration",
        status: str = "ACTIVE",
        time_updated: str = "2024-01-15T10:30:00Z",
        **kwargs,
    ) -> dict[str, Any]:
        """Build a standard integration record."""
        record = {
            "id": id,
            "name": name,
            "status": status,
            "timeUpdated": time_updated,
            "description": f"Test integration: {name}",
            "version": "1.0.0",
            "identifier": id.lower(),
        }
        record.update(kwargs)
        return record

    @staticmethod
    def connection_record(
        id: str = "TEST_CONNECTION_001",
        name: str = "Test Connection",
        status: str = "ACTIVE",
        time_updated: str = "2024-01-15T10:30:00Z",
        connection_type: str = "REST",
        **kwargs,
    ) -> dict[str, Any]:
        """Build a standard connection record."""
        record = {
            "id": id,
            "name": name,
            "status": status,
            "timeUpdated": time_updated,
            "connectionType": connection_type,
            "description": f"Test connection: {name}",
            "identifier": id.lower(),
        }
        record.update(kwargs)
        return record

    @staticmethod
    def package_record(
        id: str = "TEST_PACKAGE_001",
        name: str = "Test Package",
        status: str = "ACTIVE",
        time_updated: str = "2024-01-15T10:30:00Z",
        version: str = "1.0.0",
        **kwargs,
    ) -> dict[str, Any]:
        """Build a standard package record."""
        record = {
            "id": id,
            "name": name,
            "status": status,
            "timeUpdated": time_updated,
            "version": version,
            "description": f"Test package: {name}",
            "identifier": id.lower(),
        }
        record.update(kwargs)
        return record

    @staticmethod
    def monitoring_record(
        instance_id: str = "TEST_INSTANCE_001",
        integration_id: str = "TEST_INTEGRATION_001",
        status: str = "SUCCEEDED",
        start_time: str = "2024-01-15T10:30:00Z",
        end_time: str = "2024-01-15T10:35:00Z",
        **kwargs,
    ) -> dict[str, Any]:
        """Build a monitoring instance record."""
        record = {
            "instanceId": instance_id,
            "integrationId": integration_id,
            "status": status,
            "startTime": start_time,
            "endTime": end_time,
            "duration": 300000,  # 5 minutes in milliseconds
            "recordsProcessed": 100,
        }
        record.update(kwargs)
        return record

    @staticmethod
    def singer_record(
        stream: str,
        record_data: dict[str, Any],
        time_extracted: str | None = None,
    ) -> dict[str, Any]:
        """Build a Singer protocol record."""
        if time_extracted is None:
            time_extracted = "2024-01-15T10:35:00Z"

        return {
            "type": "RECORD",
            "stream": stream,
            "record": record_data,
            "time_extracted": time_extracted,
        }

    @staticmethod
    def singer_schema(
        stream: str,
        properties: dict[str, Any],
        key_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build a Singer protocol schema."""
        if key_properties is None:
            key_properties = ["id"]

        return {
            "type": "SCHEMA",
            "stream": stream,
            "schema": {
                "type": "object",
                "properties": properties,
            },
            "key_properties": key_properties,
        }


class TestValidator:
    """Validator utilities for test assertions."""

    @staticmethod
    def validate_tap_instance(tap_instance) -> None:
        """Validate that a TAP instance is properly configured."""
        assert hasattr(tap_instance, "name")
        assert hasattr(tap_instance, "config")
        assert hasattr(tap_instance, "catalog")
        assert hasattr(tap_instance, "discover_streams")
        assert tap_instance.name == "tap-oic"

    @staticmethod
    def validate_stream_schema(stream) -> None:
        """Validate that a stream has a proper schema."""
        assert hasattr(stream, "schema")
        assert stream.schema is not None
        assert isinstance(stream.schema, dict)
        assert "type" in stream.schema
        assert stream.schema["type"] == "object"
        assert "properties" in stream.schema
        assert len(stream.schema["properties"]) > 0

    @staticmethod
    def validate_stream_metadata(stream) -> None:
        """Validate stream metadata requirements."""
        assert hasattr(stream, "primary_keys")
        assert stream.primary_keys is not None
        assert len(stream.primary_keys) > 0

        # Ensure primary keys exist in schema
        properties = stream.schema.get("properties", {})
        for key in stream.primary_keys:
            assert key in properties, f"Primary key {key} missing from schema"

    @staticmethod
    def validate_singer_record(record: dict[str, Any]) -> None:
        """Validate Singer protocol record format."""
        assert "type" in record
        assert record["type"] == "RECORD"
        assert "stream" in record
        assert "record" in record
        assert "time_extracted" in record
        assert isinstance(record["record"], dict)

    @staticmethod
    def validate_config_schema(config_schema: dict[str, Any]) -> None:
        """Validate configuration schema structure."""
        assert "properties" in config_schema
        properties = config_schema["properties"]

        # Required fields
        required_fields = ["base_url", "auth_method"]
        for field in required_fields:
            assert field in properties, f"Required field {field} missing"

        # OAuth2 fields
        oauth2_fields = ["oauth_client_id", "oauth_client_secret", "oauth_token_url"]
        for field in oauth2_fields:
            assert field in properties, f"OAuth2 field {field} missing"

    @staticmethod
    def validate_performance_metrics(
        metrics: dict[str, Any],
        max_duration: float = 5.0,
        max_memory_growth: int = 100 * 1024 * 1024,  # 100MB
    ) -> None:
        """Validate performance metrics are within acceptable bounds."""
        if "duration" in metrics:
            assert (
                metrics["duration"] < max_duration
            ), f"Duration {metrics['duration']} exceeds {max_duration}s"

        if "memory_growth" in metrics:
            assert (
                metrics["memory_growth"] < max_memory_growth
            ), f"Memory growth {metrics['memory_growth']} exceeds {max_memory_growth} bytes"


class MockAPIServer:
    """Mock API server for testing HTTP interactions."""

    def __init__(self) -> None:
        self.requests_mock = None
        self.base_url = "https://test-oic.integration.ocp.oraclecloud.com"
        self.token_url = "https://test-idcs.identity.oraclecloud.com/oauth2/v1/token"

    def setup_oauth2_mock(self, token: str = "mock-token-12345") -> None:
        """Setup OAuth2 token endpoint mock."""
        if self.requests_mock:
            self.requests_mock.post(
                self.token_url,
                json={
                    "access_token": token,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": "urn:opc:resource:consumer::all",
                },
                status_code=200,
            )

    def setup_integrations_mock(
        self, records: list[dict[str, Any]] | None = None
    ) -> None:
        """Setup integrations endpoint mock."""
        if records is None:
            records = [TestDataBuilder.integration_record()]

        if self.requests_mock:
            self.requests_mock.get(
                f"{self.base_url}/ic/api/integration/v1/integrations",
                json={"items": records},
                status_code=200,
            )

    def setup_connections_mock(
        self, records: list[dict[str, Any]] | None = None
    ) -> None:
        """Setup connections endpoint mock."""
        if records is None:
            records = [TestDataBuilder.connection_record()]

        if self.requests_mock:
            self.requests_mock.get(
                f"{self.base_url}/ic/api/integration/v1/connections",
                json={"items": records},
                status_code=200,
            )

    def setup_error_response(
        self,
        endpoint: str,
        status_code: int = 500,
        error_message: str = "Internal Server Error",
    ) -> None:
        """Setup error response for testing error handling."""
        if self.requests_mock:
            self.requests_mock.get(
                f"{self.base_url}{endpoint}",
                json={"error": error_message},
                status_code=status_code,
            )

    @contextmanager
    def mock_context(self, requests_mock_instance):
        """Context manager for using the mock server."""
        self.requests_mock = requests_mock_instance
        try:
            yield self
        finally:
            self.requests_mock = None


class PerformanceMeasurer:
    """Utility for measuring performance metrics."""

    def __init__(self) -> None:
        self.start_time = None
        self.end_time = None
        self.measurements = []

    @contextmanager
    def measure_duration(self) -> Generator[dict[str, Any]]:
        """Measure execution duration."""
        self.start_time = time.time()
        metrics = {"start_time": self.start_time}

        try:
            yield metrics
        finally:
            self.end_time = time.time()
            metrics["end_time"] = self.end_time
            metrics["duration"] = self.end_time - self.start_time
            self.measurements.append(metrics)

    def get_average_duration(self) -> float:
        """Get average duration from measurements."""
        if not self.measurements:
            return 0.0
        return sum(m["duration"] for m in self.measurements) / len(self.measurements)

    def get_max_duration(self) -> float:
        """Get maximum duration from measurements."""
        if not self.measurements:
            return 0.0
        return max(m["duration"] for m in self.measurements)


class TestConfigGenerator:
    """Generate test configurations for various scenarios."""

    @staticmethod
    def minimal_oauth2_config() -> dict[str, Any]:
        """Generate minimal OAuth2 configuration."""
        return {
            "base_url": "https://test-oic.integration.ocp.oraclecloud.com",
            "auth_method": "oauth2",
            "oauth_client_id": "test-client",
            "oauth_client_secret": "test-secret",
            "oauth_token_url": "https://test-idcs.identity.oraclecloud.com/oauth2/v1/token",
        }

    @staticmethod
    def full_oauth2_config() -> dict[str, Any]:
        """Generate full OAuth2 configuration with all options."""
        return {
            "base_url": "https://test-oic.integration.ocp.oraclecloud.com",
            "auth_method": "oauth2",
            "oauth_client_id": "test-client-id",
            "oauth_client_secret": "test-client-secret",
            "oauth_token_url": "https://test-idcs.identity.oraclecloud.com/oauth2/v1/token",
            "oauth_client_aud": "https://test-oic.integration.ocp.oraclecloud.com",
            "oauth_scope": "urn:opc:resource:consumer::all",
            "request_timeout": 30,
            "max_retries": 3,
            "page_size": 100,
            "include_inactive": True,
            "include_monitoring": True,
            "include_extended": True,
        }

    @staticmethod
    def production_oauth2_config() -> dict[str, Any]:
        """Generate production-like OAuth2 configuration."""
        return {
            "base_url": "https://production-oic.integration.ocp.oraclecloud.com",
            "auth_method": "oauth2",
            "oauth_client_id": "prod-client-id",
            "oauth_client_secret": "prod-client-secret",
            "oauth_token_url": "https://production-idcs.identity.oraclecloud.com/oauth2/v1/token",
            "oauth_client_aud": "https://production-oic.integration.ocp.oraclecloud.com",
            "oauth_scope": "urn:opc:resource:consumer::all",
            "request_timeout": 60,
            "max_retries": 3,
            "page_size": 500,
            "include_monitoring": True,
            "include_extended": True,
        }

    @staticmethod
    def invalid_configs() -> list[dict[str, Any]]:
        """Generate various invalid configurations for error testing."""
        return [
            # Empty base URL
            {
                "base_url": "",
                "auth_method": "oauth2",
                "oauth_client_id": "test",
                "oauth_client_secret": "test",
                "oauth_token_url": "https://test.com/token",
            },
            # Invalid auth method
            {
                "base_url": "https://test.com",
                "auth_method": "invalid_method",
                "oauth_client_id": "test",
                "oauth_client_secret": "test",
                "oauth_token_url": "https://test.com/token",
            },
            # Missing required OAuth2 fields
            {
                "base_url": "https://test.com",
                "auth_method": "oauth2",
            },
            # Invalid OAuth2 scope
            {
                "base_url": "https://test.com",
                "auth_method": "oauth2",
                "oauth_client_id": "test",
                "oauth_client_secret": "test",
                "oauth_token_url": "https://test.com/token",
                "oauth_scope": "invalid_scope",
            },
        ]


class TestFileManager:
    """Manage test files and temporary data."""

    def __init__(self, temp_dir: Path) -> None:
        self.temp_dir = temp_dir
        self.created_files = []

    def create_config_file(
        self, config: dict[str, Any], filename: str = "test_config.json"
    ) -> Path:
        """Create a temporary configuration file."""
        config_path = self.temp_dir / filename
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        self.created_files.append(config_path)
        return config_path

    def create_catalog_file(
        self, catalog: dict[str, Any], filename: str = "test_catalog.json"
    ) -> Path:
        """Create a temporary catalog file."""
        catalog_path = self.temp_dir / filename
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2)
        self.created_files.append(catalog_path)
        return catalog_path

    def create_records_file(
        self, records: list[dict[str, Any]], filename: str = "test_records.jsonl"
    ) -> Path:
        """Create a temporary JSONL records file."""
        records_path = self.temp_dir / filename
        with open(records_path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        self.created_files.append(records_path)
        return records_path

    def cleanup(self) -> None:
        """Clean up created files."""
        for file_path in self.created_files:
            if file_path.exists():
                file_path.unlink()
        self.created_files.clear()


def skip_if_no_internet() -> None:
    """Skip test if no internet connection available."""
    try:
        requests.get("https://www.google.com", timeout=5)
    except requests.RequestException:
        pytest.skip("No internet connection available")


def skip_if_no_production_config() -> None:
    """Skip test if production configuration is not available."""
    import os

    required_vars = ["OIC_BASE_URL", "OIC_CLIENT_ID", "OIC_CLIENT_SECRET"]
    if not all(os.getenv(var) for var in required_vars):
        pytest.skip("Production configuration not available")


def requires_python_version(min_version: str):
    """Decorator to skip tests if Python version requirement not met."""
    import sys

    from packaging import version

    def decorator(func):
        if version.parse(
            f"{sys.version_info.major}.{sys.version_info.minor}"
        ) < version.parse(min_version):
            return pytest.mark.skip(f"Requires Python {min_version} or higher")(func)
        return func

    return decorator


@contextmanager
def timeout_test(seconds: float):
    """Context manager to timeout a test after specified seconds."""
    import signal

    def timeout_handler(signum, frame) -> Never:
        msg = f"Test timed out after {seconds} seconds"
        raise TimeoutError(msg)

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(seconds))

    try:
        yield
    finally:
        signal.alarm(0)


class ConcurrentTestRunner:
    """Utility for running tests concurrently."""

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers
        self.results = []

    def run_tests_parallel(self, test_functions: list[callable]) -> list[Any]:
        """Run multiple test functions in parallel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        self.results.clear()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {
                executor.submit(test_func): test_func for test_func in test_functions
            }

            for future in as_completed(future_to_test):
                test_func = future_to_test[future]
                try:
                    result = future.result()
                    self.results.append(
                        {"test": test_func.__name__, "result": result, "success": True}
                    )
                except Exception as e:
                    self.results.append(
                        {"test": test_func.__name__, "error": str(e), "success": False}
                    )

        return self.results

    def get_success_rate(self) -> float:
        """Get success rate of parallel tests."""
        if not self.results:
            return 0.0
        successful = sum(1 for r in self.results if r["success"])
        return successful / len(self.results)


def assert_config_valid(config: dict[str, Any]) -> None:
    """Assert that a configuration is valid for tap-oic."""
    assert "base_url" in config, "base_url is required"
    assert "auth_method" in config, "auth_method is required"
    assert config["auth_method"] == "oauth2", "OIC only supports oauth2 authentication"

    if config["auth_method"] == "oauth2":
        oauth2_required = ["oauth_client_id", "oauth_client_secret", "oauth_token_url"]
        for field in oauth2_required:
            assert field in config, f"OAuth2 field {field} is required"
    else:
        msg = (
            f"Invalid auth_method: {config['auth_method']}. OIC only supports 'oauth2'"
        )
        raise ValueError(msg)


def assert_stream_quality(stream) -> None:
    """Assert that a stream meets quality requirements."""
    TestValidator.validate_stream_schema(stream)
    TestValidator.validate_stream_metadata(stream)

    # Additional quality checks
    assert hasattr(stream, "name")
    assert isinstance(stream.name, str)
    assert len(stream.name) > 0

    # Check for required schema fields
    properties = stream.schema.get("properties", {})
    assert "id" in properties, "Stream schema must have 'id' field"

    # Validate primary keys are meaningful
    for key in stream.primary_keys:
        assert key in properties, f"Primary key {key} must exist in schema"
        assert properties[key].get("type") in {
            "string",
            "integer",
        }, f"Primary key {key} must be string or integer"
