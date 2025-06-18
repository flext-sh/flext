"""Authentication for Oracle WMS target."""

import base64
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class WMSAuthenticator:
    """Handle authentication for Oracle WMS API."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize authenticator.

        Args:
        ----
            config: Target configuration

        """
        self.config = config
        self.auth_method = config.get("auth_method", "basic")

        # Token management for OAuth
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        self._refresh_token: Optional[str] = None

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns
        -------
            Dictionary with auth headers

        """
        if self.auth_method == "basic":
            return self._get_basic_auth_headers()
        if self.auth_method == "oauth2":
            return self._get_oauth_headers()
        msg = f"Unsupported auth method: {self.auth_method}"
        raise ValueError(msg)

    def _get_basic_auth_headers(self) -> dict[str, str]:
        """Get basic authentication headers."""
        username = self.config.get("username")
        password = self.config.get("password")

        if not username or not password:
            msg = "Username and password required for basic auth"
            raise ValueError(msg)

        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()

        return {"Authorization": f"Basic {encoded}"}

    def _get_oauth_headers(self) -> dict[str, str]:
        """Get OAuth2 headers."""
        token = self._get_valid_token()
        return {"Authorization": f"Bearer {token}"}

    def _get_valid_token(self) -> str:
        """Get a valid OAuth token, refreshing if needed."""
        if self._access_token and self._is_token_valid():
            return self._access_token

        # Need to get a new token
        self._refresh_oauth_token()
        return self._access_token

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if not self._access_token or not self._token_expires:
            return False

        # Check with 60 second buffer
        return datetime.now(timezone.utc) < self._token_expires

    def _refresh_oauth_token(self) -> None:
        """Refresh OAuth token."""
        token_url = self.config.get("oauth_token_url")
        client_id = self.config.get("oauth_client_id")
        client_secret = self.config.get("oauth_client_secret")
        scope = self.config.get("oauth_scope", "wms.write")

        if not all([token_url, client_id, client_secret]):
            msg = "OAuth2 requires token_url, client_id, and client_secret"
            raise ValueError(msg)

        # Request new token
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    token_url,
                    headers=headers,
                    data=data,
                    timeout=30,
                )
                response.raise_for_status()

                token_data = response.json()
                self._access_token = token_data["access_token"]

                # Calculate expiration with buffer
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires = datetime.now(timezone.utc) + timedelta(
                    seconds=expires_in - 60
                )

                # Store refresh token if provided
                if "refresh_token" in token_data:
                    self._refresh_token = token_data["refresh_token"]

                logger.info("OAuth token refreshed successfully")

        except httpx.HTTPError as e:
            logger.error(f"Failed to refresh OAuth token: {e}")
            msg = f"OAuth token refresh failed: {e}"
            raise ValueError(msg)

    def test_authentication(self, base_url: str) -> bool:
        """Test if authentication is working.

        Args:
        ----
            base_url: WMS API base URL

        Returns:
        -------
            True if authentication works

        """
        try:
            headers = self.get_auth_headers()
            headers.update(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
            )

            # Add WMS headers if configured
            if "company_code" in self.config:
                headers["X-WMS-Company"] = self.config["company_code"]
            if "facility_code" in self.config:
                headers["X-WMS-Facility"] = self.config["facility_code"]

            # Test with entity endpoint
            test_url = f"{base_url}/wms/lgfapi/v10/entity/"

            with httpx.Client() as client:
                response = client.get(
                    test_url,
                    headers=headers,
                    timeout=30,
                )

                if response.status_code == 200:
                    logger.info("Authentication test successful")
                    return True
                if response.status_code == 401:
                    logger.error("Authentication failed: Invalid credentials")
                    return False
                if response.status_code == 403:
                    logger.error("Authentication failed: Insufficient permissions")
                    return False
                logger.warning(f"Unexpected status code: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False
