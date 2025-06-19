"""Oracle Integration Cloud Extended Sinks.

Professional-grade sinks for additional OIC entities including
libraries, certificates, schedules, and projects.
"""

from __future__ import annotations

from typing import Any

from .sinks import OICBaseSink


class LibrariesSink(OICBaseSink):
    """Oracle Integration Cloud target sink for libraries."""

    name = "libraries"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single library record."""
        library_id = record.get("id") or ""

        # Check if library exists
        response = self.client.get(f"/ic/api/integration/v1/libraries/{library_id}")

        if response.status_code == 404:
            # Create new library
            self._create_library(record)
        else:
            # Update existing library
            self._update_library(library_id, record)

    def _create_library(self, record: dict[str, Any]) -> None:
        """Create a new library."""
        # If archive content is provided, import it
        if "archive_content" in record:
            self._import_library(record)
            return

        payload = {
            "name": record["name"],
            "identifier": record["id"],
            "description": record.get("description", ""),
            "type": record.get("type", "JAVASCRIPT"),
            "version": record.get("version", "1.0"),
        }

        response = self.client.post(
            "/ic/api/integration/v1/libraries",
            json=payload,
        )
        response.raise_for_status()

    def _import_library(self, record: dict[str, Any]) -> None:
        """Import a library from archive."""
        archive_content = record.get("archive_content")
        if isinstance(archive_content, str):
            archive_content = archive_content.encode()

        files = {
            "file": (f"{record['id']}.jar", archive_content, "application/octet-stream")
        }

        response = self.client.post(
            "/ic/api/integration/v1/libraries/archive",
            files=files,  # type: ignore[arg-type]
        )
        response.raise_for_status()

    def _update_library(self, library_id: str, record: dict[str, Any]) -> None:
        """Update an existing library."""
        payload = {
            "description": record.get("description", ""),
            "version": record.get("version", "1.0"),
        }

        response = self.client.put(
            f"/ic/api/integration/v1/libraries/{library_id}",
            json=payload,
        )
        response.raise_for_status()


class CertificatesSink(OICBaseSink):
    """Oracle Integration Cloud target sink for certificates."""

    name = "certificates"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single certificate record."""
        cert_alias = record.get("alias") or ""

        # Check if certificate exists
        response = self.client.get(f"/ic/api/integration/v1/certificates/{cert_alias}")

        if response.status_code == 404:
            # Create new certificate
            self._create_certificate(record)
        else:
            # Update existing certificate
            self._update_certificate(cert_alias, record)

    def _create_certificate(self, record: dict[str, Any]) -> None:
        """Create a new certificate."""
        # Certificate content must be provided
        cert_content = record.get("certificate_content")
        if not cert_content:
            self.logger.warning(
                "No certificate content provided for %s", record.get("alias")
            )
            return

        if isinstance(cert_content, str):
            cert_content = cert_content.encode()

        files = {
            "certificate": (
                f"{record['alias']}.cer",
                cert_content,
                "application/x-x509-ca-cert",
            )
        }

        data = {
            "alias": record["alias"],
            "description": record.get("description", ""),
            "password": record.get("password", ""),  # For private key certificates
        }

        response = self.client.post(
            "/ic/api/integration/v1/certificates",
            data=data,
            files=files,
        )
        response.raise_for_status()

    def _update_certificate(self, cert_alias: str, record: dict[str, Any]) -> None:
        """Update an existing certificate."""
        # Certificates can only be replaced, not updated
        # Delete and recreate if needed
        if "certificate_content" in record:
            # Delete existing
            response = self.client.delete(
                f"/ic/api/integration/v1/certificates/{cert_alias}"
            )
            response.raise_for_status()

            # Create new
            self._create_certificate(record)


