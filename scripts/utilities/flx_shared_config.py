"""Shared configuration utilities for FLX projects.

This module provides standardized configuration patterns to ensure
consistency across all FLX adapter projects.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings as PydanticBaseSettings

T = TypeVar("T", bound="BaseSettings")


class FlxBaseConfig(PydanticBaseSettings):
    """Base configuration class for all FLX projects.

    Provides standardized configuration patterns with:
    - Environment variable loading
    - Validation
    - Type safety
    - Documentation
    """

    # Common configuration fields
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")

    # Connection settings
    timeout: int = Field(default=30, description="Default timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "forbid"
        validate_assignment = True


class FlxAdapterConfig(FlxBaseConfig):
    """Base configuration for FLX adapters.

    Extends FlxBaseConfig with adapter-specific settings.
    """

    # Adapter identification
    adapter_name: str = Field(..., description="Unique adapter name")
    adapter_version: str = Field(default="1.0.0", description="Adapter version")

    # Performance settings
    connection_pool_size: int = Field(default=10, description="Connection pool size")
    enable_caching: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")

    # Monitoring settings
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_tracing: bool = Field(
        default=False, description="Enable distributed tracing"
    )

    @classmethod
    def from_env(cls: type[T], env_prefix: str = "") -> T:
        """Create configuration from environment variables.

        Args:
            env_prefix: Prefix for environment variables

        Returns:
            Configured instance
        """
        if env_prefix:
            original_env = dict(os.environ)
            try:
                # Temporarily add prefixed env vars
                for key, value in original_env.items():
                    if key.startswith(env_prefix):
                        clean_key = key[len(env_prefix) :].lstrip("_")
                        os.environ[clean_key] = value

                return cls()
            finally:
                # Restore original environment
                os.environ.clear()
                os.environ.update(original_env)

        return cls()


class FlxDatabaseConfig(FlxAdapterConfig):
    """Configuration for database adapters."""

    # Database connection
    host: str = Field(..., description="Database host")
    port: int = Field(default=1521, description="Database port")
    service_name: str = Field(..., description="Database service name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")

    # Connection pool settings
    pool_size: int = Field(default=20, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max overflow connections")
    pool_timeout: int = Field(default=30, description="Pool checkout timeout")

    @property
    def connection_string(self) -> str:
        """Build connection string from configuration."""
        return (
            f"oracle+oracledb://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.service_name}"
        )


class FlxHttpConfig(FlxAdapterConfig):
    """Configuration for HTTP adapters."""

    # HTTP settings
    base_url: str = Field(..., description="Base URL for API")
    api_key: str | None = Field(default=None, description="API key")
    username: str | None = Field(default=None, description="Username")
    password: str | None = Field(default=None, description="Password")

    # HTTP client settings
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    follow_redirects: bool = Field(default=True, description="Follow HTTP redirects")
    max_redirects: int = Field(default=5, description="Maximum redirects")

    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Requests per minute")
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds"
    )


def create_config_from_dict[
    T: "BaseSettings"
](config_class: type[T], config_dict: dict[str, Any]) -> T:
    """Create configuration instance from dictionary.

    Args:
        config_class: Configuration class to instantiate
        config_dict: Configuration values

    Returns:
        Configured instance

    Raises:
        ValidationError: If configuration is invalid
    """
    return config_class(**config_dict)


def load_config_from_file[
    T: "BaseSettings"
](config_class: type[T], file_path: str | Path) -> T:
    """Load configuration from file.

    Args:
        config_class: Configuration class to instantiate
        file_path: Path to configuration file

    Returns:
        Configured instance

    Raises:
        FileNotFoundError: If file doesn't exist
        ValidationError: If configuration is invalid
    """
    import json
    import tomllib
    from pathlib import Path

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    if path.suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            config_dict = json.load(f)
    elif path.suffix in {".toml", ".tml"}:
        with path.open("rb") as f:
            config_dict = tomllib.load(f)
    else:
        raise ValueError(f"Unsupported configuration file format: {path.suffix}")

    return create_config_from_dict(config_class, config_dict)


def validate_config(config: FlxBaseConfig) -> list[str]:
    """Validate configuration and return any issues.

    Args:
        config: Configuration to validate

    Returns:
        List of validation issues (empty if valid)
    """
    issues = []

    # Validate log level
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if config.log_level.upper() not in valid_levels:
        issues.append(f"Invalid log level: {config.log_level}")

    # Validate timeout
    if config.timeout <= 0:
        issues.append("Timeout must be positive")

    # Validate retries
    if config.max_retries < 0:
        issues.append("Max retries cannot be negative")

    # Adapter-specific validation
    if isinstance(config, FlxAdapterConfig):
        if not config.adapter_name:
            issues.append("Adapter name is required")

        if config.connection_pool_size <= 0:
            issues.append("Connection pool size must be positive")

        if config.cache_ttl <= 0:
            issues.append("Cache TTL must be positive")

    # Database-specific validation
    if isinstance(config, FlxDatabaseConfig):
        if not config.host:
            issues.append("Database host is required")

        if config.port <= 0 or config.port > 65535:
            issues.append("Database port must be between 1 and 65535")

        if config.pool_size <= 0:
            issues.append("Pool size must be positive")

    # HTTP-specific validation
    if isinstance(config, FlxHttpConfig):
        if not config.base_url:
            issues.append("Base URL is required")

        if not config.base_url.startswith(("http://", "https://")):
            issues.append("Base URL must start with http:// or https://")

        if config.rate_limit_requests <= 0:
            issues.append("Rate limit requests must be positive")

    return issues
