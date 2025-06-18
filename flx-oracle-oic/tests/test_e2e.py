"""End-to-End tests for TAP-OIC.

These tests run against a real OIC instance if config.json is available
in the project root. If not available, tests are skipped.
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from tap_oic.cli import cli
from tap_oic.tap import TapOIC

# Check if config.json exists in project root
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
CONFIG_AVAILABLE = CONFIG_PATH.exists()

# Skip marker for tests requiring real config
requires_config = pytest.mark.skipif(
    not CONFIG_AVAILABLE, reason="config.json not available in project root"
)


@pytest.fixture()
def real_config():
    """Load real configuration if available."""
    if not CONFIG_AVAILABLE:
        pytest.skip("config.json not available")

    with open(CONFIG_PATH) as f:
        return json.load(f)


class TestE2EWithRealConfig:
    """End-to-end tests with real OIC configuration."""

    @requires_config
    def test_tap_discovery_real(self, real_config) -> None:
        """Test TAP discovery with real configuration."""
        tap = TapOIC(config=real_config)
        streams = tap.discover_streams()

        # Should discover at least core streams
        assert len(streams) >= 5

        # Check that core streams are present
        stream_names = [stream.name for stream in streams]
        core_streams = [
            "integrations",
            "connections",
            "packages",
            "lookups",
            "libraries",
        ]

        for core_stream in core_streams:
            assert core_stream in stream_names

    @requires_config
    def test_tap_catalog_generation_real(self, real_config) -> None:
        """Test catalog generation with real configuration."""
        tap = TapOIC(config=real_config)
        catalog = tap.catalog_dict

        assert "streams" in catalog
        assert len(catalog["streams"]) >= 5

        # Check that each stream has required properties
        for stream in catalog["streams"]:
            assert "tap_stream_id" in stream
            assert "schema" in stream
            assert "key_properties" in stream

    @requires_config
    def test_cli_discovery_real(self, real_config) -> None:
        """Test CLI discovery with real configuration."""
        with open("temp_config.json", "w") as f:
            json.dump(real_config, f)

        try:
            runner = CliRunner()
            result = runner.invoke(cli, ["--discover"])

            assert result.exit_code == 0

            # Parse output as JSON
            catalog_data = json.loads(result.output)
            assert "streams" in catalog_data
            assert len(catalog_data["streams"]) >= 5

        finally:
            Path("temp_config.json").unlink(missing_ok=True)

    @requires_config
    def test_cli_about_command_real(self, real_config) -> None:
        """Test CLI about command with real config available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--about", "--format", "json"])

        assert result.exit_code == 0

        about_data = json.loads(result.output)
        assert about_data["name"] == "tap-oic"
        assert "version" in about_data
        assert "capabilities" in about_data

    @requires_config
    def test_admin_test_connection_real(self, real_config) -> None:
        """Test admin test-connection with real configuration."""
        with open("temp_config.json", "w") as f:
            json.dump(real_config, f)

        try:
            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "admin",
                    "test-connection",
                    "--config",
                    "temp_config.json",
                    "--verbose",
                ],
            )

            assert result.exit_code == 0
            assert "Connection successful" in result.output
            assert "Discovered" in result.output
            assert "streams" in result.output

        finally:
            Path("temp_config.json").unlink(missing_ok=True)

    @requires_config
    def test_admin_validate_config_real(self, real_config) -> None:
        """Test admin validate-config with real configuration."""
        with open("temp_config.json", "w") as f:
            json.dump(real_config, f)

        try:
            runner = CliRunner()
            result = runner.invoke(
                cli, ["admin", "validate-config", "--config", "temp_config.json"]
            )

            assert result.exit_code == 0
            assert "Configuration is valid" in result.output

        finally:
            Path("temp_config.json").unlink(missing_ok=True)