class ProjectsSink(OICBaseSink):
    """Oracle Integration Cloud target sink for projects."""

    name = "projects"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single project record."""
        project_id = record.get("id") or ""

        # Check if project exists
        response = self.client.get(f"/ic/api/integration/v1/projects/{project_id}")

        if response.status_code == 404:
            # Create new project
            self._create_project(record)
        else:
            # Update existing project
            self._update_project(project_id, record)

    def _create_project(self, record: dict[str, Any]) -> None:
        """Create a new project."""
        payload = {
            "name": record["name"],
            "identifier": record["id"],
            "description": record.get("description", ""),
            "parentId": record.get("parentId"),
            "visibility": record.get("visibility", "PRIVATE"),
            "properties": record.get("properties", {}),
        }

        response = self.client.post(
            "/ic/api/integration/v1/projects",
            json=payload,
        )
        response.raise_for_status()

        # Create folders if provided
        if "folders" in record:
            project_id_var = record["id"]
            for folder in record["folders"]:
                self._create_folder(project_id_var, folder)

    def _create_folder(self, project_id: str, folder: dict[str, Any]) -> None:
        """Create a folder within a project."""
        payload = {
            "name": folder["name"],
            "type": folder.get("type", "INTEGRATION"),
            "description": folder.get("description", ""),
        }

        response = self.client.post(
            f"/ic/api/integration/v1/projects/{project_id}/folders",
            json=payload,
        )
        response.raise_for_status()

    def _update_project(self, project_id: str, record: dict[str, Any]) -> None:
        """Update an existing project."""
        payload = {
            "description": record.get("description", ""),
            "visibility": record.get("visibility", "PRIVATE"),
            "properties": record.get("properties", {}),
        }

        response = self.client.put(
            f"/ic/api/integration/v1/projects/{project_id}",
            json=payload,
        )
        response.raise_for_status()


class SchedulesSink(OICBaseSink):
    """Oracle Integration Cloud target sink for schedules."""

    name = "schedules"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single schedule record."""
        schedule_id = record.get("id") or ""
        integration_id = record.get("integrationId") or ""

        if not integration_id:
            self.logger.warning(
                "No integration ID provided for schedule %s", schedule_id
            )
            return

        # Check if schedule exists
        response = self.client.get(
            f"/ic/api/integration/v1/integrations/{integration_id}/schedule"
        )

        if response.status_code == 404:
            # Create new schedule
            self._create_schedule(integration_id, record)
        else:
            # Update existing schedule
            self._update_schedule(integration_id, record)

    def _create_schedule(self, integration_id: str, record: dict[str, Any]) -> None:
        """Create a new schedule."""
        payload = self._build_schedule_payload(record)

        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}/schedule",
            json=payload,
        )
        response.raise_for_status()

    def _update_schedule(self, integration_id: str, record: dict[str, Any]) -> None:
        """Update an existing schedule."""
        payload = self._build_schedule_payload(record)

        response = self.client.put(
            f"/ic/api/integration/v1/integrations/{integration_id}/schedule",
            json=payload,
        )
        response.raise_for_status()

    def _build_schedule_payload(self, record: dict[str, Any]) -> dict[str, Any]:
        """Build schedule payload from record."""
        payload = {
            "scheduleType": record.get("scheduleType", "SIMPLE"),
            "enabled": record.get("enabled", True),
            "timezone": record.get("timezone", "UTC"),
        }

        # Simple schedule
        if payload["scheduleType"] == "SIMPLE":
            payload.update(
                {
                    "frequency": record.get("frequency", "DAILY"),
                    "interval": record.get("interval", 1),
                    "startTime": record.get("startTime"),
                    "endTime": record.get("endTime"),
                }
            )

        # Cron schedule
        elif payload["scheduleType"] == "CRON":
            payload["cronExpression"] = record.get("cronExpression", "0 0 * * *")

        # Calendar schedule
        elif payload["scheduleType"] == "CALENDAR":
            payload.update(
                {
                    "calendarId": record.get("calendarId"),
                    "includeHolidays": record.get("includeHolidays", False),
                    "includeWeekends": record.get("includeWeekends", True),
                }
            )

        # Execution windows
        if "executionWindows" in record:
            payload["executionWindows"] = record["executionWindows"]

        # Advanced options
        payload.update(
            {
                "priority": record.get("priority", 5),
                "maxConcurrentExecutions": record.get("maxConcurrentExecutions", 1),
                "retryOnFailure": record.get("retryOnFailure", False),
                "retryCount": record.get("retryCount", 3),
                "retryInterval": record.get("retryInterval", 5),
            }
        )

        return payload


