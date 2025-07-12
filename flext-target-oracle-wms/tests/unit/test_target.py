"""Unit tests for TargetOracleWMS."""

from unittest.mock import Mock, patch

from flext_target_oracle_wms.target import TargetOracleWMS


class TestTargetOracleWMS:
    """Test cases for TargetOracleWMS."""

    def test_target_initialization(self) -> None:
        """Test target can be initialized with basic config."""
        config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "user": "wms_user",
            "password": "test_password",
            "schema": "WMS",
        }

        target = TargetOracleWMS(config=config, validate_config=False)

        assert target.name == "target-oracle-wms"
        assert target.config["host"] == "localhost"
        assert target.config["port"] == 1521

    def test_connection_string_building(self) -> None:
        """Test Oracle connection string is built correctly."""
        config = {
            "host": "oracle.example.com",
            "port": 1521,
            "service_name": "WMSPROD",
            "user": "wms_user",
            "password": "secret_password",
        }

        target = TargetOracleWMS(config=config, validate_config=False)
        connection_string = target._build_connection_string()

        expected = "oracle+oracledb://wms_user:secret_password@oracle.example.com:1521/?service_name=WMSPROD"
        assert connection_string == expected

    @patch("flext_target_oracle_wms.target.sa.create_engine")
    def test_engine_creation(self, mock_create_engine) -> None:
        """Test SQLAlchemy engine is created with correct parameters."""
        config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "user": "wms_user",
            "password": "test_password",
            "pool_size": 10,
            "pool_max_overflow": 20,
            "connection_timeout": 60,
        }

        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        target = TargetOracleWMS(config=config, validate_config=False)
        engine = target.engine

        assert engine == mock_engine
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args

        assert call_args[1]["pool_size"] == 10
        assert call_args[1]["max_overflow"] == 20
        assert call_args[1]["pool_timeout"] == 60

    def test_get_sink(self) -> None:
        """Test sink creation."""
        config = {
            "host": "localhost",
            "port": 1521,
            "service_name": "XEPDB1",
            "user": "wms_user",
            "password": "test_password",
        }

        target = TargetOracleWMS(config=config, validate_config=False)

        sink = target.get_sink(
            stream_name="test_stream",
            schema={"properties": {"id": {"type": "integer"}}},
            key_properties=["id"],
        )

        assert sink.stream_name == "test_stream"
        assert sink._target == target
