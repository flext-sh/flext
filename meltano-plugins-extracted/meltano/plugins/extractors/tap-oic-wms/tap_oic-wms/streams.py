"""Stream definitions for WMS."""

from singer_sdk import typing as th
from singer_sdk.streams import RESTStream


class WMSStream(RESTStream):
    """WMS stream class."""

    @property
    def url_base(self) -> str:
        """Return the base URL of the API."""
        return self.client.wms_url

    @property
    def authenticator(self):
        """Return authenticator."""
        return self.client.get_authenticator()

    def get_url_params(self, context, next_page_token):
        """Return URL parameters."""
        params = {}

        if self.client.company_code:
            params["company_code"] = self.client.company_code

        if self.client.facility_code:
            params["facility_code"] = self.client.facility_code

        if self.replication_key and self.get_starting_timestamp(context):
            params[self.replication_key] = self.get_starting_timestamp(
                context,
            ).isoformat()

        if next_page_token:
            params.update(next_page_token)

        return params


class OrderHeaderStream(WMSStream):
    """Order Headers stream."""

    name = "order_hdr"
    path = "/api/orders"
    primary_keys = ["company_code", "facility_code", "order_nbr"]
    replication_key = "modified_date"
    schema = th.PropertiesList(
        th.Property("company_code", th.StringType, required=True),
        th.Property("facility_code", th.StringType, required=True),
        th.Property("order_nbr", th.StringType, required=True),
        th.Property("order_type", th.StringType),
        th.Property("order_date", th.DateTimeType),
        th.Property("destination", th.StringType),
        th.Property("status", th.StringType),
        th.Property("modified_date", th.DateTimeType),
    ).to_dict()


class OrderDetailStream(WMSStream):
    """Order Details stream."""

    name = "order_dtl"
    path = "/api/order_details"
    primary_keys = ["company_code", "facility_code", "order_nbr", "line_nbr"]
    replication_key = "modified_date"
    schema = th.PropertiesList(
        th.Property("company_code", th.StringType, required=True),
        th.Property("facility_code", th.StringType, required=True),
        th.Property("order_nbr", th.StringType, required=True),
        th.Property("line_nbr", th.StringType, required=True),
        th.Property("item_alternate_code", th.StringType),
        th.Property("ordered_qty", th.NumberType),
        th.Property("allocated_qty", th.NumberType),
        th.Property("uom", th.StringType),
        th.Property("modified_date", th.DateTimeType),
    ).to_dict()


class AllocationStream(WMSStream):
    """Allocations stream."""

    name = "allocations"
    path = "/api/allocations"
    primary_keys = ["allocation_id"]
    replication_key = "allocation_time"
    schema = th.PropertiesList(
        th.Property("allocation_id", th.StringType, required=True),
        th.Property("company_code", th.StringType),
        th.Property("facility_code", th.StringType),
        th.Property("order_nbr", th.StringType),
        th.Property("item_alternate_code", th.StringType),
        th.Property("allocated_qty", th.NumberType),
        th.Property("allocation_time", th.DateTimeType),
        th.Property("source_loc", th.StringType),
    ).to_dict()


class InventoryHistoryStream(WMSStream):
    """Inventory History stream."""

    name = "inventory_history"
    path = "/api/inventory_history"
    primary_keys = ["transaction_id"]
    replication_key = "transaction_time"
    schema = th.PropertiesList(
        th.Property("transaction_id", th.StringType, required=True),
        th.Property("company_code", th.StringType),
        th.Property("facility_code", th.StringType),
        th.Property("transaction_type", th.StringType),
        th.Property("item_alternate_code", th.StringType),
        th.Property("quantity", th.NumberType),
        th.Property("transaction_time", th.DateTimeType),
        th.Property("location", th.StringType),
    ).to_dict()
