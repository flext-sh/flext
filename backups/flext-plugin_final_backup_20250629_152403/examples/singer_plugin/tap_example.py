"""Singer tap plugin example.

Demonstrates integration with Singer protocol for data extraction.
"""

from datetime import UTC, datetime
from typing import Any, Dict, List

from flx_plugin import Plugin, PluginCapability, PluginMetadata, PluginType


class TapExamplePlugin(Plugin):
    """Example Singer tap plugin for data extraction."""

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            id="tap-example",
            name="Example Tap",
            version="1.0.0",
            description="Example Singer tap for demonstrating data extraction",
            plugin_type=PluginType.EXTRACTOR,
            author="FLX Team",
            license="MIT",
            capabilities=[
                PluginCapability.DATA_EXTRACTION.value,
                PluginCapability.SCHEMA_INFERENCE.value,
                PluginCapability.INCREMENTAL_SYNC.value,
            ],
            dependencies=[],
            configuration_schema={
                "type": "object",
                "properties": {
                    "api_url": {"type": "string", "description": "API endpoint URL"},
                    "api_key": {
                        "type": "string",
                        "description": "API key for authentication",
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Start date for data extraction",
                    },
                    "page_size": {
                        "type": "integer",
                        "default": 100,
                        "description": "Number of records per page",
                    },
                },
                "required": ["api_url"],
            },
        )

    async def initialize(self) -> None:
        """Initialize the tap plugin."""
        self.logger.info("Initializing Example Tap")

        # Get configuration
        self.api_url = self.config.get("api_url")
        self.api_key = self.config.get("api_key")
        self.start_date = self.config.get("start_date")
        self.page_size = self.config.get("page_size", 100)

        # Initialize state
        self.state = {}
        self.catalog = None

    async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute tap operation.

        Args:
        ----
            input_data: Command (discover, sync)
            context: Execution context

        Returns:
        -------
            Singer messages (schema, record, state)

        """
        command = "sync"  # default

        if isinstance(input_data, str):
            command = input_data.lower()
        elif isinstance(input_data, dict):
            command = input_data.get("command", "sync")
            self.state = input_data.get("state", {})
            self.catalog = input_data.get("catalog")

        if command == "discover":
            return await self._discover()
        elif command == "sync":
            return await self._sync(context)
        else:
            raise ValueError(f"Unknown command: {command}")

    async def _discover(self) -> Dict[str, Any]:
        """Discover available streams and schemas.

        Returns
        -------
            Catalog with discovered streams

        """
        self.logger.info("Discovering schemas")

        # Example catalog with two streams
        catalog = {
            "streams": [
                {
                    "tap_stream_id": "users",
                    "stream": "users",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"},
                        },
                    },
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "inclusion": "available",
                                "selected": True,
                                "replication-method": "INCREMENTAL",
                                "replication-key": "updated_at",
                            },
                        }
                    ],
                },
                {
                    "tap_stream_id": "orders",
                    "stream": "orders",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "user_id": {"type": "integer"},
                            "total": {"type": "number"},
                            "status": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"},
                        },
                    },
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "inclusion": "available",
                                "selected": True,
                                "replication-method": "FULL_TABLE",
                            },
                        }
                    ],
                },
            ]
        }

        return catalog

    async def _sync(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sync data from source.

        Args:
        ----
            context: Execution context

        Returns:
        -------
            List of Singer messages

        """
        self.logger.info("Starting data sync")

        messages = []

        # Get selected streams from catalog
        if not self.catalog:
            self.catalog = await self._discover()

        for stream in self.catalog.get("streams", []):
            stream_id = stream["tap_stream_id"]

            # Check if stream is selected
            metadata = stream.get("metadata", [{}])[0].get("metadata", {})
            if not metadata.get("selected", False):
                continue

            # Write schema message
            messages.append(
                {
                    "type": "SCHEMA",
                    "stream": stream_id,
                    "schema": stream["schema"],
                    "key_properties": ["id"],
                }
            )

            # Generate sample data
            records = await self._fetch_records(stream_id, context)

            for record in records:
                # Write record message
                messages.append(
                    {
                        "type": "RECORD",
                        "stream": stream_id,
                        "record": record,
                        "time_extracted": datetime.now(UTC).isoformat(),
                    }
                )

            # Update state
            if metadata.get("replication-method") == "INCREMENTAL":
                replication_key = metadata.get("replication-key", "updated_at")
                if records:
                    last_value = max(r.get(replication_key, "") for r in records)
                    self.state[stream_id] = {
                        "replication_key_value": last_value,
                        "replication_key": replication_key,
                    }

        # Write state message
        if self.state:
            messages.append({"type": "STATE", "value": self.state})

        self.logger.info(f"Sync completed, {len(messages)} messages generated")

        return messages

    async def _fetch_records(
        self, stream_id: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fetch records for a stream (simulated).

        Args:
        ----
            stream_id: Stream to fetch
            context: Execution context

        Returns:
        -------
            List of records

        """
        # In a real implementation, this would fetch from the API
        # Here we generate sample data

        records = []

        if stream_id == "users":
            for i in range(5):
                records.append(
                    {
                        "id": i + 1,
                        "name": f"User {i + 1}",
                        "email": f"user{i + 1}@example.com",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": datetime.now(UTC).isoformat(),
                    }
                )

        elif stream_id == "orders":
            for i in range(10):
                records.append(
                    {
                        "id": i + 1,
                        "user_id": (i % 5) + 1,
                        "total": 100.0 + (i * 10),
                        "status": "completed" if i % 2 == 0 else "pending",
                        "created_at": datetime.now(UTC).isoformat(),
                    }
                )

        return records

    async def get_state(self) -> Dict[str, Any]:
        """Get tap state for preservation."""
        return {"tap_state": self.state}

    async def set_state(self, state: Dict[str, Any]) -> None:
        """Restore tap state."""
        self.state = state.get("tap_state", {})

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "tap": self.metadata.name,
            "api_url": self.api_url,
            "configured": bool(self.api_url),
            "state": self.state,
        }

    async def cleanup(self) -> None:
        """Clean up tap resources."""
        self.logger.info("Example Tap cleanup completed")


# Entry point for plugin discovery
plugin_class = TapExamplePlugin
