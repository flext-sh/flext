"""WMS API Client.

This module provides a client for interacting with WMS API.
"""

import logging
import time
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


class WMSClient:
    """Client for interacting with WMS API."""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        tenant_id: str | None = None,
        timeout: int = 60,
    ) -> None:
        """Initialize WMS client.

        Args:
            base_url: Base URL for WMS API
            client_id: OAuth client ID
            client_secret: OAuth client secret
            tenant_id: Tenant ID
            timeout: Request timeout in seconds

        """
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.timeout = timeout

        self.session = requests.Session()
        self.token = None
        self.token_expiry = 0

    def _get_token(self) -> str:
        """Get OAuth token.

        Returns:
            OAuth token

        """
        current_time = time.time()

        # Return cached token if still valid
        if self.token and current_time < self.token_expiry:
            return self.token

        # Get new token
        auth_url = f"{self.base_url}/oauth/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        if self.tenant_id:
            auth_data["scope"] = f"tenant:{self.tenant_id}"

        response = requests.post(auth_url, data=auth_data, timeout=self.timeout)
        response.raise_for_status()

        token_data = response.json()
        self.token = token_data["access_token"]

        # Set token expiry with a 60-second buffer
        expires_in = token_data.get("expires_in", 3600)
        self.token_expiry = current_time + expires_in - 60

        return self.token

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        data: dict | None = None,
        json_data: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        """Make a request to the WMS API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json_data: JSON data
            headers: Request headers

        Returns:
            Response data

        """
        url = urljoin(self.base_url, endpoint)

        # Get token
        token = self._get_token()

        # Prepare headers
        request_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if headers:
            request_headers.update(headers)

        # Make request
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json_data,
            headers=request_headers,
            timeout=self.timeout,
        )

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            logger.warning(f"Rate limited, retrying after {retry_after} seconds")
            time.sleep(retry_after)
            return self.request(method, endpoint, params, data, json_data, headers)

        response.raise_for_status()

        # Parse response
        if response.content:
            return response.json()
        return {}

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a GET request to the WMS API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data

        """
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request to the WMS API.

        Args:
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data

        """
        return self.request("POST", endpoint, json_data=data)

    def put(self, endpoint: str, data: dict) -> dict:
        """Make a PUT request to the WMS API.

        Args:
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data

        """
        return self.request("PUT", endpoint, json_data=data)

    def delete(self, endpoint: str) -> dict:
        """Make a DELETE request to the WMS API.

        Args:
            endpoint: API endpoint

        Returns:
            Response data

        """
        return self.request("DELETE", endpoint)

    def export_data(
        self,
        entity_type: str,
        start_date: str | None = None,
        end_date: str | None = None,
        file_format: str = "json",
    ) -> bytes:
        """Export data from WMS.

        Args:
            entity_type: Entity type (orders, shipments, receipts, inventory)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            file_format: Export format (json, csv)

        Returns:
            Exported data as bytes

        """
        params = {"format": file_format}

        if start_date:
            params["startDate"] = start_date

        if end_date:
            params["endDate"] = end_date

        url = urljoin(self.base_url, f"/export/{entity_type}")

        # Get token
        token = self._get_token()

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/octet-stream",
        }

        # Make request
        response = self.session.get(
            url=url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.content
