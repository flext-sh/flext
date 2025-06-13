"""Test fixtures for the flx_adapter_example API client."""

import json
from unittest.mock import MagicMock

import pytest
import responses
from requests import Response

from flx_adapter_example.client import ApiClient
from flx_adapter_example.config import Config


@pytest.fixture
def mock_config() -> Config:
    """Return a mock configuration for testing."""
    return Config(
        url="https://api.example.com",
        username="test_user",
        password="test_password",
        timeout=5,
        verify_ssl=True,
        max_retries=1,
        debug=True,
    )


@pytest.fixture
def api_client(mock_config: Config) -> ApiClient:
    """Return an API client instance with mock configuration."""
    return ApiClient(config=mock_config)


@pytest.fixture
def mock_response() -> Response:
    """Return a mock response object."""
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.text = json.dumps({"result": "success"})
    response.json.return_value = {"result": "success"}
    return response


@pytest.fixture
def response_mocks() -> responses.RequestsMock:
    """Activate the responses library for mocking HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps
