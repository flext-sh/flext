"""Configuration for Oracle Integration Cloud client with zero redundancy."""

from typing import Any

from flx.infra.config.base import ConfigManager
from pydantic import Field, SecretStr, field_validator

from .constants import (
    DEFAULT_API_VERSION,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RATE_LIMIT_CALLS,
    DEFAULT_RATE_LIMIT_PERIOD,
    DEFAULT_TIMEOUT,
    JWT_SCOPE_DEFAULT,
    OIC_API_BASE,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_INSTANCE_ID,
    TEST_REGION_ASHBURN,
)


class OracleOicConfig(ConfigManager):
    """Oracle Integration Cloud configuration using FLX config base."""

    # OIC Instance Configuration
    instance_id: str = Field(..., min_length=1, description="OIC Instance ID")
    region: str = Field(..., min_length=1, description="OIC Region")

    # Authentication Configuration
    client_id: str = Field(..., min_length=1, description="OAuth Client ID")
    client_secret: SecretStr = Field(..., description="OAuth Client Secret")
    client_aud: str = Field(..., description="IDCS Client Audience URL")
    scope: str = Field(default=JWT_SCOPE_DEFAULT, description="OAuth Scope")
    idcs_url: str = Field(..., description="IDCS URL for authentication")

    # API Configuration
    api_version: str = Field(default=DEFAULT_API_VERSION)
    base_path: str = Field(default=OIC_API_BASE)
    timeout: float = Field(default=DEFAULT_TIMEOUT, gt=0)
    max_retries: int = Field(default=DEFAULT_MAX_RETRIES, ge=0)

    # Rate Limiting
    rate_limit_calls: int = Field(default=DEFAULT_RATE_LIMIT_CALLS, gt=0)
    rate_limit_period: int = Field(default=DEFAULT_RATE_LIMIT_PERIOD, gt=0)

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
        """Build OAuth scope like bash script using client_aud."""
        if not self.client_aud:
            return self.scope  # Fallback to simple scope

        # Build scope like bash script:
        # "${IDCS_CLIENT_AUD}:443urn:opc:resource:consumer::all ${IDCS_CLIENT_AUD}:443/ic/api/"
        resource_aud = f"{self.client_aud}:443urn:opc:resource:consumer::all"
        api_aud = f"{self.client_aud}:443/ic/api/"
        return f"{resource_aud} {api_aud}"

    @property
    def base_url(self) -> str:
        """Construct base URL for OIC instance."""
        # Use design.integration format that matches the working bash script
        return f"https://design.integration.{self.region}.ocp.oraclecloud.com"

    @property
    def oauth_url(self) -> str:
        """Construct OAuth token URL."""
        # Use IDCS URL if provided, otherwise fall back to default format
        if self.idcs_url:
            return f"{self.idcs_url.rstrip('/')}/oauth2/v1/token"
        return f"https://{self.instance_id}-{self.region}.integration.ocp.oraclecloud.com/oauth2/v1/token"

    def get_headers(self) -> dict[str, str]:
        """Get default HTTP headers."""
        from .constants import ACCEPT, APPLICATION_JSON, CONTENT_TYPE

        return {
            CONTENT_TYPE: APPLICATION_JSON,
            ACCEPT: APPLICATION_JSON,
        }

    def to_adapter_config(self) -> dict[str, Any]:
        """Convert to adapter configuration format."""
        import os

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
            # HTTP client specific settings from environment
            "verify_ssl": os.getenv("HTTP_VERIFY_SSL", "true").lower() == "true",
            "user_agent": os.getenv("HTTP_USER_AGENT", "FLX-OIC-HTTP-Client/1.0"),
            "buffer_size_bytes": int(os.getenv("HTTP_BUFFER_SIZE_BYTES", "8192")),
            "keepalive_timeout_seconds": float(
                os.getenv("HTTP_KEEPALIVE_TIMEOUT_SECONDS", "30.0"),
            ),
        }

    @classmethod
    def from_env(cls, prefix: str = "OIC_") -> "OracleOicConfig":
        """Create configuration from environment variables with automatic .env loading."""
        import os

        # Try to load .env file automatically
        cls._load_dotenv()

        # Map IDCS variables to expected format for backward compatibility
        cls._map_idcs_variables()

        return cls(
            instance_id=os.getenv(f"{prefix}INSTANCE_ID", TEST_INSTANCE_ID),
            region=os.getenv(f"{prefix}REGION", TEST_REGION_ASHBURN),
            client_id=os.getenv(f"{prefix}CLIENT_ID", TEST_CLIENT_ID),
            client_secret=SecretStr(
                os.getenv(f"{prefix}CLIENT_SECRET", TEST_CLIENT_SECRET),
            ),
            client_aud=os.getenv(f"{prefix}CLIENT_AUD", ""),
            scope=os.getenv(f"{prefix}SCOPE", JWT_SCOPE_DEFAULT),
            idcs_url=os.getenv(f"{prefix}IDCS_URL", ""),
            api_version=os.getenv(f"{prefix}API_VERSION", DEFAULT_API_VERSION),
            base_path=os.getenv(f"{prefix}BASE_PATH", OIC_API_BASE),
            timeout=float(os.getenv(f"{prefix}TIMEOUT", str(DEFAULT_TIMEOUT))),
            max_retries=int(
                os.getenv(f"{prefix}MAX_RETRIES", str(DEFAULT_MAX_RETRIES)),
            ),
            rate_limit_calls=int(
                os.getenv(f"{prefix}RATE_LIMIT_CALLS", str(DEFAULT_RATE_LIMIT_CALLS)),
            ),
            rate_limit_period=int(
                os.getenv(f"{prefix}RATE_LIMIT_PERIOD", str(DEFAULT_RATE_LIMIT_PERIOD)),
            ),
            page_size=int(os.getenv(f"{prefix}PAGE_SIZE", "50")),
            enable_monitoring=os.getenv(f"{prefix}ENABLE_MONITORING", "true").lower()
            == "true",
            enable_caching=os.getenv(f"{prefix}ENABLE_CACHING", "true").lower()
            == "true",
            debug_mode=os.getenv(f"{prefix}DEBUG_MODE", "false").lower() == "true",
        )

    @staticmethod
    def _load_dotenv() -> None:
        """Load .env file automatically from project root."""
        import os
        from pathlib import Path

        # Find .env file starting from current directory and going up
        current_path = Path.cwd()
        for path in [current_path, *list(current_path.parents)]:
            env_file = path / ".env"
            if env_file.exists():
                try:
                    with env_file.open(encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                key, value = line.split("=", 1)
                                # Only set if not already in environment
                                if key.strip() not in os.environ:
                                    os.environ[key.strip()] = value.strip()
                    break
                except Exception:
                    # Silently continue if file can't be read
                    continue

    @staticmethod
    def _map_idcs_variables() -> None:
        """Map IDCS variables to expected OIC format for backward compatibility."""
        import os

        # Mapping of IDCS variables to OIC variables
        mappings = {
            "OIC_IDCS_CLIENT_ID": "OIC_CLIENT_ID",
            "OIC_IDCS_CLIENT_SECRET": "OIC_CLIENT_SECRET",
            "OIC_IDCS_CLIENT_AUD": "OIC_CLIENT_AUD",
        }

        for old_key, new_key in mappings.items():
            if old_key in os.environ and new_key not in os.environ:
                os.environ[new_key] = os.environ[old_key]
