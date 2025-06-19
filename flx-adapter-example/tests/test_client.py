"""Tests for the ApiClient class."""

from unittest.mock import MagicMock, patch

import pytest
import responses

from flx_adapter_example.client import ApiClient
from flx_adapter_example.config import Config
from flx_adapter_example.exceptions import (
    ApiError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    ResponseError,
)
from flx_adapter_example.models import FlxResponse


class TestApiClient:
    """Test cases for the ApiClient class."""

    def test_initialization(self, mock_config: Config) -> None:
        """Test client initialization with configuration."""
        client = ApiClient(config=mock_config)

        assert client.url == "https://api.example.com"
        assert client.username == "test_user"
        assert client.password == "test_password"
        assert client.timeout == 5
        assert client.verify_ssl is True
        assert client.max_retries == 1
        assert client.debug is True

    def test_initialization_with_parameters(self) -> None:
        """Test client initialization with direct parameters."""
        client = ApiClient(
            url="https://api.test.com",
            username="direct_user",
            password="direct_password",
            timeout=10,
            verify_ssl=False,
        )

        assert client.url == "https://api.test.com"
        assert client.username == "direct_user"
        assert client.password == "direct_password"
        assert client.timeout == 10
        assert client.verify_ssl is False

    def test_initialization_missing_parameters(self) -> None:
        """Test client initialization with missing required parameters."""
        with pytest.raises(ConfigurationError):
            ApiClient(url=None, username=None, password=None)

    def test_build_url(self, api_client: ApiClient) -> None:
        """Test URL building with different endpoint formats."""
        # With leading slash
        assert api_client._build_url("/users") == "https://api.example.com/users"

        # Without leading slash
        assert api_client._build_url("users") == "https://api.example.com/users"

        # With path parameters
        assert api_client._build_url("users/123") == "https://api.example.com/users/123"

    @responses.activate
    def test_get_request_success(self, api_client: ApiClient) -> None:
        """Test successful GET request."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"users": [{"id": 1, "name": "Test User"}]},
            status=200,
        )

        # Make request
        response = api_client.get("users")

        # Verify response
        assert response.success is True
        assert response.data == {"users": [{"id": 1, "name": "Test User"}]}
        assert response.status_code == 200
        assert response.error is None

    @responses.activate
    def test_post_request_success(self, api_client: ApiClient) -> None:
        """Test successful POST request."""
        # Mock response
        responses.add(
            responses.POST,
            "https://api.example.com/users",
            json={"id": 1, "name": "New User"},
            status=201,
        )

        # Make request
        response = api_client.post(
            "users",
            json_data={"name": "New User"},
        )

        # Verify response
        assert response.success is True
        assert response.data == {"id": 1, "name": "New User"}
        assert response.status_code == 201

    @responses.activate
    def test_authentication_error(self, api_client: ApiClient) -> None:
        """Test authentication error handling."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"message": "Authentication failed"},
            status=401,
        )

        # Make request and verify exception
        with pytest.raises(AuthenticationError) as exc:
            api_client.get("users")

        assert "Authentication failed" in str(exc.value)

    @responses.activate
    def test_response_error(self, api_client: ApiClient) -> None:
        """Test response error handling."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"message": "Resource not found", "code": "NOT_FOUND"},
            status=404,
        )

        # Make request and verify exception
        with pytest.raises(ResponseError) as exc:
            api_client.get("users")

        assert "Resource not found" in str(exc.value)
        assert exc.value.status_code == 404
        assert exc.value.code == "NOT_FOUND"

    def test_connection_error(self, api_client: ApiClient) -> None:
        """Test connection error handling."""
        with patch("requests.Session.request") as mock_request:
            mock_request.side_effect = ConnectionError("Failed to connect")

            with pytest.raises(ConnectionError):
                api_client.get("users")

    @responses.activate
    def test_raw_response(self, api_client: ApiClient) -> None:
        """Test raw response handling."""
        # Mock response
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            body="Raw response text",
            status=200,
        )

        # Make request
        response = api_client.get("users", raw_response=True)

        # Verify response contains raw response object
        assert response.success is True
        assert isinstance(response.data, responses.Response)
        assert response.status_code == 200

    def test_from_profile(self) -> None:
        """Test client creation from profile."""
        with patch(
            "flx_adapter_example.config.Config.from_profile"
        ) as mock_from_profile:
            mock_config = MagicMock(spec=Config)
            mock_config.url = "https://api.profile.com"
            mock_config.username = "profile_user"
            mock_config.password.get_secret_value.return_value = "profile_password"
            mock_config.timeout = 15
            mock_config.verify_ssl = True

            mock_from_profile.return_value = mock_config

            client = ApiClient.from_profile("test_profile")

            assert client.url == "https://api.profile.com"
            assert client.username == "profile_user"
            assert client.password == "profile_password"
            assert client.timeout == 15
            assert client.verify_ssl is True

            mock_from_profile.assert_called_once_with("test_profile")

    def test_test_connection_success(self, api_client: ApiClient) -> None:
        """Test successful connection test."""
        with patch.object(api_client, "get") as mock_get:
            mock_response = MagicMock(spec=FlxResponse)
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            success, message = api_client.test_connection()

            assert success is True
            assert "Connection successful" in message
            mock_get.assert_called_once_with("ping", raw_response=True)

    def test_test_connection_failure(self, api_client: ApiClient) -> None:
        """Test failed connection test."""
        with patch.object(api_client, "get") as mock_get:
            mock_get.side_effect = ApiError("Connection failed")

            success, message = api_client.test_connection()

            assert success is False
            assert "Connection failed" in message
