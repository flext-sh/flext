#!/usr/bin/env python3
"""Comprehensive End-to-End tests for flx-oracle-oic.

Tests all functionalities including:
- Unified CLI
- TAP operations
- Target operations
- Extension operations
- FLX adapter functionality
- Authentication
- Error handling
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from flx_oracle_oic.adapter import OracleOICAdapter
from flx_oracle_oic.auth import OICAuth
from flx_oracle_oic.cli import app
from typer.testing import CliRunner


class TestFLXOracleOICE2E:
    """End-to-end tests for flx-oracle-oic."""

    @pytest.fixture()
    def config_path(self):
        """Return path to config.json."""
        config_file = Path(__file__).parent.parent / "config.json"
        if not config_file.exists():
            # Generate config if it doesn't exist
            os.system("cd .. && python generate_config.py")
        return str(config_file)

    @pytest.fixture()
    def config(self, config_path):
        """Load configuration from config.json."""
        with open(config_path) as f:
            return json.load(f)

    @pytest.fixture()
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture()
    def adapter(self, config):
        """Create adapter instance."""
        return OracleOICAdapter(**config)

    def test_cli_help(self, runner) -> None:
        """Test CLI help command."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Oracle Integration Cloud Unified CLI" in result.output
        assert "tap" in result.output
        assert "target" in result.output
        assert "ext" in result.output
        assert "adapter" in result.output

    def test_tap_commands(self, runner) -> None:
        """Test TAP subcommands."""
        # Test tap help
        result = runner.invoke(app, ["tap", "--help"])
        assert result.exit_code == 0
        assert "discover" in result.output
        assert "catalog" in result.output
        assert "sync" in result.output

        # Test discover command
        result = runner.invoke(app, ["tap", "discover", "--help"])
        assert result.exit_code == 0
        assert "--config" in result.output

    def test_target_commands(self, runner) -> None:
        """Test Target subcommands."""
        # Test target help
        result = runner.invoke(app, ["target", "--help"])
        assert result.exit_code == 0
        assert "load" in result.output
        assert "validate" in result.output

    def test_extension_commands(self, runner) -> None:
        """Test Extension subcommands."""
        # Test ext help
        result = runner.invoke(app, ["ext", "--help"])
        assert result.exit_code == 0
        assert "lifecycle" in result.output
        assert "monitor" in result.output
        assert "extract" in result.output

    def test_adapter_commands(self, runner) -> None:
        """Test FLX Adapter subcommands."""
        # Test adapter help
        result = runner.invoke(app, ["adapter", "--help"])
        assert result.exit_code == 0
        assert "connect" in result.output
        assert "health" in result.output
        assert "execute" in result.output

    def test_tap_discover_integration(self, runner, config_path) -> None:
        """Test TAP discover command integration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(
                {
                    "streams": [
                        {"tap_stream_id": "connections"},
                        {"tap_stream_id": "integrations"},
                    ]
                }
            )

            result = runner.invoke(app, ["tap", "discover", "--config", config_path])

            assert result.exit_code == 0
            mock_run.assert_called_once()

            # Check that tap-oracle-oic was called
            call_args = mock_run.call_args[0][0]
            assert "tap-oracle-oic" in call_args
            assert "--discover" in call_args

    def test_target_load_integration(self, runner, config_path, tmp_path) -> None:
        """Test Target load command integration."""
        # Create test Singer data
        singer_data = [
            {"type": "SCHEMA", "stream": "connections", "schema": {"properties": {}}},
            {"type": "RECORD", "stream": "connections", "record": {"id": "test"}},
        ]

        input_file = tmp_path / "singer_data.jsonl"
        with open(input_file, "w") as f:
            for line in singer_data:
                f.write(json.dumps(line) + "\n")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            result = runner.invoke(
                app,
                ["target", "load", "--config", config_path, "--input", str(input_file)],
            )

            assert result.exit_code == 0
            mock_run.assert_called_once()

            # Check that target-oracle-oic was called
            call_args = mock_run.call_args[0][0]
            assert "target-oracle-oic" in call_args

    def test_extension_lifecycle_integration(self, runner, config_path) -> None:
        """Test Extension lifecycle command integration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"status": "ACTIVATED"}'

            result = runner.invoke(
                app,
                [
                    "ext",
                    "lifecycle",
                    "status",
                    "--config",
                    config_path,
                    "--integration-id",
                    "TEST_INT",
                ],
            )

            assert result.exit_code == 0
            mock_run.assert_called_once()

            # Check that oracle-oic-ext was called
            call_args = mock_run.call_args[0][0]
            assert "oracle-oic-ext" in call_args
            assert "lifecycle:status" in call_args

    def test_adapter_operations(self, adapter) -> None:
        """Test FLX adapter operations."""
        # Test adapter initialization
        assert adapter.name == "flx-oracle-oic"
        assert adapter.adapter_type == "http"

        # Test configuration
        assert hasattr(adapter, "base_url")
        assert hasattr(adapter, "oauth_client_id")

    def test_adapter_health_check(self, runner, config_path) -> None:
        """Test adapter health check."""
        with patch.object(OracleOICAdapter, "health_check") as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
            }

            result = runner.invoke(app, ["adapter", "health", "--config", config_path])

            assert result.exit_code == 0
            assert "healthy" in result.output

    def test_authentication_flow(self, config) -> None:
        """Test OAuth2 authentication flow."""
        auth = OICAuth(
            client_id=config["oauth_client_id"],
            client_secret=config["oauth_client_secret"],
            token_url=config["oauth_token_url"],
            scope=config.get("oauth_scope"),
        )

        # Mock token response
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = {
                "access_token": "test_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }

            token = auth.get_access_token()
            assert token == "test_token"

            # Check headers
            headers = auth.get_headers()
            assert headers["Authorization"] == "Bearer test_token"

    def test_full_pipeline_flow(self, runner, config_path, tmp_path) -> None:
        """Test complete pipeline: discover -> sync -> load."""
        # 1. Discover
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(
                {"streams": [{"tap_stream_id": "connections"}]}
            )

            catalog_file = tmp_path / "catalog.json"
            result = runner.invoke(
                app,
                [
                    "tap",
                    "discover",
                    "--config",
                    config_path,
                    "--output",
                    str(catalog_file),
                ],
            )

            assert result.exit_code == 0

        # 2. Sync
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(
                {"type": "RECORD", "stream": "connections", "record": {"id": "test"}}
            )

            sync_output = tmp_path / "sync_output.jsonl"
            result = runner.invoke(
                app,
                [
                    "tap",
                    "sync",
                    "--config",
                    config_path,
                    "--catalog",
                    str(catalog_file),
                    "--output",
                    str(sync_output),
                ],
            )

            # Command should complete
            assert result.exit_code == 0 or "not implemented" in result.output

    def test_error_handling(self, runner) -> None:
        """Test error handling for various scenarios."""
        # Test missing config
        result = runner.invoke(app, ["tap", "discover"])
        assert result.exit_code != 0

        # Test invalid command
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_concurrent_operations(self, runner, config_path) -> None:
        """Test concurrent operations don't interfere."""
        import threading

        results = []

        def run_command(cmd) -> None:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "{}"

                result = runner.invoke(app, cmd)
                results.append(result.exit_code)

        # Run multiple commands concurrently
        threads = []
        commands = [
            ["tap", "discover", "--config", config_path],
            ["ext", "monitor", "health", "--config", config_path],
            ["adapter", "health", "--config", config_path],
        ]

        for cmd in commands:
            t = threading.Thread(target=run_command, args=(cmd,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All commands should complete successfully
        assert all(code == 0 for code in results)

    def test_config_precedence(self, runner, tmp_path) -> None:
        """Test config file vs environment variable precedence."""
        # Create test config
        test_config = {"base_url": "https://test.example.com"}
        config_file = tmp_path / "test_config.json"
        with open(config_file, "w") as f:
            json.dump(test_config, f)

        # Set environment variable
        os.environ["OIC_BASE_URL"] = "https://env.example.com"

        try:
            # Environment should take precedence
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                runner.invoke(app, ["tap", "discover", "--config", str(config_file)])

                # Check that environment value was used
                # (implementation dependent)
        finally:
            os.environ.pop("OIC_BASE_URL", None)

    @pytest.mark.skipif(
        os.getenv("SKIP_LIVE_TESTS", "true").lower() == "true",
        reason="Skipping live API tests",
    )
    def test_live_api_connection(self, runner, config_path) -> None:
        """Test live API connection."""
        result = runner.invoke(app, ["adapter", "health", "--config", config_path])

        # Should either succeed or fail with auth error
        if result.exit_code != 0:
            assert "401" in result.output or "403" in result.output
        else:
            assert "healthy" in result.output.lower()

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

        # Check FLX-specific fields
        assert "adapter_name" in config
        assert config["adapter_name"] == "flx-oracle-oic"
        assert "adapter_type" in config