class BusinessEventsSink(OICBaseSink):
    """Oracle Integration Cloud target sink for business events."""

    name = "business_events"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process a single business event record."""
        # Business events are typically published, not created
        self._publish_event(record)

    def _publish_event(self, record: dict[str, Any]) -> None:
        """Publish a business event."""
        event_type = record.get("eventType") or ""

        payload = {
            "eventType": event_type,
            "eventName": record.get("eventName", ""),
            "eventVersion": record.get("eventVersion", "1.0"),
            "sourceSystem": record.get("sourceSystem", ""),
            "sourceApplication": record.get("sourceApplication", ""),
            "correlationId": record.get("correlationId", ""),
            "businessKey": record.get("businessKey", ""),
            "payload": record.get("payload", {}),
            "headers": record.get("headers", {}),
            "priority": record.get("priority", 5),
            "ttl": record.get("ttl", 3600),
        }

        response = self.client.post(
            "/ic/api/integration/v1/events/publish",
            json=payload,
        )
        response.raise_for_status()


class MonitoringConfigSink(OICBaseSink):
    """Oracle Integration Cloud target sink for monitoring configuration."""

    name = "monitoring_config"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process monitoring configuration record."""
        config_type = record.get("configType", "alerts")

        if config_type == "alerts":
            self._configure_alerts(record)
        elif config_type == "metrics":
            self._configure_metrics(record)
        elif config_type == "tracing":
            self._configure_tracing(record)

    def _configure_alerts(self, record: dict[str, Any]) -> None:
        """Configure monitoring alerts."""
        payload = {
            "alertRules": record.get("alertRules", []),
            "recipients": record.get("recipients", []),
            "enabled": record.get("enabled", True),
            "severityThreshold": record.get("severityThreshold", "ERROR"),
        }

        response = self.client.put(
            "/ic/api/integration/v1/monitoring/alerts/config",
            json=payload,
        )
        response.raise_for_status()

    def _configure_metrics(self, record: dict[str, Any]) -> None:
        """Configure metrics collection."""
        payload = {
            "metricsEnabled": record.get("metricsEnabled", True),
            "retentionPeriod": record.get("retentionPeriod", 30),
            "aggregationInterval": record.get("aggregationInterval", 300),
            "customMetrics": record.get("customMetrics", []),
        }

        response = self.client.put(
            "/ic/api/integration/v1/monitoring/metrics/config",
            json=payload,
        )
        response.raise_for_status()

    def _configure_tracing(self, record: dict[str, Any]) -> None:
        """Configure tracing settings."""
        payload = {
            "tracingEnabled": record.get("tracingEnabled", True),
            "payloadTracingEnabled": record.get("payloadTracingEnabled", False),
            "traceLevel": record.get("traceLevel", "INFO"),
            "samplingRate": record.get("samplingRate", 1.0),
        }

        response = self.client.put(
            "/ic/api/integration/v1/monitoring/tracing/config",
            json=payload,
        )
        response.raise_for_status()


class IntegrationActionsSink(OICBaseSink):
    """Oracle Integration Cloud target sink for integration actions."""

    name = "integration_actions"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process integration action record."""
        action = record.get("action", "")
        integration_id = record.get("integrationId", "")
        version = record.get("version", "01.00.0000")

        if not integration_id:
            self.logger.warning("No integration ID provided for action")
            return

        if action == "activate":
            self._activate_integration(integration_id, version, record)
        elif action == "deactivate":
            self._deactivate_integration(integration_id, version)
        elif action == "test":
            self._test_integration(integration_id, version, record)
        elif action == "clone":
            self._clone_integration(integration_id, version, record)

    def _activate_integration(
        self, integration_id: str, version: str, record: dict[str, Any]
    ) -> None:
        """Activate an integration."""
        payload = {
            "enableTracing": record.get("enableTracing", False),
            "payloadTracingEnabled": record.get("payloadTracingEnabled", False),
        }

        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}/activate",
            json=payload,
        )
        response.raise_for_status()

    def _deactivate_integration(self, integration_id: str, version: str) -> None:
        """Deactivate an integration."""
        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}/deactivate"
        )
        response.raise_for_status()

    def _test_integration(
        self, integration_id: str, version: str, record: dict[str, Any]
    ) -> None:
        """Test an integration."""
        test_payload = record.get("testPayload", {})

        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}/test",
            json=test_payload,
        )
        response.raise_for_status()

    def _clone_integration(
        self, integration_id: str, version: str, record: dict[str, Any]
    ) -> None:
        """Clone an integration."""
        payload = {
            "name": record.get("newName", f"{integration_id}_clone"),
            "identifier": record.get("newIdentifier", f"{integration_id}_clone"),
            "version": record.get("newVersion", "01.00.0001"),
            "description": record.get("description", "Cloned integration"),
        }

        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}/clone",
            json=payload,
        )
        response.raise_for_status()


class ConnectionActionsSink(OICBaseSink):
    """Oracle Integration Cloud target sink for connection actions."""

    name = "connection_actions"

    def process_record(self, record: dict[str, Any], _context: dict[str, Any]) -> None:
        """Process connection action record."""
        action = record.get("action", "")
        connection_id = record.get("connectionId", "")

        if not connection_id:
            self.logger.warning("No connection ID provided for action")
            return

        if action == "test":
            self._test_connection(connection_id)
        elif action == "refresh_metadata":
            self._refresh_metadata(connection_id)

    def _test_connection(self, connection_id: str) -> None:
        """Test a connection."""
        response = self.client.post(
            f"/ic/api/integration/v1/connections/{connection_id}/test"
        )
        response.raise_for_status()

        # Get test results
        result = response.json()
        if result.get("status") != "SUCCESS":
            self.logger.warning(
                "Connection test failed for %s: %s",
                connection_id,
                result.get("message"),
            )

    def _refresh_metadata(self, connection_id: str) -> None:
        """Refresh connection metadata."""
        response = self.client.post(
            f"/ic/api/integration/v1/connections/{connection_id}/refreshMetadata"
        )
        response.raise_for_status()
