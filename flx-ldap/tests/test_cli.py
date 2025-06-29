"""Tests for flx-ldap CLI."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from flx_ldap.cli import cli

if TYPE_CHECKING:
    from pathlib import Path


class TestCLI:
    """Test CLI commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Get CLI runner."""
        return CliRunner()

    @pytest.fixture
    def config_file(self, tmp_path: Path) -> Path:
        """Create test config file."""
        config_path = tmp_path / "config.yml"
        config_path.write_text(
            """
tap:
  host: test.ldap.com
  base_dn: dc=test,dc=com
target:
  host: test.ldap.com
  base_dn: dc=test,dc=com
output_path: ./test-output
""",
        )
        return config_path

    def test_cli_help(self, runner: CliRunner) -> None:
        """Test CLI help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FLX-LDAP: Unified CLI for LDAP ETL operations" in result.output

    def test_validate_command(self, runner: CliRunner, config_file: Path) -> None:
        """Test validate command."""
        with patch("flx_ldap.cli.LDAPOrchestrator") as mock_orchestrator:
            mock_instance = MagicMock()
            mock_instance.validate_config.return_value = True
            mock_orchestrator.return_value = mock_instance

            result = runner.invoke(cli, ["--config", str(config_file), "validate"])
            assert result.exit_code == 0
            mock_instance.validate_config.assert_called_once()

    def test_show_config_command(self, runner: CliRunner, config_file: Path) -> None:
        """Test show-config command."""
        result = runner.invoke(cli, ["--config", str(config_file), "show-config"])
        assert result.exit_code == 0
        assert "host: test.ldap.com" in result.output

    @patch("flx_ldap.cli.LDAPOrchestrator")
    def test_extract_command(
        self,
        mock_orchestrator_class: MagicMock,
        runner: CliRunner,
        config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test extract command."""
        mock_orchestrator = MagicMock()
        output_path = tmp_path / "output.jsonl"
        output_path.write_text('{"type": "RECORD", "stream": "users", "record": {}}\n')

        mock_orchestrator.run_tap.return_value = (True, output_path)
        mock_orchestrator_class.return_value = mock_orchestrator

        result = runner.invoke(cli, ["--config", str(config_file), "extract"])
        assert result.exit_code == 0
        mock_orchestrator.run_tap.assert_called_once()

    @patch("flx_ldap.cli.LDAPOrchestrator")
    def test_transform_command(
        self,
        mock_orchestrator_class: MagicMock,
        runner: CliRunner,
        config_file: Path,
    ) -> None:
        """Test transform command."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.run_dbt.return_value = True
        mock_orchestrator_class.return_value = mock_orchestrator

        result = runner.invoke(cli, ["--config", str(config_file), "transform", "run"])
        assert result.exit_code == 0
        mock_orchestrator.run_dbt.assert_called_once_with("run", None, False)

    @patch("flx_ldap.cli.LDAPOrchestrator")
    def test_load_command(
        self,
        mock_orchestrator_class: MagicMock,
        runner: CliRunner,
        config_file: Path,
    ) -> None:
        """Test load command."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.run_target.return_value = True
        mock_orchestrator_class.return_value = mock_orchestrator

        result = runner.invoke(cli, ["--config", str(config_file), "load"])
        assert result.exit_code == 0
        mock_orchestrator.run_target.assert_called_once_with(None, False)

    @patch("flx_ldap.cli.LDAPOrchestrator")
    def test_sync_command(
        self,
        mock_orchestrator_class: MagicMock,
        runner: CliRunner,
        config_file: Path,
    ) -> None:
        """Test sync command."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.run_sync.return_value = True
        mock_orchestrator_class.return_value = mock_orchestrator

        result = runner.invoke(cli, ["--config", str(config_file), "sync"])
        assert result.exit_code == 0
        mock_orchestrator.run_sync.assert_called_once()

    def test_migrate_plan_command(self, runner: CliRunner, config_file: Path) -> None:
        """Test migrate plan command."""
        with patch("flx_ldap.cli.AlgarMigrationAdapter") as mock_adapter_class:
            mock_adapter = MagicMock()
            mock_adapter.generate_migration_plan.return_value = {
                "phases": [
                    {
                        "name": "test_phase",
                        "description": "Test phase",
                        "steps": ["Step 1", "Step 2"],
                    },
                ],
            }
            mock_adapter_class.return_value = mock_adapter

            result = runner.invoke(
                cli,
                [
                    "--config",
                    str(config_file),
                    "migrate",
                    "plan",
                    "--source-host",
                    "source.ldap.com",
                    "--target-host",
                    "target.ldap.com",
                    "--base-dn",
                    "dc=test,dc=com",
                ],
            )
            assert result.exit_code == 0
            assert "Migration Plan" in result.output
            assert "test_phase" in result.output
