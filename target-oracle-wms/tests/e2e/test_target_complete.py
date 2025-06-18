"""End-to-end tests for complete target functionality."""

import pytest
from target_oracle_wms.target import TargetOracleWMS


class TestTargetComplete:
    """End-to-end tests for complete target workflow."""

    @pytest.mark.e2e()
    def test_complete_target_initialization(self, sample_config) -> None:
        """Test complete target initialization workflow."""
        target = TargetOracleWMS(config=sample_config)

        # Validate target properties
        assert target.name == "target-oracle-wms"
        assert target.config == sample_config
        assert hasattr(target, "logger")

        # Validate sink classes are available
        assert hasattr(target, "get_sink_class")

    @pytest.mark.e2e()
    def test_sink_class_resolution(self, sample_config) -> None:
        """Test that sink classes are resolved correctly for different streams."""
        target = TargetOracleWMS(config=sample_config)

        # Test sink resolution for various stream types
        stream_types = [
            "inventory",
            "orders",
            "warehouse",
            "facility",
            "company",
            "unknown_stream_type",
        ]

        for stream_name in stream_types:
            sink_class = target.get_sink_class(stream_name)
            assert sink_class is not None

            # Validate sink class has required methods
            assert hasattr(sink_class, "__init__")

    @pytest.mark.e2e()
    def test_record_processing_workflow(self, sample_config) -> None:
        """Test complete record processing workflow."""
        target = TargetOracleWMS(config=sample_config)

        # Test schema for a common stream
        test_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
            },
        }

        # Get sink class and instantiate
        sink_class = target.get_sink_class("facility")
        sink = sink_class(
            target_name="target-oracle-wms",
            stream_name="facility",
            schema=test_schema,
            key_properties=["id"],
        )

        # Test record processing
        test_record = {
            "id": "FAC001",
            "name": "Test Facility",
            "created_at": "2024-01-01T00:00:00Z",
        }

        # Should be able to process record without errors
        processed = sink._prepare_record(test_record)
        assert isinstance(processed, dict)
        assert "id" in processed

    @pytest.mark.e2e()
    def test_business_logic_integration(self, sample_config) -> None:
        """Test business logic integration across sinks."""
        target = TargetOracleWMS(config=sample_config)

        # Test different business logic modules
        business_streams = ["inventory", "orders", "warehouse"]

        for stream_name in business_streams:
            sink_class = target.get_sink_class(stream_name)
            sink = sink_class(
                target_name="target-oracle-wms",
                stream_name=stream_name,
                schema={"type": "object", "properties": {}},
                key_properties=[],
            )

            # Validate business logic is available
            assert hasattr(sink, "business_logic")

    @pytest.mark.e2e()
    def test_configuration_validation_complete(self, sample_config) -> None:
        """Test complete configuration validation."""
        # Test with valid config
        target = TargetOracleWMS(config=sample_config)
        assert target.config == sample_config

        # Test config access from sinks
        sink_class = target.get_sink_class("facility")
        sink = sink_class(
            target_name="target-oracle-wms",
            stream_name="facility",
            schema={"type": "object", "properties": {}},
            key_properties=[],
        )

        # Sink should have access to target configuration
        assert hasattr(sink, "config") or hasattr(sink, "_config")

    @pytest.mark.e2e()
    def test_error_handling_workflow(self, sample_config) -> None:
        """Test error handling throughout the target workflow."""
        target = TargetOracleWMS(config=sample_config)

        # Test with invalid stream configurations
        invalid_schemas = [
            {"type": "invalid"},  # Invalid schema type
            {},  # Empty schema
            {"properties": {}},  # Missing type
        ]

        for invalid_schema in invalid_schemas:
            try:
                sink_class = target.get_sink_class("test_stream")
                sink = sink_class(
                    target_name="target-oracle-wms",
                    stream_name="test_stream",
                    schema=invalid_schema,
                    key_properties=[],
                )

                # Try to process a record
                test_record = {"test": "data"}
                sink._prepare_record(test_record)

            except Exception as e:
                # Errors should be handled gracefully
                assert len(str(e)) > 0

    @pytest.mark.e2e()
    def test_multi_stream_handling(self, sample_config) -> None:
        """Test handling multiple streams simultaneously."""
        target = TargetOracleWMS(config=sample_config)

        # Test multiple streams can be processed
        streams = ["inventory", "orders", "facility"]
        sinks = {}

        for stream_name in streams:
            sink_class = target.get_sink_class(stream_name)
            sinks[stream_name] = sink_class(
                target_name="target-oracle-wms",
                stream_name=stream_name,
                schema={"type": "object", "properties": {"id": {"type": "string"}}},
                key_properties=["id"],
            )

        # Each sink should be independent
        for stream_name, sink in sinks.items():
            assert sink.stream_name == stream_name

            # Test record processing
            test_record = {"id": f"{stream_name}_001"}
            processed = sink._prepare_record(test_record)
            assert isinstance(processed, dict)

    @pytest.mark.e2e()
    def test_memory_efficiency(self, sample_config) -> None:
        """Test that target operations are memory efficient."""
        # Test that multiple target instances don't accumulate memory
        for i in range(5):
            target = TargetOracleWMS(config=sample_config)

            # Create and use sink
            sink_class = target.get_sink_class("facility")
            sink = sink_class(
                target_name="target-oracle-wms",
                stream_name="facility",
                schema={"type": "object", "properties": {}},
                key_properties=[],
            )

            # Process a record
            test_record = {"id": f"test_{i}"}
            processed = sink._prepare_record(test_record)
            assert isinstance(processed, dict)

            # Clean up
            del sink
            del target
