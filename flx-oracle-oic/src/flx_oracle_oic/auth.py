"""Comprehensive authentication system for Oracle Integration Cloud.

This module provides a complete authentication system supporting:
- OAuth2 Client Credentials flow
- JWT Token authentication
- IDCS authentication
- Token refresh and caching
- Multiple authentication strategies
"""

import base64
import hashlib
import logging
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

from .config import OracleOicConfig

if TYPE_CHECKING:
    from .adapter import OracleOicHttpAdapter

from .constants import APPLICATION_JSON, JWT_SCOPE_DEFAULT

logger = logging.getLogger(__name__)


class AuthToken(BaseModel):
    """Authentication token with metadata."""

    access_token: str = Field(..., description="The actual access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token expiration in seconds")
    expires_at: datetime | None = Field(
        default=None,
        description="Absolute expiration time",
    )
    scope: str | None = Field(default=None, description="Token scope")
    refresh_token: str | None = Field(
        default=None,
        description="Refresh token if available",
    )

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # Calculate expires_at if not provided
        if self.expires_at is None:
            self.expires_at = datetime.now(UTC) + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 5-minute buffer)."""
        if self.expires_at is None:
            return True
        buffer_time = timedelta(minutes=5)
        return datetime.now(UTC) >= (self.expires_at - buffer_time)

    @property
    def authorization_header(self) -> str:
        """Get the authorization header value."""
        return f"{self.token_type} {self.access_token}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for caching."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "scope": self.scope,
            "refresh_token": self.refresh_token,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuthToken":
        """Create from dictionary (for caching)."""
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)


class AuthenticationError(Exception):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class AuthStrategy(ABC):
    """Abstract base class for authentication strategies."""

    def __init__(
        self,
        config: OracleOicConfig,
        adapter: Optional["OracleOicHttpAdapter"] = None,
    ) -> None:
        self.config = config
        self.adapter = adapter
        self._cache: dict[str, AuthToken] = {}

    @abstractmethod
    async def authenticate(self, *, force_refresh: bool = False) -> AuthToken:
        """Perform authentication and return token."""

    @abstractmethod
    def get_cache_key(self) -> str:
        """Generate cache key for this authentication context."""

    def _get_cached_token(self) -> AuthToken | None:
        """Get cached token if valid."""
        cache_key = self.get_cache_key()
        if cache_key in self._cache:
            token = self._cache[cache_key]
            if not token.is_expired:
                logger.debug("Using cached auth token")
                return token
            logger.debug("Cached token expired, removing from cache")
            del self._cache[cache_key]
        return None

    def _cache_token(self, token: AuthToken) -> None:
        """Cache the token."""
        cache_key = self.get_cache_key()
        self._cache[cache_key] = token
        logger.debug("Cached auth token until %s", token.expires_at)


class OAuth2ClientCredentialsStrategy(AuthStrategy):
    """OAuth2 Client Credentials authentication strategy."""

    def get_cache_key(self) -> str:
        """Generate cache key based on client credentials."""
        key_data = (
            f"{self.config.client_id}:{self.config.oauth_url}:{self.config.oauth_scope}"
        )
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def authenticate(self, *, force_refresh: bool = False) -> AuthToken:
        """Perform OAuth2 client credentials authentication."""
        if not force_refresh:
            cached_token = self._get_cached_token()
            if cached_token:
                return cached_token

        logger.info("Performing OAuth2 client credentials authentication")

        # Prepare client credentials
        client_credentials = (
            f"{self.config.client_id}:{self.config.client_secret.get_secret_value()}"
        )
        basic_auth = base64.b64encode(client_credentials.encode()).decode()

        # Prepare request
        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept": APPLICATION_JSON,
        }

        data = {
            "grant_type": "client_credentials",
            "scope": self.config.oauth_scope,
        }

        # Convert form data to URL-encoded string
        form_data = "&".join([f"{k}={v}" for k, v in data.items()])

        try:
            # We'll need to use the HTTP client from the adapter
            # For now, this is a placeholder - the actual HTTP call should be made by the adapter
            response_data = await self._make_token_request(
                url=self.config.oauth_url,
                headers=headers,
                data=form_data,
            )

            if "access_token" not in response_data:
                msg = "OAuth2 authentication failed: No access_token in response"
                raise AuthenticationError(
                    msg,
                    error_code="MISSING_ACCESS_TOKEN",
                    details=response_data,
                )

            # Create token from response
            token = AuthToken(
                access_token=response_data["access_token"],
                token_type=response_data.get("token_type", "Bearer"),
                expires_in=response_data.get("expires_in", 3600),
                scope=response_data.get("scope"),
            )

            # Cache the token
            self._cache_token(token)

            logger.info(
                "OAuth2 authentication successful, token expires at %s",
                token.expires_at,
            )
            return token

        except Exception as e:
            error_msg = f"OAuth2 authentication failed: {e}"
            logger.exception(error_msg)
            raise AuthenticationError(error_msg, error_code="OAUTH2_FAILED") from e

    async def _make_token_request(
        self,
        url: str,
        headers: dict[str, str],
        data: str,
    ) -> dict[str, Any]:
        """Make the actual HTTP request for token."""
        if self.adapter is None:
            msg = "No adapter available for token request"
            raise AuthenticationError(
                msg,
                error_code="NO_ADAPTER",
            )

        return await self.adapter._make_token_request(url, headers, data)


class JWTAuthStrategy(AuthStrategy):
    """JWT Token authentication strategy."""

    def __init__(
        self,
        config: OracleOicConfig,
        adapter: Optional["OracleOicHttpAdapter"] = None,
        jwt_token: str = "",
    ) -> None:
        super().__init__(config, adapter)
        self.jwt_token = jwt_token

    def get_cache_key(self) -> str:
        """Generate cache key based on JWT token."""
        # Use hash of JWT to avoid storing full token in cache key
        return hashlib.sha256(self.jwt_token.encode()).hexdigest()

    async def authenticate(self, *, force_refresh: bool = False) -> AuthToken:
        """Use provided JWT token directly."""
        if not force_refresh:
            cached_token = self._get_cached_token()
            if cached_token:
                return cached_token

        logger.info("Using JWT token authentication")

        try:
            # Parse JWT to get expiration (optional)
            expires_in = self._get_jwt_expiration()

            token = AuthToken(
                access_token=self.jwt_token,
                token_type="Bearer",
                expires_in=expires_in,
                scope=JWT_SCOPE_DEFAULT,
            )

            # Cache the token
            self._cache_token(token)

            logger.info("JWT authentication successful")
            return token

        except Exception as e:
            error_msg = f"JWT authentication failed: {e}"
            logger.exception(error_msg)
            raise AuthenticationError(error_msg, error_code="JWT_FAILED") from e

    def _get_jwt_expiration(self) -> int:
        """Extract expiration from JWT token."""
        try:
            import jwt  # type: ignore[import-untyped]

            # Decode without verification to get expiration
            decoded = jwt.decode(self.jwt_token, options={"verify_signature": False})

            if "exp" in decoded:
                exp_timestamp = decoded["exp"]
                now_timestamp = int(time.time())
                return max(0, exp_timestamp - now_timestamp)

        except Exception as e:
            logger.warning("Could not parse JWT expiration: %s", e)

        # Default to 1 hour if we can't parse expiration
        return 3600


class IDCSAuthStrategy(AuthStrategy):
    """IDCS (Identity Cloud Service) authentication strategy."""

    def get_cache_key(self) -> str:
        """Generate cache key based on IDCS configuration."""
        key_data = (
            f"{self.config.client_id}:{self.config.idcs_url}:{self.config.client_aud}"
        )
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def authenticate(self, *, force_refresh: bool = False) -> AuthToken:
        """Perform IDCS authentication using exact same method as bash script."""
        if not force_refresh:
            cached_token = self._get_cached_token()
            if cached_token:
                return cached_token

        logger.info("Performing IDCS authentication")

        if not self.config.idcs_url:
            msg = "IDCS authentication requires idcs_url to be configured"
            raise AuthenticationError(
                msg,
                error_code="MISSING_IDCS_URL",
            )

        # Use exact same OAuth2 flow as bash script
        oauth_url = f"{self.config.idcs_url}/oauth2/v1/token"

        # Generate Basic Auth exactly like bash script
        client_credentials = (
            f"{self.config.client_id}:{self.config.client_secret.get_secret_value()}"
        )
        basic_auth = base64.b64encode(client_credentials.encode()).decode()

        # Build OAuth2 scope exactly like bash script
        resource_aud = f"{self.config.client_aud}:443urn:opc:resource:consumer::all"
        api_aud = f"{self.config.client_aud}:443/ic/api/"
        oauth_scope = f"{resource_aud} {api_aud}"

        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }

        data = f"grant_type=client_credentials&scope={oauth_scope}"

        try:
            response_data = await self._make_token_request(
                url=oauth_url,
                headers=headers,
                data=data,
            )

            if "access_token" not in response_data:
                msg = "IDCS authentication failed: No access_token in response"
                raise AuthenticationError(
                    msg,
                    error_code="MISSING_ACCESS_TOKEN",
                    details=response_data,
                )

            token = AuthToken(
                access_token=response_data["access_token"],
                token_type=response_data.get("token_type", "Bearer"),
                expires_in=response_data.get("expires_in", 3600),
                scope=response_data.get("scope"),
            )

            self._cache_token(token)

            logger.info(
                "IDCS authentication successful, token expires at %s",
                token.expires_at,
            )
            return token

        except Exception as e:
            error_msg = f"IDCS authentication failed: {e}"
            logger.exception(error_msg)
            raise AuthenticationError(error_msg, error_code="IDCS_FAILED") from e

    async def _make_token_request(
        self,
        url: str,
        headers: dict[str, str],
        data: str,
    ) -> dict[str, Any]:
        """Make the actual HTTP request for token."""
        if self.adapter is None:
            msg = "No adapter available for token request"
            raise AuthenticationError(
                msg,
                error_code="NO_ADAPTER",
            )

        return await self.adapter._make_token_request(url, headers, data)


class OAuth2AuthStrategy(AuthStrategy):
    """OAuth2 Client Credentials authentication strategy."""

    def get_cache_key(self) -> str:
        """Generate cache key based on OAuth2 configuration."""
        key_data = f"{self.config.client_id}:{self.config.oauth_url}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def authenticate(self, *, force_refresh: bool = False) -> AuthToken:
        """Perform OAuth2 Client Credentials authentication."""
        if not force_refresh:
            cached_token = self._get_cached_token()
            if cached_token:
                return cached_token

        logger.info("Performing OAuth2 authentication")

        client_assertion = self._create_client_assertion()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": APPLICATION_JSON,
        }

        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": client_assertion,
            "scope": self.config.oauth_scope,
        }

        form_data = "&".join([f"{k}={v}" for k, v in data.items()])

        try:
            response_data = await self._make_token_request(
                url=self.config.oauth_url,
                headers=headers,
                data=form_data,
            )

            if "access_token" not in response_data:
                msg = "OAuth2 authentication failed: No access_token in response"
                raise AuthenticationError(
                    msg,
                    error_code="MISSING_ACCESS_TOKEN",
                    details=response_data,
                )

            token = AuthToken(
                access_token=response_data["access_token"],
                token_type=response_data.get("token_type", "Bearer"),
                expires_in=response_data.get("expires_in", 3600),
                scope=response_data.get("scope"),
            )

            self._cache_token(token)

            logger.info(
                "OAuth2 authentication successful, token expires at %s",
                token.expires_at,
            )
            return token

        except Exception as e:
            error_msg = f"OAuth2 authentication failed: {e}"
            logger.exception(error_msg)
            raise AuthenticationError(error_msg, error_code="OAUTH2_FAILED") from e

    def _create_client_assertion(self) -> str:
        """Create JWT client assertion for OAuth2."""
        try:
            import jwt  # type: ignore[import-untyped]

            now = int(time.time())

            payload = {
                "iss": self.config.client_id,  # Issuer
                "sub": self.config.client_id,  # Subject
                "aud": self.config.oauth_url,  # Audience
                "iat": now,  # Issued at
                "exp": now + 300,  # Expires in 5 minutes
                "jti": hashlib.sha256(
                    f"{self.config.client_id}{now}".encode(),
                ).hexdigest()[:16],  # Unique ID
            }

            # Sign with client secret
            return jwt.encode(
                payload,
                self.config.client_secret.get_secret_value(),
                algorithm="HS256",
            )

        except ImportError:
            msg = "OAuth2 authentication requires PyJWT library. Install with: pip install PyJWT"
            raise AuthenticationError(
                msg,
                error_code="MISSING_PYJWT",
            ) from None
        except Exception as e:
            msg = f"Failed to create client assertion: {e}"
            raise AuthenticationError(
                msg,
                error_code="CLIENT_ASSERTION_FAILED",
            ) from e

    async def _make_token_request(
        self,
        url: str,
        headers: dict[str, str],
        data: str,
    ) -> dict[str, Any]:
        """Make the actual HTTP request for token."""
        if self.adapter is None:
            msg = "No adapter available for token request"
            raise AuthenticationError(
                msg,
                error_code="NO_ADAPTER",
            )

        return await self.adapter._make_token_request(url, headers, data)


class OICAuthenticator:
    """Main authenticator class that manages different authentication strategies."""

    def __init__(
        self,
        config: OracleOicConfig,
        adapter: Optional["OracleOicHttpAdapter"] = None,
    ) -> None:
        self.config = config
        self.adapter = adapter
        self._strategy: AuthStrategy | None = None
        self._current_token: AuthToken | None = None

    def use_oauth2_strategy(self) -> None:
        """Use OAuth2 Client Credentials authentication strategy."""
        self._strategy = OAuth2ClientCredentialsStrategy(self.config, self.adapter)
        logger.debug("Using OAuth2 Client Credentials authentication strategy")

    def use_jwt_strategy(self, jwt_token: str) -> None:
        """Use JWT token authentication strategy."""
        self._strategy = JWTAuthStrategy(self.config, self.adapter, jwt_token)
        logger.debug("Using JWT authentication strategy")

    def use_idcs_strategy(self) -> None:
        """Use IDCS authentication strategy."""
        self._strategy = IDCSAuthStrategy(self.config, self.adapter)
        logger.debug("Using IDCS authentication strategy")

    def auto_select_strategy(self) -> None:
        """Automatically select the best authentication strategy based on configuration."""
        if self.config.idcs_url and self.config.client_aud:
            logger.debug("Auto-selecting IDCS authentication strategy")
            self.use_idcs_strategy()
        elif self.config.client_id and self.config.client_secret:
            logger.debug(
                "Auto-selecting OAuth2 Client Credentials authentication strategy",
            )
            self.use_oauth2_strategy()
        else:
            msg = (
                "No valid authentication configuration found. "
                "Please configure client_id/client_secret or idcs_url/client_aud"
            )
            raise AuthenticationError(
                msg,
                error_code="NO_AUTH_CONFIG",
            )

    async def authenticate(self, *, force_refresh: bool = False) -> AuthToken:
        """Perform authentication using the selected strategy."""
        if self._strategy is None:
            self.auto_select_strategy()

        if self._strategy is None:
            msg = "No authentication strategy selected"
            raise AuthenticationError(
                msg,
                error_code="NO_STRATEGY",
            )

        self._current_token = await self._strategy.authenticate(force_refresh)
        return self._current_token

    async def get_valid_token(self) -> AuthToken:
        """Get a valid token, refreshing if necessary."""
        if self._current_token is None or self._current_token.is_expired:
            return await self.authenticate(force_refresh=True)
        return self._current_token

    def get_authorization_header(self) -> str | None:
        """Get the current authorization header value."""
        if self._current_token and not self._current_token.is_expired:
            return self._current_token.authorization_header
        return None

    async def refresh_token(self) -> AuthToken:
        """Force refresh the current token."""
        return await self.authenticate(force_refresh=True)

    def clear_cache(self) -> None:
        """Clear all cached tokens."""
        if self._strategy:
            self._strategy._cache.clear()
        self._current_token = None
        logger.debug("Authentication cache cleared")
