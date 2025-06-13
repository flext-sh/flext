"""OIC API Client.

This module provides a client for interacting with Oracle Integration Cloud endpoints.
"""

import logging

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class OICClient:
    """Client for interacting with Oracle Integration Cloud API endpoints."""

    def __init__(self, base_url: str, username: str, password: str, timeout: int = 60) -> None:
        """Initialize OIC client.

        Args:
            base_url: Base URL for OIC instance
            username: OIC username
            password: OIC password
            timeout: Request timeout in seconds

        """
        self.base_url = base_url.rstrip("/")
        self.auth = HTTPBasicAuth(username, password)
        self.timeout = timeout
        self.session = requests.Session()

    def get_integrations(self) -> list[dict]:
        """Get list of all integrations.

        Returns:
            list of integration configurations

        """
        endpoint = f"{self.base_url}/ic/api/integration/v1/integrations"
        response = self.session.get(endpoint, auth=self.auth, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_integration(self, integration_id: str) -> dict:
        """Get details of a specific integration.

        Args:
            integration_id: ID of the integration

        Returns:
            Integration details

        """
        endpoint = (
            f"{self.base_url}/ic/api/integration/v1/integrations/{integration_id}"
        )
        response = self.session.get(endpoint, auth=self.auth, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def create_endpoint(self, config: dict) -> dict:
        """Create a new endpoint in OIC.

        Args:
            config: Endpoint configuration

        Returns:
            Created endpoint details

        """
        endpoint = f"{self.base_url}/ic/api/integration/v1/connections"
        response = self.session.post(
            endpoint,
            auth=self.auth,
            json=config,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def update_endpoint(self, connection_id: str, config: dict) -> dict:
        """Update an existing endpoint.

        Args:
            connection_id: ID of the connection to update
            config: Updated endpoint configuration

        Returns:
            Updated endpoint details

        """
        endpoint = f"{self.base_url}/ic/api/integration/v1/connections/{connection_id}"
        response = self.session.put(
            endpoint,
            auth=self.auth,
            json=config,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def test_endpoint(self, connection_id: str) -> bool:
        """Test connection to an endpoint.

        Args:
            connection_id: ID of the connection to test

        Returns:
            True if connection successful, False otherwise

        """
        endpoint = (
            f"{self.base_url}/ic/api/integration/v1/connections/{connection_id}/test"
        )
        try:
            response = self.session.post(endpoint, auth=self.auth, timeout=self.timeout)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.exception(f"Error testing endpoint {connection_id}: {e!s}")
            return False
