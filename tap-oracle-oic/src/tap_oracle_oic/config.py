"""Configuration schema for Oracle Integration Cloud TAP."""

from __future__ import annotations

from singer_sdk import typing as th


def get_config_schema() -> th.PropertiesList:
    """Get configuration schema for the TAP."""
    return th.PropertiesList(
        # Core OIC instance configuration
        th.Property(
            "base_url",
            th.StringType,
            required=True,
            description="OIC instance base URL (e.g., https://myinstance-region.integration.ocp.oraclecloud.com)",
        ),
        # Authentication configuration - OIC only supports OAuth2
        th.Property(
            "auth_method",
            th.StringType,
            default="oauth2",
            description="Authentication method: 'oauth2' (OIC only supports OAuth2)",
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
        th.Property(
            "oauth_scope",
            th.StringType,
            default="urn:opc:resource:consumer::all",
            description="OAuth2 scope for OIC access (auto-built if client_aud provided)",
        ),
        # API configuration
        th.Property(
            "instance_id",
            th.StringType,
            description="OIC instance ID for filtering (optional)",
        ),
        th.Property(
            "page_size",
            th.IntegerType,
            default=100,
            description="Number of records per page (1-1000)",
        ),
        th.Property(
            "request_timeout",
            th.IntegerType,
            default=60,
            description="Request timeout in seconds",
        ),
        th.Property(
            "max_retries",
            th.IntegerType,
            default=3,
            description="Maximum number of retries for failed requests",
        ),
        # Data selection
        th.Property(
            "include_inactive",
            th.BooleanType,
            default=False,
            description="Include inactive/disabled entities",
        ),
        th.Property(
            "include_monitoring",
            th.BooleanType,
            default=True,
            description="Include monitoring data streams",
        ),
        th.Property(
            "include_extended",
            th.BooleanType,
            default=False,
            description="Include extended streams (lookups, libraries, agents, certificates)",
        ),
        # Process and B2B configuration
        th.Property(
            "include_processes",
            th.BooleanType,
            default=False,
            description="Include process management streams (process definitions, instances, tasks)",
        ),
        th.Property(
            "include_b2b",
            th.BooleanType,
            default=False,
            description="Include B2B trading partner streams",
        ),
        # Advanced filtering configuration
        th.Property(
            "date_range",
            th.ObjectType(
                th.Property(
                    "start_date",
                    th.StringType,
                    description="Start date for filtering (ISO 8601)",
                ),
                th.Property(
                    "end_date",
                    th.StringType,
                    description="End date for filtering (ISO 8601)",
                ),
            ),
            description="Date range for filtering data",
        ),
        th.Property(
            "integration_types",
            th.ArrayType(th.StringType),
            description="Filter integrations by type (SCHEDULED, ORCHESTRATION, etc.)",
        ),
        th.Property(
            "custom_filter",
            th.StringType,
            description="Custom OData-style filter expression",
        ),
        th.Property(
            "sort_field",
            th.StringType,
            description="Field to sort results by",
        ),
        th.Property(
            "sort_desc",
            th.BooleanType,
            default=False,
            description="Sort results in descending order",
        ),
        # Health monitoring configuration
        th.Property(
            "test_connections",
            th.BooleanType,
            default=False,
            description="Enable connection health testing (adds latency)",
        ),
        th.Property(
            "include_health",
            th.BooleanType,
            default=False,
            description="Include health monitoring streams",
        ),
        # Logging configuration
        th.Property(
            "log_level",
            th.StringType,
            description="Filter execution logs by level (INFO, WARNING, ERROR, DEBUG)",
        ),
        th.Property(
            "log_window_hours",
            th.IntegerType,
            default=24,
            description="Time window for execution logs in hours",
        ),
        # Advanced query capabilities
        th.Property(
            "select_fields",
            th.ArrayType(th.StringType),
            description="Fields to include in response (projection)",
        ),
        th.Property(
            "expand",
            th.ArrayType(th.StringType),
            description="Related entities to expand in response",
        ),
        # Lifecycle management configuration
        th.Property(
            "enable_lifecycle_management",
            th.BooleanType,
            default=False,
            description="Enable integration lifecycle management capabilities",
        ),
        th.Property(
            "lifecycle_force_operations",
            th.BooleanType,
            default=False,
            description="Force lifecycle operations even with active instances",
        ),
        # Logs and artifacts configuration
        th.Property(
            "include_logs",
            th.BooleanType,
            default=False,
            description="Include log streams (integration logs, diagnostic logs, error logs)",
        ),
        th.Property(
            "include_artifacts",
            th.BooleanType,
            default=False,
            description="Include artifact streams (download .iar packages and metadata)",
        ),
        th.Property(
            "include_payload_in_logs",
            th.BooleanType,
            default=False,
            description="Include message payloads in log extraction (increases data volume)",
        ),
        th.Property(
            "include_artifact_content",
            th.BooleanType,
            default=False,
            description="Include base64-encoded artifact content in extraction (large data volume)",
        ),
        th.Property(
            "diagnostic_time_range",
            th.StringType,
            default="24h",
            description="Time range for diagnostic logs (24h, 7d, 30d)",
        ),
        th.Property(
            "performance_aggregation",
            th.StringType,
            default="HOURLY",
            description="Performance log aggregation level (HOURLY, DAILY, WEEKLY)",
        ),
    )
