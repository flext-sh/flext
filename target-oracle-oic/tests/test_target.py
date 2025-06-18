"""Tests for target-oracle-oic."""

from target_oracle_oic.sinks import ConnectionsSink, IntegrationsSink
from target_oracle_oic.target import TargetOracleOIC


class TestTargetOracleOIC:
    """Test cases for TargetOracleOIC."""

    def test_target_initialization(self) -> None:
        """Test target can be initialized with config."""
        config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
            "oauth_client_id": "test_client",
            "oauth_client_secret": "test_secret",
            "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
        }
        target = TargetOracleOIC(config=config)
        assert target.name == "target-oracle-oic"
        assert target.config == config

    def test_get_sink_mapping(self) -> None:
        """Test sink mapping for different streams."""
        config = {
            "base_url": "https://test.integration.ocp.oraclecloud.com",
            "oauth_client_id": "test_client",
            "oauth_client_secret": "test_secret",
            "oauth_token_url": "https://test.identity.oraclecloud.com/oauth2/v1/token",
        }
        target = TargetOracleOIC(config=config)

        # Test known streams
        assert target._get_sink_class("connections") == ConnectionsSink
        assert target._get_sink_class("integrations") == IntegrationsSink

        # Test unknown stream returns default
        assert target._get_sink_class("unknown_stream") == target.default_sink_class

    def test_config_schema(self) -> None:
        """Test configuration schema is valid."""
        schema = TargetOracleOIC.config_jsonschema
        assert isinstance(schema, dict)
        assert "properties" in schema

        # Check required properties
        properties = schema["properties"]
        assert "base_url" in properties
        assert "oauth_client_id" in properties
        assert "oauth_client_secret" in properties
        assert "oauth_token_url" in properties

        # Check target-specific properties
        assert "import_mode" in properties
        assert "activate_integrations" in properties
