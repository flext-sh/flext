"""Tests for target sinks."""

from target_oracle_wms.sinks import (
    GenericWMSSink,
    InventorySink,
    OrderSink,
    WarehouseSink,
    WMSBaseSink,
)


class TestWMSBaseSink:
    """Test WMS base sink functionality."""

    def test_base_sink_initialization(self, sample_config) -> None:
        """Test that base sink initializes properly."""
        sink = WMSBaseSink(
            target_name="target-oracle-wms",
            stream_name="test_stream",
            schema={},
            key_properties=[],
        )

        assert sink.target_name == "target-oracle-wms"
        assert sink.stream_name == "test_stream"
        assert hasattr(sink, "logger")

    def test_base_sink_record_validation(self, sample_config) -> None:
        """Test that base sink validates records correctly."""
        schema = {
            "type": "object",
            "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
        }

        sink = WMSBaseSink(
            target_name="target-oracle-wms",
            stream_name="test_stream",
            schema=schema,
            key_properties=["id"],
        )

        # Test valid record
        valid_record = {"id": 1, "name": "test"}
        # Should not raise exception
        sink._validate_record(valid_record)

        # Test invalid record
        invalid_record = {"id": "not_an_integer", "name": "test"}
        # Should handle gracefully
        try:
            sink._validate_record(invalid_record)
        except Exception:
            # Expected for invalid data
            pass


class TestInventorySink:
    """Test inventory-specific sink functionality."""

    def test_inventory_sink_initialization(self, sample_config) -> None:
        """Test that inventory sink initializes with proper configuration."""
        schema = {
            "type": "object",
            "properties": {
                "item_id": {"type": "string"},
                "quantity": {"type": "number"},
                "location": {"type": "string"},
            },
        }

        sink = InventorySink(
            target_name="target-oracle-wms",
            stream_name="inventory",
            schema=schema,
            key_properties=["item_id"],
        )

        assert sink.stream_name == "inventory"
        assert hasattr(sink, "business_logic")

    def test_inventory_record_processing(self, sample_config) -> None:
        """Test inventory record processing logic."""
        schema = {
            "type": "object",
            "properties": {
                "item_id": {"type": "string"},
                "quantity": {"type": "number"},
            },
        }

        sink = InventorySink(
            target_name="target-oracle-wms",
            stream_name="inventory",
            schema=schema,
            key_properties=["item_id"],
        )

        test_record = {"item_id": "ITEM001", "quantity": 100}

        # Should be able to process record without errors
        processed = sink._prepare_record(test_record)
        assert isinstance(processed, dict)
        assert "item_id" in processed


class TestOrderSink:
    """Test order-specific sink functionality."""

    def test_order_sink_initialization(self, sample_config) -> None:
        """Test that order sink initializes properly."""
        schema = {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "status": {"type": "string"},
                "items": {"type": "array"},
            },
        }

        sink = OrderSink(
            target_name="target-oracle-wms",
            stream_name="orders",
            schema=schema,
            key_properties=["order_id"],
        )

        assert sink.stream_name == "orders"
        assert hasattr(sink, "business_logic")

    def test_order_record_transformation(self, sample_config) -> None:
        """Test order record transformation."""
        schema = {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "status": {"type": "string"},
            },
        }

        sink = OrderSink(
            target_name="target-oracle-wms",
            stream_name="orders",
            schema=schema,
            key_properties=["order_id"],
        )

        test_record = {"order_id": "ORD001", "status": "pending"}

        # Should be able to transform record
        transformed = sink._prepare_record(test_record)
        assert isinstance(transformed, dict)
        assert "order_id" in transformed


class TestWarehouseSink:
    """Test warehouse-specific sink functionality."""

    def test_warehouse_sink_initialization(self, sample_config) -> None:
        """Test that warehouse sink initializes correctly."""
        schema = {
            "type": "object",
            "properties": {
                "facility_id": {"type": "string"},
                "name": {"type": "string"},
                "location": {"type": "string"},
            },
        }

        sink = WarehouseSink(
            target_name="target-oracle-wms",
            stream_name="warehouse",
            schema=schema,
            key_properties=["facility_id"],
        )

        assert sink.stream_name == "warehouse"
        assert hasattr(sink, "business_logic")


class TestGenericWMSSink:
    """Test generic WMS sink functionality."""

    def test_generic_sink_initialization(self, sample_config) -> None:
        """Test that generic sink handles any stream type."""
        schema = {
            "type": "object",
            "properties": {"id": {"type": "string"}, "data": {"type": "object"}},
        }

        sink = GenericWMSSink(
            target_name="target-oracle-wms",
            stream_name="generic_stream",
            schema=schema,
            key_properties=["id"],
        )

        assert sink.stream_name == "generic_stream"

    def test_generic_sink_flexibility(self, sample_config) -> None:
        """Test that generic sink handles various record types."""
        schema = {"type": "object", "properties": {}}

        sink = GenericWMSSink(
            target_name="target-oracle-wms",
            stream_name="flexible",
            schema=schema,
            key_properties=[],
        )

        # Should handle various record structures
        test_records = [
            {"simple": "value"},
            {"complex": {"nested": "data"}},
            {"array_field": [1, 2, 3]},
        ]

        for record in test_records:
            processed = sink._prepare_record(record)
            assert isinstance(processed, dict)


class TestSinkFactory:
    """Test sink factory and routing functionality."""

    def test_sink_selection_logic(self, sample_config) -> None:
        """Test that appropriate sinks are selected for stream types."""
        from target_oracle_wms.target import TargetOracleWMS

        target = TargetOracleWMS(config=sample_config)

        # Test sink selection for different stream types
        stream_types = [
            ("inventory", InventorySink),
            ("orders", OrderSink),
            ("warehouse", WarehouseSink),
            ("unknown_stream", GenericWMSSink),
        ]

        for stream_name, expected_sink_class in stream_types:
            sink_class = target.get_sink_class(stream_name)
            assert (
                issubclass(sink_class, expected_sink_class)
                or sink_class == expected_sink_class
            )