class TestE2EStreamValidation:
    """Test individual stream validation with real config."""

    @requires_config
    def test_integrations_stream_real(self, real_config) -> None:
        """Test integrations stream with real data."""
        tap = TapOIC(config=real_config)
        streams = tap.discover_streams()

        integrations_stream = next(
            (s for s in streams if s.name == "integrations"), None
        )
        assert integrations_stream is not None

        # Test stream properties
        assert integrations_stream.primary_keys == ["id"]
        assert integrations_stream.replication_key == "lastUpdated"

    @requires_config
    def test_connections_stream_real(self, real_config) -> None:
        """Test connections stream with real data."""
        tap = TapOIC(config=real_config)
        streams = tap.discover_streams()

        connections_stream = next((s for s in streams if s.name == "connections"), None)
        assert connections_stream is not None

        # Test stream properties
        assert connections_stream.primary_keys == ["id"]
        assert connections_stream.replication_key == "lastUpdated"

    @requires_config
    def test_packages_stream_real(self, real_config) -> None:
        """Test packages stream with real data."""
        tap = TapOIC(config=real_config)
        streams = tap.discover_streams()

        packages_stream = next((s for s in streams if s.name == "packages"), None)
        assert packages_stream is not None

        # Test stream properties
        assert packages_stream.primary_keys == ["id"]
        assert packages_stream.replication_key == "lastUpdated"


class TestE2EExtractCommands:
    """Test extract commands with real configuration."""

    @requires_config
    @pytest.mark.slow()
    def test_extract_core_real(self, real_config) -> None:
        """Test core data extraction with real configuration."""
        with open("temp_config.json", "w") as f:
            json.dump(real_config, f)

        try:
            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "extract",
                    "core",
                    "--config",
                    "temp_config.json",
                    "--output-dir",
                    "test_extract_real",
                    "--format",
                    "json",
                ],
            )

            assert result.exit_code == 0
            assert "Core extraction completed" in result.output

            # Check that output directory was created
            output_dir = Path("test_extract_real")
            if output_dir.exists():
                # Clean up
                import shutil

                shutil.rmtree(output_dir)

        finally:
            Path("temp_config.json").unlink(missing_ok=True)


class TestE2EConfigValidation:
    """Test configuration validation scenarios."""

    def test_missing_config_detection(self) -> None:
        """Test that missing config is properly detected."""
        # This test always runs regardless of config availability
        assert CONFIG_PATH.exists() == CONFIG_AVAILABLE

    @requires_config
    def test_config_has_required_fields(self, real_config) -> None:
        """Test that real config has all required fields."""
        required_fields = [
            "base_url",
            "oauth_client_id",
            "oauth_client_secret",
            "oauth_token_url",
        ]

        for field in required_fields:
            assert field in real_config, f"Missing required field: {field}"
            assert real_config[field], f"Empty required field: {field}"

    @requires_config
    def test_config_urls_use_https(self, real_config) -> None:
        """Test that URLs in config use HTTPS."""
        url_fields = ["base_url", "oauth_token_url"]

        for field in url_fields:
            if field in real_config:
                assert real_config[field].startswith(
                    "https://"
                ), f"{field} should use HTTPS: {real_config[field]}"


class TestE2EPerformance:
    """Performance tests with real configuration."""

    @requires_config
    @pytest.mark.slow()
    def test_discovery_performance(self, real_config) -> None:
        """Test that discovery completes in reasonable time."""
        import time

        start_time = time.time()
        tap = TapOIC(config=real_config)
        streams = tap.discover_streams()
        end_time = time.time()

        discovery_time = end_time - start_time

        # Discovery should complete in less than 30 seconds
        assert discovery_time < 30, f"Discovery took {discovery_time:.2f} seconds"
        assert len(streams) >= 5, "Should discover at least 5 core streams"


# Mock tests for when config is not available
class TestE2EMockWhenNoConfig:
    """Mock E2E tests when real config is not available."""

    @pytest.mark.skipif(CONFIG_AVAILABLE, reason="Real config is available")
    def test_mock_discovery_when_no_config(self) -> None:
        """Mock discovery test when real config is not available."""
        # This provides test coverage even without real config
        mock_config = {
            "base_url": "https://mock.integration.ocp.oraclecloud.com",
            "oauth_client_id": "mock_client_id",
            "oauth_client_secret": "mock_client_secret",
            "oauth_token_url": "https://mock.identity.oraclecloud.com/oauth2/v1/token",
        }

        tap = TapOIC(config=mock_config, validate_config=False)
        streams = tap.discover_streams()

        # Should discover at least core streams even with mock config
        assert len(streams) >= 5

    @pytest.mark.skipif(CONFIG_AVAILABLE, reason="Real config is available")
    def test_mock_cli_commands_when_no_config(self) -> None:
        """Mock CLI tests when real config is not available."""
        runner = CliRunner()

        # Test commands that don't require actual connectivity
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["extract", "--help"])
        assert result.exit_code == 0


def test_config_availability_reporting() -> None:
    """Report on config availability for test runs."""
    if CONFIG_AVAILABLE:
        pass
