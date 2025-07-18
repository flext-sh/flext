"""Enterprise configuration management for Oracle WMS integrations.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

This module provides unified configuration management for all Oracle WMS operations,
eliminating duplication between tap and target implementations.
Implements flext-core configuration standards.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Import flext-core components
from flext_core.config.base import BaseSettings
from flext_core.domain.constants import ConfigDefaults
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

if TYPE_CHECKING:
    from flext_core.domain.typedefs import (
        PositiveInt,
        TimeoutSeconds,
        WMSAPIVersion,
        WMSPageSize,
        WMSPassword,
        WMSRateLimit,
        WMSRetryAttempts,
        WMSRetryDelay,
        WMSTimeout,
        WMSUsername,
    )
    from pydantic import HttpUrl

# Import Oracle WMS specific types from flext-core


class OracleWMSConfig(BaseSettings):
    """Enterprise Oracle WMS configuration with environment variable support.

    This unified configuration eliminates duplication between tap and target
    implementations while providing enterprise-grade validation and security.
    Uses flext-core BaseSettings with standardized configuration patterns.
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

    # === Oracle WMS API Configuration ===
    base_url: HttpUrl = Field(
        ...,
        description="Oracle WMS base URL (e.g., https://ta29.wms.ocs.oraclecloud.com/raizen_test)",
    )
    api_version: WMSAPIVersion = Field(
        default="v10", description="Oracle WMS API version",
    )
    username: WMSUsername = Field(..., description="Oracle WMS API username")
    password: WMSPassword = Field(..., description="Oracle WMS API password")

    # === WMS Organization Configuration ===
    company_code: str = Field(
        default="*", description="WMS company code (* for all companies)",
    )
    facility_code: str = Field(
        default="*", description="WMS facility code (* for all facilities)",
    )

    # === Performance Configuration using flext-core WMS types ===
    page_size: WMSPageSize = Field(
        default=ConfigDefaults.DEFAULT_PAGE_SIZE,
        description="Number of records per API request",
    )
    timeout: WMSTimeout = Field(
        default=ConfigDefaults.DEFAULT_HTTP_TIMEOUT,
        description="API request timeout in seconds",
    )
    max_retries: WMSRetryAttempts = Field(
        default=ConfigDefaults.DEFAULT_HTTP_RETRIES,
        description="Maximum number of retry attempts",
    )
    retry_delay: WMSRetryDelay = Field(
        default=1.0,
        description="Base delay between retries in seconds",
    )

    # === WMS Rate Limiting ===
    enable_rate_limiting: bool = Field(
        default=True, description="Enable WMS API rate limiting",
    )
    max_requests_per_minute: WMSRateLimit = Field(
        default=60, description="Max WMS requests per minute",
    )
    min_request_delay: WMSRetryDelay = Field(
        default=0.1, description="Minimum delay between WMS requests",
    )

    # === Security Configuration ===
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ssl_cert_path: Path | None = Field(
        default=None, description="Path to SSL certificate file",
    )

    # === Logging and Observability ===
    log_level: str = Field(default="INFO", description="Logging level")
    enable_request_logging: bool = Field(
        default=False, description="Log detailed API request/response information",
    )
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")

    # === Discovery Configuration ===
    auto_discover: bool = Field(
        default=True, description="Enable automatic schema discovery",
    )
    include_metadata: bool = Field(
        default=True, description="Include metadata in responses",
    )

    # === Connection Pool Configuration ===
    pool_size: PositiveInt = Field(
        default=5, description="HTTP connection pool size",
    )
    pool_timeout: TimeoutSeconds = Field(
        default=30.0, description="Connection pool timeout",
    )

    # === Version Information ===
    version: str = Field(default="1.0.0", description="Client version")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate Oracle WMS base URL format."""
        url_str = str(v)
        if not url_str.startswith(("http://", "https://")):
            msg = "Base URL must start with http:// or https://"
            raise ValueError(msg)

        # Validate Oracle WMS URL pattern
        if ".wms.ocs.oraclecloud.com" not in url_str:
            # Allow for development/testing URLs
            if not any(
                env in url_str for env in ["localhost", "test", "dev", "staging"]
            ):
                msg = "URL does not appear to be a valid Oracle WMS endpoint"
                raise ValueError(
                    msg,
                )

        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            msg = f"Log level must be one of: {', '.join(valid_levels)}"
            raise ValueError(msg)
        return v.upper()

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
            "timeout": self.timeout,
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
            "page_size": self.page_size,
        }
        params.update(additional_params)
        return params

    @classmethod
    def from_env_file(cls, env_file: str | Path = ".env") -> OracleWMSConfig:
        """Create configuration from environment file."""
        return cls(_env_file=env_file)  # type: ignore[call-arg]

    @classmethod
    def for_testing(cls) -> OracleWMSConfig:
        """Create configuration optimized for testing."""
        return cls(
            base_url="https://test.example.com",  # type: ignore[arg-type]
            username="test_user",
            password="test_password",
            page_size=10,
            timeout=5,
            max_retries=1,
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
    current_dir = os.getcwd()

    for _ in range(5):  # Search up to 5 levels up
        potential_env = Path(current_dir) / ".env"
        if Path(potential_env).exists():
            env_file = potential_env
            break
        current_dir = Path(current_dir).parent

    if env_file:
        return OracleWMSConfig(_env_file=env_file)  # type: ignore[call-arg]
    return OracleWMSConfig()


# Rebuild the model to ensure all types are properly resolved
OracleWMSConfig.model_rebuild()
