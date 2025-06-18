"""Tests for TAP OIC utility modules.

Tests individual utility functions extracted from god functions to ensure
they work correctly in isolation and can be tested independently.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from tap_oic.utils.auth_utils import (
    find_tap_authenticator,
    get_authenticator_token,
    get_fresh_access_token,
    refresh_access_token,
    validate_token,
)
from tap_oic.utils.file_utils import (
    clean_filename,
    create_directory_structure,
    save_artifact_summary,
    save_binary_file,
    save_json_data,
)
from tap_oic.utils.oic_api_client import OICAPIClient
from tap_oic.utils.stream_categorizer import StreamCategorizer


class TestStreamCategorizer:
    """Test stream categorization utility functions."""

    def test_categorize_streams_core_streams(self) -> None:
        """Test categorization of core streams."""
        # Mock stream objects
        integrations_stream = Mock()
        integrations_stream.name = "integrations"
        connections_stream = Mock()
        connections_stream.name = "connections"
        packages_stream = Mock()
        packages_stream.name = "packages"

        streams = [integrations_stream, connections_stream, packages_stream]
        categorized = StreamCategorizer.categorize_streams(streams)

        assert "core" in categorized
        assert len(categorized["core"]) == 3
        assert integrations_stream in categorized["core"]
        assert connections_stream in categorized["core"]
        assert packages_stream in categorized["core"]

    def test_categorize_streams_monitoring_streams(self) -> None:
        """Test categorization of monitoring streams."""
        monitoring_stream = Mock()
        monitoring_stream.name = "monitoring_instances"
        audit_stream = Mock()
        audit_stream.name = "audit_records"

        streams = [monitoring_stream, audit_stream]
        categorized = StreamCategorizer.categorize_streams(streams)

        assert "monitoring" in categorized
        assert len(categorized["monitoring"]) == 2

    def test_get_stream_category_core(self) -> None:
        """Test getting category for core stream names."""
        assert StreamCategorizer._get_stream_category("integrations") == "core"
        assert StreamCategorizer._get_stream_category("connections") == "core"
        assert StreamCategorizer._get_stream_category("packages") == "core"

    def test_get_stream_category_infrastructure_default(self) -> None:
        """Test default categorization to infrastructure."""
        assert (
            StreamCategorizer._get_stream_category("unknown_stream") == "infrastructure"
        )

    def test_get_category_summary(self) -> None:
        """Test getting category summary counts."""
        categorized = {
            "core": [Mock(), Mock(), Mock()],
            "monitoring": [Mock()],
            "infrastructure": [Mock(), Mock()],
        }
        summary = StreamCategorizer.get_category_summary(categorized)

        assert summary["core"] == 3
        assert summary["monitoring"] == 1
        assert summary["infrastructure"] == 2

    def test_filter_streams_by_category(self) -> None:
        """Test filtering streams by category."""
        # Create mock streams
        integrations_stream = Mock()
        integrations_stream.name = "integrations"
        libraries_stream = Mock()
        libraries_stream.name = "libraries"
        monitoring_stream = Mock()
        monitoring_stream.name = "monitoring_instances"

        streams = [integrations_stream, libraries_stream, monitoring_stream]
        filtered = StreamCategorizer.filter_streams_by_category(streams, ["core"])

        assert len(filtered) == 1
        assert integrations_stream in filtered


class TestAuthUtils:
    """Test authentication utility functions."""

    def test_validate_token_valid(self) -> None:
        """Test validation of valid tokens."""
        valid_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9"
        assert validate_token(valid_token) is True

    def test_validate_token_invalid(self) -> None:
        """Test validation of invalid tokens."""
        assert validate_token("") is False
        assert validate_token(None) is False
        assert validate_token("short") is False
        assert validate_token(123) is False

    def test_get_authenticator_token_direct_access(self) -> None:
        """Test getting token from authenticator with direct access_token attribute."""
        mock_auth = Mock()
        mock_auth.access_token = "test_token_12345678901234567890"

        token = get_authenticator_token(mock_auth)
        assert token == "test_token_12345678901234567890"

    def test_get_authenticator_token_from_headers(self) -> None:
        """Test getting token from authenticator auth headers."""
        mock_auth = Mock()
        mock_auth.access_token = None
        mock_auth.auth_headers = {"Authorization": "Bearer test_header_token_123456"}

        token = get_authenticator_token(mock_auth)
        assert token == "test_header_token_123456"

    def test_get_authenticator_token_none(self) -> None:
        """Test getting token when none available."""
        mock_auth = Mock()
        mock_auth.access_token = None
        mock_auth.auth_headers = {}

        token = get_authenticator_token(mock_auth)
        assert token is None

    def test_refresh_access_token_success(self) -> None:
        """Test successful token refresh."""
        mock_auth = Mock()
        mock_auth.update_access_token = Mock()

        result = refresh_access_token(mock_auth)
        assert result is True
        mock_auth.update_access_token.assert_called_once()

    def test_refresh_access_token_no_method(self) -> None:
        """Test token refresh when method not available."""
        mock_auth = Mock()
        del mock_auth.update_access_token

        result = refresh_access_token(mock_auth)
        assert result is False

    def test_get_fresh_access_token(self) -> None:
        """Test getting fresh access token."""
        mock_auth = Mock()
        mock_auth.update_access_token = Mock()
        mock_auth.access_token = "fresh_token_1234567890123456"

        token = get_fresh_access_token(mock_auth)
        assert token == "fresh_token_1234567890123456"
        mock_auth.update_access_token.assert_called_once()

    def test_find_tap_authenticator_success(self) -> None:
        """Test finding authenticator from TAP instance."""
        mock_stream = Mock()
        mock_stream.authenticator = "test_authenticator"

        mock_tap = Mock()
        mock_tap.discover_streams.return_value = [mock_stream]

        authenticator = find_tap_authenticator(mock_tap)
        assert authenticator == "test_authenticator"

    def test_find_tap_authenticator_not_found(self) -> None:
        """Test finding authenticator when none available."""
        mock_stream = Mock()
        del mock_stream.authenticator

        mock_tap = Mock()
        mock_tap.discover_streams.return_value = [mock_stream]

        authenticator = find_tap_authenticator(mock_tap)
        assert authenticator is None


class TestFileUtils:
    """Test file utility functions."""

    def test_clean_filename(self) -> None:
        """Test filename cleaning."""
        assert clean_filename("test|name") == "test_name"
        assert clean_filename("test/path") == "test_path"
        assert clean_filename("test\\backslash") == "test_backslash"
        assert clean_filename("normal_name") == "normal_name"

    def test_create_directory_structure(self) -> None:
        """Test directory structure creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            category_path = create_directory_structure(base_path, "test_category")

            assert category_path.exists()
            assert category_path.is_dir()
            assert category_path.name == "test_category"

    def test_save_json_data(self) -> None:
        """Test saving JSON data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            records = [{"id": 1, "name": "test"}]

            save_json_data(file_path, "test_stream", "test_category", records)

            assert file_path.exists()
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            assert data["stream_name"] == "test_stream"
            assert data["category"] == "test_category"
            assert data["record_count"] == 1
            assert data["records"] == records

    def test_save_binary_file(self) -> None:
        """Test saving binary file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.bin"
            content = b"test binary content"

            size_mb = save_binary_file(file_path, content)

            assert file_path.exists()
            assert file_path.read_bytes() == content
            assert size_mb == len(content) / (1024 * 1024)

    def test_save_artifact_summary(self) -> None:
        """Test saving artifact summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "summary.json"
            config = {"base_url": "https://test.com", "instance_id": "test"}
            artifacts = [{"id": "test1", "status": "downloaded"}]

            save_artifact_summary(file_path, config, 10, 8, 2, artifacts)

            assert file_path.exists()
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            assert data["total_integrations"] == 10
            assert data["downloaded"] == 8
            assert data["failed"] == 2
            assert data["success_rate"] == 80.0
            assert data["base_url"] == "https://test.com"


class TestOICAPIClient:
    """Test OIC API client utility functions."""

    def test_init(self) -> None:
        """Test client initialization."""
        client = OICAPIClient("https://test.com", "test_instance")
        assert client.base_url == "https://test.com"
        assert client.instance_id == "test_instance"
        assert client.base_path == "/ic/api/integration/v1"

    def test_build_integration_archive_url(self) -> None:
        """Test building integration archive URL."""
        client = OICAPIClient("https://test.com", "test_instance")
        url = client.build_integration_archive_url("TEST_INTEGRATION")

        expected = "https://test.com/ic/api/integration/v1/integrations/TEST_INTEGRATION/archive"
        assert url == expected

    def test_get_archive_request_params(self) -> None:
        """Test getting archive request parameters."""
        client = OICAPIClient("https://test.com", "test_instance")
        params = client.get_archive_request_params()

        assert params == {"integrationInstance": "test_instance"}

    def test_get_archive_request_headers(self) -> None:
        """Test getting archive request headers."""
        client = OICAPIClient("https://test.com", "test_instance")
        headers = client.get_archive_request_headers("test_token")

        expected = {
            "Authorization": "Bearer test_token",
            "Accept": "application/octet-stream",
        }
        assert headers == expected

    def test_is_binary_content_by_type(self) -> None:
        """Test binary content detection by content type."""
        client = OICAPIClient("https://test.com", "test_instance")

        assert client.is_binary_content(b"test", "application/octet-stream") is True
        assert client.is_binary_content(b"test", "application/zip") is True
        assert client.is_binary_content(b"test", "application/json") is False

    def test_is_binary_content_by_size(self) -> None:
        """Test binary content detection by size."""
        client = OICAPIClient("https://test.com", "test_instance")
        large_content = b"x" * 2000  # > 1000 bytes

        assert client.is_binary_content(large_content, "text/plain") is True
        assert client.is_binary_content(b"small", "text/plain") is False

    def test_parse_json_response_valid(self) -> None:
        """Test parsing valid JSON response."""
        client = OICAPIClient("https://test.com", "test_instance")
        content = b'{"test": "data"}'

        result = client.parse_json_response(content)
        assert result == {"test": "data"}

    def test_parse_json_response_invalid(self) -> None:
        """Test parsing invalid JSON response."""
        client = OICAPIClient("https://test.com", "test_instance")
        content = b"invalid json"

        result = client.parse_json_response(content)
        assert result is None

    @patch("tap_oic.utils.oic_api_client.requests.get")
    def test_download_integration_archive_success(self, mock_get) -> None:
        """Test successful integration archive download."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"binary archive content"
        mock_response.headers = {"content-type": "application/octet-stream"}
        mock_get.return_value = mock_response

        client = OICAPIClient("https://test.com", "test_instance")
        success, content, content_type, status_code = (
            client.download_integration_archive("TEST_INTEGRATION", "test_token")
        )

        assert success is True
        assert content == b"binary archive content"
        assert content_type == "application/octet-stream"
        assert status_code == 200

    @patch("tap_oic.utils.oic_api_client.requests.get")
    def test_download_integration_archive_failure(self, mock_get) -> None:
        """Test failed integration archive download."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = b"Not found"
        mock_response.headers = {"content-type": "text/plain"}
        mock_get.return_value = mock_response

        client = OICAPIClient("https://test.com", "test_instance")
        success, content, content_type, status_code = (
            client.download_integration_archive("TEST_INTEGRATION", "test_token")
        )

        assert success is False
        assert content is None
        assert content_type == "text/plain"
        assert status_code == 404
