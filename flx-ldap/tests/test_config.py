"""Tests for configuration management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from flx_ldap.config import (
    DBTConfig,
    FlxLDAPConfig,
    MigrationConfig,
    TapConfig,
    TargetConfig,
)

if TYPE_CHECKING:
    import pytest


class TestConfig:
    """Test configuration classes."""

    def test_tap_config(self) -> None:
        """Test TapConfig."""
        config = TapConfig(
            host="test.ldap.com",
            base_dn="dc=test,dc=com",
        )

        assert config.host == "test.ldap.com"
        assert config.port == 389
        assert config.base_dn == "dc=test,dc=com"
        assert config.use_ssl is False
        assert config.timeout == 30

    def test_target_config(self) -> None:
        """Test TargetConfig."""
        config = TargetConfig(
            host="test.ldap.com",
            base_dn="dc=test,dc=com",
            dn_templates={"users": "uid={uid},ou=users,dc=test,dc=com"},
        )

        assert config.host == "test.ldap.com"
        assert config.validate_records is True
        assert config.user_rdn_attribute == "uid"
        assert "users" in config.dn_templates

    def test_dbt_config(self) -> None:
        """Test DBTConfig."""
        config = DBTConfig(
            project_dir=Path("/tmp/dbt-ldap"),
            target="prod",
            threads=8,
            vars={"ldap_base_dn": "dc=test,dc=com"},
        )

        assert config.project_dir == Path("/tmp/dbt-ldap")
        assert config.target == "prod"
        assert config.threads == 8
        assert config.vars["ldap_base_dn"] == "dc=test,dc=com"

    def test_migration_config(self) -> None:
        """Test MigrationConfig."""
        source_tap = TapConfig(host="source.ldap.com", base_dn="dc=source,dc=com")
        target_config = TargetConfig(host="target.ldap.com", base_dn="dc=target,dc=com")

        config = MigrationConfig(
            source_tap_config=source_tap,
            target_config=target_config,
            dry_run=True,
        )

        assert config.source_tap_config.host == "source.ldap.com"
        assert config.target_config.host == "target.ldap.com"
        assert config.dry_run is True
        assert config.batch_size == 1000

    def test_flx_ldap_config(self, tmp_path: Path) -> None:
        """Test FlxLDAPConfig."""
        config = FlxLDAPConfig(
            tap=TapConfig(host="test.ldap.com", base_dn="dc=test,dc=com"),
            target=TargetConfig(host="test.ldap.com", base_dn="dc=test,dc=com"),
            output_path=tmp_path / "output",
            log_level="DEBUG",
        )

        assert config.tap is not None
        assert config.tap.host == "test.ldap.com"
        assert config.log_level == "DEBUG"
        assert config.output_path.exists()

    def test_config_from_yaml(self, tmp_path: Path) -> None:
        """Test loading config from YAML."""
        config_data = {
            "tap": {
                "host": "test.ldap.com",
                "base_dn": "dc=test,dc=com",
            },
            "output_path": str(tmp_path / "output"),
        }

        config_file = tmp_path / "config.yml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        config = FlxLDAPConfig.from_file(config_file)
        assert config.tap is not None
        assert config.tap.host == "test.ldap.com"

    def test_config_from_json(self, tmp_path: Path) -> None:
        """Test loading config from JSON."""
        config_data = {
            "tap": {
                "host": "test.ldap.com",
                "base_dn": "dc=test,dc=com",
            },
            "output_path": str(tmp_path / "output"),
        }

        config_file = tmp_path / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        config = FlxLDAPConfig.from_file(config_file)
        assert config.tap is not None
        assert config.tap.host == "test.ldap.com"

    def test_config_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Test loading config from environment."""
        monkeypatch.setenv("LDAP_TAP_HOST", "env.ldap.com")
        monkeypatch.setenv("LDAP_TAP_BASE_DN", "dc=env,dc=com")
        monkeypatch.setenv("LDAP_TAP_PORT", "636")
        monkeypatch.setenv("LDAP_TAP_USE_SSL", "true")
        monkeypatch.setenv("FLX_LDAP_LOG_LEVEL", "WARNING")
        monkeypatch.setenv("FLX_LDAP_OUTPUT_PATH", str(tmp_path / "env-output"))

        config = FlxLDAPConfig.from_env()
        assert config.tap is not None
        assert config.tap.host == "env.ldap.com"
        assert config.tap.port == 636
        assert config.tap.use_ssl is True
        assert config.log_level == "WARNING"

    def test_to_tap_config(self) -> None:
        """Test converting to tap config dict."""
        config = FlxLDAPConfig(
            tap=TapConfig(
                host="test.ldap.com",
                base_dn="dc=test,dc=com",
                bind_dn="cn=admin,dc=test,dc=com",
            ),
        )

        tap_dict = config.to_tap_config()
        assert tap_dict["host"] == "test.ldap.com"
        assert tap_dict["base_dn"] == "dc=test,dc=com"
        assert tap_dict["bind_dn"] == "cn=admin,dc=test,dc=com"

    def test_to_dbt_args(self) -> None:
        """Test converting to dbt arguments."""
        config = FlxLDAPConfig(
            dbt=DBTConfig(
                project_dir=Path("/tmp/dbt-ldap"),
                profiles_dir=Path("/tmp/profiles"),
                target="prod",
                threads=8,
                vars={"test": "value"},
            ),
        )

        args = config.to_dbt_args()
        assert "--project-dir" in args
        assert "/tmp/dbt-ldap" in args
        assert "--profiles-dir" in args
        assert "--target" in args
        assert "prod" in args
        assert "--threads" in args
        assert "8" in args
        assert "--vars" in args
