"""Oracle WMS extractor."""

from singer_sdk import Stream, Tap
from singer_sdk import typing as th
from tap_wms.client import WMSClient
from tap_wms.streams import (
    AllocationStream,
    InventoryHistoryStream,
    OrderDetailStream,
    OrderHeaderStream,
)

STREAM_TYPES = [
    OrderHeaderStream,
    OrderDetailStream,
    AllocationStream,
    InventoryHistoryStream,
]


class TapWMS(Tap):
    """WMS tap class."""

    name = "tap-wms"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "wms_url",
            th.StringType,
            required=True,
            description="WMS API URL",
        ),
        th.Property(
            "username",
            th.StringType,
            required=True,
            description="Username for WMS API authentication",
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
            secret=True,
            description="Password for WMS API authentication",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "company_code",
            th.StringType,
            description="Company code to filter records",
        ),
        th.Property(
            "facility_code",
            th.StringType,
            description="Facility code to filter records",
        ),
        th.Property(
            "extraction_mode",
            th.StringType,
            allowed_values=["api", "csv", "webhook"],
            default="api",
            description="Extraction mode: api, csv, or webhook",
        ),
        th.Property(
            "sftp_config",
            th.ObjectType(
                th.Property("host", th.StringType, description="SFTP host"),
                th.Property(
                    "port",
                    th.IntegerType,
                    default=22,
                    description="SFTP port",
                ),
                th.Property("username", th.StringType, description="SFTP username"),
                th.Property(
                    "password",
                    th.StringType,
                    secret=True,
                    description="SFTP password",
                ),
                th.Property("directory", th.StringType, description="SFTP directory"),
            ),
            description="SFTP configuration for CSV extraction mode",
        ),
        th.Property(
            "webhook_config",
            th.ObjectType(
                th.Property(
                    "listen_port",
                    th.IntegerType,
                    default=5000,
                    description="Webhook listen port",
                ),
                th.Property(
                    "endpoint_path",
                    th.StringType,
                    default="/wms-events",
                    description="Webhook endpoint path",
                ),
                th.Property(
                    "auth_required",
                    th.BooleanType,
                    default=True,
                    description="Whether authentication is required",
                ),
                th.Property(
                    "webhook_username",
                    th.StringType,
                    description="Webhook auth username",
                ),
                th.Property(
                    "webhook_password",
                    th.StringType,
                    secret=True,
                    description="Webhook auth password",
                ),
            ),
            description="Webhook configuration for webhook extraction mode",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        client = WMSClient(self.config)
        return [stream_class(tap=self, client=client) for stream_class in STREAM_TYPES]
