"""Stream definitions for OIC."""

from singer_sdk import typing as th
from singer_sdk.streams import RESTStream


class OICStream(RESTStream):
    """OIC stream class."""

    @property
    def url_base(self) -> str:
        """Return the base URL of the API."""
        return self.client.oic_url

    @property
    def authenticator(self):
        """Return authenticator."""
        return self.client.get_authenticator()


class IntegrationsStream(OICStream):
    """Integrations stream."""

    name = "integrations"
    path = "/ic/api/integration/v1/integrations"
    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.StringType, required=True),
        th.Property("name", th.StringType),
        th.Property("version", th.StringType),
        th.Property("status", th.StringType),
        th.Property("created_by", th.StringType),
        th.Property("created_on", th.DateTimeType),
        th.Property("last_updated", th.DateTimeType),
        th.Property("description", th.StringType),
        th.Property("integration_type", th.StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        """Return URL parameters."""
        params = {}

        if self.client.integration_filter:
            params["q"] = f"name:{self.client.integration_filter}"

        if next_page_token:
            params.update(next_page_token)

        return params


class InstancesStream(OICStream):
    """Integration instances stream."""

    name = "instances"
    path = "/ic/api/integration/v1/monitoring/instances"
    primary_keys = ["id"]
    replication_key = "created_on"
    schema = th.PropertiesList(
        th.Property("id", th.StringType, required=True),
        th.Property("integration_id", th.StringType),
        th.Property("integration_name", th.StringType),
        th.Property("status", th.StringType),
        th.Property("created_on", th.DateTimeType),
        th.Property("last_updated", th.DateTimeType),
        th.Property("business_identifiers", th.ObjectType()),
    ).to_dict()


class LogsStream(OICStream):
    """Integration logs stream."""

    name = "logs"
    path = "/ic/api/integration/v1/monitoring/instances/{instance_id}/logs"
    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.StringType, required=True),
        th.Property("instance_id", th.StringType),
        th.Property("activity_name", th.StringType),
        th.Property("level", th.StringType),
        th.Property("timestamp", th.DateTimeType),
        th.Property("message", th.StringType),
    ).to_dict()

    def get_child_context(self, record, context):
        """Return child context."""
        return {"instance_id": record["id"]}


class ConnectionsStream(OICStream):
    """Connections stream."""

    name = "connections"
    path = "/ic/api/integration/v1/connections"
    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.StringType, required=True),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("connection_type", th.StringType),
        th.Property("created_by", th.StringType),
        th.Property("created_on", th.DateTimeType),
        th.Property("last_updated", th.DateTimeType),
    ).to_dict()


class PayloadsStream(OICStream):
    """Payloads stream."""

    name = "payloads"
    path = "/ic/api/integration/v1/monitoring/instances/{instance_id}/payloads"
    primary_keys = ["id"]
    schema = th.PropertiesList(
        th.Property("id", th.StringType, required=True),
        th.Property("instance_id", th.StringType),
        th.Property("activity_name", th.StringType),
        th.Property("direction", th.StringType),
        th.Property("timestamp", th.DateTimeType),
        th.Property("content_type", th.StringType),
        th.Property("payload", th.StringType),
    ).to_dict()

    def get_child_context(self, record, context):
        """Return child context."""
        return {"instance_id": record["id"]}
