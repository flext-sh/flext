"""Tests for TargetOracleWMS."""

import pytest

from target_oracle_wms.sinks import (
    GenericWMSSink,
    InventorySink,
    OrderSink,
    WarehouseSink,
)
from target_oracle_wms.target import TargetOracleWMS


class TestTargetOracleWMS:
    """Test the TargetOracleWMS class."""

    def test_target_initialization(self, config: dict) -> None:
        """Test target can be initialized with config."""
        target = TargetOracleWMS(config=config)
        assert target.name == "target-oracle-wms"
        assert target.config == config

    def test_get_sink_class_inventory_streams(self) -> None:
        """Test that inventory streams return InventorySink."""
        target = TargetOracleWMS(config={})

        inventory_streams = ["inventory", "lots", "locations", "cycle_counts"]
        for stream_name in inventory_streams:
            sink_class = target.get_sink_class(stream_name)
            assert sink_class == InventorySink

    def test_get_sink_class_order_streams(self) -> None:
        """Test that order streams return OrderSink."""
        target = TargetOracleWMS(config={})

        order_streams = ["orders", "order_lines", "shipments", "allocations"]
        for stream_name in order_streams:
            sink_class = target.get_sink_class(stream_name)
            assert sink_class == OrderSink

    def test_get_sink_class_warehouse_streams(self) -> None:
        """Test that warehouse streams return WarehouseSink."""
        target = TargetOracleWMS(config={})

        warehouse_streams = ["tasks", "workers", "equipment", "zones"]
        for stream_name in warehouse_streams:
            sink_class = target.get_sink_class(stream_name)
            assert sink_class == WarehouseSink

    def test_get_sink_class_generic_streams(self) -> None:
        """Test that unknown streams return GenericWMSSink."""
        target = TargetOracleWMS(config={})

        generic_streams = ["unknown", "custom_entity", "some_other_stream"]
        for stream_name in generic_streams:
            sink_class = target.get_sink_class(stream_name)
            assert sink_class == GenericWMSSink

    def test_max_parallelism(self) -> None:
        """Test max parallelism property."""
        target = TargetOracleWMS(config={})
        assert target.max_parallelism == 4

    def test_config_validation_required_fields(self) -> None:
        """Test that required config fields are validated."""
        # Missing required fields should fail
        with pytest.raises(Exception):
            TargetOracleWMS(config={}, validate_config=True)

        # All required fields present should succeed
        valid_config = {
            "base_url": "https://test.com",
            "username": "user",
            "password": "pass",
        }
        target = TargetOracleWMS(config=valid_config, validate_config=True)
        assert target.config == valid_config

    def test_config_schema(self) -> None:
        """Test config schema is properly defined."""
        schema = TargetOracleWMS.config_jsonschema

        # Check required properties
        assert "properties" in schema
        assert "base_url" in schema["properties"]
        assert "username" in schema["properties"]
        assert "password" in schema["properties"]

        # Check optional properties
        assert "timeout" in schema["properties"]
        assert "enable_kpi_calculation" in schema["properties"]
        assert "enable_alerts" in schema["properties"]
        assert "output_path" in schema["properties"]
        assert "output_format" in schema["properties"]

        # Check required fields
        assert schema["required"] == ["base_url", "username", "password"]

        # Check secret fields
        assert schema["properties"]["password"]["secret"] is True
        assert schema["properties"]["database_url"]["secret"] is True
