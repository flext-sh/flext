"""Minimal configuration manager for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import ClassVar

from pydantic import Field, field_validator

from flext_core import FlextConfig, FlextResult


class FlextToolsConfig(FlextConfig):
    """FLEXT Tools Configuration extending FlextConfig.

    Follows standardized [Project]Config pattern:
    - Extends FlextConfig from flext-core
    - Uses Pydantic Settings for environment variable support
    - All defaults from FlextConstants
    - Proper Pydantic 2 validation
    - Singleton pattern with proper typing
    """

    # Singleton pattern attributes
    _global_instance: ClassVar[FlextToolsConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    # Configuration File Management
    config_file_path: str | None = Field(
        default=None,
        description="Path to configuration file",
    )

    # Environment Variable Prefixes
    env_prefixes: list[str] = Field(
        default_factory=lambda: ["FLEXT_", "ORACLE_", "POSTGRES_"],
        description="Environment variable prefixes to load",
    )

    # Tool Configuration
    backup_enabled: bool = Field(
        default=True,
        description="Enable backup functionality",
    )

    monitoring_enabled: bool = Field(
        default=True,
        description="Enable monitoring functionality",
    )

    linting_enabled: bool = Field(
        default=True,
        description="Enable linting functionality",
    )

    # Pydantic 2 field validators
    @field_validator("env_prefixes")
    @classmethod
    def validate_env_prefixes(cls, v: list[str]) -> list[str]:
        """Validate environment variable prefixes."""
        if not v:
            msg = "Environment prefixes cannot be empty"
            raise ValueError(msg)

        for prefix in v:
            if not prefix or not prefix.strip():
                msg = "Environment prefix cannot be empty"
                raise ValueError(msg)
            if not prefix.endswith("_"):
                msg = f"Environment prefix '{prefix}' must end with underscore"
                raise ValueError(msg)

        return v

    @field_validator("config_file_path")
    @classmethod
    def validate_config_file_path(cls, v: str | None) -> str | None:
        """Validate configuration file path."""
        if v is not None:
            if not v.strip():
                msg = "Configuration file path cannot be empty"
                raise ValueError(msg)

            # Validate path format but don't require existence
            try:
                Path(v)
            except Exception as e:
                msg = f"Invalid file path format: {e}"
                raise ValueError(msg) from e

        return v

    def load_environment_config(self) -> FlextResult[dict[str, str]]:
        """Load configuration from environment variables using Pydantic Settings."""
        try:
            # Filter environment variables with specified prefixes
            # This uses the environment variables that Pydantic BaseSettings has access to
            config_data: dict[str, str] = {}

            # Get environment variables that match our prefixes
            # Note: Pydantic BaseSettings already loaded these, we just expose them
            for key, value in os.environ.items():
                if any(key.startswith(prefix) for prefix in self.env_prefixes):
                    config_data[key] = str(value)

            return FlextResult[dict[str, str]].ok(config_data)
        except Exception as e:
            return FlextResult[dict[str, str]].fail(
                f"Failed to load environment config: {e}",
            )

    def get_config_value(self, key: str, default: str = "") -> FlextResult[str]:
        """Get configuration value with proper validation."""
        if not key or not key.strip():
            return FlextResult[str].fail("Configuration key cannot be empty")

        try:
            # Load environment config first
            env_result = self.load_environment_config()
            if env_result.is_failure:
                return FlextResult[str].fail(
                    f"Failed to load config: {env_result.error}",
                )

            value = env_result.data.get(key, default)
            return FlextResult[str].ok(value)
        except Exception as e:
            return FlextResult[str].fail(
                f"Failed to get config value for key '{key}': {e}",
            )

    def set_config_value(self, key: str, value: str) -> FlextResult[None]:
        """Set configuration value with proper validation using standardized approach."""
        if not key or not key.strip():
            return FlextResult[None].fail("Configuration key cannot be empty")

        if not isinstance(value, str):
            return FlextResult[None].fail("Configuration value must be a string")

        try:
            # Update the singleton instance instead of direct environment manipulation
            # This maintains consistency with our standardized config pattern
            if hasattr(self, key.lower()):
                # If it's a field in our config model, update it directly
                setattr(self, key.lower(), value)
            else:
                # For dynamic environment variables, we need to update the environment
                # but we document this as a legacy compatibility feature
                os.environ[key] = value

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                f"Failed to set config value for key '{key}': {e}",
            )

    def validate_tools_configuration(self) -> FlextResult[None]:
        """Validate the complete tools configuration."""
        try:
            # Validate config file if specified
            if self.config_file_path:
                config_path = Path(self.config_file_path)
                if not config_path.exists():
                    return FlextResult[None].fail(
                        f"Configuration file does not exist: {config_path}",
                    )
                if not config_path.is_file():
                    return FlextResult[None].fail(
                        f"Configuration path is not a file: {config_path}",
                    )

            # Validate environment variables
            env_result = self.load_environment_config()
            if env_result.is_failure:
                return FlextResult[None].fail(
                    f"Environment validation failed: {env_result.error}",
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration validation error: {e}")

    def get_tools_config(self) -> dict[str, object]:
        """Get tools configuration dictionary."""
        return {
            "config_file_path": self.config_file_path,
            "env_prefixes": self.env_prefixes,
            "backup_enabled": self.backup_enabled,
            "monitoring_enabled": self.monitoring_enabled,
            "linting_enabled": self.linting_enabled,
        }

    @classmethod
    def create_for_environment(
        cls,
        environment: str,
        **overrides: object,
    ) -> FlextToolsConfig:
        """Create configuration for specific environment."""
        env_overrides: dict[str, object] = {}

        if environment == "production":
            env_overrides.update(
                {
                    "backup_enabled": True,
                    "monitoring_enabled": True,
                    "linting_enabled": True,
                }
            )
        elif environment == "development":
            env_overrides.update(
                {
                    "backup_enabled": False,
                    "monitoring_enabled": True,
                    "linting_enabled": True,
                }
            )
        elif environment == "testing":
            env_overrides.update(
                {
                    "backup_enabled": False,
                    "monitoring_enabled": False,
                    "linting_enabled": True,
                }
            )

        all_overrides = {**env_overrides, **overrides, "environment": environment}
        return cls(**all_overrides)

    @classmethod
    def create_default(cls) -> FlextToolsConfig:
        """Create default configuration instance."""
        return cls()

    # Singleton pattern override for proper typing
    @classmethod
    def get_global_instance(cls) -> FlextToolsConfig:
        """Get the global singleton instance of FlextToolsConfig."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextToolsConfig instance (mainly for testing)."""
        cls._global_instance = None


