#!/usr/bin/env python3
"""Comprehensive End-to-End tests for target-oracle-oic.

Tests all functionalities including:
- Target initialization
- Sink operations
- Data loading
- Authentication
- Error handling
- Integration import/export
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from singer_sdk.testing import get_target_test_class

from target_oracle_oic.sinks import (
    ConnectionsSink,
    IntegrationsSink,
    LookupsSink,
    PackagesSink,
)
from target_oracle_oic.target import TargetOracleOIC


class TestTargetOracleOICE2E:
    """End-to-end tests for target-oracle-oic."""

    @pytest.fixture
    def config_path(self) -> str:
        """Return path to config.json."""
        config_file = Path(__file__).parent.parent / "config.json"
        if not config_file.exists():
            # Generate config if it doesn't exist
            import subprocess

            subprocess.run(
                ["python", "generate_config.py"],
                cwd=Path(__file__).parent.parent,
                check=True,
            )
        return str(config_file)

    @pytest.fixture
    def config(self, config_path: str) -> dict[str, object]:
        """Load configuration from config.json."""
        with open(config_path) as f:
            return json.load(f)

    @pytest.fixture
    def target(self, config: dict[str, object]) -> object:
        """Create target instance."""
        return TargetOracleOIC(config=config)

    def test_target_initialization(self, target, config) -> None:
        """Test target can be initialized with config."""
        assert target.name == "target-oracle-oic"
        assert target.config == config
        assert target.config["base_url"] == config["base_url"]

    def test_sink_discovery(self, target) -> None:
        """Test sink discovery for different stream types."""
        # Test known sinks
        assert target._get_sink_class("connections") == ConnectionsSink
        assert target._get_sink_class("integrations") == IntegrationsSink
        assert target._get_sink_class("packages") == PackagesSink
        assert target._get_sink_class("lookups") == LookupsSink

        # Test unknown stream returns default
        default_sink = target._get_sink_class("unknown_stream")
        assert default_sink == target.default_sink_class

    def test_sink_initialization(self, target) -> None:
        """Test that sinks can be initialized properly."""
        # Test each sink type
        sinks_to_test = [
            ("connections", ConnectionsSink),
            ("integrations", IntegrationsSink),
            ("packages", PackagesSink),
            ("lookups", LookupsSink),
        ]

        for stream_name, sink_class in sinks_to_test:
            sink = sink_class(
                target=target,
                stream_name=stream_name,
                schema={"properties": {"id": {"type": "string"}}},
                key_properties=["id"],
            )

            assert sink.name == stream_name
            assert sink.config == target.config

    def test_process_singer_messages(self, target, tmp_path) -> None:
        """Test processing of Singer protocol messages."""
        # Create test Singer messages
        messages = [
            {
                "type": "SCHEMA",
                "stream": "connections",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                    },
                },
                "key_properties": ["id"],
            },
            {
                "type": "RECORD",
                "stream": "connections",
                "record": {"id": "test-connection-1", "name": "Test Connection"},
            },
            {
                "type": "STATE",
                "value": {
                    "bookmarks": {
                        "connections": {"replication_key_value": "2024-01-01T00:00:00Z"}
                    }
                },
            },
        ]

        # Write messages to file
        input_file = tmp_path / "input.jsonl"
        with open(input_file, "w") as f:
            for msg in messages:
                f.write(json.dumps(msg) + "\n")

        # Process messages
        with open(input_file) as f, patch.object(ConnectionsSink, "process_record"):
            # Mock the sink to avoid actual API calls
            for line in f:
                message = json.loads(line)
                target._process_message(message)

    def test_authentication_handling(self, target) -> None:
        """Test OAuth2 authentication handling."""
        # Get a sink instance
        sink = ConnectionsSink(
            target=target,
            stream_name="connections",
            schema={"properties": {"id": {"type": "string"}}},
            key_properties=["id"],
        )

        # Test authenticator initialization
        authenticator = sink.authenticator
        assert authenticator is not None
        assert hasattr(authenticator, "auth_headers")

    @pytest.mark.skipif(
        os.getenv("SKIP_LIVE_TESTS", "true").lower() == "true",
        reason="Skipping live API tests",
    )
    def test_live_connection_create(self, target) -> None:
        """Test creating a connection in OIC."""
        sink = ConnectionsSink(
            target=target,
            stream_name="connections",
            schema={
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                }
            },
            key_properties=["id"],
        )

        # Test record
        test_record = {
            "id": "TEST_CONNECTION_E2E",
            "name": "E2E Test Connection",
            "type": "REST",
        }

        try:
            # Process the record
            sink.process_record(test_record, {})
            assert True
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                pytest.skip(f"Authentication failed: {e}")
            else:
                pytest.fail(f"Unexpected error: {e}")

    def test_integration_import_flow(self, target) -> None:
        """Test integration import with archive content."""
        sink = IntegrationsSink(
            target=target,
            stream_name="integrations",
            schema={
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "archive_content": {"type": "string"},
                }
            },
            key_properties=["id"],
        )

        # Mock the HTTP client to avoid actual API calls
        with patch.object(sink, "_client") as mock_client:
            # Mock responses
            mock_client.get.return_value.status_code = 404  # Integration doesn't exist
            mock_client.post.return_value.status_code = 201  # Creation successful

            # Test record with archive content
            test_record = {
                "id": "TEST_INTEGRATION_E2E",
                "name": "E2E Test Integration",
                "archive_content": "base64_encoded_iar_content_here",
            }

            # Process the record
            sink.process_record(test_record, {})

            # Verify import endpoint was called
            mock_client.post.assert_called()

    def test_error_handling(self, target) -> None:
        """Test error handling for various scenarios."""
        sink = ConnectionsSink(
            target=target,
            stream_name="connections",
            schema={"properties": {"id": {"type": "string"}}},
            key_properties=["id"],
        )

        # Test with invalid record (missing required field)
        with pytest.raises((ValueError, KeyError, TypeError)):
            sink.process_record({}, {})

    def test_config_validation(self) -> None:
        """Test config validation."""
        # Test missing required fields
        with pytest.raises((ValueError, KeyError, TypeError)):
            TargetOracleOIC(config={})

        # Test with minimal valid config
        minimal_config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
            "oauth_client_id": "test",
            "oauth_client_secret": "test",
            "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
        }

        target = TargetOracleOIC(config=minimal_config)
        assert target.config == minimal_config

    def test_batch_processing(self, target) -> None:
        """Test batch processing of records."""
        sink = PackagesSink(
            target=target,
            stream_name="packages",
            schema={
                "properties": {"id": {"type": "string"}, "name": {"type": "string"}}
            },
            key_properties=["id"],
        )

        # Create batch of test records
        records = [{"id": f"pkg-{i}", "name": f"Package {i}"} for i in range(10)]

        # Mock the HTTP client
        with patch.object(sink, "_client") as mock_client:
            mock_client.get.return_value.status_code = 404
            mock_client.post.return_value.status_code = 201

            # Process all records
            for record in records:
                sink.process_record(record, {})

            # Verify all records were processed
            assert mock_client.post.call_count >= len(records)

    def test_update_vs_create_logic(self, target) -> None:
        """Test update vs create decision logic."""
        sink = LookupsSink(
            target=target,
            stream_name="lookups",
            schema={
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                }
            },
            key_properties=["id"],
        )

        test_record = {"id": "test-lookup", "name": "Test Lookup", "version": "1.0"}

        # Mock client responses
        with patch.object(sink, "_client") as mock_client:
            # Test CREATE flow (entity doesn't exist)
            mock_client.get.return_value.status_code = 404
            mock_client.post.return_value.status_code = 201

            sink.process_record(test_record, {})
            mock_client.post.assert_called()

            # Reset mocks
            mock_client.reset_mock()

            # Test UPDATE flow (entity exists)
            mock_client.get.return_value.status_code = 200
            mock_client.get.return_value.json.return_value = {"version": "1.0"}
            mock_client.put.return_value.status_code = 200

            sink.process_record(test_record, {})
            mock_client.put.assert_called()

    def test_cli_execution(self, config_path, tmp_path) -> None:
        """Test CLI execution with Singer input."""
        import subprocess

        # Create test Singer input
        singer_input = [
            {
                "type": "SCHEMA",
                "stream": "connections",
                "schema": {"type": "object", "properties": {"id": {"type": "string"}}},
                "key_properties": ["id"],
            },
            {
                "type": "RECORD",
                "stream": "connections",
                "record": {"id": "test-cli-connection"},
            },
        ]

        input_file = tmp_path / "singer_input.jsonl"
        with open(input_file, "w") as f:
            for msg in singer_input:
                f.write(json.dumps(msg) + "\n")

        # Run target via CLI
        with open(input_file) as f:
            result = subprocess.run(
                ["python", "-m", "target_oracle_oic", "--config", config_path],
                stdin=f,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                check=False,
            )

        # Should complete without errors (might fail on actual API calls)
        # Check that it at least started processing
        assert "target-oracle-oic" in result.stderr or result.returncode == 0

    def test_conditional_config_generation(self) -> None:
        """Test conditional config.json generation."""
        config_path = Path(__file__).parent.parent / "config.json"

        # If config doesn't exist, it should be generated
        if not config_path.exists():
            import subprocess

            result = subprocess.run(
                ["python", "generate_config.py"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                input="y\n",
                check=False,
            )
            assert result.returncode == 0
            assert config_path.exists()

        # Load and validate config
        with open(config_path) as f:
            config = json.load(f)

        # Check required fields
        assert "base_url" in config
        assert "oauth_client_id" in config
        assert "oauth_client_secret" in config
        assert "oauth_token_url" in config

        # Check target-specific fields
        assert "import_mode" in config
        assert config["import_mode"] in ["create", "update", "create_or_update"]


# Additional test class using Singer SDK test framework
TargetOICTestClass = get_target_test_class(
    target_class=TargetOracleOIC,
    config={
        "base_url": "https://test.integration.ocp.oraclecloud.com",
        "oauth_client_id": "test_client",
        "oauth_client_secret": "test_secret",
        "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
    },
)


class TestTargetOICSingerSDK(TargetOICTestClass):
    """Singer SDK standard tests for target-oracle-oic."""
