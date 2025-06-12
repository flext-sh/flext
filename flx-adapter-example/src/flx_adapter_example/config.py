"""FLX Adapter Configuration - Pydantic-based configuration management.

This module provides configuration management for the FLX adapter example,
using pydantic-settings for environment variable integration and validation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class FlxAdapterConfig(BaseSettings):
    """Configuration for FLX Adapter Example.

    This configuration supports loading from environment variables with
    the prefix 'FLX_ADAPTER_' and provides sensible defaults.

    Environment Variables:
        FLX_ADAPTER_NAME: Adapter name
        FLX_ADAPTER_VERSION: Adapter version
        FLX_ADAPTER_API_URL: Base URL for external API
        FLX_ADAPTER_API_KEY: API key for authentication
        FLX_ADAPTER_TIMEOUT_SECONDS: Request timeout in seconds
        FLX_ADAPTER_RETRY_ATTEMPTS: Number of retry attempts
        FLX_ADAPTER_RETRY_DELAY_SECONDS: Delay between retries
        FLX_ADAPTER_ENABLED: Whether adapter is enabled
        FLX_ADAPTER_DEBUG: Enable debug mode

    Example:
        ```python
        # Load from environment
        config = FlxAdapterConfig.from_env()

        # Create with explicit values
        config = FlxAdapterConfig(
            name="my-adapter",
            api_url="https://api.example.com",
            api_key="secret-key"
        )
        ```
    """

    model_config = SettingsConfigDict(
        env_prefix="FLX_ADAPTER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Basic adapter information
    name: str = Field(
        default="flx_adapter_example",
        description="Adapter name identifier"
    )
    version: str = Field(
        default="1.0.0",
        description="Adapter version"
    )

    # API configuration
    api_url: HttpUrl = Field(
        default="https://jsonplaceholder.typicode.com",
        description="Base URL for external API"
    )
    api_key: str | None = Field(
        default=None,
        description="API key for authentication"
    )

    # Connection settings
    timeout_seconds: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Request timeout in seconds"
    )
    retry_attempts: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retry attempts"
    )
    retry_delay_seconds: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Delay between retries in seconds"
    )

    # Adapter behavior
    enabled: bool = Field(
        default=True,
        description="Whether adapter is enabled"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    # Additional configuration
    extra_config: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional adapter-specific configuration"
    )

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate API URL format."""
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("API URL must start with http:// or https://")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate adapter name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Adapter name cannot be empty")
        return v.strip()

    @classmethod
    def from_env(cls) -> FlxAdapterConfig:
        """Create configuration from environment variables.

        Returns:
            Configuration instance loaded from environment

        Example:
            ```python
            config = FlxAdapterConfig.from_env()
            ```
        """
        return cls()

    def to_plugin_config(self) -> FlxPluginConfig:
        """Convert to FLX FlxPluginConfig format.

        Returns:
            FlxPluginConfig instance for FLX framework
        """
        from flx.plugins.base import FlxPluginConfig, FlxPluginMode

        return FlxPluginConfig(
            name=self.name,
            version=self.version,
            mode=FlxPluginMode.BIDIRECTIONAL,
            enabled=self.enabled,
            config={
                "api_url": str(self.api_url),
                "api_key": self.api_key,
                "timeout_seconds": self.timeout_seconds,
                "retry_attempts": self.retry_attempts,
                "retry_delay_seconds": self.retry_delay_seconds,
                "debug": self.debug,
                **self.extra_config,
            },
            timeout_seconds=self.timeout_seconds,
            retry_attempts=self.retry_attempts,
            retry_delay_seconds=self.retry_delay_seconds,
        )

    def get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{self.name}/{self.version}",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def model_dump_safe(self) -> dict[str, Any]:
        """Dump model data with sensitive information masked.

        Returns:
            Dictionary with sensitive data masked
        """
        data = self.model_dump()
        if data.get("api_key"):
            data["api_key"] = "***masked***"
        return data


class FlxPluginConfig(BaseModel):
    """Temporary FlxPluginConfig for standalone usage."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    version: str
    mode: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
