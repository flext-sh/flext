"""Oracle Integration Cloud Health Check Utilities.

This module provides health checking capabilities for OIC connections,
integrations, and the overall OIC instance health.
"""

from datetime import datetime, timezone
from typing import Any

import requests
from singer_sdk.authenticators import OAuthAuthenticator


class OICHealthChecker:
    """Health check utilities for Oracle Integration Cloud."""

    def __init__(self, base_url: str, authenticator: OAuthAuthenticator) -> None:
        """Initialize health checker.

        Args:
        ----
            base_url: OIC instance base URL
            authenticator: OAuth2 authenticator instance

        """
        self.base_url = base_url.rstrip("/")
        self.authenticator = authenticator

    def _get_headers(self) -> dict[str, str]:
        """Get authenticated headers."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        # Add auth header
        auth_headers = self.authenticator.auth_headers
        if auth_headers:
            headers.update(auth_headers)
        return headers

    def check_instance_health(self) -> dict[str, Any]:
        """Check overall OIC instance health.

        Returns
        -------
            Dictionary with health status information

        """
        try:
            # Try to access the integrations endpoint as a health check
            url = f"{self.base_url}/ic/api/integration/v1/integrations?limit=1"
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "instance_url": self.base_url,
                    "api_accessible": True,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
            return {
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "instance_url": self.base_url,
                "api_accessible": False,
                "error": f"API returned status {response.status_code}",
                "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            }
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "instance_url": self.base_url,
                "api_accessible": False,
                "error": str(e),
            }

    def test_connection(self, connection_id: str) -> dict[str, Any]:
        """Test a specific connection's health.

        Args:
        ----
            connection_id: ID of the connection to test

        Returns:
        -------
            Dictionary with connection test results

        """
        try:
            # Call the connection test endpoint
            url = f"{self.base_url}/ic/api/integration/v1/connections/{connection_id}/test"
            response = requests.post(url, headers=self._get_headers(), timeout=60)

            if response.status_code in {200, 202}:
                result = response.json() if response.text else {}
                return {
                    "connectionId": connection_id,
                    "status": result.get("status", "success"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "testResult": result.get(
                        "testResult", "Connection test successful"
                    ),
                    "details": result.get("details", {}),
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
            return {
                "connectionId": connection_id,
                "status": "failed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": f"Test failed with status {response.status_code}",
                "details": response.text if response.text else {},
                "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            }
        except Exception as e:
            return {
                "connectionId": connection_id,
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def check_integration_health(self, integration_id: str) -> dict[str, Any]:
        """Check a specific integration's health and status.

        Args:
        ----
            integration_id: ID of the integration to check

        Returns:
        -------
            Dictionary with integration health information

        """
        try:
            # Get integration details
            url = f"{self.base_url}/ic/api/integration/v1/integrations/{integration_id}"
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                integration = response.json()
                status = integration.get("status", "UNKNOWN")

                # Determine health based on status
                if status == "ACTIVATED":
                    health_status = "healthy"
                elif status in {"CONFIGURED", "DRAFT"}:
                    health_status = "inactive"
                elif status in {"ERROR", "FAILED"}:
                    health_status = "unhealthy"
                else:
                    health_status = "unknown"

                return {
                    "integrationId": integration_id,
                    "name": integration.get("name"),
                    "status": status,
                    "health": health_status,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": integration.get("version"),
                    "lastUpdated": integration.get("timeUpdated"),
                    "errorDetails": integration.get("errorDetails"),
                }
            return {
                "integrationId": integration_id,
                "health": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": f"Failed to get integration status: {response.status_code}",
            }
        except Exception as e:
            return {
                "integrationId": integration_id,
                "health": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def check_monitoring_health(self) -> dict[str, Any]:
        """Check monitoring service health.

        Returns
        -------
            Dictionary with monitoring service health status

        """
        try:
            # Try to access monitoring endpoint
            url = f"{self.base_url}/ic/api/monitoring/v1/instances?limit=1"
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                return {
                    "service": "monitoring",
                    "status": "healthy",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "accessible": True,
                    "response_time_ms": int(response.elapsed.total_seconds() * 1000),
                }
            return {
                "service": "monitoring",
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "accessible": False,
                "error": f"API returned status {response.status_code}",
            }
        except Exception as e:
            return {
                "service": "monitoring",
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "accessible": False,
                "error": str(e),
            }
