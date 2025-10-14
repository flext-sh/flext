"""FLEXT Tools Configuration - Pydantic 2.11+ BaseSettings with dependency_injector.

MANDATORY PATTERNS:
- Pydantic 2.11+ BaseSettings with dependency_injector integration
- ALL defaults from FlextCore.Constants (ZERO module-level constants)
- Centralized config classes with comprehensive validation logic
- FlextCore.Result for ALL operations (railway pattern)
- Sync-only operations (temporary requirement)
- NO environments, helpers, or production/homologation configurations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from typing import ClassVar, Self

from dependency_injector import providers
from flext_core import FlextCore
from pydantic import Field, SecretStr, computed_field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict


class FlextToolsConfig(FlextCore.Config):
    """FLEXT Tools Configuration - Pydantic 2.11+ configuration extending FlextCore.Config.

    MANDATORY PATTERNS:
    - Extends FlextCore.Config for validation and environment variable support
    - dependency_injector integration for service injection
    - ALL defaults from FlextCore.Constants (ZERO module-level constants)
    - Centralized configuration with comprehensive validation logic
    - FlextCore.Result for ALL operations (railway pattern)
    - Sync-only operations (temporary requirement)
    - NO environments, helpers, or production/homologation configurations

    Core Features:
    - Environment variable support with FLEXT_ prefix
    - Pydantic validation with FlextCore.Constants defaults
    - Dependency injection provider integration
    - Computed fields for derived configuration
    - Railway pattern error handling

    Usage:
        config = FlextToolsConfig()
        # Environment variables: FLEXT_DEBUG=true, FLEXT_LOG_LEVEL=DEBUG

        # Direct access
        level = config.log_level
        timeout = config.timeout_seconds

        # Callable access
        level = config("log_level")

        # DI integration
        provider = FlextToolsConfig.get_di_config_provider()
    """

    # Singleton pattern - per-class instances
    _instances: ClassVar[dict[type, FlextToolsConfig]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    # Pydantic 2.11+ SettingsConfigDict configuration
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix=FlextCore.Constants.Platform.ENV_PREFIX,
        env_file=FlextCore.Constants.Platform.ENV_FILE_DEFAULT,
        env_file_encoding=FlextCore.Constants.Mixins.DEFAULT_ENCODING,
        env_nested_delimiter=FlextCore.Constants.Platform.ENV_NESTED_DELIMITER,
        extra="ignore",
        use_enum_values=True,
        frozen=False,
        arbitrary_types_allowed=True,
        validate_return=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        str_to_lower=False,
        json_schema_extra={
            "title": "FLEXT Tools Configuration",
            "description": "Enterprise FLEXT tools configuration",
        },
    )

    # Core application configuration - ALL defaults from FlextCore.Constants
    app_name: str = Field(
        default=f"{FlextCore.Constants.NAME} Tools Application",
        description="Application name",
    )

    version: str = Field(
        default=FlextCore.Constants.VERSION,
        description="Application version",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    trace: bool = Field(
        default=False,
        description="Enable trace mode",
    )

    # Logging configuration - ALL from FlextCore.Constants
    log_level: str = Field(
        default=FlextCore.Constants.Logging.DEFAULT_LEVEL,
        description="Logging level",
    )

    json_output: bool = Field(
        default=FlextCore.Constants.Logging.JSON_OUTPUT_DEFAULT,
        description="Use JSON output format",
    )

    include_source: bool = Field(
        default=FlextCore.Constants.Logging.INCLUDE_SOURCE,
        description="Include source code location",
    )

    structured_output: bool = Field(
        default=FlextCore.Constants.Logging.STRUCTURED_OUTPUT,
        description="Use structured logging format",
    )

    # Database configuration
    database_url: str | None = Field(
        default=None,
        description="Database connection URL",
    )

    database_pool_size: int = Field(
        default=FlextCore.Constants.Performance.DEFAULT_DB_POOL_SIZE,
        ge=FlextCore.Constants.Performance.MIN_DB_POOL_SIZE,
        le=FlextCore.Constants.Performance.MAX_DB_POOL_SIZE,
        description="Database connection pool size",
    )

    # Cache configuration - ALL from FlextCore.Constants
    cache_ttl: int = Field(
        default=FlextCore.Constants.Defaults.TIMEOUT * 10,  # 300 seconds
        ge=0,
        description="Cache TTL in seconds",
    )

    cache_max_size: int = Field(
        default=FlextCore.Constants.Defaults.PAGE_SIZE * 10,  # 1000
        ge=0,
        description="Maximum cache size",
    )

    # Security configuration
    secret_key: SecretStr | None = Field(
        default=None,
        description="Secret key for security operations",
    )

    api_key: SecretStr | None = Field(
        default=None,
        description="API key for external service authentication",
    )

    # Tools-specific configuration - ALL from FlextCore.Constants where possible
    max_retry_attempts: int = Field(
        default=FlextCore.Constants.Reliability.MAX_RETRY_ATTEMPTS,
        ge=0,
        le=FlextCore.Constants.Performance.MAX_RETRY_ATTEMPTS_LIMIT,
        description="Maximum retry attempts",
    )

    timeout_seconds: int = Field(
        default=FlextCore.Constants.Defaults.TIMEOUT,
        ge=1,
        le=FlextCore.Constants.Performance.DEFAULT_TIMEOUT_LIMIT,
        description="Default timeout in seconds",
    )

    # Feature flags
    enable_caching: bool = Field(
        default=True,
        description="Enable caching functionality",
    )

    enable_metrics: bool = Field(
        default=False,
        description="Enable metrics collection",
    )

    enable_tracing: bool = Field(
        default=False,
        description="Enable distributed tracing",
    )

    # Tools-specific feature flags
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

    # Container configuration - from FlextCore.Constants
    max_workers: int = Field(
        default=FlextCore.Constants.Container.MAX_WORKERS,
        ge=1,
        le=50,
        description="Maximum number of workers",
    )

    # Validation configuration - from FlextCore.Constants
    max_name_length: int = Field(
        default=FlextCore.Constants.Validation.MAX_NAME_LENGTH,
        ge=1,
        le=500,
        description="Maximum allowed name length",
    )

    min_phone_digits: int = Field(
        default=FlextCore.Constants.Validation.MIN_PHONE_DIGITS,
        ge=7,
        le=15,
        description="Minimum phone number digits",
    )

    # Direct access method - simplified
    def __call__(self, key: str) -> FlextCore.Types.ConfigValue:
        """Direct value access: config('log_level')."""
        if not hasattr(self, key):
            msg = f"Configuration key '{key}' not found"
            raise KeyError(msg)
        return getattr(self, key)

    # Validation methods
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level using FlextCore.Constants."""
        v_upper = v.upper()
        if v_upper not in FlextCore.Constants.Logging.VALID_LEVELS:
            error_msg = f"Invalid log level: {v}. Must be one of: {', '.join(FlextCore.Constants.Logging.VALID_LEVELS)}"
            raise FlextCore.Exceptions.ValidationError(error_msg)
        return v_upper

    @model_validator(mode="after")
    def validate_debug_trace_consistency(self) -> Self:
        """Validate debug and trace mode consistency."""
        if self.trace and not self.debug:
            error_msg = "Trace mode requires debug mode to be enabled"
            raise FlextCore.Exceptions.ValidationError(error_msg)
        return self

    # Dependency injection integration
    _di_config_provider: ClassVar[providers.Configuration | None] = None
    _di_provider_lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_di_config_provider(cls) -> providers.Configuration:
        """Get dependency-injector Configuration provider."""
        if cls._di_config_provider is None:
            with cls._di_provider_lock:
                if cls._di_config_provider is None:
                    cls._di_config_provider = providers.Configuration()
                    instance = cls._instances.get(cls)
                    if instance is not None:
                        config_dict = instance.model_dump()
                        cls._di_config_provider.from_dict(config_dict)
        return cls._di_config_provider

    @classmethod
    def get_global_instance(cls) -> Self:
        """Get or create global singleton instance."""
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = cls()
                    cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset global singleton instance."""
        with cls._lock:
            cls._instances.pop(cls, None)

    def validate_runtime_requirements(self) -> FlextCore.Result[None]:
        """Validate configuration meets runtime requirements."""
        try:
            self.validate_log_level(self.log_level)
        except FlextCore.Exceptions.ValidationError as e:
            return FlextCore.Result[None].fail(str(e))

        if self.trace and not self.debug:
            return FlextCore.Result[None].fail(
                "Trace mode requires debug mode to be enabled"
            )

        return FlextCore.Result[None].ok(None)

    def validate_business_rules(self) -> FlextCore.Result[None]:
        """Validate business rules for configuration consistency."""
        return FlextCore.Result[None].ok(None)

    # Computed fields
    @computed_field
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug or self.trace


__all__ = [
    "FlextToolsConfig",
]
