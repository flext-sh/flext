"""Configuration management for flx-ldap.

This module handles configuration for all LDAP ETL components.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    import yaml  # type: ignore[import-untyped]
else:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        yaml = None


class TapConfig(BaseModel):
    """Configuration for tap-ldap."""

    host: str = Field(..., description="LDAP server hostname")
    port: int = Field(389, description="LDAP server port")
    bind_dn: str | None = Field(None, description="Bind DN")
    password: str | None = Field(None, description="Bind password")
    base_dn: str = Field(..., description="Base DN for searches")
    use_ssl: bool = Field(default=False, description="Use SSL/TLS")
    timeout: int = Field(30, description="Connection timeout")
    page_size: int = Field(1000, description="Page size for results")
    user_filter: str = Field("(objectClass=inetOrgPerson)", description="User filter")
    group_filter: str = Field("(objectClass=groupOfNames)", description="Group filter")
    custom_streams: list[dict[str, Any]] = Field(default_factory=list)


class TargetConfig(BaseModel):
    """Configuration for target-ldap."""

    host: str = Field(..., description="LDAP server hostname")
    port: int = Field(389, description="LDAP server port")
    bind_dn: str | None = Field(None, description="Bind DN")
    password: str | None = Field(None, description="Bind password")
    base_dn: str = Field(..., description="Base DN for operations")
    use_ssl: bool = Field(default=False, description="Use SSL/TLS")
    timeout: int = Field(30, description="Connection timeout")
    validate_records: bool = Field(default=True, description="Validate before loading")
    user_rdn_attribute: str = Field("uid", description="User RDN attribute")
    group_rdn_attribute: str = Field("cn", description="Group RDN attribute")
    dn_templates: dict[str, str] = Field(default_factory=dict)
    default_object_classes: dict[str, list[str]] = Field(default_factory=dict)


class DBTConfig(BaseModel):
    """Configuration for dbt-ldap."""

    project_dir: Path = Field(..., description="dbt project directory")
    profiles_dir: Path | None = Field(None, description="dbt profiles directory")
    target: str = Field("dev", description="dbt target")
    vars: dict[str, Any] = Field(default_factory=dict, description="dbt variables")
    threads: int = Field(4, description="Number of threads")
    models: list[str] | None = Field(None, description="Specific models to run")


class MigrationConfig(BaseModel):
    """Configuration for migration operations."""

    source_tap_config: TapConfig
    target_tap_config: TapConfig | None = None
    target_config: TargetConfig
    dbt_config: DBTConfig | None = None
    comparison_enabled: bool = Field(
        default=True,
        description="Enable source/target comparison",
    )
    dry_run: bool = Field(default=False, description="Dry run mode")
    batch_size: int = Field(1000, description="Batch size for operations")


class FlxLDAPConfig(BaseModel):
    """Main configuration for flx-ldap."""

    tap: TapConfig | None = None
    target: TargetConfig | None = None
    dbt: DBTConfig | None = None
    migration: MigrationConfig | None = None
    catalog_path: Path | None = Field(None, description="Singer catalog path")
    state_path: Path | None = Field(None, description="Singer state path")
    output_path: Path = Field(Path("./output"), description="Output directory")
    log_level: str = Field("INFO", description="Logging level")

    @field_validator("output_path", mode="before")
    @classmethod
    def create_output_dir(cls, v: Any) -> Path:
        """Ensure output directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def from_file(cls, config_path: str | Path) -> FlxLDAPConfig:
        """Load configuration from file.

        Args:
            config_path: Path to configuration file (JSON or YAML)

        Returns:
            FlxLDAPConfig instance

        Raises:
            ValueError: If file format is not supported

        """
        config_path = Path(config_path)

        if config_path.suffix in {".yml", ".yaml"}:
            if yaml is None:
                msg = "PyYAML is required for YAML config files. Install with: pip install PyYAML"
                raise ValueError(msg)
            with config_path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
        elif config_path.suffix == ".json":
            with config_path.open(encoding="utf-8") as f:
                data = json.load(f)
        else:
            msg = f"Unsupported config format: {config_path.suffix}"
            raise ValueError(msg)

        return cls(**data)

    @classmethod
    def from_env(cls) -> FlxLDAPConfig:
        """Load configuration from environment variables.

        Returns:
            FlxLDAPConfig instance with values from env vars

        """
        config_data: dict[str, Any] = {}

        # Load tap config from env
        if os.getenv("LDAP_TAP_HOST"):
            config_data["tap"] = {
                "host": os.getenv("LDAP_TAP_HOST"),
                "port": int(os.getenv("LDAP_TAP_PORT", "389")),
                "bind_dn": os.getenv("LDAP_TAP_BIND_DN"),
                "password": os.getenv("LDAP_TAP_PASSWORD"),
                "base_dn": os.getenv("LDAP_TAP_BASE_DN", ""),
                "use_ssl": os.getenv("LDAP_TAP_USE_SSL", "false").lower() == "true",
            }

        # Load target config from env
        if os.getenv("LDAP_TARGET_HOST"):
            config_data["target"] = {
                "host": os.getenv("LDAP_TARGET_HOST"),
                "port": int(os.getenv("LDAP_TARGET_PORT", "389")),
                "bind_dn": os.getenv("LDAP_TARGET_BIND_DN"),
                "password": os.getenv("LDAP_TARGET_PASSWORD"),
                "base_dn": os.getenv("LDAP_TARGET_BASE_DN", ""),
                "use_ssl": os.getenv("LDAP_TARGET_USE_SSL", "false").lower() == "true",
            }

        # Load dbt config from env
        if os.getenv("DBT_PROJECT_DIR"):
            config_data["dbt"] = {
                "project_dir": os.getenv("DBT_PROJECT_DIR"),
                "profiles_dir": os.getenv("DBT_PROFILES_DIR"),
                "target": os.getenv("DBT_TARGET", "dev"),
                "threads": int(os.getenv("DBT_THREADS", "4")),
            }

        # Load general config from env
        config_data.update(
            {
                "catalog_path": os.getenv("FLX_LDAP_CATALOG_PATH"),
                "state_path": os.getenv("FLX_LDAP_STATE_PATH"),
                "output_path": os.getenv("FLX_LDAP_OUTPUT_PATH", "./output"),
                "log_level": os.getenv("FLX_LDAP_LOG_LEVEL", "INFO"),
            },
        )

        return cls(**config_data)

    def to_tap_config(self) -> dict[str, Any]:
        """Convert to tap-ldap configuration dict."""
        if not self.tap:
            return {}
        return self.tap.model_dump(exclude_none=True)

    def to_target_config(self) -> dict[str, Any]:
        """Convert to target-ldap configuration dict."""
        if not self.target:
            return {}
        return self.target.model_dump(exclude_none=True)

    def to_dbt_args(self) -> list[str]:
        """Convert to dbt command-line arguments."""
        if not self.dbt:
            return []

        args: list[str] = []

        if self.dbt.project_dir:
            args.extend(["--project-dir", str(self.dbt.project_dir)])

        if self.dbt.profiles_dir:
            args.extend(["--profiles-dir", str(self.dbt.profiles_dir)])

        if self.dbt.target:
            args.extend(["--target", self.dbt.target])

        if self.dbt.threads:
            args.extend(["--threads", str(self.dbt.threads)])

        if self.dbt.vars:
            vars_str = json.dumps(self.dbt.vars)
            args.extend(["--vars", vars_str])

        return args
