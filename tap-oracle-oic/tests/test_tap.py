"""Tests for tap-oracle-oic."""

from tap_oracle_oic.tap import TapOIC


class TestTapOIC:
    """Test cases for TapOIC."""

    def test_tap_initialization(self) -> None:
        """Test tap can be initialized with config."""
        config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
            "oauth_client_id": "test_client",
            "oauth_client_secret": "test_secret",
            "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
        }
        tap = TapOIC(config=config, validate_config=False)
        assert tap.name == "tap-oic"
        assert tap.config == config

    def test_discover_streams(self) -> None:
        """Test stream discovery."""
        config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
            "oauth_client_id": "test_client",
            "oauth_client_secret": "test_secret",
            "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
        }
        tap = TapOIC(config=config, validate_config=False)
        streams = tap.discover_streams()

        # Should have at least core streams
        assert len(streams) >= 6
        stream_names = [s.name for s in streams]
        assert "integrations" in stream_names
        assert "connections" in stream_names
        assert "packages" in stream_names
        assert "lookups" in stream_names

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        import pytest
        from singer_sdk.exceptions import ConfigValidationError

        # Missing required fields should raise exception when validation is enabled
        config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
        }
        with pytest.raises(ConfigValidationError):
            TapOIC(config=config, validate_config=True)

    def test_include_extended_streams(self) -> None:
        """Test extended streams inclusion."""
        config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
            "oauth_client_id": "test_client",
            "oauth_client_secret": "test_secret",
            "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
            "include_extended": True,
        }
        tap = TapOIC(config=config, validate_config=False)
        streams = tap.discover_streams()

        # Should include infrastructure streams
        stream_names = [s.name for s in streams]
        assert "adapters" in stream_names
        assert "agent_groups" in stream_names
