"""Oracle Integration Cloud target sinks."""

from __future__ import annotations

from typing import Any

import httpx
from singer_sdk.sinks import Sink

from target_oracle_oic.auth import OICOAuth2Authenticator


class OICBaseSink(Sink):
    """Base sink for Oracle Integration Cloud."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the sink."""
        super().__init__(*args, **kwargs)
        # CRITICAL: Set tap_name for Singer SDK auth compatibility
        self.tap_name = "target-oracle-oic"  # Required by Singer SDK authenticators
        self._authenticator: OICOAuth2Authenticator | None = None
        self._client: httpx.Client | None = None

    @property
    def authenticator(self) -> OICOAuth2Authenticator:
        """Get or create the authenticator."""
        if not self._authenticator:
            self._authenticator = OICOAuth2Authenticator(self)
        return self._authenticator

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if not self._client:
            self._client = httpx.Client(
                base_url=self.config["base_url"],
                headers=self.authenticator.auth_headers,
                timeout=30.0,
            )
        return self._client

    def preprocess_record(
        self, record: dict[str, Any], _context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Process the record before sending it to Oracle Integration Cloud."""
        return record

    def process_batch(self, context: dict[str, Any]) -> None:
        """Process batch efficiently using Oracle OIC batch API endpoints."""
        if not context.get("records"):
            return

        batch_size = min(len(context["records"]), 100)  # OIC API batch limit
        records = context["records"]

        # Group records by operation type for more efficient processing
        create_records = []
        update_records = []

        for record in records:
            if self._record_exists(record):
                update_records.append(record)
            else:
                create_records.append(record)

        # Process creates in batches
        if create_records:
            for i in range(0, len(create_records), batch_size):
                batch = create_records[i : i + batch_size]
                self._process_create_batch(batch, context)

        # Process updates in batches
        if update_records:
            for i in range(0, len(update_records), batch_size):
                batch = update_records[i : i + batch_size]
                self._process_update_batch(batch, context)

    def _record_exists(self, _record: dict[str, Any]) -> bool:
        """Check if a record already exists in OIC."""
        # Default implementation - subclasses should override
        return False

    def _process_create_batch(
        self, records: list[dict[str, Any]], context: dict[str, Any]
    ) -> None:
        """Process a batch of create operations."""
        # Default implementation processes records individually
        # Subclasses should override for true batch operations
        for record in records:
            self.process_record(record, context)

    def _process_update_batch(
        self, records: list[dict[str, Any]], context: dict[str, Any]
    ) -> None:
        """Process a batch of update operations."""
        # Default implementation processes records individually
        # Subclasses should override for true batch operations
        for record in records:
            self.process_record(record, context)


class ConnectionsSink(OICBaseSink):
    """Oracle Integration Cloud target sink for connections."""

    name = "connections"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single connection record."""
        connection_id = record.get("id") or ""

        # Check if connection exists
        response = self.client.get(
            f"/ic/api/integration/v1/connections/{connection_id}"
        )

        if response.status_code == 404:
            # Create new connection
            self._create_connection(record)
        else:
            # Update existing connection
            self._update_connection(connection_id, record)

    def _create_connection(self, record: dict[str, Any]) -> None:
        """Create a new connection."""
        payload = {
            "connectionProperties": {
                "name": record["name"],
                "identifier": record["id"],
                "description": record.get("description", ""),
                "adapterType": record["adapter_type"],
                "connectionProperties": record.get("properties", {}),
            }
        }

        response = self.client.post(
            "/ic/api/integration/v1/connections",
            json=payload,
        )
        response.raise_for_status()

    def _update_connection(self, connection_id: str, record: dict[str, Any]) -> None:
        """Update an existing connection."""
        payload = {
            "connectionProperties": {
                "description": record.get("description", ""),
                "connectionProperties": record.get("properties", {}),
            }
        }

        response = self.client.put(
            f"/ic/api/integration/v1/connections/{connection_id}",
            json=payload,
        )
        response.raise_for_status()


class IntegrationsSink(OICBaseSink):
    """Oracle Integration Cloud target sink for integrations."""

    name = "integrations"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single integration record."""
        integration_id = record.get("id") or ""
        version = record.get("version", "01.00.0000")

        # Check if integration exists
        response = self.client.get(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}"
        )

        if response.status_code == 404:
            # Create new integration from archive if provided
            if "archive_content" in record:
                self._import_integration(record)
            else:
                self._create_integration(record)
        else:
            # Update existing integration
            self._update_integration(integration_id, version, record)

    def _create_integration(self, record: dict[str, Any]) -> None:
        """Create a new integration."""
        payload = {
            "name": record["name"],
            "identifier": record["id"],
            "description": record.get("description", ""),
            "pattern": record.get("pattern", "ORCHESTRATION"),
        }

        response = self.client.post(
            "/ic/api/integration/v1/integrations",
            json=payload,
        )
        response.raise_for_status()

    def _import_integration(self, record: dict[str, Any]) -> None:
        """Import an integration from archive."""
        archive_content = record.get("archive_content")
        if isinstance(archive_content, str):
            archive_content = archive_content.encode()

        files = {
            "file": (f"{record['id']}.iar", archive_content, "application/octet-stream")
        }

        response = self.client.post(
            "/ic/api/integration/v1/integrations/archive",
            files=files,  # type: ignore[arg-type]
        )
        response.raise_for_status()

    def _update_integration(
        self, integration_id: str, version: str, record: dict[str, Any]
    ) -> None:
        """Update an existing integration."""
        payload = {
            "description": record.get("description", ""),
        }

        response = self.client.put(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}",
            json=payload,
        )
        response.raise_for_status()


class PackagesSink(OICBaseSink):
    """Oracle Integration Cloud target sink for packages."""

    name = "packages"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single package record."""
        record.get("id") or ""

        # Import package if archive content is provided
        if "archive_content" in record:
            self._import_package(record)

    def _import_package(self, record: dict[str, Any]) -> None:
        """Import a package from archive."""
        archive_content = record.get("archive_content")
        if isinstance(archive_content, str):
            archive_content = archive_content.encode()

        files = {
            "file": (f"{record['id']}.par", archive_content, "application/octet-stream")
        }

        response = self.client.post(
            "/ic/api/integration/v1/packages/archive",
            files=files,  # type: ignore[arg-type]
        )
        response.raise_for_status()


class LookupsSink(OICBaseSink):
    """Oracle Integration Cloud target sink for lookups."""

    name = "lookups"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single lookup record."""
        lookup_name = record.get("name") or ""

        # Check if lookup exists
        response = self.client.get(f"/ic/api/integration/v1/lookups/{lookup_name}")

        if response.status_code == 404:
            # Create new lookup
            self._create_lookup(record)
        else:
            # Update existing lookup
            self._update_lookup(lookup_name, record)

    def _create_lookup(self, record: dict[str, Any]) -> None:
        """Create a new lookup."""
        payload = {
            "name": record["name"],
            "description": record.get("description", ""),
            "columns": record.get("columns", []),
            "rows": record.get("rows", []),
        }

        response = self.client.post(
            "/ic/api/integration/v1/lookups",
            json=payload,
        )
        response.raise_for_status()

    def _update_lookup(self, lookup_name: str, record: dict[str, Any]) -> None:
        """Update an existing lookup."""
        payload = {
            "description": record.get("description", ""),
            "rows": record.get("rows", []),
        }

        response = self.client.put(
            f"/ic/api/integration/v1/lookups/{lookup_name}",
            json=payload,
        )
        response.raise_for_status()
