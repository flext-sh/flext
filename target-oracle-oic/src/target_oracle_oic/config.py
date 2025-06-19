"""Configuration schema for Oracle Integration Cloud Target."""

from __future__ import annotations

from typing import Any

from singer_sdk import typing as th


class TargetOracleOICConfig:
    """Configuration for Oracle Integration Cloud Target."""

    @staticmethod
    def model_json_schema() -> dict[str, Any]:
        """Return the JSON schema for the target configuration."""
        properties = th.PropertiesList(
            # Core OIC instance configuration
            th.Property(
                "base_url",
                th.StringType,
                required=True,
                description="OIC instance base URL (e.g., https://myinstance-region.integration.ocp.oraclecloud.com)",
            ),
            # OAuth2 IDCS authentication (required)
            th.Property(
                "oauth_client_id",
                th.StringType,
                required=True,
                description="OAuth2 client ID from IDCS application",
            ),
            th.Property(
                "oauth_client_secret",
                th.StringType,
                required=True,
                secret=True,
                description="OAuth2 client secret from IDCS application",
            ),
            th.Property(
                "oauth_token_url",
                th.StringType,
                required=True,
                description="IDCS token endpoint URL",
            ),
            th.Property(
                "oauth_client_aud",
                th.StringType,
                description="IDCS client audience URL for scope building",
            ),
            # Target-specific configuration
            th.Property(
                "import_mode",
                th.StringType,
                default="create_or_update",
                description=(
                    "Import mode: 'create_only', 'update_only', or 'create_or_update'"
                ),
            ),
            th.Property(
                "activate_integrations",
                th.BooleanType,
                default=False,
                description="Automatically activate integrations after import",
            ),
            th.Property(
                "validate_connections",
                th.BooleanType,
                default=True,
                description="Validate connections before creating/updating",
            ),
            th.Property(
                "archive_directory",
                th.StringType,
                description="Directory to read integration archives from",
            ),
            # Request configuration
            th.Property(
                "request_timeout",
                th.IntegerType,
                default=30,
                description="Request timeout in seconds",
            ),
            th.Property(
                "max_retries",
                th.IntegerType,
                default=3,
                description="Maximum number of retries for failed requests",
            ),
            # Stream control
            th.Property(
                "disable_collection",
                th.BooleanType,
                default=False,
                description="Disable collection of result IDs after operations",
            ),
        )
        return properties.to_dict()
