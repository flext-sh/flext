"""Oracle Integration Cloud extractor."""

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_oic.client import OICClient
from tap_oic.streams import (
    ConnectionsStream,
    InstancesStream,
    IntegrationsStream,
    LogsStream,
    PayloadsStream,
)

STREAM_TYPES = [
    IntegrationsStream,
    InstancesStream,
    LogsStream,
    ConnectionsStream,
    PayloadsStream,
]


class TapOIC(Tap):
    """OIC tap class."""

    name = "tap-oic"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "oic_url",
            th.StringType,
            required=True,
            description="OIC instance URL",
        ),
        th.Property(
            "auth_method",
            th.StringType,
            required=True,
            allowed_values=["oauth2", "basic"],
            description="Authentication method: oauth2 or basic",
        ),
        th.Property(
            "client_id",
            th.StringType,
            description="OAuth2 client ID",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            secret=True,
            description="OAuth2 client secret",
        ),
        th.Property(
            "idcs_url",
            th.StringType,
            description="IDCS URL for OAuth2",
        ),
        th.Property(
            "resource_aud",
            th.StringType,
            description="Resource audience for OAuth2",
        ),
        th.Property(
            "api_aud",
            th.StringType,
            description="API audience for OAuth2",
        ),
        th.Property(
            "username",
            th.StringType,
            description="Username for Basic Auth",
        ),
        th.Property(
            "password",
            th.StringType,
            secret=True,
            description="Password for Basic Auth",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "integration_filter",
            th.StringType,
            description="Filter pattern for integrations (e.g., WMS_*)",
        ),
        th.Property(
            "include_payload",
            th.BooleanType,
            default=False,
            description="Whether to include payload data",
        ),
        th.Property(
            "include_logs",
            th.BooleanType,
            default=True,
            description="Whether to include detailed logs",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        client = OICClient(self.config)
        return [stream_class(tap=self, client=client) for stream_class in STREAM_TYPES]
