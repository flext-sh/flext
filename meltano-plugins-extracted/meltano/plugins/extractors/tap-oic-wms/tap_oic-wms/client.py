"""REST client for WMS API."""

import requests
from singer_sdk.authenticators import BasicAuthenticator


class WMSClient:
    """Oracle WMS client."""

    def __init__(self, config) -> None:
        """Initialize client."""
        self.wms_url = config["wms_url"]
        self.username = config["username"]
        self.password = config["password"]
        self.company_code = config.get("company_code")
        self.facility_code = config.get("facility_code")
        self.extraction_mode = config.get("extraction_mode", "api")
        self.sftp_config = config.get("sftp_config", {})
        self.webhook_config = config.get("webhook_config", {})

        self._session = requests.Session()
        self._session.auth = (self.username, self.password)
        self._session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"},
        )

    def get_authenticator(self):
        """Get authenticator."""
        return BasicAuthenticator(
            stream=None,
            auth_endpoint=None,
            username=self.username,
            password=self.password,
        )

    def request(self, method, endpoint, **kwargs):
        """Make a request to the WMS API."""
        url = f"{self.wms_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = self._session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
