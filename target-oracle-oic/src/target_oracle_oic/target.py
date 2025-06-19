"""Oracle Integration Cloud target class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from singer_sdk import Target

from target_oracle_oic.config import TargetOracleOICConfig
from target_oracle_oic.sinks import (
    ConnectionsSink,
    IntegrationsSink,
    LookupsSink,
    OICBaseSink,
    PackagesSink,
)
from target_oracle_oic.sinks_extended import (
    BusinessEventsSink,
    CertificatesSink,
    ConnectionActionsSink,
    IntegrationActionsSink,
    LibrariesSink,
    MonitoringConfigSink,
    ProjectsSink,
    SchedulesSink,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from singer_sdk.sinks import Sink


class TargetOracleOIC(Target):
    """Sample target for Oracle Integration Cloud."""

    name = "target-oracle-oic"
    config_jsonschema = TargetOracleOICConfig.model_json_schema()
    default_sink_class = OICBaseSink

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the target."""
        # CRITICAL: Initialize required Singer SDK attributes FIRST
        # Note: logger is a property in Singer SDK, don't override
        super().__init__(*args, **kwargs)
        # Initialize any target-specific attributes here

    def get_sink(
        self,
        stream_name: str,
        *,
        record: dict[str, Any] | None = None,
        schema: dict[str, Any] | None = None,
        key_properties: Sequence[str] | None = None,
    ) -> Sink:
        """Return a sink for the given stream name."""
        sink_class = self._get_sink_class(stream_name)
        return sink_class(
            target=self,
            stream_name=stream_name,
            schema=schema or {},
            key_properties=key_properties,
        )

    def _get_sink_class(self, stream_name: str) -> type[OICBaseSink]:
        """Get the sink class for a stream."""
        sink_mapping = {
            # Core sinks
            "connections": ConnectionsSink,
            "integrations": IntegrationsSink,
            "packages": PackagesSink,
            "lookups": LookupsSink,
            # Extended sinks
            "libraries": LibrariesSink,
            "certificates": CertificatesSink,
            "projects": ProjectsSink,
            "schedules": SchedulesSink,
            "business_events": BusinessEventsSink,
            # Action sinks
            "integration_actions": IntegrationActionsSink,
            "connection_actions": ConnectionActionsSink,
            "monitoring_config": MonitoringConfigSink,
        }
        return sink_mapping.get(stream_name, self.default_sink_class)
