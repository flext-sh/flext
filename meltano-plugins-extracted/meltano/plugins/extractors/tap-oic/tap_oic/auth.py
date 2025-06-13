"""Authentication classes for OIC."""

import base64
import time

import requests
from singer_sdk.authenticators import APIAuthenticatorBase


class OAuth2Authenticator(APIAuthenticatorBase):
    """Authenticator class for OAuth2."""

    def __init__(self, client) -> None:
        """Initialize authenticator."""
        super().__init__(stream=None)
        self.client = client
        self.token = None
        self.expires_at = 0

    def is_token_valid(self):
        """Check if token is valid."""
        return self.token and time.time() < self.expires_at - 60

    def update_token(self) -> None:
        """Update token."""
        auth_string = f"{self.client.client_id}:{self.client.client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_auth}",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": f"{self.client.resource_aud} {self.client.api_aud}",
        }

        url = f"https://{self.client.idcs_url}/oauth2/v1/token"
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.token = token_data["access_token"]
        self.expires_at = time.time() + token_data["expires_in"]

    def auth_headers(self):
        """Return authorization headers."""
        if not self.is_token_valid():
            self.update_token()
        return {"Authorization": f"Bearer {self.token}"}
