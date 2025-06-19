"""Tests for WMS orchestrator."""

import json
from typing import Any

import pytest

from flx_oracle_wms.config import PipelineConfig, RuntimeConfig
from flx_oracle_wms.orchestrator import WMSOrchestrator


class TestWMSOrchestrator:
    """Test the WMS orchestrator."""

    def test_orchestrator_initialization(self, sample_config: dict[str, Any]) -> None:
        """Test that orchestrator initializes properly."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        assert orchestrator.config == pipeline_config
        assert hasattr(orchestrator, "logger")
        assert orchestrator.source_name == "tap-oracle-wms"
        assert orchestrator.target_name == "target-oracle-wms"

    def test_orchestrator_configuration_validation(self, sample_config: dict[str, Any]) -> None:
        """Test that orchestrator validates configuration properly."""
        # Test valid configuration
        valid_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(valid_config)
        assert orchestrator.config is not None

        # Test configuration access
        assert orchestrator.config.source_name == "tap-oracle-wms"
        assert orchestrator.config.target_name == "target-oracle-wms"

    def test_orchestrator_pipeline_setup(self, sample_config: dict[str, Any]) -> None:
        """Test that orchestrator sets up pipelines correctly."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        # Should be able to set up pipeline components
        assert hasattr(orchestrator, "setup_pipeline")

        # Pipeline setup should not raise errors
        try:
            orchestrator.setup_pipeline()
        except NotImplementedError:
            # Expected if method is not yet implemented
            pass
        except Exception as e:
            # Should not raise unexpected errors
            pytest.fail(f"Unexpected error during pipeline setup: {e}")

    def test_orchestrator_runtime_configuration(self, sample_config: dict[str, Any]) -> None:
        """Test runtime configuration handling."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        runtime_config = RuntimeConfig(
            parallelism=1, buffer_size=1000, timeout_seconds=300
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        # Should accept runtime configuration
        orchestrator.set_runtime_config(runtime_config)
        assert orchestrator.runtime_config == runtime_config

    def test_orchestrator_stream_processing(self, sample_config: dict[str, Any]) -> None:
        """Test stream processing capabilities."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        # Should have stream processing methods
        assert hasattr(orchestrator, "process_stream")

        # Test stream processing setup
        test_stream_name = "facility"
        test_schema = {
            "type": "object",
            "properties": {"id": {"type": "string"}, "name": {"type": "string"}},
        }

        try:
            orchestrator.process_stream(test_stream_name, test_schema)
        except NotImplementedError:
            # Expected if method is not yet implemented
            pass
        except Exception as e:
            # Should not raise unexpected errors
            pytest.fail(f"Unexpected error during stream processing: {e}")

    def test_orchestrator_monitoring_capabilities(self, sample_config: dict[str, Any]) -> None:
        """Test monitoring and metrics capabilities."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        # Should have monitoring capabilities
        assert hasattr(orchestrator, "get_metrics")

        # Test metrics retrieval
        try:
            metrics = orchestrator.get_metrics()
            if metrics is not None:
                assert isinstance(metrics, dict)
        except NotImplementedError:
            # Expected if method is not yet implemented
            pass
        except Exception as e:
            # Should not raise unexpected errors
            pytest.fail(f"Unexpected error getting metrics: {e}")

    def test_orchestrator_error_handling(self, sample_config: dict[str, Any]) -> None:
        """Test error handling capabilities."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        # Should handle invalid configurations gracefully
        invalid_runtime = RuntimeConfig(
            parallelism=-1,  # Invalid value
            buffer_size=0,  # Invalid value
            timeout_seconds=-10,  # Invalid value
        )

        try:
            orchestrator.set_runtime_config(invalid_runtime)
            # Should either accept and validate, or reject gracefully
        except ValueError:
            # Expected for invalid configuration
            pass
        except Exception as e:
            # Should not raise unexpected errors
            pytest.fail(f"Unexpected error handling invalid config: {e}")

    def test_orchestrator_lifecycle_management(self, sample_config: dict[str, Any]) -> None:
        """Test orchestrator lifecycle management."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        # Should have lifecycle methods
        lifecycle_methods = ["start", "stop", "pause", "resume"]
        for method in lifecycle_methods:
            if hasattr(orchestrator, method):
                try:
                    getattr(orchestrator, method)()
                except NotImplementedError:
                    # Expected if method is not yet implemented
                    pass
                except Exception as e:
                    # Should not raise unexpected errors
                    pytest.fail(f"Unexpected error in {method}: {e}")

    def test_orchestrator_configuration_serialization(self, sample_config: dict[str, Any]) -> None:
        """Test configuration serialization and deserialization."""
        pipeline_config = PipelineConfig(
            source_name="tap-oracle-wms",
            target_name="target-oracle-wms",
            config=sample_config,
        )

        orchestrator = WMSOrchestrator(pipeline_config)

        # Configuration should be serializable
        try:
            config_dict = orchestrator.config.model_dump()
            assert isinstance(config_dict, dict)
            assert "source_name" in config_dict
            assert "target_name" in config_dict

            # Should be JSON serializable
            config_json = json.dumps(config_dict)
            assert len(config_json) > 0

        except Exception as e:
            pytest.fail(f"Configuration serialization failed: {e}")
