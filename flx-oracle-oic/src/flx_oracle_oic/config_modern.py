"""Modern Oracle Integration Cloud configuration using FLX 0.4.0 hierarchical patterns.

This configuration implementation uses the modern FLX hierarchical configuration
system with environment variable support, profile management, and enhanced validation.
"""

from typing import TYPE_CHECKING, Any, Self

from pydantic import Field, SecretStr, field_validator, model_validator

if TYPE_CHECKING:
    from flx.infra.config.hierarchical import ConfigManager
else:
    # Runtime: Use dummy base class to avoid lazy_import as base class
    class ConfigManager:
        """Dummy base class for runtime."""

        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)


from .constants import (
    DEFAULT_API_VERSION,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RATE_LIMIT_CALLS,
    DEFAULT_RATE_LIMIT_PERIOD,
    DEFAULT_TIMEOUT,
    JWT_SCOPE_DEFAULT,
    OIC_API_BASE,
)


class OracleOicConfigModern(ConfigManager):
    """Modern Oracle Integration Cloud configuration with hierarchical support.

    This configuration class leverages FLX 0.4.0's hierarchical configuration
    system providing:
        - Environment variable override support
        - Profile-based configuration (dev, staging, prod)
        - Deep configuration merging
        - Enhanced validation with detailed error messages
        - Secure secret handling
        - Type-safe configuration access

    Configuration Sources (in order of precedence):
        1. Environment variables (highest)
        2. Profile-specific config files (config.{profile}.yaml)
        3. Base config file (config.yaml)
        4. Default values (lowest)

    Environment Variables:
        All configuration fields can be overridden using environment variables
        with the prefix OIC_ (configurable). For example:
        - OIC_INSTANCE_ID
        - OIC_CLIENT_ID
        - OIC_CLIENT_SECRET
        - OIC_TIMEOUT

    Configuration Profiles:
        - default: Basic configuration
        - development: Development environment settings
        - staging: Staging environment settings
        - production: Production environment settings
        - test: Test environment settings
    """

    # Set OIC-specific environment prefix
    env_prefix: str = Field(default="OIC_", description="Environment variable prefix")

    # OIC Instance Configuration
    instance_id: str = Field(
        default="test-instance",
        min_length=1,
        description="Oracle Integration Cloud instance identifier",
    )

    region: str = Field(
        default="us-ashburn-1",
        min_length=1,
        description="Oracle Cloud Infrastructure region",
    )

    # Authentication Configuration
    client_id: str = Field(
        default="test-client-id",
        min_length=1,
        description="OAuth2 client identifier",
    )

    client_secret: SecretStr = Field(
        default=SecretStr("test-client-secret"),
        description="OAuth2 client secret (secure)",
    )

    client_aud: str = Field(
        default="",
        description="IDCS client audience URL for scope construction",
    )

    scope: str = Field(
        default=JWT_SCOPE_DEFAULT,
        description="OAuth2 scope for API access",
    )

    idcs_url: str = Field(
        default="",
        description="Oracle Identity Cloud Service URL for authentication",
    )

    # JWT Authentication (alternative to OAuth2)
    jwt_private_key: SecretStr | None = Field(
        default=None,
        description="JWT private key for service account authentication",
    )

    jwt_key_id: str | None = Field(default=None, description="JWT key identifier")

    jwt_issuer: str | None = Field(default=None, description="JWT issuer claim")

    jwt_audience: str | None = Field(default=None, description="JWT audience claim")

    # API Configuration
    api_version: str = Field(default=DEFAULT_API_VERSION, description="OIC API version")

    base_path: str = Field(default=OIC_API_BASE, description="API base path")

    timeout: float = Field(
        default=DEFAULT_TIMEOUT,
        gt=0,
        le=600,
        description="HTTP request timeout in seconds",
    )

    max_retries: int = Field(
        default=DEFAULT_MAX_RETRIES,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    # Rate Limiting Configuration
    rate_limit_calls: int = Field(
        default=DEFAULT_RATE_LIMIT_CALLS,
        gt=0,
        le=10000,
        description="Maximum calls per rate limit period",
    )

    rate_limit_period: int = Field(
        default=DEFAULT_RATE_LIMIT_PERIOD,
        gt=0,
        le=3600,
        description="Rate limit period in seconds",
    )

    # Pagination Configuration
    page_size: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Default page size for paginated responses",
    )

    max_page_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum allowed page size",
    )

    # Feature Flags
    enable_monitoring: bool = Field(
        default=True,
        description="Enable monitoring and health checks",
    )

    enable_caching: bool = Field(default=True, description="Enable response caching")

    enable_metrics: bool = Field(
        default=True,
        description="Enable operation metrics collection",
    )

    debug_mode: bool = Field(
        default=False,
        description="Enable debug logging and additional information",
    )

    # SSL/TLS Configuration
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    ssl_cert_path: str | None = Field(
        default=None,
        description="Path to custom SSL certificate",
    )

    # Connection Pool Configuration
    max_connections: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of HTTP connections",
    )

    keep_alive: bool = Field(default=True, description="Enable HTTP keep-alive")

    # Validation methods

    @field_validator("region")
    @classmethod
    def validate_region_format(cls, v: str) -> str:
        """Validate Oracle Cloud Infrastructure region format."""
        valid_prefixes = ("us-", "eu-", "ap-", "ca-", "uk-", "me-", "sa-", "il-")
        if not v.startswith(valid_prefixes):
            msg = f"Invalid OCI region format. Must start with one of: {valid_prefixes}"
            raise ValueError(
                msg,
            )
        return v

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """Validate page size is reasonable."""
        if v > 1000:
            msg = "Page size cannot exceed 1000 for performance reasons"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_auth_configuration(self) -> Self:
        """Validate authentication configuration is complete."""
        has_oauth = (
            self.client_id != "test-client-id"
            and self.client_secret.get_secret_value() != "test-client-secret"
        )
        has_jwt = self.jwt_private_key is not None and self.jwt_key_id is not None

        if not has_oauth and not has_jwt:
            msg = (
                "Either OAuth2 credentials (client_id, client_secret) or "
                "JWT credentials (jwt_private_key, jwt_key_id) must be provided"
            )
            raise ValueError(
                msg,
            )

        return self

    @model_validator(mode="after")
    def validate_url_configuration(self) -> Self:
        """Validate URL configuration consistency."""
        if self.idcs_url and not self.idcs_url.startswith("https://"):
            msg = "IDCS URL must use HTTPS protocol"
            raise ValueError(msg)

        return self

    # Property methods for computed values

    @property
    def oauth_scope(self) -> str:
        """Build OAuth scope for OIC API access."""
        if not self.client_aud:
            return self.scope

        # Build scope with resource and API audience
        resource_aud = f"{self.client_aud}:443urn:opc:resource:consumer::all"
        api_aud = f"{self.client_aud}:443/ic/api/"
        return f"{resource_aud} {api_aud}"

    @property
    def base_url(self) -> str:
        """Construct base URL for OIC instance."""
        return f"https://design.integration.{self.region}.ocp.oraclecloud.com"

    @property
    def auth_url(self) -> str:
        """Construct OAuth token URL."""
        if self.idcs_url:
            return f"{self.idcs_url.rstrip('/')}/oauth2/v1/token"
        return f"https://{self.instance_id}-{self.region}.integration.ocp.oraclecloud.com/oauth2/v1/token"

    @property
    def monitoring_url(self) -> str:
        """Construct monitoring endpoint URL."""
        return f"{self.base_url}{self.base_path}/monitoring"

    @property
    def health_check_url(self) -> str:
        """Construct health check endpoint URL."""
        return f"{self.base_url}{self.base_path}/health"

    # Configuration export methods

    def get_headers(self) -> dict[str, str]:
        """Get default HTTP headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "flx_http_oracle_oic/0.4.0",
        }

        if self.debug_mode:
            headers["X-Debug-Mode"] = "true"

        return headers

    def to_adapter_config(self) -> dict[str, Any]:
        """Convert to adapter configuration format."""
        return {
            "instance_id": self.instance_id,
            "base_url": self.base_url,
            "base_path": self.base_path,
            "auth_url": self.auth_url,
            "client_id": self.client_id,
            "client_secret": self.client_secret.get_secret_value(),
            "scope": self.oauth_scope,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "rate_limit_calls": self.rate_limit_calls,
            "rate_limit_period": self.rate_limit_period,
            "headers": self.get_headers(),
            "verify_ssl": self.verify_ssl,
            "max_connections": self.max_connections,
            "keep_alive": self.keep_alive,
            "debug_mode": self.debug_mode,
        }

    def get_jwt_config(self) -> dict[str, Any] | None:
        """Get JWT authentication configuration if available."""
        if not self.jwt_private_key or not self.jwt_key_id:
            return None

        return {
            "private_key": self.jwt_private_key.get_secret_value(),
            "key_id": self.jwt_key_id,
            "issuer": self.jwt_issuer,
            "audience": self.jwt_audience or self.base_url,
            "scope": self.oauth_scope,
        }

    def get_oauth_config(self) -> dict[str, Any]:
        """Get OAuth2 authentication configuration."""
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret.get_secret_value(),
            "auth_url": self.auth_url,
            "scope": self.oauth_scope,
        }

    # Environment-specific configuration creation

    @classmethod
    def for_development(cls, **overrides: Any) -> Self:
        """Create development configuration with appropriate defaults."""
        defaults = {
            "profile": "development",
            "debug_mode": True,
            "enable_metrics": True,
            "timeout": 60.0,
            "max_retries": 5,
        }
        defaults.update(overrides)
        return cls(**defaults)

    @classmethod
    def for_production(cls, **overrides: Any) -> Self:
        """Create production configuration with appropriate defaults."""
        defaults = {
            "profile": "production",
            "debug_mode": False,
            "enable_metrics": True,
            "timeout": 30.0,
            "max_retries": 3,
            "verify_ssl": True,
        }
        defaults.update(overrides)
        return cls(**defaults)

    @classmethod
    def for_testing(cls, **overrides: Any) -> Self:
        """Create test configuration with appropriate defaults."""
        defaults = {
            "profile": "test",
            "debug_mode": True,
            "enable_metrics": False,
            "timeout": 10.0,
            "max_retries": 1,
            "verify_ssl": False,
        }
        defaults.update(overrides)
        return cls(**defaults)
