"""Tests for flx-oracle-oic unified CLI."""

import json
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from flx_oracle_oic.cli import app

runner = CliRunner()


class TestUnifiedCLI:
    """Test cases for unified CLI."""

    def test_cli_help(self) -> None:
        """Test CLI shows help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Oracle Integration Cloud Unified CLI" in result.stdout
        assert "tap" in result.stdout
        assert "target" in result.stdout
        assert "ext" in result.stdout
        assert "adapter" in result.stdout

    def test_cli_version(self) -> None:
        """Test CLI shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "flx-oracle-oic version" in result.stdout

    def test_validate_config_valid(self) -> None:
        """Test config validation with valid config."""
        config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
            "oauth_client_id": "test_client",
            "oauth_client_secret": "test_secret",
            "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            result = runner.invoke(app, ["validate-config", "--config", config_file])
            assert result.exit_code == 0
            assert "Configuration is valid" in result.stdout
        finally:
            Path(config_file).unlink()

    def test_validate_config_invalid(self) -> None:
        """Test config validation with invalid config."""
        config = {
            "base_url": "http://test.integration.ocp.oraclecloud.com",  # HTTP not allowed
            "oauth_client_id": "test_client",
            # Missing required fields
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            result = runner.invoke(app, ["validate-config", "--config", config_file])
            assert result.exit_code == 1
            assert "Configuration validation failed" in result.stdout
            assert "must use HTTPS protocol" in result.stdout
            assert "Missing required field" in result.stdout
        finally:
            Path(config_file).unlink()

    def test_tap_commands(self) -> None:
        """Test tap subcommands are available."""
        result = runner.invoke(app, ["tap", "--help"])
        assert result.exit_code == 0
        assert "discover" in result.stdout
        assert "extract" in result.stdout

    def test_target_commands(self) -> None:
        """Test target subcommands are available."""
        result = runner.invoke(app, ["target", "--help"])
        assert result.exit_code == 0
        assert "load" in result.stdout

    def test_ext_commands(self) -> None:
        """Test extension subcommands are available."""
        result = runner.invoke(app, ["ext", "--help"])
        assert result.exit_code == 0
        assert "lifecycle" in result.stdout
        assert "monitor" in result.stdout

    def test_adapter_commands(self) -> None:
        """Test adapter subcommands are available."""
        result = runner.invoke(app, ["adapter", "--help"])
        assert result.exit_code == 0
        assert "status" in result.stdout

    def test_pipeline_dry_run(self) -> None:
        """Test pipeline dry run."""
        pipeline_config = {
            "tap": {
                "base_url": "https://source.integration.ocp.oraclecloud.com",
                "oauth_client_id": "source_client",
                "oauth_client_secret": "source_secret",
                "oauth_token_url": "https://source.identity.oraclecloud.com/oauth2/v1/token",
            },
            "target": {
                "base_url": "https://target.integration.ocp.oraclecloud.com",
                "oauth_client_id": "target_client",
                "oauth_client_secret": "target_secret",
                "oauth_token_url": "https://target.identity.oraclecloud.com/oauth2/v1/token",
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(pipeline_config, f)
            config_file = f.name

        try:
            result = runner.invoke(
                app, ["pipeline", "--config", config_file, "--dry-run"]
            )
            assert result.exit_code == 0
            assert "DRY RUN" in result.stdout
            assert "Would extract data" in result.stdout
            assert "Would load data" in result.stdout
        finally:
            Path(config_file).unlink()
