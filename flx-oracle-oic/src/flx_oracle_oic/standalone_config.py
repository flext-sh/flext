"""Standalone Oracle Integration Cloud configuration that works without FLX dependencies."""

from typing import Any

from pydantic import BaseModel, Field, SecretStr, field_validator


class StandaloneOracleOicConfig(BaseModel):
    """Standalone Oracle Integration Cloud configuration."""

    # OIC Instance Configuration
    instance_id: str = Field(default="test-instance", min_length=1)
    region: str = Field(default="us-ashburn-1", min_length=1)

    # Authentication Configuration
    client_id: str = Field(default="test_client", min_length=1)
    client_secret: SecretStr = Field(default=SecretStr("test_secret"))
    client_aud: str = Field(default="", description="IDCS Client Audience URL")
    scope: str = Field(default="urn:opc:resource:consumer::all")
    idcs_url: str = Field(default="", description="IDCS URL for authentication")

    # API Configuration
    api_version: str = Field(default="v1")
    base_path: str = Field(default="/ic/api/integration/v1")
    timeout: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)

    # Rate Limiting
    rate_limit_calls: int = Field(default=100, gt=0)
    rate_limit_period: int = Field(default=60, gt=0)

    # Pagination Configuration
    page_size: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Default page size for paginated responses",
    )

    # Feature Flags
    enable_monitoring: bool = Field(default=True)
    enable_caching: bool = Field(default=True)
    debug_mode: bool = Field(default=False)

    @field_validator("region")
    @classmethod
    def validate_region_format(cls, v: str) -> str:
        """Validate OCI region format."""
        if not v.startswith(("us-", "eu-", "ap-", "ca-", "uk-", "me-", "sa-")):
            msg = "Invalid OCI region format"
            raise ValueError(msg)
        return v

    @property
    def oauth_scope(self) -> str:
        """Build OAuth scope."""
        if not self.client_aud:
            return self.scope

        resource_aud = f"{self.client_aud}:443urn:opc:resource:consumer::all"
        api_aud = f"{self.client_aud}:443/ic/api/"
        return f"{resource_aud} {api_aud}"

    @property
    def base_url(self) -> str:
        """Construct base URL for OIC instance."""
        return (
            f"https://{self.instance_id}-{self.region}.integration.ocp.oraclecloud.com"
        )

    @property
    def oauth_url(self) -> str:
        """Construct OAuth token URL."""
        if self.idcs_url:
            return f"{self.idcs_url.rstrip('/')}/oauth2/v1/token"
        return f"https://{self.instance_id}-{self.region}.integration.ocp.oraclecloud.com/oauth2/v1/token"

    def get_headers(self) -> dict[str, str]:
        """Get default HTTP headers."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def to_adapter_config(self) -> dict[str, Any]:
        """Convert to adapter configuration format."""
        return {
            "base_url": self.base_url,
            "oauth_url": self.oauth_url,
            "client_id": self.client_id,
            "client_secret": self.client_secret.get_secret_value(),
            "scope": self.scope,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "rate_limit_calls": self.rate_limit_calls,
            "rate_limit_period": self.rate_limit_period,
            "headers": self.get_headers(),
            "page_size": self.page_size,
        }
