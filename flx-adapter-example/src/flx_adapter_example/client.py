"""API client for making HTTP requests.

This module provides a client for making HTTP requests to the API, handling
authentication, retries, and error handling.
"""

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry

from .config import Config, load_config_from_env
from .exceptions import (
    ApiError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    RequestError,
    ResponseError,
)
from .models import FlxResponse

# Set up logger
logger = logging.getLogger(__name__)


class ApiClient:
    """API client for making HTTP requests.

    This client handles authentication, retries, and error handling for API
    requests. It supports both synchronous and asynchronous requests.
    """

    def __init__(
        self,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 60,
        verify_ssl: bool = True,
        max_retries: int = 3,
        retry_backoff: float = 0.5,
        debug: bool = False,
        config: Config | None = None,
    ) -> None:
        """Initialize API client.

        You can provide configuration either through individual parameters or
        through a Config object. If both are provided, individual parameters
        take precedence.

        Args:
        ----
            url: API base URL (optional if config is provided)
            username: API username (optional if config is provided)
            password: API password (optional if config is provided)
            timeout: Request timeout in seconds (default: 60)
            verify_ssl: Whether to verify SSL certificates (default: True)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_backoff: Exponential backoff factor for retries (default: 0.5)
            debug: Enable debug mode (default: False)
            config: Configuration object (optional)

        """
        # Use config object if provided
        if config is None:
            # If individual parameters are not provided, load from environment
            if url is None or username is None or password is None:
                config = load_config_from_env()

        # Set up configuration
        self.url = url or config.url
        self.username = username or config.username
        self.password = password or (
            config.password.get_secret_value() if config else None
        )
        self.timeout = (
            timeout if timeout is not None else (config.timeout if config else 60)
        )
        self.verify_ssl = (
            verify_ssl
            if verify_ssl is not None
            else (config.verify_ssl if config else True)
        )
        self.max_retries = (
            max_retries
            if max_retries is not None
            else (config.max_retries if config else 3)
        )
        self.retry_backoff = (
            retry_backoff
            if retry_backoff is not None
            else (config.retry_backoff if config else 0.5)
        )
        self.debug = debug if debug is not None else (config.debug if config else False)

        # Validate configuration
        if not self.url:
            msg = "API base URL is required"
            raise ConfigurationError(msg)
        if not self.username:
            msg = "API username is required"
            raise ConfigurationError(msg)
        if not self.password:
            msg = "API password is required"
            raise ConfigurationError(msg)

        # Set up session with retry configuration
        self.session = self._create_session()

        # Debug logging
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug(f"Initialized API client for {self.url}")

    def _create_session(self) -> requests.Session:
        """Create and configure a requests session.

        Returns
        -------
            requests.Session: Configured session

        """
        session = requests.Session()

        # Configure authentication
        session.auth = HTTPBasicAuth(self.username, self.password)

        # Configure retries
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Configure default headers
        session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Python API Client/0.1.0",
            },
        )

        return session

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for the given endpoint.

        Args:
        ----
            endpoint: API endpoint path

        Returns:
        -------
            str: Full URL

        """
        # Remove leading slash from endpoint if present
        endpoint = endpoint.removeprefix("/")

        # Combine base URL and endpoint
        return f"{self.url}/{endpoint}"

    def _handle_response(
        self,
        response: requests.Response,
        raw_response: bool = False,
    ) -> FlxResponse:
        """Handle API response.

        Args:
        ----
            response: HTTP response
            raw_response: Whether to return raw response object (default: False)

        Returns:
        -------
            FlxResponse: Processed API response

        Raises:
        ------
            ResponseError: If response contains an error

        """
        status_code = response.status_code

        # Log response in debug mode
        if self.debug:
            logger.debug(f"Response: {status_code} {response.text[:200]}...")

        # Return raw response if requested
        if raw_response:
            return FlxResponse.success_response(response, status_code=status_code)

        # Check for HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            # Try to parse error from response
            error_msg = str(e)
            error_code = None
            error_details = None

            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    error_msg = error_data.get("message", error_msg)
                    error_code = error_data.get("code")
                    error_details = error_data.get("details")
            except (ValueError, KeyError):
                # If we can't parse the response as JSON, use the raw text
                if response.text:
                    error_msg = response.text

            # Raise appropriate error based on status code
            if status_code == 401:
                raise AuthenticationError(
                    error_msg,
                    code=error_code,
                    details=error_details,
                ) from e
            raise ResponseError(
                error_msg,
                status_code=status_code,
                response_body=response.text,
                code=error_code,
                details=error_details,
            ) from e

        # Parse successful response
        try:
            data = response.json() if response.text else None
            return FlxResponse.success_response(data, status_code=status_code)
        except ValueError:
            # If response is not JSON, return text
            return FlxResponse.success_response(response.text, status_code=status_code)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> FlxResponse:
        """Make HTTP request to API.

        Args:
        ----
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters (optional)
            data: Form data (optional)
            json_data: JSON data (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
        -------
            FlxResponse: API response

        Raises:
        ------
            ConnectionError: If there is an issue connecting to the API
            RequestError: If there is an issue with the request
            ResponseError: If the API returns an error response

        """
        url = self._build_url(endpoint)

        # Log request in debug mode
        if self.debug:
            logger.debug(
                f"Request: {method} {url}\nParams: {params}\nJSON: {json_data}\nData: {data}",
            )

        # Prepare request
        request_kwargs = {
            "params": params,
            "timeout": self.timeout,
            "verify": self.verify_ssl,
            **kwargs,
        }

        # Add data or JSON payload
        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            request_kwargs["data"] = data

        # Add headers
        if headers:
            request_kwargs["headers"] = headers

        try:
            response = self.session.request(method, url, **request_kwargs)
            return self._handle_response(response, raw_response=raw_response)
        except requests.ConnectionError as e:
            msg = f"Failed to connect to API: {e!s}"
            raise ConnectionError(msg)
        except requests.Timeout as e:
            msg = f"Request timed out: {e!s}"
            raise ConnectionError(msg)
        except requests.RequestException as e:
            msg = f"Request failed: {e!s}"
            raise RequestError(msg)

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> FlxResponse:
        """Make GET request to API.

        Args:
        ----
            endpoint: API endpoint path
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
        -------
            FlxResponse: API response

        """
        return self._make_request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> FlxResponse:
        """Make POST request to API.

        Args:
        ----
            endpoint: API endpoint path
            data: Form data (optional)
            json_data: JSON data (optional)
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
        -------
            FlxResponse: API response

        """
        return self._make_request(
            "POST",
            endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> FlxResponse:
        """Make PUT request to API.

        Args:
        ----
            endpoint: API endpoint path
            data: Form data (optional)
            json_data: JSON data (optional)
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
        -------
            FlxResponse: API response

        """
        return self._make_request(
            "PUT",
            endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> FlxResponse:
        """Make DELETE request to API.

        Args:
        ----
            endpoint: API endpoint path
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
        -------
            FlxResponse: API response

        """
        return self._make_request(
            "DELETE",
            endpoint,
            params=params,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    def patch(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_response: bool = False,
        **kwargs: Any,
    ) -> FlxResponse:
        """Make PATCH request to API.

        Args:
        ----
            endpoint: API endpoint path
            data: Form data (optional)
            json_data: JSON data (optional)
            params: Query parameters (optional)
            headers: Additional headers (optional)
            raw_response: Whether to return raw response object (default: False)
            **kwargs: Additional arguments to pass to requests

        Returns:
        -------
            FlxResponse: API response

        """
        return self._make_request(
            "PATCH",
            endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            raw_response=raw_response,
            **kwargs,
        )

    @classmethod
    def from_profile(cls, profile_name: str) -> "ApiClient":
        """Create API client from configuration profile.

        Args:
        ----
            profile_name: Name of the profile to load

        Returns:
        -------
            ApiClient: API client instance

        Raises:
        ------
            ValueError: If the profile doesn't exist or is invalid

        """
        from .config import Config

        config = Config.from_profile(profile_name)
        return cls(config=config)

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to API.

        Returns
        -------
            tuple[bool, str]: (success, message)

        """
        try:
            # Try a simple request to test connection
            response = self.get("ping", raw_response=True)
            return True, f"Connection successful (status {response.status_code})"
        except ApiError as e:
            return False, f"Connection failed: {e!s}"
