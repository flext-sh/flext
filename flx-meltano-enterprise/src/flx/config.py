"""
FLX Core Configuration using Pydantic Settings.

This module provides centralized configuration management for the FLX platform
using Pydantic Settings with full type safety and validation.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for FLX Core daemon."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="FLX_",
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = Field(default=False, description="Debug mode flag")

    # gRPC Configuration
    grpc_port: int = Field(
        default=50051, ge=1024, le=65535, description="gRPC server port"
    )
    grpc_max_workers: int = Field(
        default=10, ge=1, le=100, description="Max gRPC workers"
    )
    grpc_max_message_length: int = Field(
        default=100 * 1024 * 1024,  # 100MB
        description="Max message size in bytes",
    )

    # Meltano Configuration
    meltano_project_root: Path = Field(
        default_factory=Path.cwd,
        description="Root directory for Meltano projects",
    )
    meltano_environment: Optional[str] = Field(
        default=None,
        description="Meltano environment to use",
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql://flx:flx@localhost:5432/flx",
        description="PostgreSQL connection URL",
    )
    database_pool_size: int = Field(default=20, ge=1, le=100)
    database_max_overflow: int = Field(default=10, ge=0, le=50)
    database_pool_timeout: int = Field(default=30, ge=1, le=300)

    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_max_connections: int = Field(default=50, ge=10, le=200)
    redis_decode_responses: bool = Field(default=True)

    # Message Queue Configuration
    amqp_url: Optional[str] = Field(
        default="amqp://guest:guest@localhost:5672/",
        description="RabbitMQ connection URL",
    )
    amqp_heartbeat: int = Field(default=60, ge=0, le=3600)
    amqp_connection_attempts: int = Field(default=3, ge=1, le=10)
    amqp_retry_delay: int = Field(default=5, ge=1, le=60)

    # Monitoring Configuration
    metrics_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Prometheus metrics port",
    )
    tracing_enabled: bool = Field(
        default=True, description="Enable OpenTelemetry tracing"
    )
    tracing_endpoint: Optional[str] = Field(
        default="http://localhost:4317",
        description="OpenTelemetry collector endpoint",
    )
    tracing_service_name: str = Field(
        default="flx-core", description="Service name for tracing"
    )

    # Security Configuration
    jwt_secret: str = Field(
        default="dev-secret-key-change-in-production-please",
        description="JWT signing secret",
        min_length=32,
    )
    jwt_algorithm: str = Field(
        default="HS256", pattern="^(HS256|HS384|HS512|RS256|RS384|RS512)$"
    )
    jwt_expiration: int = Field(
        default=3600, ge=300, le=86400, description="JWT expiration in seconds"
    )
    jwt_refresh_expiration: int = Field(
        default=604800, ge=3600, le=2592000, description="Refresh token expiration"
    )

    # Feature Flags
    multi_tenancy_enabled: bool = Field(
        default=False, description="Enable multi-tenancy"
    )
    circuit_breaker_enabled: bool = Field(
        default=True, description="Enable circuit breaker pattern"
    )
    rate_limiting_enabled: bool = Field(
        default=True, description="Enable rate limiting"
    )

    # Circuit Breaker Configuration
    circuit_breaker_failure_threshold: int = Field(default=5, ge=1, le=100)
    circuit_breaker_recovery_timeout: int = Field(default=60, ge=10, le=600)
    circuit_breaker_expected_exception: Optional[str] = Field(default=None)

    # Rate Limiting Configuration
    rate_limit_requests: int = Field(default=1000, ge=1, le=100000)
    rate_limit_period: int = Field(default=3600, ge=60, le=86400)

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    log_format: str = Field(
        default="json",
        pattern="^(json|console)$",
    )
    log_file: Optional[Path] = Field(default=None, description="Log file path")

    # Object Storage Configuration
    s3_endpoint: Optional[str] = Field(default="http://localhost:9000")
    s3_access_key: Optional[str] = Field(default="minioREDACTED_LDAP_BIND_PASSWORD")
    s3_secret_key: Optional[str] = Field(default="minioREDACTED_LDAP_BIND_PASSWORD")
    s3_bucket: str = Field(default="flx-data")
    s3_use_ssl: bool = Field(default=False)

    # Email Configuration (for alerts)
    email_host: Optional[str] = Field(default=None)
    email_port: int = Field(default=587, ge=1, le=65535)
    email_user: Optional[str] = Field(default=None)
    email_password: Optional[str] = Field(default=None)
    email_use_tls: bool = Field(default=True)
    email_from: Optional[str] = Field(default="flx@example.com")

    # Slack Configuration (for alerts)
    slack_webhook_url: Optional[str] = Field(default=None)
    slack_channel: Optional[str] = Field(default="#flx-alerts")

    # Performance Configuration
    worker_processes: int = Field(default=4, ge=1, le=32)
    worker_threads: int = Field(default=2, ge=1, le=16)
    connection_pool_size: int = Field(default=100, ge=10, le=1000)

    @field_validator("meltano_project_root")
    @classmethod
    def validate_meltano_root(cls, v: Path) -> Path:
        """Ensure Meltano project root exists."""
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("log_file")
    @classmethod
    def validate_log_file(cls, v: Optional[Path]) -> Optional[Path]:
        """Ensure log directory exists if log file is specified."""
        if v and not v.parent.exists():
            v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() in ("production", "prod")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() in ("development", "dev")

    def get_database_url_with_pool(self) -> str:
        """Get database URL with pool parameters."""
        if "?" in self.database_url:
            separator = "&"
        else:
            separator = "?"

        pool_params = (
            f"pool_size={self.database_pool_size}"
            f"&max_overflow={self.database_max_overflow}"
            f"&pool_timeout={self.database_pool_timeout}"
        )

        return f"{self.database_url}{separator}{pool_params}"


# Global settings instance
settings = Settings()
