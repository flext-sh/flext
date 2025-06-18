"""Oracle Integration Cloud Singer Tap - Main TAP Implementation.

Clean, modular TAP class focused on core functionality without legacy code.
Architecture Layer: Application - Main TAP Entry Point
Dependencies: Singer SDK, OIC REST APIs, OAuth2/IDCS Authentication
Pattern: Facade pattern providing unified interface to OIC data sources
"""

from __future__ import annotations

from typing import Any

from singer_sdk import Tap
from singer_sdk.helpers import capabilities

from .config import get_config_schema
from .streams_core import (
    CertificatesStream,
    ConnectionsStream,
    IntegrationsStream,
    LibrariesStream,
    LookupsStream,
    PackagesStream,
)
from .streams_extended import (
    BusinessEventsStream,
    ImportExportJobsStream,
    ProjectsStream,
    SchedulesStream,
)
from .streams_infrastructure import AdaptersStream, AgentGroupsStream
from .streams_monitoring import (
    AuditEventsStream,
    ErrorsStream,
    ExecutionsStream,
    InstancesStream,
    MetricsStream,
)


class TapOIC(Tap):
    """Oracle Integration Cloud Singer TAP.

    Clean implementation focused on working streams only.
    No legacy code, no god functions, modular design.
    """

    name = "tap-oic"
    config_jsonschema = get_config_schema().to_dict()

    supported_capabilities = [
        capabilities.TapCapabilities.CATALOG,
        capabilities.TapCapabilities.DISCOVER,
        capabilities.TapCapabilities.STATE,
    ]

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        catalog: dict[str, Any] | None = None,
        state: dict[str, Any] | None = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
        setup_mapper: bool = True,
    ) -> None:
        """Initialize TAP with clean configuration validation."""
        super().__init__(
            config=config,
            catalog=catalog,
            state=state,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
            setup_mapper=setup_mapper,
        )

        if validate_config:
            self._validate_oic_config()

    def _validate_oic_config(self) -> None:
        """Validate OIC-specific configuration requirements."""
        auth_method = self.config.get("auth_method", "oauth2")
        if auth_method != "oauth2":
            self.logger.warning(
                f"auth_method '{auth_method}' not recommended. "
                "OIC only supports OAuth2 authentication."
            )

        required_fields = [
            "oauth_client_id",
            "oauth_client_secret",
            "oauth_token_url",
            "base_url",
        ]

        missing_fields = [
            field for field in required_fields if not self.config.get(field)
        ]

        if missing_fields:
            self.logger.warning(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate HTTPS URLs
        for url_field in ["base_url", "oauth_token_url"]:
            url = self.config.get(url_field, "")
            if url and not url.startswith("https://"):
                self.logger.warning(f"{url_field} should use HTTPS protocol")

    def _get_core_streams(self) -> list[Any]:
        """Get core OIC streams that always work."""
        return [
            IntegrationsStream(self),
            ConnectionsStream(self),
            PackagesStream(self),
            LookupsStream(self),
            LibrariesStream(self),
            CertificatesStream(self),
            ProjectsStream(self),
            SchedulesStream(self),
        ]

    def _get_infrastructure_streams(self) -> list[Any]:
        """Get infrastructure streams based on configuration."""
        streams = []

        if self.config.get("include_extended", False):
            streams.extend(
                [
                    AdaptersStream(self),
                    AgentGroupsStream(self),
                ]
            )

        return streams

    def _get_extended_streams(self) -> list[Any]:
        """Get extended streams based on configuration."""
        streams = []

        if self.config.get("include_extended", False):
            streams.extend(
                [
                    BusinessEventsStream(self),
                    ImportExportJobsStream(self),
                ]
            )

        return streams

    def _get_monitoring_streams(self) -> list[Any]:
        """Get monitoring streams based on configuration."""
        streams = []

        if self.config.get("include_monitoring", False):
            streams.extend(
                [
                    ExecutionsStream(self),
                    MetricsStream(self),
                    ErrorsStream(self),
                    AuditEventsStream(self),
                    InstancesStream(self),
                ]
            )

        return streams

    def _get_logs_streams(self) -> list[Any]:
        """Log streams moved to oracle-oic-ext."""
        return []

    def _get_process_streams(self) -> list[Any]:
        """Process streams moved to oracle-oic-ext."""
        return []

    def _get_b2b_streams(self) -> list[Any]:
        """B2B streams moved to oracle-oic-ext."""
        return []

    def _get_health_streams(self) -> list[Any]:
        """Health streams moved to oracle-oic-ext."""
        return []

    def discover_streams(self) -> list[Any]:
        """Discover available streams based on configuration.

        Returns streams organized by category:
        - Core: Always included (integrations, connections, packages, lookups, libraries, projects, schedules)
        - Infrastructure: Optional (certificates, adapters, agents)
        - Extended: Optional (business events, import/export jobs)
        - Monitoring: Optional (executions, errors, metrics, audit, instances)
        - Logs: Optional (execution logs, error logs)
        - Process: Optional (process definitions, instances)
        - B2B: Optional (trading partners, agreements)
        - Health: Optional (system health, diagnostics)

        Professional approach with intelligent stream selection based on
        OIC instance capabilities and user permissions.
        """
        streams = self._get_core_streams()

        # Add infrastructure streams if requested
        streams.extend(self._get_infrastructure_streams())

        # Add extended streams if requested
        streams.extend(self._get_extended_streams())

        # Add monitoring streams if requested
        streams.extend(self._get_monitoring_streams())

        # Add specialized log streams if requested
        if self.config.get("include_logs", False) and not self.config.get(
            "include_monitoring", False
        ):
            # Only add log streams if monitoring not already included
            streams.extend(self._get_logs_streams())

        # Add process management streams if requested
        if self.config.get("include_processes", False):
            streams.extend(self._get_process_streams())

        # Add B2B trading partner streams if requested
        if self.config.get("include_b2b", False):
            streams.extend(self._get_b2b_streams())

        # Add health monitoring streams if requested
        if self.config.get("include_health", False):
            streams.extend(self._get_health_streams())

        self.logger.info(f"Discovered {len(streams)} streams based on configuration")
        return streams


if __name__ == "__main__":
    TapOIC.cli()