# Legacy compatibility wrapper - maintain backward compatibility
class ConfigurationManager:
    """Legacy ConfigurationManager wrapper for backward compatibility."""

    def __init__(self, config_file: str | Path | None = None) -> None:
        """Initialize configuration manager with legacy interface."""
        self._config_instance = FlextToolsConfig(
            config_file_path=str(config_file) if config_file else None,
        )
        # Legacy attribute compatibility
        self.config_file = Path(config_file) if config_file else None
        self._config: dict[str, str] = {}

    def load_config(self) -> FlextResult[dict[str, str]]:
        """Load configuration from file or environment."""
        result = self._config_instance.load_environment_config()
        if result.is_success:
            self._config = result.data
        return result

    def get(self, key: str, default: str = "") -> FlextResult[str]:
        """Get configuration value with type-safe error handling."""
        # Check internal config first, then environment
        if key in self._config:
            return FlextResult[str].ok(self._config[key])
        return self._config_instance.get_config_value(key, default)

    def set(self, key: str, value: str) -> FlextResult[None]:
        """Set configuration value with type-safe error handling."""
        result = self._config_instance.set_config_value(key, value)
        if result.is_success:
            # Also update internal config for immediate access
            self._config[key] = value
        return result

    def validate_config(self) -> FlextResult[None]:
        """Validate configuration."""
        return self._config_instance.validate_tools_configuration()
