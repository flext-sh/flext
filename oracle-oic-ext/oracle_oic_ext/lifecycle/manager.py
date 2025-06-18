"""Integration lifecycle management for Oracle OIC."""

from __future__ import annotations

from typing import Any

import httpx
import structlog

log = structlog.get_logger()


class LifecycleManager:
    """Manages integration lifecycle operations in Oracle OIC."""

    def __init__(self, base_url: str, auth_config: dict) -> None:
        """Initialize the lifecycle manager."""
        self.base_url = base_url
        self.auth_config = auth_config
        self._client = None
        self._access_token = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if not self._client:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self._get_auth_headers(),
                timeout=60.0,
            )
        return self._client

    def _get_auth_headers(self) -> dict:
        """Get authentication headers."""
        if not self._access_token:
            self._refresh_token()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _refresh_token(self) -> None:
        """Refresh OAuth2 access token."""
        with httpx.Client() as client:
            response = client.post(
                self.auth_config["oauth_token_url"],
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.auth_config["oauth_client_id"],
                    "client_secret": self.auth_config["oauth_client_secret"],
                    "scope": f"{self.base_url}urn:opc:resource:consumer::all",
                },
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]

    def activate_integration(
        self, integration_id: str, version: str = "01.00.0000"
    ) -> dict:
        """Activate an integration."""
        log.info(f"Activating integration: {integration_id}|{version}")

        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}/activate"
        )

        if response.status_code == 200:
            log.info(f"Integration {integration_id}|{version} activated successfully")
            return response.json()
        log.error(
            f"Failed to activate integration {integration_id}|{version}",
            status_code=response.status_code,
            response=response.text,
        )
        response.raise_for_status()
        return None

    def deactivate_integration(
        self, integration_id: str, version: str = "01.00.0000"
    ) -> dict:
        """Deactivate an integration."""
        log.info(f"Deactivating integration: {integration_id}|{version}")

        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}/deactivate"
        )

        if response.status_code == 200:
            log.info(f"Integration {integration_id}|{version} deactivated successfully")
            return response.json()
        log.error(
            f"Failed to deactivate integration {integration_id}|{version}",
            status_code=response.status_code,
            response=response.text,
        )
        response.raise_for_status()
        return None

    def get_integration_status(
        self, integration_id: str, version: str = "01.00.0000"
    ) -> str:
        """Get the status of an integration."""
        response = self.client.get(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}"
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("status", "UNKNOWN")
        log.error(
            f"Failed to get integration status for {integration_id}|{version}",
            status_code=response.status_code,
        )
        return "ERROR"

    def bulk_activate(self, integration_list: list[dict[str, str]]) -> dict[str, Any]:
        """Activate multiple integrations."""
        results = {
            "success": [],
            "failed": [],
        }

        for integration in integration_list:
            integration_id = integration["id"]
            version = integration.get("version", "01.00.0000")

            try:
                self.activate_integration(integration_id, version)
                results["success"].append(f"{integration_id}|{version}")
            except Exception as e:
                log.error(
                    f"Failed to activate {integration_id}|{version}",
                    error=str(e),
                )
                results["failed"].append(
                    {
                        "integration": f"{integration_id}|{version}",
                        "error": str(e),
                    }
                )

        return results

    def bulk_deactivate(self, integration_list: list[dict[str, str]]) -> dict[str, Any]:
        """Deactivate multiple integrations."""
        results = {
            "success": [],
            "failed": [],
        }

        for integration in integration_list:
            integration_id = integration["id"]
            version = integration.get("version", "01.00.0000")

            try:
                self.deactivate_integration(integration_id, version)
                results["success"].append(f"{integration_id}|{version}")
            except Exception as e:
                log.error(
                    f"Failed to deactivate {integration_id}|{version}",
                    error=str(e),
                )
                results["failed"].append(
                    {
                        "integration": f"{integration_id}|{version}",
                        "error": str(e),
                    }
                )

        return results

    def validate_integration(
        self, integration_id: str, version: str = "01.00.0000"
    ) -> dict:
        """Validate an integration configuration."""
        log.info(f"Validating integration: {integration_id}|{version}")

        response = self.client.post(
            f"/ic/api/integration/v1/integrations/{integration_id}|{version}/validate"
        )

        if response.status_code == 200:
            validation_result = response.json()
            if validation_result.get("valid", False):
                log.info(f"Integration {integration_id}|{version} is valid")
            else:
                log.warning(
                    f"Integration {integration_id}|{version} has validation issues",
                    issues=validation_result.get("issues", []),
                )
            return validation_result
        log.error(
            f"Failed to validate integration {integration_id}|{version}",
            status_code=response.status_code,
        )
        response.raise_for_status()
        return None

    def __del__(self) -> None:
        """Clean up resources."""
        if self._client:
            self._client.close()
