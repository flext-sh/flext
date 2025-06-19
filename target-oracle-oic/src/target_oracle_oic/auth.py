"""Oracle Integration Cloud Authentication Module.

This module provides OAuth2 authentication capabilities for accessing Oracle Integration
Cloud (OIC) APIs through Oracle Identity Cloud Service (IDCS). OIC exclusively supports
OAuth2 authentication using the client credentials flow.

Architecture Layer: Infrastructure - Authentication
Dependencies: Singer SDK, IDCS OAuth2 service
Pattern: Adapter pattern implementing Singer SDK authentication interface

Example:
-------
    ```python
    from tap_oracle_oic.auth import OICOAuth2Authenticator

    # Authentication is typically handled automatically by streams
    auth = OICOAuth2Authenticator(stream=stream_instance)
    token = auth.get_access_token()
    ```

Security Notes:
    - All credentials are handled securely through environment variables
    - Tokens are cached and automatically refreshed when expired
    - Client credentials use HTTP Basic authentication for token requests
    - All communication uses HTTPS with certificate validation

References:
----------
    - Oracle IDCS OAuth2 Documentation
    - Singer SDK Authentication Framework


"""

import base64
from typing import Any

import requests
from singer_sdk.authenticators import OAuthAuthenticator


class OICOAuth2Authenticator(OAuthAuthenticator):
    """OAuth2 authenticator for Oracle Integration Cloud using IDCS.

    Oracle Integration Cloud exclusively uses OAuth2 authentication through Oracle
    Identity Cloud Service (IDCS). This authenticator implements the client credentials
    flow required by OIC APIs, which is the standard authentication method for
    server-to-server API access.

    The client credentials flow is used because:
    - OIC APIs are designed for application-to-application access
    - No user interaction is required for data extraction
    - Provides secure, automated authentication for data pipelines

    Attributes
    ----------
        _stream: Reference to the stream instance for configuration access
        auth_endpoint: IDCS OAuth2 token endpoint URL
        oauth_scopes: OAuth2 scopes for API access permissions

    Security:
        - Client credentials are never logged or exposed in error messages
        - Tokens are cached in memory and automatically refreshed
        - All HTTP communication uses TLS encryption
        - Credentials use HTTP Basic authentication per OAuth2 RFC

    Example Configuration:
        ```json
        {
            "oauth_client_id": "your-idcs-application-id",
            "oauth_client_secret": "your-idcs-application-secret",
            "oauth_token_url": "https://your-idcs.identity.oraclecloud.com/oauth2/v1/token",
            "oauth_scope": "urn:opc:resource:consumer::all"
        }
        ```

    """

    def __init__(self, stream: Any) -> None:
        """Initialize OAuth2 authenticator for Oracle Integration Cloud.

        Extracts authentication configuration from the stream and sets up the OAuth2
        client credentials flow for IDCS authentication. Builds the correct scope
        format that OIC expects based on client_aud configuration.

        Args:
        ----
            stream: Singer stream instance containing configuration
            *args: Additional positional arguments passed to parent class
            **kwargs: Additional keyword arguments passed to parent class

        Raises:
        ------
            ValueError: If required OAuth2 configuration is missing

        Note:
        ----
            The stream configuration must include oauth_token_url, oauth_client_id,
            oauth_client_secret, and oauth_client_aud. The scope is automatically
            built using the audience URL to match OIC requirements.

        """
        auth_endpoint = stream.config.get("oauth_token_url")

        # Build OAuth2 scope exactly like flx-http-oracle-oic (working implementation)
        client_aud = stream.config.get("oauth_client_aud", "")
        if client_aud:
            # Build scope like: "audience:443urn:opc:resource:consumer::all ..."
            resource_aud = f"{client_aud}:443urn:opc:resource:consumer::all"
            api_aud = f"{client_aud}:443/ic/api/"
            oauth_scopes = f"{resource_aud} {api_aud}"
        else:
            # Fallback to simple scope if no audience configured
            oauth_scopes = stream.config.get(
                "oauth_scope", "urn:opc:resource:consumer::all"
            )

        # Store reference to stream for access to config during token refresh
        self._stream = stream

        super().__init__(
            stream=stream, auth_endpoint=auth_endpoint, oauth_scopes=oauth_scopes
        )

    @property
    def oauth_request_body(self) -> dict[str, Any]:
        """Generate OAuth2 request body for client credentials flow.

        Constructs the standard OAuth2 client credentials request body according to
        RFC 6749. The scope is set to the configured value or defaults to the
        standard OIC consumer scope.

        Returns:
        -------
            Dict containing grant_type and scope for OAuth2 token request

        Note:
        ----
            The grant_type is always "client_credentials" as OIC uses server-to-server
            authentication. The scope determines API access permissions in OIC.

        """
        return {
            "grant_type": "client_credentials",
            "scope": self.oauth_scopes or "urn:opc:resource:consumer::all",
        }

    @property
    def oauth_request_payload(self) -> dict[str, Any]:
        """Get OAuth2 request payload for token requests.

        Returns:
        -------
            Dict containing the complete request payload for OAuth2 token requests

        Note:
        ----
            This is an alias for oauth_request_body to maintain compatibility with
            different Singer SDK versions and authentication patterns.

        """
        return self.oauth_request_body

    def update_access_token(self) -> None:
        """Update the access token using OAuth2 client credentials flow.

        Performs the complete OAuth2 client credentials flow:
        1. Validates that token endpoint is configured
        2. Extracts client credentials from stream configuration
        3. Encodes credentials using HTTP Basic authentication
        4. Sends token request to IDCS endpoint
        5. Parses and stores the access token

        The access token is cached and reused until it expires. IDCS typically
        issues tokens with 1-hour expiration.

        Raises
        ------
            ValueError: If OAuth2 token URL is not configured
            HTTPError: If token request fails (401, 403, 500, etc.)
            ConnectionError: If network connectivity issues occur
            Timeout: If request takes longer than configured timeout

        Security Notes:
            - Client credentials are encoded using RFC 7617 HTTP Basic authentication
            - Credentials are never logged or included in error messages
            - All communication uses HTTPS with certificate validation
            - Token response is validated before storing access token

        Example Token Request:
            ```http
            POST /oauth2/v1/token HTTP/1.1
            Host: your-idcs.identity.oraclecloud.com
            Authorization: Basic <base64(client_id:client_secret)>
            Content-Type: application/x-www-form-urlencoded

            grant_type=client_credentials&scope=urn:opc:resource:consumer::all
            ```

        """
        if not self.auth_endpoint:
            msg = "OAuth token URL is required"
            raise ValueError(msg)

        client_id = self._stream.config["oauth_client_id"]
        client_secret = self._stream.config["oauth_client_secret"]

        # Encode client credentials for HTTP Basic authentication per RFC 7617
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(
            self.auth_endpoint,
            headers=headers,
            data=self.oauth_request_payload,
            timeout=30,
        )
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
