"""Oracle WMS target implementation with full Singer SDK functionality."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from singer_sdk import Target
from singer_sdk import typing as th

from target_oracle_wms.sinks_advanced import DynamicWMSSink


if TYPE_CHECKING:
    from singer_sdk.sinks import Sink


class TargetOracleWMS(Target):
    """Target for Oracle Warehouse Management System."""

    name = "target-oracle-wms"

    config_jsonschema = th.PropertiesList(
        # Core WMS API Configuration
        th.Property(
            "base_url",
            th.StringType,
            required=True,
            description="Base URL for Oracle WMS API",
            examples=["https://instance.wms.ocs.oraclecloud.com/tenant"],
        ),
        th.Property(
            "company_code",
            th.StringType,
            required=True,
            description="WMS company code",
        ),
        th.Property(
            "facility_code",
            th.StringType,
            required=True,
            description="WMS facility code",
        ),
        # Authentication
        th.Property(
            "auth_method",
            th.StringType,
            default="basic",
            allowed_values=["basic", "oauth2"],
            description="Authentication method",
        ),
        th.Property(
            "username",
            th.StringType,
            required=False,
            secret=True,
            description="Username for basic authentication",
        ),
        th.Property(
            "password",
            th.StringType,
            required=False,
            secret=True,
            description="Password for basic authentication",
        ),
        th.Property(
            "oauth_token_url",
            th.StringType,
            required=False,
            description="OAuth2 token endpoint URL",
        ),
        th.Property(
            "oauth_client_id",
            th.StringType,
            required=False,
            secret=True,
            description="OAuth2 client ID",
        ),
        th.Property(
            "oauth_client_secret",
            th.StringType,
            required=False,
            secret=True,
            description="OAuth2 client secret",
        ),
        th.Property(
            "oauth_scope",
            th.StringType,
            default="wms.write",
            description="OAuth2 scope",
        ),
        # Operation Configuration
        th.Property(
            "operation_mode",
            th.StringType,
            default="upsert",
            allowed_values=["create", "update", "upsert", "delete"],
            description="Default operation mode for records",
        ),
        th.Property(
            "batch_size",
            th.IntegerType,
            default=500,
            description="Batch size for API operations",
        ),
        th.Property(
            "max_parallel_requests",
            th.IntegerType,
            default=5,
            description="Maximum parallel API requests",
        ),
        # Data Validation
        th.Property(
            "validate_data",
            th.BooleanType,
            default=True,
            description="Validate data before sending to WMS",
        ),
        th.Property(
            "sanitize_data",
            th.BooleanType,
            default=True,
            description="Sanitize data for WMS compatibility",
        ),
        # Retry Configuration
        th.Property(
            "max_retries",
            th.IntegerType,
            default=3,
            description="Maximum retry attempts for failed requests",
        ),
        th.Property(
            "retry_delay",
            th.NumberType,
            default=1.0,
            description="Initial retry delay in seconds",
        ),
        th.Property(
            "backoff_factor",
            th.NumberType,
            default=2.0,
            description="Exponential backoff factor",
        ),
        # Advanced Features
        th.Property(
            "bulk_operations",
            th.ObjectType(
                th.Property(
                    "enabled",
                    th.BooleanType,
                    default=False,
                    description="Enable bulk API operations",
                ),
                th.Property(
                    "batch_size",
                    th.IntegerType,
                    default=1000,
                    description="Batch size for bulk operations",
                ),
            ),
            description="Bulk operations configuration",
        ),
        th.Property(
            "enable_transactions",
            th.BooleanType,
            default=False,
            description="Enable transaction support",
        ),
        th.Property(
            "entity_mapping",
            th.ObjectType(),
            description="Map stream names to WMS entity names",
        ),
        # Output Configuration
        th.Property(
            "output_path",
            th.StringType,
            default="./output",
            description="Path for output files",
        ),
        th.Property(
            "output_format",
            th.StringType,
            default="json",
            allowed_values=["json", "csv", "parquet"],
            description="Output format for results",
        ),
        th.Property(
            "write_results",
            th.BooleanType,
            default=True,
            description="Write operation results to files",
        ),
        # Performance
        th.Property(
            "timeout",
            th.IntegerType,
            default=300,
            description="Request timeout in seconds",
        ),
        th.Property(
            "connection_pool_size",
            th.IntegerType,
            default=20,
            description="HTTP connection pool size",
        ),
        # Monitoring
        th.Property(
            "enable_monitoring",
            th.BooleanType,
            default=False,
            description="Enable performance monitoring",
        ),
        th.Property(
            "log_api_calls",
            th.BooleanType,
            default=False,
            description="Log all API calls for debugging",
        ),
    ).to_dict()

    def get_sink_class(self, stream_name: str) -> type[Sink]:
        """Get sink class for a stream."""
        # Always use dynamic sink that adapts to any WMS entity
        return DynamicWMSSink

    @property
    def max_parallelism(self) -> int:
        """Get max parallel sinks."""
        # Use configured value or default
        return self.config.get("max_parallel_requests", 5)

    def validate_config(self) -> None:
        """Validate configuration."""
        super().validate_config()

        # Validate authentication
        auth_method = self.config.get("auth_method", "basic")
        if auth_method == "basic":
            if not self.config.get("username") or not self.config.get("password"):
                msg = "Basic auth requires username and password"
                raise ValueError(msg)
        elif auth_method == "oauth2":
            required = ["oauth_token_url", "oauth_client_id", "oauth_client_secret"]
            if not all(self.config.get(field) for field in required):
                msg = f"OAuth2 requires: {', '.join(required)}"
                raise ValueError(msg)

        # Test authentication if configured
        if self.config.get("test_connection", True):
            from .auth import WMSAuthenticator

            auth = WMSAuthenticator(self.config)
            if not auth.test_authentication(self.config["base_url"]):
                msg = "Authentication test failed"
                raise ValueError(msg)

    def _write_state_message(self, state: dict[str, Any]) -> None:
        """Write state message to stdout."""
        super()._write_state_message(state)


def main() -> None:
    """Run target."""
    if len(sys.argv) == 1 and sys.stdin.isatty():
        # Show help when no input
        sys.exit(1)

    TargetOracleWMS.cli()


if __name__ == "__main__":
    main()
