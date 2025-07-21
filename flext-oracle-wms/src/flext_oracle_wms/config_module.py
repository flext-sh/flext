"""Enterprise configuration management for Oracle WMS integrations.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

This module provides unified configuration management for all Oracle WMS operations,
eliminating duplication between tap and target implementations.
Implements flext-core unified configuration standards with composition mixins.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydantic import HttpUrl
else:
    HttpUrl = str

# Import unified configuration system from flext-core
from flext_core.config.unified_config import (
    BaseConfigMixin,
    LoggingConfigMixin,
    PerformanceConfigMixin,
    WMSConfigMixin,
)
from flext_core.domain.constants import ConfigDefaults
from flext_core.domain.shared_types import (
    BatchSize,
    Environment,
    Password,
    PositiveInt,
    RetryCount,
    RetryDelay,
    TimeoutSeconds,
    Username,
    Version,
)
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Oracle WMS specific types using unified core types
type WMSAPIVersion = str
type WMSPageSize = BatchSize  # Reuse BatchSize for page size
type WMSRateLimit = PositiveInt
type WMSRetryAttempts = RetryCount
type WMSRetryDelay = RetryDelay
type WMSTimeout = TimeoutSeconds


class OracleWMSConfig(
    BaseConfigMixin,
    LoggingConfigMixin,
    PerformanceConfigMixin,
    WMSConfigMixin,
    BaseSettings,
):
    """Enterprise Oracle WMS configuration using unified composition mixins.

    This configuration eliminates duplication by composing standardized mixins
    from flext-core while adding Oracle WMS-specific fields. Uses modern Python 3.13
    patterns and Pydantic v2 with field composition.
    """

    model_config = SettingsConfigDict(
        env_prefix=ConfigDefaults.ENV_PREFIX + "ORACLE_WMS_",
        env_file=".env",
        env_file_encoding=ConfigDefaults.DEFAULT_ENCODING,
        env_nested_delimiter=ConfigDefaults.ENV_DELIMITER,
        case_sensitive=False,
        extra="ignore",  # Allow extra fields in .env
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # === Oracle WMS API Configuration (additional to WMSConfigMixin) ===
    base_url: HttpUrl = Field(
        ...,
        description="Oracle WMS base URL (e.g., https://ta29.wms.ocs.oraclecloud.com/raizen_test)",
    )
    api_version: WMSAPIVersion = Field(
        default="v10",
        description="Oracle WMS API version",
    )
    username: Username = Field(..., description="Oracle WMS API username")
    password: Password = Field(..., description="Oracle WMS API password")

    # === WMS Rate Limiting (additional to PerformanceConfigMixin) ===
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable WMS API rate limiting",
    )
    max_requests_per_minute: WMSRateLimit = Field(
        default=60,
        description="Max WMS requests per minute",
    )
    min_request_delay: WMSRetryDelay = Field(
        default=0.1,
        description="Minimum delay between WMS requests",
    )

    # === Security Configuration ===
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ssl_cert_path: Path | None = Field(
        default=None,
        description="Path to SSL certificate file",
    )

    # === Observability (additional to LoggingConfigMixin) ===
    enable_request_logging: bool = Field(
        default=False,
        description="Log detailed API request/response information",
    )
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")

    # === Discovery Configuration ===
    auto_discover: bool = Field(
        default=True,
        description="Enable automatic schema discovery",
    )
    include_metadata: bool = Field(
        default=True,
        description="Include metadata in responses",
    )

    # === Connection Pool Configuration (additional to PerformanceConfigMixin) ===
    pool_size: PositiveInt = Field(
        default=5,
        description="HTTP connection pool size",
    )
    pool_timeout: TimeoutSeconds = Field(
        default=30.0,
        description="Connection pool timeout",
    )

    # === Version Information ===
    version: Version = Field(default="1.0.0", description="Client version")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate Oracle WMS base URL format."""
        url_str = str(v)
        if not url_str.startswith(("http://", "https://")):
            msg = f"Invalid Oracle WMS base URL: {url_str} (must start with http:// or https://)"
            raise ValueError(msg)

        # Validate Oracle WMS URL pattern
        if ".wms.ocs.oraclecloud.com" not in url_str:
            # Allow for development/testing URLs
            if not any(
                env in url_str for env in ["localhost", "test", "dev", "staging"]
            ):
                msg = f"Invalid Oracle WMS base URL: {url_str} (must contain .wms.ocs.oraclecloud.com or be a dev/test URL)"
                raise ValueError(msg)

        return v

    # Note: log_level validation is now handled by LoggingConfigMixin

    @property
    def api_headers(self) -> dict[str, str]:
        """Generate standard API headers for Oracle WMS requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"flext-oracle-wms/{self.version}",
        }

    @property
    def connection_config(self) -> dict[str, Any]:
        """Generate connection configuration for HTTP client."""
        return {
            "base_url": str(self.base_url),
            "timeout": self.timeout_seconds,  # Using composition mixin field
            "verify": self.verify_ssl,
            "headers": self.api_headers,
        }

    @property
    def wms_endpoint_base(self) -> str:
        """Get the WMS API endpoint base path."""
        return f"/wms/lgfapi/{self.api_version}/entity/"

    def get_entity_endpoint(self, entity_name: str) -> str:
        """Get the full endpoint URL for a specific entity."""
        return f"{self.wms_endpoint_base}{entity_name}"

    def get_entity_params(self, **additional_params: Any) -> dict[str, Any]:
        """Generate standard entity query parameters."""
        params = {
            "page_size": self.batch_size,  # Using composition mixin field
        }
        params.update(additional_params)
        return params

    @classmethod
    def from_env_file(cls, env_file: str | Path = ".env") -> OracleWMSConfig:
        """Create configuration from environment file."""
        return cls(_env_file=env_file)

    @classmethod
    def for_testing(cls) -> OracleWMSConfig:
        """Create configuration optimized for testing."""
        return cls(
            project_name="flext-oracle-wms-test",
            environment=Environment.TEST,
            base_url="https://test.example.com",  # type: ignore[arg-type]
            username="test_user",
            password="test_password",
            batch_size=10,  # Using composition mixin field
            timeout_seconds=5.0,  # Using composition mixin field
            max_retries=1,  # Using composition mixin field
            enable_request_logging=True,
            verify_ssl=False,
        )


def load_config() -> OracleWMSConfig:
    """Load Oracle WMS configuration from environment.

    This function provides a convenient way to load configuration
    with automatic environment file detection.
    """
    # Try to find .env file in current directory or parent directories
    env_file = None
    current_dir = Path.cwd()

    for _ in range(5):  # Search up to 5 levels up
        potential_env = Path(current_dir) / ".env"
        if Path(potential_env).exists():
            env_file = potential_env
            break
        current_dir = Path(current_dir).parent

    if env_file:
        return OracleWMSConfig(_env_file=env_file)
    return OracleWMSConfig()


# Rebuild the model to ensure all types are properly resolved
OracleWMSConfig.model_rebuild()
